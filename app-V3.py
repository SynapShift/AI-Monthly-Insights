import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(
    page_title="AI Sentinel",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚡"
)

# ========= 样式（克制版，不会炸） =========
st.markdown("""
<style>
.stApp {
    background: #f8fafc;
}

/* 卡片 */
.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.card:hover {
    border-color: #cbd5e1;
}

/* 标题 */
.title {
    font-size: 26px;
    font-weight: 700;
}

/* 轻标签 */
.tag {
    padding: 2px 8px;
    border-radius: 8px;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# ========= 数据 =========
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

# ========= Tabs =========
tab1, tab2, tab3 = st.tabs(["📆 月度进展", "🗣️ 博主", "📚 学习资料"])

# ======================
# 📆 月度进展
# ======================
with tab1:

    col1, col2 = st.columns([3,1])

    with col1:
        st.markdown('<div class="title">⚡ AI Sentinel</div>', unsafe_allow_html=True)
        st.caption("Track the signal. Ignore the noise.")

    with col2:
        st.metric("Signals", len(df))

    if df.empty:
        st.info("暂无数据")
        st.stop()

    months = sorted(df['选择月份'].unique(), reverse=True)
    selected_month = st.selectbox("选择月份", months)

    data = df[df['选择月份'] == selected_month]

    # ⭐ Highlight
    top = data.iloc[0]
    st.success(f"🚨 今日重点：{top.get('公司')}")

    # 列表
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

            c1, c2 = st.columns([6,2])

            with c1:
                st.markdown(f"**{row.get('公司','未知公司')}**")
                st.caption(row['日期'].strftime("%Y-%m-%d"))

            with c2:
                st.markdown(
                    f'<span class="tag" style="background:{color}20;color:{color}">{cat}</span>',
                    unsafe_allow_html=True
                )

            st.write(row.get("进展",""))

            st.info(f"✨ {row.get('核心特点','')}")

            if pd.notna(row.get("市场反响")):
                st.caption(f"💬 {row.get('市场反响')}")

            st.markdown('</div>', unsafe_allow_html=True)

# ======================
# 🗣️ 博主
# ======================
with tab2:

    bloggers = [
        {"name": "Andrej Karpathy", "desc": "从零训练LLM项目"},
        {"name": "李沐", "desc": "D2L更新"},
    ]

    cols = st.columns(2)

    for i, b in enumerate(bloggers):
        with cols[i % 2]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**{b['name']}**")
            st.write(b['desc'])
            st.markdown('</div>', unsafe_allow_html=True)

# ======================
# 📚 学习资料
# ======================
with tab3:

    resources = [
        {"title": "D2L", "desc": "深度学习教材"},
        {"title": "HF Course", "desc": "NLP课程"},
        {"title": "FastAI", "desc": "实战课程"},
    ]

    cols = st.columns(3)

    for i, r in enumerate(resources):
        with cols[i % 3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**{r['title']}**")
            st.write(r['desc'])
            st.markdown('</div>', unsafe_allow_html=True)
