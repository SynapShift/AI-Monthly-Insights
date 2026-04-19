import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

# ================= 1. 基础配置与 Apple 风格样式 =================
st.set_page_config(page_title="AI 行业洞察", layout="wide", page_icon="🚀")

st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 2rem;}
.stApp {background-color: #FFFFFF;}
/* 筛选器容器 */
.filter-container { background-color: #F5F5F7; padding: 20px; border-radius: 12px; margin-bottom: 25px; }
/* 产品卡片样式 */
.product-card {background-color: #FFFFFF; border: 1px solid #F2F2F2; padding: 24px; border-radius: 12px; margin-bottom: 20px; transition: all 0.3s ease; min-height: 250px;}
.product-card:hover {box-shadow: 0 8px 24px rgba(0,0,0,0.05);}
.tag {display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-right: 8px; background-color: #F5F5F7; color: #1D1D1F;}
.tag-highlight {background-color: #E60012; color: white;}
.insight-quote {background-color: #FBFBFD; padding: 15px; border-radius: 8px; font-size: 13px; border-left: 4px solid #E60012; color: #424245; margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

# ================= 2. 数据获取函数 =================
@st.cache_data(ttl=600)
def load_data():
    full_url = st.secrets.get("gsheet_url", "")
    if not full_url:
        return pd.DataFrame()
    try:
        # 降级方案：使用 CSV 导出链接，避免插件版本冲突
        if "/edit" in full_url:
            csv_url = full_url.split("/edit")[0] + "/export?format=csv"
        else:
            csv_url = full_url
        return pd.read_csv(csv_url)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_github_content():
    # 优先获取示例内容进行展示，后续可改为真实动态路径
    url = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/examples/sample-digest.md"
    try:
        r = requests.get(url, timeout=10)
        return r.text if r.status_code == 200 else "获取失败"
    except:
        return "连接超时"

# ================= 3. 导航栏 =================
selected = option_menu(
    menu_title=None,
    options=["AI 产品进展", "知名博主动态", "AI 学习资料库"],
    icons=["rocket-takeoff", "person-badge", "book"],
    orientation="horizontal",
    styles={
        "container": {"background-color": "#fbfbfd"},
        "nav-link-selected": {"background-color": "#E60012", "color": "white"}
    }
)

# ================= 4. 路由逻辑 =================

# --- 页面 1: AI 产品进展 ---
if selected == "AI 产品进展":
    st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🚀 AI 产品进展</h1>", unsafe_allow_html=True)
    
    df = load_data()
    
    if not df.empty:
        # --- 补回筛选逻辑 ---
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            month_list = sorted(df['选择月份'].unique()) if '选择月份' in df.columns else []
            month_filter = st.multiselect("📅 时间范围", options=month_list)
        with c2:
            cat_list = sorted(df['分类'].unique()) if '分类' in df.columns else []
            category_filter = st.multiselect("🏷️ 产品分类", options=cat_list)
        with c3:
            comp_list = sorted(df['公司'].unique()) if '公司' in df.columns else []
            company_filter = st.multiselect("🏢 所属公司", options=comp_list)
        st.markdown('</div>', unsafe_allow_html=True)

        # 执行过滤
        filtered_df = df.copy()
        if month_filter:
            filtered_df = filtered_df[filtered_df['选择月份'].isin(month_filter)]
        if category_filter:
            filtered_df = filtered_df[filtered_df['分类'].isin(category_filter)]
        if company_filter:
            filtered_df = filtered_df[filtered_df['公司'].isin(company_filter)]

        # 网格展示
        cols_per_row = 3
        for i in range(0, len(filtered_df), cols_per_row):
            batch = filtered_df.iloc[i : i + cols_per_row]
            cols = st.columns(cols_per_row)
            for idx, (index, row) in enumerate(batch.iterrows()):
                with cols[idx]:
                    # 使用 HTML 拼接，确保样式精准
                    st.markdown(f"""
                    <div class="product-card">
                        <div style="font-size:12px;color:#86868b;font-weight:600;">{row.get('公司','-')} · {row.get('日期','-')}</div>
                        <h3 style="font-size:19px;margin:10px 0;">{row.get('进展','-')}</h3>
                        <div style="margin-bottom:12px;">
                            <span class="tag tag-highlight">{row.get('分类','-')}</span>
                            <span class="tag">{row.get('地域','-')}</span>
                        </div>
                        <p style="font-size:14px;color:#424245;line-height:1.5;">{row.get('核心特点','-')}</p>
                        <div class="insight-quote">
                            <b>市场反馈：</b>{row.get('市场反响','-')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("💡 请在 Secrets 中配置 gsheet_url 并确保表格已发布。")

# --- 页面 2: 知名博主动态 ---
elif selected == "知名博主动态":
    st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🏗️ 建造者动态 (Follow Builders)</h1>", unsafe_allow_html=True)
    st.markdown('<div class="insight-quote" style="border-left: 4px solid #0071e3;"><b>追踪逻辑：</b>聚合来自 Karpathy 等 25 位 Top Builder 及顶级播客的每日摘要。</div>', unsafe_allow_html=True)
    
    raw_content = fetch_github_content()
    
    if "PODCASTS" in raw_content:
        # 简单结构化渲染
        st.markdown("### 🎧 播客精选")
        pod_text = raw_content.split("PODCASTS")[1].split("X / TWITTER")[0]
        st.markdown(f'<div class="product-card" style="background:#FBFBFD;">{pod_text}</div>', unsafe_allow_html=True)
        
        st.markdown("### 🐦 社交媒体洞察")
        x_text = raw_content.split("X / TWITTER")[1].split("Reply to")[0]
        st.markdown(f'<div class="product-card">{x_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(raw_content)

# --- 页面 3: 学习资料库 ---
elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center;'>📚 知识库</h1>", unsafe_allow_html=True)
    st.info("内容同步中，敬请期待...")
