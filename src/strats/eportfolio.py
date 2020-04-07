import numpy as np
import pandas as pd
import pandas_datareader as web
import matplotlib.pyplot as plt
from matplotlib import style
import datetime as dt

style.use = ('ggplot')

start = dt.datetime(2010,1,1)
end = dt.datetime(2020,3,1)

ticker = ['XLF', 'XLI', 'XLY', 'SPY', 'XLK', 'XLU', 'VHT', 'IVW']
def get_eport():
    dictionary = {}
    for tempticker in ticker:
        getData = web.DataReader(tempticker,'yahoo',start,end)
        dictionary[tempticker] = getData

    df = pd.DataFrame()

    #Dataframe done
    for x in ticker:
    df[x] = dictionary[x]['Adj Close']
    returns_daily = df.pct_change()
    returns_annual = returns_daily.mean() * 250
    cov_daily = returns_daily.cov()
    cov_annual = cov_daily * 250

    Expectedreturns = []
    Expectedvolatility = []
    stock_weights = []

    num_assets = len(ticker)
    num_portfolios = 25000

    for trialportfolio in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        returns = np.dot(weights, returns_annual)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
        Expectedreturns.append(returns)
        Expectedvolatility.append(volatility)
        stock_weights.append(weights)
    
    portfolio = {'Returns': Expectedreturns,
                'Volatility': Expectedvolatility}

    for counter,symbol in enumerate(ticker):
        portfolio[symbol+ 'weight'] = [weight[counter] for weight in stock_weights]

    desiredvol = .15
    maxval = -100
    desiredvollist = []

if __name__ == '__main__':
    get_eport()
