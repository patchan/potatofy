import unittest
from decimal import Decimal

from Broker import Broker
from Portfolio import Account, Portfolio
from tests.MockAuthenticator import MockAuthenticator, load_test_balance, \
    load_test_positions


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        self.broker = Broker()
        self.broker.set_authenticator(MockAuthenticator())
        self.portfolio = Portfolio(self.broker)
        self.portfolio.load_accounts()

    def test_load_accounts(self):
        self.portfolio.load_accounts()
        result = self.portfolio.list_accounts()
        expected = ['111111', '222222']
        self.assertEqual(result, expected)

    def test_get_all_positions(self):
        expected = {}
        for account in self.portfolio.list_accounts():
            positions = load_test_positions(account)
            for position in positions:
                if position['symbol'] not in expected:
                    expected[position['symbol']] = Decimal(
                        position['currentMarketValue']).quantize(
                        Decimal('0.00'))
                else:
                    expected[position['symbol']] += Decimal(
                        position['currentMarketValue']).quantize(
                        Decimal('0.00'))
        result = self.portfolio.get_all_positions()
        self.assertEqual(result, expected)

    def test_get_total_holdings(self):
        expected = 0
        for account in self.portfolio.list_accounts():
            expected += Decimal(
                load_test_balance(account)['combinedBalances'][0][
                    'marketValue']).quantize(Decimal('0.00'))
        result = self.portfolio.get_total_holdings()
        self.assertEqual(result, expected)

    def test_get_cash(self):
        expected = 0
        for account in self.portfolio.list_accounts():
            expected += Decimal(
                load_test_balance(account)['combinedBalances'][0][
                    'cash']).quantize(Decimal('0.00'))
        result = self.portfolio.get_cash()
        self.assertEqual(result, expected)


class TestAccount(unittest.TestCase):

    def setUp(self):
        self.account_id = '111111'
        self.account = Account(load_test_balance(self.account_id),
                               load_test_positions(self.account_id))

    def test_get_balance(self):
        expected = load_test_balance(self.account_id)
        result = self.account.get_balance()
        self.assertEqual(result, expected)

    def test_get_total_holdings(self):
        expected = Decimal(
            load_test_balance(self.account_id)['combinedBalances'][0][
                'marketValue']).quantize(Decimal('0.00'))
        result = self.account.get_total_holdings()
        self.assertEqual(result, expected)

    def test_get_positions(self):
        positions = load_test_positions(self.account_id)
        expected = {}
        for position in positions:
            expected[position['symbol']] = Decimal(
                position['currentMarketValue']).quantize(Decimal('0.00'))
        result = self.account.get_positions()
        self.assertEqual(result, expected)

    def test_get_cash(self):
        balance = load_test_balance(self.account_id)
        expected = Decimal(balance['combinedBalances'][0]['cash']).quantize(
            Decimal('0.00'))
        result = self.account.get_cash()
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
