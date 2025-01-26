import pandas as pd

from datafeed.expr_utils import calc_by_symbol


@calc_by_symbol
def ts_corr(left: pd.Series, right: pd.Series, periods=20):
    res = left.rolling(window=periods).corr(right)
    # left.rolling(window=periods).apply(func=func,right)
    res.loc[
        np.isclose(left.rolling(periods, min_periods=1).std(), 0, atol=2e-05)
        | np.isclose(right.rolling(periods, min_periods=1).std(), 0, atol=2e-05)
        ] = np.nan
    return res


@calc_by_symbol
def ts_cov(left: pd.Series, right: pd.Series, periods=10):
    res = left.rolling(window=periods).cov(right)
    return res


# @calc_by_symbol
# def ts_beta(x, y, d):
#     x.ffill(inplace=True)
#     y.ffill(inplace=True)
#     z = talib.BETA(x, y, d)
#     return z


import numpy as np

#from numpy.lib.stride_tricks import as_strided as strided


# def rolling_window(a: np.array, window: int):
#     '生成滚动窗口，以三维数组的形式展示'
#     shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
#     strides = a.strides + (a.strides[-1],)
#     return strided(a, shape=shape, strides=strides)


# def numpy_rolling_regress(x1, y1, window: int = 18, array: bool = False):
#     """在滚动窗口内进行，每个矩阵对应进行回归"""
#     x_series = np.array(x1)
#     y_series = np.array(y1)
#     # 创建一个一维数组
#     dd = x_series
#     x = rolling_window(dd, window)
#     yT = rolling_window(y_series, window)
#     y = np.array([i.reshape(window, 1) for i in yT])
#     ones_vector = np.ones((1, x.shape[1]))
#     XT = np.stack([np.vstack([ones_vector, row]) for row in x])  # 加入常数项
#     X = np.array([matrix.T for matrix in XT])  # 以行数组表示
#     reg_result = np.linalg.pinv(XT @ X) @ XT @ y  # 线性回归公示
#
#     if array:
#         return reg_result
#     else:
#         frame = pd.DataFrame()
#         result_const = np.zeros(x_series.shape[0])
#         const = reg_result.reshape(-1, 2)[:, 0]
#         result_const[-const.shape[0]:] = const
#         frame['const'] = result_const
#         frame.index = x1.index
#         for i in range(1, reg_result.shape[1]):
#             result = np.zeros(x_series.shape[0])
#             beta = reg_result.reshape(-1, 2)[:, i]
#             result[-beta.shape[0]:] = beta
#             frame[f'factor{i}'] = result
#         return frame


# @calc_by_symbol
# def RSRS(high: pd.Series, low: pd.Series, N: int = 18):
#     beta_series = numpy_rolling_regress(low, high, window=N, array=True)
#     beta = beta_series.reshape(-1, 2)[:, 1]
#     len_to_pad = len(low.index) - len(beta)
#     pad = [np.nan for i in range(len_to_pad)]
#     pad.extend(beta)
#     beta = pd.Series(pad, index=low.index)
#     return beta


# @calc_by_symbol
# def RSRS_zscore(high: pd.Series, low: pd.Series, N: int = 18, M: int = 600):
#     beta_series = numpy_rolling_regress(low, high, window=N, array=True)
#     beta = beta_series.reshape(-1, 2)[:, 1]
#
#     beta_rollwindow = rolling_window(beta, M)
#     beta_mean = np.mean(beta_rollwindow, axis=1)
#     beta_std = np.std(beta_rollwindow, axis=1)
#     zscore = (beta[M - 1:] - beta_mean) / beta_std
#     len_to_pad = len(low.index) - len(zscore)
#     # print(len_to_pad)
#     pad = [np.nan for i in range(len_to_pad)]
#     pad.extend(zscore)
#     zscore = pd.Series(pad, index=low.index)
#     return zscore
