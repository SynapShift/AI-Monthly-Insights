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

# ---------- 全新设计系统 CSS (Modern Glassmorphism + Editorial) ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

    :root {
        --bg-gradient: linear-gradient(145deg, #f9fafc 0%, #f0f2f7 100%);
        --glass-bg: rgba(255, 255, 255, 0.75);
        --glass-border: rgba(255, 255, 255, 0.5);
        --text-primary: #0b0c0e;
        --text-secondary: #5b6778;
        --text-tertiary: #8a95a5;
        --accent-blue: #0066ff;
        --accent-green: #00b894;
        --accent-orange: #e67e22;
        --accent-purple: #8e44ad;
        --shadow-sm: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
        --shadow-md: 0 20px 30px -10px rgba(0, 0, 0, 0.1), 0 10px 20px -10px rgba(0, 0, 0, 0.04);
        --shadow-glow: 0 0 0 1px rgba(0, 102, 255, 0.1), 0 8px 20px rgba(0, 102, 255, 0.15);
        --transition: all 0.25s cubic-bezier(0.2, 0.0, 0.0, 1.0);
    }

    .stApp {
        background: var(--bg-gradient);
        background-attachment: fixed;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 隐藏默认元素 */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }

    .main .block-container {
        max-width: 1300px;
        padding-top: 1.5rem;
    }

    /* ----- 品牌头部 ----- */
    .brand-header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }
    .brand-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #0b0c0e 0%, #3a4a6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .brand-sub {
        font-size: 0.95rem;
        color: var(--text-tertiary);
        font-weight: 400;
        margin-left: 0.75rem;
    }

    /* ----- 筛选栏融合在标题行 ----- */
    .filter-row {
        display: flex;
        gap: 1.5rem;
        align-items: center;
        margin-bottom: 2rem;
    }
    .filter-chip {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 40px;
        padding: 0.4rem 0.8rem 0.4rem 1.5rem;
        box-shadow: var(--shadow-sm);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .filter-chip span {
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 0.9rem;
    }
    .filter-chip .stSelectbox {
        min-width: 140px;
    }
    .filter-chip div[data-baseweb="select"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* ----- 统计卡片 (毛玻璃大数字) ----- */
    .stat-grid {
        display: flex;
        gap: 1.2rem;
        margin-bottom: 2.5rem;
    }
    .stat-item {
        flex: 1;
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 32px;
        padding: 1.8rem 1rem;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        text-align: center;
    }
    .stat-item:hover {
        box-shadow: var(--shadow-md), var(--shadow-glow);
        transform: translateY(-4px);
        border-color: rgba(0, 102, 255, 0.3);
    }
    .stat-number {
        font-size: 3.2rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--text-primary);
        line-height: 1.1;
        margin-bottom: 0.3rem;
    }
    .stat-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-tertiary);
    }

    /* ----- 胶囊式分类切换器 (替代大按钮) ----- */
    .category-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        padding-bottom: 0.8rem;
    }
    .cat-pill {
        padding: 0.6rem 1.5rem;
        border-radius: 40px;
        font-weight: 550;
        font-size: 0.95rem;
        background: transparent;
        color: var(--text-secondary);
        transition: var(--transition);
        cursor: pointer;
        border: none;
        text-align: center;
    }
    .cat-pill:hover {
        background: rgba(0,0,0,0.03);
        color: var(--text-primary);
    }
    .cat-pill.active {
        background: var(--text-primary);
        color: white;
        box-shadow: var(--shadow-glow);
    }

    /* ----- 信息流卡片 (编辑风格) ----- */
    .feed-card-new {
        display: flex;
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 28px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    .feed-card-new:hover {
        box-shadow: var(--shadow-md);
        border-color: rgba(0, 102, 255, 0.2);
    }
    /* 左侧彩色装饰条 */
    .card-accent-bar {
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 6px;
        background: var(--accent-color, #ccc);
    }
    .card-content {
        margin-left: 0.5rem;
        flex: 1;
    }
    .card-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.5rem;
        font-size: 0.8rem;
        color: var(--text-tertiary);
    }
    .card-company {
        font-weight: 650;
        font-size: 1.3rem;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }
    .card-progress {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    .feature-block-new {
        background: rgba(0,0,0,0.02);
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        border-left: 3px solid var(--accent-blue);
    }
    .feature-label-new {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--text-tertiary);
        margin-bottom: 0.3rem;
    }
    .feature-text {
        font-size: 0.95rem;
        color: var(--text-primary);
        line-height: 1.5;
    }
    .feedback-text {
        font-size: 0.85rem;
        color: var(--text-tertiary);
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    /* 按钮等重置 */
    .stButton > button {
        background: transparent;
        border: none;
        padding: 0;
    }
    .stSelectbox label {
        display: none;
    }

    /* 空状态 */
    .stInfo {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(12px);
        border-radius: 28px !important;
        border: 1px solid var(--glass-border) !important;
        padding: 2.5rem !important;
        text-align: center;
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

# ---------- 全新第一页 ----------
def render_monthly_insights():
    # 品牌头部（与筛选栏融合）
    st.markdown("""
    <div class="brand-header">
        <div>
            <span class="brand-title">⚡ AI Sentinel</span>
            <span class="brand-sub">智能瞭望台 · 每日 AI 脉搏</span>
        </div>
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

    # 筛选行（融合进设计）
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div style="margin-bottom: 0.5rem; font-weight: 600; color: var(--text-secondary);">📅 月份</div>', unsafe_allow_html=True)
        selected_month = st.selectbox("月份", month_options, label_visibility="collapsed")
    with col2:
        st.markdown('<div style="margin-bottom: 0.5rem; font-weight: 600; color: var(--text-secondary);">🌐 地域</div>', unsafe_allow_html=True)
        if region_col:
            region_values = sorted(all_data[region_col].unique().tolist())
            region_options = ["全部地区"] + region_values
            selected_region = st.selectbox("地域", region_options, label_visibility="collapsed")
        else:
            selected_region = "全部地区"
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

    # 统计卡片（毛玻璃）
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-item">
            <div class="stat-number">{total_n}</div>
            <div class="stat-label">📊 全部动态</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{infra_n}</div>
            <div class="stat-label">🏗️ 基建</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{app_n}</div>
            <div class="stat-label">🎨 应用</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{fin_n}</div>
            <div class="stat-label">💰 金融</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 胶囊切换器
    active_cat = st.session_state.active_category
    cats = ["全部", "基建", "应用", "金融"]
    cat_icons = ["📊", "🏗️", "🎨", "💰"]

    # 渲染胶囊 (使用自定义 HTML + st.button 混合)
    cols = st.columns(len(cats))
    for i, (cat, icon) in enumerate(zip(cats, cat_icons)):
        with cols[i]:
            # 通过 st.button 实现点击切换
            if st.button(f"{icon} {cat}", key=f"cat_{cat}", use_container_width=True,
                         type="primary" if active_cat == cat else "secondary"):
                st.session_state.active_category = cat

    # 注入胶囊样式覆盖 st.button 默认外观
    st.markdown("""
    <style>
        /* 让 st.button 看起来像胶囊 */
        div[data-testid="stButton"] button {
            background: transparent !important;
            border: none !important;
            border-radius: 40px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 550 !important;
            font-size: 0.95rem !important;
            color: var(--text-secondary) !important;
            box-shadow: none !important;
            transition: var(--transition) !important;
            width: 100%;
        }
        div[data-testid="stButton"] button:hover {
            background: rgba(0,0,0,0.03) !important;
            color: var(--text-primary) !important;
        }
        /* 激活状态（primary 类型） */
        div[data-testid="stButton"] button[kind="primary"] {
            background: var(--text-primary) !important;
            color: white !important;
            box-shadow: var(--shadow-glow) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 根据激活分类过滤数据
    if cat_col and st.session_state.active_category != "全部":
        display_df = df[df[cat_col] == st.session_state.active_category]
    else:
        display_df = df

    # 信息流
    if display_df.empty:
        st.info("✨ 当前筛选条件下暂无数据")
        return

    for _, row in display_df.iterrows():
        cat = row.get('分类', '未分类')
        if cat == "基建":
            accent_color = "var(--accent-blue)"
        elif cat == "金融":
            accent_color = "var(--accent-orange)"
        else:
            accent_color = "var(--accent-green)"

        month_str = f"{row['日期'].year}年{row['日期'].month}月"
        company_key = next((k for k in ['公司', 'Company', '企业'] if k in row), '公司')
        company_name = row.get(company_key, '未知公司')
        progress = row.get('进展', '暂无进展说明')
        feature = row.get('核心特点', '暂无描述')
        feedback = row.get('市场反响', '暂无评价')

        st.markdown(f"""
        <div class="feed-card-new">
            <div class="card-accent-bar" style="--accent-color: {accent_color};"></div>
            <div class="card-content">
                <div class="card-meta">
                    <span>📅 {month_str}</span>
                    <span>•</span>
                    <span style="font-weight: 600;">{cat}</span>
                </div>
                <div class="card-company">{company_name}</div>
                <div class="card-progress">{progress}</div>
                <div class="feature-block-new">
                    <div class="feature-label-new">✨ 核心特点</div>
                    <div class="feature-text">{feature}</div>
                </div>
                <div class="feedback-text">
                    <span>💬</span> {feedback}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------- 第二、三页保持原样（略作适配）----------
def render_bloggers():
    st.markdown("""
    <div style="margin-top: 1rem;">
        <span style="font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary);">🗣️ 知名博主 · 洞见追踪</span>
        <p style="color: var(--text-secondary); margin-top: 0.25rem;">汇集 AI 领域顶尖研究者和开发者的最新观点</p>
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
        <div style="background: var(--glass-bg); backdrop-filter: blur(12px); border: 1px solid var(--glass-border); border-radius: 28px; padding: 1.5rem; margin-bottom: 1.2rem; box-shadow: var(--shadow-sm);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 3rem;">{b['avatar']}</div>
                <div>
                    <div style="font-weight: 700; font-size: 1.3rem;">{b['name']} <span style="color: var(--accent-blue); font-weight: 500;">{b['handle']}</span></div>
                    <div style="color: var(--text-tertiary);">{b['platform']} · {b['date']} · {b['category']}</div>
                </div>
            </div>
            <div style="margin-top: 1rem; padding: 1rem 1.2rem; background: rgba(0,0,0,0.02); border-radius: 18px; border-left: 4px solid var(--accent-blue);">
                “{b['quote']}”
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.caption("💡 数据为手动更新，计划接入 RSS / X API 自动同步。")

def render_resources():
    st.markdown("""
    <div style="margin-top: 1rem;">
        <span style="font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary);">📚 学习资料 · 系统进阶</span>
        <p style="color: var(--text-secondary); margin-top: 0.25rem;">精选 AI 学习路径、课程与工具，支持一键跳转</p>
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
            <div style="background: var(--glass-bg); backdrop-filter: blur(12px); border: 1px solid var(--glass-border); border-radius: 28px; padding: 1.5rem; height: 100%; box-shadow: var(--shadow-sm); transition: var(--transition);">
                <div style="font-size: 2.2rem; margin-bottom: 1rem;">{res['icon']}</div>
                <div style="font-weight: 700; font-size: 1.2rem; margin-bottom: 0.5rem;">{res['title']}</div>
                <div style="color: var(--text-tertiary); font-size: 0.9rem; margin-bottom: 1rem;">{res['desc']}</div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1.2rem;">
                    {"".join([f'<span style="background: rgba(0,0,0,0.03); padding: 0.2rem 0.6rem; border-radius: 30px; font-size: 0.7rem; color: var(--text-tertiary);">{tag}</span>' for tag in res['tags']])}
                </div>
                <a href="{res['url']}" target="_blank" style="display: inline-block; background: var(--text-primary); color: white; padding: 0.5rem 1.2rem; border-radius: 30px; font-weight: 500; font-size: 0.9rem; text-decoration: none;">
                    🌐 访问网站 →
                </a>
            </div>
            """, unsafe_allow_html=True)
    st.caption("⭐ 收藏本页，随时回来充电。")

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
