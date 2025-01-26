import pandas as pd

from datafeed.expr_functions import calc_by_symbol


@calc_by_symbol
def cross_up(left, right):
    left = pd.Series(left)
    right = pd.Series(right)
    diff = left - right
    diff_shift = diff.shift(1)
    se = (diff >= 0) & (diff_shift < 0)
    print('cross_up_se', se)
    return se


@calc_by_symbol
def cross_down(left, right):
    left = pd.Series(left)
    right = pd.Series(right)
    diff = left - right
    diff_shift = diff.shift(1)
    return (diff <= 0) & (diff_shift > 0)
