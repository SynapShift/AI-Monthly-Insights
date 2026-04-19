import streamlit as st
import pandas as pd
import urllib.parse

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="AI Sentinel",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚡"
)

# ---------- 全局样式 ----------
st.markdown("""
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
    }

    .stApp {
        background: #f8fafc;
    }

    header, footer {visibility: hidden;}

    .block-container {
        max-width: 960px;
        padding-top: 2rem;
    }

    /* 卡片 */
    .feed-item {
        background:white;
        border:1px solid #e2e8f0;
        border-radius:16px;
        padding:16px 18px;
        margin-bottom:12px;
        transition:all 0.2s ease;
        position:relative;
    }

    .feed-item:hover {
        transform:translateY(-3px);
        box-shadow:0 10px 25px rgba(0,0,0,0.08);
    }

    .company {
        font-size:1.15rem;
        font-weight:700;
    }

    .meta {
        font-size:0.8rem;
        color:#94a3b8;
    }

    .feature {
        background:#f1f5f9;
        padding:10px 12px;
        border-radius:10px;
        margin-top:8px;
        font-size:0.9rem;
    }

    .badge {
        padding:2px 10px;
        border-radius:999px;
        font-size:0.7rem;
        font-weight:600;
    }

</style>
""", unsafe_allow_html=True)

# ---------- 数据 ----------
GSHEET_URL = st.secrets.get("gsheet_url", "")

@st.cache_data(ttl=300)
def load_data():
    if not GSHEET_URL:
        return pd.DataFrame()

    base_url = GSHEET_URL.split('/edit')[0]
    csv_url = f"{base_url}/export?format=csv&sheet=sheet"
    df = pd.read_csv(csv_url)

    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['日期'])
    df = df.sort_values('日期', ascending=False)
    df['选择月份'] = df['日期'].dt.strftime('%Y-%m')

    return df

df = load_data()

# ---------- Hero ----------
st.markdown(f"""
<div style="
display:flex;
justify-content:space-between;
align-items:center;
padding:24px 28px;
border-radius:20px;
background:linear-gradient(135deg,#1e293b,#0f172a);
color:white;
margin-bottom:20px;
">
    <div>
        <div style="font-size:28px;font-weight:700;">⚡ AI Sentinel</div>
        <div style="opacity:0.7;">Track the signal. Ignore the noise.</div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:32px;font-weight:700;">{len(df)}</div>
        <div style="opacity:0.6;">Signals</div>
    </div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.info("没有数据")
    st.stop()

# ---------- 筛选 ----------
months = sorted(df['选择月份'].unique(), reverse=True)
selected_month = st.selectbox("选择月份", months)

filtered = df[df['选择月份'] == selected_month]

# ---------- 今日重点 ----------
top = filtered.iloc[0]

st.markdown(f"""
<div style="
padding:14px 18px;
background:#fee2e2;
border-radius:12px;
font-weight:600;
margin-bottom:16px;
">
🚨 今日最重要信号：{top.get('公司','未知公司')}
</div>
""", unsafe_allow_html=True)

# ---------- 列表 ----------
for _, row in filtered.iterrows():

    cat = row.get('分类', '其他')

    if cat == "基建":
        color = "#2563eb"
    elif cat == "金融":
        color = "#f59e0b"
    else:
        color = "#10b981"

    st.markdown(f"""
    <div class="feed-item">
        <div style="
            position:absolute;
            left:0;
            top:0;
            bottom:0;
            width:4px;
            border-radius:16px 0 0 16px;
            background:{color};
        "></div>

        <div class="company">{row.get('公司','未知公司')}</div>

        <div class="meta">
            {row['日期'].strftime('%Y-%m-%d')} · 
            <span class="badge" style="background:{color}20;color:{color}">
                {cat}
            </span>
        </div>

        <div style="margin-top:6px;font-size:0.95rem;">
            {row.get('进展','')}
        </div>

        <div class="feature">
            ✨ {row.get('核心特点','')}
        </div>

        <div style="margin-top:6px;font-size:0.85rem;color:#64748b;">
            💬 {row.get('市场反响','')}
        </div>
    </div>
    """, unsafe_allow_html=True)
