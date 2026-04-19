import streamlit as st
import pandas as pd
import requests
import re
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

# ================= 1. 配置与样式 =================
st.set_page_config(page_title="AI 行业洞察看板", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #1D1D1F !important; font-family: "SF Pro Display", "PingFang SC", sans-serif; font-weight: 600; }
    .product-card { background-color: #FFFFFF; border: 1px solid #F2F2F2; padding: 24px; border-radius: 12px; margin-bottom: 20px; min-height: 280px; transition: all 0.3s ease; }
    .product-card:hover { box-shadow: 0 10px 30px rgba(0,0,0,0.08); transform: translateY(-2px); }
    .tag { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-right: 8px; background-color: #F5F5F7; color: #1D1D1F; }
    .tag-highlight { background-color: #E60012; color: white; }
    .insight-quote { background-color: #FBFBFD; padding: 15px; border-radius: 8px; font-size: 14px; border-left: 4px solid #E60012; color: #424245; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. 数据获取函数 =================
@st.cache_data(ttl=600)
def load_data():
    gsheet_url = st.secrets.get("gsheet_url", "")
    if not gsheet_url:
        return pd.DataFrame()
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(spreadsheet=gsheet_url)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_github_builders_report():
    raw_url = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/README.zh-CN.md"
    try:
        response = requests.get(raw_url, timeout=10)
        if response.status_code == 200:
            return response.text
        return "⚠️ 无法获取 GitHub 内容，请检查网络连接。"
    except Exception as e:
        return f"❌ 获取失败: {str(e)}"

# ================= 3. 导航栏 =================
selected = option_menu(
    menu_title=None,
    options=["AI 产品进展", "知名博主动态", "AI 学习资料库"],
    icons=["rocket-takeoff", "person-badge", "book"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fbfbfd", "max-width": "100%"},
        "nav-link": {"font-size": "15px", "color": "#1d1d1f", "font-weight": "500"},
        "nav-link-selected": {"background-color": "#E60012", "color": "white"},
    }
)

df = load_data()

# ================= 4. 页面路由逻辑 =================

# --- 页面 1: AI 产品进展 ---
if selected == "AI 产品进展":
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>🚀 AI 产品进展</h1>", unsafe_allow_html=True)
    
    if not df.empty:
        # 筛选器
        with st.container():
            c1, c2, c3 = st.columns(3)
            with c1: month_filter = st.multiselect("时间", options=df['选择月份'].unique())
            with c2: category_filter = st.multiselect("分类", options=df['分类'].unique())
            with c3: company_filter = st.multiselect("公司", options=df['公司'].unique())

        filtered_df = df.copy()
        if month_filter: filtered_df = filtered_df[filtered_df['选择月份'].isin(month_filter)]
        if category_filter: filtered_df = filtered_df[filtered_df['分类'].isin(category_filter)]
        if company_filter: filtered_df = filtered_df[filtered_df['公司'].isin(company_filter)]

        # 网格布局展示
        cols_per_row = 3 
        for i in range(0, len(filtered_df), cols_per_row):
            row_data = filtered_df.iloc[i : i + cols_per_row]
            cols = st.columns(cols_per_row)
            for index, (idx, row) in enumerate(row_data.iterrows()):
                with cols[index]:
                    # 采用 HTML 拼接字符串，避免 f-string 内部引号解析混乱
                    card_content = f"""
                    <div class="product-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 12px; color: #86868b; font-weight: 600;">{row['公司']}</span>
                            <span style="color: #86868b; font-size: 12px;">{row['日期']}</span>
                        </div>
                        <h2 style="margin: 12px 0 8px 0; font-size: 20px; line-height: 1.2;">{row['进展']}</h2>
                        <div style="margin-bottom: 12px;">
                            <span class="tag tag-highlight">{row['分类']}</span>
                            <span class="tag">{row['地域']}</span>
                        </div>
                        <p style="color: #424245; line-height: 1.5; font-size: 14px; height: 60px; overflow: hidden;">{row['核心特点']}</p>
                        <div class="insight-quote">
                            <div style="font-size: 12px; font-weight: 700; color: #1d1d1f;">市场反馈</div>
                            <div style="font-size: 13px; color: #6e6e73;">{row['市场反响']}</div>
                        </div>
                    </div>
                    """
                    st.markdown(card_content, unsafe_allow_html=True)
    else:
        st.warning("请检查数据配置...")

# --- 页面 2: 知名博主动态 ---
elif selected == "知名博主动态":
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>📢 业界动态：Follow Builders</h1>", unsafe_allow_html=True)
    report_content = fetch_github_builders_report()
    
    if "###" in report_content:
        sections = report_content.split("###")[1:]
        cols_per_row = 2
        for i in range(0, len(sections), cols_per_row):
            row_data = sections[i : i + cols_per_row]
            cols = st.columns(cols_per_row)
            for index, section in enumerate(row_data):
                with cols[index]:
                    # 限制字符长度防止排版撑破
                    clean_text = section[:500] + "..." if len(section) > 500 else section
                    st.markdown(f"""
                    <div class="product-card">
                        <div style="color: #E60012; font-weight: 600; font-size: 14px; margin-bottom: 10px;">推送更新</div>
                        <div style="font-size: 14px; color: #1d1d1f; line-height: 1.6;">{clean_text}</div>
                        <div style="margin-top: 15px; text-align: right;">
                            <a href="https://github.com/zarazhangrui/follow-builders" target="_blank" style="color: #0066CC; text-decoration: none; font-size: 12px;">查看原文 →</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("暂无格式化内容，直接显示原文：")
        st.markdown(f"<div class='insight-quote'>{report_content}</div>", unsafe_allow_html=True)

# --- 页面 3: 学习资料库 ---
elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>📚 知识库</h1>", unsafe_allow_html=True)
    st.info("资料库内容正在同步中，请稍后再来。")
