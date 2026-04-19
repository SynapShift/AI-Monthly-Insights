import pandas as pd
import streamlit as st


def to_csv_url(url: str) -> str:
    """
    把 Google Sheet 的 edit 链接转换为 CSV 导出链接
    """
    if "/edit" in url:
        base = url.split("/edit")[0]
        return base + "/export?format=csv"
    return url


@st.cache_data(ttl=300)
def load_gsheet():
    url = st.secrets["gsheet_url"]

    csv_url = to_csv_url(url)

    df = pd.read_csv(csv_url)
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
