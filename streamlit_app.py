import streamlit as st
import pandas as pd
import tushare as ts
import yfinance as yf
import matplotlib.pyplot as plt
import os

# 使用 Streamlit Cloud 的 secrets
ts.set_token(st.secrets["TUSHARE_TOKEN"])
pro = ts.pro_api()

# 页面配置
st.set_page_config(page_title="简易智能选股工具", layout="wide")
st.title("📊 简易智能选股工具")
st.markdown("基于 Tushare 与 Yahoo Finance 接口支持 **A股 / 港股 / 美股** 切换")

# ======= 侧边栏选项 =======
st.sidebar.title("📋 选股条件")
market = st.sidebar.radio("选择市场", ["A股", "港股", "美股"])

# 设置筛选条件（仅对 A股开放财务筛选）
if market == "A股":
    roe_min = st.sidebar.slider("ROE（净资产收益率）>%", 0, 40, 15)
    pe_max = st.sidebar.slider("PE（市盈率）<", 0, 100, 25)
    gross_min = st.sidebar.slider("毛利率（%）>", 0, 100, 30)

# ======= 数据加载与展示 =======
st.info(f"📡 当前市场：{market}，正在获取数据...")

if market == "A股":
    try:
        stock_basic = pro.stock_basic(exchange='', list_status='L',
                                      fields='ts_code,symbol,name,area,industry,list_date')
        financials = pro.fina_indicator(start_date='20240101', end_date='20241231')
        df = pd.merge(stock_basic, financials, on='ts_code', how='inner')
        df_filtered = df[
            (df['roe'] > roe_min) &
            (df['pe'] < pe_max) &
            (df['grossprofit_margin'] > gross_min)
        ]
        st.success(f"✅ 共筛选出 {len(df_filtered)} 只符合条件的 A 股股票")
        st.dataframe(df_filtered[['ts_code', 'name', 'industry', 'roe', 'pe', 'grossprofit_margin']]
                     .sort_values(by='roe', ascending=False).reset_index(drop=True))
    except Exception as e:
        st.error("🚫 获取 A 股数据失败：" + str(e))

elif market == "港股":
    try:
        hk_df = pro.hk_basic()
        st.success(f"✅ 当前获取港股列表：{len(hk_df)} 条")
        st.dataframe(hk_df[['ts_code', 'name', 'list_date']])
    except Exception as e:
        st.error("🚫 获取港股数据失败：" + str(e))

elif market == "美股":
    try:
        tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        data = {t: yf.Ticker(t).info for t in tickers}
        df_us = pd.DataFrame(data).T
        st.success(f"✅ 当前展示精选美股 {len(tickers)} 只")
        st.dataframe(df_us[['symbol', 'shortName', 'marketCap', 'forwardPE', 'sector']])
    except Exception as e:
        st.error("🚫 获取美股数据失败：" + str(e))
