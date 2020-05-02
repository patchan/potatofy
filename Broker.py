from Authenticator import Authenticator
import os
import json


class Broker:
    BALANCE_PATH = os.path.expanduser('./balances/balances.json')
    POSITIONS_PATH = os.path.expanduser('./positions/positions.json')

    def __init__(self):
        self.auth = Authenticator()

    def authenticate(self, username, password):
        self.auth.authorize(username, password)

    def get_accounts(self):
        return self.auth.request_accounts()

    def get_balance(self, account_id):
        balance = self.auth.request_balances(account_id)
        self.save_balance(balance)
        return balance

    def get_positions(self, account_id):
        positions = self.auth.request_positions(account_id)
        self.save_positions(positions)
        return positions

    def get_share_prices(self, positions):
        return self.auth.request_share_prices(positions)

    def save_balance(self, balances):
        with open(self.BALANCE_PATH, 'w') as file:
            json.dump(balances, file)

    def save_positions(self, positions):
        with open(self.POSITIONS_PATH, 'w') as file:
            json.dump(positions, file)
