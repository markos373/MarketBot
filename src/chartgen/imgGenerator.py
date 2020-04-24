import alpaca_trade_api as tradeapi
from alpaca.AlpacaConnection import AlpacaConnection
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import discord
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta as rd
import os
import numpy as np

img_prefix = 'img/'

class imgGenerator:
    def __init__(self,alpaca,logger):
        self.alpaca = alpaca
        self.logger = logger
    
    def prep(self,filepath):
        # converts the generated image file to discord file
        self.logger.info('ChartGenerator: Preparing image file '+img_prefix+filepath+' to send through discord')
        return discord.File(img_prefix+filepath)

    def positions_chart(self):
        self.logger.info('ChartGenerator: Starting to prepare positions chart')
        lfilename = 'long_positions.png'
        sfilename = 'short_positions.png'
        po = self.alpaca.listPositions()
        longs = {'labels':[],'sizes':[],'exp':[]}
        shorts = {'labels':[],'sizes':[],'exp':[]}
        explode = []
        for pos in po:
            if float(pos.market_value) > 0:
                longs['sizes'].append(float(pos.market_value))
                longs['labels'].append(pos.symbol+' '+str(pos.market_value))
                longs['exp'].append(0.01)
            else:
                shorts['sizes'].append(float(pos.market_value)*-1)
                shorts['labels'].append(pos.symbol+' '+str(pos.market_value))
                shorts['exp'].append(0.01)
            
        if po:
            ll = None
            ss = None
            if longs:
                plt.pie(longs['sizes'],explode=longs['exp'],labels=longs['labels'],autopct='%0.2f%%',pctdistance=0.7, labeldistance=1.2)
                plt.title('Long stocks')
                plt.savefig(img_prefix+lfilename)
                plt.close()
                self.logger.info('ChartGenerator: Created '+img_prefix+lfilename+' for output')
                ll = self.prep(lfilename)
            if shorts:
                plt.pie(shorts['sizes'],explode=shorts['exp'],labels=shorts['labels'],autopct='%0.2f%%', pctdistance=0.7, labeldistance=1.2)
                plt.title('Short stocks')
                plt.savefig(img_prefix+sfilename)
                plt.close()
                self.logger.info('ChartGenerator: Created '+img_prefix+sfilename+' for output')
                ss = self.prep(sfilename)
            if ll and ss: return ll,ss
            elif ll: return ll
            elif ss: return ss
        else: return 'invalid'
    
    # base method for generating portfolio graphs. 
    # time can be day, week, month and year
    def portfolio_graph(self,time='week'):
        self.logger.info('ChartGenerator: Starting to prepare portfolio graph')
        filename = 'portfolio_'+time+'.png'
        period_switcher = {
            'day'  : '1D', 
            'week' : '1W',
            'month': '1M',
            'year' : '1A'
        }
        tf_switcher = {
            '1D':'1Min',
            '1W':'1H',
            '1M':'1D',
            '1A':'1D'
        }
        period = period_switcher[time]
        date_end = str(datetime.now().date())
        timeframe = tf_switcher[period]
        # not sure what this is good for, so just gonna leave it out for now
        extended_hours = False
        
        portfolio = self.alpaca.porfolio_history(period,timeframe,date_end,extended_hours)
        
        ts = portfolio['timestamp']
        eq = portfolio['equity']
        
        # here we do some funky stuff, since alpaca only allows for 1Min,15Min,1H,1D as timeframes
        # and it doesn't work very nicely on periods such as day or week.

        # not the best way to make the tick marks, but this is pretty simple so just gonna use this for now
        xlabel_swticher = {
            '1D':['12 AM', '4 AM','8 AM','12 PM','4 PM', '8 PM', '12 AM'],
            '1W':[str((datetime.now()-timedelta(days=1*(i))).date())
                for i in reversed(range(7))],
            '1M':[str((datetime.now()-timedelta(days=7*(i))).date())
                for i in reversed(range(4))],
            '1A':[(datetime.now()-rd(months=+i)).strftime('%b')
                for i in reversed(range(12))],
        }

        # these two are the same thing
        profit_loss = portfolio['profit_loss']               # this one is in dollars
        profit_loss_percent = portfolio['profit_loss_pct']   # this one is in percentages
        # not gonna use it for now anyway
        bval = portfolio['base_value']

        offset_switcher = {
            '1D':int(len(eq)/6),
            '1W':int(len(eq)/7),
            '1M':int(len(eq)/4),
            '1A':int(len(eq)/12)
        }
        
        labels = xlabel_swticher[period]
        offset = offset_switcher[period]

        fig = plt.figure(figsize=(10,4))
        
        print(len(eq))
        indexes = np.linspace(0,len(eq),len(labels))
        print(labels)
        print(indexes)

        axes = fig.add_subplot(111)
        axes.set_xticks([int(n) for n in np.linspace(0,len(eq),len(labels))])
        axes.set_xticklabels(labels)
        axes.plot(eq)
        axes.set_title('Portfolio over the last '+time )
        plt.tight_layout()
        if os.path.exists(img_prefix + filename):
            os.remove(img_prefix + filename)

        plt.savefig(img_prefix + filename)
        plt.close()
        self.logger.info("ChartGenerator: Created "+img_prefix+filename+" for output")
        return self.prep(filename)

    def best_performers(self,top=5,timeframe='all_time'):
        # this function will return a bar graph of how each stock performs 
        activities = self.alpaca.account_activities()
        parsed = self.parse_activities(activities)
        return parsed['GS']
        # return self.prep('madgoose.png')

    # helper function for best_performers
    # should not be called anywhere else
    def parse_activities(self,activities):
        by_symbols = {}
        for a in activities:
            sym = a['symbol']
            if sym not in by_symbols: by_symbols[sym] = [a]
            else: by_symbols[sym].append(a)
        return by_symbols