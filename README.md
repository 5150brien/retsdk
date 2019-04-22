# RETSDK

A Python SDK for the Real Estate Transaction Standard (RETS)

## Supported Transactions

-Login/Logout
-GetMetadata
-Search
-GetObject

## Usage

### Initialize a client

Start a new client to setup a connection to a RETS server and load account options.

```python
from retsdk.client import RETSConnection

rets = RETSConnection(
    username='your_rets_username',
    password='your_rets_password',
    login_url='https://rets.somemls.com/rets/Login/'
)

# Metadata info will be loaded for you (if you're into metadata-aware applications)
print(rets.metadata_version)
# 1.00.00235

print(rets.metadata_timestamp)
# 2015-05-20T20:08:15Z

print(rets.min_metadata_timestamp)
# 2015-05-20T20:08:15Z

# Transaction URLs will be loaded too (but you don't usually need to worry about them)
print(rets.get_metadata_url)
# https://rets.somemls.com/rets/GetMetadata/

print(rets.get_search_url)
# https://rets.somemls.com/rets/Search/

print(rets.get_object_url)
# https://rets.somemls.com/rets/GetObject/
```

#### Initialization Parameters

Parameter Name | Required | Meaning
------------ | ------------- | -------------
username | Yes | RETS account username
password | Yes | RETS account password
login_url | Yes | RETS server login URL
auth_type | No | Authentication type (defaults to 'digest')
rets_version | No | Specifies the RETS version to be used (defaults to 'RETS/1.7.2')
user_agent | No | Specifies the client's user-agent (defaults to 'Mozilla/4.0')

#### Exceptions
Exception Name | Meaning
------------ | -------------
retsdk.exceptions.AuthenticationError | Raised when an unsupported authentication type is specified by the auth_type parameter
retsdk.exceptions.RequestError | Raised if authentication fails because of invalid account credentials or an incorrect login URL

### Get System Metadata

There are (usually) several different tiers of metadata to consider. Resource metadata tells you what resources are available on a RETS server.

```python
from pprint import pprint

# Get the RETS system's resource metadata
response = rets.get_resource_metadata()
pprint(response)
#{'more_rows': False,
# 'ok': True,
# 'record_count': 2,
# 'reply_code': '0',
# 'reply_text': 'Operation Success.',
# 'rows': [{'ClassCount': 1,
#           'ClassDate': '2015-01-28T21:06:04Z',
#           'ClassVersion': '1.00.00001',
#           'Description': 'Agent',
#           'EditMaskDate': '2014-03-21T17:15:05Z',
#           'EditMaskVersion': '1.00.00000',
#           'KeyField': 'sysid',
#           'LookupDate': '2015-01-21T17:31:54Z',
#           'LookupVersion': '1.00.00001',
#           'ObjectDate': '2014-03-21T17:15:24Z',
#           'ObjectVersion': '1.00.00001',
#           'ResourceID': 'Agent',
#           'SearchHelpDate': '2015-03-21T17:15:05Z',
#           'SearchHelpVersion': '1.00.00001',
#           'StandardName': 'Agent',
#           'TableName': 'Agent',
#           'UpdateHelpDate': '2014-03-21T17:15:05Z',
#           'UpdateHelpVersion': '1.00.00001',
#           'ValidationExpressionDate': '2014-03-21T17:15:05Z',
#           'ValidationExpressionVersion': '1.00.00001',
#           'ValidationExternalDate': '2014-03-21T17:15:05Z',
#           'ValidationExternalVersion': '1.00.00001',
#           'ValidationLookupDate': '2014-03-21T17:15:05Z',
#           'ValidationLookupVersion': '1.00.00001',
#           'VisibleName': 'Agent'},
#          {'ClassCount': 1,
#           'ClassDate': '2015-01-28T16:19:02Z',
#           'ClassVersion': '1.00.00001',
#           'Description': 'Listing',
#           'EditMaskDate': '2015-01-28T14:34:35Z',
#           'EditMaskVersion': '1.00.00001',
#           'KeyField': 'sysid',
#           'LookupDate': '2015-01-28T14:34:35Z',
#           'LookupVersion': '1.00.00001',
#           'ObjectDate': '2015-01-28T14:34:35Z',
#           'ObjectVersion': '1.00.00001',
#           'ResourceID': 'Property',
#           'SearchHelpDate': '2015-01-28T14:34:35Z',
#           'SearchHelpVersion': '1.00.00001',
#           'StandardName': 'Property',
#           'TableName': 'Listing',
#           'UpdateHelpDate': '2015-01-28T14:34:35Z',
#           'UpdateHelpVersion': '1.00.00001',
#           'ValidationExpressionDate': '2015-01-28T14:34:35Z',
#           'ValidationExpressionVersion': '1.00.00001',
#           'ValidationExternalDate': '2015-01-28T14:34:35Z',
#           'ValidationExternalVersion': '1.00.00001',
#           'ValidationLookupDate': '2015-01-28T14:34:35Z',
#           'ValidationLookupVersion': '1.00.00001',
#           'VisibleName': 'Listing'}]}

```

Class metadata will provide information about the classes in a resource. Use the ResourceID from resource metadata to look up class metadata.

```python
class_metadata_response = rets.get_class_metadata(resource='Property')
pprint(class_metadata_response)
#{'more_rows': False,
# 'ok': True,
# 'record_count': 1,
# 'reply_code': '0',
# 'reply_text': 'Operation Success.',
# 'rows': [{'ClassName': 'Listing',
#           'Description': 'Cross Property',
#           'StandardName': None,
#           'TableDate': '2015-01-28T02:49:39Z',
#           'TableVersion': '1.00.00985',
#           'UpdateDate': '2015-01-28T14:32:06Z',
#           'UpdateVersion': '1.00.00001',
#           'VisibleName': 'Cross Property'}]}
```

Table metadata tells you about the specific fields available in a class. Use the ResourceID from resource metadata and the ClassName from class metadata to look up table metadata.

```python
table_metadata_response = rets.get_table_metadata(resource='Property', _class='Listing')
pprint(table_metadata_response)
#{'more_rows': False,
# 'ok': True,
# 'record_count': 2,
# 'reply_code': '0',
# 'reply_text': 'Operation Success.',
# 'rows': [{'Alignment': 'Left',
#           'DBName': 'price',
#           'DataType': 'Int',
#           'Default': None,
#           'EditMaskID': None,
#           'InKeyIndex': 0,
#           'Index': 1,
#           'Interpretation': 'Number',
#           'LongName': 'Price',
#           'LookupName': None,
#           'MaxSelect': None,
#           'Maximum': 2147483647,
#           'MaximumLength': 11,
#           'MetadataEntryID': 200,
#           'Minimum': -2147483648,
#           'Precision': None,
#           'Required': 1,
#           'SearchHelpID': None,
#           'Searchable': 1,
#           'ShortName': 'Price',
#           'StandardName': 'Price',
#           'SystemName': 'Price',
#           'Unique': 0,
#           'Units': 'USD',
#           'UseSeparator': None},
#          {'Alignment': 'Left',
#           'DBName': 'property_type',
#           'DataType': 'Character',
#           'Default': None,
#           'EditMaskID': None,
#           'InKeyIndex': 0,
#           'Index': 1,
#           'Interpretation': 'Lookup',
#           'LongName': 'Property Type',
#           'LookupName': 'PropertyType',
#           'MaxSelect': None,
#           'Maximum': None,
#           'MaximumLength': 32,
#           'MetadataEntryID': 201,
#           'Minimum': None,
#           'Precision': None,
#           'Required': 1,
#           'SearchHelpID': None,
#           'Searchable': 1,
#           'ShortName': 'PropertyType',
#           'StandardName': 'PropertyType',
#           'SystemName': 'PropertyType',
#           'Unique': 0,
#           'Units': None,
#           'UseSeparator': None}]}
```

The last kind of metadata is "lookup type" metadata. When a field in a RETS class has an interpretation value of "Lookup", you can look up a table of possible values for that field. Use the ResourceID from resource metadata and the LookupName from table metadata to get lookup metadata.

```python
lookup_type_metadata_response = rets.get_lookup_type_metadata(resource='Property', lookup_name='PropertyType')
pprint(lookup_type_metadata_response)
# {'more_rows': False,
#  'ok': True,
#  'record_count': 3,
#  'reply_code': '0',
#  'reply_text': 'Operation Success.',
#  'rows': [{'LongValue': 'Single Family Detached',
#           'MetadataEntryID': 10002,
#           'ShortValue': 'SFD',
#           'Value': 'SFD'},
#          {'LongValue': 'Condominium',
#           'MetadataEntryID': 10003,
#           'ShortValue': 'CON',
#           'Value': 'CON'},
#          {'LongValue': 'Multifamily',
#           'MetadataEntryID': 10004,
#           'ShortValue': 'MUL',
#           'Value': 'MUL'}]}
```

#### GetMetadata Parameters

Parameter Name | Required | Meaning
------------ | ------------- | -------------
username | Yes | RETS account username
password | Yes | RETS account password
login_url | Yes | RETS server login URL
auth_type | No | Authentication type (defaults to 'digest')
rets_version | No | Specifies the RETS version to be used (defaults to 'RETS/1.7.2')
user_agent | No | Specifies the client's user-agent (defaults to 'Mozilla/4.0')

#### Exceptions
Exception Name | Meaning
------------ | -------------
retsdk.exceptions.AuthenticationError | Raised when an unsupported authentication type is specified by the auth_type parameter
retsdk.exceptions.RequestError | Raised if authentication fails because of invalid account credentials or an incorrect login URL

### Downloading Data from a RETS server

Download data or search through records using the RETSConnection's get_data() method. Generally, you will want to examine the system metadata first so that you can see what fields are available (both to download and to query). The fields parameter accepts a list of fields to be downloaded for each record that matches the query.

```python
# A RETS query (DMQL)
rets_query = "(PropertyType=SFD)"

# A list of fields that should be downloaded for each record
fields_to_be_downloaded = ["MLSNumber", "Price"]

data = rets.get_data(
    resource='Property',
    class_name='Property',
    query=query,
    fields=fields_to_be_downloaded,
)

print(data)
# {'more_rows': False,
#  'ok': True,
#  'record_count': '10',
#  'reply_code': '0',
#  'reply_text': 'Operation Success.',
#  'rows': [{'Price': 199000.0, 'MLSNumber': 'MLS0000001'},
#           {'Price': 2500000.0, 'MLSNumber': 'MLS0000002'},
#           {'Price': 319500.0, 'MLSNumber': 'MLS0000003'},
#           {'Price': 275900.0, 'MLSNumber': 'MLS0000004'},
#           {'Price': 239900.0, 'MLSNumber': 'MLS0000005'},
#           {'Price': 339900.0, 'MLSNumber': 'MLS0000006'},
#           {'Price': 249900.0, 'MLSNumber': 'MLS0000007'},
#           {'Price': 219900.0, 'MLSNumber': 'MLS0000008'},
#           {'Price': 579900.0, 'MLSNumber': 'MLS0000009'},
#           {'Price': 209900.0, 'MLSNumber': 'MLS0000010'}]}

```

You may optionally use the limit and offset parameters to page the data that you want to download. This allows you to break large downloads into smaller pieces.

```python
# A broad RETS query
rets_query=(PropertyType=SFD,CON,MUL)

# A list of the fields to be returned for each row
fields_to_be_downloaded = ["MLSNumber", "Price"]

# Use Limit and Offset to download rows matching the query a little at a time
download_complete = False
last_offset = 0
while not download_complete:
    data = rets.get_data(
        resource='Property',
        class_name='Property',
        query=rets_query,
        fields=fields_to_be_downloaded,
        limit=10,                           # Specify how many rows to return at once
        offset=last_offset                  # Specify where in the results to start
    )

    for row in data['rows']:
        # Do something with the rows you downloaded here (save to a database, etc.)
        pass

    if data['more_rows']:
        # Still more coming! Increment the offset to get the next set of rows
        last_offset += 10
    else:
        # All rows matching the query have been downloaded
        download_complete = True

```

If you just want a count of how many records match your query, you can use the .get_count() method instead of .get_data(). Note that .get_data() still provides a count in the response dictionary, so .get_count() is for situations where you want only the count with no other data returned. You do not specify fields, limit, or offset with .get_count().

```python
row_count = rets.get_count('Property', class_name='Property', query=rets_query)
print(row_count)
# 105
```

### Downloading Images
To download images, use the get_object() method. The response dictionary for this method will include object data that can be written to a file. An order number is used to specify which image you want to download in situations where more than one object is available (this usually matches a reference to the image object in a RETS server's Media table).

```python
# Download some image data
img_response = rets.get_object(resource='Property', obj_type='Photo', obj_id='MLS0000001', order_no=0)

# Write the image (as bytes) to a file somewhere
path = "/tmp/rets/images/MLS0000001_01.jpg"
if img_response['ok']:
    with open(path, 'wb') as f:
        f.write(img_data['object_data'])

```
