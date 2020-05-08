import unittest

from Broker import Broker


class TestRebalancer(unittest.TestCase):

    def setUp(self):
        self.broker = Broker()

