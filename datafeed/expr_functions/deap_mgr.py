import copy
import re
from random import random

import numpy as np
import pandas as pd
from loguru import logger
from deap import base, creator, gp, tools
from alpha.add_ops import *
from alpha.deap_patch import *  # noqa
from datafeed.dataloader import CSVDataloader


def calc_ic(x, y):
    """个体fitness函数"""
    ic = pd.Series(x.corr(y, method='spearman'))
    return ic


def convert_inverse_prim(prim, args):
    """
    Convert inverse prims according to:
    [Dd]iv(a,b) -> Mul[a, 1/b]
    [Ss]ub(a,b) -> Add[a, -b]
    We achieve this by overwriting the corresponding format method of the sub and div prim.
    """
    prim = copy.copy(prim)

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


class DeapMgr:
    def __init__(self, symbols, init_n=10, mode='multi_symbols', label_expr='shift(close,-5)/close -1',
                 split_date='20230101'):
        self._init_data(symbols)
        self.label_expr = label_expr
        self.split_date = split_date
        self.init_n = init_n
        self.mode = mode

        logger.info('开始Deap因子挖掘...')
        random.seed(88)
        creator = self._init_creator()
        self._init_toolbox(creator)

    def _init_data(self, symbols):
        self.df = CSVDataloader.get_df(symbols, set_index=True)

    def _init_creator(self):
        # 可支持多目标优化
        # TODO 必须元组，1表示找最大值,-1表示找最小值
        FITNESS_WEIGHTS = (1.0, 1.0)
        creator.create("FitnessMulti", base.Fitness, weights=FITNESS_WEIGHTS)
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMulti)
        return creator

    def _init_pset(self):
        pset = gp.PrimitiveSetTyped("MAIN", [], RET_TYPE)
        pset = add_constants(pset)
        pset = add_operators(pset)
        pset = add_factors(pset)
        return pset

    def _init_toolbox(self, creator):
        toolbox = base.Toolbox()
        pset = self._init_pset()
        toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=2, max_=5)
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", print)  # 、，在map中一并做了

        toolbox.register("select", tools.selTournament, tournsize=3)  # 目标优化
        # toolbox.register("select", tools.selNSGA2)  # 多目标优化 FITNESS_WEIGHTS = (1.0, 1.0)
        toolbox.register("mate", gp.cxOnePoint)
        toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
        toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

        import operator
        toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
        toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

        from datetime import datetime
        dt1 = datetime(2021, 1, 1)
        LABEL_y = 'y_predict'
        from itertools import count

        # 这里注册优化函数
        # toolbox.register('map', self.map_exprs, gen=count(), label=LABEL_y, split_date=dt1)

        if self.mode == 'multi_symbols':
            toolbox.register('map', self.backtester)
        elif self.mode == 'pick_time':
            toolbox.register('map', self.picktime_backtester)
        self.toolbox = toolbox

    def picktime_backtester(self, evaluate, inds):
        print('开始择时回测')
        df, names = self._calc_df(inds)
        results = []
        # 向量化回测
        # 计算每日收益
        for name in names:
            if name in df.columns:

                daily_returns = df['close'].pct_change()

                # 根据信号计算策略收益]
                signal = df[name]
                signal_80 = df[name].rolling(window=1000).apply(lambda x: np.percentile(x, 80))
                signal_20 = df[name].rolling(window=1000).apply(lambda x: np.percentile(x, 20))
                signal = np.where(signal > signal_80, 1, np.nan)
                signal = np.where(signal < signal_20, -1, signal)
                signal = pd.Series(signal, index=df.index)
                signal = signal.ffill()  # 这一步很关键在1后面的会前向填充，即持仓不变。
                signal = signal.fillna(0)

                strategy_returns = signal * daily_returns.shift(1)

                # 计算累积收益
                portfolio_value = (1 + strategy_returns).cumprod()

                # 计算投资组合的平均回报率
                mean_return = np.mean(strategy_returns)

                # 计算投资组合回报率的标准差
                std_dev = np.std(strategy_returns)

                # 计算夏普比率
                sharpe_ratio = (mean_return - 0) / std_dev
                results.append((portfolio_value[-1], sharpe_ratio))
            else:
                results.append((0, 0))
        print(results)
        return results

    def _calc_df(self, inds):
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
        df = CSVDataloader.calc_expr(self.df.copy(deep=True), fields=features, names=names)
        # df.set_index([df['symbol'], df.index], inplace=True)
        return df, names

    def backtester(self, evaluate, inds):

        df, names = self._calc_df(inds)
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
        print(stats.loc['cagr'])

        results = []
        for name in names:
            if name not in df.columns:
                results.append((0, 0))
            else:
                results.append((stats.loc['cagr'][name], stats.loc['calmar'][name]))
        return results

    def map_exprs(self, evaluate, invalid_ind, gen, label, split_date):
        names, features = [], []
        for i, expr in enumerate(invalid_ind):
            names.append(f'GP_{i:04d}')
            features.append(stringify_for_sympy(expr))

        features = []
        for f in features:

            if 'ta_aroonosc' in f:
                pattern = r'ta_aroonosc\((\d+)\)'
                # 替换函数，将匹配的数字替换为high,low,数字
                replacement = r'ta_aroonosc(high,low,\1)'
                # 执行替换
                new_string = re.sub(pattern, replacement, f)

                features.append(new_string)
            else:
                features.append(f)
        # features = [f.lower() for f in features]

        all_names = names.copy()
        all_names.append(label)
        all_features = features.copy()
        all_features.append(self.label_expr)

        df = CSVDataloader.calc_expr(self.df.copy(deep=True), fields=all_features, names=all_names)
        df.set_index([df['symbol'], df.index], inplace=True)

        # 将IC划分成训练集与测试集
        df_train = df[df.index.get_level_values(1) < split_date]
        df_valid = df[df.index.get_level_values(1) >= split_date]

        valid_names = []
        for name in names:
            if name in df.columns:
                valid_names.append(name)

        ic_train = df_train[valid_names].groupby(level=0, group_keys=False).agg(
            lambda x: calc_ic(x, df_train[label])).mean()
        ic_valid = df_valid[valid_names].groupby(level=0, group_keys=False).agg(
            lambda x: calc_ic(x, df_valid[label])).mean()
        # print('ic_train', ic_train)
        # print('ic_valid', ic_valid)

        results = {}
        for name, factor in zip(names, features):
            if name not in valid_names:
                results[factor] = {'ic_train': 0,
                                   'ic_valid': 0,
                                   }
                continue
            results[factor] = {'ic_train': ic_train.loc[name],
                               'ic_valid': ic_valid.loc[name],
                               }
            # print(results)
        print(results)
        return [(v['ic_train'], v['ic_valid']) for v in results.values()]

    def start(self):
        n = self.init_n
        pop = self.toolbox.population(n=n)
        logger.info('完成初代种群初始化：{}个'.format(n))
        hof = tools.HallOfFame(10)

        # 只统计一个指标更清晰
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        # 打补丁后，名人堂可以用nan了，如果全nan会报警
        stats.register("avg", np.nanmean, axis=0)
        stats.register("std", np.nanstd, axis=0)
        stats.register("min", np.nanmin, axis=0)
        stats.register("max", np.nanmax, axis=0)

        # 使用修改版的eaMuPlusLambda
        population, logbook = eaMuPlusLambda(pop, self.toolbox,
                                             # 选多少个做为下一代，每次生成多少新个体
                                             mu=150, lambda_=100,
                                             # 交叉率、变异率，代数
                                             cxpb=0.5, mutpb=0.1, ngen=2,
                                             # 名人堂参数
                                             # alpha=0.05, beta=10, gamma=0.25, rho=0.9,
                                             stats=stats, halloffame=hof, verbose=True,
                                             # 早停
                                             early_stopping_rounds=5)

        print('=' * 60)
        print(logbook)

        print('=' * 60)

        def print_population(population):
            for p in population:
                expr = stringify_for_sympy(p)
                print(expr, p.fitness)

        print_population(hof)


if __name__ == '__main__':
    import warnings

    warnings.filterwarnings('ignore', category=RuntimeWarning)
    # DeapMgr(symbols=CSVDataloader.get_symbols_from_instruments('全球大类资产.txt')).start()
    DeapMgr(symbols=['TA888_minutes'], mode='pick_time', init_n=10).start()
