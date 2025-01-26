import talib

from datafeed.expr_utils import calc_by_symbol


@calc_by_symbol
def ta_dema(X, d):
    X.ffill(inplace=True)
    y = talib.DEMA(X, d)
    return y


@calc_by_symbol
def ta_kama(X, d):
    X.ffill(inplace=True)
    y = talib.KAMA(X, d)
    return y


@calc_by_symbol
def ta_ema(X, d):
    X.ffill(inplace=True)
    y = talib.EMA(X, d)
    return y


@calc_by_symbol
def ta_linearreg_angle(X, d):
    X.ffill(inplace=True)
    y = talib.LINEARREG_ANGLE(X, d)
    return y


@calc_by_symbol
def ta_linearreg_slope(X, d):
    X.ffill(inplace=True)
    y = talib.LINEARREG_SLOPE(X, d)
    return y


@calc_by_symbol
def ta_linearreg_intercept(X, d):
    X.ffill(inplace=True)
    y = talib.LINEARREG_INTERCEPT(X, d)
    return y


@calc_by_symbol
def ta_midpoint(X, d):
    X.ffill(inplace=True)
    y = talib.MIDPOINT(X, d)
    return y

