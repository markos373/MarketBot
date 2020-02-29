import discord
from strats.longshort import LongShort
from AlphaVantage.AlphaParser import AlphaParser
import threading
import asyncio
from multiprocessing import Pipe

class DiscordBot:
    def __init__(self,token,alpha, alpaca):
        self.client = discord.Client()
        self.alpha = alpha
        self.alpaca = alpaca
        self.wlist = None
        self.userSettings = {}
        self.token = token
        self.LSUniverse = set()
        self.instance = None
        self.user = None
    
    #===================Piping====================

        p1,p2 = Pipe(True)
        e1 = threading.Event()  #FOR DISCORD TO SET ONLY
        e2 = threading.Event()  #FOR ALGO TO SET ONLY
        algoside_pipe = (p1,e2,e1)
        disc_algo_pipe = (p2,e1,e2)
    #=============================================

        # piping protocol: calling recv on an empty pipe will cause the program to indefinitely hang
        # to get around this, we use two threading.Event() with it as a triple.
        # Each process will raise the event flag when sending data, and the receiveing end should rest it

        self.algo = LongShort(self.alpaca.key_id, self.alpaca.secret_key,algoside_pipe)
        self.algopipe = disc_algo_pipe
        # self.listener = threading.Thread(target = self.waiter_thread)
        
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
                elif '!longshort' in input:
                    if '-add' in input:
                        if ',' in input[input.index('-add')+1]:
                            addlist = set(input[input.index('-add')+1].split(","))
                            print("hit this")
                        else:
                            addlist = set(input[input.index('-add')+1])
                        print(input)
                        msg = 'adding {}'.format(list(addlist))
                        self.LSUniverse.update(addlist)
                    elif '-remove' in input:
                        if ',' in input[input.index('-remove')+1]:
                            rmlist = set(input[input.index('-remove')+1].split(","))
                        else:
                            rmlist = set(input[input.index('-remove')+1])
                        msg = 'removing {}'.format(list(rmlist))
                        for thing in rmlist:
                            self.LSUniverse.discard(thing)
                    elif '-run' in input:
                        self.instance = threading.Thread(target = self.algo.run)
                        self.instance.start()
                        print("started algo")
                        msg= 'Successfully starting running algo!'
                    elif '-view' in input:
                        msg = "Stock Universe: {}".format(list(self.LSUniverse))
                    else:
                        msg = """!longshort -[add/remove] TICKER,TICKER\n
                               ex: !longshort -add AAPL,MMM"""
                elif 'algo' in input:
                    print("user said algo!")
                    self.talk_to_algo("hey there algo")
                else:
                    msg = 'how can I help? (type \'help\' to see options)'
            if msg:
                await message.channel.send(msg)

    async def listener(self):
        await self.client.wait_until_ready()
        print('what does this say:', self.client.is_closed())
        while not self.client.is_closed():
            # make sure a valid user exists!
            print('ima a pieec of shit')
            if(self.algopipe[2].isSet()):
                print('algo sent me a message:',self.algopipe[2].isSet())
            if self.user and self.algopipe[2].isSet():
                algomsg = self.algopipe[0].recv()
                await self.user.send(algomsg)
                self.algopipe[2].clear()
                print("do i get here?")
            await asyncio.sleep(3) 
    
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

    def talk_to_algo(self,msg):
        self.algopipe[0].send(msg)
        self.algopipe[1].set()