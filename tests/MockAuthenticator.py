import json
import os

from Authenticator import Authenticator
from error.AuthError import AuthError
from error.LoginError import LoginError


def load_test_accounts():
    with open(os.path.expanduser('./data/accounts.json')) as file:
        return json.load(file)['accounts']


def load_test_balance(account):
    with open(os.path.expanduser(
            './data/balances_' + account + '.json')) as file:
        return json.load(file)


def load_test_positions(account):
    with open(os.path.expanduser(
            './data/positions_' + account + '.json')) as file:
        return json.load(file)['positions']


def load_test_prices():
    with open(os.path.expanduser('./data/prices.json')) as file:
        return json.load(file)['symbols']


class MockAuthenticator(Authenticator):

    def __init__(self):
        self.accounts = None
        self.balances = None
        self.positions = None

    def login(self, username, password):
        if username == 'username' and password == 'password':
            return 'security question'
        else:
            raise LoginError('invalid username or password')

    def two_factor(self, answer):
        if answer == 'security answer':
            return True
        else:
            raise AuthError('failed to authenticate')

    def request_accounts(self):
        return load_test_accounts()

    def request_balances(self, account):
        return load_test_balance(account)

    def request_positions(self, account):
        return load_test_positions(account)

    def request_share_prices(self, positions):
        return load_test_prices()
