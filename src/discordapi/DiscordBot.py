import discord
from AlphaVantage.AlphaParser import AlphaParser

class DiscordBot:
    def __init__(self,token,alpha, alpaca):
        client = discord.Client()
        print('bot ready to go')
        self.alpha = alpha
        self.alpaca = alpaca
        self.wlist = None
        self.userSettings = {}

        @client.event
        async def on_ready():
            print(f'{client.user} is a very bad bot')

        @client.event
        async def on_message(message):
            if message.author == client.user:
                return
            print(message.content)
            input = message.content.split()
            msg = ''
            user = message.author
            if not isinstance(message.channel,discord.DMChannel):
            # messages in server
                print("message in guild!")
                if '672484881208442894' in message.content:
                    # bot is mentioned
                    print("I have been summoned")
                    msg += self.respondMention()
            else:
                if user not in self.userSettings.keys():
                    self.userSettings[user] = {}
                # messages in dm
                # this is where we parse user messages
                if 'help' in input:
                    msg = self.help()
                elif 'data' in input:
                    # for now we will just return SMA
                    msg = self.getdata()
                elif 'watchlist' in input:
                    if 'create' in input:
                        slist = input[input.index('create')+1:]
                        print('creating watchlist for ', slist)
                        msg = self.createWatchlist(slist)
                    elif 'view' in input:
                        msg = self.viewWatchlist()    
                elif 'add' in input:
                    i = input.index('add')
                    if not input[i+1]:
                        msg = 'please specify an input!'
                else:
                    msg = 'how can I help? (type \'help\' to see options)'
            if msg:
                await message.channel.send(msg)

        client.run(token)

    def getAlpha(self):
        return self.alpha

    def help(self):
        helpmenu = 'options:\n'
        helpmenu += '\t-data\n'
        helpmenu += '\t-stats\n'
        helpmenu += '\t-add symbol\n' 
        helpmenu += '\t-watchlist:\n'
        helpmenu += '\t\t-create [inputs: \'symbol_0\',\'symbol_1\', ..]\n'
        helpmenu += '\t\t example: watchlist create MSFT TSLA\n'
        helpmenu += '\t\t-view\n'
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
            print('something fucked up')
        return "watchlist successfully created!"

    def viewWatchlist(self):
        wlist = self.alpaca.getWatchlist()
        print(wlist)
        return 'yes'
