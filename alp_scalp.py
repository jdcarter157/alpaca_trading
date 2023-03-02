import alpaca_trade_api as tradeapi

import pandas as pd
import time
import requests
# Define your Alpaca API credentials
api_key = ''
api_secret = ''
base_url = 'https://paper-api.alpaca.markets'

# Authenticate your client
api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
# Define the symbol and timeframe for the data
symbol = 'VOO'
timeframe = '1Min'
response = requests.get(base_url)


# Check if we can connect to the API by getting the account information
account_info = api.get_account()
print("Connected to Alpaca API. Account Info:")
print(account_info)
# Check if the symbol is valid by retrieving its asset information
asset_info = api.get_asset(symbol)
print("Asset Info for {}: ".format(symbol))
print(asset_info)

while True:
    # Load the data from Alpaca
    data = api.get_bars(symbol,timeframe,limit=288).df
    # print(data)
    time.sleep(1)  # Pause for 1 second between requests to avoid rate limiting

    # Calculate the moving averages
    ma_20 = data['close'].rolling(window=20).mean()
    ma_50 = data['close'].rolling(window=50).mean()

    # Calculate the Bollinger Bands
    std_20 = data['close'].rolling(window=20).std()
    upper_band = ma_20 + (std_20 * 1.5)
    lower_band = ma_20 - (std_20 * 1.5)

    # Create a new dataframe with the indicators
    indicators = pd.DataFrame()
    indicators['Close'] = data['close'].astype(float)
    indicators['MA_20'] = ma_20.astype(float)
    indicators['MA_50'] = ma_50.astype(float)
    indicators['Upper_Band'] = upper_band
    indicators['Lower_Band'] = lower_band
    # print(indicators)

    # Define the trading strategy function
    def trading_strategy(data):
        # print("hey")
        try:
            # If the close price is above the upper Bollinger Band and the 20-day moving average is above the 50-day moving average, sell the security
            if data['Close'] > data['Upper_Band'] and data['MA_20'] > data['MA_50']:
                return 'SELL'
            # If the close price is below the lower Bollinger Band and the 20-day moving average is below the 50-day moving average, buy the security
            elif data['Close'] < data['Lower_Band'] and data['MA_20'] < data['MA_50']:
                return 'BUY'
            else:
                return 'HOLD'
        except Exception as e:
            print(e)
            return 'HOLD'


    # Apply the trading strategy function to the indicators dataframe
    indicators['Signal'] = indicators.apply(trading_strategy, axis=1)
    # print("yoyo")

    # Define the order function
    def place_order(signal, product_id=symbol):
        # print("yurp")
        if signal == 'BUY':
            # Place a buy order for 1 unit of the product
            api.submit_order(
                symbol=symbol,
                qty=1,
                side='buy',
                type='market',
                time_in_force='gtc',
            )
            print(f"Placed a buy order for {product_id}")

        elif signal == 'SELL':
            # Place a sell order for 1 unit of the product
            api.submit_order(
                symbol=symbol,
                qty=1,
                side='sell',
                type='market',
                time_in_force='gtc',
            )
            print(f"Placed a sell order for {product_id}")
        else:
            print('No order placed')

        # Place an order based on the latest signal
    latest_signal = indicators['Signal'].iloc[-1]
    # print("latest signal")
    print(latest_signal)
    place_order(latest_signal)

