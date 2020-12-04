## Simple Leboncoin scrapper and SMS alert

Simple use of https://github.com/Shinyhero36/Leboncoin-API-Wrapper to periodically check for Leboncoin ads and alert by sms using a custom sms API when something new is found.

This script is quick'n dirty, probably not really maintainable and not adapted to your needs.

## Install

    pip install -r requirements.txt
    cp config.yml.tpl config.yml
    touch already_seen_ads.json

Then edit `config.yml` file.

## Config example

```yaml
searches:
  - terms: # Everywhere in France
      - Kindle Paperwhite 3
      - Kindle Paperwhite 2015
      - Kindle Paperwhite 7eme
    price: [0,70]
    shippable: true  # only shippable items
  - terms: la cité de la peur
  - terms: Clio 5
    price: [0, 2000]
    location:
      gps: 50.6311, 3.0468
      radius: 60

# url used to send sms alerts. Must contain "{}" in order to receive message
sms_url: "https://smsapi.free-mobile.fr/sendmsg?user=#######&pass=############&msg={}"
```

## TODO

- regex filter on results titles (to blacklist some type of ads typically)
