import streamlit as st
from .blocks import select_instruments, select_dates


def build_page():
    symbols = select_instruments()
    factor_expr = st.text_input('请输入因子表达式', value='roc(close,20)')
    start_date, end_date = select_dates()
    if st.button('加载数据并进行因子分析', type='primary'):
        with st.spinner('分析进行中，请稍后...'):
            from datafeed.dataloader import CSVDataloader

            loader = CSVDataloader()
            df = loader.get_df(symbols=symbols, set_index=True, start_date=start_date, end_date=end_date)
            df = loader.calc_expr(df, fields=[factor_expr], names=['factor_name'])
            # df.set_index(['date', 'symbol'], inplace=True)
            factor_df = df[['factor_name','symbol']]
            factor_df.set_index([factor_df.index, 'symbol'], inplace=True)
            close_df = loader.get_col_df(df, col='close')

            st.write(factor_df)

            from alpha.alphalens.utils import get_clean_factor_and_forward_returns

            results = get_clean_factor_and_forward_returns(factor_df, close_df)
            # st.write(results)

            from alpha.alphalens.streamit_tears import create_full_tear_sheet
            create_full_tear_sheet(results)
