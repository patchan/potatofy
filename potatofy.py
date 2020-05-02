from Rebalancer import Rebalancer
from Portfolio import Portfolio
from Broker import Broker
from GUI import *

# reb = Rebalancer(portfolio)
# reb.set_target_alloc()
# print(reb.calculate_purchases())

broker = Broker()
portfolio = Portfolio(broker)
rebalancer = Rebalancer(portfolio)
gui = GUI(broker, portfolio, rebalancer)
