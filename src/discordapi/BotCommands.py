# structure of the bot command
# [Action] [Field1] [Field2]..

help_menus = {
    'default':  
'''Command options:
    -**longshort**
    -**show**
    -**positions**
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

def help(input):
    menu = 'default'
    if not len(input) ==  0: menu = input.pop(0)
    assert(menu in help_menus.keys())
    return help_menus[menu]

commands = {
    'help': help,
    # 'longshort': longshort()
    # 'show'
    # 'positions'
}

def parse(input):
    assert(len(input)>0)
    # input is a list of strings containing the command
    com = input.pop(0)
    fn = commands[com]
    return fn(input)