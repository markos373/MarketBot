# MarketBot
Ever wanted to trade stocks programmatically?  Here at MarketBot, we plan on creating a tool to analyze the equities market and execute orders via code.  Our vision is to learn about technical indicators and attempt to employ them in the creation of a profitable, automated trader.

Initialize your configuration with the following in MarketBot/settings.json
```
{
    "config": {
        "requests_interval_millis": "12000",
        "alpaca_key_id": "",
        "alpaca_private_key": "",
        "alphavantage_key": "",
        "discord_token": ""
        "discord_user_id": ""
    }
}

```
Current usage requires Python 3.7.  This bot is remote controlled via Discord, allowing for commands such as:
```
longshort [add/remove] TICKER
    Adds / removes a ticker from the universe of stocks within your longshort strategy.

longshort run
    Begins running longshort strategy.

longshort kill
    Terminates longshort.
    
longshort view 
    View current universe of stocks.

positions 
    Shows current portfolio positions and profits/loss from each position
    
show positions
    Shows the distribution of the current positions in a pie chart
    
show portfolio [day/week/month/year] 
    Shows the graph for the equity portfolio of the account for the specified time period (ending on the current day)
    If not specified, it will default to week
```
