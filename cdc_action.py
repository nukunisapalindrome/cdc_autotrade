from binance.client import Client
import pandas as pd
import matplotlib.pyplot as plt
from time import sleep
import schedule
from datetime import datetime

class cdc_action:

    def get_data(self):
        client = Client()
        bars = client.get_historical_klines('BTCUSDT','1d','1 Jan, 2023', '1 Jan, 2025')
        df = pd.DataFrame(bars, columns=['Date','Open','High','Low','Close','Volume','Close time', 'Quote asset Volume',
                                         'Number of Trades', 'Taker Buy base asset volume','Taker buy quote asset volume',
                                         'Taker buy quote asset volume'])

        df = df.apply(pd.to_numeric)
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        df.set_index('Date', inplace=True)
        # df = df.iloc[:, 5]
        # print(df)
        return df

    def signal(self,df):
        #creating ema 12 and ema 16
        df['ema_short'] = df.Close.ewm(span=12, adjust=False, min_periods=12).mean()
        df['ema_long'] = df.Close.ewm(span=26, adjust=False, min_periods=26).mean()
        df['trend'] = df['ema_short'] > df['ema_long']
        df.loc[(df.trend == True) & (df.trend.shift() == False), 'action'] = 'buy'
        df.loc[(df.trend == False) & (df.trend.shift() == True), 'action'] = 'sell'
        df.loc[df['action'] == 'buy', 'marker_position'] = df['Low'] * 0.95
        df.loc[df['action'] == 'sell', 'marker_position'] = df['High'] * 1.05

        # buy action dataframe
        a = df.loc[df.action == 'buy']
        # sell action dataframe
        b = df.loc[df.action == 'sell']
        return df,a,b

    def plot(self,df,a,b):
        plt.figure(figsize=(10,6))
        plt.plot(df.Close, label='Close Price')
        plt.plot(df.ema_short, label='EMA 12')
        plt.plot(df.ema_long, label='EMA 26')
        plt.plot(a.marker_position, 'g^', markersize=10)
        plt.plot(b.marker_position, 'rv', markersize=10)
        plt.legend()
        return plt.show()

    def run_trading_analysis(self):
        print("Hi! Today BTC price is {}", )

        data = cdc_action.get_data()
        signals, buy_df, sell_df = cdc_action.signal(data)
        cdc_action.plot(signals, buy_df, sell_df)

cdc_action = cdc_action()
# Schedule the function to run at a specific time (e.g., 10:00 AM)
schedule.every().day.at("10:00").do(cdc_action.run_trading_analysis())
while True:
    print("Hi! Today BTC price is {}", )
    schedule.run_pending()
    sleep(1)
