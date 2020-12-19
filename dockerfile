FROM faucet/python3
WORKDIR /app
COPY common.py config_model.py leboncoin_scrapper.py scrapper.py requirements.txt ./
RUN apk add git
RUN pip install -r requirements.txt
CMD python leboncoin_scrapper.py
