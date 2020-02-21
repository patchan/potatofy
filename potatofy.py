import requests
import requests.auth
import json

CLIENT_ID = 'B0RJvfEsABEDcH3EBupD6Ci35V9cFw'
REDIRECT_URI = 'http://localhost:5000/callback'

from flask import Flask
app = Flask(__name__)
@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with Questrade</a>'
    return text % make_authorization_url()

def make_authorization_url():
    from uuid import uuid4
    state = str(uuid4())
    save_created_state(state)
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI
    }
    import urllib
    url = 'https://login.questrade.com/oauth2/authorize?' + urllib.parse.urlencode(params)
    return url

def save_created_state(state):
    pass

def is_valid_state(state):
    return True

if __name__ == '__main__':
    app.run(debug=True, port=5000)

from flask import abort, request
@app.route('/qt_callback')
def qt_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        abort(403)
    code = request.args.get('code')
    access_token = get_token(code)
    return "got an access token! %s" % get_account_info(access_token)

def get_token(code):
    post_data = {
        "client_id": CLIENT_ID,
        "code": code,
        "grant_type": 'authorization_code',
        "redirect_uri": REDIRECT_URI
    }
    import urllib
    response = requests.post('https://login.questrade.com/oauth2/token?' + urllib.parse.urlencode(post_data))
    token_json = response.json()
    return token_json["access_token"]



def getNewAccessToken(refreshToken):
    new_token = requests.get(
        'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token=' + refreshToken)
    new_token = new_token.json()
    with open('token.json') as outfile:
        json.dump(new_token, outfile)
    return new_token

def get_account_info(token):
    url = 'https://api01.iq.questrade.com/accounts'
    header = {'Authorization': token['token_type'] + ' ' + token['access_token']}
    response = requests.get(url, headers=header)
    if response.ok:
        result = response.json()
        return result
    else:
        return "ERROR"


# api_server = 'https://api01.iq.questrade.com/'
# token = {
#   "access_token": "V1xPMqy3djnD8BmbCUXQdE1BbPDI8gHA0",
#   "api_server": "https://api03.iq.questrade.com/",
#   "expires_in": 1800,
#   "refresh_token": "B1L8Lu7YRgE8_tu8rJIxVO_JA_0QUymi0",
#   "token_type": "Bearer"
# }

# get_account_info(token)

# token = getNewAccessToken(token['refresh_token'])
# header = {'Authorization': token['token_type'] + ' ' + token['access_token']}
# url = api_server + 'v1/' + 'accounts'
# url2 = api_server + 'v1/' + 'accounts/51845382/balances'
# url3 = api_server + 'v1/' + 'accounts/51845382/positions'
# print(url)
#
# response = requests.get(url, headers=header)
# response = response.json()
# response2 = requests.get(url2, headers=header)
# response2 = response2.json()
# response3 = requests.get(url3, headers=header)
# response3 = response3.json()
#
# if response:
#     print(response)
# else:
#     print("no")
#
# if response2:
#     print(response2)
# else:
#     print("no")
#
# if response3:
#     print(response3)
# else:
#     print("no")