import alpaca_trade_api as tradeapi
import threading
import time
import datetime
import multiprocessing as mp
from .basestrat import BaseStrat
from AlphaVantage import AlphaParser


"""
RSI ( ticker, interval, time_period, close/open/high/low )
what values for interval / time period / series type?

SMA ( ticker, daily, 180, ^^^^^^^^^^^^^^^^^^^^ )

if curr_price > SMA ( ticker, daily, timeperiod? ^^^^^^^^^^^^^^^^^^^^ )
then buy
else sell
"""
API_KEY = None
API_SECRET = None
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

class IndicatorStrat(BaseStrat):
  def __init__(self, alpha_instance,_API_KEY, _API_SECRET, pipe, logger, stockUniverse = ['DOMO', 'TLRY', 'SQ', 'MRO', 'AAPL', 'GM']):
    API_KEY = _API_KEY
    API_SECRET = _API_SECRET
    self.alpha_instance = alpha_instance
    self.alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
    super().__init__(pipe,logger,self.alpaca)
    # Format the allStocks variable for use in the class.
    self.allStocks = stockUniverse.copy()
    self.logger = logger
    self.timeToClose = None

    self.logger.info("Indicator Strat: Algorithm initiated")

  def get_action(self,ticker):
    '''
    Run calculations
    Return True for buy, False for sell
    '''
    a = self.alpha_instance.getSMA(ticker, "daily", 10, "close")
    print(a)
    return "NOT IMPLEMENTED"

  def run(self):
    # First, cancel any existing orders so they don't impact our buying power.
    orders = self.alpaca.list_orders(status="open")
    for order in orders:
      self.alpaca.cancel_order(order.id)

    # Wait for market to open.
    self.m_queue.add_msg("Waiting for market to open...")
    self.checkMarketOpen()

    # the waiting thread may be killed while the market is open, so check flag
    if not self.stop:
      self.m_queue.add_msg("Market opened.")
    self.get_action("MSFT")
    return
    # max_positions = 5
    # pos_alloc = 1.0 / max_positions

    # while not self.stop:
    #     for stock in self.allStocks:
    #         if get_action(ticker):
    #             #place buy
    #         else:
    #             #sell
            
        