import streamlit as st
import pandas as pd
import requests
import re
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu  # 需要安装: pip install streamlit-option-menu

# ================= 配置与样式 =================
st.set_page_config(page_title="AI 行业洞察看板", layout="wide", page_icon="🚀")

# 自定义 CSS：模仿苹果官网的毛玻璃效果与极简导航
st.markdown("""
    <style>
    /* 隐藏原生顶部间距和菜单 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 全局背景与文字 */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* 标题样式 */
    h1, h2, h3 {
        color: #1D1D1F !important; /* 苹果黑 */
        font-family: "SF Pro Display", "PingFang SC", sans-serif;
        font-weight: 600;
    }

    /* 顶部导航容器微调 */
    .nav-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(0,0,0,0.1);
    }

    /* 卡片样式 */
    .product-card {
        background-color: #FFFFFF;
        border: 1px solid #F2F2F2;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0,0,0.5,1);
    }
    .product-card:hover {
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    /* 标签样式 */
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 8px;
        background-color: #F5F5F7;
        color: #1D1D1F;
    }
    .tag-highlight {
        background-color: #E60012;
        color: white;
    }

    /* 模拟引用块样式 */
    .insight-quote {
        background-color: #FBFBFD;
        padding: 15px;
        border-radius: 8px;
        font-size: 14px;
        border-left: 4px solid #E60012;
        color: #424245;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 顶部导航栏实现 =================
# 使用 option_menu 创建水平导航

selected = option_menu(
    menu_title=None, # 不显示标题
    options=["AI 产品进展", "知名博主动态", "AI 学习资料库"],
    icons=["rocket-takeoff", "person-badge", "book"], # 使用 bootstrap 图标
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fbfbfd", "max-width": "100%"},
        "icon": {"color": "#6e6e73", "font-size": "18px"}, 
        "nav-link": {
            "font-size": "15px", 
            "text-align": "center", 
            "margin": "0px", 
            "color": "#1d1d1f",
            "font-weight": "500"
        },
        "nav-link-selected": {"background-color": "#E60012", "color": "white"},
    }
)


# ================= 数据获取 =================
@st.cache_data(ttl=600)
def load_data():
    gsheet_url = st.secrets.get("gsheet_url", "")
    if not gsheet_url:
        return pd.DataFrame()
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=gsheet_url)
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()


# ================= 页面路由：AI 产品进展部分 =================
if selected == "AI 产品进展":
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>🚀 AI 产品进展</h1>", unsafe_allow_html=True)
    
    if not df.empty:
        # 极简筛选器
        with st.container():
            c1, c2, c3 = st.columns(3)
            with c1: month_filter = st.multiselect("时间", options=df['选择月份'].unique())
            with c2: category_filter = st.multiselect("分类", options=df['分类'].unique())
            with c3: company_filter = st.multiselect("公司", options=df['公司'].unique())

        filtered_df = df.copy()
        if month_filter: filtered_df = filtered_df[filtered_df['选择月份'].isin(month_filter)]
        if category_filter: filtered_df = filtered_df[filtered_df['分类'].isin(category_filter)]
        if company_filter: filtered_df = filtered_df[filtered_df['公司'].isin(company_filter)]

        # --- 修改部分：网格布局实现 ---
        # 设定每行显示的列数
        cols_per_row = 3 
        
        # 将数据按每行 3 个进行分组
        for i in range(0, len(filtered_df), cols_per_row):
            row_data = filtered_df.iloc[i : i + cols_per_row]
            cols = st.columns(cols_per_row)
            
            for index, (idx, row) in enumerate(row_data.iterrows()):
                with cols[index]:
                    st.markdown(f"""
                    <div class="product-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 12px; color: #86868b; font-weight: 600; text-transform: uppercase;">{row['公司']}</span>
                            <span style="color: #86868b; font-size: 12px;">{row['日期']}</span>
                        </div>
                        <h2 style="margin: 12px 0 8px 0; font-size: 20px; line-height: 1.2;">{row['进展']}</h2>
                        <div style="margin-bottom: 12px;">
                            <span class="tag tag-highlight">{row['分类']}</span>
                            <span class="tag">{row['地域']}</span>
                        </div>
                        <p style="color: #424245; line-height: 1.5; font-size: 14px; height: 60px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                            {row['核心特点']}
                        </p>
                        <div class="insight-quote" style="margin-top: 10px;">
                            <div style="font-size: 12px; font-weight: 700; color: #1d1d1f; margin-bottom: 4px;">市场反馈</div>
                            <div style="font-size: 13px; color: #6e6e73;">{row['市场反响']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        # --- 修改结束 ---

    else:
        st.warning("请检查数据配置...")
#获取数据信息
@st.cache_data(ttl=3600)  # 每小时缓存一次，避免频繁请求被 GitHub 封 IP
def fetch_github_builders_report():
    raw_url = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/README.zh-CN.md"
    try:
        response = requests.get(raw_url)
        if response.status_code == 200:
            content = response.text
            # 这里可以根据 README 的结构进行正则解析
            # 假设我们要提取“每日更新”部分的内容
            # 建议直接展示或简单清洗
            return content
        return "无法获取内容，请检查链接或网络。"
    except Exception as e:
        return f"发生错误: {e}"
# elif selected == "知名博主动态":
#     st.markdown("<h1 style='text-align: center; margin-top: 20px;'>📢 业界动态</h1>", unsafe_allow_html=True)
#     # 此处保留原有的博主动态展示逻辑...
#     st.info("博主动态加载中...")
elif selected == "知名博主动态":
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>📢 业界动态：Follow Builders</h1>", unsafe_allow_html=True)
    
    report_content = fetch_github_builders_report()
    
    if "###" in report_content:
        # 将内容按照日期或博主进行简单的切分展示
        # 这里使用 Streamlit 的容器来保持你的苹果风设计
        sections = report_content.split("###")[1:] # 假设 README 用 ### 分隔不同日期/博主
        
        # 同样采用 2-3 列的网格布局
        cols_per_row = 2
        for i in range(0, len(sections), cols_per_row):
            row_data = sections[i : i + cols_per_row]
            cols = st.columns(cols_per_row)
            
            for index, section in enumerate(row_data):
                with cols[index]:
                    st.markdown(f"""
                    <div class="product-card">
                        <div style="color: #E60012; font-weight: 600; font-size: 14px; margin-bottom: 10px;">推送更新</div>
                        <div style="font-size: 14px; color: #1d1d1f; line-height: 1.6;">
                            {section[:500] + '...' if len(section) > 500 else section}
                        </div>
                        <div style="margin-top: 15px; text-align: right;">
                            <a href="https://github.com/zarazhangrui/follow-builders" target="_blank" style="color: #0066CC; text-decoration: none; font-size: 12px;">查看原文 →</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='insight-quote'>{report_content}</div>", unsafe_allow_html=True)    

elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>📚 知识库</h1>", unsafe_allow_html=True)
    # 此处保留原有的资料库展示逻辑...
    st.info("资料库同步中...")
