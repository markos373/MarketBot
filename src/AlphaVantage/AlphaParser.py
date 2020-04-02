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
    
    #Temp Print
    def tprint(self, myDict):
        bigList = "Past 30 SMA values:\n"
        for i in myDict.keys():
            print("-----------------------------------------------------------------------------------")
            print(i)
            count = 0
            for dates, num in myDict[i].items():
                functionType = list(num.keys())
                num2 = list(num.values())
                print(dates + ": " + num2[0] + " | " + functionType[0])
                if count < 30:
                    line = dates + ": " + num2[0] + "\n"
                    bigList += line
                count += 1
        return bigList

    #Parse Data Set
    #returns data under "Technical Analysis: [functionType]"
    def parseData(self, dataSet):
        analysis = list(dataSet.keys())[1]
        myDict = dataSet[analysis]
        return myDict

    ### MAIN TESTING ###
    # alpha = AlphaParser(AlphaAPIKey, "MSFT", "weekly", "10", "open")
    # alpha.addSymbol("TSLA")
    # dataset = alpha.getSMAvalue()

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
        self.tprint(finalDict)
        return finalDict

    # Returns the exponential moving area (EMA) values
    def getEMAvalue(self):
        finalDict = {}
        for s in self.symbols:
            parameters = {
                'function' : 'EMA',
                'symbol' : self.symbols,
                'interval' : self.interval,
                'time_period' : self.time_period,
                'series_type' : self.series_type,
                'apikey' : self.key
            }
            r = requests.get(api_url, parameters)
            data = self.parseData(r.json())
            finalDict[s] = data
        self.tprint(finalDict)
        return finalDict

    # Returns the volume weighted average price (VWAP) for intraday time series
    def getVWAPvalue(self):
        finalDict = {}
        for s in self.symbols:
            parameters = {
                'function' : 'VWAP',
                'symbol' : self.symbols,
                'interval' : self.interval,
                'apikey' : self.key
            }
            r = requests.get(api_url, parameters)
            data = self.parseData(r.json())
            finalDict[s] = data
        self.tprint(finalDict)
        return finalDict

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

