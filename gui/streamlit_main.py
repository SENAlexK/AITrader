import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title='Quantlab - AI量化实验室', page_icon=":bar_chart:", layout='wide')
# 定义边栏导航
with st.sidebar:
    # https://icons.getbootstrap.com/
    choose = option_menu('AI量化实验室', ['量化策略', '金融数据分析'],
                         icons=['amazon','bar-chart', 'boxes', 'caret-right','fingerprint'])  # , 'boxes', 'caret-right', 'fingerprint'

if choose == '股票分析':
    from streamlit_pages.page_stock import build_page

    build_page()

if choose == '量化策略':
    from streamlit_pages.page_tasks import build_page
    build_page()


if choose == '金融数据分析':
    from streamlit_pages.page_timeseries import build_page

    build_page()

if choose == '创建策略':
    from streamlit_pages.page_strategy import build_page

    build_page()

if choose == '单因子分析':
    from streamlit_pages.page_alphalens import build_page

    build_page()

if choose == '数据下载与管理':
     from streamlit_pages.page_data import build_page
     build_page()
