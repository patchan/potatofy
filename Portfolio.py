from decimal import Decimal


class Portfolio:

    def __init__(self, broker):
        # initialize fields
        self.accounts = {}
        self.broker = broker

    def get_broker(self):
        return self.broker

    def load_accounts(self):
        accounts = self.broker.get_accounts()
        for account in accounts:
            account_id = account['number']
            balance = self.broker.get_balance(account_id)
            positions = self.broker.get_positions(account_id)
            self.accounts[account_id] = Account(balance, positions)

    def get_account(self, account_id):
        return self.accounts[account_id]

    def list_accounts(self):
        return list(self.accounts.keys())

    def get_all_positions(self):
        positions = {}
        for account in self.accounts:
            account_pos = self.get_account(account).get_positions()
            for k, v in account_pos.items():
                if k not in positions:
                    positions[k] = v
                else:
                    positions[k] += v
        return positions

    def get_total_holdings(self):
        holdings = 0
        for account in self.accounts:
            holdings += self.get_account(account).get_total_holdings()
        return holdings

    def get_cash(self):
        total_cash = 0
        for account in self.accounts:
            total_cash += self.get_account(account).get_cash()
        return total_cash


class Account:
    def __init__(self, balance, positions):
        self.balance = balance
        self.positions = positions

    def get_balance(self):
        return self.balance

    def get_total_holdings(self):
        total_holdings = Decimal(0)
        for currency in self.balance['combinedBalances']:
            if currency['currency'] == 'CAD':
                total_holdings += Decimal(currency['marketValue']).quantize(Decimal('0.00'))
        return total_holdings

    def get_positions(self):
        positions_dict = {}
        for position in self.positions:
            positions_dict[position['symbol']] = Decimal(position['currentMarketValue']).quantize(Decimal('0.00'))
        return positions_dict

    def get_cash(self):
        for currency in self.balance['perCurrencyBalances']:
            if currency['currency'] == 'CAD':
                return Decimal(currency['cash']).quantize(Decimal('0.00'))
            else:
                return 0
