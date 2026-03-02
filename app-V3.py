--- 1. 页面配置 ---
import streamlit as st
import pandas as pd
import urllib.parse
import requests
import io
import re

st.set_page_config(
page_title="AI Sentinel - 自动化版",
layout="wide",
initial_sidebar_state="expanded",
page_icon="⚡"
)

--- 2. 隐藏数据源配置 ---
GSHEET_URL = st.secrets.get("gsheet_url", "")

--- 3. 核心函数：动态获取所有工作表名称 ---
@st.cache_data(ttl=300)
def get_all_sheet_names_automatically(url):
if not url:
return ["未配置数据源"]
try:
sheet_id = url.split('/d/')[1].split('/')[0]
html_res = requests.get(f"{sheet_id}/htmlview", timeout=10)
sheets = re.findall(r'class="sheet-name">([^\<]+)', html_res.text)
if not sheets:
sheets = re.findall(r'"name":"([^\\"]+)"', html_res.text)
forbidden = ['Inner', 'top', 'bottom', 'true', 'false', 'Summary', 'Sheet1']
sheets = [s for s in sheets if s not in forbidden and not s.startswith('Print_')]
if sheets:
unique_sheets = []
for s in sheets:
if s not in unique_sheets:
unique_sheets.append(s)
return unique_sheets
return ["未检测到有效工作表"]
except Exception as e:
return [f"连接错误: {str(e)[:20]}"]

--- 4. 核心函数：精准读取指定工作表 ---
@st.cache_data(ttl=60)
def load_data_from_gsheet(url, sheet_name):
if not url or not sheet_name or "未检测" in sheet_name:
return pd.DataFrame()
try:
base_url = url.split('/edit')[0]
encoded_name = urllib.parse.quote(sheet_name)
csv_url = f"{base_url}/export?format=csv&sheet={encoded_name}"
response = requests.get(csv_url, timeout=10)
if response.status_code == 200:
df = pd.read_csv(io.StringIO(response.text))
df.columns = df.columns.astype(str).str.strip()
if '日期' in df.columns:
df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
df = df.dropna(subset=['日期']).sort_values('日期', ascending=False)
return df
return pd.DataFrame()
except Exception:
return pd.DataFrame()

--- 5. 视觉样式 ---
st.markdown("""
<style>
@import url('');
html, body { font-family: 'Inter', sans-serif; }
.stApp { background-color: #f6f8fa; }
[data-testid="stSidebar"] { background-color: #0d1117 !important; }
[data-testid="stSidebar"] * { color: #f0f6fc !important; }
div[data-testid="stRadio"] label p { color: #f0f6fc !important; font-weight: 500; }
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

--- 6. 侧边栏交互 ---
st.sidebar.markdown('<p class="sidebar-title">📑 AI Sentinel</p>', unsafe_allow_html=True)

if GSHEET_URL:
all_sheets = get_all_sheet_names_automatically(GSHEET_URL)
selected_month = st.sidebar.selectbox("📅 选择月份", all_sheets)
if st.sidebar.button("🔄 刷新数据列表"):
st.cache_data.clear()
st.rerun()
else:
st.sidebar.warning("⚠️ 请在 Secrets 中配置 gsheet_url")
selected_month = None

--- 7. 主页面渲染 ---
st.title("🚀 AI Weekly Insights")

if selected_month and "未检测" not in selected_month:
df = load_data_from_gsheet(GSHEET_URL, selected_month)
if not df.empty:
region_col = next((c for c in df.columns if c in ['地域', '地区']), None)
selected_region = "全部地区"
if region_col:
region_options = ["全部地区"] + sorted(df[region_col].unique().tolist())
selected_region = st.sidebar.radio("🌏 地域筛选", region_options)
if selected_region != "全部地区":
df = df[df[region_col] == selected_region]

else:
st.info("💡 请选择月份。")
