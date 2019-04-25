import xml.etree.ElementTree as ET
import urllib.request as request
from urllib.parse import urlparse, urlencode
from urllib.error import HTTPError, URLError
from http.client import IncompleteRead
from socket import timeout
import time
import sys

from retsdk.exceptions import *
from retsdk.utilities import parse_response


class RETSConnection(object):

    def __init__(self, username='', password='', login_url='', 
                 auth_type='digest', rets_version='RETS/1.7.2',
                                       user_agent='RETSDK/1.0'):
        """
        Sets up a connection to a RETS server and loads account options
        """
        self.headers = {'User-Agent': user_agent, 
                        'RETS-Version': rets_version}

        # Get a base URL from the login URL
        parsed_url = urlparse(login_url)
        if parsed_url.scheme and parsed_url.netloc:
            base_url = parsed_url.scheme + "://" + parsed_url.netloc
        else:
            url_msg = "{0} is not a valid RETS Login URL".format(login_url)
            raise AuthenticationError(url_msg)

        # Setup an opener that can handle authentication
        pw_mgr = request.HTTPPasswordMgrWithDefaultRealm()
        pw_mgr.add_password(None, base_url, username, password)

        if auth_type == 'digest':
            handler = request.HTTPDigestAuthHandler(pw_mgr)
        elif auth_type == 'basic':
            handler = request.HTTPBasicAuthHandler(pw_mgr)
        else:
            raise AuthenticationError("auth_type must be 'basic' or 'digest'")

        opener = request.build_opener(handler)
        request.install_opener(opener)

        # Perform a login request to get server & account info
        login_response = self.__login(login_url)

        for option in login_response['rows']:
            for key, val in option.items():
                if key == 'MetadataVersion':
                    self.metadata_version = val
                if key == 'MetadataTimestamp':
                    self.metadata_timestamp = val
                if key == 'MinMetadataTimestamp':
                    self.min_metadata_timestamp = val
                if key == 'Login':
                    self.login_url = val
                if key == 'Logout':
                    self.logout_url = val
                if key == 'Search':
                    self.search_url = val
                if key == 'GetMetadata':
                    self.get_metadata_url = val
                if key == 'GetObject':
                    self.get_object_url = val
                if key == 'Update':
                    self.update_url = val
                if key == 'PostObject':
                    self.post_object_url = val

    def __login(self, login_url):
        """
        Performs a login request and returns the server/account options
        """
        login_request = request.Request(login_url, headers=self.headers)
        response = self.__make_request(login_request)[1]
        if response['ok']:
            return response
        else:
            raise ResponseError(response=response['reply_text'])

    def logout(self):
        """
        Closes a session with a RETS server
        """
        logout_request = request.Request(self.logout_url, headers=self.headers)
        response = self.__make_request(logout_request)[1]

        return response

    def get_resource_metadata(self):
        """
        Gets the metadata for what resources are available on the RETS server

        :rtype: dict
        :return: Response dictionary with rows of resource metadata
        """
        get_metadata_params = {
            'Type': 'METADATA-RESOURCE',
            'ID': 0,
            'Format': 'COMPACT',
        }

        encoded_parameters = urlencode(get_metadata_params)
        response = self.__get_metadata(encoded_parameters)
        return response

    def get_class_metadata(self, resource='Property'):
        """
        Gets top-level metadata for the classes within a resource

        :param resource: The resource for which you would like the class info
        :type resource: str
        :rtype: dict
        :return: Response dictionary with rows of class metadata
        """
        get_metadata_params = {
            'Type': 'METADATA-CLASS',
            'ID': resource,
            'Format': 'COMPACT',
        }

        encoded_parameters = urlencode(get_metadata_params)
        response = self.__get_metadata(encoded_parameters)
        return response

    def get_table_metadata(self, resource='Property', class_name='Listing'):
        """
        Gets the detailed field metadata for a specific class

        A class 'table' usually just means the fields exposed for that class.

        :param resource: The name of a specific resource on a RETS server
        :type resource: str
        :param class_name: The ClassName/SystemName of a class within resource
        :type class_name: str
        :rtype: dict
        :return: Response dictionary with rows of field metadata for a class
        """
        _id = resource + ':' + class_name
        get_metadata_params = {
            'Type': 'METADATA-TABLE',
            'ID': _id,
            'Format': 'COMPACT',
        }

        encoded_parameters = urlencode(get_metadata_params)
        response = self.__get_metadata(encoded_parameters)
        return response

    def get_lookup_type_metadata(self, resource='Property', lookup_name=''):
        """
        Gets the lookup values for a specific field within a class

        If a field's 'Interpretation' column has values like 'Lookup' or
        'LookupMulti' for a particular field, you can use this method to get
        a list of the values that are allowed for that field.

        :param resource: The name of a resource on a RETS server
        :type resource: str
        :param lookup_name: the 'LookupName' of a specific field
        :type lookup_name: str
        :rtype: dict
        :return: Response dictionary of values for a field
        """
        _id = resource + ':' + lookup_name
        get_metadata_params = {
            'Type': 'METADATA-LOOKUP_TYPE',
            'ID': _id,
            'Format': 'COMPACT',
        }

        encoded_parameters = urlencode(get_metadata_params)
        response = self.__get_metadata(encoded_parameters)
        return response

    def __get_metadata(self, parameters):
        """
        Handles the GetMetadata transaction for all of the metadata methods

        :param parameters: A string of encoded GetMetadata URL parameters
        :type parameters: str
        :rtype: dict
        :return: Response dictionary for GetMetadata requests
        """
        if not self.get_metadata_url:
            raise TransactionError(transaction_type='GetMetadata')
        else:
            url = self.get_metadata_url + '?' + parameters
            metadata_request = request.Request(url, headers=self.headers)
            response = self.__make_request(metadata_request)[1]

            return response

    def get_object(self, resource, obj_type, obj_id,
                   order_no=0, path=None, write=False):
        """
        Performs a getObject transaction. 

        For consistency, reply_code and reply_text are included in all 
        responses (not just error cases)

        When write=False, the response dictionary will contain the key
        'object_data'. The corresponding value will be the actual bytes of
        object data returned by the RETS server. If write=True and a valid
        filesystem path is provided to 'path', the object data will be written
        to the file specified in 'path' and 'object_data' will not be included
        in the response dictionary.

        :param resourse: The name of a resource on a RETS server
        :type resource: str
        :param obj_type: the Object Type (ex. "Photo")
        :type obj_type: str
        :param obj_id: the system ID of the record associated with the object
        :type obj_id: str
        :param order_no: The order number of the object
        :type order_no: int
        :param path: A destination path where object data can be written
        :type path: str
        :param write: True if you want to write data to a file (specified
                      by path); False if you just want to return the object
                      data in the response dictionary
        :type write: bool
        :rtype: dict
        :return: response dictionary that includes 'object_data'
        """
        if self.get_object_url:
            obj_id = obj_id + ':' + order_no

            get_object_params = {
                'Type': obj_type,
                'Resource': resource,
                'Id': obj_id,
            }

            url_params = urlencode(get_object_params)
            full_url = self.get_object_url + '?' + url_params
            r = request.Request(full_url, headers=self.headers)
            successful = False
            retry_counter = 3

            while retry_counter > 0 and successful == False:
                successful, response = self.__make_request(r)
                retry_counter -= 1

                # Pause/retry if rate limit exceeded 
                if successful and response['reply_text'] == 'Too many outstanding requests':
                    successful = False
                    print('Rate limit exceeded. Pausing for 60 seconds...', file=sys.stdout)
                    time.sleep(60)

            if not successful:
                # Ran out of retries without a successful response
                raise RequestError('The RETS request could not be completed')

            if write:
                if response['ok']:
                    with open(path, 'wb') as f:
                        f.write(response['object_data'])
                    del response['object_data']

            return response
        else:
            # No GetObject transaction access on this account
            raise TransactionError(transaction_type='GetObject')

    def get_count(self, resource, class_name, query):
        """
        Performs the Search transaction and returns the record count only

        :param resource: A Resource on a RETS server
        :type resource: str
        :param class_name: A class within resource
        :type class_name: str
        :param query: A DMQL query to request rows of data from the class
        :type query: str
        :rtype: int
        :return: the number of rows that query would return
        """
        query_data = {
            'FORMAT': 'COMPACT-DECODED', 
            'SearchType': resource, 
            'Class': class_name,
            'StandardNames': '0', 
            'QueryType': 'DMQL2', 
            'Query': query,
            'Count' : 2,
        }

        count_params = urlencode(query_data)
        response = self.__search(count_params)

        return response['record_count']

    def get_data(self, resource, class_name, query, fields,
                 data_format='COMPACT-DECODED', limit=None, offset=None):
        """
        Performs the Search transaction and returns data

        :param resource: A Resource on a RETS server
        :type resource: str
        :param class_name: A class within resource
        :type class_name: str
        :param query: A DMQL query to request rows of data from the class
        :type query: str
        :param fields: a list of the fields to be returned for each record
        :type: fields: list
        :param data_format: the data format for response data
        :type data_format: str
        :param limit: the maximum number of records that should be returned
        :type limit: int
        :param offset: the number of records to offset in the response
        :type offset: int
        :rtype: dict
        :return: Response dictionary
        """
        query_data = {
            'FORMAT': 'COMPACT-DECODED', 
            'SearchType': resource, 
            'Class': class_name,
            'StandardNames': '0', 
            'QueryType': 'DMQL2', 
            'Query': query,
            'Select': ','.join(fields),
            'Count' : 1,
        }

        if limit:
            query_data['Limit'] = str(limit)
        if offset:
            query_data['Offset'] = str(offset)
        
        url_params = urlencode(query_data)
        response = self.__search(url_params)

        return response

    def __search(self, parameters):
        """
        Handles the Search transaction for get_count and get_data

        :param parameters: A string of encoded URL parameters for search
        :type parameters: str
        :rtype: dict
        :return: response dictionary
        """
        if not self.search_url:
            raise TransactionError(transaction_type="Search")
        else:
            full_url = self.search_url + '?' + parameters
            search_request = request.Request(full_url, headers=self.headers)
            success = False
            retry_counter = 10
            response = {}

            while retry_counter > 0 and success == False:
                success, response = self.__make_request(search_request)
                retry_counter -= 1

                if success and \
                response['reply_text'] == 'Too many outstanding queries':
                    success = False
                    print('Rate limit exceeded. Pausing for 60 seconds...', 
                                                            file=sys.stdout)
                    time.sleep(60)

            if not success:
                raise RequestError('The RETS request could not be completed')

            return response

    def __make_request(self, rets_request):
        """
        Makes a transaction request to the RETS server.
        
        Note: errors are only supressed if they could be fixed with a retry.

        :param request: a request to a RETS server
        :type request: urllib.request.Request
        :rtype: bool, dict
        :return: boolean success value, response dict
        """
        success = False
        response = None

        try:
            r = request.urlopen(rets_request)
            content_type = r.headers['Content-Type']
            payload = r.read()

            if content_type == 'text/xml; charset=utf-8':
                xml = ET.fromstring(payload)
                response = parse_response(xml)
            elif content_type == 'image/jpeg':
                response = dict()
                response['ok'] = True
                response['reply_code'] = '0'
                response['reply_text'] = 'Operation Success.'
                response['object_data'] = payload

            success = True

        except IncompleteRead:
            print('Incomplete read during download', file=sys.stderr)
        except timeout:
            print('The RETS request has timed out', file=sys.stderr)
        except HTTPError as e:
            msg = 'The RETS request caused HTTP Error {0}: {1}'.format(e.code, e.reason)
            raise RequestError(msg)
        except URLError as e:
            msg = 'The RETS request caused URL Error: '.format(e.reason)
            raise RequestError(msg)
        except ET.ParseError as e:
            # Something in an XML response could not be read
            raise
        
        return success, response
