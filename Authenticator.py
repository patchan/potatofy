import sys
from pathlib import Path

import requests
import requests.auth
import json
from bs4 import BeautifulSoup

from error.AuthError import AuthError
from error.LoginError import LoginError

LOGIN_SERVER = 'https://login.questrade.com/oauth2/' \
               'token?grant_type=refresh_token&refresh_token='
AUTH_SERVER = 'https://login.questrade.com/oauth2/' \
              'authorize?client_id=B0RJvfEsABEDcH3EBupD6Ci35V9cFw' \
              '&response_type=token' \
              '&redirect_uri=https://patchan.github.io/potatofy/'

TOKEN_PARENT_DIR = 'token'
TOKEN_PATH = 'token/token.json'


def get_resource_path(path):
    ROOT_PATH = Path(__file__).parent.absolute()
    """
    Returns a Path representing where to look for resource files for the
    program, such as databases or images.
    This location changes if the program is run from an application built
    with pyinstaller.
    """

    if hasattr(sys, '_MEIPASS'):  # being run from a pyinstall app
        return Path(sys._MEIPASS) / Path(path)
    return ROOT_PATH / Path(path)


class Authenticator:

    def __init__(self):
        self.TOKEN = None
        self.session = None
        self.last_response = None

    def get_access_token(self):
        return self.TOKEN.get_access_token()

    def get_refresh_token(self):
        return self.TOKEN.get_refresh_token()

    def get_api_server(self):
        return self.TOKEN.get_server()

    def get_token_type(self):
        return self.TOKEN.get_token_type()

    def authenticate(self):
        if self.TOKEN is None:
            try:
                self.load_token()
            except:
                raise AuthError('unable to authenticate')

    def login(self, username, password):
        self.initialize_session()
        try:
            self.request_login(username, password)
            self.request_security_question()
        except:
            raise LoginError('unable to log in')

    def two_factor(self, answer):
        try:
            self.request_security_check(answer)
            self.authorize_api()
            token = self.parse_token(self.last_response.url)
            self.save_token(token)
            return True
        except:
            raise AuthError('could not create token')

    def initialize_session(self):
        self.session = None
        self.session = requests.Session()
        self.last_response = None
        self.TOKEN = None
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
                     '(KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
        headers = {'User-Agent': user_agent}
        self.session.headers.update(headers)
        self.last_response = self.session.get(AUTH_SERVER)

    def request_login(self, username, password):
        data = {'UserId': username,
                'Password': password,
                'button': 'login',
                'Captcha': ''
                }
        self.set_return_url(self.last_response.text, data)
        self.set_verification_token(self.last_response.text, data)
        self.last_response = self.session.post('https://login.questrade.com/Account/Login',
                                               data=data)
        if self.last_response.url != \
                'https://login.questrade.com/Account/LoginMfa':
            raise LoginError('invalid username or password')

    def request_security_question(self):
        self.last_response = self.session.get(self.last_response.url)
        print(self.last_response)
        data = {'provider': 'PhoneSms',
                'button': 'submit'
                }
        self.set_verification_token(self.last_response.text, data)
        self.last_response = self.session.post('https://login.questrade.com/Account/ChooseMfaProvider', data=data)
        print(self.last_response.url)

    def request_security_check(self, answer):
        data = {'Provider': 'PhoneSms',
                'Code': answer,
                'button': 'submit',
                'RememberDevice': 'false'
                }
        self.set_verification_token(self.last_response.text, data)
        self.last_response = self.session.post(self.last_response.url,
                                               data=data)

    def authorize_api(self):
        data = {'__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                'ctl00$DefaultContent$btnAllow': 'Allow',
                'ctl00$DefaultContent$txtDevice': 'Mac+OS+X+10.15+Firefox'
                }
        self.set_asp_state(self.last_response.text, data)
        self.last_response = self.session.post(self.last_response.url, data=data)

    def extract_view_state(self, html):
        return html.find(id='__VIEWSTATE')['value']

    def extract_view_state_generator(self, html):
        return html.find(id='__VIEWSTATEGENERATOR')['value']

    def extract_event_validation(self, html):
        return html.find(id='__EVENTVALIDATION')['value']

    def set_return_url(self, text, data):
        html = self.parse_html(text)
        return_url = self.extract_return_url(html)
        data['ReturnUrl'] = return_url

    def set_verification_token(self, text, data):
        html = self.parse_html(text)
        request_verification_token = self.extract_request_verification_token(html)
        data['__RequestVerificationToken'] = request_verification_token

    def set_asp_state(self, text, data):
        html = self.parse_html(text)
        data['__VIEWSTATE'] = self.extract_view_state(html)
        data['__VIEWSTATEGENERATOR'] = self.extract_view_state_generator(html)
        data['__EVENTVALIDATION'] = self.extract_event_validation(html)

    def parse_html(self, text):
        return BeautifulSoup(text, 'html.parser')

    def extract_return_url(self, html):
        return html.find(id='ReturnUrl')['value']

    def extract_request_verification_token(self, html):
        return html.find('input', {'name': '__RequestVerificationToken'})['value']

    def parse_token(self, url):
        split_url = url.split('#')
        params = split_url[1].split('&')
        access = params[0].split('=')[1]
        refresh = params[1].split('=')[1]
        token_type = params[2].split('=')[1]
        expiry = params[3].split('=')[1]
        server = params[4].split('=')[1]
        token = Token(access, refresh, token_type, expiry, server)
        return token

    # uses loaded refresh token to generate a new access token
    # else prompts login for re-authentication
    def get_new_token(self):
        response = requests.post(LOGIN_SERVER + self.get_refresh_token())
        if response.ok:
            response = response.json()
            self.save_token(self.create_token(response))
        else:
            raise AuthError('Failed to retrieve new access token. Login again')

    # saves Token type as json
    def save_token(self, token):
        self.write_token(token)
        self.TOKEN = token

    # writes Token to TOKEN_PATH as a json
    def write_token(self, token):
        token_json = token.convert_to_json()
        Path(get_resource_path(TOKEN_PARENT_DIR)).mkdir(parents=True, exist_ok=True)
        with open(get_resource_path(TOKEN_PATH), 'w') as file:
            json.dump(token_json, file)

    # tries to read token from disk, prompts login re-authentication if fails
    def load_token(self):
        with open(get_resource_path(TOKEN_PATH)) as file:
            json_token = json.load(file)
            self.TOKEN = self.create_token(json_token)

    # creates a Token object from json
    def create_token(self, json_token):
        access = json_token['access_token']
        refresh = json_token['refresh_token']
        token_type = json_token['token_type']
        expiry = json_token['expires_in']
        server = json_token['api_server']
        token = Token(access, refresh, token_type, expiry, server)
        return token

    # sets GET request header from self.TOKEN
    def set_get_header(self):
        header = {
            'Authorization': self.get_token_type()
                             + ' '
                             + self.get_access_token()}
        return header

    # request list of accounts
    def request_accounts(self):
        self.authenticate()
        header = self.set_get_header()
        response = requests.get(self.get_api_server() + 'v1/accounts',
                                headers=header)
        if response.ok:
            return response.json()['accounts']
        else:
            self.get_new_token()
            new_header = self.set_get_header()
            response = requests.get(self.get_api_server() + 'v1/accounts',
                                    headers=new_header)
            return response.json()['accounts']

    # request balances of account
    def request_balances(self, account):
        self.authenticate()
        header = self.set_get_header()
        response = requests.get(
            self.get_api_server() + 'v1/accounts/' + account + '/balances',
            headers=header)
        if response.ok:
            return response.json()
        else:
            self.get_new_token()
            new_header = self.set_get_header()
            response = requests.get(
                self.get_api_server() + 'v1/accounts/' + account + '/balances',
                headers=new_header)
            return response.json()

    # request list of positions in account
    def request_positions(self, account):
        self.authenticate()
        header = self.set_get_header()
        response = requests.get(
            self.get_api_server() + 'v1/accounts/' + account + '/positions',
            headers=header)
        if response.ok:
            return response.json()['positions']
        else:
            self.get_new_token()
            new_header = self.set_get_header()
            response = requests.get(
                self.get_api_server() + 'v1/accounts/'
                + account + '/positions',
                headers=new_header)
            return response.json()['positions']

    # request share information for all positions
    def request_share_prices(self, positions):
        self.authenticate()
        header = self.set_get_header()
        tickers = ""
        for k in positions:
            tickers += k + ","
        response = requests.get(
            self.get_api_server() + 'v1/symbols?names=' + tickers,
            headers=header)
        if response.ok:
            return response.json()['symbols']
        else:
            print("ERROR: failed to get share prices")


class Token:

    def __init__(self, access, refresh, token_type, expiry, server):
        self.access = access
        self.refresh = refresh
        self.token_type = token_type
        self.expiry = expiry
        self.server = server

    def get_access_token(self):
        return self.access

    def get_refresh_token(self):
        return self.refresh

    def get_token_type(self):
        return self.token_type

    def get_expiry(self):
        return self.expiry

    def get_server(self):
        return self.server

    def convert_to_json(self):
        token = {'access_token': self.get_access_token(),
                 "token_type": self.get_token_type(),
                 "expires_in": self.get_expiry(),
                 "refresh_token": self.get_refresh_token(),
                 "api_server": self.get_server()}
        return token
