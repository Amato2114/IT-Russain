import streamlit as st

@st.cache_data
def apply_filters(df_raw, selected_stores, selected_categories, date_range):
    df = df_raw.copy()
    if 'Все' not in selected_stores:
        df = df[df['Магазин'].isin(selected_stores)]
    if 'Все' not in selected_categories:
        df = df[df['Категория'].isin(selected_categories)]
    df = df[(df['Дата'].dt.date >= date_range[0]) & (df['Дата'].dt.date <= date_range[1])]
    return df