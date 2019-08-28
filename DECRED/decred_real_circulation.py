import json
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

MIN_COINBASE_RANKING = 1
MAX_COINBASE_RANKING = 70

COINBASE_API_KEY = 'c5b33796-bb72-46c2-98eb-ac52807d08c9'
MIN_CIRCULATION = 0


def acquire_real_time_circulation():

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

            real_time_circulation = MIN_CIRCULATION

            for i in range(MIN_COINBASE_RANKING, MAX_COINBASE_RANKING):
                if data['data'][i]['name'] == 'Decred':
                    real_time_circulation = data['data'][i]['circulating_supply']

            global IS_CIRCULATION_REAL
            IS_CIRCULATION_REAL = True
            return int(real_time_circulation)

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    except ValueError:
        pass


p = acquire_real_time_circulation()
print(p)
