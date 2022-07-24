# { import the libraries
import ccxt
from datetime import datetime
import pandas as pd
#import pandas_ta as ta

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# }

# { show all rows and column
pd.set_option('display.max_rows', None)
#pd.set_option('display.max_column', None)
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
    #df = df.set_index(pd.DatetimeIndex(df.timestamp))
    return df
# }


# { set the symbol for data function
BTC = fetch('BTC/USDT', '1h', 900)
# }


# { function for calculate povit high
def PIVOTHIGH(data: str = BTC['high'], left_bar: int = 14, right_bar: int = 14):
    data_len = np.size(data)
    pivothigh = []
    for i in range(data_len - right_bar):
        pivothigh.append(np.nan)
        pivot = True
        if i > left_bar:
            for x in range(left_bar + 1):
                if data[i-x] > data[i]:
                    pivot = False
            for x in range(right_bar + 1):
                if data[i+x] > data[i]:
                    pivot = False
        if pivot is True:
            pivothigh[np.size(pivothigh)-1] = data[i]
    for i in range(right_bar):
        pivothigh.append(np.nan)
    return np.round(pivothigh, 2)
# }


# { function for calculate povit low
def PIVOTLOW(data: str = BTC['low'], left_bar: int = 14, right_bar: int = 14):
    data_len = np.size(data)
    pivotlow = []
    for i in range(data_len - right_bar):
        pivotlow.append(np.nan)
        pivot = True
        if i > left_bar:
            for x in range(left_bar + 1):
                if data[i-x] < data[i]:
                    pivot = False
            for x in range(right_bar + 1):
                if data[i+x] < data[i]:
                    pivot = False
        if pivot is True:
            pivotlow[np.size(pivotlow)-1] = data[i]
    for i in range(right_bar):
        pivotlow.append(np.nan)
    return np.round(pivotlow, 2)
# }


# { ATR (averge true range)
def ATR(data: str = BTC, length: int = 14):
    h_l = data['high'] - data['low']
    h_pc = np.abs(data['high'] - data['close'].shift())
    low_pc = np.abs(data['low'] - data['close'].shift())
    tr = np.max(pd.concat([h_l, h_pc, low_pc], axis=1), axis=1)
    atr = tr.rolling(length).mean()

    return np.round(atr, 2)
# ​}


# { pivot high calclution
def SLOPE_PH(data: str, ATR: str, pivot: str, lenpivot: int = 14):
    slope = np.zeros(np.size(data))
    slope[:lenpivot] = np.nan
    for i in range(lenpivot, np.size(data), 1):
        if data[i] == 'True':
            atr = ATR[i]
            slope[i] = pivot[i]
        if data[i] == 'False':
            slope[i] = slope[i-1]-atr
    return np.round(slope)
# }


# { pivot low calclution
def SLOPE_PL(data: str, ATR: str, pivot: str, lenpivot: int = 14):
    slope = np.zeros(np.size(data))
    slope[:lenpivot] = np.nan
    for i in range(lenpivot, np.size(data), 1):
        if data[i] == 'True':
            atr = ATR[i]
            slope[i] = pivot[i]
        if data[i] == 'False':
            slope[i] = slope[i-1]+atr
    return np.round(slope)
# }


# { pivothigh
BTC['pivothigh'] = PIVOTHIGH()

BTC['pivothigh'][:14] = np.nan

BTC['pivothighfill'] = BTC['pivothigh'].fillna(method='ffill')
# }


# { pivotlow
BTC['pivotlow'] = PIVOTLOW()

BTC['pivotlow'][:14] = np.nan

BTC['pivotlowfill'] = BTC['pivotlow'].fillna(method='ffill')
# }


# { return bool if condition is true for add slope
BTC['pivothigh_bool'] = np.where(
    BTC['pivothigh'] == BTC['high'], 'True', 'False')

BTC['pivotlow_bool'] = np.where(
    BTC['pivotlow'] == BTC['low'], 'True', 'False')
# }


# { use atr function and / len(pivot) * multy
multy = 1
BTC['atr'] = np.round(ATR()/14*multy)
# }


# { use slop functions to calcluate pivot slope
BTC['slope_ph'] = SLOPE_PH(BTC['pivothigh_bool'], BTC['atr'], BTC['pivothigh'])

BTC['slope_ph'] = np.where(BTC['pivothigh_bool'] ==
                           'True', np.NAN, BTC['slope_ph'])

BTC['slope_pl'] = SLOPE_PL(BTC['pivotlow_bool'], BTC['atr'], BTC['pivotlow'])

BTC['slope_pl'] = np.where(BTC['pivotlow_bool'] ==
                           'True', np.NAN, BTC['slope_pl'])
# }


print(BTC)


# {  plot the data
#fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
fig = go.Figure()

fig.add_trace(go.Candlestick(x=BTC.index,
                             open=BTC['open'],
                             high=BTC['high'],
                             low=BTC['low'],
                             close=BTC['close'],
                             showlegend=False))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['slope_ph'],
                         opacity=0.7,
                         line=dict(color='green', width=2, dash='dot'),
                         name='pivothigh'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['slope_pl'],
                         opacity=0.7,
                         line=dict(color='red', width=2, dash='dot'),
                         name='pivotlow'))


fig.add_trace(go.Scatter(
    x=BTC.index,
    y=BTC['pivotlow'],
    mode="markers+text",
    name="Markers and Text",

    text=BTC['pivotlow'],
    textfont=dict(
        family="sans serif",
        size=15,
        color="red"
    ),
    textposition="bottom center"))

fig.add_trace(go.Scatter(
    x=BTC.index,
    y=BTC['pivothigh'],
    mode="markers+text",
    name="Markers and Text",

    text=BTC['pivothigh'],
    textfont=dict(
        family="sans serif",
        size=15,
        color="green"
    ),
    textposition="top center"))

# colors = ['green' if row['open'] - row['close'] >= 0
#           else 'red' for index, row in BTC.iterrows()]
# fig.add_trace(go.Bar(x=BTC.index,
#                      y=BTC['volume'],
#                      marker_color=colors
#                      ), row=2, col=1)

fig.show()
# }
