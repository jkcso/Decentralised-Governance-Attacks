# API KEY: c5b33796-bb72-46c2-98eb-ac52807d08c9
# Sign in to track credits: https://pro.coinmarketcap.com/account
# API Documentation: https://coinmarketcap.com/api/documentation/v1/#section/Introduction
# Live Rankings: https://coinmarketcap.com

MIN_COINBASE_RANKING = ONE_MN = 1
MAX_COINBASE_RANKING = 20
COINBASE_API_KEY = 'c5b33796-bb72-46c2-98eb-ac52807d08c9'
MIN_PRICE = MIN_CIRCULATION = 0

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


# OPTIMISATION that provides two data with one call
def acquire_real_time_data():
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
            'start': str(MIN_COINBASE_RANKING),
            'limit': str(MAX_COINBASE_RANKING),
            'convert': 'GBP'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': COINBASE_API_KEY
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)

            real_time_price = MIN_PRICE
            real_time_circulation = MIN_CIRCULATION

            for i in range(MIN_COINBASE_RANKING, MAX_COINBASE_RANKING):
                if data['data'][i]['name'] == 'Dash':
                    real_time_price = data['data'][i]['quote']['GBP']['price']
                    real_time_circulation = data['data'][i]['circulating_supply']
            return float("{0:.2f}".format(real_time_price)), int(real_time_circulation)

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    except ValueError:
        pass


real_time_data = acquire_real_time_data()
real_time_price = real_time_data[0]
real_time_circulation = real_time_data[1]

print("Real time price", real_time_price)
print("Real time circulation", real_time_circulation)

