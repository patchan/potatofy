import os
import json


class Rebalancer:
    TARGET_PATH = os.path.expanduser('./targets/targets.json')

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.target_alloc = self.load_targets()
        self.buying_power = 0

    def get_buying_power(self):
        return self.portfolio.get_cash() + self.buying_power

    def get_total_holdings(self):
        return self.portfolio.get_total_holdings()

    def get_positions(self):
        return self.portfolio.get_all_positions()

    def get_share_prices(self, positions):
        return self.portfolio.get_broker().get_share_prices(positions)

    # TODO: refactor Portfolio class method here
    def add_cash(self, cash):
        self.buying_power += cash

    def reset_cash(self):
        self.buying_power = 0

    def set_target_alloc(self, ticker, allocation):
        self.target_alloc[ticker] = allocation
        self.save_target_alloc()

    def reset_target_alloc(self):
        self.target_alloc = {}

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
            result = {}
            target_total = self.get_total_holdings() + self.get_buying_power()
            positions = self.get_positions()
            share_data = self.get_share_prices(positions)
            for ticker in share_data:
                symbol = ticker['symbol']
                stock = {'price': ticker['prevDayClosePrice']}
                target_alloc = self.target_alloc[symbol]
                stock['target_alloc'] = target_alloc
                stock['target_pos'] = round(target_alloc / 100 * target_total, 2)
                diff = stock['target_pos'] - positions[symbol]
                stock['amount'] = diff // stock['price']
                result[symbol] = stock
            return result
        else:
            return False

    def calculate_buy_only_purchases(self):
        if self.is_valid_allocation():
            result = {}
            # TODO: implement
            return result
        else:
            return False

