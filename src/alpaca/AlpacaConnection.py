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
        self.key_id = key_id
        self.secret_key = secret_key
        # stored by 'name' : 'id'
        self.watchlists = {}

        # initiating functions to grab values for use
        print(self.getAccountInformation())
        self.getWatchlists()

    #Takes type, url, params
    def requestsFunc(self, type, endpoint, params):
        if type == 'get':
            print("get")
            try: 
                func = requests.get(url = endpoint, headers = self.header) 
            except Exception as e:
                logging.error("ERROR: REQUEST.GET FAILED")
                print(e.args)
            return func

        elif type == 'post':
            print("post")
            data = json.dumps(params)
            try:
                func = requests.post(url = endpoint, data = data, headers = self.header)
            except Exception as e:
                logging.error("ERROR: REQUEST.POST FAILED")
                print(e.args)
            return func

        elif type == 'delete':
            print("delete")
            try:
                func = requests.delete(url = endpoint, headers = self.header)
            except Exception as e:
                logging.error("ERROR: REQUEST.DELETE FAILED")
                print(e.args)
            return func        
        else:
            logging.fatal("ERROR: BAD ARGUMENTS")
            print("requestFunc failed")
        
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
        r = self.requestsFunc('get', API_ACCOUNT_URL, {})
        self.account_data = r.json()
        ###should not need
        #try:
        #    r = requests.get(url = API_ACCOUNT_URL,headers = self.header)
        #    self.account_data = r.json()
        #except Exception as e:
        #    return "Failed to establish connection. Error: {}".format(e)

        return self.account_data

    def getClock(self):
        return self.api.get_clock()

    def listPositions(self):
        return self.api.list_positions()

    def getSpecificPosition(self, ticker):
        return self.api.get_position(ticker)

    def cancelAllOrders(self):
        self.api.cancel_all_orders()

    def createWatchlist(self, wname):
        params = { "name":wname, "symbols":[]}
        r = self.requestsFunc('post', API_WATCHLIST_URL, params)
        d = r.json()
        id = d['id']
        name = d['name']
        self.watchlists[name] = id
        return d
    
    # this function does not return anything. It should only be used inside the AlpacaConnection class.
    # we do not want to call this everytime to get watchlists because we have limited requests
    def getWatchlists(self):
        r = self.requestsFunc('get', API_WATCHLIST_URL, {})
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
        r = self.requestsFunc('get', endpoint, {})
        return r.json()

    def addSymbol(self, name, ticker):
        id = self.watchlists[name]
        endpoint = API_WATCHLIST_URL + '/' + id
        params = {"symbol": ticker}
        response = self.requestsFunc('post', endpoint, params)
        print(response.text, response.status_code, sep="\n")

    def removeSymbol(self, name, ticker):
        id = self.watchlists[name]        
        endpoint = API_WATCHLIST_URL + "/" + id + "/" + ticker
        response = self.requestsFunc('delete', endpoint, {})
        print(response.text, response.status_code, sep="\n")
    
    def deleteWatchlist(self,name):
        id = self.watchlists[name]
        endpoint = API_WATCHLIST_URL + '/' + id
        self.requestsFunc('delete', endpoint, {})
        if name in self.watchlists.keys():
            del self.watchlists[name]

    def buildErrorMessage(self, error):
        return str(error) + str(error.status_code)   
