import os
import json

from Authenticator import Authenticator

BALANCE_PATH = os.path.expanduser('./balances/balances.json')
POSITIONS_PATH = os.path.expanduser('./positions/positions.json')


class Broker:

    def __init__(self):
        self.auth = Authenticator()

    def set_authenticator(self, auth):
        self.auth = auth

    def authenticate(self, username, password):
        return self.auth.login(username, password)

    def authenticate_two_factor(self, answer):
        return self.auth.two_factor(answer)

    def get_accounts(self):
        return self.auth.request_accounts()

    def get_balance(self, account_id):
        balance = self.auth.request_balances(account_id)
        return balance

    def get_positions(self, account_id):
        positions = self.auth.request_positions(account_id)
        return positions

    def get_share_prices(self, positions):
        return self.auth.request_share_prices(positions)

    # def save_balance(self, balances):
    #     with open(BALANCE_PATH, 'w') as file:
    #         json.dump(balances, file)
    #
    # def save_positions(self, positions):
    #     with open(POSITIONS_PATH, 'w') as file:
    #         json.dump(positions, file)
