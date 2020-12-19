FROM faucet/python3
WORKDIR /app
RUN apk add git
COPY common.py config_model.py leboncoin_scrapper.py scrapper.py requirements.txt ./
RUN pip install -r requirements.txt
CMD python leboncoin_scrapper.py
