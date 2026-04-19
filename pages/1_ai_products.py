import streamlit as st
import pandas as pd
from utils.data import load_gsheet, clean_ai_products

st.set_page_config(page_title="AI Products", layout="wide")

st.title("🤖 AI 产品进展追踪")

df = clean_ai_products(load_gsheet())

if df.empty:
    st.warning("暂无数据")
    st.stop()

# ========= 筛选 =========
col1, col2, col3 = st.columns(3)

with col1:
    company = st.multiselect("公司", df["company"].dropna().unique())

with col2:
    category = st.multiselect("分类", df["category"].dropna().unique())

with col3:
    region = st.multiselect("地域", df["region"].dropna().unique())

filtered = df.copy()

if company:
    filtered = filtered[filtered["company"].isin(company)]
if category:
    filtered = filtered[filtered["category"].isin(category)]
if region:
    filtered = filtered[filtered["region"].isin(region)]

# ========= 展示 =========
for _, row in filtered.sort_values("date", ascending=False).iterrows():

    with st.container():
        st.markdown(f"### 🏢 {row['company']} · {row['date']}")

        st.markdown(f"""
**📌 进展：** {row['progress']}  

**⚙️ 核心特点：** {row['feature']}  

**📊 市场反响：** {row['reaction']}
""")

        st.divider()
