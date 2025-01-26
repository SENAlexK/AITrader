import pandas as pd
import streamlit as st
import requests
from config import DATA_DIR_QUOTES


def download_quotes(symbol):
    url = 'http://ailabx.com/api/quotes?tb_name=quotes_future_continue_d&symbol={}'.format(symbol)
    data = requests.get(url).json()['data']
    df = pd.DataFrame(data)
    return df

def get_future_list():
    url = 'http://ailabx.com/api/basic?tb_name=basic_future_continue'
    data = requests.get(url).json()['data']
    symbols = list(pd.DataFrame(data)['symbol'])
    return symbols

def build_page():
    st.write('下载期货主连合约数据')
    b_skip = st.checkbox('本地已存在，则自动跳过')
    if st.button('下载期货主连合约数据'):
        symbols = get_future_list()
        for s in symbols:
            if b_skip and DATA_DIR_QUOTES.joinpath(s+'.csv').exists():
                print('本地已存在，跳过')
                continue
            print('下载：{}'.format(s))
            df = download_quotes(s)
            df.to_csv(DATA_DIR_QUOTES.joinpath(s+'.csv'),index=False)

