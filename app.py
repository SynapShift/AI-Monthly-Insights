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
    data_feeds = fetch_builder_feeds()
    tab1, tab2, tab3 = st.tabs(["Twitter Insights", "Podcast Summary", "Official Blog"])

    with tab1:
        twitter_list = data_feeds.get("Twitter", [])
        if twitter_list:
            x_cols = st.columns(2)
            for i, tweet in enumerate(twitter_list[:20]):
                with x_cols[i % 2]:
                    clean_text = html.unescape(tweet.get('text', '')).replace("\n", "<br>")
                    st.markdown(f"""
                    <div class="product-card" style="min-height:160px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                            <b style="color:#E60012; font-size:14px;">{tweet.get('author_name')}</b>
                            <span style="color:#888; font-size:11px;">@{tweet.get('author_handle')}</span>
                        </div>
                        <div style="font-size:13px; color:#1D1D1F; line-height:1.6;">{clean_text}</div>
                        <div style="margin-top:15px; border-top: 1px solid #F2F2F7; padding-top:10px; display:flex; justify-content:space-between;">
                            <span style="color:#86868b; font-size:10px;">Date: {tweet.get('createdAt', '')[:10]}</span>
                            <a href="{tweet.get('url', '#')}" target="_blank" style="color:#0071e3; font-size:11px; text-decoration:none; font-weight:600;">Original Post &rarr;</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab2:
            # 定义弹窗函数
            @st.dialog("对话全文摘要", width="large")
            def show_full_transcript(title, content):
                st.markdown(f"### {title}")
                st.markdown("---")
                with st.container(height=500):
                    st.write(content)
                if st.button("关闭"):
                    st.rerun()
    
            pod_list = data_feeds.get("Podcasts", [])
            if pod_list:
                for pod in pod_list[:8]:
                    # 1. 文本清洗
                    import re
                    raw_transcript = pod.get('transcript', '')
                    clean_text = re.sub(r'Speaker \d+ \| \d+:\d+ - \d+:\d+', '', raw_transcript).strip()
                    
                    # 预览长度延长至 600 字符
                    preview_summary = html.escape(clean_text)[:600] + "..."
                    
                    pub_date = str(pod.get('publishedAt', ''))[:10] or "2026-04-10"
                    pod_name = pod.get('name', 'PODCAST').upper()
                    title = pod.get('title', 'Untitled')
    
                    # 2. 渲染卡片头部和内容 (使用 div 开头但不闭合，包裹后续按钮)
                    st.markdown(f"""
                    <div class="product-card" style="margin-bottom: 0px; border-bottom: none; border-radius: 16px 16px 0 0;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                            <span style="border-left:3px solid #E60012; padding-left:8px; font-size:11px; font-weight:700; color:#1D1D1F;">{pod_name}</span>
                            <span style="color:#86868B; font-size:11px;">{pub_date}</span>
                        </div>
                        <h4 style="margin:0 0 12px 0; font-size:17px; color:#1D1D1F; line-height:1.4;">{html.escape(title)}</h4>
                        <div class="insight-box">
                            <p style="margin:0; font-size:13px; color:#424245; line-height:1.6;">
                                <span style="color:#E60012; font-weight:700; font-size:10px; margin-right:6px;">KEY INSIGHT:</span>{preview_summary}
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
                    # 3. 在同一个“视觉卡片”内放置操作按钮
                    # 通过设置背景色和边框，使其视觉上与上方卡片连为一体
                    with st.container():
                        st.markdown("""
                            <style>
                            div[data-testid="stVerticalBlock"] > div:has(div.button-row) {
                                background-color: white;
                            }
                            </style>
                        """, unsafe_allow_html=True)
                        
                        # 使用两列，第一列留空，将按钮挤到右侧
                        col1, col2, col3 = st.columns([2, 1.2, 1.2])
                        with col2:
                            if st.button("展开全文", key=f"full_{pod.get('url')}", use_container_width=True):
                                show_full_transcript(title, clean_text)
                        with col3:
                            # 构造一个与 st.button 高度一致的 HTML 按钮样式
                            st.markdown(f"""
                            <a href="{pod.get('url','#')}" target="_blank" style="
                                text-decoration: none;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 38px;
                                background-color: #FFFFFF;
                                color: #0071E3;
                                border: 1px solid #0071E3;
                                border-radius: 8px;
                                font-size: 14px;
                                font-weight: 500;
                            ">
                                收听原片 &rarr;
                            </a>
                            """, unsafe_allow_html=True)
                    
                    # 添加卡片底部的圆角补丁和间隔
                    st.markdown('<div style="height: 20px; border: 1px solid #F2F2F7; border-top: none; background: white; border-radius: 0 0 16px 16px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);"></div>', unsafe_allow_html=True)
    
            else:
                st.info("💡 正在同步最新播客洞察...")



    with tab3:
        blog_list = data_feeds.get("Blogs", [])
        if blog_list:
            for blog in blog_list[:8]:
                raw_date = blog.get('publishedAt') or blog.get('date')
                date_str = str(raw_date)[:10] if raw_date else "2026-04-19"
                clean_blog = html.unescape(blog.get('content', blog.get('description', '')))[:200] + "..."
                
                st.markdown(f"""
                <div class="product-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span class="tag" style="background-color:#E8F2FF; color:#0071E3; margin:0;">{blog.get('name', 'Official Blog')}</span>
                        <span style="color:#86868b; font-size:11px;">Date: {date_str}</span>
                    </div>
                    <h4 style="margin:0 0 10px 0; font-size:17px; line-height:1.4;">{blog.get('title')}</h4>
                    <p style="font-size:13px; color:#424245; line-height:1.6;">{clean_blog}</p>
                    <div style="margin-top:12px; text-align:right; border-top:1px solid #F5F5F7; padding-top:10px;">
                        <a href="{blog.get('url','#')}" target="_blank" style="color:#0071e3; font-size:12px; text-decoration:none; font-weight:600;">READ FULL ARTICLE &rarr;</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center;'>📚 知识库</h1>", unsafe_allow_html=True)
    st.info("内容正在开发中...")
