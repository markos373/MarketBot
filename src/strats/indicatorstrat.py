import alpaca_trade_api as tradeapi
import threading
import time
import datetime
import multiprocessing as mp
from .basestrat import BaseStrat
import csv
from AlphaVantage import AlphaParser
from polygon.PolyWrapper import PolyWrapper

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
    super().__init__(pipe,logger,self.alpaca)
    self.poly = PolyWrapper(API_KEY)
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

  def submitOrder(self, qty, stock, side, resp):
    if(qty > 0):
      try:
        self.alpaca.submit_order(stock, qty, side, "market", "day")
        self.m_queue.add_msg("Market order of | " + str(qty) + " " + stock + " " + side + " | completed.")
        resp.append(True)
      except:
        self.m_queue.add_msg("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
        resp.append(False)
    else:
      self.m_queue.add_msg("Quantity is 0, order of | " + str(qty) + " " + stock + " " + side + " | not completed.")
      resp.append(True)

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
      self.m_queue.add_msg("Market opened.")  def submitOrder(self, qty, stock, side, resp):
    if(qty > 0):
      try:
        self.alpaca.submit_order(stock, qty, side, "market", "day")
        self.m_queue.add_msg("Market order of | " + str(qty) + " " + stock + " " + side + " | completed.")
        resp.append(True)
      except:
        self.m_queue.add_msg("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
        resp.append(False)
    else:
      self.m_queue.add_msg("Quantity is 0, order of | " + str(qty) + " " + stock + " " + side + " | not completed.")
      resp.append(True)
    '''
    data = parse_csv(UNDERVALUED_DATA)
    top_ten = []
    for i in range(1,11):
      top_ten.append(data[i][0])

    orders = calc_allocations(top_ten)
    buying_power = self.get_buying_power()
    
    resp = self.execute_trades(buying_power,orders)
    #print(self.get_buying_power().buying_power)
    print(resp)
    #get allocations, get buying power, calculate budget per stock, calculate units per stock, execute trade

    #EXIT STRAT: develop get_action to determine if we should sell out
    return

            
  def get_buying_power(self):
    return float(self.alpaca.get_account().buying_power)


  def submitOrder(self, qty, stock, side, resp):
    if(qty > 0):
      try:
        self.alpaca.submit_order(stock, qty, side, "market", "day")
        self.m_queue.add_msg("Market order of | " + str(qty) + " " + stock + " " + side + " | completed.")
        resp.append(True)
      except:
        self.m_queue.add_msg("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
        resp.append(False)
    else:
      self.m_queue.add_msg("Quantity is 0, order of | " + str(qty) + " " + stock + " " + side + " | not completed.")
      resp.append(True)

  def execute_trades(self, buying_power,orders):
    resp = []
    print("Buying Power: : {}".format(buying_power))
    for order in orders:
      
      dollar_alloc = buying_power * order[1] # calc alloc
      quantity = dollar_alloc // self.poly.getLastQuote(order[0])
      self.submitOrder(quantity, order[0], "buy", resp)
    return resp

    


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

def calc_allocations(tickers):
  max_alloc = 1.0 / len(tickers)
  orders = []
  for ticker in tickers:
    orders.append((ticker,max_alloc))
  return orders
  



def parse_csv(fp):
  data = []
  with open(fp) as csvfile:
    read = csv.reader(csvfile)
    for row in read:
      data.append((row[0],row[1]))
  
  return data

