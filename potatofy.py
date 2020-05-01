from Rebalancer import Rebalancer
from Portfolio import Portfolio
from GUI import *

# auth = Authenticator()
# # auth.get_initial_token(initial_token)
#
# account_nums = auth.get_account_nums()
# accounts = []
# for account_num in account_nums:
#     accounts.append(Account(account_num))
#
# for account in accounts:
#     test = Rebalancer(account)
#     purchases = test.calculate_purchases()
#     print(purchases)
portfolio = Portfolio()
reb = Rebalancer(portfolio)
reb.set_target_alloc()
print(reb.calculate_purchases(portfolio))

gui = GUI()
