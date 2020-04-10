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

    # the most basic one showing a piechart of positions currently held.
    # now it makes a chart, so TODO: make more purchases and diversify 
    # positions so we can see it actually works
    def positions_chart(self):
        self.logger.info('ChartGenerator: Starting to prepare positions chart')
        filename = 'positions.png'
        po = self.alpaca.listPositions()
        labels = []
        sizes = []
        explode = []
        for pos in po:
            labels.append(pos.symbol)
            sizes.append(int(pos.qty))
            explode.append(0.01)
        plt.pie(sizes,explode=explode,labels=labels,shadow=True)
        plt.savefig(img_prefix+filename)
        plt.close()
        self.logger.info('ChartGenerator: Created '+img_prefix+filename+' for output')
        return self.prep(filename)
    
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

    def performaces(self,top=5):
        # this function will return a bar graph of how each stock performs 
        # default of top 5 stock
        return self.prep('madgoose.png')