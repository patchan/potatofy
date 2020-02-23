import requests
import requests.auth
import os
import json

initial_token = 'n6fuHb3yE8LundlvCEpNdUGvqAFKW6cS0'
login_server = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token='
api_server = 'https://api01.iq.questrade.com/'

TOKEN_PATH = os.path.expanduser('./token/token.json')
BALANCE_PATH = os.path.expanduser('./balances/balances.json')

def get_intial_token(refresh_token):
    response = requests.get(login_server + refresh_token)
    if response.ok:
        response = response.json()
        write_token(response)
    else:
        print('Failed to retrieve access token')

def get_new_token(token):
    response = requests.get(login_server + token["refresh_token"])
    if response.ok:
        response = response.json()
        write_token(response)
    else:
        print('Failed to retrieve access token')

def write_token(token):
    with open(TOKEN_PATH, 'w') as file:
        json.dump(token, file)

def read_token():
    try:
        with open(TOKEN_PATH) as file:
            return json.load(file)
    except IOError:
        print('No token provided and none found at {}'.format(TOKEN_PATH))

def get_api_server():
    try:
        with open(TOKEN_PATH) as file:
            loaded_json = json.load(file)
            api_server = loaded_json["api_server"]
            return api_server
    except IOError:
        print('No token provided and none found at {}'.format(TOKEN_PATH))

def get_account_info():
    header = set_header(read_token())
    print(header)
    response = requests.get(get_api_server() + 'v1/accounts', headers=header)
    if response.ok:
        return response.json()
    else:
        get_new_token(read_token())
        new_token = read_token()
        print(new_token)
        new_header = set_header(new_token)
        print(new_header)
        response = requests.get(get_api_server() + 'v1/accounts', headers=new_header)
        print(response)
        return response.json()

def set_header(token):
    header = {'Authorization': token["token_type"] + ' ' + token["access_token"]}
    return header

def get_balance_info(accounts):
    result = []
    for account in accounts:
        header = set_header(read_token())
        response = requests.get(get_api_server() + 'v1/accounts/' + account + '/balances', headers=header)
        if response.ok:
            result.append(response.json())
        else:
            get_new_token(read_token())
            new_token = read_token()
            new_header = set_header(new_token)
            response = requests.get(get_api_server() + 'v1/accounts/' + account + '/balances', headers=new_header)
            result.append(response.json())
    return result

def get_account_num(accounts_info):
    accounts = accounts_info['accounts']
    result = []
    for account in accounts:
        result.append(account["number"])
    return result

def save_balance_info(balances):
    with open(BALANCE_PATH, 'w') as file:
            json.dump(balances, file)

'''
this is only necessary to get the intial access token manually
'''
get_intial_token(initial_token)
# '''
account_info = get_account_info()
account_nums = get_account_num(account_info)
save_balance_info(get_balance_info(account_nums))