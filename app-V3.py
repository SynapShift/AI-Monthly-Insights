import streamlit as st
import pandas as pd
import urllib.parse

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="AI Sentinel · 月度洞察",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

GSHEET_URL = st.secrets.get("gsheet_url", "")

# ---------- 数据加载 (保持不变) ----------
@st.cache_data(ttl=300)
def load_all_data():
    if not GSHEET_URL:
        return pd.DataFrame()
    try:
        base_url = GSHEET_URL.split('/edit')[0]
        encoded_name = urllib.parse.quote("sheet")
        csv_url = f"{base_url}/export?format=csv&sheet={encoded_name}"
        df = pd.read_csv(csv_url)
        df.columns = df.columns.astype(str).str.strip()
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            df = df.dropna(subset=['日期'])
            df['选择月份'] = df['日期'].dt.strftime('%Y-%m')
            df = df.sort_values('日期', ascending=False)
        if '分类' in df.columns:
            df['分类'] = df['分类'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"读取失败，请确保工作表名称确认为 'sheet' 且包含'日期'列。错误: {e}")
        return pd.DataFrame()

# ---------- 设计系统 CSS (Apple Inspired) ----------
st.markdown("""
<style>
    /* ----- 导入字体 (SF Pro 风格，用 Inter 替代) ----- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

    /* ----- 全局变量 (Apple 调色板) ----- */
    :root {
        --bg-primary: #f5f5f7;
        --bg-secondary: #ffffff;
        --bg-tertiary: #fbfbfd;
        --text-primary: #1d1d1f;
        --text-secondary: #86868b;
        --text-tertiary: #6e6e73;
        --border-light: rgba(0, 0, 0, 0.04);
        --border-medium: rgba(0, 0, 0, 0.08);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.02), 0 0 0 1px rgba(0, 0, 0, 0.02);
        --shadow-md: 0 8px 20px rgba(0, 0, 0, 0.04), 0 0 0 1px rgba(0, 0, 0, 0.02);
        --accent-blue: #0071e3;
        --accent-green: #28cd41;
        --accent-orange: #ff9f0a;
        --accent-purple: #af52de;
        --transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1);
    }

    /* ----- 基础重置 ----- */
    .stApp {
        background-color: var(--bg-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ----- 侧边栏：磨砂玻璃效果 (Apple 风格) ----- */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.72) !important;
        backdrop-filter: saturate(180%) blur(20px) !important;
        -webkit-backdrop-filter: saturate(180%) blur(20px) !important;
        border-right: 1px solid var(--border-medium) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    .sidebar-title {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        color: var(--text-primary) !important;
        padding: 1rem 0 0.5rem 0 !important;
        margin-bottom: 1.5rem !important;
        border-bottom: 1px solid var(--border-light) !important;
    }

    /* ----- 下拉菜单 & 单选按钮 (更精致的交互) ----- */
    div[data-baseweb="select"] > div {
        background-color: var(--bg-secondary) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-medium) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: var(--transition) !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 4px 12px rgba(0, 113, 227, 0.08) !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    /* 地域筛选 Radio 样式 */
    div[data-testid="stRadio"] label {
        background: transparent !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        transition: var(--transition) !important;
        font-weight: 450 !important;
    }
    div[data-testid="stRadio"] label:hover {
        background: rgba(0, 0, 0, 0.03) !important;
    }

    /* ----- 统计卡片 (干净、透气) ----- */
    .stat-card {
        background: var(--bg-secondary);
        padding: 1.75rem 0.5rem;
        border-radius: 20px;
        box-shadow: var(--shadow-sm);
        text-align: center;
        border: 1px solid var(--border-light);
        transition: var(--transition);
        backdrop-filter: blur(8px);
    }
    .stat-card:hover {
        box-shadow: var(--shadow-md);
        transform: scale(1.01);
    }
    .stat-val {
        font-size: 2.8rem;
        font-weight: 600;
        letter-spacing: -0.03em;
        color: var(--text-primary);
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }
    .stat-label {
        color: var(--text-secondary);
        font-weight: 450;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }

    /* ----- 信息流卡片 (主要视觉焦点) ----- */
    .feed-card {
        display: flex;
        background: var(--bg-secondary);
        padding: 1.75rem;
        border-radius: 24px;
        margin-bottom: 1.25rem;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        backdrop-filter: blur(8px);
    }
    .feed-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--border-medium);
    }

    .card-icon-area {
        flex-shrink: 0;
        width: 64px;
        height: 64px;
        border-radius: 18px;
        margin-right: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-light);
    }

    .card-title-main {
        font-size: 1.25rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        line-height: 1.4;
    }

    .feature-block {
        background-color: var(--bg-tertiary);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0 0.5rem 0;
        border: 1px solid var(--border-light);
    }

    .feature-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.4rem;
        display: block;
    }

    .feature-content {
        font-size: 0.95rem;
        color: var(--text-primary);
        font-weight: 450;
        line-height: 1.5;
    }

    .meta-text {
        font-size: 0.8rem;
        color: var(--text-tertiary);
        font-weight: 400;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* ----- 标签页 (Tab) 风格统一 ----- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid var(--border-light);
        padding-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        color: var(--text-tertiary);
        padding: 0.5rem 0.25rem;
        border-radius: 0;
        transition: var(--transition);
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-blue) !important;
        border-bottom: 2px solid var(--accent-blue);
        font-weight: 600;
    }

    /* ----- 标题区 ----- */
    h1 {
        font-weight: 650 !important;
        letter-spacing: -0.02em !important;
        color: var(--text-primary) !important;
        margin-bottom: 1.5rem !important;
    }

    /* ----- 空状态优化 ----- */
    .stInfo, .stWarning {
        background: var(--bg-secondary) !important;
        border-radius: 20px !important;
        border: 1px solid var(--border-light) !important;
        box-shadow: var(--shadow-sm) !important;
        padding: 2rem !important;
        color: var(--text-secondary) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 侧边栏控件 ----------
st.sidebar.markdown('<p class="sidebar-title">⚡ AI Sentinel</p>', unsafe_allow_html=True)

all_data = load_all_data()

if not all_data.empty:
    month_options = sorted(all_data['选择月份'].unique().tolist(), reverse=True)
    selected_month = st.sidebar.selectbox("📅 选择月份", month_options)
    df = all_data[all_data['选择月份'] == selected_month].copy()

    region_col = next((c for c in df.columns if c in ['地域', '地区']), None)
    if region_col:
        region_options = ["全部地区"] + sorted(df[region_col].unique().tolist())
        selected_region = st.sidebar.radio("🌏 地域筛选", region_options, index=0)
        if selected_region != "全部地区":
            df = df[df[region_col] == selected_region]

    # ---------- 主内容区 ----------
    st.title("月度 AI 进展 · 动态看板")

    # 统计卡片行 (四列)
    c1, c2, c3, c4 = st.columns(4)
    cat_col = '分类' if '分类' in df.columns else None
    if cat_col:
        infra_n = len(df[df[cat_col] == '基建'])
        app_n = len(df[df[cat_col] == '应用'])
        fin_n = len(df[df[cat_col] == '金融'])
    else:
        infra_n = app_n = fin_n = 0

    with c1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-val">{len(df)}</div>
                <div class="stat-label">📊 总计</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-val">{infra_n}</div>
                <div class="stat-label">🏗️ 基建</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-val">{app_n}</div>
                <div class="stat-label">🎨 应用</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-val">{fin_n}</div>
                <div class="stat-label">💰 金融</div>
            </div>
        """, unsafe_allow_html=True)

    # 标签页切换
    tabs = st.tabs(["🔥 全部动态", "🏗️ 基建", "🎨 应用", "💰 金融"])

    def render_feed(data):
        if data.empty:
            st.info("✨ 当前筛选条件下暂无数据，可调整月份或地域。")
            return
        for _, row in data.iterrows():
            cat = row.get('分类', '未分类')
            # 根据分类设置图标和强调色
            if cat == "基建":
                icon, accent_color = "🏗️", "var(--accent-blue)"
            elif cat == "金融":
                icon, accent_color = "💰", "var(--accent-orange)"
            else:
                icon, accent_color = "🎨", "var(--accent-green)"

            month_str = f"{row['日期'].year}年{row['日期'].month}月"
            company_key = next((k for k in ['公司', 'Company', '企业'] if k in row), '公司')
            company_name = row.get(company_key, '未知公司')
            progress = row.get('进展', '暂无进展说明')
            feature = row.get('核心特点', '暂无描述')
            feedback = row.get('市场反响', '暂无评价')

            st.markdown(f"""
                <div class="feed-card">
                    <div class="card-icon-area" style="color: {accent_color};">
                        {icon}
                    </div>
                    <div style="flex-grow: 1;">
                        <div class="meta-text" style="margin-bottom: 0.25rem;">
                            <span>📅 {month_str}</span>
                            <span style="margin: 0 8px;">·</span>
                            <span style="font-weight: 500;">{cat}</span>
                        </div>
                        <div class="card-title-main">
                            {company_name}：{progress}
                        </div>
                        <div class="feature-block">
                            <span class="feature-label">✨ 核心特点</span>
                            <div class="feature-content">{feature}</div>
                        </div>
                        <div class="meta-text" style="margin-top: 0.5rem;">
                            💬 {feedback}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    if cat_col:
        with tabs[0]:
            render_feed(df)
        with tabs[1]:
            render_feed(df[df[cat_col] == '基建'])
        with tabs[2]:
            render_feed(df[df[cat_col] == '应用'])
        with tabs[3]:
            render_feed(df[df[cat_col] == '金融'])
    else:
        st.warning("⚠️ 数据中未检测到“分类”列，无法按类别筛选。")

else:
    st.info("📭 等待数据接入 — 请在 Google Sheet 中创建一个名为 `sheet` 的工作表，并确保包含 `日期`、`分类` 等字段。")
