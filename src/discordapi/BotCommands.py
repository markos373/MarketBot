from discordapi.BotFunctions import BotFunctions
import discordapi.BotResponses as br
import asyncio
# structure of the bot command
# [Action] [Field1] [Field2]..

default_msg = 'how can I help? (type \'help\' to see options)'

'''
Pipeline of parsing:
call parse with given argumenets
The parse then matches the operation using head of arguments
And calls the given operation passing in the rest of arguments

Each 'opertion' (help/longshort/etc..) function should return a TIPLE
In case of returning message:   ('MSG_CONTENT',None,None)
In case of returning operation: ('FUNCTION_TOCALL',arguments,is_async)
The async check for some reason doesn't work, I think its because the async is being
called from botfuncs which is not declared as 'async'. It's a corner case for 'longshort kill'
'''

def help(input,discordbot,*_):
    menu = 'default'
    if not len(input) ==  0: menu = input.pop(0)
    assert(menu in br.help_menus.keys())
    return br.help_menus[menu],[]

def longshort(input,discordbot,*_):
    print(input)
    # the dictionary needs to be called through function because of discordbot context
    longshort_menus = br.get_ls_menus(BotFunctions(discordbot))

    async_fns = ['kill']

    menu = 'default'
    if not len(input) ==  0: menu = input.pop(0)
    assert(menu in longshort_menus.keys())
    val = longshort_menus[menu]
    if type(val) is type(list()):
        val = val[0]

    # max number of args for any longshort operation is 1
    assert(len(input) <= 1)
    args = input
    return val,args

def show(input,discordbot,channel,*_):
    menu = 'default'
    show_menus = br.get_show_menus(BotFunctions(discordbot))
    if not len(input) ==  0: menu = input.pop(0)
    assert(menu in show_menus.keys())
    val = show_menus[menu]
    args = input
    args.insert(0,channel)
    return val,args

commands = {
    'help': help,
    'longshort': longshort,
    'show': show
    # 'positions'
}

def parse(msg,discordbot):
    # dealing with commas and spaces here
    inputstr = msg.content
    inputstr = inputstr.replace(' , ',',')
    inputstr = inputstr.replace(', ',',')
    inputstr = inputstr.replace(' ,',',')
    input = inputstr.split()

    # for sending images, we need to know the channel
    channel = msg.channel
    assert(len(input)>0)
    # input is a list of strings containing the command
    com = input.pop(0)
    if not com in commands: return default_msg,None
    fn = commands[com]
    return fn(*[input,discordbot,channel])