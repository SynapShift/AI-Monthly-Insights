import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def load_gsheet():
    """
    直接从 Streamlit secrets 读取 Google Sheet CSV URL
    """
    url = st.secrets["gsheet_url"]  # 注意：这里用强制读取，不再 get()

    df = pd.read_csv(url)
    return df


def clean_ai_products(df: pd.DataFrame):
    if df.empty:
        return df

    rename_map = {
        "选择月份": "month",
        "日期": "date",
        "分类": "category",
        "地域": "region",
        "公司": "company",
        "进展": "progress",
        "核心特点": "feature",
        "市场反响": "reaction",
    }

    return df.rename(columns=rename_map)
