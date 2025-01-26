
from deap import gp
from alpha.deap_patch import *  # noqa

def dummy(*args):
    # 由于生成后的表达计算已经被map和evaluate接管，所以这里并没有用到，可随便定义
    return 1


class RET_TYPE:
    # 是什么不重要
    # 只要addPrimitive中in_types, ret_type 与 PrimitiveSetTyped("MAIN", [], ret_type)中
    # 这三种type对应即可
    pass


EXPR = RET_TYPE


def add_operators_base(pset):
    """基础算子"""
    # 无法给一个算子定义多种类型，只好定义多个不同名算子，之后通过helper.py中的convert_inverse_prim修正
    pset.addPrimitive(dummy, [EXPR, EXPR], EXPR, name='fadd')
    pset.addPrimitive(dummy, [EXPR, EXPR], EXPR, name='fsub')
    pset.addPrimitive(dummy, [EXPR, EXPR], EXPR, name='fmul')
    pset.addPrimitive(dummy, [EXPR, EXPR], EXPR, name='fdiv')

    pset.addPrimitive(dummy, [EXPR, int], EXPR, name='iadd')
    pset.addPrimitive(dummy, [EXPR, int], EXPR, name='isub')
    pset.addPrimitive(dummy, [EXPR, int], EXPR, name='imul')
    pset.addPrimitive(dummy, [EXPR, int], EXPR, name='idiv')
    return pset


def add_unary_ops(pset):
    from datafeed.expr_functions import unary_funcs
    for func in unary_funcs:
        pset.addPrimitive(dummy, [EXPR], EXPR, name=func)


def _random_int_():
    import random
    return random.choice([1, 5, 10, 20, 40, 60, 120])

def add_unary_ops(pset):
    from datafeed import unary_funcs
    for func in unary_funcs:
        pset.addPrimitive(dummy, [EXPR], EXPR, name=func)


def add_unary_rolling_ops(pset):
    from datafeed import ts_rolling_funcs
    for func in ts_rolling_funcs:
        pset.addPrimitive(dummy, [EXPR, int], EXPR, name=func)

    #from datafeed import ts_rolling_talib_funcs
    #for func in ts_rolling_talib_funcs:
    #    pset.addPrimitive(dummy, [EXPR, int], EXPR, name=func)

def add_binary_ops(pset):
    from datafeed.expr_functions import binary_funcs
    for func in binary_funcs:
        pset.addPrimitive(dummy, [EXPR, EXPR], EXPR, name=func)


def add_binary_rolling_ops(pset):
    from datafeed.expr_functions import binary_roilling_funcs
    for func in binary_roilling_funcs:
        pset.addPrimitive(dummy, [EXPR, EXPR, int], EXPR, name=func)


def add_period_ops(pset):
    from datafeed.expr_functions import only_period_funs
    for func in only_period_funs:
        pset.addPrimitive(dummy, [int], EXPR, name=func)



def get_pset():
    pset = gp.PrimitiveSetTyped("MAIN", [], EXPR)
    pset = add_operators_base(pset)
    add_unary_ops(pset)
    add_unary_rolling_ops(pset)
    #add_period_ops(pset)
    #add_binary_ops(pset)
    #add_binary_rolling_ops(pset)


    pset.addEphemeralConstant('_random_int_', _random_int_, int)

    pset.addTerminal(1, EXPR, name='open')
    pset.addTerminal(1, EXPR, name='high')
    pset.addTerminal(1, EXPR, name='low')
    pset.addTerminal(1, EXPR, name='close')
    pset.addTerminal(1, EXPR, name='volume')

    return pset
