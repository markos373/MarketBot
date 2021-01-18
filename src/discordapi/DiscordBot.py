import discord
from strats.longshort import LongShort
from strats.indicatorstrat import IndicatorStrat
import threading
import asyncio
from chartgen.imgGenerator import imgGenerator
from discordapi.BotFunctions import BotFunctions,Pipe,create_pipe
from discordapi.BotCommands import parse
import inspect

def is_str(word):
    return type(word) == type('str')

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
        self.listen_pipe = p2
        
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
            if not isinstance(message.channel,discord.DMChannel):
                # skip if it is not dm
                pass
            else:
                sender = "{}#{}".format(message.author.name,message.author.discriminator)
                if sender != self.user_id:
                    # if not the registered user
                    await message.author.send('You are not my boss!')
                    return
                elif not self.user:
                    self.user = message.author
                self.logger.info("Discord: User input = [{}]".format(message.content))
                operation,arguments = parse(message,self)
                # if no operation, the operation variable contains the string
                if is_str(operation):
                    msg = operation
                # elif is_async:
                #     print('heyy this guy async')
                #     # checking if function is async or not
                #     msg = await operation(*arguments)
                else:
                    msg = operation(*arguments)
                # if the message is not a string, 
                # it is an async function that needs to be evaluated
                # it will come in a nested form of tuples in lists
                if not is_str(msg):
                    for m in msg:
                        msg = await m[0](**m[1])
                    if not is_str(msg): msg = ''
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
    def start_instance(self,algo):
        pipe = self.listen_pipe
        self.logger.info('Discord: Received user input for algo start')
        msg = ''
        if self.instance is None:
            msg = "Starting {}!".format(algo)
            if algo == "longshort":
                self.algo = LongShort(self.alpaca.key_id, self.alpaca.secret_key,pipe,self.logger,self.StockUniverse)
            if algo == "indicator":
                self.algo = IndicatorStrat(self.alpaca.key_id, self.alpaca.secret_key,pipe,self.logger,self.StockUniverse)
            # self.instance = mp.Process(target=self.algo.run)
            self.instance = threading.Thread(target = self.algo.run)
            self.instance.start()
            self.instance_kill = False
            self.logger.info('Discord: Algorithm initiated')
        else:
            msg = "{} is already running!".format(algo)
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