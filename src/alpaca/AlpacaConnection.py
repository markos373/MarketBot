import alpaca_trade_api as tradeapi

import logging
import requests
import json

API_WATCHLIST_URL = "https://paper-api.alpaca.markets/v2/watchlists"
API_ORDERS_URL    = "https://paper-api.alpaca.markets/v2/orders"
API_ACCOUNT_URL   = "https://paper-api.alpaca.markets/v2/account"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets/v2"
class AlpacaConnection:

    def __init__(self, logger, key_id, secret_key):
        self.api = tradeapi.REST(key_id, secret_key,APCA_API_BASE_URL, api_version='v2') 
        self.logger = logger
        self.account_data = ""
        self.header = { "APCA-API-KEY-ID":key_id, "APCA-API-SECRET-KEY":secret_key}
        
        # stored by 'name' : 'id'
        self.watchlists = {}

        # initiating functions to grab values for use
        self.getAccountInformation()
        self.getWatchlists()

    def submitOrder(self, ticker, qty, side,ordertype,tz):
        params = {
            "symbol":ticker,
            "qty":qty,
            "side":side,
            "type":ordertype,
            "time_in_force":tz
        }
        r = self.api.submit_order(ticker,qty,side,ordertype,tz)
        print(r)

    def getAccountInformation(self):
        r = requests.get(url = API_ACCOUNT_URL,headers = self.header)
        self.account_data = r.json()
        return self.account_data

    def getClock(self):
        return self.api.get_clock()

    def listPositions(self):
        return self.api.list_positions()

    def getSpecificPosition(self, ticker):
        return self.api.get_position(ticker)

    def cancelAllOrders(self):
        self.api.cancel_all_orders()

    def addToWatchlist(self, tickers):
        pass

    def createWatchlist(self, wname, tickers):
        params = { "name":wname, "symbols":tickers }
        data = json.dumps(params)
        r = requests.post(url=API_WATCHLIST_URL, data=data, headers=self.header)
        d = r.json()
        id = d['id']
        name = d['name']
        self.watchlists[name] = id
        return d
    
    # this function does not return anything. It should only be used inside the AlpacaConnection class.
    # we do not want to call this everytime to get watchlists because we have limited requests
    def getWatchlists(self):
        r = requests.get(url=API_WATCHLIST_URL, headers=self.header)
        d = r.json()
        for watchlist in d:
            id = watchlist['id']
            name = watchlist['name']
            self.watchlists[name] = id
    
    def getAllWatchlists(self):
        return self.watchlists.keys()

    def viewWatchlist(self,name):
        id = self.watchlists[name]
        endpoint = API_WATCHLIST_URL+'/' + id
        r = requests.get(url=endpoint,headers=self.header)
        return r.json()

    def removeSymbol(self, ticker,name):
        id = self.watchlists[name]        
        endpoint = API_WATCHLIST_URL + "/" + name + "/" + ticker
        response = requests.delete(url=endpoint, headers=self.header)
        print(response.text, response.status_code, sep="\n")
    
    def deleteWatchlist(self,name):
        id = self.watchlists[name]
        endpoint = API_WATCHLIST_URL + '/' + id
        requests.delete(url= endpoint,headers = self.header)
        self.getWatchlists()

    def buildErrorMessage(self, error):
        return str(error) + str(error.status_code)   