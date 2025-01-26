import streamlit as st
from config import DATA_DIR
import os
from .blocks import select_symbols


def build_page():
    st.write('金融序列风险，收益特性及时间序列分析')

    symbols = select_symbols()
    if len(symbols):
        from datafeed.dataloader import CSVDataloader
        df_all = CSVDataloader.get_df(symbols, set_index=True)
        df_close = CSVDataloader.get_col_df(df_all, 'close')
        df_close.dropna(inplace=True)
        df_returns = df_close.pct_change()
        df_equity = (df_returns + 1).cumprod()
        df_equity.dropna(inplace=True)
        print(df_equity)

        st.line_chart(df_equity, x=None)

        st.dataframe(df_returns.corr())
