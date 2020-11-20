import requests

ENDPOINT = "https://api.polygon.io/v1/last_quote/stocks/{}?apiKey={}"

class PolyWrapper:
    def __init__(self,alpaca_api_key):
        self.api_key = alpaca_api_key

    def getLastQuote(self,ticker):
        url = ENDPOINT.format(ticker,self.api_key)
        data = requests.get(url).json()
        return data["last"]["askprice"]