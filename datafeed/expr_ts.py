import pandas as pd

from datafeed.expr_utils import calc_by_symbol


@calc_by_symbol
def ts_delay(se: pd.Series, periods=5):  # 滞后N天的序列
    return se.shift(periods=periods)


@calc_by_symbol
def ts_delta(se: pd.Series, periods=20):  # 当前序列与滞后N天之差
    se_result = se - se.shift(periods=periods)
    return se_result


@calc_by_symbol
def ts_mean(se: pd.Series, d):
    return se.rolling(window=d).mean()


@calc_by_symbol
def ts_median(se: pd.Series, d):
    return se.rolling(window=d).median()


@calc_by_symbol
def ts_pct_change(se: pd.Series, N):
    return se / se.shift(N) - 1

@calc_by_symbol
def roc(se: pd.Series, N):
    return se / se.shift(N) - 1


@calc_by_symbol
def ts_max(se: pd.Series, periods=5):
    return se.rolling(window=periods).max()


@calc_by_symbol
def ts_min(se: pd.Series, periods=5):
    return se.rolling(window=periods).min()


@calc_by_symbol
def ts_maxmin(X, d):
    return (X - ts_min(X, d)) / (ts_max(X, d) - ts_min(X, d))


@calc_by_symbol
def ts_sum(se: pd.Series, N):
    ret = se.rolling(N).sum()
    return ret


@calc_by_symbol
def ts_std(se, periods=5):
    return se.rolling(window=periods).std()


@calc_by_symbol
def ts_skew(X, d):
    return X.rolling(window=d).skew()


@calc_by_symbol
def ts_kurt(X, d):
    return X.rolling(window=d).kurt()


#
@calc_by_symbol
def ts_argmin(se: pd.Series, periods=5):
    return se.rolling(periods, min_periods=1).apply(lambda x: x.argmin())


@calc_by_symbol
def ts_argmax(se: pd.Series, periods=5):
    return se.rolling(periods, min_periods=1).apply(lambda x: x.argmax())


@calc_by_symbol
def ts_argmaxmin(X, d):
    return ts_argmax(X, d) - ts_argmin(X, d)


@calc_by_symbol
def ts_rank(se: pd.Series, periods=9):
    ret = se.rolling(window=periods).rank(pct=True)
    return ret


# @calc_by_symbol
# def ts_product(se: pd.Series, d):
#     return se.rolling(window=d).apply(np.product)
#
#

@calc_by_symbol
def ma(X, d):
    X.ffill(inplace=True)
    y = X.rolling(window=d).mean()
    return y



