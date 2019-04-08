import unittest
from retsdk.client import RETSConnection
from retsdk.exceptions import AuthenticationError


class TestRETSConnection(unittest.TestCase):
    """
    Tests RETSConnection client setup
    """
    def setUp(self):
        self.url = 'https://rets.somemls.com/Login'
        self.username = 'joe'
        self.password = 'joe123'

    def test_login_url(self):
        msg = 'bad/missing Login URL should raise AuthenticationError'
        with self.assertRaises(AuthenticationError, msg=msg):
            RETSConnection(
                username=self.username,
                password=self.password,
                login_url='',
                auth_type='basic'
            )
        with self.assertRaises(AuthenticationError, msg=msg):
            RETSConnection(
                username=self.username,
                password=self.password,
                login_url='rets.com',
                auth_type='basic'
            )

    def test_connection_auth_options(self):
        msg = 'unsupported auth_types should raise AuthenticationError'
        with self.assertRaises(AuthenticationError, msg=msg):
            RETSConnection(
                username=self.username,
                password=self.password,
                login_url=self.url,
                auth_type='oauth'
            )
