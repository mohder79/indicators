# { import the libraries
import ccxt
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
# }

# { show all rows and column
pd.set_option('display.max_rows', None)
# pd.set_option('display.max_column', None)
# }

# { load exchange
exchange = ccxt.binance({
    'options': {
        'adjustForTimeDifference': True,
    },

})
# }


# { load data as function
def fetch(symbol: str, timeframe: str, limit: int):
    print(f"Fetching {symbol} new bars for {datetime.now().isoformat()}")

    bars = exchange.fetch_ohlcv(
        symbol, timeframe=timeframe, limit=limit)  # fetch ohlcv
    df = pd.DataFrame(bars[:-1], columns=['timestamp',
                      'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index(pd.DatetimeIndex(df.timestamp))
    return df
# }


# Bollinger Bands® are a technical analysis tool developed by John Bollinger for generating oversold or overbought signals.
# There are three lines that compose Bollinger Bands: A simple moving average(middle band) and an upper and lower band.
# The upper and lower bands are typically 2 standard deviations + /- from a 20-day simple moving average, but they can be modified.

# {​Here is this Bollinger Band® formula:

# BOLU=MA(TP,n)+m∗σ[TP,n]
# BOLD=MA(TP,n)−m∗σ[TP,n]
# where:
# BOLU=Upper Bollinger Band
# BOLD=Lower Bollinger Band
# MA=Moving average
# TP (typical price)=(High+Low+Close)÷3
# n=Number of days in smoothing period (typically 20)
# m=Number of standard deviations (typically 2)
# σ[TP,n]=Standard Deviation over last n periods of TP
# ​} https://www.investopedia.com/terms/b/bollingerbands.asp


# { bollinger band
def SMA(data: str = 'BTC', src: str = 'close', length: int = 20):  # sma for middle band
    return data[src].rolling(window=length).mean()


def TP(data: str = 'BTC'):  # hlc/3 (typical price)
    return(data['high']+data['low']+data['close'])/3


def BOLU(data: str = "BTC", src: str = 'tp', length: int = 20, m: int = 2):  # upperband
    return SMA(data, src, 20)+((m)*data[src].rolling(window=length).std())


def BOLD(data: str = 'BTC', src: str = 'tp', length: int = 20, m: int = 2):  # lower band
    return SMA(data, 'close', 20)-((m)*data[src].rolling(window=length).std())
# ​}


# { ATR (averge true range)
def ATR(data: str = 'BTC', length: int = 20):
    tr = abs(data['high']-data['low'])
    atr = tr.rolling(window=length).mean()
    return atr
# ​}


# Keltner Channels are volatility-based bands that are placed on either side of an asset's price and can aid in determining the direction of a trend.
# The exponential moving average (EMA) of a Keltner Channel is typically 20 periods, although this can be adjusted if desired.
# The upper and lower bands are typically set two times the average true range (ATR) above and below the EMA, although the multiplier can also be adjusted based on personal preference.
# Price reaching the upper Keltner Channel band is bullish, while reaching the lower band is bearish.
# The angle of the Keltner Channel also aids in identifying the trend direction. The price may also oscillate between the upper and lower Keltner Channel bands, which can be interpreted as resistance and support levels.
# Keltner Channel Calculation :
# Keltner Channel Middle Line=EMA
# Keltner Channel Upper Band=EMA+2∗ATR
# Keltner Channel Lower Band=EMA−2∗ATR
# where:
# EMA=Exponential moving average (typically over 20 periods)
# ATR=Average True Range (typically over 10 or 20 periods)
# } https://www.investopedia.com/terms/k/keltnerchannel.asp


# { Keltner channel (this calculetion is difrent and like Squeeze Momentum Indicator [LazyBear] in tradingview )
def UPPERKC(data: str = 'BTC', src: str = 'close', length: int = 20, multKC: float = 1.5):
    ma = SMA(data, src, length)
    rangema = ATR(data, length)
    upperKC = ma + rangema * multKC
    return upperKC


def LOWERKC(data: str = 'BTC', src: str = 'close', length: int = 20, multKC: float = 1.5):
    ma = SMA(data, src, length)
    rangema = ATR(data, length)
    lowerKC = ma - rangema * multKC
    return lowerKC

# ​}


# { Squeeze finder
def SQZON(data: str = 'BTC', upperband: str = 'upperband', lowerband: str = 'lowerband', upperKC: str = 'upperKC', lowerKC: str = 'lowerKC'):
    return (data[lowerband] > data[lowerKC]) and (data[upperband] < data[upperKC])


def SQZOFF(data: str = 'BTC', upperband: str = 'upperband', lowerband: str = 'lowerband', upperKC: str = 'upperKC', lowerKC: str = 'lowerKC'):
    return (data[lowerband] < data[lowerKC]) and (data[upperband] < data[upperKC])
# ​}


# { set the symbol for data function
BTC = fetch('BTC/USDT', '1h', 1000)
# }


# { use bollinger band functions to calculate  bbband
BTC['middelband'] = SMA(BTC, 'close', 20)
BTC['tp'] = TP(BTC)
BTC['upperband'] = BOLU(BTC, 'tp')
BTC['lowerband'] = BOLD(BTC, 'tp')
# }


# { use keltner channel functions for calculate upper and lower kc channel
BTC['upperKC'] = UPPERKC(BTC)
BTC['lowerKC'] = LOWERKC(BTC)
# }


# { use squeez finder functions
BTC['in_sqz'] = BTC.apply(SQZON, axis=1)
BTC['out_sqz'] = BTC.apply(SQZOFF, axis=1)
# }


# { for set marker color
BTC['squeez'] = np.where(BTC['in_sqz'] == True,
                         BTC['lowerKC']*0.9, np.NAN)  # gray

BTC['bullish_momentum'] = np.where((BTC['in_sqz'] == False) & (
    BTC['close'] > BTC['middelband']), BTC['lowerKC']*0.9, np.NAN)  # green

BTC['berish_momentum'] = np.where((BTC['in_sqz'] == False) & (
    BTC['close'] < BTC['middelband']), BTC['lowerKC']*0.9, np.NAN)  # red
# }


# { for candlestick color (set new dataframe)
berish = BTC[(BTC['in_sqz'] == False) & (
    BTC['close'] < BTC['middelband'])]
not_berish = BTC[BTC.index.isin(berish.index)].index

bulish = BTC[(BTC['in_sqz'] == False) & (
    BTC['close'] > BTC['middelband'])]
not_bulish = BTC[BTC.index.isin(bulish.index)].index

sqz = BTC[BTC['in_sqz'] == True]
not_sqz = BTC[BTC.index.isin(sqz.index)].index
# }


# print(BTC)


# {  plot the data
fig = go.Figure()

fig.add_trace(go.Candlestick(x=BTC.index,
                             open=BTC['open'],
                             high=BTC['high'],
                             low=BTC['low'],
                             close=BTC['close'],
                             name='Candlestick',
                             visible='legendonly'))


fig.add_traces(go.Candlestick(x=berish.index,
                              open=berish['open'], high=berish['high'],
                              low=berish['low'], close=berish['close'],
                              increasing_line_color='red',
                              decreasing_line_color='DarkRed',
                              name='Berish momentum(+/-)'))

fig.add_traces(go.Candlestick(x=bulish.index,
                              open=bulish['open'], high=bulish['high'],
                              low=bulish['low'], close=bulish['close'],
                              increasing_line_color='SpringGreen',
                              decreasing_line_color='DarkGreen',
                              name='Bulish momentum(+/-)'))

fig.add_traces(go.Candlestick(x=sqz.index,
                              open=sqz['open'], high=sqz['high'],
                              low=sqz['low'], close=sqz['close'],
                              increasing_line_color='Silver',
                              decreasing_line_color='DimGrey',
                              name='Squeez(+/-)'))


fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['middelband'],
                         opacity=1,
                         line=dict(color='orange', width=2),
                         name='middelband',
                         visible='legendonly'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['upperband'],
                         fill=None,
                         mode='lines',
                         line_color='rgba(0, 0, 255, 0.5)',
                         line=dict(width=2),
                         name='upperband',
                         visible='legendonly'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['lowerband'],
                         opacity=0.3,
                         fill='tonexty',
                         line=dict(width=2),
                         name='lowerband',
                         line_color='rgba(0, 0, 255, 0.5)',
                         mode='lines', fillcolor='rgba(0, 0, 255, 0.1)',
                         visible='legendonly'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['upperKC'],
                         opacity=1,
                         line=dict(color='blue', width=2),
                         name='upperKC',
                         visible='legendonly'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['lowerKC'],
                         opacity=1,
                         line=dict(color='blue', width=2),
                         name='lowerKC',
                         visible='legendonly'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['squeez'],
                         mode='markers',
                         marker=dict(color='gray', size=5,
                                     opacity=1),
                         marker_symbol=203,
                         name='squeez',
                         visible='legendonly'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['bullish_momentum'],
                         mode='markers',
                         marker=dict(color='green', size=5,
                                     opacity=1),
                         marker_symbol=5,
                         name='bullish momentum',
                         visible='legendonly'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['berish_momentum'],
                         mode='markers',
                         marker=dict(color='red', size=5,
                                     opacity=1),
                         marker_symbol=6,
                         name='berish momentum',
                         visible='legendonly'))

fig.show()
