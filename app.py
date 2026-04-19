import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

# 1. 基础配置
st.set_page_config(page_title="AI 行业洞察", layout="wide", page_icon="🚀")

# 2. 样式注入
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 2rem;}
.stApp {background-color: #FFFFFF;}
.product-card {background-color: #FFFFFF; border: 1px solid #F2F2F2; padding: 24px; border-radius: 12px; margin-bottom: 20px; transition: all 0.3s ease;}
.tag {display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-right: 8px; background-color: #F5F5F7; color: #1D1D1F;}
.tag-highlight {background-color: #E60012; color: white;}
.insight-quote {background-color: #FBFBFD; padding: 15px; border-radius: 8px; font-size: 14px; border-left: 4px solid #E60012; color: #424245; margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

# 3. 数据函数定义
@st.cache_data(ttl=600)
def load_data():
    gsheet_url = st.secrets.get("gsheet_url", "")
    if not gsheet_url: return pd.DataFrame()
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(spreadsheet=gsheet_url)
    except: return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_github_report():
    url = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/README.zh-CN.md"
    try:
        r = requests.get(url, timeout=10)
        return r.text if r.status_code == 200 else "获取失败"
    except: return "连接超时"

# 4. 导航栏
selected = option_menu(
    menu_title=None,
    options=["AI 产品进展", "知名博主动态", "AI 学习资料库"],
    icons=["rocket-takeoff", "person-badge", "book"],
    orientation="horizontal",
    styles={"nav-link-selected": {"background-color": "#E60012"}}
)

# 5. 路由逻辑 (严格对齐)
if selected == "AI 产品进展":
    df = load_data()
    st.markdown("<h1 style='text-align: center;'>🚀 AI 产品进展</h1>", unsafe_allow_html=True)
    if not df.empty:
        cols_per_row = 3
        for i in range(0, len(df), cols_per_row):
            batch = df.iloc[i : i + cols_per_row]
            cols = st.columns(cols_per_row)
            for idx, (index, row) in enumerate(batch.iterrows()):
                with cols[idx]:
                    html = f"""
                    <div class="product-card">
                        <div style="font-size:12px;color:#86868b;">{row.get('公司','-')} | {row.get('日期','-')}</div>
                        <h2 style="font-size:20px;">{row.get('进展','-')}</h2>
                        <div style="margin:10px 0;"><span class="tag tag-highlight">{row.get('分类','-')}</span></div>
                        <p style="font-size:14px;color:#424245;height:60px;overflow:hidden;">{row.get('核心特点','-')}</p>
                        <div class="insight-quote"><b>反馈:</b> {row.get('市场反响','-')}</div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("数据加载中或配置有误...")

elif selected == "知名博主动态":
    st.markdown("<h1 style='text-align: center;'>📢 业界动态</h1>", unsafe_allow_html=True)
    content = fetch_github_report()
    if "###" in content:
        sections = content.split("###")[1:]
        cols = st.columns(2)
        for i, s in enumerate(sections[:10]): # 先取前10个防止页面太长
            with cols[i % 2]:
                txt = s[:400] + "..." if len(s) > 400 else s
                st.markdown(f'<div class="product-card"><div style="color:#E60012;font-weight:600;">博主动态</div><div style="font-size:14px;">{txt}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='insight-quote'>{content}</div>", unsafe_allow_html=True)

elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center;'>📚 知识库</h1>", unsafe_allow_html=True)
    st.info("内容同步中...")
