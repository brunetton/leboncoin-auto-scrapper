#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Usage:
    {self_filename} [options]

Options:
    -t --test               do not send sms on exception
"""

import json
import time
from pathlib import Path

import yaml
from docopt import docopt
from leboncoin_api_wrapper import Leboncoin
from requests import Session, exceptions, get
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry

SEEN_FILEPATH = Path('already_seen_ads.json')
CONFIG_FILE = Path('config.yml')


# parse args
args = docopt(__doc__.format(self_filename=Path(__file__).name))

# Parse config file
with open(CONFIG_FILE) as f:
    config = yaml.load(f.read(), Loader=yaml.BaseLoader)


def main():
    requests_session = Session()
    # http://www.coglib.com/~icordasc/blog/2014/12/retries-in-requests.html
    # backoff_factor=2 will make sleep for 2 * (2 ^ (retry_number - 1)), ie 0, 2, 4, 8, 16, 32 ... up to 1 hour (for total=12)
    # method_whitelist=False makes retry for GET and POST (https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html)
    requests_retry = Retry(total=4, backoff_factor=3, status_forcelist=[500], method_whitelist=False)  # retry when server return ont of this statuses
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

    # do the request
    lbc = Leboncoin()
    results = search(lbc, config['searches'], config['price']['min'], config['price']['max'])

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
    get(config['sms_url'].format(sms))


def write_json_file(file_path, data):
    with file_path.open('w', encoding='utf-8') as file_:
        json.dump(data, file_, ensure_ascii=False)


def search(lbc, queries, min_price=None, max_price=None):
    results = []
    if max_price:
        lbc.maxPrice(max_price)
    if min_price:
        lbc.minPrice(min_price)
    for i, query in enumerate(ensure_list(queries)):
        lbc.searchFor(query)
        result = lbc.execute()
        if result._:
            results.append(result._)
        if len(queries) > 1 and i < len(queries)-1:
            time.sleep(2)
    return results


def ensure_list(value):
    return value if isinstance(value, (list, tuple)) else [value]


def is_shippable(item):
    shippable_attr = [e for e in item['attributes'] if e['key'] == 'shippable']
    return shippable_attr and shippable_attr[0]['value'] == 'true'


main()
