import streamlit as st
import pandas as pd
import urllib.parse
import requests
import re

# ---------------- 页面配置 ----------------
st.set_page_config(
    page_title="AI Sentinel",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

GSHEET_URL = st.secrets.get("gsheet_url", "")

# ---------------- 获取 Sheet 名 ----------------
@st.cache_data(ttl=300)
def get_all_sheet_names_automatically(url):
    sheet_id = url.split('/d/')[1].split('/')[0]
    html = requests.get(
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/htmlview"
    ).text
    sheets = re.findall(r'class="sheet-name">([^<]+)', html)
    return [s.strip() for s in sheets]

def get_gsheet_download_url(url, sheet_name):
    base_url = url.split('/edit')[0]
    return f"{base_url}/export?format=csv&sheet={urllib.parse.quote(sheet_name)}"

# ---------------- 样式 ----------------
st.markdown("""
<style>
.stApp { background-color: #f6f8fa; }
.stat-card { background:white;padding:20px;border-radius:12px;text-align:center }
.feed-card { background:white;padding:20px;border-radius:16px;margin-bottom:16px }
</style>
""", unsafe_allow_html=True)

# ---------------- 读取所有 Sheet ----------------
@st.cache_data(ttl=300)
def load_all_sheets_data(sheet_names):
    all_df = []

    for sheet in sheet_names:
        try:
            csv_url = get_gsheet_download_url(GSHEET_URL, sheet)
            df = pd.read_csv(csv_url)
            df.columns = df.columns.astype(str).str.strip()

            # ✅ 强制加 SheetName
            df["SheetName"] = sheet

            # 日期处理
            if "日期" in df.columns:
                df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
                df = df.dropna(subset=["日期"])

            # 分类标准化（AI应用）
            df["分类_std"] = df["分类"].astype(str)
            df.loc[df["分类_std"].str.contains("基建"), "分类_std"] = "基建"
            df.loc[df["分类_std"].str.contains("AI应用"), "分类_std"] = "AI应用"
            df.loc[df["分类_std"].str.contains("金融"), "分类_std"] = "金融"

            all_df.append(df)

        except Exception as e:
            st.warning(f"Sheet {sheet} 加载失败: {e}")

    if len(all_df) == 0:
        return pd.DataFrame()

    return pd.concat(all_df, ignore_index=True)

# ---------------- Sidebar ----------------
st.sidebar.title("📑 AI Sentinel")

if not GSHEET_URL:
    st.sidebar.error("请配置 gsheet_url")
    st.stop()

all_sheets = get_all_sheet_names_automatically(GSHEET_URL)

selected_month = st.sidebar.selectbox(
    "📅 选择月份",
    ["全部"] + all_sheets
)

# ---------------- 主逻辑 ----------------
df_all = load_all_sheets_data(all_sheets)

# ✅ 兜底：如果没有 SheetName 列，直接全部显示
if "SheetName" not in df_all.columns:
    st.error("数据中不存在 SheetName 列，请检查 load_all_sheets_data")
    st.write(df_all.head())
    st.stop()

if selected_month != "全部":
    df = df_all[df_all["SheetName"] == selected_month]
else:
    df = df_all.copy()

st.title("🚀 AI Weekly Insights")

if df.empty:
    st.warning("⚠️ 当前月份无数据")
    st.write("当前月份:", selected_month)
    st.write("已有 SheetName:", df_all["SheetName"].unique())
    st.stop()

# ---------------- 地域筛选 ----------------
region_col = "地域"
regions = ["全部地区"] + sorted(df[region_col].dropna().unique())
selected_region = st.sidebar.radio("🌏 地域筛选", regions)

if selected_region != "全部地区":
    df = df[df[region_col] == selected_region]

# ---------------- 统计 ----------------
infra_n = len(df[df["分类_std"] == "基建"])
app_n = len(df[df["分类_std"] == "AI应用"])
fin_n = len(df[df["分类_std"] == "金融"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL", len(df))
c2.metric("🏗️ 基建", infra_n)
c3.metric("🎨 AI应用", app_n)
c4.metric("💰 金融", fin_n)

tabs = st.tabs(["🔥 全部", "🏗️ 基建", "🎨 AI应用", "💰 金融"])

def render_feed(data):
    if data.empty:
        st.info("暂无数据")
        return

    for _, row in data.iterrows():
        st.markdown(f"""
        <div class="feed-card">
        <b>{row['公司']}</b> ｜ {row['日期'].strftime('%Y-%m-%d')} ｜ {row['分类_std']} ｜ {row['地域']}<br>
        <b>进展：</b>{row['进展']}<br>
        <b>核心特点：</b>{row['核心特点']}<br>
        <b>市场反响：</b>{row['市场反响']}
        </div>
        """, unsafe_allow_html=True)

with tabs[0]:
    render_feed(df)

with tabs[1]:
    render_feed(df[df["分类_std"] == "基建"])

with tabs[2]:
    render_feed(df[df["分类_std"] == "AI应用"])

with tabs[3]:
    render_feed(df[df["分类_std"] == "金融"])
