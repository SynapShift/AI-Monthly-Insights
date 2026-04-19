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
    
    # 1. 核心 CSS 注入：定义标题 Hover 效果和透明点击层
    st.markdown("""
    <style>
    /* 标题悬停动画 */
    .click-title {
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .click-title:hover {
        color: #0071E3 !important;
        text-decoration: underline;
    }

    /* 强制让原生按钮透明，并使其覆盖在标题区域 */
    .title-trigger button {
        height: 60px !important;
        width: 100% !important;
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        position: relative !important;
        top: -190px !important; /* 向上平移覆盖标题，根据内容长度可能需微调 */
        z-index: 10 !important;
        box-shadow: none !important;
    }
    .title-trigger button:hover {
        background-color: transparent !important;
    }
    .title-trigger button:active {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    data_feeds = fetch_builder_feeds()
    tab1, tab2, tab3 = st.tabs(["Twitter Insights", "Podcast Summary", "Official Blog"])

    # --- Tab 1: Twitter (保持稳定) ---
    with tab1:
        twitter_list = data_feeds.get("Twitter", [])
        if twitter_list:
            x_cols = st.columns(2)
            for i, tweet in enumerate(twitter_list[:20]):
                with x_cols[i % 2]:
                    clean_text = html.unescape(tweet.get('text', '')).replace("\n", "<br>")
                    st.markdown(f"""
                    <div class="product-card" style="min-height:160px; padding:20px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <b style="color:#E60012; font-size:14px;">{tweet.get('author_name')}</b>
                            <span style="color:#888; font-size:11px;">@{tweet.get('author_handle')}</span>
                        </div>
                        <div style="font-size:13px; color:#1d1d1f; line-height:1.6;">{clean_text}</div>
                        <div style="margin-top:15px; border-top: 1px solid #F5F5F7; padding-top:10px; display:flex; justify-content:space-between; align-items:center;">
                            <span style="color:#86868b; font-size:10px;">🕒 {tweet.get('createdAt', '')[:10]}</span>
                            <a href="{tweet.get('url', '#')}" target="_blank" style="color:#0071e3; font-size:11px; text-decoration:none; font-weight:600;">Original Post →</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # --- Tab 2: Podcast (标题点击重构) ---
    with tab2:
        @st.dialog("对话全文摘要", width="large")
        def show_full_transcript(title, content):
            st.markdown(f"### {title}")
            st.markdown("---")
            with st.container(height=500):
                st.write(content)
            if st.button("关闭窗口", key="close_p_dlg"):
                st.rerun()

        pod_list = data_feeds.get("Podcasts", [])
        if pod_list:
            for pod in pod_list[:8]:
                raw_transcript = pod.get('transcript', '')
                clean_text = re.sub(r'Speaker \d+ \| \d+:\d+ - \d+:\d+', '', raw_transcript).strip()
                preview_summary = html.escape(clean_text)[:1000] + "..."
                pub_date = str(pod.get('publishedAt', ''))[:10] or "2026-04-19"
                title_val = pod.get('title', 'Untitled')

                # A. 渲染视觉卡片
                st.markdown(f"""
                <div class="product-card" style="padding-bottom: 24px; position: relative;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                        <span style="border-left:3px solid #E60012; padding-left:8px; font-size:11px; font-weight:700; color:#1D1D1F;">{pod.get('name', 'PODCAST').upper()}</span>
                        <span style="color:#86868B; font-size:11px;">{pub_date}</span>
                    </div>
                    
                    <h4 class="click-title" style="margin:0 0 12px 0; font-size:17px; color:#1D1D1F; line-height:1.4;">
                        {html.escape(title_val)}
                    </h4>

                    <div class="insight-box" style="margin-bottom: 20px;">
                        <p style="margin:0; font-size:13px; color:#424245; line-height:1.6;">
                            <span style="color:#E60012; font-weight:700; font-size:10px; margin-right:6px;">KEY INSIGHT:</span>{preview_summary}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <a href="{pod.get('url','#')}" target="_blank" style="color:#86868B; font-size:12px; text-decoration:none; font-weight:500;">收听原片 &rarr;</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # B. 透明触发层：覆盖在标题上方
                st.markdown('<div class="title-trigger">', unsafe_allow_html=True)
                if st.button(" ", key=f"t_btn_{pod.get('url')}", help="点击标题查看全文"):
                    show_full_transcript(title_val, clean_text)
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.info("💡 正在同步最新播客洞察...")

    # --- Tab 3: Official Blog ---
    with tab3:
        blog_list = data_feeds.get("Blogs", [])
        if blog_list:
            for blog in blog_list[:8]:
                raw_date = blog.get('publishedAt') or blog.get('date')
                date_str = str(raw_date)[:10] if raw_date else "2026-04-19"
                clean_blog = html.unescape(blog.get('content', blog.get('description', '')))[:300] + "..."
                st.markdown(f"""
                <div class="product-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span class="tag" style="background-color:#E8F2FF; color:#0071E3; margin:0;">{blog.get('name', 'Official Blog')}</span>
                        <span style="color:#86868b; font-size:11px;">{date_str}</span>
                    </div>
                    <h4 style="margin:0 0 10px 0; font-size:17px; line-height:1.4;">{blog.get('title')}</h4>
                    <p style="font-size:13px; color:#424245; line-height:1.6;">{clean_blog}</p>
                    <div style="margin-top:12px; text-align:right; border-top:1px solid #F5F5F7; padding-top:10px;">
                        <a href="{blog.get('url','#')}" target="_blank" style="color:#0071e3; font-size:12px; text-decoration:none; font-weight:600;">阅读全文 &rarr;</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
          




elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center;'>📚 知识库</h1>", unsafe_allow_html=True)
    st.info("内容正在开发中...")
