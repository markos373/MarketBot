import alpaca_trade_api as tradeapi
from alpaca.AlpacaConnection import AlpacaConnection
from AlphaVantage.AlphaParser import AlphaParser
from discordapi.DiscordBot import DiscordBot
from strats.longshort import LongShort
import strats.indicatorstrat
import strats.backtest
import json
import logging
import sys
import requests
import threading

CONFIGURATION_FILE_PATH = "settings.json"

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
        user_id = data['config']['discord_user_id']
    except:
        logger.fatal("ERROR: failed to extract keys from configuration file located at \"%s\"" % CONFIGURATION_FILE_PATH)
        print("settings file required!")
        sys.exit()
        
    #strats.backtest.run(key_id,secret_key,True,['AAPL','GOOG','AMZN'])
    #strats.backtest.run(key_id,secret_key,True,['AAPL','MSFT'])
    IStrat = strats.indicatorstrat.IndicatorStrat(key_id,secret_key)
    IStrat.run()
    #test.run()
    #alpaca = AlpacaConnection(logger, key_id, secret_key)
    #bot = DiscordBot(discordToken, alpaca,logger,user_id)
    #bot.run()
    
    logging.shutdown()

