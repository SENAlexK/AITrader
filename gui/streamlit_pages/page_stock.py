import pandas as pd
import streamlit as st
import requests
@st.cache_data
def get_data():
    url = BASE_URL + 'api/basic_col?tb_name=basic_stock&col_name=industry'
    industries = requests.get(url).json()['data']

    url = BASE_URL + 'api/basic_col?tb_name=basic_stock&col_name=market'
    markets = requests.get(url).json()['data']
    return industries, markets


BASE_URL = 'http://ailabx.com/'
def build_page():

    st.write('A股数据分析')
    industries, markets = get_data()
    industry = st.multiselect('请选择行业',options=industries)
    market = st.multiselect('请选择板块：', options=markets)

    if st.button('筛选股票',type='primary'):
        # st.write(industry)
        # st.write(market)

        url = BASE_URL + 'api/query_basic?tb_name=basic_stock&industries={}&markets={}'.format(','.join(industry), ','.join(market))
        stocks = requests.get(url).json()['data']
        df = pd.DataFrame(stocks)
        st.write('符合条件的股票一共：{}支'.format(len(df)))
        st.write(df)


