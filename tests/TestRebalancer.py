import unittest

from Broker import Broker
from Portfolio import Portfolio
from Rebalancer import Rebalancer
from tests.MockAuthenticator import MockAuthenticator


class TestRebalancer(unittest.TestCase):

    def setUp(self):
        self.broker = Broker()
        self.broker.set_authenticator(MockAuthenticator())
        self.portfolio = Portfolio(self.broker)
        self.portfolio.load_accounts()
        self.rebalancer = Rebalancer(self.portfolio)

