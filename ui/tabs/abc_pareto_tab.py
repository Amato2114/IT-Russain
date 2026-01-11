import streamlit as st
import plotly.express as px

def render_abc_pareto_tab(abc_xyz, pareto_store, plotly_template, reds_scale, download_config):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ABC-анализ категорий")
        st.dataframe(abc_xyz[['Категория', 'СуммаПотерь', 'Доля_%', 'ABC']])
        st.subheader("XYZ-анализ (вариабельность)")
        st.dataframe(abc_xyz[['Категория', 'CV', 'XYZ']])
    with col2:
        st.subheader("ABC-XYZ матрица")
        matrix = abc_xyz.groupby(['ABC', 'XYZ']).size().unstack(fill_value=0)
        fig = px.imshow(matrix, text_auto=True, color_continuous_scale=reds_scale, template=plotly_template)
        st.plotly_chart(fig, config=download_config)
        st.subheader("Pareto магазинов")
        st.dataframe(pareto_store[['Магазин', 'СуммаПотерь', 'Доля_%', 'Накопительная_доля']])