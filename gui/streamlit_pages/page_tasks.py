import json
from datetime import datetime

from bt_algos_extend import Engine
from config import DATA_DIR
import os
import streamlit as st

from tasks import task_list


def get_instruments():
    files = os.listdir(DATA_DIR.joinpath('instruments').resolve())
    return files


def build_page():
    tasks = task_list()

    def _format_x(task):
        return task.name

    task_selected = st.multiselect(label='请选择策略(支持同时运行多个策略)', options=tasks, format_func=lambda x: _format_x(x))
    file = st.selectbox(label='选择标的池', options=get_instruments(),index=None)
    symbols = None
    if file:
        with open(DATA_DIR.joinpath('instruments').joinpath(file).resolve(), 'r') as file:
            lines = file.readlines()

            # 将每行的数据放入列表中
            symbols = [line.strip() for line in lines]
            st.write(symbols)
    if st.button('运行策略'):
        with st.spinner('回测进行中，请稍后...'):
            if symbols and len(symbols):
                for t in task_selected:
                    t.symbols = symbols
            res = Engine().run_tasks(task_selected)

            # df = res.stats
            df = res.stats
            import matplotlib.pyplot as plt
            # plt.title('策略运行结果')
            from matplotlib import rcParams
            rcParams['font.family'] = 'SimHei'
            res.plot()

            st.pyplot(plt.gcf())

            for c in df.columns:
                st.markdown("<strong><u>{}</u></strong>".format(c), unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="年化收益", value='{}%'.format(round(df.loc['cagr'][c] * 100, 1)))
                with col2:
                    st.metric(label="最大回撤率", value=str(round(df.loc['max_drawdown'][c] * 100, 1)) + '%')
                with col3:
                    st.metric(label="卡玛比率", value=str(round(df.loc['calmar'][c], 2)))

            # performance = {key: round(value, 3) for key, value in performance.items()}
            #
            # st.write('策略：')
            # col1, col2, col3, col4 = st.columns(4)
            # with col1:
            #     # st.write(str(performance['cagr']*100))
            #     st.metric(label="年化收益", value='{}%'.format(round(performance['cagr'] * 100, 1)))
            #
            # with col2:
            #     st.metric(label="最大回撤率", value=str(round(performance['max_drawdown'] * 100, 1)) + '%')
            # with col3:
            #     st.metric(label="卡玛比率", value=performance['calmar'])
            # with col4:
            #     st.metric(label="夏普比率", value=performance['sharpe'])
            # st.write('基准')
            # col1, col2, col3, col4 = st.columns(4)
            # with col1:
            #     st.metric(label="年化收益", value=str(round(performance['cagr_benchmark'] * 100, 1)) + '%')
            # with col2:
            #     st.metric(label="最大回撤率", value=str(performance['max_drawdown_benchmark'] * 100) + '%')
            # with col3:
            #     st.metric(label="卡玛比率", value=performance['calmar_benchmark'])
            # with col4:
            #     st.metric(label="夏普比率", value=performance['sharpe_benchmark'])

            3

            # df = res.stats
            # index_labels = ['cagr', 'calmar','max_drawdown']  # 假设这是你想要选择的行的索引标签列表
            # index_positions = [df.index.get_loc(label) for label in index_labels]
            # df_selected = df.iloc[index_positions]
            # st.write(df_selected)

            # st.write(res.get_transactions())
