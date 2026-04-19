import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ================= 配置与样式 =================
st.set_page_config(page_title="AI 行业洞察看板", layout="wide")

# 自定义 CSS：极简红白配色与卡片样式
st.markdown("""
    <style>
    /* 全局背景与文字 */
    .stApp {
        background-color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #E60012 !important; /* 核心红 */
        font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #EEEEEE;
    }

    /* 卡片容器 */
    .product-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-left: 5px solid #E60012;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* 标签样式 */
    .tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
        background-color: #E60012;
        color: white;
    }
    .tag-secondary {
        background-color: #333333;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 数据获取 =================
def load_data():
    gsheet_url = st.secrets.get("gsheet_url", "")
    if not gsheet_url:
        st.error("请在 .streamlit/secrets.toml 中配置 gsheet_url")
        return pd.DataFrame()
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # 假设数据在第一个工作表
        df = conn.read(spreadsheet=gsheet_url, ttl="10m")
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()

df = load_data()

# ================= 导航栏 =================
with st.sidebar:
    st.title("Insights Hub")
    page = st.radio("导航", ["AI 产品进展", "知名博主动态", "AI 学习资料库"])
    st.divider()
    st.caption("AI Product Insights v1.0")

# ================= 页面 1：AI 产品进展 =================
if page == "AI 产品进展":
    st.header("🚀 AI 产品进展跟踪")
    
    if not df.empty:
        # 筛选器
        cols = st.columns(3)
        with cols[0]:
            month_filter = st.multiselect("选择月份", options=df['选择月份'].unique())
        with cols[1]:
            category_filter = st.multiselect("分类", options=df['分类'].unique())
        with cols[2]:
            company_filter = st.multiselect("公司", options=df['公司'].unique())

        # 过滤逻辑
        filtered_df = df.copy()
        if month_filter:
            filtered_df = filtered_df[filtered_df['选择月份'].isin(month_filter)]
        if category_filter:
            filtered_df = filtered_df[filtered_df['分类'].isin(category_filter)]
        if company_filter:
            filtered_df = filtered_df[filtered_df['公司'].isin(company_filter)]

        # 卡片展示
        for _, row in filtered_df.iterrows():
            st.markdown(f"""
            <div class="product-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <h3 style="margin: 0;">{row['公司']} - {row['进展']}</h3>
                    <span style="color: #666; font-size: 14px;">📅 {row['日期']}</span>
                </div>
                <div style="margin: 10px 0;">
                    <span class="tag">{row['分类']}</span>
                    <span class="tag tag-secondary">{row['地域']}</span>
                </div>
                <p><b>核心特点：</b>{row['核心特点']}</p>
                <p style="background-color: #FDF2F2; padding: 10px; border-radius: 4px; font-size: 14px; border-left: 3px solid #E60012;">
                    <b>市场反响：</b>{row['市场反响']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("等待数据同步中...")

# ================= 页面 2：知名博主动态 =================
elif page == "知名博主动态":
    st.header("📢 知名博主实时动态")
    
    # 模拟数据，实际可对接 RSS 或 API
    bloggers = [
        {"name": "Sam Altman", "platform": "X/Twitter", "content": "GPT-5 研发进度符合预期，推理能力有质的飞跃。", "time": "2小时前"},
        {"name": "Greg Brockman", "platform": "X/Twitter", "content": "Prism 工作空间正在邀请首批科研机构内测。", "time": "5小时前"}
    ]
    
    for post in bloggers:
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(f"**{post['name']}**")
                st.caption(post['platform'])
            with col2:
                st.write(post['content'])
                st.caption(f"发布时间: {post['time']}")
            st.divider()

# ================= 页面 3：学习资料库 =================
elif page == "AI 学习资料库":
    st.header("📚 AI 学习资料更新")
    
    materials = [
        {"title": "OpenAI 官方科研文档：Prism 工作流指南", "type": "PDF/文档", "date": "2026-01-10"},
        {"title": "从零开始理解多模态 Agentic Vision", "type": "视频教程", "date": "2026-01-15"},
        {"title": "2026 AI 医疗合规白皮书", "type": "行业报告", "date": "2026-01-18"}
    ]
    
    for item in materials:
        with st.expander(f"{item['title']} ({item['date']})"):
            st.write(f"资源类型: {item['type']}")
            st.button(f"点击查看详情 - {item['title'][:10]}...", key=item['title'])
