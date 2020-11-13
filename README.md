## Simple Leboncoin scrapper and SMS alert

Simple use of https://github.com/Shinyhero36/Leboncoin-API-Wrapper to periodically check for Leboncoin ads and alert by sms using a custom sms API when something new is found.

This script is quick'n dirty, probably not really maintainable and not adapted to your needs.

## Install

    pip install -r requirements.txt
    cp config.yml.tpl config.yml
    touch already_seen_ads.json

Then edit `config.yml` file

## TODO

- per-search price range, or something like searches groups with prices ranges
- regex filter on results titles (to blacklist some type of ads typically)
