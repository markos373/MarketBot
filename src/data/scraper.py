import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime as dt
import dateutil.relativedelta

TICKER_TRAK_URL = "http://tickertrak.com/"
QQ_SENATE_URL = "https://www.quiverquant.com/sources/senatetrading"
QQ_HOUSE_URL = "https://www.quiverquant.com/sources/housetrading"

def download_page_source(url,outfile):
    response = requests.get(url).text
    with open(outfile,"w") as fp:
        fp.write(response)
    return response

def extract_tables(src):
    #extract table from HTML
    data = []
    soup = BeautifulSoup(src, 'html.parser')
    table = soup.find('table', attrs={'id':'myTable'})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    return data

def get_file_contents(path):
    with open(path,"r") as fp:
        src = fp.read()
    return src

def get_ticker_frequency(list, lookback_months): 
    #TODO: Currently we look back an entire year.  Maybe cut down to ~1-3 months?
    #List of lists in the format ['BAC', '15798240001/24/2020', 'Perdue, David', 'Sale', '$1,001 - $15,000', 'R']
    freqs = dict()
    for item in list:

        if len(item[0]) > 6:
            #Bad data in source
            continue

        date_index = item[1].find("/")
        trade_date = dt.strptime(item[1][date_index-2:],"%m/%d/%Y")
        date_bound = dt.now() + dateutil.relativedelta.relativedelta(months=-1 * lookback_months)

        if trade_date < date_bound:# or item[4] == '$1,001 - $15,000': #Small purchases / out of date bound -> SKIP
            continue

        if item[0] not in freqs: #Initialize
            freqs[item[0]] = dict()
            freqs[item[0]]['buy'] = 0
            freqs[item[0]]['sell'] = 0
            freqs[item[0]]['unique_participants'] = set()

        freqs[item[0]]['unique_participants'].add(item[2])
        if item[3] == 'Sale':
            freqs[item[0]]['sell'] += 1
        else:
            freqs[item[0]]['buy'] += 1

    return freqs


def QQ_main():
    QQ_house_outfile = "data/housetrading.txt"
    QQ_senate_outfile = "data/senatetrading.txt"
    
    #Store page source in files
    house_src = get_file_contents(QQ_house_outfile)
    senate_src = get_file_contents(QQ_senate_outfile)

    #Uncomment to download latest (commented so that we don't scrape the site every script run)
    #download_page_source(QQ_HOUSE_URL,QQ_house_outfile)  
    #download_page_source(QQ_SENATE_URL,QQ_senate_outfile)

    #Extract table from HTML source
    house_list = extract_tables(house_src)
    senate_list = extract_tables(senate_src)

    #Merge + categorize buy / sells
    merged_list = house_list + senate_list
    merged_dict = get_ticker_frequency(merged_list,3)
    #house_dict = get_ticker_frequency(house_list)
    #senate_dict = get_ticker_frequency(senate_list)

    #Sort by buy to sell ratios
    ticker_list = sorted(merged_dict.items(), key=lambda k_v: k_v[1]['buy']/(1 if k_v[1]['sell']==0 else k_v[1]['sell']), reverse=True)
    #for i in range(15):
    #    print(ticker_list[i])
    return ticker_list
    


if __name__ == "__main__":
    QQ_main()




''' In case we return to tickertrak idea
def extract_data(src):
    #Regex definitely better for this.
    start,end = src.find('var arrayFromPHP = '), src.find('<script src="js/ana.js"></script>')
    return src[start+19:end-23]

def str_to_list(string):
    return json.loads(string)

def filter_list(list, category, lookback_hours):
    #lookback_hours as string
    #List format [Category, Ticker Company Name, Ticker, Lookback_Hours, Upvotes, Mentions, Mentions Change %, Upvotes Change %, RANK]
    #            [0       , 1                  , 2     , 3             , 4      , 5       , 6                , 7               , 8]
    filtered = []
    for element in list:
        if category in element and element[3] == lookback_hours:
            filtered.append(element)
    return filtered

def calc_upvotes_per_mention(data):
    #todo
    return None

def TT_main():
    TT_outfile = "temp.txt"
    #get_page_source("http://tickertrak.com/",TT_outfile)
    with open(TT_outfile,"r") as fp:
        src = fp.read()
    
    data = extract_data(src)
    
    data_as_list = str_to_list(data)
    
    filtered_data = filter_list(data_as_list,'Stocks', '72')
    print(filtered_data)
    '''