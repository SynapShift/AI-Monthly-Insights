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

# ---------- 极简设计系统 CSS ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

    :root {
        --bg-page: #fafbfc;
        --surface: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-tertiary: #94a3b8;
        --border-light: #e2e8f0;
        --border-medium: #cbd5e1;
        --accent-blue: #2563eb;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
        --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-sm: 0 4px 6px -2px rgba(0,0,0,0.05);
        --transition: all 0.15s ease;
    }

    .stApp {
        background-color: var(--bg-page);
        font-family: 'Inter', sans-serif;
    }

    /* 隐藏侧边栏等 */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }

    .main .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* ----- 品牌头 ----- */
    .app-header {
        display: flex;
        align-items: baseline;
        margin-bottom: 2rem;
    }
    .app-title {
        font-size: 1.8rem;
        font-weight: 650;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }
    .app-sub {
        font-size: 0.9rem;
        color: var(--text-tertiary);
        margin-left: 1rem;
        font-weight: 400;
    }

    /* ----- 筛选栏（芯片式）----- */
    .filter-bar {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        align-items: center;
        flex-wrap: wrap;
    }
    .filter-chip {
        background: var(--surface);
        border: 1px solid var(--border-light);
        border-radius: 40px;
        padding: 0.25rem 0.5rem 0.25rem 1rem;
        box-shadow: var(--shadow-xs);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .filter-chip span {
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 0.85rem;
    }
    .filter-chip .stSelectbox > div {
        min-width: 130px;
    }
    .filter-chip div[data-baseweb="select"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-weight: 500;
    }

    /* ----- 分类指标条（可点击标签）----- */
    .category-strip {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--border-light);
        padding-bottom: 1rem;
    }
    .cat-tag {
        padding: 0.4rem 1.2rem;
        border-radius: 40px;
        font-weight: 500;
        font-size: 0.9rem;
        background: var(--surface);
        border: 1px solid var(--border-light);
        color: var(--text-secondary);
        cursor: pointer;
        transition: var(--transition);
        box-shadow: var(--shadow-xs);
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .cat-tag:hover {
        border-color: var(--accent-blue);
        color: var(--text-primary);
    }
    .cat-tag.active {
        background: var(--text-primary);
        border-color: var(--text-primary);
        color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .cat-count {
        font-weight: 600;
        margin-left: 4px;
    }

    /* ----- 信息流列表（无卡片）----- */
    .feed-list {
        margin-top: 0.5rem;
    }
    .feed-item {
        padding: 1.2rem 0.5rem;
        border-bottom: 1px solid var(--border-light);
        transition: var(--transition);
        display: block;
        text-decoration: none;
        color: inherit;
    }
    .feed-item:hover {
        background: rgba(37, 99, 235, 0.02);
        padding-left: 1rem;
        border-radius: 8px;
    }
    .item-header {
        display: flex;
        align-items: baseline;
        gap: 1rem;
        margin-bottom: 0.3rem;
    }
    .item-company {
        font-weight: 650;
        font-size: 1.1rem;
        color: var(--text-primary);
    }
    .item-meta {
        font-size: 0.8rem;
        color: var(--text-tertiary);
        display: flex;
        gap: 0.8rem;
    }
    .item-progress {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin: 0.5rem 0 0.3rem 0;
        line-height: 1.5;
    }
    .item-feature {
        background: #f8fafc;
        padding: 0.6rem 1rem;
        border-radius: 12px;
        font-size: 0.9rem;
        color: var(--text-primary);
        margin: 0.6rem 0;
        border-left: 3px solid var(--accent-blue);
    }
    .item-feedback {
        font-size: 0.85rem;
        color: var(--text-tertiary);
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* 第二、三页卡片（轻量版） */
    .card-generic {
        background: var(--surface);
        border: 1px solid var(--border-light);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-xs);
        transition: var(--transition);
    }
    .card-generic:hover {
        box-shadow: var(--shadow-sm);
        border-color: var(--border-medium);
    }

    /* 标签页 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid var(--border-light);
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        color: var(--text-tertiary);
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-blue) !important;
    }

    /* 空状态 */
    .stInfo {
        background: var(--surface) !important;
        border-radius: 16px !important;
        border: 1px solid var(--border-light) !important;
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

# ---------- 第一页：极简列表 ----------
def render_monthly_insights():
    # 品牌头部
    st.markdown("""
    <div class="app-header">
        <span class="app-title">⚡ AI Sentinel</span>
        <span class="app-sub">智能瞭望台 · 每日 AI 脉搏</span>
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

    # 筛选栏（两芯片）
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="filter-chip">
            <span>📅 月份</span>
        """, unsafe_allow_html=True)
        selected_month = st.selectbox("月份", month_options, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="filter-chip">
            <span>🌐 地域</span>
        """, unsafe_allow_html=True)
        if region_col:
            region_values = sorted(all_data[region_col].unique().tolist())
            region_options = ["全部地区"] + region_values
            selected_region = st.selectbox("地域", region_options, label_visibility="collapsed")
        else:
            selected_region = "全部地区"
            st.selectbox("地域", ["全部地区"], disabled=True, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    # 数据过滤
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

    # 分类指标条（使用自定义 HTML + st.markdown 实现点击？但我们需要切换）
    # 用 st.radio 内联样式化
    active_cat = st.session_state.active_category
    cats = ["全部", "基建", "应用", "金融"]
    counts = [total_n, infra_n, app_n, fin_n]
    icons = ["📊", "🏗️", "🎨", "💰"]

    # 用 st.radio 但通过 CSS 隐藏默认样式，替换成胶囊标签
    selected_index = cats.index(active_cat) if active_cat in cats else 0
    selected_cat = st.radio(
        "分类筛选",
        options=cats,
        index=selected_index,
        horizontal=True,
        label_visibility="collapsed",
        key="category_radio"
    )
    # 更新 session_state
    if selected_cat != active_cat:
        st.session_state.active_category = selected_cat
        st.rerun()

    # 自定义 radio 样式为胶囊标签
    st.markdown("""
    <style>
        div[data-testid="stRadio"] > div {
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-light);
            padding-bottom: 1rem;
        }
        div[data-testid="stRadio"] label {
            padding: 0.4rem 1.2rem !important;
            border-radius: 40px !important;
            background: var(--surface) !important;
            border: 1px solid var(--border-light) !important;
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
            box-shadow: var(--shadow-xs) !important;
            transition: var(--transition) !important;
        }
        div[data-testid="stRadio"] label:hover {
            border-color: var(--accent-blue) !important;
            color: var(--text-primary) !important;
        }
        div[data-testid="stRadio"] label[data-selected="true"] {
            background: var(--text-primary) !important;
            border-color: var(--text-primary) !important;
            color: white !important;
        }
        /* 隐藏 radio 圆圈 */
        div[data-testid="stRadio"] div[role="radiogroup"] > div > div:first-child {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

    # 根据分类过滤数据
    if cat_col and active_cat != "全部":
        display_df = df[df[cat_col] == active_cat]
    else:
        display_df = df

    if display_df.empty:
        st.info("✨ 当前筛选条件下暂无数据")
        return

    # 列表渲染
    st.markdown('<div class="feed-list">', unsafe_allow_html=True)
    for _, row in display_df.iterrows():
        cat = row.get('分类', '未分类')
        if cat == "基建":
            accent = "var(--accent-blue)"
        elif cat == "金融":
            accent = "var(--accent-orange)"
        else:
            accent = "var(--accent-green)"

        month_str = f"{row['日期'].year}年{row['日期'].month}月"
        company_key = next((k for k in ['公司', 'Company', '企业'] if k in row), '公司')
        company_name = row.get(company_key, '未知公司')
        progress = row.get('进展', '暂无进展说明')
        feature = row.get('核心特点', '暂无描述')
        feedback = row.get('市场反响', '暂无评价')

        st.markdown(f"""
        <div class="feed-item">
            <div class="item-header">
                <span class="item-company">{company_name}</span>
                <span class="item-meta">
                    <span>📅 {month_str}</span>
                    <span style="color: {accent};">{cat}</span>
                </span>
            </div>
            <div class="item-progress">{progress}</div>
            <div class="item-feature" style="border-left-color: {accent};">
                <strong style="font-size:0.8rem; color: var(--text-tertiary);">✨ 核心特点</strong><br>
                {feature}
            </div>
            <div class="item-feedback">
                <span>💬</span> {feedback}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- 第二页：博主（轻量卡片）----------
def render_bloggers():
    st.markdown("""
    <div class="app-header">
        <span class="app-title">🗣️ 知名博主</span>
        <span class="app-sub">洞见追踪 · 观点速递</span>
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
        <div class="card-generic">
            <div style="display: flex; gap: 1rem;">
                <div style="font-size: 2.8rem;">{b['avatar']}</div>
                <div style="flex:1;">
                    <div style="font-weight: 650; font-size: 1.2rem;">{b['name']} 
                        <span style="color: var(--accent-blue); font-weight: 500;">{b['handle']}</span>
                    </div>
                    <div style="color: var(--text-tertiary); font-size: 0.8rem; margin-top: 0.2rem;">
                        {b['platform']} · {b['date']} · {b['category']}
                    </div>
                    <div style="margin-top: 1rem; padding: 0.8rem 1rem; background: #f8fafc; border-radius: 14px; border-left: 4px solid var(--accent-blue);">
                        “{b['quote']}”
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.caption("💡 数据手动更新，计划接入 RSS / X API。")

# ---------- 第三页：学习资料（网格卡片）----------
def render_resources():
    st.markdown("""
    <div class="app-header">
        <span class="app-title">📚 学习资料</span>
        <span class="app-sub">系统进阶 · 精选资源</span>
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
        st.info("没有匹配的学习资料")
        return

    cols = st.columns(3)
    for i, res in enumerate(filtered_res):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card-generic" style="height: 100%; display: flex; flex-direction: column;">
                <div style="font-size: 2rem; margin-bottom: 0.8rem;">{res['icon']}</div>
                <div style="font-weight: 650; font-size: 1.1rem;">{res['title']}</div>
                <div style="color: var(--text-tertiary); font-size: 0.85rem; margin: 0.5rem 0 1rem;">{res['desc']}</div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.3rem; margin-bottom: 1rem;">
                    {"".join([f'<span style="background:#f1f5f9; padding:2px 8px; border-radius:20px; font-size:0.7rem; color:var(--text-secondary);">{tag}</span>' for tag in res['tags']])}
                </div>
                <a href="{res['url']}" target="_blank" style="margin-top: auto; display: inline-block; background: var(--text-primary); color: white; padding: 0.4rem 1rem; border-radius: 30px; text-decoration: none; font-size:0.85rem; font-weight:500; text-align: center;">
                    🌐 访问 →
                </a>
            </div>
            """, unsafe_allow_html=True)
    st.caption("⭐ 收藏本页，随时充电。")

# ---------- 主入口 ----------
def main():
    tab1, tab2, tab3 = st.tabs(["📆 月度进展", "🗣️ 知名博主", "📚 学习资料"])

    with tab1:
        render_monthly_insights()
    with tab2:
        render_bloggers()
    with tab3:
        render_resources()

if __name__ == "__main__":
    main()
