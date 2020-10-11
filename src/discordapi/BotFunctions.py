import multiprocessing as mp

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

class BotFunctions:
    def __init__(self):
        pass
    
    def LongShort_Add(self,StockUniverse,input):
        #Add Typecheck
        msg = 'Adding {}'
        if ',' in input[input.index('add')+1]:
            addlist = set(input[input.index('add')+1].split(","))
            msg = msg.format(list(addlist))
            StockUniverse.update(addlist)
        else:
            addlist = str(input[input.index('add')+1])
            msg = msg.format(addlist)
            StockUniverse.add(addlist)
        return msg

    def LongShort_Remove(self,StockUniverse,input):
        #Add Typecheck
        msg = 'Removing {}'
        if ',' in input[input.index('remove')+1]:
            rmlist = set(input[input.index('remove')+1].split(","))
            msg = msg.format(list(rmlist))
            for thing in rmlist:
                StockUniverse.discard(thing)
        else:
            rmlist = str(input[input.index('remove')+1])
            msg = msg.format(rmlist)
            StockUniverse.remove(rmlist)      
        return msg

    # def LongShort_Run()