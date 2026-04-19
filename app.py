import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ================= 1. 性能层：页面配置与缓存优化 =================
st.set_page_config(
    page_title="AI Insights | 进展跟踪", 
    layout="wide", 
    initial_sidebar_state="collapsed" # 移动端默认收起侧边栏
)

# 自定义 CSS：增强移动端适配与视觉深度
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* 搜索框美化 */
    .stTextInput input {
        border-radius: 20px;
        border: 1px solid #E60012;
    }

    /* 移动端适配卡片 */
    .product-card {
        background-color: #FFFFFF;
        border: 1px solid #F0F0F0;
        border-left: 4px solid #E60012;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* 响应式字体调整 */
    @media (max-width: 640px) {
        .product-title { font-size: 16px !important; }
        .tag { font-size: 10px !important; }
    }

    .tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
        background-color: #FEECEC;
        color: #E60012;
        border: 1px solid #FAD2D2;
    }
    
    .metric-box {
        text-align: center;
        padding: 10px;
        background: #F8F9FA;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. 数据层：性能优化 (TTL缓存) =================
@st.cache_data(ttl=600) # 10分钟内不重复请求，大幅提升加载速度
def get_data():
    gsheet_url = st.secrets.get("gsheet_url", "")
    if not gsheet_url:
        return pd.DataFrame()
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(spreadsheet=gsheet_url)

df = get_data()

# ================= 3. 交互层：搜索与发现逻辑 =================
# 顶部搜索栏与核心指标
st.title("🔴 AI 进展实时跟踪")

if not df.empty:
    # 搜索框 - 增强发现效率
    search_query = st.text_input("", placeholder="🔍 输入公司、技术关键词或地域进行快速检索...")

    # 数据概览组件
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-box"><b>本月新增</b><br><span style="color:#E60012;font-size:20px;">{len(df)}</span></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-box"><b>覆盖公司</b><br><span style="color:#E60012;font-size:20px;">{df["公司"].nunique()}</span></div>', unsafe_allow_html=True)
    with m3:
        latest_date = df["日期"].max()
    st.markdown("---")

    # 过滤逻辑
    filtered_df = df.copy()
    if search_query:
        # 支持全字段模糊搜索
        mask = filtered_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        filtered_df = filtered_df[mask]

    # ================= 4. 展示层：移动端优先布局 =================
    if filtered_df.empty:
        st.warning("未找到匹配的结果，请尝试其他关键词。")
    else:
        # 使用列布局，但在窄屏下会自动堆叠
        for _, row in filtered_df.iterrows():
            st.markdown(f"""
            <div class="product-card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: bold; color: #333; font-size: 18px;" class="product-title">{row['公司']}</span>
                    <span style="color: #999; font-size: 12px;">{row['日期']}</span>
                </div>
                <div style="margin-bottom: 12px;">
                    <span class="tag">{row['分类']}</span>
                    <span class="tag" style="background:#333; color:white; border:none;">{row['地域']}</span>
                </div>
                <div style="font-size: 15px; color: #444; line-height: 1.6;">
                    <strong>进展：</strong>{row['进展']}<br>
                    <div style="margin-top: 8px; padding: 10px; background: #FAFAFA; border-radius: 6px; font-size: 14px;">
                        <span style="color: #E60012;">●</span> <b>核心：</b>{row['核心特点']}<br>
                        <span style="color: #E60012;">●</span> <b>反响：</b>{row['市场反响']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("💡 请在 Secrets 中配置数据源链接。")

# 侧边栏保持极简
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/e60012/artificial-intelligence.png", width=50)
    page = st.selectbox("功能切换", ["产品进展", "博主动态", "学习资料"])
    st.divider()
    st.caption("Designed for AI PMs")
