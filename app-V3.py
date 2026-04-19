import streamlit as st
import pandas as pd
import urllib.parse

# ---------- 页面基础配置 ----------
st.set_page_config(
    page_title="AI Sentinel · 智能瞭望台",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚡"
)

# ---------- 全球领先的极简设计系统 (Design System) ----------
st.markdown("""
<style>
    /* 引入现代字体堆栈 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');

    :root {
        --bg-color: #f5f5f7; /* Apple 背景色 */
        --card-bg: #ffffff;
        --text-title: #1d1d1f;
        --text-body: #424245;
        --accent-blue: #0066cc;
        --accent-green: #28cd41;
        --accent-orange: #ff9500;
        --border-color: rgba(0,0,0,0.05);
        --shadow: 0 8px 30px rgba(0,0,0,0.04);
    }

    /* 容器重置 */
    .stApp {
        background-color: var(--bg-color);
        font-family: 'Inter', 'Noto Sans SC', sans-serif;
    }

    .main .block-container {
        max-width: 900px;
        padding-top: 3rem;
    }

    /* 隐藏默认元素 */
    [data-testid="stHeader"], footer { visibility: hidden; }

    /* ----- 品牌视觉 ----- */
    .brand-box {
        text-align: center;
        margin-bottom: 4rem;
    }
    .brand-logo {
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        background: linear-gradient(135deg, #1d1d1f 0%, #424245 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-tagline {
        color: #86868b;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* ----- 模块卡片 (Cards) ----- */
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: var(--shadow);
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.08);
    }

    /* ----- 内容元素 ----- */
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 12px;
        background: #f0f0f2;
        color: #86868b;
    }
    .card-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-title);
        margin-bottom: 10px;
        line-height: 1.3;
    }
    .card-desc {
        font-size: 1rem;
        color: var(--text-body);
        line-height: 1.6;
        margin-bottom: 16px;
    }
    .quote-box {
        border-left: 3px solid var(--accent-blue);
        background: #f9f9fb;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        font-size: 0.95rem;
        color: #1d1d1f;
        margin: 12px 0;
    }

    /* ----- 按钮与导航 ----- */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 30px;
        border-bottom: none;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #86868b !important;
        font-size: 1rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-blue) !important;
        font-weight: 700;
    }
    
    /* 自定义链接按钮 */
    .btn-primary {
        display: inline-block;
        background: var(--text-title);
        color: white !important;
        padding: 8px 20px;
        border-radius: 99px;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 500;
        float: right;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 数据模拟 (你可以替换回你的 load_monthly_data) ----------
def get_mock_data():
    return [
        {"cat": "金融AI", "title": "FlashFin 2.0 架构升级", "body": "全面接入 iPhone 原生 NPU 加速，研报总结速度提升 40%，新增异动回测模块。", "meta": "2026-04", "status": "Stable"},
        {"cat": "底层基建", "title": "多 Agent 协同系统上线", "body": "基于 Streamlit + Google Sheets 构建的自动化同步面板，支持多级数据缓存与异常重试。", "meta": "2026-03", "status": "Testing"}
    ]

def get_blogger_data():
    return [
        {"name": "Andrej Karpathy", "handle": "@karpathy", "avatar": "🧠", "quote": "最近在构建一个从零开始的 LLM 训练项目，数据质量远比架构重要。"},
        {"name": "Lilian Weng", "handle": "@lilianweng", "avatar": "🤖", "quote": "OpenAI 内部使用的 Agent 设计原则：规划、记忆与工具的深度解耦。"}
    ]

# ---------- 渲染函数 ----------

def render_brand():
    st.markdown("""
    <div class="brand-box">
        <div class="brand-logo">AI SENTINEL</div>
        <div class="brand-tagline">智能瞭望 · 每日 AI 脉搏</div>
    </div>
    """, unsafe_allow_html=True)

def render_insights():
    data = get_mock_data()
    for item in data:
        color = "var(--accent-blue)" if "金融" in item['cat'] else "var(--accent-orange)"
        st.markdown(f"""
        <div class="glass-card">
            <span class="tag" style="color: {color}; background: {color}15;">{item['cat']}</span>
            <div class="card-title">{item['title']}</div>
            <div class="card-desc">{item['body']}</div>
            <div style="border-top: 1px solid #f2f2f2; padding-top: 15px; overflow: hidden;">
                <span style="font-size: 0.8rem; color: #86868b;">📅 {item['meta']} · 状态: {item['status']}</span>
                <a href="#" class="btn-primary">详情内容 →</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_bloggers():
    bloggers = get_blogger_data()
    for b in bloggers:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; gap: 20px; align-items: center;">
                <div style="font-size: 2.5rem; background: #f5f5f7; width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">{b['avatar']}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 700; font-size: 1.2rem;">{b['name']} <span style="font-weight: 400; color: var(--accent-blue); font-size: 0.9rem;">{b['handle']}</span></div>
                    <div class="quote-box">“{b['quote']}”</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_resources():
    st.markdown("### 📚 精选资源仓库")
    # 采用网格布局
    cols = st.columns(2)
    res_list = [
        {"title": "Fast.ai 深度学习", "icon": "⚡", "tags": ["入门", "实战"]},
        {"title": "Hugging Face 课程", "icon": "🤗", "tags": ["NLP", "工程"]},
    ]
    for i, res in enumerate(res_list):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="glass-card" style="height: 160px;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">{res['icon']}</div>
                <div style="font-weight: 700;">{res['title']}</div>
                <div style="margin-top: 10px;">
                    {" ".join([f'<span class="tag">{t}</span>' for t in res['tags']])}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ---------- 主入口 ----------
def main():
    render_brand()
    
    # 这种方式可以让 Tab 看起来更像二级导航
    tab1, tab2, tab3 = st.tabs(["📆 动态追踪", "🗣️ 思想领袖", "📚 进阶资料"])
    
    with tab1:
        render_insights()
    with tab2:
        render_bloggers()
    with tab3:
        render_resources()

if __name__ == "__main__":
    main()
