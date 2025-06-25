
import streamlit as st
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
import os

# 设置 Tushare Token
ts.set_token(os.getenv("TUSHARE_TOKEN", "your_token_here"))
pro = ts.pro_api()

st.set_page_config(page_title="智能选股工具", layout="wide")
st.title("📊 简易智能选股工具")
st.caption("基于 Tushare 接口和基础财务指标")

# 选择筛选条件
st.sidebar.header("📋 选股条件")
roe_min = st.sidebar.slider("ROE（净资产收益率）>%", 0, 40, 15)
pe_max = st.sidebar.slider("PE（市盈率）<", 0, 100, 25)
gross_min = st.sidebar.slider("毛利率（%）>", 0, 100, 30)

# 获取股票列表
@st.cache_data
def get_basic_stocks():
    return pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

# 获取财务指标
@st.cache_data
def get_financial_data():
    return pro.fina_indicator(start_date='20240101', end_date='20241231')

st.info("📡 正在获取数据...")
stock_basic = get_basic_stocks()
fina = get_financial_data()

# 合并数据
df = pd.merge(stock_basic, fina, on='ts_code', how='inner')

# 筛选条件
df_filtered = df[
    (df['roe'] > roe_min) &
    (df['pe'] < pe_max) &
    (df['grossprofit_margin'] > gross_min)
]

st.success(f"✅ 共筛选出 {len(df_filtered)} 只符合条件的股票")

# 显示表格
st.dataframe(df_filtered[['ts_code', 'name', 'area', 'industry', 'roe', 'pe', 'grossprofit_margin']]
             .sort_values(by='roe', ascending=False).reset_index(drop=True))

# 可视化柱状图
st.subheader("📈 ROE Top10 可视化")
top10 = df_filtered.sort_values(by='roe', ascending=False).head(10)
fig, ax = plt.subplots()
ax.bar(top10['name'], top10['roe'])
ax.set_ylabel('ROE (%)')
ax.set_xticklabels(top10['name'], rotation=45)
st.pyplot(fig)

st.caption("数据来源：Tushare，筛选逻辑仅供学习参考")
