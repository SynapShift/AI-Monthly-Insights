import streamlit as st
import pandas as pd
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
# selected = option_menu(
#     menu_title=None, # 不显示标题
#     options=["AI 产品进展", "知名博主动态", "AI 学习资料库"],
#     icons=["rocket-takeoff", "person-badge", "book"], # 使用 bootstrap 图标
#     menu_icon="cast",
#     default_index=0,
#     orientation="horizontal",
#     styles={
#         "container": {"padding": "0!important", "background-color": "#fbfbfd", "max-width": "100%"},
#         "icon": {"color": "#6e6e73", "font-size": "18px"}, 
#         "nav-link": {
#             "font-size": "15px", 
#             "text-align": "center", 
#             "margin": "0px", 
#             "color": "#1d1d1f",
#             "font-weight": "500"
#         },
#         "nav-link-selected": {"background-color": "#E60012", "color": "white"},
#     }
# )
selected = option_menu(
    menu_title=None,
    options=["AI 产品进展", "知名博主动态", "AI 学习资料库"],
    icons=["cpu", "broadcast", "archive"],
    orientation="horizontal",
    styles={
        "container": {
            "padding": "5px", 
            "background-color": "#ffffff", 
            "border-radius": "50px", # 彻底变圆
            "margin": "0 auto", 
            "width": "fit-content", # 宽度随内容变化
            "border": "1px solid #f0f0f0",
            "box-shadow": "0 4px 12px rgba(0,0,0,0.05)"
        },
        "nav-link": {
            "font-size": "14px", 
            "border-radius": "50px", # 链接也要变圆
            "padding": "10px 20px"
        },
        "nav-link-selected": {"background-color": "#E60012"},
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

# ================= 页面路由 =================
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

        # 瀑布流布局
        for _, row in filtered_df.iterrows():
            st.markdown(f"""
            <div class="product-card">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 13px; color: #86868b; font-weight: 600;">{row['公司']}</span>
                    <span style="color: #86868b; font-size: 13px;">{row['日期']}</span>
                </div>
                <h2 style="margin: 8px 0; font-size: 24px;">{row['进展']}</h2>
                <div style="margin-bottom: 15px;">
                    <span class="tag tag-highlight">{row['分类']}</span>
                    <span class="tag">{row['地域']}</span>
                </div>
                <p style="color: #1d1d1f; line-height: 1.5;">{row['核心特点']}</p>
                <div class="insight-quote">
                    <b>市场反馈：</b>{row['市场反响']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("请检查数据配置...")

elif selected == "知名博主动态":
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>📢 业界动态</h1>", unsafe_allow_html=True)
    # 此处保留原有的博主动态展示逻辑...
    st.info("博主动态加载中...")

elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>📚 知识库</h1>", unsafe_allow_html=True)
    # 此处保留原有的资料库展示逻辑...
    st.info("资料库同步中...")
