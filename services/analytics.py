import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def calculate_metrics(df):
    current_losses = df['СуммаПотерь'].sum()
    category_losses = df.groupby('Категория')['СуммаПотерь'].sum().reset_index().sort_values('СуммаПотерь', ascending=False)
    store_losses = df.groupby('Магазин')['СуммаПотерь'].sum().reset_index().sort_values('СуммаПотерь', ascending=False)

    abc = category_losses.copy()
    abc['Доля_%'] = (abc['СуммаПотерь'] / current_losses * 100).round(2)
    abc['Накопительная_доля'] = abc['Доля_%'].cumsum()
    abc['ABC'] = abc['Накопительная_доля'].apply(lambda x: 'A' if x <= 80 else 'B' if x <= 95 else 'C')

    pareto_store = store_losses.copy()
    pareto_store['Доля_%'] = (pareto_store['СуммаПотерь'] / current_losses * 100).round(2)
    pareto_store['Накопительная_доля'] = pareto_store['Доля_%'].cumsum()
    pareto_store['Pareto_group'] = pareto_store['Накопительная_доля'].apply(lambda x: '80%' if x <= 80 else '95%' if x <= 95 else '100%')

    df['Month'] = df['Дата'].dt.to_period('M')
    monthly = df.groupby(['Категория', 'Month'])['СуммаПотерь'].sum().reset_index()
    xyz_stats = monthly.groupby('Категория')['СуммаПотерь'].agg(['mean', 'std']).reset_index()
    xyz_stats['CV'] = (xyz_stats['std'] / xyz_stats['mean'].replace(0, np.nan) * 100).fillna(0).round(1)
    xyz_stats['XYZ'] = xyz_stats['CV'].apply(lambda x: 'X' if x < 10 else 'Y' if x < 25 else 'Z')
    abc_xyz = abc.merge(xyz_stats[['Категория', 'CV', 'XYZ']], on='Категория', how='left')

    a_class_loss = abc[abc['ABC'] == 'A']['СуммаПотерь'].sum()
    df['День'] = df['Дата'].dt.day_name()
    peak_days_loss = df.groupby('День')['СуммаПотерь'].sum().nlargest(2).sum()
    top_store_loss = pareto_store[pareto_store['Pareto_group'] == '80%']['СуммаПотерь'].sum()

    return current_losses, category_losses, store_losses, abc_xyz, pareto_store, a_class_loss, peak_days_loss, top_store_loss