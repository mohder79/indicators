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
pd.options.plotting.backend = "plotly"
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


# { line 31
def HILO(data: str, high: str, low: str, ATRPeriod: int = ATRPeriod):
    hi_minus_lo = data[high]-data[low]
    atr = 1.5 * hi_minus_lo.rolling(window=ATRPeriod).mean().fillna(0)
    hilo = np.zeros(np.size(data[high]))
    for i in range(0, np.size(data[high])):
        hilo[i] = min(hi_minus_lo[i], atr[i])
    return hilo
# }


# { line 33 HiLo
def HREF(data, high, low, close):
    href = np.zeros(np.size(data[high]))

    for i in range(1, np.size(data[high])):
        if data[low][i] <= data[high][i-1]:
            href[i] = data[high][i]-data[close][i-1]
        else:
            href[i] = (((data[high][i]) - (data[close][i-1])) -
                       0.5) * ((data[low][i])-(data[high][i-1]))
    return href
# }


# { line 37 LRef
def LREF(data: str, high: str, low: str, close: str):
    lref = np.zeros(np.size(data[high]))
    for i in range(1, np.size(data[high])):
        if data[high][i] >= data[low][i-1]:
            lref[i] = data[close][i-1] - data[low][i]
        else:
            lref[i] = (((data[close][i-1]) - (data[low])) - 0.5) * \
                ((data[low][i-1])-(data[high]))
    return lref
# }


# { line 41 trueRange HiLo,
def TRUERANGE(data: str, high: str, low: str, close: str, LRef: str, HRef: str, HiLo: str, trailType: str = 'modified'):
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
# }


# { line 49
def LOSS(data: str, trueRange: str, ATRPeriod: int = ATRPeriod, ATRFactor: int = ATRFactor):
    _wild = np.zeros(np.size(data['trueRange']))
    _wild[0] = 0

    for i in range(1, np.size(data['trueRange'])):
        _wild[i] = _wild[i-1] + ((data[trueRange][i] - _wild[i-1]) / ATRPeriod)
    return ATRFactor * _wild
# }


# { line 58
def TRENDUP(data: str, close: str, Up: str):
    trendup = np.empty(np.size(data[close]))
    trendup[:] = np.nan

    for i in range(1, np.size(data[close])):
        if data[close][i-1] > trendup[i-1]:
            trendup[i] = max(trendup[i-1], data[Up][i])
        else:
            trendup[i] = data[Up][i]
    return trendup
# }


# { line 59
def TRENDDOWN(data: str, close: str, Dn: str):
    trenddown = np.empty(np.size(data[close]))
    trenddown[:] = np.nan

    for i in range(1, np.size(data[close])):
        if data[close][i-1] < trenddown[i-1]:
            trenddown[i] = min(trenddown[i-1], data[Dn][i])
        else:
            trenddown[i] = data[Dn][i]
    return trenddown
# }


# { line 61
def TREND(data: str, close: str, TrendDown: str, TrendUp: str):
    trend = np.empty(np.size(data[close]))
    trend[0] = 1

    for i in range(1, np.size(data[close])):
        if data[close][i] > data[TrendDown][i-1]:
            trend[i] = 1
        elif data[close][i] < data[TrendUp][i-1]:
            trend[i] = -1
        else:
            trend[i] = trend[i-1]

    return(trend)
# }


# { line 65
def EX(data: str, Trend: str = 'Trend', high: str = 'high', low: str = 'low'):
    ex = np.empty(np.size(data[Trend]))
    ex[:] = np.nan
    for i in range(1, np.size(data[Trend])):
        if data[Trend][i] > 0 and data[Trend][i-1] < 0:
            ex[i] = data[high][i]
        elif data[Trend][i] < 0 and data[Trend][i-1] > 0:
            ex[i] = data[low][i]
        elif data[Trend][i] == 1:
            ex[i] = max(ex[i-1], data[high][i])
        elif data[Trend][i] == -1:
            ex[i] = min(ex[i-1], data[low][i])
        else:
            ex[i] = ex[i-1]
    return ex
# }


# { function to set fill colors

def fill_df1_df2(color):
    if color == 1:
        return 'rgba(0,250,0,0.2)'
    else:
        return 'rgba(250,0,0,0.2)'


def fill_df2_df3(color):
    if color == 1:
        return 'rgba(0,250,0,0.5)'
    else:
        return 'rgba(250,0,0,0.5)'


def fill_df3_l100(color):
    if color == 1:
        return 'rgba(0,250,0,0.7)'
    else:
        return 'rgba(250,0,0,0.7)'


def ex_color(color):
    if color == 1:
        return 'rgb(0, 255, 153)'
    else:
        return 'rgb(255, 0, 102)'
