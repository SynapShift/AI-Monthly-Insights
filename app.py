import streamlit as st
import pandas as pd
import requests
from streamlit_option_menu import option_menu
import html
import re

# ================= 1. 基础配置与 Apple 风格样式 =================
st.set_page_config(page_title="AI 行业洞察", layout="wide", page_icon="🚀")

st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 2rem;}
.stApp {background-color: #FFFFFF;}

/* 产品卡片通用样式 */
.product-card {
    background-color: #FFFFFF; 
    border: 1px solid #F2F2F7; 
    padding: 24px; 
    border-radius: 16px; 
    margin-bottom: 20px; 
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.product-card:hover {box-shadow: 0 8px 24px rgba(0,0,0,0.05);}

/* 标签样式 */
.tag {
    display: inline-block; 
    padding: 4px 12px; 
    border-radius: 6px; 
    font-size: 11px; 
    font-weight: 600; 
    margin-right: 8px; 
    background-color: #F5F5F7; 
    color: #1D1D1F;
}
.tag-highlight {background-color: #E60012; color: white;}

/* 摘要内容区域 */
.insight-box {
    background-color: #FBFBFD; 
    padding: 16px; 
    border-radius: 10px; 
    border: 1px solid #F2F2F7; 
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ================= 2. 数据获取逻辑 =================

@st.cache_data(ttl=600)
def load_sheet_data():
    full_url = st.secrets.get("gsheet_url", "")
    if not full_url: return pd.DataFrame()
    try:
        csv_url = full_url.split("/edit")[0] + "/export?format=csv" if "/edit" in full_url else full_url
        return pd.read_csv(csv_url)
    except: return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_builder_feeds():
    base_url = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/"
    feeds = {
        "Twitter": base_url + "feed-x.json",
        "Podcasts": base_url + "feed-podcasts.json",
        "Blogs": base_url + "feed-blogs.json"
    }
    results = {"Twitter": [], "Podcasts": [], "Blogs": []}
    
    for key, url in feeds.items():
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                raw_data = r.json()
                if key == "Twitter":
                    builders_list = raw_data.get("x") if isinstance(raw_data, dict) else raw_data
                    if not builders_list and isinstance(raw_data, list): builders_list = raw_data
                    if builders_list:
                        flattened_x = []
                        for b in builders_list:
                            if not isinstance(b, dict): continue
                            for t in b.get('tweets', []):
                                t['author_name'] = b.get('name', 'Unknown')
                                t['author_handle'] = b.get('handle', 'unknown')
                                flattened_x.append(t)
                        results["Twitter"] = sorted(flattened_x, key=lambda x: x.get('createdAt', ''), reverse=True)
                elif key == "Podcasts":
                    results["Podcasts"] = raw_data.get("podcasts", []) if isinstance(raw_data, dict) else raw_data
                elif key == "Blogs":
                    results["Blogs"] = raw_data.get("blogs", []) if isinstance(raw_data, dict) else raw_data
        except: continue
    return results

# ================= 3. 导航栏 =================
selected = option_menu(
    menu_title=None,
    options=["AI 产品进展", "知名博主动态", "AI 学习资料库"],
    icons=["rocket-takeoff", "person-badge", "book"],
    orientation="horizontal",
    styles={
        "container": {"background-color": "transparent", "padding": "0"},
        "nav-link-selected": {"background-color": "#E60012", "color": "white"}
    }
)

# ================= 4. 页面路由 =================

if selected == "AI 产品进展":
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>🚀 AI 产品进展</h1>", unsafe_allow_html=True)
    df = load_sheet_data()
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: m_filter = st.multiselect("Time Range", sorted(df['选择月份'].unique()) if '选择月份' in df.columns else [])
        with c2: cat_filter = st.multiselect("Category", sorted(df['分类'].unique()) if '分类' in df.columns else [])
        with c3: comp_filter = st.multiselect("Company", sorted(df['公司'].unique()) if '公司' in df.columns else [])

        f_df = df.copy()
        if m_filter: f_df = f_df[f_df['选择月份'].isin(m_filter)]
        if cat_filter: f_df = f_df[f_df['分类'].isin(cat_filter)]
        if comp_filter: f_df = f_df[f_df['公司'].isin(comp_filter)]

        cols = st.columns(3)
        for i, (idx, row) in enumerate(f_df.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="product-card">
                    <div style="font-size:11px;color:#86868b;font-weight:600;">{row.get('公司','-')} | {row.get('日期','-')}</div>
                    <h3 style="font-size:18px;margin:12px 0;">{row.get('进展','-')}</h3>
                    <div style="margin-bottom:12px;">
                        <span class="tag tag-highlight">{row.get('分类','-')}</span>
                        <span class="tag">{row.get('地域','-')}</span>
                    </div>
                    <p style="font-size:13px;color:#424245;line-height:1.5;">{row.get('核心特点','-')}</p>
                    <div class="insight-box"><b style="color:#1D1D1F;">Market Feedback:</b><br>{row.get('市场反响','-')}</div>
                </div>
                """, unsafe_allow_html=True)

elif selected == "知名博主动态":
    st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🏗️ 知名博主动态</h1>", unsafe_allow_html=True)
    
    # 1. 注入 CSS：美化 st.expander 变成 Apple 卡片样式
    st.markdown("""
    <style>
    /* 隐藏折叠面板的默认边框和背景 */
    .stExpander {
        background-color: white !important;
        border: 1px solid #F2F2F7 !important;
        border-radius: 16px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    }
    /* 美化标题栏 */
    .stExpander [data-testid="stExpanderHeader"] {
        font-size: 17px !important;
        font-weight: 600 !important;
        color: #1D1D1F !important;
        padding: 20px !important;
    }
    .stExpander [data-testid="stExpanderHeader"]:hover {
        color: #0071E3 !important;
    }
    /* 内容区样式 */
    .stExpander [data-testid="stVerticalBlock"] {
        padding: 0 20px 20px 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    data_feeds = fetch_builder_feeds()
    tab1, tab2, tab3 = st.tabs(["Twitter Insights", "Podcast Summary", "Official Blog"])

    with tab1:
        # Twitter 部分保持你现有的代码即可...
        pass

    with tab2:
        pod_list = data_feeds.get("Podcasts", [])
        if pod_list:
            for pod in pod_list[:8]:
                raw_transcript = pod.get('transcript', '')
                clean_text = re.sub(r'Speaker \d+ \| \d+:\d+ - \d+:\d+', '', raw_transcript).strip()
                # 预览摘要：取前 300 字
                short_summary = clean_text[:300] + "..."
                pub_date = str(pod.get('publishedAt', ''))[:10] or "2026-04-19"
                title = pod.get('title', 'Untitled')

                # 使用 st.expander 作为卡片，标题就是面板名字
                with st.expander(f"🎙️ {title}"):
                    st.markdown(f"""
                    <div style="margin-bottom: 10px;">
                        <span style="color:#86868B; font-size:11px;">发布日期: {pub_date}</span>
                    </div>
                    <div style="background: #F5F5F7; padding: 15px; border-radius: 12px; margin-bottom: 15px;">
                        <p style="font-size: 14px; color: #424245; line-height: 1.6; margin: 0;">
                            <b style="color: #E60012;">核心摘要：</b><br>{clean_text[:1500]} 
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <a href="{pod.get('url','#')}" target="_blank" style="color:#0071E3; font-size:13px; text-decoration:none; font-weight:600;">收听原片 &rarr;</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("💡 正在同步最新播客洞察...")

    with tab3:
        # Blog 部分保持你现有的代码即可...
        pass




elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center;'>📚 知识库</h1>", unsafe_allow_html=True)
    st.info("内容正在开发中...")
