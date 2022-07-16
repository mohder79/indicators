# { import the libraries
import ccxt
from datetime import datetime
import pandas as pd
import pandas_ta as ta
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# }

# { show all rows and column
pd.set_option('display.max_rows', None)
#pd.set_option('display.max_column', None)
# }

# { load exchange
exchange = ccxt.bybit({
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
#    df = df.set_index(pd.DatetimeIndex(df.timestamp))
    return df
# }


# { function for calculate EMA metod 1
def EMA(data: str, src: str, length: int):
    return np.round(data[src].ewm(span=length, min_periods=length, adjust=False).mean(), 2)
# }


# { function for calculate EMA metod 2
def EMA2(data: str, src: str, Length: int, smoothing=2):
    EMA = np.zeros(np.size(data[src]))
    emasize = np.size(data[src])
    EMA[:Length-1] = np.NaN
    EMA[Length-1] = np.mean(data[src][:Length])
    for i in range(Length, emasize):
        EMA[i] = (((smoothing/(Length + 1)) * data[src][i]) +
                  ((1-(smoothing/(Length + 1))) * EMA[i-1]))
    return np.round(EMA, 2)
# }


# { set the symbol for data function
BTC = fetch('BTC/USDT:USDT', '1d', 200)
# }


BTC['ema1'] = EMA(BTC, 'close', 15)  # use function for calculate ema metod 1

BTC['ema2'] = EMA2(BTC, 'close', 15)  # use function for calculate ema metod 2


# use ta lib for calculate ema
BTC['emata'] = np.round(ta.ema(BTC.close, 15), 2)


BTC.loc[BTC['emata'] == BTC['ema2'], 'equal'] = 'true'  # test for equal

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
                         y=BTC['ema1'],
                         opacity=0.7,
                         line=dict(color='black', width=2),
                         name='ema'))


# colors = ['green' if row['open'] - row['close'] >= 0
#           else 'red' for index, row in BTC.iterrows()]
# fig.add_trace(go.Bar(x=BTC.index,
#                      y=BTC['volume'],
#                      marker_color=colors
#                      ), row=2, col=1)

fig.show()
# }
