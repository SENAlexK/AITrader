import pandas as pd

from datafeed import *


def expr_transform(df, expr):
    # close/shift(close,5) -1
    for col in df.columns:
        if col == 'pe' or 'col' == 'pb':
            continue
        expr = expr.replace(col, 'df["{}"]'.format(col))
    return expr


def calc_expr(df: pd.DataFrame, expr: str):  # correlation(rank(open),rank(volume))
    # 列若存在，就直接返回
    if expr in list(df.columns):
        return df[expr]
    print(expr)
    expr = expr_transform(df, expr)
    se = eval(expr)
    return se
    # try:
    #
    # except:
    #     import traceback
    #     traceback.print_exc()
    # raise NameError('{}——eval异常'.format(expr))
    # shift(close,1) -> shift(df['close'],1)
    return None
