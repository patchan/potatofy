import os
import json


class Rebalancer:
    TARGET_PATH = os.path.expanduser('./targets/targets.json')

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.target_alloc = self.load_targets()

    # def get_allocator(self):
    #     return self.allocator
    #
    # def reset_allocator(self):
    #     self.allocator = 100

    def get_buying_power(self):
        return self.portfolio.get_cash()

    def get_total_holdings(self):
        return self.portfolio.get_total_holdings()

    def get_positions(self):
        return self.portfolio.get_all_positions()

    def get_share_prices(self, positions):
        return self.portfolio.get_broker().get_share_prices(positions)

    # TODO: refactor Portfolio class method here
    def add_cash(self, cash):
        self.buying_power += cash

    def set_target_alloc(self, ticker, allocation):
        self.target_alloc[ticker] = allocation
        self.save_target_alloc()

    def reset_target_alloc(self):
        self.target_alloc = {}
        self.allocator = 100
        # TODO: delete alloc file

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
        positions = self.get_positions()
        for k, v in positions.items():
            alloc[k] = v / self.get_total_holdings()
        return alloc

    def is_valid_allocation(self):
        total = 0.0
        for ticker in self.target_alloc:
            total += self.target_alloc[ticker]
        return total == 100.0

    def calculate_purchases(self):
        if self.is_valid_allocation():
            target = self.get_total_holdings() + self.get_buying_power()
            target_pos = {}
            diff = {}
            shares = {}
            share_prices = {}
            positions = self.get_positions()
            share_data = self.get_share_prices(positions)
            for ticker in share_data:
                share_prices[ticker['symbol']] = ticker['prevDayClosePrice']
            for k, v in self.target_alloc.items():
                target_pos[k] = v / 100 * target
            for k, v in target_pos.items():
                diff[k] = v - positions[k]
            for k, v in diff.items():
                shares[k] = diff[k] // share_prices[k]
            return shares
        else:
            return False
