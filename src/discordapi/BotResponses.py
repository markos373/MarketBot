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

def get_ls_menus(bf):
    return {
    'default':
'''longshort [add/remove] TICKER,TICKER
    ex: longshort add AAPL,MMM''',
    'add': bf.LongShort_Add,
    'remove': bf.LongShort_Remove,
    'run': bf.LongShort_Run,
    'kill': bf.LongShort_Kill,
    'view': bf.LongShort_View
    }

def get_show_menus(bf):
    return{
    'default': 'Specify what you would like to see!',
    'goose': bf.Show_Goose, 
    'positions': bf.Show_Positiions,
    'performance': bf.Show_Performance,
}