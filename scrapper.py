import itertools
import time

# import yaml
from leboncoin_api_wrapper import Leboncoin
from requests import Session, exceptions, get
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry


requests_session = Session()
# http://www.coglib.com/~icordasc/blog/2014/12/retries-in-requests.html
# backoff_factor=2 will make sleep for 2 * (2 ^ (retry_number - 1)), ie 0, 2, 4, 8, 16, 32 ... up to 1 hour (for total=12)
# method_whitelist=False makes retry for GET and POST (https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html)
requests_retry = Retry(total=4, backoff_factor=3, status_forcelist=[
    500], method_whitelist=False)  # retry when server return ont of this statuses
requests_session.mount('http://', HTTPAdapter(max_retries=requests_retry))
requests_session.mount('https://', HTTPAdapter(max_retries=requests_retry))


def scrap(config, log, already_seen_set=set()):
    """Return:
        - results list
        - newly seen IDs
    """

    # do the requests
    lbc = Leboncoin()
    results = search(lbc, config.searches, log=log)

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
        send_sms(sms, config)

    # Write ids to file
    return results, ids - already_seen_set


def search(lbc, queries, log):
    results = []
    for query in queries:
        log.debug(f"query: {query.dict()!r}")
        if query.price:
            if query.price['min']:
                lbc.minPrice(query.price['min'])
            if query.price['max']:
                lbc.maxPrice(query.price['max'])
        # for each term of the current query
        for term, location in iter_terms_and_locations(query):
            if location:
                log.info(f" - location: {location!r}")
                lbc.setLocation(
                    lat=location.gps['lat'], lng=location.gps['long'], radius=location.radius)
            log.info(f" - term: {term!r}")
            lbc.searchFor(term, autoCatgory=False)
            result = lbc.execute()
            if result:
                results.append(result)
            time.sleep(2)
    return results


def iter_terms_and_locations(query):
    if query.location:
        # If location given, do the cartesian product of terms and locations
        yield from itertools.product(query.terms, query.location)
    else:
        yield from ((term, None) for term in query.terms)


def is_last_one(i, _list):
    """Return True if the total len of the list > 1 and given index is not the last one
    """
    return len(_list) > 1 and i < len(_list)-1


def is_shippable(item):
    shippable_attr = [e for e in item['attributes'] if e['key'] == 'shippable']
    return shippable_attr and shippable_attr[0]['value'] == 'true'


def send_sms(sms, config):
    if config.sms_url:
        get(config.sms_url.format(sms)).raise_for_status()
