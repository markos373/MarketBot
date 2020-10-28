from discordapi.BotFunctions import BotFunctions
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

#################################################################
# DO NOT TAB THIS STUFF IT WILL MESS UP THE ALIGNMENT OF OUTPUT #
#################################################################
help_menus = {
    'default':  
'''Command options:
    - **longshort**
    - **show**
    - **positions**
For more help, enter: help [command]''',
    'longshort':
'''**longshort** command options:
    -**add**    | info: add symbol to longshort (multiple symbols allowed, separate with \',\')
        enter: longshort add [symbol]\n
    -**remove** | info: remove symbol from longshort (multiple symbols allowed, separate with \',\')
        enter: longshort remove [symbol]\n
    -**run**    | info: start longshort
        enter: longshort run\n
    -**kill**   | info: terminate longshort\n
        enter: longshort kill\n
    -**view**   | info: view all symbols in longshort
        enter: longshort view\n''',
    'show':
'''**show** command options:
    -**positions**   | info: displays positions chart
        enter: show positions\n
    -**performance** | info: displays past week performance graph
        enter: show performance\n''',
    'positions':
'''**positions** command options:\n
    -**positions**   | info: displays positions table
        enter: positions\n'''
}

def help(input,discordbot):
    menu = 'default'
    if not len(input) ==  0: menu = input.pop(0)
    assert(menu in help_menus.keys())
    return help_menus[menu],[],False

def longshort(input,discordbot):
    print(input)
    bf = BotFunctions(discordbot)
    # the dictionary needs to be inside method to use discordbot
    longshort_menus = {
    'default':
'''longshort [add/remove] TICKER,TICKER
    ex: longshort add AAPL,MMM''',
    'add': bf.LongShort_Add,
    'remove': bf.LongShort_Remove,
    'run': bf.LongShort_Run,
    'kill': bf.LongShort_Kill,
    'view': bf.LongShort_View
    }

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
    return val,args,menu in async_fns

commands = {
    'help': help,
    'longshort': longshort
    # 'show'
    # 'positions'
}

def parse(inputstr,discordbot):
    # dealing with commas and spaces here
    inputstr = inputstr.replace(' , ',',')
    inputstr = inputstr.replace(', ',',')
    inputstr = inputstr.replace(' ,',',')
    input = inputstr.split()

    assert(len(input)>0)
    # input is a list of strings containing the command
    com = input.pop(0)
    if not com in commands: return default_msg,None
    fn = commands[com]
    return fn(input,discordbot)