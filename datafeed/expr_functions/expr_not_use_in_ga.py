# 在因子表达式里用，但GA里暂时不用的算子函数
import numpy as np
import pandas as pd
import talib

from datafeed.expr_functions import calc_by_symbol


@calc_by_symbol
def sign(se: pd.Series):
    return np.sign(se)


# @calc_by_symbol
# def signed_power(se: pd.Series, a):
#    return np.where(se < 0, -np.abs(se) ** a, np.abs(se) ** a)

def scale(x, a=1):
    """
    Scales the array x such that the sum of the absolute values equals a.

    Parameters:
    x (array-like): The input array to be scaled.
    a (float, optional): The target sum of absolute values. Default is 1.

    Returns:
    numpy.ndarray: The scaled array.
    """
    import numpy as np
    x = np.array(x)  # 确保输入是numpy数组
    sum_abs_x = np.sum(np.abs(x))  # 计算x的绝对值之和
    if sum_abs_x == 0:
        raise ValueError("The sum of absolute values of x is zero, cannot scale by a non-zero value.")
    scale_factor = a / sum_abs_x  # 计算缩放因子
    return x * scale_factor  # 应用缩放因子


@calc_by_symbol
def slope_pair(se_left, se_right, N=18):
    slopes = []
    R2 = []
    # 计算斜率值
    for i in range(len(se_left)):
        if i < (N - 1):
            slopes.append(np.nan)
            R2.append(np.nan)
        else:
            x = se_right[i - N + 1:i + 1]
            y = se_left[i - N + 1:i + 1]
            slope, intercept = np.polyfit(x, y, 1)

            # lr = LinearRegression().fit(np.array(x).reshape(-1, 1), y)
            ## y_pred = lr.predict(x.reshape(-1, 1))
            # beta = lr.coef_[0]
            # r2 = r2_score(y, y_pred)
            if slope is np.nan:
                print(slope)
            slopes.append(slope)
            # R2.append(r2)
    slopes = pd.Series(slopes)
    slopes.index = se_left.index
    return slopes


def decay_linear(series, window):
    """
    对输入的时间序列进行线性衰减。

    :param series: 输入的时间序列。
    :param window: 衰减的窗口大小。
    :return: 衰减后的序列。
    """
    weights = np.arange(1, window + 1)
    decay = np.convolve(series, weights, 'valid') / np.sum(weights)
    return decay


@calc_by_symbol
def zscore(se: pd.Series, N):
    def _zscore(x):

        try:
            x.dropna(inplace=True)
            # print('sub', x)
            value = (x[-1] - x.mean()) / x.std()
            if value:
                return value
        except:
            return -1

    # print(se)
    ret = se.rolling(window=N).apply(lambda x: _zscore(x))
    return ret


@calc_by_symbol
def shift(se: pd.Series, N):
    return se.shift(N)


@calc_by_symbol
def roc(se: pd.Series, N):
    return se / shift(se, N) - 1


def _obv(close, volume):
    return talib.OBV(close, volume)


def ta_obv(close, volume):
    close.name = 'close'
    volume.name = 'volume'
    df = pd.concat([close, volume], axis=1)
    se = df.groupby('symbol', group_keys=False).apply(lambda sub_df: _obv(sub_df['close'], sub_df['volume']))
    if type(se) is pd.DataFrame:
        se = se.T
        se = se[se.columns[0]]
    return se
