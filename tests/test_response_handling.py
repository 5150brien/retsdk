import os
import unittest
import xml.etree.ElementTree as ET
from retsdk.utilities import parse_response


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class TestBadRequestResponseHandling(unittest.TestCase):
    """
    Tests handling of RETS server responses for invalid requests
    """
    def setUp(self):
        response_tree = ET.parse(os.path.join(TEST_DIR, 'bad_request.xml'))
        xml = response_tree.getroot()
        self.response_dict = parse_response(xml)

    def test_return_type(self):
        """
        Invalid requests should still return a complete response dict
        """
        self.assertIsInstance(self.response_dict, dict)
        self.assertEqual(len(self.response_dict), 6)

    def test_response_data_payload(self):
        """
        The 'rows' value should be an empty list (no data payload returned)
        """
        self.assertIsInstance(self.response_dict['rows'], list)
        self.assertEqual(len(self.response_dict['rows']), 0)

    def test_error_reply_code(self):
        """
        Reply code for bad requests should be non-null and non-zero
        """
        self.assertIsNotNone(self.response_dict['reply_code'])
        self.assertNotEqual(self.response_dict['reply_code'], '')
        self.assertNotEqual(self.response_dict['reply_code'], '0')

    def test_reply_text(self):
        """
        Reply text for bad requests should be non-null
        """
        self.assertIsNotNone(self.response_dict['reply_text'])
        self.assertNotEqual(self.response_dict['reply_text'], '')

    def test_ok_value(self):
        """
        The response dict's 'ok' val should be False for bad requests
        """
        self.assertFalse(self.response_dict['ok'])

    def test_more_rows_value(self):
        """
        The response dict's 'more_rows' val should be False for bad requests
        """
        self.assertFalse(self.response_dict['more_rows'])


class TestSearchResponseWithNoAdditionalRows(unittest.TestCase):
    """
    Tests single-response handling for valid search transactions
    """
    def setUp(self):
        response_tree = ET.parse(
            os.path.join(
                TEST_DIR, 
                'search_response.xml'
            )
        )
        xml = response_tree.getroot()
        self.response_dict = parse_response(xml)

    def test_response_rows(self):
        """
        The response dict should contain a list of values (can be empty)
        """
        self.assertIsInstance(self.response_dict['rows'], list)
        self.assertGreaterEqual(len(self.response_dict['rows']), 0)

    def test_ok_value(self):
        """
        The response dict's 'ok' val should be True
        """
        self.assertTrue(self.response_dict['ok'])

    def test_more_rows_value(self):
        """
        The response dict's 'more_rows' val should be False
        """
        self.assertFalse(self.response_dict['more_rows'])


class TestSearchResponseWithAdditionalRows(unittest.TestCase):
    """
    Tests multiple-response handling of valid search transactions
    """
    def setUp(self):
        response_tree = ET.parse(
            os.path.join(
                TEST_DIR, 'search_response_maxrows.xml'
            )
        )
        xml = response_tree.getroot()
        self.response_dict = parse_response(xml)

    def test_response_rows(self):
        """
        The response dict should contain a list of values (can be empty)
        """
        self.assertIsInstance(self.response_dict['rows'], list)
        self.assertGreaterEqual(len(self.response_dict['rows']), 0)

    def test_ok_value(self):
        """
        The response dict's 'ok' val should be True
        """
        self.assertTrue(self.response_dict['ok'])

    def test_more_rows_value(self):
        """
        The response dict's 'more_rows' val should be True
        """
        self.assertTrue(self.response_dict['more_rows'])
