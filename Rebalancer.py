import os
import json

BALANCE_PATH = os.path.expanduser('./balances/balances.json')
POSITIONS_PATH = os.path.expanduser('./positions/positions.json')
BUY_AMOUNT = 0


def read_from_disk(path):
    try:
        with open(path) as file:
            return json.load(file)
    except IOError:
        print('No token provided and none found at {}'.format(path))

def extract_total_holdings(balances):
    total_holdings = 0
    for currency in balances[0]['perCurrencyBalances']:
        if currency['currency'] == 'CAD':
            total_holdings += currency['marketValue']
    return total_holdings

def extract_positions(positions):
    positions_dict = {}
    for position in positions[0]['positions']:
        positions_dict[position['symbol']] = position['currentMarketValue']
    return positions_dict


def set_target_alloc(positions_dict):
    target_allocs = {}
    for k in positions_dict:
        target_allocs[k] = get_target()
    return target_allocs

def get_target():
    target = input("target allocation: ")
    return float(target)

def calculate_alloc(positions, total_holdings):
    allocs = {}
    for k, v in positions.items():
        allocs[k] = v / total_holdings
    return allocs

def input_buy_amount():
    BUY_AMOUNT = input("input buy amount: ")

