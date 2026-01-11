import streamlit as st
import plotly.express as px

def render_charts_tab(df, category_losses, plotly_template, reds_scale, download_config):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Динамика по месяцам")
        df['Месяц'] = df['Дата'].dt.to_period('M').astype(str)
        monthly = df.groupby('Месяц')['СуммаПотерь'].sum().reset_index()
        fig = px.line(monthly, x='Месяц', y='СуммаПотерь', markers=True, template=plotly_template)
        st.plotly_chart(fig, config=download_config)

    with col2:
        st.subheader("Тепловая карта (день недели × категория)")
        df['День недели'] = df['Дата'].dt.day_name()
        pivot = df.pivot_table(values='СуммаПотерь', index='Категория', columns='День недели', aggfunc='sum', fill_value=0)
        fig = px.imshow(pivot, color_continuous_scale=reds_scale, template=plotly_template, text_auto=True)
        st.plotly_chart(fig, config=download_config)

    st.subheader("Корреляция потерь между категориями (топ-15)")
    top_cats = category_losses.head(15)['Категория'].tolist()
    df_corr = df[df['Категория'].isin(top_cats)].copy()
    df_corr['Дата'] = df_corr['Дата'].dt.date
    pivot_corr = df_corr.pivot_table(index='Дата', columns='Категория', values='СуммаПотерь', aggfunc='sum', fill_value=0)
    corr = pivot_corr.corr()
    fig = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu', zmin=-1, zmax=1, template=plotly_template)
    st.plotly_chart(fig, config=download_config)