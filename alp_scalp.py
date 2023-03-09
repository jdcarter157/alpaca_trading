import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream import Stream

import pandas as pd
import time
import requests

# Define your Alpaca API credentials
api_key = 'PK29T59TY9HH3UJPEJLG'
api_secret = 'j3aozAJ74WNBgDQVR4SVl8wZW0Qe0yfWouQfZTqj'
base_url = 'https://paper-api.alpaca.markets'

# Authenticate your client
api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

# Define the symbol and timeframe for the data
symbol = 'VOO'
timeframe = '1Min'

# Check if we can connect to the API by getting the account information
account_info = api.get_account()
print("Connected to Alpaca API. Account Info:")
print(account_info)
# Check if the symbol is valid by retrieving its asset information
asset_info = api.get_asset(symbol)
print("Asset Info for {}: ".format(symbol))
print(asset_info)


# Define the trading strategy function
def trading_strategy(indicators):
    print("entered trading strategy:")
    try:
        # If the close price is above the upper Bollinger Band and the 20-day moving average is above the 50-day moving average, sell the security
        if indicators['price'].iloc[-1] >= indicators['Upper_Band_Tight'].iloc[-1]:
            return 'SELL'
        # If the close price is below the lower Bollinger Band and the 20-day moving average is below the 50-day moving average, buy the security
        elif indicators['price'].iloc[-1] <= indicators['Lower_Band_Tight'].iloc[-1] :
            return 'BUY'
        else:
            return 'HOLD'
    except Exception as e:
        print(e)
        return "EXE"


# Define the order function
def place_order(signal, product_id=symbol):
    print("entered place order:")
    if signal == 'BUY':
        # Place a buy order for 1 unit of the product
        api.submit_order(
            symbol=symbol,
            qty=1,
            side='buy',
            type='market',
            time_in_force='gtc',
        )
        print('\033[92m' + f"Placed a buy order for {product_id} "+ '\033[0m')

    elif signal == 'SELL':
        # Place a sell order for 1 unit of the product
        api.submit_order(
            symbol=symbol,
            qty=1,
            side='sell',
            type='market',
            time_in_force='gtc',
        )
        print('\033[93m' +f"Placed a sell order for {product_id}"+ '\033[0m')
    elif signal == 'HOLD':

        print(f"HOLD or WAIT for better opportunities on {product_id}")


# Create an empty dataframe to store the quotes
data = pd.DataFrame(columns=['symbol', 'bid_exchange', 'bid_price', 'bid_size', 'ask_exchange', 'ask_price', 'ask_size', 'conditions', 'tape', 'timestamp'])

async def quote_callback(q):
    # print('quote', q)

    # Convert the quote object to a dictionary
    q_dict = q._raw


    # Append the quote to the dataframe
    global data
    # data = data.append(q_dict, ignore_index=True)
    data = pd.concat([data, pd.DataFrame.from_dict([q_dict])], ignore_index=True)
    # print('data',data)
    # Convert the timestamp column to a datetime object
    # data['timestamp'] = pd.to_datetime(data['timestamp'], unit='us').tz_localize('UTC').tz_convert('US/Eastern')

    # Calculate the moving averages and Bollinger Bands
    ma_20 = data['bid_price'].rolling(window=20).mean()

    ma_50 = data['bid_price'].rolling(window=50).mean()
    std_20 = data['bid_price'].rolling(window=20).std()

    upper_band = ma_20 + (std_20 * 1.5)
    lower_band = ma_20 - (std_20 * 1.5)
    upper_band_tight = round(ma_20 + (std_20 * 1.25),2)
    lower_band_tight = round(ma_20 - (std_20 * 1.25),2)
    # Create a new dataframe with the indicators
    indicators = pd.DataFrame()
    indicators['price'] = data['bid_price'].astype(float)
    indicators['MA_20'] = ma_20.astype(float)
    indicators['MA_50'] = ma_50.astype(float)
    indicators['Upper_Band'] = upper_band
    indicators['Lower_Band'] = lower_band
    indicators['Upper_Band_Tight'] = upper_band_tight
    indicators['Lower_Band_Tight'] = lower_band_tight
    print("indicators",indicators.tail(1))
    # print("length of data",len(data))


    place_order(trading_strategy(indicators))

# Initiate the quote stream
stream = Stream(api_key, api_secret, base_url="wss://stream.data.alpaca.markets/v2/iex",
                data_feed='iex')
stream.subscribe_quotes(quote_callback, symbol)
try:
    stream.run()
except Exception as e:
    print(e)
print("see you next trading day")
