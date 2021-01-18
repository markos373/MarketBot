import alpaca_trade_api as tradeapi
import threading
import time
import datetime
import multiprocessing as mp
from .basestrat import BaseStrat
from data import scraper
import csv
from AlphaVantage import AlphaParser
from alpaca.AlpacaConnection import AlpacaConnection
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
    #TODO: Replace alpaca with alpaca_wrapper
    self.alpaca_wrapper = AlpacaConnection(logger, API_KEY, API_SECRET)
    self.alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
    super().__init__(pipe,logger,self.alpaca)
    self.poly = PolyWrapper(API_KEY)
    self.allStocks = stockUniverse.copy()
    self.logger = logger
    self.timeToClose = None

    #self.logger.info("Indicator Strat: Algorithm initiated")

  def submitOrder(self, qty, stock, side, resp):
    '''
    Wrapper for Alpaca API submit_order.  Returns response in resp as list.
    '''
    if(qty > 0):
      try:
        self.alpaca_wrapper.submitOrder(stock, qty, side, "market", "day")
        self.m_queue.add_msg("Market order of | " + str(qty) + " " + stock + " " + side + " | completed.")
        resp.append(True)
      except Exception as e:
        self.m_queue.add_msg("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
        resp.append((False, e))
    else:
      self.m_queue.add_msg("Quantity is 0, order of | " + str(qty) + " " + stock + " " + side + " | not completed.")
      resp.append(True)

  def run(self):
    '''
    Core of bot.  Will repeat on startup
    '''
    # First, cancel any existing orders so they don't impact our buying power.
    orders = self.alpaca.list_orders(status="open")
    for order in orders:
      self.alpaca.cancel_order(order.id)
    
    #Reset orders
    self.alpaca_wrapper.closePositions()
        
      
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
    

    #for position in positions:
    #  if position["unrealized_plpc"] > 0.1: #10% GAIN or more, sell a quarter!
    #    self.submitOrder(position["quantity"]//4, position["ticker"], "sell", resp) 
    #data = parse_csv(UNDERVALUED_DATA)
    
    tickers = scraper.QQ_main()
    top_ten = []
    curr_index = 0
    while(len(top_ten) < 10):
      try:
        asset = self.alpaca.get_asset(tickers[curr_index][0])
        if asset.tradable:
          top_ten.append(tickers[curr_index][0])
        else:
          curr_index += 1
      except:
          curr_index += 1
      curr_index += 1

      
    print(top_ten)
    orders = calc_allocations(top_ten)

    time.sleep(2)
    buying_power = self.get_buying_power()
    
    resp = self.execute_trades(buying_power,orders, 0)

    print(resp)

    return

            
  def get_buying_power(self):
    '''
    Get current buying power of account as a float
    '''
    return float(self.alpaca.get_account().buying_power)


  def execute_trades(self, buying_power,orders, dbg=0):
    '''
    Execute a list of trades in the format [(ticker, pct_allocation),...]
    Calculates appropriate shares based on buying power and percent allocation.
    '''
    resp = []
    
    if dbg:
      print("Buying Power: : {}".format(buying_power))
    for order in orders:
      
      dollar_alloc = buying_power * order[1] # calc alloc
      quantity = dollar_alloc // self.poly.getLastQuote(order[0])
      if dbg:
        print("Order: {}, {}, {} | ALLOCATION : {}".format(quantity,order[0],"buy",dollar_alloc))
      else:  
        self.submitOrder(quantity, order[0], "buy", resp)
      
      

    return resp

  

def calc_allocations(tickers):
  '''
  Evenly distribute portfolio allocation across N tickers
  '''
  max_alloc = 1.0 / len(tickers)
  orders = []
  for ticker in tickers:
    orders.append((ticker,max_alloc))
  return orders
  



def parse_csv(fp):
  '''
  Read file fp and return data as list in format [(ticker, rating)] (using undervalued.csv)
  '''
  data = []
  with open(fp) as csvfile:
    read = csv.reader(csvfile)
    for row in read:
      data.append((row[0],row[1]))
  
  return data

