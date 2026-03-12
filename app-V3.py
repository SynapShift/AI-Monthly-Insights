import streamlit as st
import pandas as pd
import urllib.parse
import requests

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="AI Sentinel - 自动化版",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# --- 2. 配置读取 ---
GSHEET_URL = st.secrets.get("gsheet_url", "")

# --- 3. 核心数据加载 (仅读取第一页) ---
@st.cache_data(ttl=300)
def load_raw_data():
    """直接读取 Google Sheet 的第一张工作表"""
    if not GSHEET_URL:
        return pd.DataFrame()
    try:
        # 将 /edit 结尾改为 /export?format=csv 即可默认下载第一页
        base_url = GSHEET_URL.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv"
        
        df = pd.read_csv(csv_url)
        # 清洗列名
        df.columns = df.columns.astype(str).str.strip()
        
        # 处理日期
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            df = df.dropna(subset=['日期'])
            # 【新增：生成月份字段用于筛选】
            df['月份筛选'] = df['日期'].dt.strftime('%Y-%m')
            df = df.sort_values('日期', ascending=False)
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()

# --- 4. 视觉样式 (保留原有 UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f6f8fa; }
    [data-testid="stSidebar"] { background-color: #0d1117 !important; }
    [data-testid="stSidebar"] * { color: #f0f6fc !important; }
    .sidebar-title { color: #00c897 !important; font-size: 1.5rem; font-weight: 800; margin-bottom: 20px; }
    .stat-card { background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid #eef2f6; }
    .stat-val { font-size: 2.2rem; font-weight: 800; color: #1a1e26; }
    .feed-card { display: flex; background: white; padding: 30px; border-radius: 20px; margin-bottom: 25px; border: 1px solid #eef2f6; box-shadow: 0 4px 10px rgba(0,0,0,0.03); transition: transform 0.3s ease; }
    .feed-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }
    .card-icon-area { flex-shrink: 0; width: 80px; height: 80px; border-radius: 16px; margin-right: 25px; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; }
    .card-title-main { font-size: 1.4rem; font-weight: 800; color: #111827; margin-bottom: 12px; }
    .feature-block { background-color: #f8fafc; border-radius: 12px; padding: 18px; margin-bottom: 15px; border: 1px solid #eef2f6; }
    .feature-label { font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 5px; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. 侧边栏与逻辑处理 ---
st.sidebar.markdown('<p class="sidebar-title">📑 AI Sentinel</p>', unsafe_allow_html=True)

raw_df = load_raw_data()

if not raw_df.empty:
    # --- 【新增：左侧月份筛选】 ---
    month_list = sorted(raw_df['月份筛选'].unique().tolist(), reverse=True)
    selected_month = st.sidebar.selectbox("📅 选择月份", month_list)
    
    # 根据月份过滤数据
    df = raw_df[raw_df['月份筛选'] == selected_month].copy()

    # 地域筛选
    region_col = next((c for c in df.columns if c in ['地域', '地区']), None)
    if region_col:
        region_options = ["全部地区"] + sorted(df[region_col].unique().tolist())
        selected_region = st.sidebar.radio("🌏 地域筛选", region_options)
        if selected_region != "全部地区":
            df = df[df[region_col] == selected_region]

    # --- 6. 主页面渲染 ---
    st.title(f"🚀 AI Insights - {selected_month}")

    # 统计卡片渲染
    c1, c2, c3, c4 = st.columns(4)
    cat_col = '分类' if '分类' in df.columns else None
    
    if cat_col:
        infra_n = len(df[df[cat_col].str.contains('基建', na=False)])
        app_n = len(df[df[cat_col].str.contains('应用', na=False)])
        fin_n = len(df[df[cat_col].str.contains('金融', na=False)])
    else:
        infra_n = app_n = fin_n = 0
    
    c1.markdown(f'<div class="stat-card"><div class="stat-val">{len(df)}</div><div style="color:#94a3b8">TOTAL</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-val">{infra_n}</div><div style="color:#94a3b8">🏗️ INFRA</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-val">{app_n}</div><div style="color:#94a3b8">🎨 APPS</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-val">{fin_n}</div><div style="color:#94a3b8">💰 FINANCE</div></div>', unsafe_allow_html=True)

    # 内容显示函数
    def render_feed(data):
        if data.empty:
            st.info("当前条件下暂无数据")
            return
        for _, row in data.iterrows():
            cat = str(row['分类']) if '分类' in row else "未分类"
            icon, color = ("🏗️", "#0088cc") if "基建" in cat else (("💰", "#dd9900") if "金融" in cat else ("🎨", "#00c897"))
            reg = f" | {row[region_col]}" if region_col else ""
            company_key = next((k for k in ['公司', 'Company', '企业'] if k in row), '公司')
            date_val = row['日期'].strftime('%Y-%m-%d')
            
            st.markdown(f"""
                <div class="feed-card">
                    <div class="card-icon-area" style="background-color:{color}15; color:{color};">{icon}</div>
                    <div style="flex-grow:1">
                        <div style="display:flex; justify-content:space-between; color:#94a3b8; font-size:0.8rem; margin-bottom:5px;">
                            <span>📅 {date_val}</span>
                            <span>{cat}{reg}</span>
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

    tabs = st.tabs(["🔥 全部", "🏗️ 基建", "🎨 应用", "💰 金融"])
    with tabs[0]: render_feed(df)
    with tabs[1]: render_feed(df[df[cat_col].str.contains('基建', na=False)]) if cat_col else st.warning("缺失分类列")
    with tabs[2]: render_feed(df[df[cat_col].str.contains('应用', na=False)]) if cat_col else st.warning("缺失分类列")
    with tabs[3]: render_feed(df[df[cat_col].str.contains('金融', na=False)]) if cat_col else st.warning("缺失分类列")

elif not GSHEET_URL:
    st.info("💡 请在 Streamlit 云端后台配置 Secrets 变量 `gsheet_url` 即可看到内容。")
else:
    st.warning("⚠️ 未能从 Google Sheet 读取到有效数据，请确保表格公开且列名包含“日期”。")
