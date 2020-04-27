import Authenticator
import Rebalancer
import os

initial_token = 'ASk8PUcDY-4bfZlkkVMC6OhJWVnSJFOA0'
BALANCE_PATH = os.path.expanduser('./balances/balances.json')
POSITIONS_PATH = os.path.expanduser('./positions/positions.json')

# Authenticator.get_initial_token(initial_token)

account_info = Authenticator.get_account_info()
account_nums = Authenticator.get_account_num(account_info)
Authenticator.save_balance_info(Authenticator.get_balance_info(account_nums))
Authenticator.save_positions(Authenticator.get_positions(account_nums))

balances = Rebalancer.read_from_disk(BALANCE_PATH)
positions = Rebalancer.read_from_disk(POSITIONS_PATH)

total_holdings = Rebalancer.extract_total_holdings(balances)
positions_dict = Rebalancer.extract_positions(positions)

allocations = Rebalancer.calculate_alloc(positions_dict, total_holdings)
target_allocations = Rebalancer.set_target_alloc(positions_dict)