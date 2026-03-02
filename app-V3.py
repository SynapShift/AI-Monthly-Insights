import streamlit as st
import pandas as pd
import urllib.parse
import requests
import json
import re

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="AI Sentinel - 自动化版",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# --- 2. 数据源配置 ---
GSHEET_URL = st.secrets.get("gsheet_url", "")

# --- 3. 自动获取所有 Sheet 名称 ---
@st.cache_data(ttl=300)
def get_all_sheet_names_automatically(url):
    if not url:
        return ["未配置数据源"]
    try:
        sheet_id = url.split('/d/')[1].split('/')[0]
        html_res = requests.get(f"https://docs.google.com/spreadsheets/d/{sheet_id}/htmlview")
        sheets = re.findall(r'class="sheet-name">([^<]+)', html_res.text)
        if sheets:
            return sheets
        return ["2026年2月"]
    except Exception:
        return ["2026年2月"]

def get_gsheet_download_url(url, sheet_name):
    base_url = url.split('/edit')[0]
    encoded_name = urllib.parse.quote(sheet_name)
    return f"{base_url}/export?format=csv&sheet={encoded_name}"

# --- 4. 视觉样式 ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body { font-family: 'Inter', sans-serif; }
.stApp { background-color: #f6f8fa; }

[data-testid="stSidebar"] { background-color: #0d1117 !important; }
[data-testid="stSidebar"] * { color: #f0f6fc !important; }
.sidebar-title { color: #00c897 !important; font-size: 1.5rem; font-weight: 800; margin-bottom: 20px; }

.stat-card {
    background: white; padding: 24px; border-radius: 16px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center;
    border: 1px solid #eef2f6;
}
.stat-val { font-size: 2.2rem; font-weight: 800; color: #1a1e26; }

.feed-card {
    display: flex; background: white; padding: 30px; border-radius: 20px;
    margin-bottom: 25px; border: 1px solid #eef2f6;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    transition: transform 0.3s ease;
}
.feed-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }
.card-icon-area {
    flex-shrink: 0; width: 80px; height: 80px; border-radius: 16px;
    margin-right: 25px; display: flex; align-items: center; justify-content: center;
    font-size: 2.5rem;
}
.card-title-main { font-size: 1.4rem; font-weight: 800; color: #111827; margin-bottom: 12px; }
.feature-block { background-color: #f8fafc; border-radius: 12px; padding: 18px; margin-bottom: 15px; border: 1px solid #eef2f6; }
.feature-label { font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 5px; display: block; }
</style>
""", unsafe_allow_html=True)

# --- 5. 读取所有 Sheet 数据 ---
@st.cache_data(ttl=300)
def load_all_sheets_data(sheet_names):
    if not GSHEET_URL:
        return pd.DataFrame()

    all_df = []

    for sheet in sheet_names:
        try:
            csv_url = get_gsheet_download_url(GSHEET_URL, sheet)
            df = pd.read_csv(csv_url)
            df.columns = df.columns.astype(str).str.strip()
            df["SheetName"] = sheet

            if '日期' in df.columns:
                df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
                df = df.dropna(subset=['日期']).sort_values('日期', ascending=False)

            all_df.append(df)
        except Exception as e:
            st.warning(f"Sheet {sheet} 加载失败: {e}")

    if all_df:
        return pd.concat(all_df, ignore_index=True)
    return pd.DataFrame()

# --- 6. Sidebar ---
st.sidebar.markdown('<p class="sidebar-title">📑 AI Sentinel</p>', unsafe_allow_html=True)

if GSHEET_URL:
    all_sheets = get_all_sheet_names_automatically(GSHEET_URL)
    selected_month = st.sidebar.selectbox("📅 选择月份", ["全部"] + all_sheets)
else:
    st.sidebar.error("请在 Streamlit Secrets 中配置 gsheet_url")
    selected_month = None

# --- 7. 主页面 ---
st.title("🚀 AI Weekly Insights")

if GSHEET_URL:
    df_all = load_all_sheets_data(all_sheets)

    if selected_month != "全部":
        df = df_all[df_all["SheetName"] == selected_month]
    else:
        df = df_all.copy()

    if not df.empty:

        # 地域筛选
        region_col = next((c for c in df.columns if c in ['地域', '地区']), None)
        selected_region = "全部地区"
        if region_col:
            region_options = ["全部地区"] + sorted(df[region_col].dropna().unique().tolist())
            selected_region = st.sidebar.radio("🌏 地域筛选", region_options)
            if selected_region != "全部地区":
                df = df[df[region_col] == selected_region]

        # 分类统计
        cat_col = '分类' if '分类' in df.columns else None
        if cat_col:
            infra_n = len(df[df[cat_col].str.contains('基建', na=False)])
            app_n = len(df[df[cat_col].str.contains('应用', na=False)])
            fin_n = len(df[df[cat_col].str.contains('金融', na=False)])
        else:
            infra_n = app_n = fin_n = 0

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="stat-card"><div class="stat-val">{len(df)}</div><div>TOTAL</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stat-card"><div class="stat-val">{infra_n}</div><div>🏗️ INFRA</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stat-card"><div class="stat-val">{app_n}</div><div>🎨 APPS</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="stat-card"><div class="stat-val">{fin_n}</div><div>💰 FINANCE</div></div>', unsafe_allow_html=True)

        tabs = st.tabs(["🔥 全部", "🏗️ 基建", "🎨 应用", "💰 金融"])

        def render_feed(data):
            if data.empty:
                st.info("当前条件下暂无数据")
                return

            for _, row in data.iterrows():
                cat = str(row.get('分类', '未分类'))
                icon, color = ("🏗️", "#0088cc") if "基建" in cat else (("💰", "#dd9900") if "金融" in cat else ("🎨", "#00c897"))
                reg = f" | {row[region_col]}" if region_col else ""

                company_key = next((k for k in ['公司', 'Company', '企业'] if k in row), '公司')
                date_val = row['日期'].strftime('%Y-%m-%d') if hasattr(row['日期'], 'strftime') else row['日期']

                st.markdown(f"""
                <div class="feed-card">
                    <div class="card-icon-area" style="background-color:{color}15; color:{color};">{icon}</div>
                    <div style="flex-grow:1">
                        <div style="display:flex; justify-content:space-between; color:#94a3b8; font-size:0.8rem;">
                            <span>📅 {date_val}</span>
                            <span>{cat}{reg}</span>
                        </div>
                        <div class="card-title-main">{row.get(company_key,'未知公司')}：{row.get('进展','暂无进展说明')}</div>
                        <div class="feature-block">
                            <span class="feature-label">💡 核心特点</span>
                            <div>{row.get('核心特点','暂无描述')}</div>
                        </div>
                        <div style="font-size:0.85rem; color:#64748b;">💬 {row.get('市场反响','暂无评价')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with tabs[0]:
            render_feed(df)
        with tabs[1]:
            render_feed(df[df['分类'].str.contains('基建', na=False)]) if cat_col else st.warning("未找到分类列")
        with tabs[2]:
            render_feed(df[df['分类'].str.contains('应用', na=False)]) if cat_col else st.warning("未找到分类列")
        with tabs[3]:
            render_feed(df[df['分类'].str.contains('金融', na=False)]) if cat_col else st.warning("未找到分类列")

    else:
        st.warning("⚠️ 当前筛选条件下无数据")

else:
    st.info("💡 请在 Streamlit Secrets 中配置 gsheet_url")
