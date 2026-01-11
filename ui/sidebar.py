import streamlit as st
from datetime import date

def render_sidebar_filters_and_scenarios(df_raw):
    """
    Возвращает словари:
        filters = {
            "selected_stores": [...],
            "selected_categories": [...],
            "date_range": (start, end)
        }
        scenarios = {
            "reduce_a": int,
            "reduce_peak": int,
            "reduce_top_store": int,
            "investments": int
        }
    """
    st.header("⚙️ Фильтры")

    # ---------- магазины ----------
    # если колонки «Магазин» нет – подменяем фейковой
    if "Магазин" in df_raw.columns:
        store_values = df_raw["Магазин"].unique().tolist()
    else:
        store_values = ["Магазин1"]
    stores = ["Все"] + sorted(store_values)
    selected_stores = st.multiselect("Магазины", stores, default=["Все"])

    # ---------- категории ----------
    if "Категория" in df_raw.columns:
        cat_values = df_raw["Категория"].unique().tolist()
    else:
        cat_values = ["Без категории"]
    categories = ["Все"] + sorted(cat_values)
    selected_categories = st.multiselect("Категории", categories, default=["Все"])

    # ---------- даты ----------
    if "Дата" in df_raw.columns:
        min_date = df_raw["Дата"].min().date()
        max_date = df_raw["Дата"].max().date()
    else:
        min_date = date(2025, 1, 1)
        max_date = date(2026, 1, 1)
    date_range = st.date_input(
        "Период",
        (min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    st.divider()
    st.subheader("📊 What-if сценарии")
    reduce_a = st.slider("Снижение A-класса (%)", 0, 50, 15)
    reduce_peak = st.slider("Снижение пиковых дней (%)", 0, 50, 20)
    reduce_top_store = st.slider("Снижение в топ-магазинах (Pareto 80 %) (%)", 0, 50, 25)
    investments = st.number_input("Предполагаемые инвестиции в меры (₽)", min_value=0, value=500_000, step=10_000)

    filters = {
        "selected_stores": selected_stores,
        "selected_categories": selected_categories,
        "date_range": date_range
    }
    scenarios = {
        "reduce_a": reduce_a,
        "reduce_peak": reduce_peak,
        "reduce_top_store": reduce_top_store,
        "investments": investments
    }
    return filters, scenarios