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

# --- 3. 数据加载 ---
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

# --- 4. 视觉样式 (侧边栏下拉框改为浅色背景+黑色文字) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f6f8fa; }
    
  
    [data-testid="stSidebar"] { background-color: #0d1117 !important; }
    [data-testid="stSidebar"] * { color: #f0f6fc !important; }
    .sidebar-title { color: #00c897 !important; font-size: 1.5rem; font-weight: 800; margin-bottom: 20px; }

  
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important; 
        border-radius: 8px !important;
        border: none !important;
    }
    

    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: #000000 !important; 
        font-weight: 700 !important; 
    }

   
    div[data-testid="stSelectbox"] svg {
        fill: #000000 !important; 
    }

  
    div[data-baseweb="popover"] ul {
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] li {
        color: #000000 !important; 
    }
    /* -------------------------------------- */

    .stat-card { background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid #eef2f6; }
    .stat-val { font-size: 2.2rem; font-weight: 800; color: #1a1e26; }
    .feed-card { display: flex; background: white; padding: 30px; border-radius: 20px; margin-bottom: 25px; border: 1px solid #eef2f6; transition: transform 0.3s ease; }
    .feed-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }
    .card-icon-area { flex-shrink: 0; width: 80px; height: 80px; border-radius: 16px; margin-right: 25px; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; }
    .card-title-main { font-size: 1.4rem; font-weight: 800; color: #111827; margin-bottom: 12px; }
    .feature-block { background-color: #f8fafc; border-radius: 12px; padding: 18px; margin-bottom: 15px; border: 1px solid #eef2f6; }
    .feature-label { font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 5px; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. 侧边栏与过滤逻辑 ---
st.sidebar.markdown('<p class="sidebar-title">📑 AI报告</p>', unsafe_allow_html=True)

all_data = load_all_data()

if not all_data.empty:

    month_options = sorted(all_data['选择月份'].unique().tolist(), reverse=True)
    selected_month = st.sidebar.selectbox("📅 选择月份", month_options)

    df = all_data[all_data['选择月份'] == selected_month].copy()

    region_col = next((c for c in df.columns if c in ['地域', '地区']), None)
    if region_col:
        region_options = ["全部地区"] + sorted(df[region_col].unique().tolist())
        selected_region = st.sidebar.radio("🌏 地域筛选", region_options)
        if selected_region != "全部地区":
            df = df[df[region_col] == selected_region]

    # --- 6. 主页面渲染 ---
    st.title("🚀 AI Monthly Insights")


    c1, c2, c3, c4 = st.columns(4)
    cat_col = '分类' if '分类' in df.columns else None
    infra_n = len(df[df[cat_col].str.contains('基建', na=False)]) if cat_col else 0
    app_n = len(df[df[cat_col].str.contains('应用', na=False)]) if cat_col else 0
    fin_n = len(df[df[cat_col].str.contains('金融', na=False)]) if cat_col else 0
    
    c1.markdown(f'<div class="stat-card"><div class="stat-val">{len(df)}</div><div style="color:#94a3b8">TOTAL</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-val">{infra_n}</div><div style="color:#94a3b8">🏗️ INFRA</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-val">{app_n}</div><div style="color:#94a3b8">🎨 APPS</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-val">{fin_n}</div><div style="color:#94a3b8">💰 FINANCE</div></div>', unsafe_allow_html=True)


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
