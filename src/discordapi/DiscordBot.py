import discord
from strats.longshort import LongShort
from strats.indicatorstrat import IndicatorStrat
from AlphaVantage.AlphaParser import AlphaParser
from prettytable import PrettyTable
import threading
import asyncio
import multiprocessing as mp
from chartgen.imgGenerator import imgGenerator

# piping protocol: calling recv on an empty pipe will cause the program to indefinitely hang
# to get around this, we use two threading.Event() with it as a triple.
# Each process will raise the event flag when sending data, and the receiveing end should reset it

class Pipe:
    def __init__(self,q1,q2):
        self.receiver = q1
        self.sender = q2
    
    # calling this function will not reset the flag. only the actual reading does
    def has_data(self):
        return not self.receiver.empty()
    
    def read(self):
        return self.receiver.get()

    def send(self,data):
        self.sender.put(data)

def create_pipe():
    q1 = mp.Queue()
    q2 = mp.Queue()

    p1 = Pipe(q1,q2)
    p2 = Pipe(q2,q1)

    return p1,p2

class DiscordBot:
    def __init__(self,token,alpha, alpaca, logger, user):
        self.client = discord.Client()
        self.alpha = alpha
        self.alpaca = alpaca
        self.wlist = None
        self.userSettings = {}
        self.token = token
        self.StockUniverse = set()
        self.instance = None
        self.user = None
        self.user_id = user
        self.logger = logger
        # not sure if this is good practice to keep reusing this alpaca object
        # but i will coz why not
        self.img_gen = imgGenerator(self.alpaca,self.logger)

        self.instance_kill = False        
    
    #===================Piping====================

        p1,p2 = create_pipe()

    #=============================================
        self.algo = None
        self.algopipe = p1
        
        self.logger.info('Discord: Bot initiated')

        @self.client.event
        async def on_ready():
            print(f'{self.client.user} is now online!')

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return
            print(message.content)
            msg = ''
            input = message.content.split()
            if not isinstance(message.channel,discord.DMChannel):
            # messages in server
                print("Server message:")
                if '672484881208442894' in message.content:
                    # bot is mentioned
                    print("I have been summoned")
                    msg += self.respondMention()
            else:
                sender = message.author.name+'#'+message.author.discriminator
                if sender != self.user_id:
                    await message.author.send('you are not my boss!')
                    return
                elif not self.user:
                    # we got the right user, so we now store the user object info here
                    self.user = message.author
                self.logger.info("Discord: User input = [{}]".format(message.content))
                # messages in dm
                # this is where we parse user messages
                if 'help' in input:
                    if 'data' in input:
                        msg = self.help('data')
                    elif 'watchlist' in input:                
                        msg = self.help('watchlist')
                    elif 'longshort' in input:
                        msg = self.help('longshort')
                    elif 'show' in input:
                        msg = self.help('show')
                    elif 'positions' in input:
                        msg = self.help('positions')
                    else: 
                        msg = self.help('default')
                elif 'data' in input:
                    # for now we will just return SMA
                    msg = self.getdata()
                elif 'watchlist' in input:
                    if 'create' in input:
                        slist = ' '.join(input[input.index('create')+1:])  #joins string in list
                        print('creating watchlist for ', slist)
                        msg = self.createWatchlist(slist)
                    elif 'view' in input:
                        newname = ' '.join(input[input.index('view')+1:])
                        if newname == 'all':
                            msg = self.viewAllWatchlists()
                        else:
                            msg = self.viewWatchlist(newname)
                        # msg = self.viewWatchlist()    
                    elif 'delete' in input:
                        dname = ' '.join(input[input.index('delete')+1:])
                        msg = self.deleteWatchlist(dname)
                    #add 1 symbol to watchlist
                    elif 'add' in input:
                        watchlistid = input[input.index('add')+1]
                        print("watchlist: " + watchlistid)
                        symbol = ' '.join(input[input.index(watchlistid)+1:])
                        print("symbol: " + symbol)
                        msg = self.addSymbol(watchlistid, symbol)
                    elif 'remove' in input:
                        watchlistid = input[input.index('remove')+1]
                        print("watchlist: " + watchlistid)
                        symbol = ' '.join(input[input.index(watchlistid)+1:])
                        print("symbol: " + symbol)
                        msg = self.removeSymbol(watchlistid, symbol)
                    else:
                        msg = 'requires additonal input!'
                ### I dont think this is needed but I'm leaving it here just in case - Solomon 
                        #i = input.index('add')
                        #if not input[i+1]:
                            #msg = 'please specify an input!'
                elif 'longshort' in input:
                    if 'add' in input:
                        msg = 'adding {}'
                        if ',' in input[input.index('add')+1]:
                            addlist = set(input[input.index('add')+1].split(","))
                            msg = msg.format(list(addlist))
                            self.StockUniverse.update(addlist)
                        else:
                            addlist = str(input[input.index('add')+1])
                            msg = msg.format(addlist)
                            self.StockUniverse.add(addlist)
                        
                    elif 'remove' in input:
                        msg = 'removing {}'
                        if ',' in input[input.index('remove')+1]:
                            rmlist = set(input[input.index('remove')+1].split(","))
                            msg = msg.format(list(rmlist))
                            for thing in rmlist:
                                self.StockUniverse.discard(thing)
                        else:
                            rmlist = str(input[input.index('remove')+1])
                            msg = msg.format(rmlist)
                            self.StockUniverse.remove(rmlist)                      
                    elif 'run' in input:
                        msg = self.start_instance(p2,"longshort")
                    elif 'kill' in input:
                        msg = await self.kill_instance()
                    elif 'view' in input:
                        msg = "Stock Universe: {}".format(list(self.StockUniverse))
                    else:
                        msg = """longshort [add/remove] TICKER,TICKER\n
                               ex: longshort add AAPL,MMM"""
                elif 'show' in input:
                    picture = False
                    if 'goose' in input:
                        goosepicture = 'img/madgoose.png'
                        picture = discord.File(goosepicture)
                    elif 'positions' in input:
                        picture = self.img_gen.positions_chart()
                    elif 'portfolio' in input:
                        timeperiod = 'week'
                        if len(input) > input.index('portfolio')+1:
                            timeperiod = input[input.index('portfolio')+1]
                        picture = self.img_gen.portfolio_graph(timeperiod)
                    
                    if picture: await message.channel.send(file = picture)
                elif 'positions' in input:
                    positions = self.alpaca.listPositions()
                    headers = ["Symbol","Avg Buy Price","Curr Price","Qty","Curr Diff"]
                    table = PrettyTable(headers)
                    for position in positions:
                        table.add_row([position.symbol,position.avg_entry_price,position.current_price,position.qty,position.unrealized_pl])
                    msg = '```'+table.get_string()+'```'
                    print(table)
                elif 'istrat' in input:
                    if 'add' in input:
                        msg = 'adding {}'
                        if ',' in input[input.index('add')+1]:
                            addlist = set(input[input.index('add')+1].split(","))
                            msg = msg.format(list(addlist))
                            self.StockUniverse.update(addlist)
                        else:
                            addlist = str(input[input.index('add')+1])
                            msg = msg.format(addlist)
                            self.StockUniverse.add(addlist)
                        
                    elif 'remove' in input:
                        msg = 'removing {}'
                        if ',' in input[input.index('remove')+1]:
                            rmlist = set(input[input.index('remove')+1].split(","))
                            msg = msg.format(list(rmlist))
                            for thing in rmlist:
                                self.StockUniverse.discard(thing)
                        else:
                            rmlist = str(input[input.index('remove')+1])
                            msg = msg.format(rmlist)
                            self.StockUniverse.remove(rmlist)                      
                    elif 'run' in input:
                        msg = self.start_instance(p2,"indicator")
                    elif 'kill' in input:
                        msg = await self.kill_instance()
                    elif 'view' in input:
                        msg = "Stock Universe: {}".format(list(self.StockUniverse))
                    else:
                        msg = """indicatorstrat [add/remove] TICKER,TICKER\n
                               ex: indicatorstrat add AAPL,MMM"""
                else:
                    msg = 'how can I help? (type \'help\' to see options)'
            if msg:
                await message.channel.send(msg)

    async def kill_instance(self):
        self.logger.info("Discord: Received user input for algo termination")
        if self.instance is not None:
            self.algopipe.send('kill')
            while True:
                if self.instance_kill:
                    self.instance.join()
                    print("REALLY REALLY KILLED IT!!!")
                    self.instance = None
                    self.logger.info('Discord: Algo successfully terminated')
                    return 'Algorithm successfully terminated!'
                else:
                    # this is dirty but this guy has to wait for the listner to 
                    # confirm that the instance thread has wrapped up
                    self.logger.info('Discord: waiting for algo to wrap up...')
                    await asyncio.sleep(3)
        else:
            self.logger.error("Discord: Algo is not running")
            return 'The algorithm is not running!'

    async def listener(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            # make sure a valid user exists!
            if self.user and self.algopipe.has_data():
                algomsg = self.algopipe.read()
                if '#' in algomsg:
                    if algomsg == '#kill-success':
                        print('confirmed kill')
                        self.logger.info('Discord: Received kill success message from algo')
                        self.instance_kill = True
                else:
                    await self.user.send(algomsg)
            await asyncio.sleep(1)
    
    def run(self):
        self.client.loop.create_task(self.listener())
        self.client.run(self.token)        

    def help(self, menu):
        if menu == 'default':
            helpmenu = 'Command options:\n'
            helpmenu += '\t-longshort\n'
            helpmenu += '\t-show\n'
            helpmenu += '\t-positions\n'
            helpmenu += '\t-watchlist\n'
            helpmenu += '\t-data\n'
            helpmenu += 'For more help, enter: help [command]\n'
        elif menu == 'data':
            helpmenu = '**data** command options:\n'
            helpmenu += '\t-**data** | info: shows latest 30 SMA values\n'
            helpmenu += '\t\tenter: data\n' 
        elif menu == 'watchlist':
            helpmenu = '**watchlist** command options:\n'
            helpmenu += '\t-**create** | info: creates watchlist\n'
            helpmenu += '\t\tenter: watchlist create [watchlist]\n\n'
            helpmenu += '\t-**delete** | info: deletes specified watchlist\n'  
            helpmenu += '\t\tenter: watchlist delete [watchlist]\n\n'  
            helpmenu += '\t-**view** | info: returns specified watchlist\n'
            helpmenu += '\t\tenter: watchlist view [watchlist]\n\n'
            helpmenu += '\t-**view all** | info: returns all watchlists\n'  
            helpmenu += '\t\tenter: watchlist view all\n\n'   
            helpmenu += '\t-**add** | info: adds specified symbol to specified watchlist\n'  
            helpmenu += '\t\tenter: watchlist add [watchlist] [symbol]\n\n'  
            helpmenu += '\t-**remove** | info: removes specified symbol from specified watchlist\n'  
            helpmenu += '\t\tenter: watchlist remove [watchlist] [symbol]\n\n'   
        elif menu == 'longshort':
            helpmenu = '**longshort** command options:\n'
            helpmenu += '\t-**add** | info: add symbol to longshort (multiple symbols allowed, separate with \',\')\n'
            helpmenu += '\t\tenter: longshort add [symbol]\n\n'                       
            helpmenu += '\t-**remove** | info: remove symbol from longshort (multiple symbols allowed, separate with \',\')\n'
            helpmenu += '\t\tenter: longshort remove [symbol]\n\n'
            helpmenu += '\t-**run** | info: start longshort\n'
            helpmenu += '\t\tenter: longshort run\n\n'
            helpmenu += '\t-**kill** | info: terminate longshort\n'
            helpmenu += '\t\tenter: longshort kill\n\n'
            helpmenu += '\t-**view** | info: view all symbols in longshort\n'
            helpmenu += '\t\tenter: longshort view\n\n'   
        elif menu == 'show':
            helpmenu = '**show** command options:\n'
            helpmenu += '\t-**positions** | info: displays positions chart\n'
            helpmenu += '\t\tenter: show positions\n\n'
            helpmenu += '\t-**portfolio** | info: displays past week portfolio graph\n'
            helpmenu += '\t\tenter: show portfolio\n\n'
        elif menu == 'positions':
            helpmenu = '**positions** command options:\n'
            helpmenu += '\t-**positions** | info: displays positions table\n'
            helpmenu += '\t\tenter: positions\n\n'
        else:
            print("no menu option stated\n")
        return helpmenu

    # p2 is the pipe for the algo instance to talk through
    def start_instance(self,pipe,algo):
        self.logger.info('Discord: Received user input for algo start')
        msg = ''
        if self.instance is None:
            msg = "Starting {}!".format(algo)
            if algo == "longshort":
                self.algo = LongShort(self.alpaca.key_id, self.alpaca.secret_key,pipe,self.logger,self.StockUniverse)
            if algo == "indicator":
                self.algo = IndicatorStrat(self.alpha,self.alpaca.key_id, self.alpaca.secret_key,pipe,self.logger,self.StockUniverse)
            # self.instance = mp.Process(target=self.algo.run)
            self.instance = threading.Thread(target = self.algo.run)
            self.instance.start()
            self.instance_kill = False
            self.logger.info('Discord: Algorithm initiated')
        else:
            msg = "Longshort is already running!"
            self.logger.error('Discord: Algorithm is already running, skipping execution')
        return msg

    def respondMention(self):
        return 'type --help in my dm for more info!\n'

    def getdata(self):
        d = self.alpha.getSMAvalue()
        l = self.alpha.tprint(d)
        return l

    def createWatchlist(self, watchlist):
        try:
            self.alpaca.createWatchlist(watchlist)
        except:
            print('something messed up')
        return "Watchlist successfully created!"
    
    def deleteWatchlist(self,watchlist):
        self.alpaca.deleteWatchlist(watchlist)
        return "success!"

    def viewAllWatchlists(self):
        nameslist = self.alpaca.getAllWatchlists()
        return ', '.join(nameslist)

    def viewWatchlist(self,name):
        if name not in self.alpaca.watchlists.keys():
            return 'Please provide a valid watchlist name!'
        wlist = self.alpaca.viewWatchlist(name)
        returnstring = ''
        for k,v in wlist.items():
            if k == 'id' or k == 'account_id':
                continue
            if k == 'assets':
                returnstring += k + ':\n'
                for item in v:
                    for k,v in item.items():
                        if k == 'id':
                            continue
                        returnstring += '\t' + k + ': ' + str(v) + '\n'
                    returnstring += '\t----------------------\n'
            returnstring += k + ': ' + str(v) + '\n'

        return returnstring

    def addSymbol(self,name,ticker):
        try: 
            return self.alpaca.addSymbol(name, ticker)
        except:
            return "addSymbol failed (D)"

    def removeSymbol(self,name,ticker):
        try: 
            return self.alpaca.removeSymbol(name, ticker)
        except:
            return "removeSymbol failed (D)"