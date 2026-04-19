import pandas as pd
import streamlit as st

GSHEET_URL = st.secrets.get("gsheet_url", "")

@st.cache_data(ttl=300)
def load_gsheet():
    """
    兼容 Google Sheet CSV 导出链接
    """
    if not GSHEET_URL:
        return pd.DataFrame()

    # 如果你是公开 sheet，一般用这个格式：
    # https://docs.google.com/spreadsheets/d/{id}/export?format=csv

    df = pd.read_csv(GSHEET_URL)
    return df


def clean_ai_products(df: pd.DataFrame):
    """
    标准化字段（防止sheet乱）
    """
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

    df = df.rename(columns=rename_map)
    return df
