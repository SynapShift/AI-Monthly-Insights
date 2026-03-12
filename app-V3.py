import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="AI Sentinel - 自动化版",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# --- 2. 配置读取 ---
GSHEET_URL = st.secrets.get("gsheet_url", "")

# --- 3. 核心数据加载 (仅读取名为 'sheet' 的分页) ---
@st.cache_data(ttl=300)
def load_all_data():
    """从名为 'sheet' 的工作表读取所有数据"""
    if not GSHEET_URL:
        return pd.DataFrame()
    try:
        base_url = GSHEET_URL.split('/edit')[0]
        # 指定读取 sheet_name 为 'sheet'
        encoded_name = urllib.parse.quote("sheet")
        csv_url = f"{base_url}/export?format=csv&sheet={encoded_name}"
        
        df = pd.read_csv(csv_url)
        df.columns = df.columns.astype(str).str.strip()
        
        if '日期' in df.columns:
            # 转换日期格式
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            df = df.dropna(subset=['日期'])
            # 【核心逻辑：从日期列生成 YYYY-MM 字段用于左侧筛选】
            df['选择月份'] = df['日期'].dt.strftime('%Y-%m')
            df = df.sort_values('日期', ascending=False)
        return df
    except Exception as e:
        st.error(f"读取失败，请确保工作表名称确认为 'sheet' 且包含'日期'列。错误: {e}")
        return pd.DataFrame()

# --- 4. 视觉样式 (强力覆盖：纯白背景 + 纯黑文字 + 100% 不透明) ---
st.markdown("""
<style>
/* 全局字体与背景保持不变 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body { font-family: 'Inter', sans-serif; }
.stApp { background-color: #f6f8fa; }

/* 侧边栏样式不变 */
[data-testid="stSidebar"] { background-color: #0d1117 !important; }
[data-testid="stSidebar"] * { color: #f0f6fc !important; }
.sidebar-title { color: #00c897 !important; font-size: 1.5rem; font-weight: 800; margin-bottom: 20px; }

/* ========== 核心修复：所有输入框文字强制深色 ========== */
/* 1. 通用输入框 (text_input, number_input, text_area 等) */
div[data-baseweb="input"] input,
div[data-baseweb="input"] textarea,
div[data-baseweb="input"] [data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;  /* Safari/Chrome 强制填充 */
    caret-color: #000000 !important;              /* 光标颜色也改为黑色 */
    background-color: #FFFFFF !important;          /* 背景纯白 */
}

/* 2. 下拉选择框 (selectbox) - 选中后显示的文本 */
div[data-testid="stSelectbox"] div[data-baseweb="select"] span[data-testid="stMarkdownContainer"],
div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
div[data-testid="stSelectbox"] div[data-baseweb="select"] [data-testid="stMarkdownContainer"] {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

/* 3. 下拉框背景和箭头 */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: none !important;
}
div[data-testid="stSelectbox"] svg {
    fill: #000000 !important;
    opacity: 1 !important;
}

/* 4. 下拉选项弹出层 */
div[data-baseweb="popover"] ul {
    background-color: #FFFFFF !important;
}
div[data-baseweb="popover"] li {
    color: #000000 !important;
    background-color: #FFFFFF !important;
}
div[data-baseweb="popover"] li:hover {
    background-color: #f0f0f0 !important;  /* 悬停背景浅灰，文字保持黑 */
    color: #000000 !important;
}

/* 5. 多选框/单选按钮的标签文字（如果有标签） */
div[data-testid="stCheckbox"] label,
div[data-testid="stRadio"] label {
    color: #000000 !important;
}

/* 6. 强制所有输入相关的占位符为深灰色（可选） */
::placeholder {
    color: #555555 !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 5. 侧边栏与过滤逻辑 ---
st.sidebar.markdown('<p class="sidebar-title">📑 AI Sentinel</p>', unsafe_allow_html=True)

all_data = load_all_data()

if not all_data.empty:
    # 获取唯一的月份列表并排序
    month_options = sorted(all_data['选择月份'].unique().tolist(), reverse=True)
    selected_month = st.sidebar.selectbox("📅 选择月份", month_options)
    
    # 根据选择的月份过滤
    df = all_data[all_data['选择月份'] == selected_month].copy()

    # 地域筛选 (保持原样)
    region_col = next((c for c in df.columns if c in ['地域', '地区']), None)
    if region_col:
        region_options = ["全部地区"] + sorted(df[region_col].unique().tolist())
        selected_region = st.sidebar.radio("🌏 地域筛选", region_options)
        if selected_region != "全部地区":
            df = df[df[region_col] == selected_region]

    # --- 6. 主页面渲染 ---
    st.title("🚀 AI Weekly Insights")

    # 统计卡片渲染
    c1, c2, c3, c4 = st.columns(4)
    cat_col = '分类' if '分类' in df.columns else None
    infra_n = len(df[df[cat_col].str.contains('基建', na=False)]) if cat_col else 0
    app_n = len(df[df[cat_col].str.contains('应用', na=False)]) if cat_col else 0
    fin_n = len(df[df[cat_col].str.contains('金融', na=False)]) if cat_col else 0
    
    c1.markdown(f'<div class="stat-card"><div class="stat-val">{len(df)}</div><div style="color:#94a3b8">TOTAL</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-val">{infra_n}</div><div style="color:#94a3b8">🏗️ INFRA</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-val">{app_n}</div><div style="color:#94a3b8">🎨 APPS</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-val">{fin_n}</div><div style="color:#94a3b8">💰 FINANCE</div></div>', unsafe_allow_html=True)

    # Tab 渲染
    tabs = st.tabs(["🔥 全部", "🏗️ 基建", "🎨 应用", "💰 金融"])
    
    def render_feed(data):
        if data.empty:
            st.info("当前月份及条件下暂无数据")
            return
        for _, row in data.iterrows():
            cat = str(row['分类']) if '分类' in row else "未分类"
            icon, color = ("🏗️", "#0088cc") if "基建" in cat else (("💰", "#dd9900") if "金融" in cat else ("🎨", "#00c897"))
            date_val = row['日期'].strftime('%Y-%m-%d')
            company_key = next((k for k in ['公司', 'Company', '企业'] if k in row), '公司')
            
            st.markdown(f"""
                <div class="feed-card">
                    <div class="card-icon-area" style="background-color:{color}15; color:{color};">{icon}</div>
                    <div style="flex-grow:1">
                        <div style="display:flex; justify-content:space-between; color:#94a3b8; font-size:0.8rem; margin-bottom:5px;">
                            <span>📅 {date_val}</span>
                            <span>{cat}</span>
                        </div>
                        <div class="card-title-main">{row.get(company_key, '未知公司')}：{row.get('进展', '暂无进展说明')}</div>
                        <div class="feature-block">
                            <span class="feature-label">💡 核心特点</span>
                            <div style="font-size:0.95rem; color:#334155;">{row.get('核心特点', '暂无描述')}</div>
                        </div>
                        <div style="font-size:0.85rem; color:#64748b;">💬 {row.get('市场反响', '暂无评价')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with tabs[0]: render_feed(df)
    with tabs[1]: render_feed(df[df[cat_col].str.contains('基建', na=False)]) if cat_col else st.warning("未找到分类列")
    with tabs[2]: render_feed(df[df[cat_col].str.contains('应用', na=False)]) if cat_col else st.warning("未找到分类列")
    with tabs[3]: render_feed(df[df[cat_col].str.contains('金融', na=False)]) if cat_col else st.warning("未找到分类列")

else:
    st.info("💡 请确保 Google Sheet 中有一个名为 `sheet` 的工作表，且包含有效数据。")



