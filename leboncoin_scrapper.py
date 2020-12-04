#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Usage:
    {self_filename} [options]

Options:
    -t --test               do not catch exception (and do not send sms in case of exceptions)
    --debug                 show debug messages
"""

import json
import logging
import time
from pathlib import Path

import yaml
from docopt import docopt
from leboncoin_api_wrapper import Leboncoin
from requests import Session, exceptions, get
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry

from config_model import config_model


SEEN_FILEPATH = Path('already_seen_ads.json')
CONFIG_FILE = Path('config.yml')


# parse args
args = docopt(__doc__.format(self_filename=Path(__file__).name))

# Parse config file
with open(CONFIG_FILE) as f:
    config_yaml = yaml.load(f.read(), Loader=yaml.BaseLoader)
    config = config_model.Config(**config_yaml)

# Init logging
import logging
log = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s: %(message)s", level=(logging.DEBUG if args['--debug'] else logging.INFO))
logging.basicConfig(
    level=logging.DEBUG,
    format = "%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s:%(funcName)s line %(lineno)d] %(message)s"
)


def main():
    requests_session = Session()
    # http://www.coglib.com/~icordasc/blog/2014/12/retries-in-requests.html
    # backoff_factor=2 will make sleep for 2 * (2 ^ (retry_number - 1)), ie 0, 2, 4, 8, 16, 32 ... up to 1 hour (for total=12)
    # method_whitelist=False makes retry for GET and POST (https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html)
    requests_retry = Retry(total=4, backoff_factor=3, status_forcelist=[
                           500], method_whitelist=False)  # retry when server return ont of this statuses
    requests_session.mount('http://', HTTPAdapter(max_retries=requests_retry))
    requests_session.mount('https://', HTTPAdapter(max_retries=requests_retry))

    try:
        scrap()
    except:
        if not args["--test"]:
            send_sms("EXCEPTION")
        raise


def scrap():
    if not SEEN_FILEPATH.exists():
        raise Exception(f'init "{SEEN_FILEPATH}" file before use.')

    already_seen_set = set()
    if SEEN_FILEPATH.stat().st_size != 0:
        with open(SEEN_FILEPATH) as f:
            already_seen_set = set(ensure_list(json.load(f)))

    # do the requests
    lbc = Leboncoin()
    results = search(lbc, config.searches)

    # iterate results, filter and print in console
    ids = set()
    sms = []
    for result in results:
        if result['total'] > 0:
            for res in result['ads']:
                _id = res['list_id']
                if not _id in ids:
                    already_seen = _id in already_seen_set
                    price = res['price'][0]
                    shippable = is_shippable(res)
                    shipp_str = "" if shippable else " --PAS D'ENVOI -- "
                    seen_str = "👀" if already_seen else "🌟"
                    msg = f"{price}€ - {res['url']} - {res['subject']}{shipp_str}"
                    print(f"{seen_str} {res['first_publication_date']} {msg}")
                    if not already_seen:
                        print("=> SMS")
                        sms.append(f"- {msg}")
                    ids.add(_id)
    # SMS
    if sms:
        sms = "\n".join(sms).replace(' ', '%20')
        send_sms(sms)

    # Write ids to file
    if ids - already_seen_set:
        print('-> update json')
        write_json_file(SEEN_FILEPATH, list(ids))


def send_sms(sms):
    if config.sms_url:
        get(config.config.sms_url.format(sms))


def ensure_list(value):
    return value if isinstance(value, (list, tuple)) else [value]


def write_json_file(file_path, data):
    with file_path.open('w', encoding='utf-8') as file_:
        json.dump(data, file_, ensure_ascii=False)


def search(lbc, queries):
    results = []
    for i, query in enumerate(queries):
        if query.price:
            if query.price['min']:
                lbc.minPrice(query.price['min'])
            if query.price['max']:
                lbc.maxPrice(query.price['max'])
        if query.location:
            lbc.setLocation(
                lat=query.location.gps['lat'], lng=query.location.gps['long'], radius=query.location.radius)
        # for each term of the current query
        for j, term in enumerate(query.terms):
            lbc.searchFor(term, autoCatgory=False)
            result = lbc.execute()
            log.debug(f'-> search {term!r}')
            if result._:
                results.append(result._)
            # Do we need to sleep ? (we do if we are not at the last term of the last search)
            if is_last_one(i, queries) or is_last_one(j, query.terms):
                log.debug("sleep")
                time.sleep(2)
    return results


def is_last_one(i, _list):
    """Return True if the total len of the list > 1 and given index is not the last one
    """
    return len(_list) > 1 and i < len(_list)-1


def is_shippable(item):
    shippable_attr = [e for e in item['attributes'] if e['key'] == 'shippable']
    return shippable_attr and shippable_attr[0]['value'] == 'true'


main()
