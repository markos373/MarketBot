import requests
import json

api_url = 'https://www.alphavantage.co/query'

class AlphaParser:

    def __init__(self,key):
        self.key = key
        
    # Just a sample from the api documentation. 
    # To use other functions, check https://www.alphavantage.co/documentation/

    # Returns the simple moving average (SMA) values
    def getSMA(self, symbol, interval,time_period,series_type):
        parameters = {
            'function' : 'SMA',
            'symbol' : symbol,
            'interval' : interval,
            'time_period' : time_period,
            'series_type' : series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the exponential moving area (EMA) values
    def getEMA(self, symbol, interval, time_period, series_type):
        parameters = {
            'function' : 'EMA',
            'symbol' : symbol,
            'interval' : interval,
            'time_period' : time_period,
            'series_type' : series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the volume weighted average price (VWAP) for intraday time series
    def getVWAP(self, symbol, interval, series_type):
        parameters = {
            'function' : 'VWAP',
            'symbol' : symbol,
            'interval' : interval,
            'series_type' : series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the moving average convergence / divergence (MACD) values
    def getMACD(self, symbol, interval, series_type):
        parameters = {
            'function' : 'MACD',
            'symbol' : symbol,
            'interval' : interval,
            'series_type' : series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the stochastic oscillator (STOCH) values
    def getSTOCH(self, symbol, interval):
        parameters = {
            'function' : 'STOCH',
            'symbol' : symbol,
            'interval' : interval,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the relative strength index (RSI) values
    def getRSI(self, symbol, interval, time_period, series_type):
        parameters = {
            'function' : 'RSI',
            'symbol' : symbol,
            'interval' : interval,
            'time_period' : time_period,
            'series_type' : series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the average directional movement index (ADX) values
    def getADX(self, symbol, interval, time_period, series_type):
        parameters = {
            'function' : 'ADX',
            'symbol' : symbol,
            'interval' : interval,
            'time_period' : time_period,
            'series_type' : series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the commodity channel index (CCI) values
    def getCCI(self, symbol, interval, time_period):
        parameters = {
            'function' : 'CCI',
            'symbol' : symbol,
            'interval' : interval,
            'time_period' : time_period,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the Aroon (AROON) values
    def getAROON(self, symbol, interval, time_period):
        parameters = {
            'function' : 'AROON',
            'symbol' : symbol,
            'interval' : interval,
            'time_period' : time_period,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()      

    # Returns the Bollinger bands (BBANDS) values
    def getBBANDS(self, symbol, interval, time_period, series_type):
        parameters = {
            'function' : 'BBAND',
            'symbol' : symbol,
            'interval' : interval,
            'time_period' : time_period,
            'series_type' : series_type,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json() 

    # Returns the Chaikin A/D line (AD) values
    def getAD(self, symbol, interval):
        parameters = {
            'function' : 'AD',
            'symbol' : symbol,
            'interval' : interval,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Returns the on balance volume (OBV) values
    def getOBV(self, symbol, interval):
        parameters = {
            'function' : 'OBV',
            'symbol' : symbol,
            'interval' : interval,
            'apikey' : self.key
        }
        r = requests.get(api_url, parameters)
        return r.json()

    # Change Interval
    def changeInterval(self, new_interval):
        self.interval = new_interval

    # Change Time Period
    def changeTimePeriod(self, new_time_period):
        self.time_period = new_time_period

    # Change Series Type
    def changeSeriesType(self, new_series_type):
        self.series_type = new_series_type

