from datafeed.dataloader import CSVDataloader
import copy,re

symbols = [
    '159934.SZ',  # 黄金ETF（黄金）
    # '511260.SH',  # 十年国债ETF（债券）
    '161716.SZ',
    '512890.SH',  # 红利低波（股票）
    '159985.SZ',  # 豆粕（商品）
    '513100.SH'  # 纳指100
]
df = CSVDataloader.get_df(symbols, set_index=True)


def convert_inverse_prim(prim, args):
    """
    Convert inverse prims according to:
    [Dd]iv(a,b) -> Mul[a, 1/b]
    [Ss]ub(a,b) -> Add[a, -b]
    We achieve this by overwriting the corresponding format method of the sub and div prim.
    """
    prim = copy.copy(prim)
    df = CSVDataloader.get_df(symbols, set_index=True)

    converter = {
        'Add': lambda *args_: "{}+{}".format(*args_),
        'Mul': lambda *args_: "{}*{}".format(*args_),
        'fsub': lambda *args_: "{}-{}".format(*args_),
        'fdiv': lambda *args_: "{}/{}".format(*args_),
        'fmul': lambda *args_: "{}*{}".format(*args_),
        'fadd': lambda *args_: "{}+{}".format(*args_),
        # 'fmax': lambda *args_: "max_({},{})".format(*args_),
        # 'fmin': lambda *args_: "min_({},{})".format(*args_),

        'isub': lambda *args_: "{}-{}".format(*args_),
        'idiv': lambda *args_: "{}/{}".format(*args_),
        'imul': lambda *args_: "{}*{}".format(*args_),
        'iadd': lambda *args_: "{}+{}".format(*args_),
        # 'imax': lambda *args_: "max_({},{})".format(*args_),
        # 'imin': lambda *args_: "min_({},{})".format(*args_),
    }

    prim_formatter = converter.get(prim.name, prim.format)

    return prim_formatter(*args)

def stringify_for_sympy(f):
    """Return the expression in a human readable string.
    """
    string = ""
    stack = []
    for node in f:
        stack.append((node, []))
        while len(stack[-1][1]) == stack[-1][0].arity:
            prim, args = stack.pop()
            string = convert_inverse_prim(prim, args)
            if len(stack) == 0:
                break  # If stack is empty, all nodes should have been seen
            stack[-1][1].append(string)
    # print(string)
    return string



def _calc_df(inds):
    df = CSVDataloader.get_df(symbols, set_index=True)

    names, features = [], []
    for i, expr in enumerate(inds):
        names.append(f'GP_{i:04d}')
        features.append(stringify_for_sympy(expr))

    new_features = []
    replace = {
        r'ta_ADX\((\d+)\)': r'ta_ADX(high,low,close,\1)',
        r'ta_aroonosc\((\d+)\)': r'ta_aroonosc(high,low,\1)',

    }
    for f in features:
        new_string = f
        for pattern, replacement in replace.items():
            new_string = re.sub(pattern, replacement, new_string)
        new_features.append(new_string)
    features = new_features
    df = CSVDataloader.calc_expr(df.copy(deep=True), fields=features, names=names)
    # df.set_index([df['symbol'], df.index], inplace=True)
    return df, names

def backtester(evaluate, inds):
    df, names = _calc_df(inds)
    import bt
    from bt_algos_extend import SelectTopK
    close = CSVDataloader.get_col_df(df, 'close')
    all = []

    for f in names:
        if f in df.columns:
            signal = CSVDataloader.get_col_df(df, f)

            for K in [1]:
                s = bt.Strategy('{}'.format(f), [
                    bt.algos.RunWeekly(),
                    SelectTopK(signal, K),
                    bt.algos.WeighEqually(),
                    bt.algos.Rebalance()])
                all.append(s)

    stras = [bt.Backtest(s, close) for s in all]
    res = bt.run(*stras)
    stats = res.stats
    #print(stats.loc['cagr'])

    results = []
    for name in names:
        if name not in df.columns:
            #results.append((0, 0))
            results.append((0,))
        else:
            results.append((stats.loc['cagr'][name],))
            #results.append((stats.loc['cagr'][name], stats.loc['calmar'][name]))
    return results