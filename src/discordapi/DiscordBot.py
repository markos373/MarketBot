import discord
from strats.longshort import LongShort
from strats.indicatorstrat import IndicatorStrat
import threading
import asyncio
import multiprocessing as mp
from chartgen.imgGenerator import imgGenerator
from discordapi.BotFunctions import BotFunctions

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
    def __init__(self,token, alpaca, logger, user):
        self.client = discord.Client()
        self.alpaca = alpaca
        self.wlist = None
        self.userSettings = {}
        self.token = token
        self.StockUniverse = set()
        self.instance = None
        self.user = None
        self.user_id = user
        self.logger = logger
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
                pass
            else:
                sender = "{}#{}".format(message.author.name,message.author.discriminator)
                if sender != self.user_id:
                    await message.author.send('You are not my boss!')
                    return
                elif not self.user:
                    self.user = message.author
                self.logger.info("Discord: User input = [{}]".format(message.content))
                if 'help' in input:
                    if 'longshort' in input:
                        msg = BotFunctions.Help('longshort')
                    elif 'show' in input:
                        msg = BotFunctions.Help('show')
                    elif 'positions' in input:
                        msg = BotFunctions.Help('positions')
                    else: 
                        msg = BotFunctions.Help('default')
                elif 'longshort' in input:
                    if 'add' in input:
                        msg = BotFunctions.LongShort_Add(self.StockUniverse,input)
                    elif 'remove' in input:
                        msg = BotFunctions.LongShort_Remove(self.StockUniverse,input)
                    elif 'run' in input:
                        msg = BotFunctions.LongShort_Run(self,p2)
                    elif 'kill' in input:
                        msg = await self.kill_instance()
                    elif 'view' in input:
                        msg = BotFunctions.LongShort_View(self.StockUniverse)
                    else:
                        msg = BotFunctions.Help('longshort')
                elif 'show' in input:
                    picture = False
                    if 'goose' in input:
                        picture = discord.File(BotFunctions.Show_Goose())
                    elif 'positions' in input:
                        picture = self.img_gen.positions_chart()
                        if len(picture) > 1: 
                            await message.channel.send(file=picture[0])
                            picture = picture[1]
                    elif 'performance' in input:
                        timeperiod = 'week'
                        if len(input) > input.index('performance')+1:
                            timeperiod = input[input.index('performance')+1]
                        picture = self.img_gen.portfolio_graph(timeperiod)
                    if picture and picture != 'invalid': 
                        await message.channel.send(file = picture)
                    elif picture == 'invalid': 
                        msg = 'No positions to display!'
                    else: 
                        msg = '''show [positions/performance] \n      
                        ex: show performance [day/week/month]'''
                elif 'positions' in input:
                    msg = BotFunctions.Show_Positions(self)
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