import requests
import json
from bs4 import BeautifulSoup

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

def get_ticker_frequency(list): 
    #TODO: Currently we look back an entire year.  Maybe cut down to ~1-3 months?
    #List of lists in the format ['BAC', '15798240001/24/2020', 'Perdue, David', 'Sale', '$1,001 - $15,000', 'R']
    freqs = dict()
    for item in list:
        if len(item[0]) > 6 or item[4] != '$50,001 - $100,000':
            #Bad data in source or not large enough purchase... skip it
            continue

        if item[0] not in freqs:
            freqs[item[0]] = dict()
            if item[3] == 'Sale':
                freqs[item[0]]['buy'] = 0
                freqs[item[0]]['sell'] = 1
            else:
                freqs[item[0]]['buy'] = 1
                freqs[item[0]]['sell'] = 0
        else:
            if item[3] == 'Sale':
                freqs[item[0]]['sell'] += 1
            else:
                freqs[item[0]]['buy'] += 1

    return freqs


def QQ_main():
    QQ_house_outfile = "housetrading.txt"
    QQ_senate_outfile = "senatetrading.txt"
    
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
    merged_dict = get_ticker_frequency(merged_list)
    #house_dict = get_ticker_frequency(house_list)
    #senate_dict = get_ticker_frequency(senate_list)

    #Temp data view
    for item in merged_dict.keys():
        print("ticker: {} | {}".format(item,merged_dict[item]))
    


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