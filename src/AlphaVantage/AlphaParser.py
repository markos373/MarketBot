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

    # Returns the simple moving average (SMA) values
    def getSMAvalue(self):
        parameters = {
            'function' : 'SMA',
            'symbol' : self.symbols,
            'interval' : self.interval,
            'time_period' : self.time_period,
            'series_type' : self.series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the exponential moving area (EMA) values
    def getEMAvalue(self):
        parameters = {
            'function' : 'EMA',
            'symbol' : self.symbols,
            'interval' : self.interval,
            'time_period' : self.time_period,
            'series_type' : self.series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the volume weighted average price (VWAP) for intraday time series
    def getVWAPvalue(self):
        parameters = {
            'function' : 'VWAP',
            'symbol' : self.symbols,
            'interval' : self.interval,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the moving average convergence / divergence (MACD) values
    def getMACDvalue(self):
        parameters = {
            'function' : 'MACD',
            'symbol' : self.symbols,
            'interval' : self.interval,
            'series_type' : self.series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()   

    # Returns the stochastic oscillator (STOCH) values
    def getSTOCHvalue(self):
        parameters = {
            'function' : 'STOCH',
            'symbol' : self.symbols,
            'interval' : self.interval,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the relative strength index (RSI) values
    def getRSIvalue(self):
        parameters = {
            'function' : 'RSI',
            'symbol' : self.symbols,
            'interval' : self.interval,
            'time_period' : self.time_period,
            'series_type' : self.series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Adds new symbol if not added and if len(symbols) < 5
    def addSymbol(self, new_symbol):
        if len(self.symbols) < 5 and new_symbol not in self.symbols:
            self.symbols.append(new_symbol)
        else:
            print("Too many symbols")

    # Change Interval
    def changeInterval(self, new_interval):
        self.interval = new_interval

    # Change Time Period
    def changeTimePeriod(self, new_time_period):
        self.time_period = new_time_period

    # Change Series Type
    def changeSeriesType(self, new_series_type):
        self.series_type = new_series_type

