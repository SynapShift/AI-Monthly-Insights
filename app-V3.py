import streamlit as st
import pandas as pd
import urllib.parse

# ---------- 页面 ----------
st.set_page_config(
    page_title="AI Sentinel",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚡"
)

# ---------- 样式 ----------
st.markdown("""
<style>
.stApp {
    background: #f8fafc;
}

.block-container {
    max-width: 1200px;
}

.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

.card:hover {
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

.badge {
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

.hero {
    padding: 24px;
    border-radius: 20px;
    background: linear-gradient(135deg,#1e293b,#0f172a);
    color: white;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# ---------- 数据 ----------
GSHEET_URL = st.secrets.get("gsheet_url", "")

@st.cache_data
def load():
    if not GSHEET_URL:
        return pd.DataFrame()

    base = GSHEET_URL.split('/edit')[0]
    url = f"{base}/export?format=csv&sheet=sheet"
    df = pd.read_csv(url)

    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['日期'])
    df = df.sort_values('日期', ascending=False)
    df['选择月份'] = df['日期'].dt.strftime('%Y-%m')
    return df

df = load()

# ---------- tabs ----------
tab1, tab2, tab3 = st.tabs(["📆 月度进展", "🗣️ 博主", "📚 学习资料"])

# =============================
# 📆 页面1
# =============================
with tab1:

    st.markdown(f"""
    <div class="hero">
        <h2>⚡ AI Sentinel</h2>
        <p>Track the signal. Ignore the noise.</p>
        <h3>{len(df)} signals</h3>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("无数据")
        st.stop()

    months = sorted(df['选择月份'].unique(), reverse=True)
    m = st.selectbox("月份", months)

    data = df[df['选择月份'] == m]

    # ⭐ 今日重点
    top = data.iloc[0]
    st.warning(f"🚨 今日最重要信号：{top.get('公司')}")

    for _, row in data.iterrows():

        cat = row.get('分类', '其他')

        if cat == "基建":
            color = "#3b82f6"
        elif cat == "金融":
            color = "#f59e0b"
        else:
            color = "#10b981"

        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)

            col1, col2 = st.columns([8,2])

            with col1:
                st.markdown(f"**{row.get('公司','未知')}**")
                st.caption(f"{row['日期'].date()} · {cat}")

            with col2:
                st.markdown(
                    f'<span class="badge" style="background:{color}20;color:{color}">{cat}</span>',
                    unsafe_allow_html=True
                )

            st.write(row.get("进展",""))

            st.markdown(f"""
            <div style="background:#f1f5f9;padding:10px;border-radius:10px;">
            ✨ {row.get("核心特点","")}
            </div>
            """, unsafe_allow_html=True)

            if pd.notna(row.get("市场反响")):
                st.caption(f"💬 {row.get('市场反响')}")

            st.markdown('</div>', unsafe_allow_html=True)

# =============================
# 🗣️ 页面2（恢复）
# =============================
with tab2:

    bloggers = [
        {"name":"Karpathy","desc":"从零训练LLM"},
        {"name":"李沐","desc":"D2L更新"},
    ]

    for b in bloggers:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**{b['name']}**")
            st.write(b['desc'])
            st.markdown('</div>', unsafe_allow_html=True)

# =============================
# 📚 页面3（恢复）
# =============================
with tab3:

    resources = [
        {"title":"D2L","desc":"深度学习教材"},
        {"title":"HF Course","desc":"NLP课程"},
    ]

    cols = st.columns(3)

    for i, r in enumerate(resources):
        with cols[i % 3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**{r['title']}**")
            st.write(r['desc'])
            st.markdown('</div>', unsafe_allow_html=True)
