def Sub(left, right):
    return left - right


def Add(left, right):
    return left + right


def Mul(left, right):
    return left * right


def Div(left, right):
    return left / right


def list_funcs(mod):
    import inspect
    funcs = []

    name_funcs = {name: func for name, func in inspect.getmembers(mod, inspect.isfunction)}

    for name, func in name_funcs.items():
        if name[0] == '_':
            continue
        if name in ['calc_by_date', 'calc_by_symbol', 'wraps']:
            continue

        funcs.append(name)

    return funcs


from datafeed.expr_ts import *
from datafeed.expr_unary import *
from datafeed.expr_talib import *
from datafeed.expr_not_use_in_ga import *
from datafeed import expr_ts, expr_unary, expr_talib

ts_rolling_funcs = list_funcs(expr_ts)
unary_funcs = list_funcs(expr_unary)
ts_rolling_talib_funcs = list_funcs(expr_talib)