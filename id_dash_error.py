# API KEY: c5b33796-bb72-46c2-98eb-ac52807d08c9
# Sign in to track credits: https://pro.coinmarketcap.com/account
# API Documentation: https://coinmarketcap.com/api/documentation/v1/#section/Introduction
# Live Rankings: https://coinmarketcap.com

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
    'start': '1',
    'limit': '20',
    'convert': 'GBP'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'c5b33796-bb72-46c2-98eb-ac52807d08c9',
}

session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    for i in range(1, 20):
        if data['data'][i]['name'] == 'Dash':
            # print(data['data'][i])  # Test providing all Dash's fields
            print(data['data'][i]['quote']['GBP']['price'])  # GBP Price
            print(data['data'][i]['circulating_supply'])  # Coins in Circulation
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
