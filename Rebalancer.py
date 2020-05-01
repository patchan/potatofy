from Broker import Broker
import os
import json


class Rebalancer:
    TARGET_PATH = os.path.expanduser('./targets/targets.json')

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.positions = portfolio.get_all_positions()
        self.total_holdings = portfolio.get_total_holdings()
        self.buying_power = portfolio.get_cash()
        self.target_alloc = self.load_targets()

    def get_buying_power(self):
        return self.buying_power

    def add_cash(self, cash):
        self.buying_power += cash

    def set_target_alloc(self):
        for k in self.positions:
            self.target_alloc[k] = float(input("target allocation for " + k + ": "))
        self.save_target_alloc()

    def save_target_alloc(self):
        with open(self.TARGET_PATH, 'w') as file:
            json.dump(self.target_alloc, file)

    def load_targets(self):
        try:
            with open(self.TARGET_PATH) as file:
                return json.load(file)
        except IOError:
            print('No target allocations found at {}'.format(self.TARGET_PATH))
            return {}

    def calculate_alloc(self):
        alloc = {}
        for k, v in self.positions.items():
            alloc[k] = v / self.total_holdings
        return alloc

    # TODO: add functionality for selecting certain accounts to rebalance
    def calculate_purchases(self):
        target = self.total_holdings + self.buying_power
        target_pos = {}
        diff = {}
        shares = {}
        share_prices = {}
        share_data = Broker().get_share_prices(self.positions)
        for ticker in share_data:
            share_prices[ticker['symbol']] = ticker['prevDayClosePrice']
        for k, v in self.target_alloc.items():
            target_pos[k] = v * target
        for k, v in target_pos.items():
            diff[k] = v - self.positions[k]
        for k, v in diff.items():
            shares[k] = diff[k] // share_prices[k]
        return shares
