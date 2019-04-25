# RETSDK

A Python SDK for the Real Estate Transaction Standard (RETS)

## Installation

```
pip install retsdk
```

## Usage

### Initialize a client

Create a new RETSConnection instance to connect to a RETS server.

##### Example
```python
from retsdk.client import RETSConnection

rets = RETSConnection(
    username='your_rets_username',
    password='your_rets_password',
    login_url='https://rets.somemls.com/rets/Login/'
)

# Metadata info & transaction URLs get loaded automatically
print(rets.metadata_version)
# 1.00.00235

print(rets.metadata_timestamp)
# 2015-05-20T20:08:15Z

print(rets.min_metadata_timestamp)
# 2015-05-20T20:08:15Z

print(rets.get_metadata_url)
# https://rets.somemls.com/rets/GetMetadata/

print(rets.get_search_url)
# https://rets.somemls.com/rets/Search/

print(rets.get_object_url)
# https://rets.somemls.com/rets/GetObject/
```

##### Initialization Arguments
Argument | Type | Required | Meaning
------------ | ------------- | ------------- | -------------
username | String | Yes | RETS account username
password | String | Yes | RETS account password
login_url | String | Yes | RETS server login URL
auth_type | String | No | Authentication type (defaults to 'digest')
rets_version | String | No | Specifies the RETS version to be used (defaults to 'RETS/1.7.2')
user_agent | String | No | Specifies the user-agent (defaults to 'RETSDK/1.0')


### Download Metadata

There are (usually) several tiers of metadata to consider in a RETS system. These are resource metadata, class metadata, table metadata, and lookup-type metadata. RETSDK has methods to work with each of these programmatically, but if you would like to view metadata right in your browser with no additional setup, you can also try [RETSMD](https://retsmd.com/).

All of the metadata query methods return a response dictionary with the following items:

Key | Meaning | Value 
------------ | ------------- | -------------
more_rows | Indicates whether there are more rows to download | Boolean
ok | Indicates whether the process completed successfully | Boolean
record_count | The number of rows returned | Integer
reply_code | The server's RETS reply code | Integer
reply_text | The message accompanying the RETS reply code | String
rows | The metadata records returned by the server | List


#### 1. Resource Metadata
Resource metadata is the top layer of metadata; it tells you what resources are accessible from your account. Use the **get_resource_metadata()** method to download resource metadata.

##### Arguments
None

##### Example
```python
# Get the RETS system's resource metadata
response = rets.get_resource_metadata()

from pprint import pprint
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
#           'KeyField': 'sysid',
#           'LookupDate': '2015-01-21T17:31:54Z',
#           'LookupVersion': '1.00.00001',
#           'ObjectDate': '2014-03-21T17:15:24Z',
#           'ObjectVersion': '1.00.00001',
#           'ResourceID': 'Agent',
#           'StandardName': 'Agent',
#           'TableName': 'Agent',
#           'VisibleName': 'Agent'},
#          {'ClassCount': 1,
#           'ClassDate': '2015-01-28T16:19:02Z',
#           'ClassVersion': '1.00.00001',
#           'Description': 'Listing',
#           'KeyField': 'sysid',
#           'LookupDate': '2015-01-28T14:34:35Z',
#           'LookupVersion': '1.00.00001',
#           'ObjectDate': '2015-01-28T14:34:35Z',
#           'ObjectVersion': '1.00.00001',
#           'ResourceID': 'Property',
#           'StandardName': 'Property',
#           'TableName': 'Listing',
#           'VisibleName': 'Listing'}]}

```

#### 2. Class Metadata
Class metadata provides information about the classes in a resource. Use the **get_class_metadata()** method to get class metadata.

##### Arguments
Argument Name | Required | Meaning
------------ | ------------- | -------------
resource | No | The ID of a RETS resource. Defaults to 'Property'.

##### Example
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

#### 3. Table Metadata
Table metadata tells you about the specific fields available in a class. Use the **get_table_metadata()** method to get table metadata.

##### Arguments
Argument Name | Required | Meaning
------------ | ------------- | -------------
resource | No | The ID of a resource. Defaults to 'Property'.
class_name | No | The class name or system name of a class within a resource. Defaults to 'Listing'.

##### Example
```python
table_metadata_response = rets.get_table_metadata(
    resource='Property', 
    class_name='Listing'
)

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
#           'Searchable': 1,
#           'ShortName': 'PropertyType',
#           'StandardName': 'PropertyType',
#           'SystemName': 'PropertyType',
#           'Unique': 0,
#           'Units': None,
#           'UseSeparator': None}]}
```

#### 4. Lookup-Type Metadata
The last type of metadata data to consider is lookup-type metdata. If a field in the table metadata has an interpretation of "Lookup", there is a list of specific values that the field can hold. Get this list of values with the **get_lookup_type_metadata()** method.

##### Arguments
Argument Name | Required | Meaning
------------ | ------------- | -------------
resource | No | The ID of a resource. Defaults to 'Property'.
lookup_name | Yes | A field's lookup name.

##### Example
```python
lookup_type_metadata_response = rets.get_lookup_type_metadata(
    resource='Property',
    lookup_name='PropertyType'
)

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


### Download Data

Download data or search through records using the **get_data()** method. You will need to specify a query (using DMQL) and a list of the fields that you would like to have returned to you (see *Download Metadata* to learn how to find out what fields are available).

##### Arguments
Argument Name | Required | Meaning
------------ | ------------- | -------------
resource | Yes | The ID of a RETS system resource.
class_name | Yes | The name of a class in the specified resource.
query | Yes | A DMQL query
fields | Yes | A list of the fields to be returned
data_format | No | The RETS data format to be used with fields. Defaults to 'COMPACT-DECODED'.
limit | No | The maximum number of records to return
offset | No | An offset position that can be used with limit

##### Response Dictionary
Key | Meaning | Value Type
------------ | ------------- | -------------
more_rows | Indicates whether there are more rows to download for the current query | Boolean
ok | Indicates whether the query was processed successfully | Boolean
record_count | The number of rows returned | Integer
reply_code | The server's RETS reply code | Integer
reply_text | The message accompanying the RETS reply code | String
rows | The actual records returned by the query | List

##### Examples
```python
# Query all listings with "SFD" PropertyType, return only MLSNumber and Price
rets_query = "(PropertyType=SFD)"
fields_to_be_downloaded = ["MLSNumber", "Price"]

data = rets.get_data(
    resource='Property',
    class_name='Property',
    query=query,
    fields=fields_to_be_downloaded,
)

pprint(data)
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

You may optionally use the **limit** and **offset** parameters to page the data that you want to download. This allows you to break large downloads into smaller pieces.

```python
# A broader RETS query that might returns lots of records
rets_query=(PropertyType=SFD,CON,MUL)
fields_to_be_downloaded = ["MLSNumber", "Price"]

# Use a loop to download 10 records at a time
download_complete = False
last_offset = 0
while not download_complete:
    data = rets.get_data(
        resource='Property',
        class_name='Listing',
        query=rets_query,
        fields=fields_to_be_downloaded,
        limit=10,
        offset=last_offset
    )

    for row in data['rows']:
        # Do something with the rows you downloaded here (save to a database, etc.)
        pass

    if data['more_rows']:
        # Still more to download!
        last_offset += 10
    else:
        # Done!
        download_complete = True

```

#### Getting a Record Count without Returning Data
If you just want a count of how many records match your query, you can use **get_count()** instead of get_data(). get_count() will return an integer instead of a full response dictionary.

You do not specify fields, limit, or offset with get_count(), but otherwise it works just like get_data(). It is, in fact, just another wrapper for the RETS Search transaction with the *Count* parameter set differently.

##### Example
```python
row_count = rets.get_count(
    'Property',
    class_name='Property',
    query=rets_query
)

print(row_count)
# 105
```


### Download Images
Use the **get_object()** method to download images. This method is a wrapper for the RETS specification's GetObject transaction.

get_object() returns a response dictionary, but the dictionary does not contain 'rows', 'record_count' or 'more_rows'. Instead, it will contain an item called 'object_data', where the actual object data will be stored as bytes.

##### Arguments
Argument Name | Required | Meaning
------------ | ------------- | -------------
resource | Yes | The ID of a RETS system resource.
obj_type | Yes | The type of object to be returned (e.g., 'Photo').
obj_id | Yes | The system ID of the record associated with object.
order_no | No | The order number of the image or other object (for situations where there are multiple images associated with one listing)
path | No | A file system path where image data should be written (used only when write=True).
write | No | A boolean value that can optionally be set to True if you would like get_object() to write image/object data to a file for you. You must specifiy a path if you wish to use this option.

##### Response Dictionary:

Key | Meaning | Value Type
------------ | ------------- | ------------- 
ok | Indicates whether the object download was successful | Boolean
reply_code | The server's RETS reply code | Integer
reply_text | The message accompanying the RETS reply code | String
object_data | The object data payload | Bytes

##### Example
```python
# Download an image (as bytes)
img_response = rets.get_object(
    resource='Property',
    obj_type='Photo',
    obj_id='MLS0000001',
    order_no=0
)

# Write the image data to a file somewhere
path = "/tmp/rets/images/MLS0000001_01.jpg"
if img_response['ok']:
    with open(path, 'wb') as f:
        f.write(img_response['object_data'])

```


### Logout
If you would like to, you can close your RETS session with the **logout()** method.

##### Arguments
None

##### Response Dictionary:
Key | Meaning | Value Type
------------ | ------------- | -------------
more_rows | Indicates whether there are more rows to download for the current transaction | Boolean
ok | Indicates whether the transaction was successful | Boolean
record_count | The number of rows returned | Integer
reply_code | The server's RETS reply code | Integer
reply_text | The message accompanying the RETS reply code | String
rows | The actual records returned by the logout transaction | List

##### Example
```python
logout_response = rets.logout()

pprint(logout_response)
# {'more_rows': False,
#  'ok': True,
#  'record_count': 1,
#  'reply_code': '0',
#  'reply_text': 'Operation Success.',
#  'rows': [{'SignOffMessage': 'Connection Closed'}]}
```

### Exceptions
RETSDK raises these exceptions when stuff goes wrong:

Exception | Meaning
------------ | -------------
retsdk.exceptions.AuthenticationError | Raised when an unsupported authentication type is specified during intialization
retsdk.exceptions.RequestError | Raised if a RETS transaction request cannot be completed
retsdk.exceptions.TransactionError | Raised if the user attempts to perform a transaction that is not supported by the current RETS account.


