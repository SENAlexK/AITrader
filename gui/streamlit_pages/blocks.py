import os

import pandas as pd
import streamlit as st

from config import DATA_DIR
from datetime import datetime


@st.cache_data
def load_basic():
    basics = os.listdir(DATA_DIR.joinpath('basic').resolve())
    dfs = []
    for file in basics:
        dfs.append(pd.read_csv(DATA_DIR.joinpath('basic').joinpath(file)))
    all = pd.concat(dfs)[['name', 'symbol']]
    all.set_index('symbol', inplace=True)
    return all


all_basic = load_basic()


def select_symbols():
    files = os.listdir(DATA_DIR.joinpath('quotes').resolve())
    files = [f.replace('.csv', '') for f in files]

    # print(files)
    def _format_x(x):
        if x in all_basic.index:
            name = all_basic.loc[x]['name']
            return '{}({})'.format(name, x)
        return x

    symbols = st.multiselect(label='请选择投资标的', default=['510300.SH', '159915.SZ'],
                             options=list(files), format_func=lambda x: _format_x(x))
    return symbols


def select_instruments():
    from config import DATA_DIR
    instru = DATA_DIR.joinpath('instruments')
    import os

    files = os.listdir(instru.resolve())
    filename = st.selectbox('请选择投资标的集合:', options=files)
    with open(instru.joinpath(filename).resolve(), 'r') as f:
        symbols = f.readlines()

    symbols = [s.replace('\n', '') for s in symbols]
    st.write(symbols)
    return symbols


def select_dates():
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('起始日期', value=datetime.strptime('20100101','%Y%m%d'))
    with col2:
        end_date = st.date_input('结束日期', value=datetime.now().date())
    return start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
