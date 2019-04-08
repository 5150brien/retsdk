import unittest
from datetime import datetime
from retsdk.utilities import cast


class TestRETSDataTypeCasting(unittest.TestCase):
    """
    Tests for the cast utility (converts RETS data into Python types)
    """
    def test_date_conversion(self):
        rets_date = "2018-01-01T00:00:00.004"
        self.assertIs(type(cast(rets_date)), datetime)

    def test_integer_conversion(self):
        int_string = '256'
        self.assertIs(type(cast(int_string)), int)

    def test_integer_conversion(self):
        int_string = '02882'
        self.assertIs(type(cast(int_string)), str)

    def test_float_conversion(self):
        float_string = '2.56'
        self.assertIs(type(cast(float_string)), float)

    def test_float_with_leading_zero(self):
        float_string = '0.56'
        self.assertIs(type(cast(float_string)), float)

    def test_zero_float(self):
        float_string = '0.0'
        self.assertIs(type(cast(float_string)), float)

    def test_normal_string(self):
        normal_string = 'RETSdiculous'
        self.assertIs(type(cast(normal_string)), str)

    def test_empty_string(self):
        empty_string = ''
        self.assertIsNone(cast(empty_string))
