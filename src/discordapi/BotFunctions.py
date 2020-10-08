from prettytable import PrettyTable

class BotFunctions:
    def __init__():
        pass
    
    def LongShort_Add(StockUniverse,input):
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

    def LongShort_Remove(StockUniverse,input):
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

    def LongShort_Run(self, pipe):
        msg = self.start_instance(pipe,"longshort")
        return msg

    def LongShort_View(StockUniverse):
        msg = "Stock Universe: {}".format(list(StockUniverse))
        return msg
    
    def Show_Goose():
        goosepicture = 'img/madgoose.png'
        return goosepicture
    
    def Show_Positions(self):
        positions = self.alpaca.listPositions()
        headers = ["Symbol","Avg Buy Price","Curr Price","Qty","Curr Diff"]
        table = PrettyTable(headers)
        for position in positions:
            table.add_row([position.symbol,position.avg_entry_price,position.current_price,position.qty,position.unrealized_pl])
        msg = '```'+table.get_string()+'```'
        return msg

    def Help(menu):
        if menu == 'default':
            helpmenu = 'Command options:\n'
            helpmenu += '\t-longshort\n'
            helpmenu += '\t-show\n'
            helpmenu += '\t-positions\n'
            helpmenu += 'For more help, enter: help [command]\n'
        elif menu == 'longshort':
            helpmenu = '**longshort** command options:\n'
            helpmenu += '\t-**add** | info: add symbol to longshort (multiple symbols allowed, separate with \',\')\n'
            helpmenu += '\t\tenter: longshort add [symbol]\n\n'                       
            helpmenu += '\t-**remove** | info: remove symbol from longshort (multiple symbols allowed, separate with \',\')\n'
            helpmenu += '\t\tenter: longshort remove [symbol]\n\n'
            helpmenu += '\t-**run** | info: start longshort\n'
            helpmenu += '\t\tenter: longshort run\n\n'
            helpmenu += '\t-**kill** | info: terminate longshort\n'
            helpmenu += '\t\tenter: longshort kill\n\n'
            helpmenu += '\t-**view** | info: view all symbols in longshort\n'
            helpmenu += '\t\tenter: longshort view\n\n'   
        elif menu == 'show':
            helpmenu = '**show** command options:\n'
            helpmenu += '\t-**positions** | info: displays positions chart\n'
            helpmenu += '\t\tenter: show positions\n\n'
            helpmenu += '\t-**performance** | info: displays past week performance graph\n'
            helpmenu += '\t\tenter: show performance\n\n'
        elif menu == 'positions':
            helpmenu = '**positions** command options:\n'
            helpmenu += '\t-**positions** | info: displays positions table\n'
            helpmenu += '\t\tenter: positions\n\n'
        else:
            print("No menu option stated\n")
        return helpmenu