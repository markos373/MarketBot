import multiprocessing as mp
from prettytable import PrettyTable
import discord

# Pipe class for talking to process

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


# I think these functions should be named more generically, 
# because a lot of these operations (run,kill,add,view ..) can apply to any other algo that is not longshort.
class BotFunctions:
    def __init__(self,discordbot):
        self.dcbot = discordbot
    
    # required arg: input
    def LongShort_Add(self,inputstr):
        StockUniverse = self.dcbot.StockUniverse
        assert(type(inputstr) == type('string'))
        input = inputstr.split(',')
        # the input must be an array of length 1 or greater
        for i in input: StockUniverse.add(i)
        return 'Adding {}'.format(input)

    # required arg: input
    def LongShort_Remove(self,inputstr):
        StockUniverse = self.dcbot.StockUniverse
        assert(type(inputstr) == type('string'))
        input = inputstr.split(',')
        #Add Typecheck
        for i in input: StockUniverse.discard(i)      
        return 'Removing {}'.format(input)
    
    def LongShort_Run(self):
        msg = self.dcbot.start_instance("longshort")
        return msg

    def LongShort_Kill(self):
        # msg = self.dcbot.kill_instance()
        return [(self.dcbot.kill_instance,{})]
    
    def LongShort_View(self):
        msg = "Stock Universe: {}".format(list(self.dcbot.StockUniverse))
        return msg
    
    def Show_Goose(self,channel):
        print('hey they let me go')
        goosepicture = 'src/img/madgoose.png'
        return [(channel.send,
            {'file': discord.File(goosepicture)})]
    
    def Show_Positiions(self,channel):
        pics = self.dcbot.img_gen.positions_chart()
        if pics == 'invalid':
            return 'Could not generate a positions chart!\nMaybe open some positions first?'
        return [(channel.send,
            {'file':pp}) for pp in pics]

    def Show_Performance(self,channel,timeperiod='week'):
        pic = self.dcbot.img_gen.portfolio_graph(timeperiod)
        print(pic)
        return [(channel.send,
            {'file':pic})]


    def Get_Positions(self):
        positions = self.dcbot.alpaca.listPositions()
        headers = ["Symbol","Avg Buy Price","Curr Price","Qty","Curr Diff"]
        table = PrettyTable(headers)
        for position in positions:
            table.add_row([position.symbol,position.avg_entry_price,position.current_price,position.qty,position.unrealized_pl])
        msg = '```'+table.get_string()+'```'
        return msg

    # def send_img(self,channel,img):
    #     channel.send(file=img)
