import requests
import requests.auth
import os
import json
import questrade_api

CLIENT_ID = 'YHvFCEIWtdfoRPu1XbwBpZZ1cA6MlwHC0'
REDIRECT_URI = 'https://patchan.ca/potatofy'

intial_token = 'SZGRBaN1-AABX5cIR5iB1YitvpVnGX7i0'
login_server = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token='
api_server = 'https://api01.iq.questrade.com/'
token = {
  "access_token": "V1xPMqy3djnD8BmbCUXQdE1BbPDI8gHA0",
  "api_server": "https://api03.iq.questrade.com/",
  "expires_in": 1800,
  "refresh_token": "B1L8Lu7YRgE8_tu8rJIxVO_JA_0QUymi0",
  "token_type": "Bearer"
}

TOKEN_PATH = os.path.expanduser('./token/token.json')

def get_access_token(refresh_token):
    response = requests.get(login_server + refresh_token)
    if response.ok:
        response = response.json()
        print(response)
        write_token(response)
    else:
        print('Failed to retrieve access token')

def write_token(token):
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token, f)

def read_token():
    try:
        with open(TOKEN_PATH) as f:
            string = f.read()
            return json.loads(string)
    except IOError:
        print('No token provided and none found at {}'.format(TOKEN_PATH))

def get_account_info(header):
    response = requests.get(api_server + 'v1/accounts', headers=header)
    if response.ok:
        return response.json()
    else:
        new_header = set_header(read_token(), 'refresh')
        return get_account_info(new_header)

def set_header(token, token_type):
    if (token_type == 'access'):
        header = {'Authorization': token['token_type'] + ' ' + token['access_token']}
        return header
    elif (token_type == 'refresh'):
        header = {'Authorization': token['token_type'] + ' ' + token['refresh_token']}
        return header

def get_balance_info(header, account):
    response = requests.get(api_server + 'v1/accounts/' + account + '/balances', headers=header)
    if response.ok:
        return response
    else:
        new_header = set_header(read_token(), 'refresh')
        return get_balance_info(new_header, account)

def set_account(account):
    # TODO
    # ACCOUNT_NUM = account.accounts.

# get_access_token(intial_token)
header = set_header(read_token(), 'access')
print(get_account_info(header))