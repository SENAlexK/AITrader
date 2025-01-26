import numpy as np

from datafeed.expr_utils import *


@calc_by_symbol
def abs(se):
    return np.abs(se)


@calc_by_symbol
def sqrt(se):
    return np.sqrt(se)


@calc_by_symbol
def log(se: pd.Series):
    return np.log(se)


@calc_by_symbol
def inv(x: pd.Series):
    with np.errstate(divide="ignore", invalid="ignore"):
        se = np.where(np.abs(x) > 0.001, 1.0 / x, 0.0)
        return pd.Series(se, index=x.index)

#from statsmodels.tsa.statespace.kalman_filter import KalmanFilter



