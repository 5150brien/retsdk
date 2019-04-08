from datetime import datetime


def decode_reply(reply_code):
    """
    Returns True if the RETS request was successful, otherwise False

    Intended to fill the response dict's 'ok' field as an alternative to
    the RETS specification's wonky reply code bullshit.

    :param reply_code: a RETS reply code
    :type reply_code: str
    :rtype: bool
    :return: True if the reply code was 0 (success), False otherwise
    """
    if reply_code == '0':
        return True
    else:
        return False

def parse_response(xml):
    """
    Packages RETS server responses in a Python dict

    Note that this function handles responses for data-only transactions
    (Login, Logout, GetMetadata, Search). GetObject transactions have a
    slightly different response payload, which is handled by 
    RETSConnection.__make_request directly.

    :param xml: the XML returned by a RETS server as a response
    :type xml: xml.etree.ElementTree.Element
    :rtype: dict
    :return: a response dictionary
    """
    response = {}
    response['rows'] = []
    response['reply_code'] = xml.attrib['ReplyCode']
    response['reply_text'] = xml.attrib['ReplyText']
    response['ok'] = decode_reply(xml.attrib['ReplyCode'])
    response['record_count'] = 0
    response['more_rows'] = False

    if response['reply_text'] == 'Operation Success.':
        if xml[0].tag == 'RETS-RESPONSE':
            # Login/Logout transactions (can come with options/messages)
            response_data = split_line(xml[0].text)
            for item in response_data:
                if len(item.split('=')) > 1:
                    key = item.split('=')[0]
                    value = item.split('=')[1]
                    response['rows'].append({key: value})
        else:
            if xml[0].tag == 'COUNT':
                response['record_count'] = xml[0].attrib['Records']

            if xml[-1].tag == 'MAXROWS':
                response['more_rows'] = True

            if 'METADATA-' in xml[0].tag:
                # GetMetadata response data is nested
                response['rows'] = extract_values(xml[0])
            else:
                response['rows'] = extract_values(xml)

    if not response['record_count']:
        response['record_count'] = len(response['rows'])

    return response

def extract_values(xml):
    """
    Processes the delimited rows of data returned by a RETS server

    :param xml: the XML returned by a RETS server as a response
    :type xml: xml.etree.ElementTree.Element
    :rtype: list
    :return: a list of dictionaries that represent rows of mapped RETS data 
    """
    rows = []
    columns = []
    for child in xml:
        if child.tag == 'COLUMNS':
            columns = split_line(child.text)
        if child.tag == 'DATA':
            line = split_line(child.text)
            if len(line) == len(columns):
                mapped_row = map_fields(columns, line)
            else:
                # Row can't be mapped (column mismatch)
                mapped_row = None

            rows.append(mapped_row)
    return rows

def split_line(xml_line_text):
    """
    Returns a list of values, given a row of delimited RETS response data

    :param xml_line_text: a string of delimited RETS data
    :type xml_line_text: str
    :rtype: list
    :return: a list of values from xml_line_text
    """
    if '\x09' in xml_line_text:
        # Search Transactions
        return xml_line_text.strip().split('\x09')
    elif '\t' in xml_line_text:
        # Metadata Transactions
        return xml_line_text.strip().split('\t')
    elif '\n' in xml_line_text.strip():
        # Login/Logout Transactions
        return xml_line_text.strip().split('\n')
    return  [xml_line_text.strip()]

def map_fields(columns, line):
    """
    Returns a dictionary with fields matched to column names

    :param columns: a list of column header/name values
    :type columns: list
    :param line: a row of data values matching columns
    :type line: list
    :rtype: dict
    :return: a dictionary mapping columns to line values
    """
    row = {}
    for i, field_value in enumerate(line):
        name = columns[i]
        val = cast(field_value)
        row[name] = val

    return row

def convert_boolean(value):
    """
    Converts MLS pseudo-Boolean values into actual Boolean values.

    Some MLSs seem to use y/Y, yes/YES/Yes, or 1 as True and n/N, no/NO/No or
    0 as False. Apparently RESO transport specifications actually encourage
    this, but RESO compliance is inconsistent among MLSs.

    :param value: An MLS/RESO boolean-type value
    :type value: str and int are both acceptable
    :rtype: bool
    :return: True for affirmative values, False for negative values
    """
    if value != None:
        try:
            v = value.lower()
            if v == 'y' or v == 'yes':
                return True
            elif v == 'n' or v == 'no':
                return False
            else:
                # Value was something like 'Unknown' or 'U'
                return None
        except AttributeError:
            # True/False was represented as 1 or 0
            if value == 1:
                return True
            else:
                return False
    else:
        return None

def is_numeric(value):
    """
    Returns True if value is numeric, returns False otherwise

    :param value: a data value returned by a RETS server
    :type value: str
    :rtype: bool
    :return: True for numeric value, False otherwise
    """
    try:
        float(value)    # can include things like '2e100'
    except ValueError:
        # Value was not numeric
        return False
    except TypeError:
        # Value was None
        return False
    
    return True

def cast(value):
    """
    Casts a RETS value into a Python data type

    Since RETS servers can return non-Boolean strings (like 'yes' or 'no') or
    numeric values (namely 0 or 1) for Booleans, these values are left alone
    and are NOT cast into Python Booleans. Application developers should
    decide on a case-by-case basis whether to store MLS Booleans as strings,
    integers, or legitimate Booleans. The function convert_boolean is
    included in this module to help with that.

    Similarly, numeric values containing alpha characters (like '2e100')
    are returned as strings so that application deverlopers can decide how
    to correctly handle them.

    Integers with leading zeroes are also returned as strings.

    :param value: a value returned by a RETS server
    :type value: str
    :rtype: int, float, str, or none
    :return: the original value as a native Python type
    """
    if is_numeric(value):
        if value.lstrip('-').replace('.', '', 1).isdigit():
            # Cases where value is numeric without special characters
            if value == '0':
                # Actual Integer zero
                return int(value)
            elif value == '0.0' or value == '0.00':
                # Actual Decimal zero
                return float(value)
            if value[0] == '0':
                if not float(value).is_integer():
                    # Decimals with a leading zero (<1)
                    return float(value)
                else:
                    # Numeric strings with leading zeros (like zip code)
                    return str(value)
            elif '.' in value:
                # Decimals
                return float(value)
            else:
                # Integers
                return int(value)
        else:
            # value is numeric WITH special chars (like '2e100')
            return str(value)
    elif len(value) == 23 and value[4] == '-' and \
        value[7] == '-' and value[10] == 'T':
        # Dates in ISO 8601 format
        return unrets_date(value)
    elif value == '':
        return None
    else:
        return str(value)

def unrets_date(rets_date):
    """
    Converts a RETS date (ISO 8601 format) into a Python datetime

    :param rets_date: a RETS/ISO 8601 date
    :type rets_date: str
    :rtype: datetime.datetime
    :return: rets_date as a Python datetime
    """
    # For datetimes with microseconds
    return datetime.strptime(rets_date, '%Y-%m-%dT%H:%M:%S.%f')

def rets_date(py_date):
    """
    Converts a Python datetime into a RETS (ISO 8601 format) date

    :param py_date: a Python datetime
    :type pydate: date
    :rtype: str
    :return: py_date as a string in ISO 8601 format (no microseconds)
    """
    return py_date.replace(microsecond=0).isoformat()
