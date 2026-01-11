import streamlit as st

def setup_theme():
    dark_mode = st.sidebar.toggle("Тёмная тема", value=False)
    if dark_mode:
        colors = {"bg_color": "#0e1117", "text_color": "#fafafa", "secondary_bg": "#262730", "card_bg": "#1e2130"}
        plotly_template = "plotly_dark"
        reds_scale = "Reds"
    else:
        colors = {"bg_color": "#ffffff", "text_color": "#000000", "secondary_bg": "#f8f9fa", "card_bg": "#ffffff"}
        plotly_template = "plotly"
        reds_scale = "Reds"
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {colors["bg_color"]}; color: {colors["text_color"]}; }}
    .card {{ background-color: {colors["card_bg"]}; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)
    return dark_mode, colors, plotly_template, reds_scale

def render_header(colors):
    st.markdown("""
    <div class="card" style="text-align:center;">
    <h1 style="color:#e74c3c;margin:0;">📉 RetailLoss Sentinel</h1>
    <p style="font-size:1.2rem;margin:10px 0;">Интеллектуальный анализ потерь в рознице • What-if • ABC/XYZ • Pareto • Прогноз • Аномалии • Кластеры</p>
    </div>
    """, unsafe_allow_html=True)