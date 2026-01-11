import streamlit as st
import pandas as pd
import os
from datetime import datetime
from services.data_loader import load_uploaded_or_test_data
from services.analytics import calculate_metrics
from services.filters import apply_filters
from ui.sidebar import render_sidebar_filters_and_scenarios
from ui.styles import setup_theme, render_header
from ui.auth import sidebar_auth_and_upload, logout
from ui.tabs.overview_tab import render_overview_tab
from ui.tabs.charts_tab import render_charts_tab
from ui.tabs.anomalies_tab import render_anomalies_tab
from ui.tabs.abc_pareto_tab import render_abc_pareto_tab
from ui.tabs.forecast_tab import render_forecast_tab
from ui.tabs.recommendations_tab import render_recommendations_tab
import secrets

# ---------- page ----------
st.set_page_config(page_title="RetailLoss Sentinel", layout="wide", page_icon="📉")
dark_mode, colors, plotly_template, reds_scale = setup_theme()
render_header(colors)

# ---------- CSRF ----------
if "csrf" not in st.session_state:
    st.session_state["csrf"] = secrets.token_urlsafe(16)

# ---------- auth ----------
with st.sidebar:
    uploaded_file, use_test_data = sidebar_auth_and_upload()

# ---------- logs button (admin) ----------
LOG_FILE = "logs/login_log.csv"
if st.session_state.get("user") == "admin":
    with st.sidebar:
        if st.button("📋 Логи входов"):
            st.session_state["show_logs"] = True

if st.session_state.get("show_logs"):
    st.subheader("📋 Логи входов")
    if os.path.exists(LOG_FILE):
        logs = pd.read_csv(LOG_FILE)
        st.dataframe(logs)
        st.download_button("📥 Скачать логи", data=logs.to_csv(index=False), file_name="login_log.csv")
    else:
        st.info("Логи пока пусты.")
    st.divider()

# ---------- data ----------
df_raw = load_uploaded_or_test_data(uploaded_file, use_test_data)
if df_raw is None or df_raw.empty:
    st.info("📤 Загрузите файл или используйте тестовые данные")
    st.stop()

# ---------- filters ----------
with st.sidebar:
    filters, scenarios = render_sidebar_filters_and_scenarios(df_raw)

df = apply_filters(df_raw, filters["selected_stores"], filters["selected_categories"], filters["date_range"])
if df.empty:
    st.warning("По выбранным фильтрам данных нет")
    st.stop()

# ---------- metrics ----------
period_days = (filters["date_range"][1] - filters["date_range"][0]).days + 1
(current_losses, category_losses, store_losses, abc_xyz, pareto_store,
 a_class_loss, peak_days_loss, top_store_loss) = calculate_metrics(df)

savings_a     = round(a_class_loss   * scenarios["reduce_a"] / 100)
savings_peak  = round(peak_days_loss * scenarios["reduce_peak"] / 100)
savings_store = round(top_store_loss * scenarios["reduce_top_store"] / 100)
total_savings = savings_a + savings_peak + savings_store
annual_savings= round(total_savings * (365 / period_days)) if period_days else 0
roi           = round(total_savings / scenarios["investments"] * 100, 1) if scenarios["investments"] and total_savings else 0
roi_display   = f"{roi:.1f}%" if scenarios["investments"] else "—"

# ---------- top card ----------
st.markdown(f"""
<div class="card" style="text-align:center;">
<h1 style="color:#e74c3c;margin:0;">{current_losses:,.0f}₽</h1>
<p style="font-size:1.2rem;margin:10px 0;">Общие потери за период</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📊 Потенциальная экономия (What-if)")
cols = st.columns(5)
cols[0].metric("A-класс", f"{savings_a:,.0f}₽", f"-{scenarios['reduce_a']}%")
cols[1].metric("Пиковые дни", f"{savings_peak:,.0f}₽", f"-{scenarios['reduce_peak']}%")
cols[2].metric("Топ-магазины (80%)", f"{savings_store:,.0f}₽", f"-{scenarios['reduce_top_store']}%")
cols[3].metric("Итого за период", f"{total_savings:,.0f}₽")
cols[4].metric("Годовая экономия", f"{annual_savings:,.0f}₽")
if scenarios["investments"]:
    st.metric("ROI (возврат инвестиций)", roi_display)

st.divider()

# ---------- tabs ----------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Обзор", "📈 Графики", "🔍 Аномалии + Кластеры",
    "📦 ABC / XYZ / Pareto", "📅 Прогноз", "💡 Рекомендации"
])
download_config = {"toImageButtonOptions": {"format": "svg", "filename": "chart", "height": 600, "width": 800, "scale": 1}, "displaylogo": False}

with tab1:
    render_overview_tab(df, current_losses, category_losses, store_losses, plotly_template, reds_scale, download_config)
with tab2:
    render_charts_tab(df, category_losses, plotly_template, reds_scale, download_config)
with tab3:
    anomalies = render_anomalies_tab(df, plotly_template, download_config)
with tab4:
    render_abc_pareto_tab(abc_xyz, pareto_store, plotly_template, reds_scale, download_config)
with tab5:
    forecast, hist, future_losses = render_forecast_tab(df, plotly_template, download_config)
with tab6:
    render_recommendations_tab(total_savings, annual_savings, roi_display)

# ---------- Excel export ----------
import io
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Исходные данные', index=False)
    category_losses.to_excel(writer, sheet_name='По категориям', index=False)
    pareto_store.to_excel(writer, sheet_name='По магазинам', index=False)
    abc_xyz.to_excel(writer, sheet_name='ABC-XYZ', index=False)
    if 'anomalies' in locals() and anomalies is not None and not anomalies.empty:
        anomalies.to_excel(writer, sheet_name='Аномалии', index=False)
    pd.DataFrame({
        'Сценарий': ['A-класс', 'Пиковые дни', 'Топ-магазины (80%)', 'Итого'],
        'Снижение %': [scenarios['reduce_a'], scenarios['reduce_peak'], scenarios['reduce_top_store'], '-'],
        'Экономия ₽': [savings_a, savings_peak, savings_store, total_savings],
        'Годовая экономия ₽': [
            round(savings_a * 365 / period_days),
            round(savings_peak * 365 / period_days),
            round(savings_store * 365 / period_days),
            annual_savings
        ]
    }).to_excel(writer, sheet_name='What-if', index=False)

buffer.seek(0)
st.download_button("📥 Скачать полный отчёт Excel", data=buffer, file_name=f"RetailLoss_Report_{datetime.now().strftime('%Y-%m-%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.caption("RetailLoss Sentinel • Январь 2026 • Все права защищены")