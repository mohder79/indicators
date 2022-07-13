# { import the libraries
from cProfile import label
import ccxt
from datetime import datetime
import pandas as pd
import pandas_ta as ta
import numpy as np
from matplotlib import pyplot as plt
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
    df = df.set_index(pd.DatetimeIndex(df.timestamp))
    return df
# }


# { function for calculate EMA metod 1
def EMA(data: str, src: str, length: int):
    return data[src].ewm(span=length, min_periods=length, adjust=False).mean()
# }


# { function for calculate EMA metod 2
def EMA2(data: str, src: str, Length: int, smoothing=2):
    size = np.size(data[src]) - Length + 1
    EMA = np.zeros(np.size(data[src]))
    EMA[0] = np.mean(data[src][:Length])
    print(EMA[0])
    for i in range(1, size):
        EMA[i] = (((2/(Length + 1)) * data[src][i+Length-1]) +
                  ((1-(2/(Length + 1))) * EMA[i-1]))
    return EMA
# }


# { set the symbol for data function
BTC = fetch('BTC/USDT:USDT', '1d', 200)
# }

BTC['ema1'] = EMA(BTC, 'close', 5)  # use function for calculate ema metod 1

BTC['ema2'] = EMA2(BTC, 'close', 5)  # use function for calculate ema metod 1
# shift ema data (ema calculation start length - 1)
BTC['ema2'] = BTC['ema2'].shift(4)

BTC['emata'] = ta.ema(BTC.close, 5)  # use ta lib for calculate ema

print(BTC)

# { plot the data
plt.plot(BTC.close, label='closes price')
plt.plot(BTC.ema1, label='EMA')
plt.xlabel('time')
plt.ylabel('price')
plt.legend()
plt.show()
# }
