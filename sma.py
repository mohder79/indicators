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
#pd.set_option('display.max_rows', None)
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
    df = df.set_index(pd.DatetimeIndex(df.timestamp))
    return df
# }


# { set the symbol for data function
BTC = fetch('BTC/USDT:USDT', '1h', 200)
# }

# { function for calculate sma


def SMA(data: str, length: int, column: str):
    return data[column].rolling(window=length).mean()
# }


BTC['sma'] = SMA(BTC, 30, 'close')  # use function for  calculate sma

BTC['ta sma'] = ta.sma(BTC.close, 30)  # use pandas ta lib for calculate sma

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
                         y=BTC['sma'],
                         opacity=0.7,
                         line=dict(color='LightSkyBlue', width=2),
                         name='sma'))


# colors = ['green' if row['open'] - row['close'] >= 0
#           else 'red' for index, row in BTC.iterrows()]
# fig.add_trace(go.Bar(x=BTC.index,
#                      y=BTC['volume'],
#                      marker_color=colors
#                      ), row=2, col=1)

fig.show()
# }
