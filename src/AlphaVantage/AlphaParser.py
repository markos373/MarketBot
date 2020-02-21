import requests
import json

api_url = 'https://www.alphavantage.co/query'

class AlphaParser:

    def __init__(self,key,symbols,interval,time_period,series_type):
        self.key = key
        self.symbols = []
        self.symbols.append(symbols)
        self.interval = interval
        self.time_period = time_period
        self.series_type = series_type    
        
    # Just a sample from the api documentation. 
    # To use other functions, check https://www.alphavantage.co/documentation/
    
    #Parse Data Set
    #returns data under "Technical Analysis: [data_type]"
    def parseData(self, dataSet):
        analysis = list(dataSet.keys())[1]
        myDict = dataSet[analysis]

        return myDict
        # key_list = list(myDict.keys()) 
        # val_list = list(myDict.values())
        # print(key_list[0])
        # print(val_list[0])

    # Returns the simple moving average (SMA) values
    def getSMAvalue(self):
        finalDict = {}
        for s in self.symbols:
            parameters = {
                'function' : 'SMA',
                'symbol' : s,
                'interval' : self.interval,
                'time_period' : self.time_period,
                'series_type' : self.series_type,
                'apikey' : self.key
            }
            r = requests.get(api_url, parameters)
            data = self.parseData(r.json())
            finalDict[s] = data
        return finalDict

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

