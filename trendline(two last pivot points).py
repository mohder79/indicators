# telegram: @mohder
# website: mohder.com
# email: mohder1379@gmail.com

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
    #df = df.set_index(pd.DatetimeIndex(df.timestamp))
    return df
# }


# { set the symbol for data function
BTC = fetch('BTC/USDT', '5m', 999)
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


# { function to calculate line between pivot
def pivot_line(data: str, pivot: str, bool: str, lenpivot: int = 14):
    x = np.empty(np.size(data[pivot]))
    x[:lenpivot] = np.nan
    x2 = np.empty(np.size(data))
    x2[:lenpivot] = np.nan
    for i in range(lenpivot, np.size(data[pivot]), 1):
        if data[bool][i] == 'True':
            x[i] = data[pivot][i]
            for i2 in range(i+1,  np.size(data[pivot]), 1):
                if data[bool][i2] == 'True':

                    if data[pivot][i] > data[pivot][i2]:
                        y = i2 - i
                        mydata = -(data[pivot][i] - data[pivot][i2]) / y
                        x2[i2-1] = data[pivot][i2]
                        break
                    elif data[pivot][i] < data[pivot][i2]:
                        y = i2 - i
                        mydata = (data[pivot][i2] - data[pivot][i]) / y
                        x2[i2-1] = data[pivot][i2]
                        break
        else:
            x[i] = x[i-1] + mydata

    return x
# }


# { function to calculate trendline   (use two last pivotlow or pivothigh to calculate trend line )
def trendline(data: str, pivot: str, bool: str, pivothighfill: str, pivot_line, lenpivot: int = 14):
    x = np.zeros(np.size(data[pivot]))
    for i in range(lenpivot, np.size(data[pivot]), 1):
        if data[bool][i] == 'True':
            x[i] = data[pivot][i]
            if data[pivot][i] > data[pivothighfill][i-1]:
                v = -(data[pivot_line][i-4] - data[pivot_line][i-3])
            elif data[pivot][i] < data[pivothighfill][i-1]:
                v = -(data[pivot_line][i-4] - data[pivot_line][i-3])
            for i2 in range(i+1,  np.size(data[pivot]), 1):
                if data[bool][i2] == 'True':
                    break
        else:
            x[i] = x[i-1] + (v)
    return x


# { pivothigh
BTC['pivothigh'] = PIVOTHIGH()

BTC['pivothighfill'] = BTC['pivothigh'].fillna(method='ffill')
# }

# { pivotlow
BTC['pivotlow'] = PIVOTLOW()

BTC['pivotlowfill'] = BTC['pivotlow'].fillna(method='ffill')
# }


# { return bool. for function conditions
BTC['pivothigh_bool'] = np.where(
    BTC['pivothigh'] == BTC['high'], 'True', 'False')

BTC['pivotlow_bool'] = np.where(
    BTC['pivotlow'] == BTC['low'], 'True', 'False')
# }

# { use pivot_line and trendline function  for pivot high
BTC['pivot_line_high'] = pivot_line(
    BTC, 'pivothigh', 'pivothigh_bool')

BTC['trendline_high'] = trendline(
    BTC, 'pivothigh', 'pivothigh_bool', 'pivothighfill', 'pivot_line_high')

# }


# { use pivot_line and trendline function  for pivot low
BTC['pivot_line_low'] = pivot_line(
    BTC, 'pivotlow', 'pivotlow_bool')

BTC['trendline_low'] = trendline(
    BTC, 'pivotlow', 'pivotlow_bool', 'pivotlowfill', 'pivot_line_low')


# }


# { set nan for beter plot
BTC['pivotlow'][:14] = np.nan
BTC['pivothigh'][:14] = np.nan
BTC['trendline_high'][:100] = np.nan
BTC['trendline_low'][:100] = np.nan
BTC['pivot_line_high'][:100] = np.nan
BTC['pivot_line_low'][:100] = np.nan
BTC['pivot_line_high'] = np.where(BTC['pivothigh_bool'] ==
                                  'True', np.NAN, BTC['pivot_line_high'])
BTC['trendline_high'] = np.where(BTC['pivothigh_bool'] ==
                                 'True', np.NAN, BTC['trendline_high'])
BTC['pivot_line_low'] = np.where(BTC['pivotlow_bool'] ==
                                 'True', np.NAN, BTC['pivot_line_low'])
BTC['trendline_low'] = np.where(BTC['pivotlow_bool'] ==
                                'True', np.NAN, BTC['trendline_low'])
# }

# {  plot the data
fig = go.Figure()

fig.add_trace(go.Candlestick(x=BTC.index,
                             open=BTC['open'],
                             high=BTC['high'],
                             low=BTC['low'],
                             close=BTC['close'],
                             showlegend=False))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['pivot_line_low'],
                         opacity=1,
                         line=dict(color='black', width=2),
                         name='pivot_line_low',
                         visible='legendonly'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['trendline_low'],
                         opacity=1,
                         line=dict(color='red', width=2),
                         name='trendline_low'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['pivot_line_high'],
                         opacity=1,
                         line=dict(color='black', width=2),
                         name='pivot_line_high',
                         visible='legendonly'))

fig.add_trace(go.Scatter(x=BTC.index,
                         y=BTC['trendline_high'],
                         opacity=1,
                         line=dict(color='green', width=2),
                         name='trendline_high'))

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


fig.show()
# }
