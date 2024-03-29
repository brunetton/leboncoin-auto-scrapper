#!python3
# -*- coding: utf-8 -*-

"""
Usage:
    {self_filename} [options] [<config_file>]

Options:
    -t --test               do not catch exception (and do not send sms in case of exceptions)
    --no-sms                do not send any sms
    --clipboard             copy all links to clipboard
    --debug                 show debug messages
"""

import json
import logging
import sys
import traceback
from pathlib import Path

import yaml
from docopt import docopt

sys.path.append(str(Path(__file__).parent.absolute()))
import config_model
import scrapper
from common import ensure_list, write_json_file

SEEN_FILEPATH = Path('already_seen_ads.json')
DEFAULT_CONFIG_FILE = Path(__file__).parent / 'config.yml'


def main():
    # parse args
    args = docopt(__doc__.format(self_filename=Path(__file__).name))

    # Parse config file
    with open(args['<config_file>'] or DEFAULT_CONFIG_FILE) as f:
        config_yaml = yaml.load(f.read(), Loader=yaml.BaseLoader)
        config = config_model.Config(**config_yaml)

    # Init logging
    log = logging.getLogger(__name__)
    logging.basicConfig(format="%(levelname)s: %(message)s", level=(
        logging.DEBUG if args['--debug'] else logging.INFO))

    # Parse already_seen file
    if not SEEN_FILEPATH.exists():
        log.error(f'init "{SEEN_FILEPATH}" file before use. ("echo \'[]\' > {SEEN_FILEPATH})"')
        sys.exit(-1)
    already_seen_set = set()
    if SEEN_FILEPATH.stat().st_size != 0:
        with open(SEEN_FILEPATH) as f:
            already_seen_set = set(ensure_list(json.load(f)))

    new_ids_set = links = None
    try:
        _, new_ids_set, links = scrapper.scrap(config, log, already_seen_set=already_seen_set, send_sms=not args["--no-sms"])
    except:
        if not args["--test"] and not args["--no-sms"]:
            scrapper.send_sms("EXCEPTION", config)
        raise
    finally:
        # Write new found ids to seen file
        if new_ids_set:
            print(f'-> update {SEEN_FILEPATH!r}')
            write_json_file(SEEN_FILEPATH, list(already_seen_set | new_ids_set))
        if args['--clipboard'] and links:
            # Copy urls links to clipboard
            import clipboard
            try:
                clipboard.copy("\n".join(links))
            except Exception as e:
                log.error(f"Error while copying to clipboard:\n{e}")
                traceback.print_tb(e.__traceback__)
            else:
                log.info("URLs copied to clipboard")


if __name__ == '__main__':
    main()
