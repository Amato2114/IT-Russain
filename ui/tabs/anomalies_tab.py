import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans

@st.cache_data
def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Выявляет аномалии в столбце 'СуммаПотерь' с помощью Isolation Forest.
    Возвращает подмножество строк, помеченных как аномальные.
    """
    if len(df) < 20:
        return pd.DataFrame()

    iso = IsolationForest(contamination=0.05, random_state=42)
    df_anom = df[['СуммаПотерь']].copy()
    df_anom['аномалия'] = iso.fit_predict(df_anom)

    anomalies = df.copy()
    anomalies['аномалия'] = df_anom['аномалия']
    return anomalies[anomalies['аномалия'] == -1].sort_values('СуммаПотерь', ascending=False)

@st.cache_data
def cluster_losses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Кластеризует потери на 3 группы (KMeans) и возвращает статистику по кластерам.
    """
    if len(df) < 5:
        return pd.DataFrame()

    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    df_cluster = df[['СуммаПотерь']].copy()
    df_cluster['кластер'] = kmeans.fit_predict(df_cluster)

    centers = kmeans.cluster_centers_.flatten()
    order = np.argsort(centers)
    labels = ['Низкие потери', 'Средние потери', 'Высокие потери']
    df_cluster['Кластер'] = df_cluster['кластер'].map({order[i]: labels[i] for i in range(3)})

    cluster_stats = (df_cluster
                     .groupby('Кластер')['СуммаПотерь']
                     .agg(['count', 'mean', 'min', 'max'])
                     .round(0)
                     .reindex(labels))
    return cluster_stats

def render_anomalies_tab(df: pd.DataFrame, plotly_template: str, download_config: dict):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Аномалии (Isolation Forest)")
        anomalies = detect_anomalies(df)
        if not anomalies.empty:
            st.metric("Обнаружено аномалий", len(anomalies))
            st.dataframe(anomalies[['Дата', 'Категория', 'Магазин', 'СуммаПотерь']])
        else:
            st.info("Недостаточно данных для поиска аномалий")

    with col2:
        st.subheader("Кластеризация потерь (KMeans)")
        cluster_stats = cluster_losses(df)
        if not cluster_stats.empty:
            st.dataframe(cluster_stats)
        else:
            st.info("Недостаточно данных для кластеризации")