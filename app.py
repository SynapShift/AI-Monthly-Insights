import streamlit as st
import pandas as pd
import requests

from streamlit_option_menu import option_menu

# 1. 基础配置
st.set_page_config(page_title="AI 行业洞察", layout="wide", page_icon="🚀")

# 2. 样式注入
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 2rem;}
.stApp {background-color: #FFFFFF;}
.product-card {background-color: #FFFFFF; border: 1px solid #F2F2F2; padding: 24px; border-radius: 12px; margin-bottom: 20px; transition: all 0.3s ease;}
.tag {display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-right: 8px; background-color: #F5F5F7; color: #1D1D1F;}
.tag-highlight {background-color: #E60012; color: white;}
.insight-quote {background-color: #FBFBFD; padding: 15px; border-radius: 8px; font-size: 14px; border-left: 4px solid #E60012; color: #424245; margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

# 3. 数据函数定义


@st.cache_data(ttl=600)
def load_data():
    # 从 Secrets 获取你的表格链接
    full_url = st.secrets.get("gsheet_url", "")
    if not full_url:
        st.error("请在 Secrets 中配置 gsheet_url")
        return pd.DataFrame()
    
    try:
        # 核心逻辑：将普通 Google Sheet 链接转为 CSV 下载链接
        # 这样就不需要任何额外的安装包了
        if "/edit" in full_url:
            csv_url = full_url.split("/edit")[0] + "/export?format=csv"
            # 如果有多个 sheet，可以在后面加 &gid=xxxx
        else:
            csv_url = full_url
            
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"表格读取失败: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_follow_builders_feed():
    # 根据其工作原理，它有一个中心化的 feed 地址
    # 在该项目中，通常是这个 raw 链接（或指向其后端 API）
    feed_url = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/data/feed.json"
    
    try:
        response = requests.get(feed_url, timeout=10)
        if response.status_code == 200:
            return response.json() # 这是一个包含原始内容的 JSON
        else:
            # 如果 json 不存在，尝试读取它的示例输出作为兜底
            sample_url = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/examples/sample-digest.md"
            r = requests.get(sample_url, timeout=10)
            return r.text
    except Exception as e:
        return f"数据连接失败: {str(e)}"

# 4. 导航栏
selected = option_menu(
    menu_title=None,
    options=["AI 产品进展", "知名博主动态", "AI 学习资料库"],
    icons=["rocket-takeoff", "person-badge", "book"],
    orientation="horizontal",
    styles={"nav-link-selected": {"background-color": "#E60012"}}
)

# 5. 路由逻辑 (严格对齐)
if selected == "AI 产品进展":
    df = load_data()
    st.markdown("<h1 style='text-align: center;'>🚀 AI 产品进展</h1>", unsafe_allow_html=True)
    if not df.empty:
        cols_per_row = 3
        for i in range(0, len(df), cols_per_row):
            batch = df.iloc[i : i + cols_per_row]
            cols = st.columns(cols_per_row)
            for idx, (index, row) in enumerate(batch.iterrows()):
                with cols[idx]:
                    html = f"""
                    <div class="product-card">
                        <div style="font-size:12px;color:#86868b;">{row.get('公司','-')} | {row.get('日期','-')}</div>
                        <h2 style="font-size:20px;">{row.get('进展','-')}</h2>
                        <div style="margin:10px 0;"><span class="tag tag-highlight">{row.get('分类','-')}</span></div>
                        <p style="font-size:14px;color:#424245;height:60px;overflow:hidden;">{row.get('核心特点','-')}</p>
                        <div class="insight-quote"><b>反馈:</b> {row.get('市场反响','-')}</div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("数据加载中或配置有误...")

if selected == "AI 产品进展":
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>🚀 AI 产品进展</h1>", unsafe_allow_html=True)
    


###知名博主
elif selected == "知名博主动态":
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>🏗️ 建造者动态 (Follow Builders)</h1>", unsafe_allow_html=True)
    
    # 1. 获取内容（这里依然用你获取到的那段 Sample 文本）
    raw_content = fetch_follow_builders_feed() # 假设这里返回了你刚才贴出的那段文本
    
    # 2. UI 顶部的提示词
    st.markdown(f"""
    <div class="insight-quote" style="border-left: 4px solid #0071e3; margin-bottom: 25px;">
        <b>💡 追踪逻辑：</b> 聚合来自 Karpathy 等 25 位 Top Builder 及 6 个顶级 AI 播客的每日摘要。
    </div>
    """, unsafe_allow_html=True)


    
    # 3. 结构化展示 - 播客部分
    if "PODCASTS" in raw_content:
        st.subheader("🎧 顶级 AI 播客精选")
        # 简单解析：按播客名称分割（这里用正则或字符串分割模拟）
        pod_sections = raw_content.split("PODCASTS")[1].split("X / TWITTER")[0].split("\n\n")
        
        for pod in pod_sections:
            if "—" in pod:
                name, detail = pod.split("—", 1)
                st.markdown(f"""
                <div class="product-card" style="border-left: 5px solid #E60012;">
                    <div style="color: #E60012; font-weight: 700; font-size: 14px; margin-bottom: 5px;">Podcast</div>
                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 10px;">{name.strip()}</div>
                    <div style="font-size: 14px; color: #1d1d1f; line-height: 1.6; background: #f5f5f7; padding: 12px; border-radius: 8px;">
                        {detail.strip()}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 4. 结构化展示 - X/Twitter 部分
    if "X / TWITTER" in raw_content:
        st.markdown("---")
        st.subheader("🐦 建造者观点 (X/Twitter)")
        x_sections = raw_content.split("X / TWITTER")[1].split("Reply to adjust")[0].split("\n")
        
        # 过滤掉空行
        x_items = [item for item in x_sections if "@" in item]
        
        cols = st.columns(2) # 左右两栏布局
        for idx, item in enumerate(x_items):
            with cols[idx % 2]:
                # 提取博主名
                parts = item.split(" ", 2)
                name = parts[0] + " " + parts[1] if len(parts) > 1 else "Builder"
                insight = parts[2] if len(parts) > 2 else item
                
                st.markdown(f"""
                <div class="product-card" style="min-height: 180px;">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <div style="width: 32px; height: 32px; background: #000; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; margin-right: 10px;">X</div>
                        <div style="font-weight: 600; font-size: 15px;">{name}</div>
                    </div>
                    <div style="font-size: 13px; color: #424245; line-height: 1.5;">{insight}</div>
                </div>
                """, unsafe_allow_html=True)


###知名博主

elif selected == "AI 学习资料库":
    st.markdown("<h1 style='text-align: center;'>📚 知识库</h1>", unsafe_allow_html=True)
    st.info("内容同步中...")
