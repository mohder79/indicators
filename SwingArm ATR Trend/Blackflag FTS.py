# telegram: @mohder
# website: mohder.com
# email: mohder1379@gmail.com


# { import the libraries
from calculation import *
import ccxt
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
pd.options.plotting.backend = "plotly"

# }


# { show all rows and column
#pd.set_option('display.max_rows', None)
# pd.set_option('display.max_column', None)
# }


# {load exchange
exchange = ccxt.binance({
    'options': {
        'adjustForTimeDifference': True,
    },
})
# }


# inputs{
symbol = 'BTC/USDT'  # my symbol
ATRPeriod = 28
ATRFactor = 5
trailType = 'modified'  # or 'unmodified'
show_fib_entries = True
fib1Level = 61.8
fib2Level = 78.6
fib3Level = 88.6
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
df = fetch(symbol, '1d', 999)
# }


df['HiLo'] = HILO(df, 'high', 'low')


df['HRef'] = HREF(df, 'high', 'low', 'close')


# { line 37 LRef
def LREF(data: str, high: str, low: str, close: str):
    lref = np.zeros(np.size(data[high]))
    for i in range(1, np.size(data[high])):
        if df[high][i] >= df[low][i-1]:
            lref[i] = df[close][i-1] - df[low][i]
        else:
            lref[i] = (((data[close][i-1]) - (data[low])) - 0.5) * \
                ((data[low][i-1])-(data[high]))
    return lref


df['LRef'] = LREF(df, 'high', 'low', 'close')
# }


# { line 41 trueRange HiLo,
def TRUERANGE(data: str, high: str, low: str, close: str, LRef: str, HRef: str, HiLo: str):
    if trailType == 'modified':
        truerange = data[[HRef, LRef, HiLo]].max(axis=1)
    elif trailType == 'unmodified':
        truerange = np.zeros(np.size(data[high]))
        h_l = np.zeros(np.size(data[high]))
        h_prec = np.zeros(np.size(data[high]))
        l_prec = np.zeros(np.size(data[high]))
        for i in range(1, np.size(data[high])):
            h_l[i] = df[high][i] - df[low][i]
            h_prec[i] = abs(df[high][i] - df[close][i-1])
            l_prec[i] = abs(df[low][i] - df[close][i-1])
            truerange[i] = max(h_l[i], h_prec[i], l_prec[i])
        return truerange
    return truerange


df['trueRange'] = TRUERANGE(df, 'high', 'low', 'close', 'LRef', 'HRef', 'HiLo')
# }


# { line 49
def LOSS(data: str, trueRange: str, ATRPeriod: int = ATRPeriod, ATRFactor: int = ATRFactor):
    _wild = np.zeros(np.size(data['trueRange']))
    _wild[0] = 0

    for i in range(1, np.size(data['trueRange'])):
        _wild[i] = _wild[i-1] + ((data[trueRange][i] - _wild[i-1]) / ATRPeriod)
    return ATRFactor * _wild


df['loss'] = LOSS(df, 'trueRange')
# }


# { line 51 , 52
df['Up'] = df.close - df.loss
df['Dn'] = df.close + df.loss
# }


df['TrendUp'] = TRENDUP(df, 'close', 'Up')


df['TrendDown'] = TRENDDOWN(df, 'close', 'Dn')


df['Trend'] = TREND(df, 'close', 'TrendDown', 'TrendUp')


df['trail'] = np.where(df['Trend'] == 1, df['TrendUp'], df['TrendDown'])


df['ex'] = EX(df)


df['state'] = np.where(df['Trend'] == 1, "long", "short")


df['f1'] = df['ex'] + (df['trail'] - df['ex']) * fib1Level / 100
df['f2'] = df['ex'] + (df['trail'] - df['ex']) * fib2Level / 100
df['f3'] = df['ex'] + (df['trail'] - df['ex']) * fib3Level / 100
df['l100'] = df['trail'] + 0


df['color'] = np.where(df['state'] == "long", 1, 0)
df['group'] = df['color'].ne(df['color'].shift(1)).cumsum()
df = df.groupby('group')
dfs = []
for name, data in df:
    dfs.append(data)


# {  plot the data
#fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
fig = go.Figure()

for df in dfs:
    fig.add_traces(go.Scatter(x=df.index, y=df.f1,
                              line=dict(color='rgba(0,0,0,0)'),
                              showlegend=False))

    fig.add_traces(go.Scatter(x=df.index, y=df.f2,
                              line=dict(color='rgba(0,0,0,0)'),
                              fill='tonexty',
                              fillcolor=fill_df1_df2(df['color'].iloc[0]),
                              showlegend=False))

for df in dfs:
    fig.add_traces(go.Scatter(x=df.index, y=df.f2,
                              line=dict(color='rgba(0,0,0,0)'),
                              showlegend=False))

    fig.add_traces(go.Scatter(x=df.index, y=df.f3,
                              line=dict(color='rgba(0,0,0,0)'),
                              fill='tonexty',
                              fillcolor=fill_df2_df3(df['color'].iloc[0]),
                              showlegend=False))

for df in dfs:
    fig.add_traces(go.Scatter(x=df.index, y=df.f3,
                              line=dict(color='rgba(0,0,0,0)'),
                              showlegend=False))

    fig.add_traces(go.Scatter(x=df.index, y=df.l100,
                              line=dict(color='rgba(0,0,0,0)'),
                              fill='tonexty',
                              fillcolor=fill_df3_l100(df['color'].iloc[0]),
                              showlegend=False))
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 showlegend=False))


for df in dfs:
    fig.add_trace(go.Scatter(x=df.index,
                             y=df['ex'],
                             mode='markers',
                             marker=dict(color=ex_color(df['color'].iloc[0]), size=3,
                                         opacity=1),
                             marker_symbol=0,
                             name='short signal',
                             showlegend=False))


fig.show()
# }

print(np.round(df.head(10), 2))  # head data

print(np.round(df.tail(10), 2))  # tail data
