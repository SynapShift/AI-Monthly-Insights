import streamlit as st
import pandas as pd
import requests
from streamlit_option_menu import option_menu
import html  # 在文件顶部添加导入

# ================= 1. 基础配置与 Apple 风格样式 =================
st.set_page_config(page_title="AI 行业洞察", layout="wide", page_icon="🚀")

st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 2rem;}
.stApp {background-color: #FFFFFF;}

/* 产品卡片样式 */
.product-card {
    background-color: #FFFFFF; 
    border: 1px solid #F2F2F2; 
    padding: 24px; 
    border-radius: 12px; 
    margin-bottom: 20px; 
    transition: all 0.3s ease; 
    min-height: 200px;
}
.product-card:hover {box-shadow: 0 8px 24px rgba(0,0,0,0.05);}
.tag {display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-right: 8px; background-color: #F5F5F7; color: #1D1D1F;}
.tag-highlight {background-color: #E60012; color: white;}
.insight-quote {background-color: #FBFBFD; padding: 15px; border-radius: 8px; font-size: 13px; border-left: 4px solid #E60012; color: #424245; margin-top: 10px;}
.builder-name {color: #E60012; font-weight: 700; font-size: 15px; margin-bottom: 5px;}
</style>
""", unsafe_allow_html=True)

# ================= 2. 数据获取逻辑 =================

# 读取 Google Sheets (第一页数据)
@st.cache_data(ttl=600)
def load_sheet_data():
    full_url = st.secrets.get("gsheet_url", "")
    if not full_url: return pd.DataFrame()
    try:
        csv_url = full_url.split("/edit")[0] + "/export?format=csv" if "/edit" in full_url else full_url
        return pd.read_csv(csv_url)
    except: return pd.DataFrame()

# 爬取 Follow-Builders 开源项目数据 (第二页数据)
# 修改后的函数
@st.cache_data(ttl=3600)
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
                
                # --- 增强版 Twitter 解析 ---
                if key == "Twitter":
                    # 兼容性检查：有些版本嵌套在 'x' 里，有些直接是列表
                    builders_list = raw_data.get("x") if isinstance(raw_data, dict) else raw_data
                    if not builders_list and isinstance(raw_data, list):
                        builders_list = raw_data
                    
                    if builders_list:
                        flattened_x = []
                        for builder in builders_list:
                            # 确保 builder 是字典格式
                            if not isinstance(builder, dict): continue
                            name = builder.get('name', 'Unknown')
                            handle = builder.get('handle', 'unknown')
                            for tweet in builder.get('tweets', []):
                                tweet['author_name'] = name
                                tweet['author_handle'] = handle
                                flattened_x.append(tweet)
                        # 排序并去重
                        results["Twitter"] = sorted(flattened_x, key=lambda x: x.get('createdAt', ''), reverse=True)
                
                # --- 播客解析 ---
                elif key == "Podcasts":
                    results["Podcasts"] = raw_data.get("podcasts", []) if isinstance(raw_data, dict) else raw_data
                
                # --- 博客解析 ---
                elif key == "Blogs":
                    results["Blogs"] = raw_data.get("blogs", []) if isinstance(raw_data, dict) else raw_data
        except Exception as e:
            # 方便你在本地控制台看到错误详情
            print(f"Error fetching {key}: {e}")
            continue
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

# --- 页面 1: AI 产品进展 ---
if selected == "AI 产品进展":
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>🚀 AI 产品进展</h1>", unsafe_allow_html=True)
    df = load_sheet_data()
    
    if not df.empty:
        # 筛选器
        c1, c2, c3 = st.columns(3)
        with c1:
            m_filter = st.multiselect("📅 时间范围", sorted(df['选择月份'].unique()) if '选择月份' in df.columns else [])
        with c2:
            cat_filter = st.multiselect("🏷️ 产品分类", sorted(df['分类'].unique()) if '分类' in df.columns else [])
        with c3:
            comp_filter = st.multiselect("🏢 所属公司", sorted(df['公司'].unique()) if '公司' in df.columns else [])

        # 过滤数据
        f_df = df.copy()
        if m_filter: f_df = f_df[f_df['选择月份'].isin(m_filter)]
        if cat_filter: f_df = f_df[f_df['分类'].isin(cat_filter)]
        if comp_filter: f_df = f_df[f_df['公司'].isin(comp_filter)]

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 布局展示
        cols = st.columns(3)
        for i, (idx, row) in enumerate(f_df.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="product-card">
                    <div style="font-size:12px;color:#86868b;font-weight:600;">{row.get('公司','-')} · {row.get('日期','-')}</div>
                    <h3 style="font-size:19px;margin:10px 0;">{row.get('进展','-')}</h3>
                    <div style="margin-bottom:12px;">
                        <span class="tag tag-highlight">{row.get('分类','-')}</span>
                        <span class="tag">{row.get('地域','-')}</span>
                    </div>
                    <p style="font-size:14px;color:#424245;">{row.get('核心特点','-')}</p>
                    <div class="insight-quote"><b>市场反馈：</b>{row.get('市场反响','-')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 请在 Secrets 中检查 gsheet_url 配置。")



# --- 页面 2: 知名博主动态 (乱码修正版) ---
# 修改后的页面渲染部分
# --- 页面 2: 知名博主动态 ---
elif selected == "知名博主动态":
    st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🏗️ 建造者动态</h1>", unsafe_allow_html=True)
    
    data_feeds = fetch_builder_feeds()
    
    # 确保这里定义了 3 个变量
    tab1, tab2, tab3 = st.tabs(["🐦 Twitter 洞察", "🎧 播客摘要", "📝 官方博客"])
    
    with tab1:
        twitter_list = data_feeds.get("Twitter", [])
        if twitter_list:
            x_cols = st.columns(2)
            for i, tweet in enumerate(twitter_list[:20]):
                with x_cols[i % 2]:
                    raw_text = html.unescape(tweet.get('text', ''))
                    clean_text = raw_text.replace("\n", "<br>")
                    st.markdown(f"""
                    <div class="product-card" style="min-height:160px; padding:20px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <b style="color:#E60012; font-size:14px;">{tweet.get('author_name')}</b>
                            <span style="color:#888; font-size:11px;">@{tweet.get('author_handle')}</span>
                        </div>
                        <div style="font-size:13px; color:#1d1d1f; line-height:1.6;">{clean_text}</div>
                        <div style="margin-top:15px; border-top: 1px solid #F5F5F7; padding-top:10px; text-align:right;">
                            <a href="{tweet.get('url', '#')}" target="_blank" style="color:#0071e3; font-size:11px; text-decoration:none;">查看原文 →</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("💡 正在同步最新 Twitter 动态...")

    with tab2:
        pod_list = data_feeds.get("Podcasts", [])
        if pod_list:
            for pod in pod_list[:8]:
                # 适配 transcript 字段
                summary = pod.get('transcript', '')[:250].replace("\n", " ") + "..."
                st.markdown(f"""
                <div class="product-card" style="border-left: 4px solid #E60012;">
                    <div style="font-size:12px;color:#86868b;font-weight:600;">{pod.get('name')} · {pod.get('publishedAt','')[:10]}</div>
                    <h4 style="margin:10px 0; font-size:16px;">{pod.get('title')}</h4>
                    <div class="insight-quote"><b>内容摘要：</b>{summary}</div>
                    <div style="margin-top:10px; text-align:right;">
                        <a href="{pod.get('url','#')}" target="_blank" style="color:#0071e3; font-size:12px;">收听原文 →</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 正在获取播客数据...")

    with tab3:  # <-- 注意这一行的缩进必须和 with tab1、with tab2 完全对齐
        blog_list = data_feeds.get("Blogs", [])
        if blog_list:
            for blog in blog_list[:8]:
                st.markdown(f"""
                <div class="product-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="tag" style="background-color:#E8F2FF; color:#0071E3;">{blog.get('name', 'Blog')}</span>
                        <span class="date-text">{blog.get('publishedAt', '')[:10]}</span>
                    </div>
                    <h4 style="margin:10px 0; font-size:16px;">{blog.get('title')}</h4>
                    <p style="font-size:13px; color:#424245;">{blog.get('description', '')[:150]}...</p>
                    <div style="margin-top:10px; text-align:right;">
                        <a href="{blog.get('url','#')}" target="_blank" style="color:#0071e3; font-size:12px;">阅读全文 →</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 正在获取官方博客数据...")
     

# --- 页面 3: 学习资料库 ---
elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center;'>📚 知识库</h1>", unsafe_allow_html=True)
    st.info("内容正在从 Notion/GitHub 自动同步中...")
