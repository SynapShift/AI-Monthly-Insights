import streamlit as st
import pandas as pd
import urllib.parse
import requests
import io
import re

# 1. Page Config

st.set_page_config(
page_title="AI Sentinel",
layout="wide",
initial_sidebar_state="expanded",
page_icon="⚡"
)

# 2. Secret URL

GSHEET_URL = st.secrets.get("gsheet_url", "")

# 3. Get Sheet Names

@st.cache_data(ttl=300)
def get_all_sheet_names_automatically(url):
if not url:
return ["No URL Configured"]
try:
sheet_id = url.split('/d/')[1].split('/')[0]
html_res = requests.get(f"[https://docs.google.com/spreadsheets/d/](https://docs.google.com/spreadsheets/d/){sheet_id}/htmlview", timeout=10)
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
return ["No Sheets Found"]
except Exception as e:
return [f"Error: {str(e)[:20]}"]

# 4. Load Data

@st.cache_data(ttl=60)
def load_data_from_gsheet(url, sheet_name):
if not url or not sheet_name or "No" in sheet_name:
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

# 5. CSS Styles

st.markdown("""
<style>
@import url('[https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap)');
html, body { font-family: 'Inter', sans-serif; }
.stApp { background-color: #f6f8fa; }
[data-testid="stSidebar"] { background-color: #0d1117 !important; }
[data-testid="stSidebar"] * { color: #f0f6fc !important; }
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

# 6. Sidebar

st.sidebar.title("📑 AI Sentinel")
if GSHEET_URL:
all_sheets = get_all_sheet_names_automatically(GSHEET_URL)
selected_month = st.sidebar.selectbox("📅 Month", all_sheets)
if st.sidebar.button("🔄 Refresh Data"):
st.cache_data.clear()
st.rerun()
else:
st.sidebar.warning("Please set gsheet_url in Secrets")
selected_month = None

# 7. Main Page

st.title("🚀 AI Weekly Insights")
if selected_month and "No" not in selected_month:
df = load_data_from_gsheet(GSHEET_URL, selected_month)
if not df.empty:
region_col = next((c for c in df.columns if c in ['地域', '地区']), None)
selected_region = "全部地区"
if region_col:
region_options = ["全部地区"] + sorted(df[region_col].unique().tolist())
selected_region = st.sidebar.radio("🌏 Region", region_options)
if selected_region != "全部地区":
df = df[df[region_col] == selected_region]

```
    cat_col = '分类' if '分类' in df.columns else None
    c1, c2, c3, c4 = st.columns(4)
    infra_n = len(df[df[cat_col].str.contains('基建', na=False)]) if cat_col else 0
    app_n = len(df[df[cat_col].str.contains('应用', na=False)]) if cat_col else 0
    fin_n = len(df[df[cat_col].str.contains('金融', na=False)]) if cat_col else 0
    
    c1.markdown(f'<div class="stat-card"><div class="stat-val">{len(df)}</div><div style="color:#94a3b8">TOTAL</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-val">{infra_n}</div><div style="color:#94a3b8">INFRA</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-val">{app_n}</div><div style="color:#94a3b8">APPS</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-val">{fin_n}</div><div style="color:#94a3b8">FINANCE</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🔥 All", "🏗️ Infra", "🎨 Apps", "💰 Finance"])
    
    def render_feed(data):
        if data.empty:
            st.info("No data available")
            return
        for _, row in data.iterrows():
            cat = str(row.get('分类', 'Other'))
            icon, color = ("🏗️", "#0088cc") if "基建" in cat else (("💰", "#dd9900") if "金融" in cat else ("🎨", "#00c897"))
            reg = f" | {row[region_col]}" if region_col else ""
            company_key = next((k for k in ['公司', 'Company', '企业'] if k in row), '公司')
            date_str = row['日期'].strftime('%Y-%m-%d') if hasattr(row['日期'], 'strftime') else str(row['日期'])
            
            st.markdown(f"""
                <div class="feed-card">
                    <div class="card-icon-area" style="background-color:{color}15; color:{color};">{icon}</div>
                    <div style="flex-grow:1">
                        <div style="display:flex; justify-content:space-between; color:#94a3b8; font-size:0.8rem; margin-bottom:5px;">
                            <span>📅 {date_str}</span>
                            <span>{cat}{reg}</span>
                        </div>
                        <div class="card-title-main">{row.get(company_key, 'Unknown')}：{row.get('进展', '')}</div>
                        <div class="feature-block">
                            <span class="feature-label">💡 Features</span>
                            <div style="font-size:0.95rem; color:#334155;">{row.get('核心特点', '')}</div>
                        </div>
                        <div style="font-size:0.85rem; color:#64748b;">💬 {row.get('市场反响', '')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with tabs[0]: render_feed(df)
    with tabs[1]: render_feed(df[df['分类'].str.contains('基建', na=False)]) if cat_col else None
    with tabs[2]: render_feed(df[df['分类'].str.contains('应用', na=False)]) if cat_col else None
    with tabs[3]: render_feed(df[df['分类'].str.contains('金融', na=False)]) if cat_col else None
else:
    st.warning("No data found in this sheet.")

```

else:
st.info("Please select a month in the sidebar.")

