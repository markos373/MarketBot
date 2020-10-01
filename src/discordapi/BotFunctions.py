

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