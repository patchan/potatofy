import unittest

from Broker import Broker
from error.AuthError import AuthError
from error.LoginError import LoginError
from tests.MockAuthenticator import MockAuthenticator, load_test_balance, \
    load_test_positions


class TestBroker(unittest.TestCase):

    def setUp(self):
        self.broker = Broker()
        self.broker.set_authenticator(MockAuthenticator())

    def test_authenticate(self):
        username = 'username'
        password = 'password'
        self.assertEqual(self.broker.authenticate(username, password),
                         'security question')
        with self.assertRaises(LoginError):
            self.broker.authenticate(username, username)

    def test_authenticate_two_factor(self):
        self.assertTrue(self.broker.authenticate_two_factor('security answer'))
        with self.assertRaises(AuthError):
            self.broker.authenticate_two_factor('wrong answer')

    def test_get_accounts(self):
        expected = ['111111', '222222']
        accounts = self.broker.get_accounts()
        result = []
        for account in accounts:
            result.append(account['number'])
        self.assertEqual(result, expected)

    def test_get_balance(self):
        account = '111111'
        expected = load_test_balance(account)
        result = self.broker.get_balance(account)
        self.assertEqual(result, expected)

    def test_get_positions(self):
        account = '111111'
        expected = load_test_positions(account)
        result = self.broker.get_positions('111111')
        self.assertEqual(result, expected)

    def test_get_share_prices(self):
        positions = {}
        self.broker.get_share_prices(positions)


if __name__ == '__main__':
    unittest.main()
