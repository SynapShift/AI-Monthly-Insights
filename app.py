import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

# ================= 配置与样式 =================
st.set_page_config(page_title="AI 行业洞察看板", layout="wide")

# 自定义 CSS：深度复刻图中的高端奢华画册风格
st.markdown("""
    <style>
    /* 隐藏原生顶部和菜单 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem;
        max-width: 1100px; /* 收窄主内容区，保持图中的呼吸感 */
    }

    /* 全局背景与大标题 */
    .stApp {
        background-color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #1D1D1F !important;
        font-family: "PingFang SC", "Helvetica Neue", sans-serif;
        font-weight: 700 !important;
    }
    
    /* 顶部导航容器 */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid #EAEAEA;
        margin-bottom: 30px;
    }

    /* 苹果/高端品牌风格的纯文字导航项覆盖 */
    div[data-component-instance-name="option_menu"] {
        border: none !important;
    }
    .nav-link {
        font-size: 14px !important;
        color: #515154 !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        background: none !important;
    }
    .nav-link:hover {
        color: #000000 !important;
    }
    .nav-link-selected {
        color: #6B001A !important; /* 图中的高级暗酒红色 */
        font-weight: 600 !important;
        background: none !important;
        border-bottom: 2px solid #6B001A !important;
        border-radius: 0px !important;
    }

    /* 复刻图中的胶囊按钮 */
    .pill-btn-red {
        background-color: #6B001A;
        color: white !important;
        padding: 8px 24px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none;
        transition: opacity 0.2s;
    }
    .pill-btn-white {
        background-color: #FFFFFF;
        color: #1D1D1F !important;
        padding: 8px 24px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid #1D1D1F;
        text-decoration: none;
    }
    
    /* 图中的大卡片样式 */
    .luxury-card {
        background-color: #FFFFFF;
        padding: 0px;
        margin-bottom: 40px;
    }
    .featured-box {
        background-color: #6B001A;
        color: white;
        padding: 40px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .featured-box h2, .featured-box p {
        color: white !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

# ================= 1. 完全复刻的顶边栏 =================
# 使用 Streamlit columns 模拟“左Logo、中导航、右按钮”
head_col1, head_col2, head_col3 = st.columns([1.5, 4, 1.2], vertical_alignment="center")

with head_col1:
    st.markdown("<h3 style='margin:0; font-size: 20px; letter-spacing: 1px;'>SHUFFLE PROJECT</h3>", unsafe_allow_html=True)

with head_col2:
    # 隐藏菜单的边框，使其纯文字悬浮
    page = option_menu(
        menu_title=None,
        options=["Product进展", "博主动态", "资料库"],
        icons=None,
        orientation="horizontal",
        styles={"container": {"background-color": "transparent"}}
    )

with head_col3:
    # 右侧胶囊 CTA 按钮
    st.markdown("<a href='#' class='pill-btn-red'>Contact</a>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top:0; border-top: 1px solid #EAEAEA;'>", unsafe_allow_html=True)


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


# ================= 2. 页面路由与画册风排版 =================
if page == "Product进展":
    # 模拟图中的大字报 Title
    st.markdown("""
        <div style='margin: 40px 0;'>
            <span style='font-size:12px; text-transform:uppercase; color:#86868b; letter-spacing:2px;'>AI Platform</span>
            <h1 style='font-size: 40px; margin-top: 10px; line-height: 1.2;'>AI 行业前沿进展<br>与核心动态追踪</h1>
        </div>
        """, unsafe_allow_html=True)

    # 模拟图中的图文排版
    col_text, col_img = st.columns([1, 1.5], gap="large")
    
    with col_text:
        st.markdown("""
            <div style='margin-top: 20px;'>
                <p style='color:#6e6e73; font-size:15px; line-height:1.6;'>
                    持续追踪全球最顶尖的人工智能进展。通过极简的结构化看板，为您过滤噪音，直击核心技术突破与商业落地动态。
                </p>
                <div style='margin-top: 30px; display: flex; gap: 15px;'>
                    <a href='#' class='pill-btn-red'>View properties</a>
                    <a href='#' class='pill-btn-white'>Learn more</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with col_img:
        # 这里模拟图中的主视觉图（实际可放图表或卡片）
        st.markdown("""
            <div class='featured-box'>
                <span style='font-size: 11px; text-transform: uppercase; opacity: 0.8;'>Feature Highlight</span>
                <h2 style='margin: 10px 0; font-size: 28px;'>快速拉升与<br>多模态 Agent 演进</h2>
                <p style='font-size:14px; opacity: 0.9;'>本月重点关注各大模型在视觉处理和自主决策层面的突飞猛进...</p>
                <a href='#' style='color: white; font-size: 14px; font-weight: 600; text-decoration: none;'>Explore →</a>
            </div>
            """, unsafe_allow_html=True)

    # 瀑布流/Bento 栅格卡片
    st.markdown("<h2 style='font-size: 28px; margin: 40px 0 20px 0;'>最新跟踪</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        # 筛选器
        c1, c2 = st.columns([1, 3])
        with c1:
            month_filter = st.multiselect("月份", options=df['选择月份'].unique())
        
        filtered_df = df if not month_filter else df[df['选择月份'].isin(month_filter)]

        # 复刻图中的多栏画册排版
        cols = st.columns(3, gap="medium")
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                    <div style='border-bottom: 1px solid #EAEAEA; padding-bottom: 20px; margin-bottom: 20px;'>
                        <span style='font-size: 11px; font-weight: 700; color: #6B001A;'>{row['分类']}</span>
                        <h3 style='font-size: 18px; margin: 5px 0;'>{row['公司']} - {row['进展']}</h3>
                        <p style='color: #6e6e73; font-size: 13px; line-height: 1.5;'>{row['核心特点']}</p>
                        <a href='#' style='color: #1D1D1F; font-size: 13px; font-weight: 600; text-decoration: none;'>View project →</a>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("等待数据同步中...")

elif page == "博主动态":
    st.markdown("<h1 style='margin-top: 30px;'>📢 业界动态</h1>", unsafe_allow_html=True)
    st.info("博主动态正在按照该风格重构中...")

elif page == "资料库":
    st.markdown("<h1 style='margin-top: 30px;'>📚 知识库</h1>", unsafe_allow_html=True)
    st.info("学习资料库正在按照该风格重构中...")
