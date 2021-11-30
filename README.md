## UPDATE november 2021

This script **does not works** anymore, as Leboncoin now use DataDome protection against bots.

## Simple Leboncoin scrapper and SMS alert

Simple use of https://github.com/Shinyhero36/Leboncoin-API-Wrapper to periodically check for Leboncoin ads and alert by sms using a custom sms API when something new is found.

This script is quick'n dirty, probably not really maintainable and not adapted to your needs.

## Install

To make clipboard copy works, install `xclip`

    pip install -r requirements.txt
    cp config.yml.tpl config.yml
    touch already_seen_ads.json

Then edit `config.yml` file.

## Config example

```yaml
searches:
  # First search, multiple terms
  - terms: # Everywhere in France
      - Kindle Paperwhite 3
      - Kindle Paperwhite 2015
      - Kindle Paperwhite 7eme
    price: [0,70]
    shippable: true  # only shippable items
  # Second search, simple one
  - terms: la cité de la peur
  # Third search, one location
  - terms: Clio 5
    price: [0, 2000]
    location:
      gps: 50.6311, 3.0468
      radius: 60
  # Fourth search, multiple terms and locations
  - terms:
      - Piano Yamaha P-35
      - Piano Yamaha P-45
      - Piano Yamaha P-65
    price: [0,350]
    location:
      - gps: 50.644275,3.130413  # Lille
        radius: 20
      - gps: 50.535293,3.182598
        radius: 10
      - gps: 50.442678,3.326794
        radius: 10

# url used to send sms alerts. Must contain "{}" in order to receive message
sms_url: "https://smsapi.free-mobile.fr/sendmsg?user=#######&pass=############&msg={}"
```

## TODO

- regex filter on results titles (to blacklist some type of ads typically)
