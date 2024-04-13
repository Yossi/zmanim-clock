import feedparser
import datetime
import bisect
from collections import OrderedDict
from functools import lru_cache
from settings import zipcode
import json

import logging
logging.basicConfig(format='%(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def chabad_org(zipcode, date):
    feed = 'http://www.chabad.org/tools/rss/zmanim.xml?z=%s&tDate=%s' % (zipcode, date)
    info = feedparser.parse(feed)
    return {entry['title'].split('-')[0]:entry['title'].split('-')[1] for entry in info.entries}


def get_events(raw_times):
    times = {}
    for key in raw_times.keys():
        for time in ['Alot Hashachar', 'Misheyakir', 'Hanetz Hachamah', 'Latest Shema', 'Latest Shacharit', 'Chatzot Hayom',
                     'Mincha Gedolah', 'Mincha Ketanah', 'Plag Hamincha', 'Shkiah', 'Chatzot HaLailah', 'Tzeit Hakochavim', 'Ends']:
            if time in key:
                times[time] = raw_times[key]

    time_string = times["Alot Hashachar"]
    alot = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Misheyakir"]
    misheyakir = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Hanetz Hachamah"]
    netz = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Latest Shema"]
    shema = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Latest Shacharit"]
    shacharit = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Chatzot Hayom"]
    midday = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Mincha Gedolah"]
    gedolah = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Mincha Ketanah"]
    ketanah = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Plag Hamincha"]
    plag = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Shkiah"]
    shkiah = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times.get('Tzeit Hakochavim', times.get('Ends'))
    tzeit = datetime.datetime.strptime(time_string, " %I:%M %p ")

    time_string = times["Chatzot HaLailah"]
    midnight = datetime.datetime.strptime(time_string, " %I:%M %p ")


    events = {
        # where the clock should be pointing at each listed zman
        (0,00): midnight,
        (4,00): alot,
        (5,00): misheyakir,
        (6,00): netz,
        (9,00): shema,
        (10,00): shacharit,
        (12,00): midday,
        (12,30): gedolah,
        (15,30): ketanah,
        (16,45): plag,
        (18,00): shkiah,
        (18,30): tzeit,
        (24,00): midnight + datetime.timedelta(days=1),
    }
    return events


@lru_cache(maxsize=1)
def get_times(zipcode, date):
    raw_times = chabad_org(zipcode, date)

    # logger.info(json.dumps(raw_times, indent=2))

    events = get_events(raw_times)

    events_keys = list(events.keys())
    calc_times = {}
    for z_minute_in_day in range(0, int(24 * 60)):
        z_time = datetime.timedelta(minutes=z_minute_in_day)
        z_hour, z_minute = divmod(z_time.seconds, 60 * 60)
        z_minute //= 60

        index = bisect.bisect_right(events_keys, (z_hour, z_minute))
        current_event = events_keys[index-1]
        next_event = events_keys[index]

        current_event_z_minutes = current_event[0] * 60 + current_event[1]
        next_event_z_minutes = next_event[0] * 60 + next_event[1]

        current_event_start = events[current_event]
        next_event_start = events[next_event]

        z_span = next_event_z_minutes - current_event_z_minutes
        span = next_event_start - current_event_start
        tick = span / z_span

        tick_multiplier = z_minute_in_day - current_event_z_minutes

        real_time = current_event_start + tick * tick_multiplier

        calc_times[real_time.strftime('%H:%M:%S')] = {'hour':z_hour, 'minute':z_minute}

    keys = list(calc_times.keys())
    keys.sort()
    output = OrderedDict()
    for key in keys:
        output[key] = calc_times[key]

    return output


if __name__ == '__main__':
    date = datetime.datetime.today().strftime('%m/%d/%Y')
    # calc_times = get_times(zipcode, date)

    # print(calc_times)

    raw_times = chabad_org(zipcode, date)
    events = get_events(raw_times)
    print(events)