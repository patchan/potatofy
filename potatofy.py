from Authenticator import Authenticator
from Rebalancer import Account
from Rebalancer import Rebalancer

auth = Authenticator()
# auth.get_initial_token(initial_token)

account_nums = auth.get_account_nums()
accounts = []
for account_num in account_nums:
    accounts.append(Account(account_num))

for account in accounts:
    test = Rebalancer(account)
    purchases = test.calculate_purchases()
    print(purchases)
