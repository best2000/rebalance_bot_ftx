from matplotlib import style
import requests
import time
import pandas
import ta
import mplfinance as mpf

# return finished caldles only (no current candle)


def get_candles(symbol: str, timeframe: str = '1h', limit: int = 500):  # 1h 4h 1d
    candles = requests.get("https://api.binance.com/api/v3/klines",
                           params={"symbol": symbol, "limit": limit, "interval": timeframe})
    return candles  # candles[-1] is newest (not current)


def cal_tech(df):
    # df['K'] = ta.momentum.stoch(
    # df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
    #df['D'] = df['K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
    # atr = ta.volatility.AverageTrueRange(
    #   df['High'], df['Low'], df['Close'], window=14)
    #df['atr'] = atr.average_true_range()
    #ema50 = ta.trend.EMAIndicator(df['Close'], window=50)
    #df['ema50'] = ema50.ema_indicator()
    #ema100 = ta.trend.EMAIndicator(df['Close'], window=100)
    #df['ema100'] = ema100.ema_indicator()
    df.dropna(inplace=True)
    return df


def plot(df):
    # vlines = dict(vlines=['2022-04-30 15:00:00',
    #         '2022-05-20 15:00:00'], linewidths=(1))
    # print(vlines)
    #alines_points = [('2022-04-30 15:00:00', 24.178654), ('2022-05-20 15:00:00', 39.397142)]
    mpf.plot(df, type='candle', volume=False, style='yahoo')


def check_ta(symbol:str, timeframe:str):
    candles = get_candles(symbol, timeframe, 1000).json()
    df = pandas.DataFrame(candles).iloc[0:-1, 0:7]
    df.columns = ['Open time', 'Open', 'High',
                  'Low', 'Close', 'Volume', 'Close Time']
    df = df.set_index('Open time')
    df = df.astype(float)
    df.index = pandas.to_datetime(df.index, unit='ms')
    df['Close Time'] = pandas.to_datetime(df['Close Time'], unit='ms')
    df = cal_tech(df)
    signal = df.query('(rsi > 70 ) | (rsi < 30)')
    if signal.iloc[-1]['Close Time'] == df.iloc[-1]['Close Time']:
        return True
    return False

#print(check_ta())


# dynamic ratio (asset confident++)
# trend down => adjust more asset ratio => buy more asset
# trend up => adjust less asset ratio => take some profit
# rebalance => down > (2atr/price)% & stoch < 80 & rsi < 30
# rebalance => up > (2atr/price)% & stoch > 80 & rsi > 70
# TREND CHECK EMA 50 & EMA 100 if down trend rebalance only on the way down if recover and trend up rebalance when price higher than started balance