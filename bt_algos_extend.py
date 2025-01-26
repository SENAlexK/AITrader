from dataclasses import dataclass, asdict
from typing import List, Dict

import bt
import numpy as np
import pandas as pd


class SelectTopK(bt.AlgoStack):
    def __init__(self, signal, K, dropN=0, sort_descending=True, all_or_none=False, filter_selected=True):
        super(SelectTopK, self).__init__(bt.algos.SetStat(signal),
                                         bt.algos.SelectN(K + dropN, sort_descending, all_or_none, filter_selected))
        self.dropN = dropN

    def __ceil__(self, target):
        super(SelectTopK, self).__ceil__()
        if self.dropN > 0:
            sel = target.temp["selected"]
            if self.dropN >= len(sel):
                target.temp['selected'] = []
            else:
                target.temp["selected"] = target.temp["selected"][self.dropN:]
            return True


from datafeed.dataloader import CSVDataloader
from datetime import datetime
from matplotlib import rcParams
from dataclasses import dataclass, field

rcParams['font.family'] = 'SimHei'


@dataclass
class Task:
    name: str = '策略'
    symbols: List[str] = field(default_factory=list)
    strategies: List[str] = field(default_factory=list)  # 策略组合的id
    start_date: str = '20100101'
    end_date: str = None

    benchmark: str = '510300.SH'
    select: str = 'SelectAll'

    select_buy: List[str] = field(default_factory=list)
    buy_at_least_count: int = 0
    select_sell: List[str] = field(default_factory=list)
    sell_at_least_count: int = 1

    order_by_signal: str = ''
    order_by_topK: int = 1
    order_by_dropN: int = 0
    order_by_DESC: bool = True  # 默认从大至小排序

    weight: str = 'WeighEqually'
    weight_fixed: Dict[str, int] = field(default_factory=dict)
    period: str = 'RunDaily'
    period_days: int = None


@dataclass
class StrategyConfig:
    name: str = '策略'
    desc: str = '策略描述'
    config_json: Dict[str, int] = field(default_factory=dict)
    author: str = ''


import importlib


class Engine:
    def _parse_rules(self, task: Task, df):

        def _rules(df, rules, at_least):
            if not rules or len(rules) == 0:
                return None

            all = None
            for r in rules:
                if r == '':
                    continue

                df_r = CSVDataloader.get_col_df(df, r)
                if df_r is not None:
                    df_r = df_r.astype(int)
                else:
                    print(r)
                if all is None:
                    all = df_r
                else:
                    all += df_r
            return all >= at_least

        buy_at_least_count = task.buy_at_least_count
        if buy_at_least_count <= 0:
            buy_at_least_count = len(task.select_buy)

        all_buy = _rules(df, task.select_buy, at_least=buy_at_least_count)
        all_sell = _rules(df, task.select_sell, task.sell_at_least_count)  # 卖出 求或，满足一个即卖出
        return all_buy, all_sell

    def _get_algos(self, task: Task, df):

        bt_algos = importlib.import_module('bt.algos')

        if task.period == 'RunEveryNPeriods':
            algo_period = bt.algos.RunEveryNPeriods(n=task.period_days)
        else:
            algo_period = getattr(bt_algos, task.period)()

        algo_select_where = None
        # 信号规则
        signal_buy, signal_sell = self._parse_rules(task, df)
        if signal_buy is not None or signal_sell is not None:  # 至少一个不为None
            df_close = CSVDataloader.get_col_df(df, 'close')
            if signal_buy is None:
                select_signal = np.ones(df_close.shape)
                select_signal = pd.DataFrame(select_signal, columns=df_close.columns, index=df_close.index)
            else:
                select_signal = np.where(signal_buy, 1, np.nan)
            if signal_sell is not None:
                select_signal = np.where(signal_sell, 0, select_signal)
            select_signal = pd.DataFrame(select_signal, index=df_close.index, columns=df_close.columns)
            select_signal.ffill(inplace=True)
            select_signal.fillna(0, inplace=True)
            algo_select_where = bt.algos.SelectWhere(signal=select_signal)

        # 排序因子
        algo_order_by = None
        if task.order_by_signal:
            signal_order_by = CSVDataloader.get_col_df(df, col=task.order_by_signal)
            algo_order_by = SelectTopK(signal=signal_order_by, K=task.order_by_topK, dropN=task.order_by_dropN,
                                       sort_descending=task.order_by_DESC)

        algos = []
        algos.append(algo_period)

        if algo_select_where:
            algos.append(algo_select_where)
        else:
            algos.append(bt.algos.SelectAll())

        if algo_order_by:
            algos.append(algo_order_by)

        if task.weight == 'WeighERC':
            algos.insert(0, bt.algos.RunAfterDays(days=256))
            algo_weight = getattr(bt_algos, task.weight)()
        elif task.weight == 'WeighSpecified':
            print(task.weight_fixed)
            algo_weight = bt.algos.WeighSpecified(**task.weight_fixed)
        else:
            algo_weight = getattr(bt_algos, task.weight)()

        algos.append(algo_weight)
        algos.append(bt.algos.Rebalance())

        return algos

    def run_tasks(self, tasks: list[Task]):
        bkts = []
        benchmarks = []
        for task in tasks:
            # 加载数据
            df = CSVDataloader.get_df(task.symbols, True, task.start_date, task.end_date)

            # 计算因子
            if len(task.symbols):
                fields = list(set(task.select_buy + task.select_sell + [task.order_by_signal]))
                names = fields
                if len(fields):
                    df = CSVDataloader.calc_expr(df, fields, names=names)

            s = bt.Strategy(task.name, self._get_algos(task, df))

            df_close = CSVDataloader.get_col_df(df, 'close')
            bkt = bt.Backtest(s, df_close, name=task.name)
            bkts.append(bkt)
            benchmarks.append(task.benchmark)

        for bench in list(set(benchmarks)):
            data = CSVDataloader.get([bench])
            s = bt.Strategy(bench, [bt.algos.RunOnce(),
                                    bt.algos.SelectAll(),
                                    bt.algos.WeighEqually(),
                                    bt.algos.Rebalance()])
            stra = bt.Backtest(s, data, name="基准:" + bench)
            bkts.append(stra)

        res = bt.run(*bkts)
        # res.get_transactions()
        self.res = res
        return res

    def run(self, task: Task):
        # 加载数据
        df = CSVDataloader.get_df(task.symbols, True, task.start_date, task.end_date)

        # 计算因子
        if len(task.symbols):
            fields = list(set(task.select_buy + task.select_sell + [task.order_by_signal]))
            names = fields
            if len(fields):
                df = CSVDataloader.calc_expr(df, fields, names=names)

        s = bt.Strategy('策略', self._get_algos(task, df))

        df_close = CSVDataloader.get_col_df(df, 'close')
        bkt = bt.Backtest(s, df_close, name='策略')

        bkts = [bkt]
        for bench in [task.benchmark]:
            data = CSVDataloader.get([bench])
            s = bt.Strategy(bench, [bt.algos.RunOnce(),
                                    bt.algos.SelectAll(),
                                    bt.algos.WeighEqually(),
                                    bt.algos.Rebalance()])
            stra = bt.Backtest(s, data, name='benchmark')
            bkts.append(stra)

        res = bt.run(*bkts)
        # res.get_transactions()
        self.res = res
        return res

    def get_equities(self):
        quotes = (self.res.prices.pct_change() + 1).cumprod().dropna()
        quotes['date'] = quotes.index
        # quotes['date'] = quotes['date'].apply(lambda x: x.strftime('%Y%m%d'))
        quotes.index = pd.to_datetime(quotes.index).map(lambda x: x.value)
        quotes = quotes[['策略', 'benchmark']]
        dict = quotes.to_dict(orient='series')

        results = {}
        for k, s in dict.items():
            result = list(zip(s.index, s.values))
            results[k] = result
        print(results)


import requests, json




if __name__ == '__main__':
    t = Task()
    t.name = '全球大类资产-等权重-月度再平衡'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（黄金）
        # '511260.SH',  # 十年国债ETF（债券）
        '512890.SH',
        '512890.SH',  # 红利低波（股票）
        '159985.SZ',  # 豆粕（商品）
        '513100.SH'  # 纳指100
    ]
    t.period = 'RunMonthly'

    # config = StrategyConfig(name=t.name, desc='股票、债券、商品，黄金全球大类资产-等权重-月度再平衡，这是一个基准策略', config_json=asdict(t))
    # config.author = '678e02e71db30668ad7221e5'
    # put_task(config, task_id='678f5151ae544c859c97e06d')
    e = Engine()
    res = e.run(t)
    print(res.get_security_weights().iloc[-1].to_dict())
    print(res.get_weights())
    # import matplotlib.pyplot as plt
    # res.plot()
    # plt.show()
