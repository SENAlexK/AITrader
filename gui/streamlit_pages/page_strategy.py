from dataclasses import dataclass, field, asdict
import importlib

import bt
import numpy as np
import pandas as pd
import requests

from bt_algos_extend import SelectTopK
import streamlit as st

from datafeed.dataloader import CSVDataloader
from .blocks import select_symbols
# from streamlit_tree_select import tree_select



def rule_to_signal(df_all: pd.DataFrame, rule: str):
    # roc_20>0.08 and rsi>80
    rule = 'result =  {}'.format(rule)
    try:
        df_all.eval(rule, inplace=True)
        signal = CSVDataloader.get_col_df(df_all, 'result')
        return signal
    except:
        print('解析规则：{}出错'.format(rule))
        return None


@dataclass
class Task:
    symbols: list = field(default_factory=list)
    features: list = field(default_factory=list)
    feature_names: list = field(default_factory=list)
    period: str = None
    weight: str = None
    order_by: str = None
    topK: int = 3
    sort_descending: bool = True
    buy_rules: str = None
    sell_rules: str = None

    def get_bt_algo(self, algo_name):
        module = importlib.import_module('bt.algos')
        algo = getattr(module, algo_name)()
        return algo

    def get_algos(self):
        algos = []
        algos.append(self.get_bt_algo(self.period))
        algos.append(bt.algos.SelectAll())

        if self.buy_rules or self.sell_rules:  # 至少有一条规则
            if self.buy_rules and self.sell_rules:
                signal_buy = rule_to_signal(self.df_all, self.buy_rules)
                signal_sell = rule_to_signal(self.df_all, self.sell_rules)
                signal = np.where(signal_buy, 1, np.nan)
                signal = np.where(signal_sell, 0, signal)
                signal = pd.DataFrame(signal, index=signal_buy.index, columns=signal_buy.columns)
            elif self.buy_rules:
                signal_buy = rule_to_signal(self.df_all, self.buy_rules)
                signal = np.where(signal_buy, 1, np.nan)
                signal = pd.DataFrame(signal, index=signal_buy.index, columns=signal_buy.columns)
            elif self.sell_rules:
                signal_sell = rule_to_signal(self.df_all, self.sell_rules)
                signal = np.where(signal_sell, 0, 1)
                signal = pd.DataFrame(signal, index=signal_sell.index, columns=signal_sell.columns)

            # signal = np.where(df_roc > 0.08, 1, np.nan)
            # signal = np.where(df_roc < 0, 0, signal)
            # signal = pd.DataFrame(signal, index=df_roc.index, columns=df_roc.columns)
            signal = signal.ffill()
            signal = signal.fillna(0)
            algos.append(bt.algos.SelectWhere(signal))

        if self.order_by:
            algos.append(
                SelectTopK(signal=self.get_signal(self.order_by), K=self.topK, sort_descending=self.sort_descending))

        algos.append(self.get_bt_algo(self.weight))
        algos.append(bt.algos.Rebalance())
        return algos

    def calc_data(self):
        df_all = CSVDataloader.get_df(self.symbols, set_index=True)
        self.df_all = CSVDataloader.calc_expr(df_all, self.features, self.feature_names)
        self.df_close = CSVDataloader.get_col_df(df_all, 'close')
        self.df_close.fillna(method='ffill', inplace=True)

    def get_signal(self, col):
        if col not in list(self.df_all.columns):
            print('{}不存在'.format(col))
            return None
        return CSVDataloader.get_col_df(self.df_all, col)


def weight_config():
    text_2_weight = {'WeighEqually': '等权', 'WeighERC': '风险平价'}

    def _format(x):
        return text_2_weight[x]

    weight = st.selectbox('权重方案', options=list(text_2_weight.keys()), format_func=lambda x: _format(x))
    return weight


def period_config():
    periods = {'RunDaily': '每天运行', 'RunWeekly': '每周运行', 'RunMonthly': '每月运行', 'RunQuarterly': '每季度运行',
               'RunYealy': '每年运行',
               'RunOnce': '运行一次'}

    def _format(x):
        return periods[x]

    period = st.selectbox(label='调仓周期', index=0, options=list(periods.keys()),
                          format_func=lambda x: _format(x))
    return period


# 因子列表
def factor_config():
    # Create nodes to display
    nodes = [
        {"label": "价量指标", "value": "tech"},
        {
            "label": "Folder B",
            "value": "folder_b",
            "children": [
                {"label": "Sub-folder A", "value": "sub_a"},
                {"label": "Sub-folder B", "value": "sub_b"},
                {"label": "Sub-folder C", "value": "sub_c"},
            ],
        },
        {
            "label": "基本面指标",
            "value": "fundmental",
            "children": [
                {"label": "动量", "value": "mom"},
                {
                    "label": "Sub-folder E",
                    "value": "sub_e",
                    "children": [
                        {"label": "Sub-sub-folder A", "value": "sub_sub_a"},
                        {"label": "Sub-sub-folder B", "value": "sub_sub_b"},
                    ],
                },
                {"label": "Sub-folder F", "value": "sub_f"},
            ],
        },
    ]

    # return_select = tree_select(nodes)
    # st.write(return_select)

    url = "http://bbs.ailabx.com/forum.php?mod=viewthread&tid=29&extra="
    st.write("因子表达式帮助[地址](%s)" % url)

    col1, col2 = st.columns(2)
    with col1:
        features_str = st.text_area('输入因子表达式，一行一个', value='roc(close,20)')
    with col2:
        feature_names_str = st.text_area('输入因子名称， 一行一个', value='roc_20')

    features = features_str.split('\n')
    names = feature_names_str.split('\n')
    if len(features) != len(names):
        st.write('因子表达式与名字数量不一致，请检查')

    return features, names


def order_by_config(task: Task):
    col1, col2 = st.columns(2)
    directions = {True: '从大到小', False: '从小至大'}
    with col1:
        topK = st.number_input('topK', 1, len(task.symbols))
        order_by = st.selectbox('请选择排序因子', options=task.feature_names)
    with col2:
        def _format(x):
            return directions[x]

        direction = st.selectbox('排序方向', options=list(directions.keys()), format_func=lambda x: _format(x))
    return order_by, direction, topK


def signal_config():
    col1, col2 = st.columns(2)
    with col1:
        buy_str = st.text_input('入场信号，可以复合 比如 roc_20>0.08 and rsi>80', value='roc_20>0.08')
    with col2:
        sell_str = st.text_input('出场信号', value='roc_20<0')
    return buy_str, sell_str


def run_task(task: Task):
    import bt

    task.calc_data()
    s = bt.Strategy('策略', task.get_algos())

    s = bt.Backtest(s, data=task.df_close)
    stras = [s]

    for bench in ['000300.SH']:
        data = CSVDataloader.get([bench])
        s = bt.Strategy(bench, [bt.algos.RunOnce(),
                                bt.algos.SelectAll(),
                                bt.algos.WeighEqually(),
                                bt.algos.Rebalance()])
        stra = bt.Backtest(s, data,name='benchmark')
        stras.append(stra)
    res = bt.run(*stras)
    dict_data = res.stats.to_dict(orient='index')
    performance = {
        'cagr': dict_data['cagr']['策略'],
        'cagr_benchmark': dict_data['cagr']['benchmark'],
        'max_drawdown': dict_data['max_drawdown']['策略'],
        'max_drawdown_benchmark': dict_data['max_drawdown']['benchmark'],
        'calmar': dict_data['calmar']['策略'],
        'calmar_benchmark': dict_data['calmar']['benchmark'],
        'sharpe': dict_data['yearly_sharpe']['策略'],
        'sharpe_benchmark': dict_data['yearly_sharpe']['benchmark'],
    }
    performance = {key: round(value, 3) for key, value in performance.items()}
    return res, performance


def backtest(task: Task):
    # st.write(task)
    with st.spinner('回测进行中，请稍后...'):
        # res.plot()
        res, performance = run_task(task)


        # st.write(dict_data)

        # st.write(performance)

        st.write('策略：')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # st.write(str(performance['cagr']*100))
            st.metric(label="年化收益", value='{}%'.format(round(performance['cagr'] * 100, 1)))

        with col2:
            st.metric(label="最大回撤率", value=str(round(performance['max_drawdown'] * 100,1)) + '%')
        with col3:
            st.metric(label="卡玛比率", value=performance['calmar'])
        with col4:
            st.metric(label="夏普比率", value=performance['sharpe'])
        st.write('基准')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="年化收益", value=str(round(performance['cagr_benchmark'] * 100, 1)) + '%')
        with col2:
            st.metric(label="最大回撤率", value=str(performance['max_drawdown_benchmark'] * 100) + '%')
        with col3:
            st.metric(label="卡玛比率", value=performance['calmar_benchmark'])
        with col4:
            st.metric(label="夏普比率", value=performance['sharpe_benchmark'])

        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        rcParams['font.family'] = 'SimHei'
        res.plot()
        st.pyplot(plt.gcf())

        # #st.write(res.get_transactions())
        # df_trans = res.get_transactions()
        # #
        # st.write(df_trans)
        # df_trans.reset_index(inplace=True)
        # df_trans['Date'] = df_trans['Date'].apply(lambda x:x.strftime('%Y%m%d'))
        # dict_trans = df_trans.to_dict(orient='list')
        # st.write(dict_trans)
        # #st.write(res.stats)


@st.dialog("发布任务到服务器")
def post_task(task):
    st.text_input('您的token')
    name = st.text_input('任务名称')
    desc = st.text_area('任务描述')
    if st.button('发布到服务器'):
        st.write('发布...')
        from streamlit_modal import Modal
        # requests.post('http://')
        url = 'http://127.0.0.1:8000/api/upsert_task'
        data = {
            'token': '190756c6-47d0-4734-97d4-c4c4ad31ab56',
            'name': name,
            'desc': desc,
            'rule': asdict(task)
        }
        import json

        response = requests.post(url, data=json.dumps(data))
        # response.json()
        if response.status_code == 200:
            st.write('{} 发布成功'.format(name))


def build_page():
    st.write('创建AI量化策略')
    task = Task()
    task.symbols = select_symbols()
    task.features, task.feature_names = factor_config()

    tab1, tab2 = st.tabs(['信号规则', '策略配置'])
    with tab1:
        task.buy_rules, task.sell_rules = signal_config()
    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            task.period = period_config()
        with col2:
            task.weight = weight_config()
        with col3:
            task.order_by, task.sort_descending, task.topK = order_by_config(task)

    if st.button('运行回测', type='primary'):
        # st.write(weight)
        # st.write(task)
        backtest(task)

    # if st.button('发布任务'):
    #     post_task(task)
