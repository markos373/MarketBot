import multiprocessing as mp
import time
import threading
import datetime

'''
How to use:
use the longshort class as an example.
In the __init__ funciton, include a call to
super().__init__(pipe,logger,alpaca)
this will take care of the pipeline creation

To send a message to the user directly, use self.talk()

To store messages in a queue to burst after a certain point, 
(useful in case of too many messages) use self.m_queue.add_msg()
and it will take care of sending the message on its own 
(after it stacks to 10 messages)

To make sure the running loops are terminated, 
use self.stop as a checking parameter (ex. 'while not self.stop')
and use self.killcheck() to terminate the listener correctly.

Whenever sleep calls are necessary, use self.asleep() instead. 
This will ensure the termination happens immediately rather than 
waiting on the sleep call to finish

To check if market is open (and wait if it is not), call self.checkMarketOpen()
This function will keep everything on hold if market is not open, and will pass if it is open
'''

class BaseStrat:
    def __init__(self, pipe, logger, alpaca):
        print('base class here')
        self.pipe = pipe
        self.stop = False
        self.logger = logger
        self.alpaca = alpaca
        self.listener = threading.Thread(target= self.waiter_thread)
        self.m_queue = message_queue(self.pipe)
        self.listener.start()
        print('started listner')

    def waiter_thread(self):
        while True:
            if self.pipe.has_data():
                msg = self.pipe.read()
                if msg == 'kill':
                    print('kill signal received from discord')
                    self.logger.info('Algo: kill signal received from discord')
                    self.kill()
                    return
                else:
                    # add additional parameters in here
                    print("discord said something!")

    def talk(self,msg):
        self.pipe.send(msg)
    
    def kill(self):
        self.talk("wrapping up...")
        self.logger.info("Algo: Setting stop to true..")
        self.stop = True

    def killcheck(self):
        if self.stop:
            print('killing listener first')
            self.listener.join()
            self.logger.info("Algo: listener successfully terminated")

    def asleep(self,t):
        # im gonna replace all the time sleep calls with this so that 
        # the thread doesnt sleep when the user wants it to die
        counter = 0
        while not self.stop and counter < t:
            time.sleep(1)
            counter += 1
        self.logger.info('Algo: This guy tried to sleep but he ain\'t slick')

    def checkMarketOpen(self):
        tAMO = threading.Thread(target=self.awaitMarketOpen)
        tAMO.start()
        tAMO.join()

    def awaitMarketOpen(self):
        isOpen = self.alpaca.get_clock().is_open
        while not isOpen and not self.stop:
            clock = self.alpaca.get_clock()
            openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            timeToOpen = int((openingTime - currTime) / 60)
            self.m_queue.add_msg(str(timeToOpen) + " minutes til market open.")      
            self.asleep(60 * 5)
            # five minutes
            isOpen = self.alpaca.get_clock().is_open
            self.killcheck()

class message_queue:
    def __init__(self, pipe):
        self.message = ''
        self.msg_count = 0
        self.pipe = pipe

    def add_msg(self, msg):
        print('added message to queue:',msg,self.msg_count,'out of 10')
        self.message += msg + '\n'
        self.msg_count += 1
        if self.msg_count == 10:
            self.pipe.send(self.message)
            self.message = ''
            self.msg_count = 0