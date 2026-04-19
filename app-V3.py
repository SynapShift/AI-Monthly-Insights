import streamlit as st
import pandas as pd
import urllib.parse

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="AI Sentinel · 智能瞭望台",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚡"
)

# ---------- 全局设计系统 (Apple Inspired) ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

    :root {
        --bg-primary: #f5f5f7;
        --bg-secondary: #ffffff;
        --bg-tertiary: #fbfbfd;
        --text-primary: #1d1d1f;
        --text-secondary: #86868b;
        --text-tertiary: #6e6e73;
        --border-light: rgba(0, 0, 0, 0.04);
        --border-medium: rgba(0, 0, 0, 0.08);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.02), 0 0 0 1px rgba(0, 0, 0, 0.02);
        --shadow-md: 0 8px 20px rgba(0, 0, 0, 0.04), 0 0 0 1px rgba(0, 0, 0, 0.02);
        --accent-blue: #0071e3;
        --accent-green: #28cd41;
        --accent-orange: #ff9f0a;
        --accent-purple: #af52de;
        --transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1);
    }

    .stApp {
        background-color: var(--bg-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }

    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
    }

    .page-header {
        margin-bottom: 2.5rem;
        border-bottom: 1px solid var(--border-medium);
        padding-bottom: 1rem;
    }
    .page-header h1 {
        font-weight: 650 !important;
        letter-spacing: -0.02em !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.25rem !important;
    }
    .page-header p {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 400;
    }

    .filter-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.25rem;
    }

    /* 统计按钮默认样式 */
    .stButton > button {
        width: 100%;
        background: var(--bg-secondary);
        border: 1px solid var(--border-light) !important;
        border-radius: 20px !important;
        padding: 1.5rem 0.5rem !important;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        color: var(--text-primary) !important;
        font-weight: 500;
    }
    .stButton > button:hover {
        box-shadow: var(--shadow-md) !important;
        transform: scale(1.01);
        border-color: var(--accent-blue) !important;
    }

    /* 信息流卡片 */
    .feed-card {
        display: flex;
        background: var(--bg-secondary);
        padding: 1.75rem;
        border-radius: 24px;
        margin-bottom: 1.25rem;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
    }
    .feed-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--border-medium);
    }
    .card-icon-area {
        flex-shrink: 0;
        width: 64px;
        height: 64px;
        border-radius: 18px;
        margin-right: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-light);
    }
    .card-title-main {
        font-size: 1.25rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        line-height: 1.4;
    }
    .feature-block {
        background-color: var(--bg-tertiary);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0 0.5rem 0;
        border: 1px solid var(--border-light);
    }
    .feature-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.4rem;
        display: block;
    }
    .feature-content {
        font-size: 0.95rem;
        color: var(--text-primary);
        font-weight: 450;
        line-height: 1.5;
    }
    .meta-text {
        font-size: 0.8rem;
        color: var(--text-tertiary);
        font-weight: 400;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* 博主卡片 */
    .blogger-card {
        background: var(--bg-secondary);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        margin-bottom: 1.25rem;
        transition: var(--transition);
    }
    .blogger-card:hover {
        box-shadow: var(--shadow-md);
    }
    .blogger-name {
        font-weight: 650;
        font-size: 1.3rem;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .blogger-handle {
        color: var(--accent-blue);
        font-weight: 500;
        font-size: 0.9rem;
    }
    .blogger-quote {
        margin-top: 1rem;
        padding: 1rem 1.25rem;
        background: var(--bg-tertiary);
        border-radius: 16px;
        border-left: 4px solid var(--accent-blue);
        font-style: normal;
        color: var(--text-primary);
        line-height: 1.6;
    }

    /* 学习资料卡片 */
    .resource-card {
        background: var(--bg-secondary);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        height: 100%;
        transition: var(--transition);
        display: flex;
        flex-direction: column;
    }
    .resource-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-4px);
    }
    .resource-icon {
        font-size: 2.2rem;
        margin-bottom: 1rem;
    }
    .resource-title {
        font-weight: 650;
        font-size: 1.2rem;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    .resource-desc {
        color: var(--text-tertiary);
        font-size: 0.9rem;
        line-height: 1.5;
        flex-grow: 1;
        margin-bottom: 1.25rem;
    }
    .resource-link {
        display: inline-block;
        background: var(--accent-blue);
        color: white !important;
        padding: 0.5rem 1.2rem;
        border-radius: 30px;
        font-weight: 500;
        font-size: 0.9rem;
        text-decoration: none;
        text-align: center;
        transition: var(--transition);
        border: none;
        width: fit-content;
    }
    .resource-link:hover {
        background: #005bb5;
        text-decoration: none;
    }

    /* 标签页定制 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2.5rem;
        border-bottom: 1px solid var(--border-light);
        padding-bottom: 0;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 1.1rem;
        color: var(--text-tertiary);
        padding: 0.75rem 0.25rem;
        border-radius: 0;
        transition: var(--transition);
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-blue) !important;
        border-bottom: 3px solid var(--accent-blue);
        font-weight: 600;
    }

    div[data-baseweb="select"] > div {
        background-color: var(--bg-secondary) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-medium) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stInfo, .stWarning {
        background: var(--bg-secondary) !important;
        border-radius: 20px !important;
        border: 1px solid var(--border-light) !important;
        box-shadow: var(--shadow-sm) !important;
        padding: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 数据加载 ----------
GSHEET_URL = st.secrets.get("gsheet_url", "")

@st.cache_data(ttl=300)
def load_monthly_data():
    if not GSHEET_URL:
        return pd.DataFrame()
    try:
        base_url = GSHEET_URL.split('/edit')[0]
        encoded_name = urllib.parse.quote("sheet")
        csv_url = f"{base_url}/export?format=csv&sheet={encoded_name}"
        df = pd.read_csv(csv_url)
        df.columns = df.columns.astype(str).str.strip()
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            df = df.dropna(subset=['日期'])
            df['选择月份'] = df['日期'].dt.strftime('%Y-%m')
            df = df.sort_values('日期', ascending=False)
        if '分类' in df.columns:
            df['分类'] = df['分类'].astype(str).str.strip()
        return df
    except Exception:
        return pd.DataFrame()

def get_blogger_data():
    return [
        {"name": "Andrej Karpathy", "handle": "@karpathy", "platform": "X / YouTube", "avatar": "🧠",
         "quote": "最近在构建一个从零开始的 LLM 训练项目，代码已开源在 GitHub。最让我惊讶的是数据质量对最终效果的影响远超模型架构。",
         "date": "2026-04-15", "category": "技术大牛"},
        {"name": "李沐", "handle": "@mli", "platform": "Bilibili / 知乎", "avatar": "📚",
         "quote": "动手学深度学习 第三版正在更新中，新增了关于 MoE 和 RLHF 的章节。欢迎大家提 PR 和 issue。",
         "date": "2026-04-10", "category": "教育者"},
        {"name": "Simon Willison", "handle": "@simonw", "platform": "X / Blog", "avatar": "🐍",
         "quote": "Datasette 的新插件支持了 embedding 搜索，现在你可以用自然语言查询 SQLite 数据库了。",
         "date": "2026-04-08", "category": "开发者"},
        {"name": "Lilian Weng", "handle": "@lilianweng", "platform": "X / 个人博客", "avatar": "🤖",
         "quote": "写了一篇长文梳理 OpenAI 内部使用的 Agent 系统设计原则，包括规划、记忆和工具使用。",
         "date": "2026-04-01", "category": "研究员"}
    ]

def get_resource_data():
    return [
        {"title": "动手学深度学习", "desc": "李沐等人的开源深度学习教材，包含 PyTorch 代码实现。", "icon": "📘",
         "url": "https://zh.d2l.ai/", "tags": ["入门", "PyTorch", "书籍"]},
        {"title": "Hugging Face NLP Course", "desc": "学习使用 Transformers 库和扩散模型的最佳实践。", "icon": "🤗",
         "url": "https://huggingface.co/learn/nlp-course", "tags": ["NLP", "Transformers", "实战"]},
        {"title": "Fast.ai", "desc": "面向程序员的实用深度学习课程，强调快速上手和可复现结果。", "icon": "⚡",
         "url": "https://course.fast.ai/", "tags": ["入门", "计算机视觉", "实战"]},
        {"title": "LLM Bootcamp", "desc": "Full Stack Deep Learning 出品的大语言模型训练与部署课程。", "icon": "🚀",
         "url": "https://fullstackdeeplearning.com/llm-bootcamp/", "tags": ["LLM", "高级", "工程"]},
        {"title": "Papers with Code", "desc": "机器学习论文与代码对照，追踪 SOTA 模型。", "icon": "📄",
         "url": "https://paperswithcode.com/", "tags": ["论文", "SOTA", "资源"]},
        {"title": "The Illustrated Transformer", "desc": "Jay Alammar 的图解 Transformer，直观理解注意力机制。", "icon": "🎨",
         "url": "https://jalammar.github.io/illustrated-transformer/", "tags": ["Transformer", "图解", "必读"]}
    ]

# ---------- 组件 ----------
def render_feed_cards(data):
    if data.empty:
        st.info("✨ 当前筛选条件下暂无数据")
        return
    for _, row in data.iterrows():
        cat = row.get('分类', '未分类')
        if cat == "基建":
            icon, accent_color = "🏗️", "var(--accent-blue)"
        elif cat == "金融":
            icon, accent_color = "💰", "var(--accent-orange)"
        else:
            icon, accent_color = "🎨", "var(--accent-green)"

        month_str = f"{row['日期'].year}年{row['日期'].month}月"
        company_key = next((k for k in ['公司', 'Company', '企业'] if k in row), '公司')
        company_name = row.get(company_key, '未知公司')
        progress = row.get('进展', '暂无进展说明')
        feature = row.get('核心特点', '暂无描述')
        feedback = row.get('市场反响', '暂无评价')

        st.markdown(f"""
            <div class="feed-card">
                <div class="card-icon-area" style="color: {accent_color};">
                    {icon}
                </div>
                <div style="flex-grow: 1;">
                    <div class="meta-text" style="margin-bottom: 0.25rem;">
                        <span>📅 {month_str}</span>
                        <span style="margin: 0 8px;">·</span>
                        <span style="font-weight: 500;">{cat}</span>
                    </div>
                    <div class="card-title-main">
                        {company_name}：{progress}
                    </div>
                    <div class="feature-block">
                        <span class="feature-label">✨ 核心特点</span>
                        <div class="feature-content">{feature}</div>
                    </div>
                    <div class="meta-text" style="margin-top: 0.5rem;">
                        💬 {feedback}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def render_monthly_insights():
    st.markdown("""
    <div class="page-header">
        <h1>📆 月度 AI 进展 · 动态看板</h1>
        <p>追踪全球 AI 基建、应用与金融领域的每月动态</p>
    </div>
    """, unsafe_allow_html=True)

    all_data = load_monthly_data()
    if all_data.empty:
        st.info("📭 等待数据接入 — 请确保数据源已配置并包含所需字段。")
        return

    if 'active_category' not in st.session_state:
        st.session_state.active_category = "全部"

    month_options = sorted(all_data['选择月份'].unique().tolist(), reverse=True)
    region_col = next((c for c in all_data.columns if c in ['地域', '地区']), None)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="filter-label">📅 月份</div>', unsafe_allow_html=True)
        selected_month = st.selectbox("月份", month_options, label_visibility="collapsed")
    with col2:
        if region_col:
            region_values = sorted(all_data[region_col].unique().tolist())
            region_options = ["全部地区"] + region_values
            st.markdown('<div class="filter-label">🌐 地域</div>', unsafe_allow_html=True)
            selected_region = st.selectbox("地域", region_options, label_visibility="collapsed")
        else:
            selected_region = "全部地区"
            st.markdown('<div class="filter-label">🌐 地域</div>', unsafe_allow_html=True)
            st.selectbox("地域", ["全部地区"], disabled=True, label_visibility="collapsed")

    df = all_data[all_data['选择月份'] == selected_month].copy()
    if region_col and selected_region != "全部地区":
        df = df[df[region_col] == selected_region]

    cat_col = '分类' if '分类' in df.columns else None
    if cat_col:
        infra_n = len(df[df[cat_col] == '基建'])
        app_n = len(df[df[cat_col] == '应用'])
        fin_n = len(df[df[cat_col] == '金融'])
    else:
        infra_n = app_n = fin_n = 0
    total_n = len(df)

    # 四列按钮
    c1, c2, c3, c4 = st.columns(4)

    # 根据当前激活分类注入高亮样式
    active = st.session_state.active_category
    highlight_css = ""
    if active == "全部":
        highlight_css = """
        div[data-testid="column"]:nth-of-type(1) .stButton > button {
            border: 2px solid var(--accent-blue) !important;
            background: linear-gradient(145deg, #ffffff, #f8faff) !important;
        }
        """
    elif active == "基建":
        highlight_css = """
        div[data-testid="column"]:nth-of-type(2) .stButton > button {
            border: 2px solid var(--accent-blue) !important;
            background: linear-gradient(145deg, #ffffff, #f8faff) !important;
        }
        """
    elif active == "应用":
        highlight_css = """
        div[data-testid="column"]:nth-of-type(3) .stButton > button {
            border: 2px solid var(--accent-blue) !important;
            background: linear-gradient(145deg, #ffffff, #f8faff) !important;
        }
        """
    elif active == "金融":
        highlight_css = """
        div[data-testid="column"]:nth-of-type(4) .stButton > button {
            border: 2px solid var(--accent-blue) !important;
            background: linear-gradient(145deg, #ffffff, #f8faff) !important;
        }
        """
    st.markdown(f"<style>{highlight_css}</style>", unsafe_allow_html=True)

    with c1:
        if st.button(f"📊 全部\n\n{total_n}", key="btn_all", use_container_width=True):
            st.session_state.active_category = "全部"
    with c2:
        if st.button(f"🏗️ 基建\n\n{infra_n}", key="btn_infra", use_container_width=True):
            st.session_state.active_category = "基建"
    with c3:
        if st.button(f"🎨 应用\n\n{app_n}", key="btn_app", use_container_width=True):
            st.session_state.active_category = "应用"
    with c4:
        if st.button(f"💰 金融\n\n{fin_n}", key="btn_fin", use_container_width=True):
            st.session_state.active_category = "金融"

    # 根据激活分类过滤数据
    if cat_col and st.session_state.active_category != "全部":
        display_df = df[df[cat_col] == st.session_state.active_category]
    else:
        display_df = df

    render_feed_cards(display_df)

def render_bloggers():
    st.markdown("""
    <div class="page-header">
        <h1>🗣️ 知名博主 · 洞见追踪</h1>
        <p>汇集 AI 领域顶尖研究者和开发者的最新观点</p>
    </div>
    """, unsafe_allow_html=True)

    bloggers = get_blogger_data()
    categories = ["全部"] + sorted({b["category"] for b in bloggers})
    selected_cat = st.selectbox("按领域筛选", categories, label_visibility="collapsed")
    filtered = bloggers if selected_cat == "全部" else [b for b in bloggers if b["category"] == selected_cat]

    if not filtered:
        st.info("暂无该分类的博主动态")
        return

    for b in filtered:
        st.markdown(f"""
        <div class="blogger-card">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 3rem; line-height: 1;">{b['avatar']}</div>
                <div style="flex-grow: 1;">
                    <div class="blogger-name">
                        {b['name']}
                        <span class="blogger-handle">{b['handle']}</span>
                    </div>
                    <div class="meta-text">{b['platform']} · {b['date']} · 分类: {b['category']}</div>
                </div>
            </div>
            <div class="blogger-quote">
                “{b['quote']}”
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("💡 数据为手动更新，计划接入 RSS / X API 自动同步。")

def render_resources():
    st.markdown("""
    <div class="page-header">
        <h1>📚 学习资料 · 系统进阶</h1>
        <p>精选 AI 学习路径、课程与工具，支持一键跳转</p>
    </div>
    """, unsafe_allow_html=True)

    resources = get_resource_data()
    all_tags = sorted({tag for r in resources for tag in r["tags"]})
    selected_tags = st.multiselect("筛选标签", all_tags, default=[], placeholder="点击选择标签...")

    if selected_tags:
        filtered_res = [r for r in resources if any(tag in selected_tags for tag in r["tags"])]
    else:
        filtered_res = resources

    if not filtered_res:
        st.info("没有匹配的学习资料，请调整标签筛选。")
        return

    cols = st.columns(3)
    for i, res in enumerate(filtered_res):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="resource-card">
                <div class="resource-icon">{res['icon']}</div>
                <div class="resource-title">{res['title']}</div>
                <div class="resource-desc">{res['desc']}</div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1.2rem;">
                    {"".join([f'<span style="background: var(--bg-tertiary); padding: 0.2rem 0.6rem; border-radius: 30px; font-size: 0.7rem; color: var(--text-tertiary); border: 1px solid var(--border-light);">{tag}</span>' for tag in res['tags']])}
                </div>
                <a href="{res['url']}" target="_blank" class="resource-link">
                    🌐 访问网站 →
                </a>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("⭐ 收藏本页，随时回来充电。")

# ---------- 主入口 ----------
def main():
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <span style="font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; background: linear-gradient(135deg, #0071e3 0%, #af52de 80%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            ⚡ AI Sentinel
        </span>
        <span style="font-size: 1rem; color: var(--text-tertiary); margin-left: 1rem; font-weight: 400;">智能瞭望台 · 每日 AI 脉搏</span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📆 月度进展", "🗣️ 知名博主", "📚 学习资料"])

    with tab1:
        render_monthly_insights()
    with tab2:
        render_bloggers()
    with tab3:
        render_resources()

if __name__ == "__main__":
    main()
