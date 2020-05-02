import requests
import requests.auth
import os
import json
from AuthException import AuthException
from bs4 import BeautifulSoup


class Authenticator:
    LOGIN_SERVER = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token='
    AUTH_SERVER = 'https://login.questrade.com/oauth2/authorize?client_id=B0RJvfEsABEDcH3EBupD6Ci35V9cFw&response_type=token&redirect_uri=https://patchan.ca/potatofy'

    TOKEN_PATH = os.path.expanduser('./token/token.json')

    def __init__(self):
        self.TOKEN = None
        # try:
        #     self.load_token()
        # except:
        #     raise AuthException('unable to authenticate')

    def get_access_token(self):
        return self.TOKEN.get_access_token()

    def get_refresh_token(self):
        return self.TOKEN.get_refresh_token()

    def get_api_server(self):
        return self.TOKEN.get_server()

    def get_token_type(self):
        return self.TOKEN.get_token_type()

    # def login(self):
    #     username = input('enter username: ')
    #     password = input('enter password: ')
    #     self.authorize(username, password)

    def authenticate(self):
        if self.TOKEN is None:
            try:
                self.load_token()
            except:
                raise AuthException('unable to authenticate')

    def authorize(self, username, password):
        session = requests.Session()
        init_resp = self.initialize_session(session)
        login_resp = self.request_login(session, init_resp, username, password)
        security_check = self.request_security_question(session, login_resp)
        auth_response = self.request_security_check(session, security_check)
        final_resp = self.authorize_api(session, auth_response)
        token = self.parse_token(final_resp.url)
        self.save_token(token)

    def initialize_session(self, session):
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
        headers = {'User-Agent': user_agent}
        session.headers.update(headers)
        return session.get(self.AUTH_SERVER)

    def request_login(self, session, response, username, password):
        data = {}
        data['ctl00$DefaultContent$txtUsername'] = username
        data['ctl00$DefaultContent$txtPassword'] = password
        data['ctl00$DefaultContent$btnContinue'] = 'Log in'
        data['ctl00$DefaultContent$txtUsernameHidden'] = ''
        data['ctl00$DefaultContent$hdnIsCaptchaVisible'] = ''
        data['ctl00$DefaultContent$hidResponseRelyingParty'] = '/oauth2/authorize?client_id=B0RJvfEsABEDcH3EBupD6Ci35V9cFw'
        self.set_view_state(response.text, data)
        return session.post(response.url, data=data)

    def request_security_question(self, session, response):
        return session.get(response.url)

    def request_security_check(self, session, response):
        check_html = self.parse_html(response.text)
        question_id = self.extract_question_id(check_html)
        print(self.extract_question(check_html))
        answer = input('enter answer: ')
        data = {}
        data['ctl00$DefaultContent$hdnQuestionID'] = question_id
        data['ctl00$DefaultContent$txtAnswer'] = answer
        data['ctl00_DefaultContent_RadWindowManager1_ClientState'] = ''
        self.set_view_state(response.text, data)
        # view state has a unique EVENTTARGET not in HTML
        data['__EVENTTARGET'] = 'ctl00$DefaultContent$btnContinue'
        return session.post(response.url, data=data)

    def authorize_api(self, session, response):
        data = {'ctl00$DefaultContent$btnAllow': 'Allow'}
        self.set_view_state(response.text, data)
        return session.post(response.url, data=data)

    def set_asp_state(self, data, event_target, event_argument, view_state, view_state_generator, event_validation):
        data['__EVENTTARGET'] = event_target
        data['__EVENTARGUMENT'] = event_argument
        data['__VIEWSTATE'] = view_state
        data['__VIEWSTATEGENERATOR'] = view_state_generator
        data['__EVENTVALIDATION'] = event_validation

    def parse_html(self, text):
        return BeautifulSoup(text, 'html.parser')

    def extract_view_state(self, html):
        return html.find(id='__VIEWSTATE')['value']

    def extract_view_state_generator(self, html):
        return html.find(id='__VIEWSTATEGENERATOR')['value']

    def extract_event_validation(self, html):
        return html.find(id='__EVENTVALIDATION')['value']

    def extract_event_target(self, html):
        return html.find(id='__EVENTTARGET')['value']

    def extract_event_argument(self, html):
        return html.find(id='__EVENTARGUMENT')['value']

    def extract_question(self, html):
        return html.find(class_='question lg').string

    def extract_question_id(self, html):
        return html.find(id='ctl00_DefaultContent_hdnQuestionID')['value']

    def set_view_state(self, text, data):
        html = self.parse_html(text)
        event_target = self.extract_event_target(html)
        event_argument = self.extract_event_argument(html)
        view_state = self.extract_view_state(html)
        view_state_generator = self.extract_view_state_generator(html)
        event_validation = self.extract_event_validation(html)
        self.set_asp_state(data, event_target, event_argument, view_state, view_state_generator, event_validation)

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
        response = requests.get(self.LOGIN_SERVER + self.get_refresh_token())
        if response.ok:
            response = response.json()
            self.save_token(self.create_token(response))
        else:
            print('Failed to retrieve new access token. Login again')
            # self.login()

    # saves Token type as json
    def save_token(self, token):
        self.write_token(token)
        self.TOKEN = token

    # writes Token to TOKEN_PATH as a json
    def write_token(self, token):
        token_json = token.convert_to_json()
        with open(self.TOKEN_PATH, 'w') as file:
            json.dump(token_json, file)

    # tries to read token from disk, prompts login re-authentication if fails
    def load_token(self):
        with open(self.TOKEN_PATH) as file:
            json_token = json.load(file)
            self.TOKEN = self.create_token(json_token)
        # try:
        # return self.read_token()
        # except IOError:
        #     print('No token provided and none found at {}'.format(self.TOKEN_PATH))
            # return None
            # self.login()
        # except ValueError:
        #     print('Invalid token found.')
            # return None
            # self.login()

    # def read_token(self):
    #     with open(self.TOKEN_PATH) as file:
    #         json_token = json.load(file)
    #         return self.create_token(json_token)

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
        header = {'Authorization': self.get_token_type() + ' ' + self.get_access_token()}
        return header

    # request list of accounts
    def request_accounts(self):
        self.authenticate()
        header = self.set_get_header()
        response = requests.get(self.get_api_server() + 'v1/accounts', headers=header)
        if response.ok:
            return response.json()
        else:
            self.get_new_token()
            new_header = self.set_get_header()
            response = requests.get(self.get_api_server() + 'v1/accounts', headers=new_header)
            return response.json()

    # request balances of account
    def request_balances(self, account):
        self.authenticate()
        header = self.set_get_header()
        response = requests.get(self.get_api_server() + 'v1/accounts/' + account + '/balances', headers=header)
        if response.ok:
            return response.json()
        else:
            self.get_new_token()
            new_header = self.set_get_header()
            response = requests.get(self.get_api_server() + 'v1/accounts/' + account + '/balances',
                                    headers=new_header)
            return response.json()

    # request positions in account
    def request_positions(self, account):
        self.authenticate()
        header = self.set_get_header()
        response = requests.get(self.get_api_server() + 'v1/accounts/' + account + '/positions', headers=header)
        if response.ok:
            return response.json()['positions']
        else:
            self.get_new_token()
            new_header = self.set_get_header()
            response = requests.get(self.get_api_server() + 'v1/accounts/' + account + '/positions',
                                    headers=new_header)
            return response.json()['positions']

    # request share information for all positions
    def request_share_prices(self, positions):
        self.authenticate()
        header = self.set_get_header()
        tickers = ""
        for k, v in positions.items():
            tickers += k + ","
        response = requests.get(self.get_api_server() + 'v1/symbols?names=' + tickers, headers=header)
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
