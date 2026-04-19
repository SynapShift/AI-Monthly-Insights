import streamlit as st

st.set_page_config(page_title="Learning", layout="wide")

st.title("📚 AI 学习资料")

materials = [
    {
        "title": "CS336 - LLM Systems",
        "desc": "Stanford 大模型系统课程",
        "link": "https://example.com"
    },
    {
        "title": "Transformer 原理",
        "desc": "Attention is all you need",
        "link": "https://arxiv.org/abs/1706.03762"
    }
]

for m in materials:
    with st.container():
        st.subheader(m["title"])
        st.write(m["desc"])
        st.markdown(f"[打开链接]({m['link']})")
        st.divider()
