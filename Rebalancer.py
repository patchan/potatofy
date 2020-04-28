from Authenticator import Authenticator


class Account:
    def __init__(self, id):
        self.id = id
        self.balance = self.set_balance()
        self.positions = self.set_positions()

    def get_account(self):
        return self.id

    def get_balance(self):
        return self.balance

    def set_balance(self):
        return Authenticator().get_balance_info(self.id)

    def set_positions(self):
        return Authenticator().get_positions(self.id)

    def get_total_holdings(self):
        total_holdings = 0
        for currency in self.balance['perCurrencyBalances']:
            if currency['currency'] == 'CAD':
                total_holdings += currency['marketValue']
        return total_holdings

    def get_positions(self):
        positions_dict = {}
        for position in self.positions:
            positions_dict[position['symbol']] = position['currentMarketValue']
        return positions_dict

    def get_cash(self):
        for currency in self.balance['perCurrencyBalances']:
            if currency['currency'] == 'CAD':
                return currency['cash']
            else:
                return 0


class Rebalancer:

    def __init__(self, account):
        self.positions = account.get_positions()
        self.total_holdings = account.get_total_holdings()
        self.buying_power = account.get_cash()
        self.target_alloc = {}
        self.set_target_alloc()

    def set_target_alloc(self):
        for k in self.positions:
            self.target_alloc[k] = float(input("target allocation for " + k + ": "))

    def calculate_alloc(self):
        allocs = {}
        for k, v in self.positions.items():
            allocs[k] = v / self.total_holdings
        return allocs

    def calculate_purchases(self):
        target = self.total_holdings + self.buying_power
        target_pos = {}
        diff = {}
        shares = {}
        share_prices = {}
        share_data = Authenticator().get_share_prices(self.positions)
        for ticker in share_data:
            share_prices[ticker['symbol']] = ticker['prevDayClosePrice']
        for k, v in self.target_alloc.items():
            target_pos[k] = v * target
        for k, v in target_pos.items():
            diff[k] = v - self.positions[k]
        for k, v in diff.items():
            shares[k] = diff[k] // share_prices[k]
        return shares
