import requests
import json

api_url = 'https://www.alphavantage.co/query'

class AlphaParser:
    def __init__(self,key,symbol,interval,time_period,series_type):
        self.key = key
        self.symbol = symbol
        self.interval = interval
        self.time_period = time_period
        self.series_type = series_type    

    # Just a sample from the api documentation. 
    # To use other functions, check https://www.alphavantage.co/documentation/
    def getSMAvalue(self,company, interval, time_period, series_type):
        parameters = {
            'function' : 'SMA',
            'symbol' : company,
            'interval' : interval,
            'time_period' : time_period,
            'series_type' : series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()
        
