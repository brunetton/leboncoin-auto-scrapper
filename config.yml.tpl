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
