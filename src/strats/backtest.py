import alpaca_backtrader_api
import backtrader as bt
from datetime import datetime


class SmaCross1(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30,   # period for the slow moving average
        rsi_per=14,
        rsi_upper=65.0,
        rsi_lower=35.0,
        rsi_out=50.0,
        warmup=35
    )

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime[0]
        dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_trade(self, trade):
        self.log("placing trade for {}. target size: {}".format(
            trade.getdataname(),
            trade.size))

    def notify_order(self, order):
        pass

    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('==================================================')

    def __init__(self):
        # this checks how many datas is being put in
        for i in range(1000):
            dname = 'data' + str(i)
            if not hasattr(self,dname):
                self.num_data = i
                break

        sma1 = bt.ind.SMA(self.data0, period=self.p.pfast)
        sma2 = bt.ind.SMA(self.data0, period=self.p.pslow)
        self.crossover0 = bt.ind.CrossOver(sma1, sma2)

        rsi = bt.indicators.RSI(period=self.p.rsi_per,
                                upperband=self.p.rsi_upper,
                                lowerband=self.p.rsi_lower)

        self.crossdown0 = bt.ind.CrossDown(rsi, self.p.rsi_upper)
        self.crossup0 = bt.ind.CrossUp(rsi, self.p.rsi_lower)

        sma1 = bt.ind.SMA(self.data1, period=self.p.pfast)
        sma2 = bt.ind.SMA(self.data1, period=self.p.pslow)
        self.crossover1 = bt.ind.CrossOver(sma1, sma2)

        rsi = bt.indicators.RSI(period=self.p.rsi_per,
                                upperband=self.p.rsi_upper,
                                lowerband=self.p.rsi_lower)

        self.crossdown1 = bt.ind.CrossDown(rsi, self.p.rsi_upper)
        self.crossup1 = bt.ind.CrossUp(rsi, self.p.rsi_lower)

    def next(self):
        for i in range(self.num_data):
            data = eval('self.data' + str(i))
            # if fast crosses slow to the upside
            if not self.positionsbyname[data.p.dataname].size:
                if self.crossover0 > 0 or self.crossup0 > 0:
                    self.buy(data=data, size=5)  # enter long

            # in the market & cross to the downside
            if self.positionsbyname[data.p.dataname].size:
                if self.crossover0 <= 0 or self.crossdown0 < 0:
                    self.close(data=data)  # close long position

def run(ALPACA_API_KEY,ALPACA_SECRET_KEY,ALPACA_PAPER,symbols):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross1)

    store = alpaca_backtrader_api.AlpacaStore(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=ALPACA_PAPER
    )

    DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
    
    for s in symbols:
        data = DataFactory(dataname=s, historical=True, fromdate=datetime(
                            2015, 1, 1), timeframe=bt.TimeFrame.Days)
        cerebro.adddata(data)

    if not ALPACA_PAPER:
        # backtrader broker set initial simulated cash
        cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    cerebro.run()
    print('Final Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    cerebro.plot()
    