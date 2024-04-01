from settings import lat_lon, api_key
import requests
import json
import datetime
import pickle

import logging
logging.basicConfig(format='%(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

data = ''
last_hit = datetime.datetime(1900, 1, 1)

def get_weather():
    global data
    global last_hit

    now = datetime.datetime.now()
    data_age = now - last_hit
    is_old = data_age > datetime.timedelta(minutes=60)

    if is_old:
        try:
            with open('weather_timestamp.pickle', 'rb') as f:
                last_hit = pickle.load(f)
                logger.info(f'{last_hit=}')
                data_age = now - last_hit
                is_old = data_age > datetime.timedelta(minutes=60)
        except (FileNotFoundError, EOFError):
            pass

    if is_old: # free tier only gets 25 api hits a day
        try:
            url = f'http://dataservice.accuweather.com/forecasts/v1/minute?q={lat_lon}&apikey={api_key}'
            headers = {'accept-encoding': 'gzip'}
            r = requests.get(url, headers=headers)
            data = r.json()
            logger.info(f"API hits left {r.headers['RateLimit-Remaining']}/{r.headers['RateLimit-Limit']}")

            with open('weather_results.json', 'w') as f:
                f.write(r.text)

            with open('weather_timestamp.pickle', 'wb') as f:
                pickle.dump(now, f)
                last_hit = now

        except Exception as e:
            logger.info(f"Error fetching weather data: {e}")

    if not data and not is_old:
        try:
            with open('weather_results.json') as f:
                data = json.loads(f.read())

                logger.info('hdd hit')
        except FileNotFoundError:
            data = {}

    summaries = data.get('Summaries', [])

    output = []
    for section in summaries:
        output[section['StartMinute']:section['EndMinute']] = [ '|' if section['Type'] else '.' ] * section['CountMinute']

    return ''.join(output)[data_age.seconds//60:]

if __name__ == '__main__':
    logger.info(get_weather())
