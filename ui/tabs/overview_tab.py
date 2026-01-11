import streamlit as st
import plotly.express as px

def render_overview_tab(df, current_losses, category_losses, store_losses, plotly_template, reds_scale, download_config):
    cols = st.columns(4)
    cols[0].metric("Потери", f"{current_losses:,.0f}₽")
    cols[1].metric("Категорий", df['Категория'].nunique())
    cols[2].metric("Магазинов", df['Магазин'].nunique())
    cols[3].metric("Записей", f"{len(df):,}")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Топ-10 категорий")
        fig = px.bar(category_losses.head(10), x='Категория', y='СуммаПотерь', text_auto='.0f', color='СуммаПотерь', color_continuous_scale=reds_scale, template=plotly_template)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, config=download_config)
    with col2:
        st.subheader("Топ-10 магазинов")
        fig = px.bar(store_losses.head(10), x='Магазин', y='СуммаПотерь', text_auto='.0f', color='СуммаПотерь', color_continuous_scale=reds_scale, template=plotly_template)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, config=download_config)