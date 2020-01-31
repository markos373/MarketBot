import alpaca_trade_api as tradeapi
from alpaca.AlpacaConnection import AlpacaConnection
from AlphaVantage.AlphaParser import AlphaParser
from discordapi.DiscordBot import DiscordBot

import json
import logging
import sys
import requests

CONFIGURATION_FILE_PATH = "../settings.json"

if __name__ == "__main__":
    logging.basicConfig(filename="python.log", filemode="w", format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)
    logger = logging.getLogger()

    key_id = secret_key = ""
    AlphaAPIKey = ""
    try:
        file = open(CONFIGURATION_FILE_PATH, "r")
        data = json.load(file)
        key_id = data["config"]["alpaca_key_id"]
        secret_key = data["config"]["alpaca_private_key"]
        AlphaAPIKey = data["config"]["alphavantage_key"]
        discordToken = data["config"]["discord_token"]
    except:
        logger.fatal("ERROR: failed to extract keys from configuration file located at \"%s\"" % CONFIGURATION_FILE_PATH)
        sys.exit()
    alpaca = AlpacaConnection(logger, key_id, secret_key)
    #account = alpaca.getAccountInformation()


    #print(account)
   ## r = alpaca.submitOrder("AAPL", 1, 'buy','market','gtc')
   # print(r)
    # tickers_list = ["TSLA", "MSFT"]
    # print(alpaca.listPositions())
    #alpaca.createWatchlist(tickers_list)
    account = alpaca.getAccountInformation()
    print(account)

    alpha = AlphaParser(AlphaAPIKey, "MSFT", "weekly","10","open")
    bot = DiscordBot(discordToken, alpha)

    dataset = alpha.getSMAvalue()
    print(dataset)

    tickers_list = ["TSLA", "MSFT"]
    alpaca.createWatchlist(tickers_list)

    wlist = alpaca.getWatchlist()
    print(wlist)

    logging.shutdown()