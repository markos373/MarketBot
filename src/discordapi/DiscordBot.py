import discord
from strats.longshort import LongShort
from AlphaVantage.AlphaParser import AlphaParser
from prettytable import PrettyTable
import threading
import asyncio
import multiprocessing as mp

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
    def __init__(self,token,alpha, alpaca, logger):
        self.client = discord.Client()
        self.alpha = alpha
        self.alpaca = alpaca
        self.wlist = None
        self.userSettings = {}
        self.token = token
        self.LSUniverse = set()
        self.instance = None
        self.user = None
        self.logger = logger

        self.instance_kill = False        
    
    #===================Piping====================

        p1,p2 = create_pipe()

    #=============================================
        self.algo = None
        self.algopipe = p1
        
        self.logger.info('Discord: Bot initiated')

        @self.client.event
        async def on_ready():
            print(f'{self.client.user} is a very bad bot')

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return
            print(message.content)
            msg = ''
            input = message.content.split()
            if not isinstance(message.channel,discord.DMChannel):
            # messages in server
                print("message in guild!")
                if '672484881208442894' in message.content:
                    # bot is mentioned
                    print("I have been summoned")
                    msg += self.respondMention()
            else:
                if not self.user:
                    self.user = message.author
                if message.author != self.user:
                    await message.author.send('you are not my boss!')
                    return
                self.logger.info("Discord: User input = [{}]".format(message.content))
                # messages in dm
                # this is where we parse user messages
                if 'help' in input:
                    msg = self.help()
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
                elif 'add' in input:
                    i = input.index('add')
                    if not input[i+1]:
                        msg = 'please specify an input!'
                elif 'longshort' in input:
                    if 'add' in input:
                        msg = 'adding {}'
                        if ',' in input[input.index('add')+1]:
                            addlist = set(input[input.index('add')+1].split(","))
                            msg = msg.format(list(addlist))
                            self.LSUniverse.update(addlist)
                        else:
                            addlist = str(input[input.index('add')+1])
                            msg = msg.format(addlist)
                            self.LSUniverse.add(addlist)
                        
                    elif 'remove' in input:
                        msg = 'removing {}'
                        if ',' in input[input.index('remove')+1]:
                            rmlist = set(input[input.index('remove')+1].split(","))
                            msg = msg.format(list(rmlist))
                            for thing in rmlist:
                                self.LSUniverse.discard(thing)
                        else:
                            rmlist = str(input[input.index('remove')+1])
                            msg = msg.format(rmlist)
                            self.LSUniverse.remove(rmlist)
                        
                    elif 'run' in input:
                        msg = self.start_instance(p2)
                    elif 'kill' in input:
                        msg = await self.kill_instance()
                    elif 'view' in input:
                        msg = "Stock Universe: {}".format(list(self.LSUniverse))
                    else:
                        msg = """longshort [add/remove] TICKER,TICKER\n
                               ex: longshort add AAPL,MMM"""
                elif 'algo' in input:
                    print("user said algo!")
                    self.algopipe.send("hey there algo")
                elif 'positions' in input:
                    positions = self.alpaca.listPositions()
                    headers = ["Symbol","Avg Buy Price","Curr Price","Qty","Curr Diff"]
                    table = PrettyTable(headers)
                    for position in positions:
                        table.add_row([position.symbol,position.avg_entry_price,position.current_price,position.qty,position.unrealized_pl])
                    msg = table
                    print(table)
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

    def help(self):
        helpmenu = 'options:\n'
        helpmenu += '\t-watchlist:\n'
        helpmenu += '\t\t-create [inputs: \'symbol_0\',\'symbol_1\', ..]\n'
        helpmenu += '\t\t example: watchlist create MSFT TSLA\n'
        helpmenu += '\t\t-view\n'
        helpmenu += '\t\t\t view all\n'
        helpmenu += '\t\t\t returns the name of all watchlists\n'
        helpmenu += '\t\t\t [watchlist name]\n'
        helpmenu += '\t\t\t returns specified watchlist\n'
        helpmenu += '\t\t-delete\n'
        helpmenu += '\t\t example: watchlist delete [watchlistname]'
        return helpmenu

    # p2 is the pipe for the algo instance to talk through
    def start_instance(self,pipe):
        self.logger.info('Discord: Received user input for algo start')
        msg = ''
        if self.instance is None:
            msg = "Starting longshort!"
            self.algo = LongShort(self.alpaca.key_id, self.alpaca.secret_key,pipe,self.logger,self.LSUniverse)
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
        d = d[list(d.keys())[1]]
        d = d[list(d.keys())[0]]
        return d

    def createWatchlist(self, watchlist):
        try:
            self.alpaca.createWatchlist(watchlist)
        except:
            print('something messed up')
        return "watchlist successfully created!"
    
    def deleteWatchlist(self,watchlist):
        self.alpaca.deleteWatchlist(watchlist)
        return "success!"

    def viewAllWatchlists(self):
        nameslist = self.alpaca.getAllWatchlists()
        return ', '.join(nameslist)

    def viewWatchlist(self,name):
        if name not in self.alpaca.watchlists.keys():
            return 'please provide a valid watchlist name!'
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
