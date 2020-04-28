import requests
import requests.auth
import os
import json


class Authenticator:
    LOGIN_SERVER = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token='
    API_SERVER = 'https://api01.iq.questrade.com/'
    LOGIN_URL = 'https://login.questrade.com/APISignin.aspx?ReturnUrl=/oauth2/authorize?client_id=B0RJvfEsABEDcH3EBupD6Ci35V9cFw&response_type=token&redirect_uri=https://patchan.ca/potatofy'
    ACCEPT_LINK = 'https://login.questrade.com/OAuth2/authorize_handler?response_type=token&redirect_uri=https://patchan.ca/potatofy&device=Windows+NT+4.0+Firefox&client_id=B0RJvfEsABEDcH3EBupD6Ci35V9cFw&scope=&state='

    TOKEN_PATH = os.path.expanduser('./token/token.json')
    BALANCE_PATH = os.path.expanduser('./balances/balances.json')
    POSITIONS_PATH = os.path.expanduser('./positions/positions.json')

    def authorize(self):
        USERNAME = input("enter username: ")
        PASSWORD = input("enter password: ")
        data = {'ctl00$DefaultContent$txtUsername': USERNAME, 'ctl00$DefaultContent$txtPassword': PASSWORD,
                'ctl00$DefaultContent$hidResponseRelyingParty': '/oauth2/authorize?client_id=B0RJvfEsABEDcH3EBupD6Ci35V9cFw&response_type=token&redirect_uri=https://patchan.ca/potatofy'}
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
        # response = requests.post(self.LOGIN_URL, params=data)
        session = requests.Session()
        session.get(self.LOGIN_URL, headers=header)
        response = session.post(self.LOGIN_URL, data=data, headers=header)
        # response = session.get(self.ACCEPT_LINK)
        print(response.body)

    def get_initial_token(self, refresh_token):
        response = requests.get(self.LOGIN_SERVER + refresh_token)
        if response.ok:
            response = response.json()
            self.write_token(response)
        else:
            print('Failed to retrieve initial access token')

    def get_new_token(self, token):
        response = requests.get(self.LOGIN_SERVER + token["refresh_token"])
        if response.ok:
            response = response.json()
            self.write_token(response)
        else:
            print('Failed to retrieve new access token')

    def write_token(self, token):
        with open(self.TOKEN_PATH, 'w') as file:
            json.dump(token, file)

    def read_token(self):
        try:
            with open(self.TOKEN_PATH) as file:
                return json.load(file)
        except IOError:
            print('No token provided and none found at {}'.format(self.TOKEN_PATH))

    def get_api_server(self):
        try:
            with open(self.TOKEN_PATH) as file:
                loaded_json = json.load(file)
                api_server = loaded_json["api_server"]
                return api_server
        except IOError:
            print('No token provided and none found at {}'.format(self.TOKEN_PATH))

    def get_account_info(self):
        header = self.set_header(self.read_token())
        print(header)
        response = requests.get(self.get_api_server() + 'v1/accounts', headers=header)
        if response.ok:
            return response.json()
        else:
            self.get_new_token(self.read_token())
            new_token = self.read_token()
            print(new_token)
            new_header = self.set_header(new_token)
            print(new_header)
            response = requests.get(self.get_api_server() + 'v1/accounts', headers=new_header)
            print(response)
            return response.json()

    def set_header(self, token):
        header = {'Authorization': token["token_type"] + ' ' + token["access_token"]}
        return header

    def get_balance_info(self, account):
        header = self.set_header(self.read_token())
        response = requests.get(self.get_api_server() + 'v1/accounts/' + account + '/balances', headers=header)
        if response.ok:
            return response.json()
        else:
            self.get_new_token(self.read_token())
            new_token = self.read_token()
            new_header = self.set_header(new_token)
            response = requests.get(self.get_api_server() + 'v1/accounts/' + account + '/balances',
                                    headers=new_header)
            return response.json()

    def get_account_num(self, accounts_info):
        accounts = accounts_info['accounts']
        result = []
        for account in accounts:
            result.append(account["number"])
        return result

    def save_balance_info(self, balances):
        with open(self.BALANCE_PATH, 'w') as file:
            json.dump(balances, file)

    def get_positions(self, account):
        header = self.set_header(self.read_token())
        response = requests.get(self.get_api_server() + 'v1/accounts/' + account + '/positions', headers=header)
        if response.ok:
            return response.json()['positions']
        else:
            self.get_new_token(self.read_token())
            new_token = self.read_token()
            new_header = self.set_header(new_token)
            response = requests.get(self.get_api_server() + 'v1/accounts/' + account + '/positions',
                                    headers=new_header)
            return response.json()['positions']

    def save_positions(self, positions):
        with open(self.POSITIONS_PATH, 'w') as file:
            json.dump(positions, file)

    def get_share_prices(self, positions):
        header = self.set_header(self.read_token())
        tickers = ""
        for k, v in positions.items():
            tickers += k + ","
        response = requests.get(self.get_api_server() + 'v1/symbols?names=' + tickers, headers=header)
        if response.ok:
            return response.json()['symbols']
        else:
            print("ERROR: failed to get share prices")