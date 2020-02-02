import requests
import json

api_url = 'https://www.alphavantage.co/query'

class AlphaParser:

    def __init__(self,key,symbols,interval,time_period,series_type):
        self.key = key
        self.symbols = symbols
        self.interval = interval
        self.time_period = time_period
        self.series_type = series_type    

    # Just a sample from the api documentation. 
    # To use other functions, check https://www.alphavantage.co/documentation/
    def getSMAvalue(self, company, interval, time_period, series_type):
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

    def addSymbol(self, new_symbol):
        if len(self.symbols) < 5 and new_symbol not in self.symbols:
            self.symbols.append(new_symbol)
        else:
            print("Too many symbols")

    def changeInterval(self, new_interval):
        self.interval = new_interval

    def changeTimePeriod(self, new_time_period):
        self.time_period = new_time_period

    def changeSeriesType(self, new_series_type):
        self.series_type = new_series_type

