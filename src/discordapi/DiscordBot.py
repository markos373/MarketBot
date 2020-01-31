import discord

class DiscordBot:
    def __init__(self,token):
        client = discord.Client()
        print('bot ready to go')

        @client.event
        async def on_ready():
            print(f'{client.user} is a very bad bot')

        @client.event
        async def on_message(message):
            if message.author == client.user:
                return
            print(message.content)
            msg = ''
            if not isinstance(message.channel,discord.DMChannel):
            # messages in server
                print("message in guild!")
                if '672484881208442894' in message.content:
                    # bot is mentioned
                    print("I have been summoned")
                    msg += self.respondMention()
            else:
                # messages in dm
                # this is where we parse user messages
                if '--help' in message.content:
                    msg += self.help()
                else:
                    msg = 'how can I help? (type \'help\' to see options)'
            if msg:
                await message.channel.send(msg)

        client.run(token)

    def perv(self):
        return 'it\'s not even monday yet, you dick!\n'

    def help(self):
        helpmenu = '--options\n'
        helpmenu += '-data (function, param)\n'
        helpmenu += '-stats'
        return helpmenu

    def respondMention(self):
        return 'type --help in my dm for more info!\n'