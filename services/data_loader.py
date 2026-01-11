import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from dateutil.parser import parse

DATE_KEYS = ["дат", "date", "время", "период", "день", "data"]
CAT_KEYS = ["кат", "товар", "групп", "категория", "продукт", "item", "ассортимент"]
LOSS_KEYS = ["сумм", "потер", "убыт", "спис", "loss", "shrinkage", "убыток", "списание", "amount", "value"]
STORE_KEYS = ["маг", "магаз", "store", "точк", "филиал", "shop", "outlet", "location", "point", "адрес", "город"]

def normalize_name(col):
    return str(col).strip().lower()

def detect_columns_auto(df: pd.DataFrame):
    df.columns = [normalize_name(c) for c in df.columns]
    cols = df.columns
    date_col = cat_col = loss_col = store_col = None
    for c in cols:
        if any(k in c for k in DATE_KEYS) and date_col is None:
            date_col = c
        elif any(k in c for k in CAT_KEYS) and cat_col is None:
            cat_col = c
        elif any(k in c for k in LOSS_KEYS) and loss_col is None:
            loss_col = c
        elif any(k in c for k in STORE_KEYS) and store_col is None:
            store_col = c
    if date_col is None and len(cols) > 0: date_col = cols[0]
    if cat_col is None and len(cols) > 1: cat_col = cols[1]
    if loss_col is None and len(cols) > 2: loss_col = cols[2]
    if store_col is None and len(cols) > 3: store_col = cols[3]
    return date_col, cat_col, loss_col, store_col

@st.cache_data
def _read_excel(f):
    return pd.read_excel(f, engine='openpyxl')

@st.cache_data
def generate_test_data():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=300, freq='D')
    categories = np.random.choice(['Смартфоны', 'Ноутбуки', 'Телевизоры', 'Холодильники'], 300)
    amounts = np.random.uniform(500, 8500, 300).round(2)
    stores = np.random.choice(['Маг1', 'Маг2', 'Маг3', 'Маг4', 'Маг5'], 300)
    return pd.DataFrame({'Дата': dates.strftime('%d.%m.%Y'), 'Категория': categories, 'СуммаПотерь': amounts, 'Магазин': stores})

def parse_date_auto(series):
    parsed = []
    for val in series.dropna().astype(str).head(100):
        try:
            parsed.append(parse(val, dayfirst=None, yearfirst=None))
        except:
            continue
    if parsed:
        return pd.to_datetime(series.apply(lambda x: parse(str(x), dayfirst=None, yearfirst=None) if pd.notnull(x) else pd.NaT), errors='coerce')
    return pd.to_datetime(series, errors='coerce')

@st.cache_data
def load_uploaded_or_test_data(uploaded_file, use_test_data):
    if uploaded_file is not None:
        df_raw = _read_excel(uploaded_file)
        date_col, cat_col, loss_col, store_col = detect_columns_auto(df_raw)
        rename_dict = {date_col: 'Дата', cat_col: 'Категория', loss_col: 'СуммаПотерь', store_col: 'Магазин'}
        df_raw = df_raw.rename(columns=rename_dict)
        if 'Дата' not in df_raw.columns:
            df_raw['Дата'] = pd.date_range(start='2025-01-01', periods=len(df_raw), freq='D')
        else:
            df_raw['Дата'] = parse_date_auto(df_raw['Дата'])
        return df_raw

    if use_test_data:
        df_raw = generate_test_data()
        df_raw['Дата'] = pd.to_datetime(df_raw['Дата'], format='%d.%m.%Y')
        return df_raw

    return pd.DataFrame()