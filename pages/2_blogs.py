import streamlit as st

st.set_page_config(page_title="Blogs", layout="wide")

st.title("🧠 知名博主动态")

# 先做静态结构，后面可以接 RSS / Twitter API
blogs = [
    {"name": "Andrej Karpathy", "content": "LLM agent 架构正在重塑软件开发"},
    {"name": "Elon Musk", "content": "Grok 强化实时推理能力"},
]

for b in blogs:
    with st.container():
        st.subheader(b["name"])
        st.write(b["content"])
        st.divider()
