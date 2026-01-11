import streamlit as st

def render_recommendations_tab(total_savings, annual_savings, roi_display):
    st.subheader("💡 Приоритетные рекомендации")
    st.success(f"Общий потенциал экономии: **{total_savings:,.0f}₽** ({annual_savings:,.0f}₽ в год) при ROI {roi_display}")
    st.markdown("""
    **Ключевые меры:**
    1. Усилить контроль в категориях **A-класса** (80 % потерь)
    2. Провести аудит топ-магазинов (Pareto 80/20)
    3. Внедрить меры в пиковые дни (выходные)
    4. Особое внимание к категориям с высокой вариабельностью (**Z-класс**)
    5. Расследовать выявленные аномалии
    """)