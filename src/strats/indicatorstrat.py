import alpaca_trade_api as tradeapi
import threading
import time
import datetime
import multiprocessing as mp
from .basestrat import BaseStrat
import csv
from AlphaVantage import AlphaParser

API_KEY = None
API_SECRET = None
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"
UNDERVALUED_DATA = "data/undervalued.csv"

class IndicatorStrat(BaseStrat):
  def __init__(self, _API_KEY, _API_SECRET, pipe=None, logger=None, alpha_instance=None, stockUniverse = ['DOMO', 'TLRY', 'SQ', 'MRO', 'AAPL', 'GM']):
    API_KEY = _API_KEY
    API_SECRET = _API_SECRET
    #self.alpha_instance = alpha_instance
    self.alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
    #super().__init__(pipe,logger,self.alpaca)
    # Format the allStocks variable for use in the class.
    self.allStocks = stockUniverse.copy()
    self.logger = logger
    self.timeToClose = None

    #self.logger.info("Indicator Strat: Algorithm initiated")

  def get_action(self,ticker):
    '''
    Run calculations
    Return True for buy, False for sell
    '''
    data = self.alpha_instance.getSMA(ticker, "daily", 20, "open")
    short_term = get_most_recent(data,"SMA")

    data = self.alpha_instance.getSMA(ticker, "daily", 100, "open")
    long_term = get_most_recent(data,"SMA")
    
    print("short: {} vs long: {}".format(short_term,long_term))

    data = self.alpha_instance.getRSI(ticker, "daily", 90, "open")
    rsi_short_term = get_most_recent(data,"RSI")
    if short_term > long_term and rsi_short_term < 0.3:
      return False
    else:
      return True


  def run(self):
    # First, cancel any existing orders so they don't impact our buying power.
    orders = self.alpaca.list_orders(status="open")
    for order in orders:
      self.alpaca.cancel_order(order.id)

    # Wait for market to open.
    '''
    uncomment when real testing
    self.m_queue.add_msg("Waiting for market to open...")
    self.checkMarketOpen()

    # the waiting thread may be killed while the market is open, so check flag
    if not self.stop:
      self.m_queue.add_msg("Market opened.")
    '''
    data = parse_csv(UNDERVALUED_DATA)
    print(data)
    #self.get_action("GE")
    
    return
    # max_positions = 5
    # pos_alloc = 1.0 / max_positions

    # while not self.stop:
    #     for stock in self.allStocks:
    #         if get_action(ticker):
    #             #place buy
    #         else:
    #             #sell
            

def get_most_recent(data,indicator):
  '''
  Takes raw AlphaVantage data, with indicator such as "SMA","EMA",etc... and returns most recent value
  '''
  ta_str = "Technical Analysis: {}".format(indicator)
  ta_data = data[ta_str]
  recent = None
  for date in ta_data:
    recent = ta_data[date]
    break
  return recent[indicator]

def parse_csv(fp):
  data = []
  with open(fp) as csvfile:
    read = csv.reader(csvfile)
    for row in read:
      data.append((row[0],row[1]))
  
  return data
