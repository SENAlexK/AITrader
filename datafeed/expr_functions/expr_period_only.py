import math

import numpy as np
#from ta.volatility import BollingerBands
import talib

from datafeed.expr_utils import *


@calc_by_symbol
def ta_aroonosc(high, low, d):
    high.ffill(inplace=True)
    low.ffill(inplace=True)

    ret = talib.AROONOSC(high, low, d)
    return ret


@calc_by_symbol
def ta_ADX(high, low, close, d):
    high.ffill(inplace=True)
    low.ffill(inplace=True)
    close.ffill(inplace=True)
    ret = talib.ADX(high, low, close, d)
    return ret


@calc_by_symbol
def ta_atr(high, low, close, period=14):
    se = talib.ATR(high, low, close, period)
    # se = se / close.mean()
    se = pd.Series(se)
    se.index = high.index
    return se


