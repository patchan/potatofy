from Authenticator import Authenticator
from Rebalancer import Account
from Rebalancer import Rebalancer
import os

initial_token = 'ZjUBG48pUe808yQBWotMrUw8tC9szwaS0'
BALANCE_PATH = os.path.expanduser('./balances/balances.json')
POSITIONS_PATH = os.path.expanduser('./positions/positions.json')


auth = Authenticator()
# auth.get_initial_token(initial_token)

account_info = auth.get_account_info()
account_nums = auth.get_account_num(account_info)
accounts = []
for account_num in account_nums:
    accounts.append(Account(account_num))

for account in accounts:
    test = Rebalancer(account)
    purchases = test.calculate_purchases()
    print(purchases)
