# ui/tabs/forecast_tab.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.seasonal import seasonal_decompose

# ---------- кэшированные вспомогательные функции ----------
@st.cache_data
def get_forecast(_df: pd.DataFrame, horizon: int):
    """
    Строит прогноз потерь методом Prophet.
    Возвращает: forecast, модель, исторические данные (prophet_df)
    """
    daily = _df.groupby('Дата', as_index=False)['СуммаПотерь'].sum()
    daily = daily.sort_values('Дата')
    prophet_df = daily.rename(columns={'Дата': 'ds', 'СуммаПотерь': 'y'})

    m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
    m.fit(prophet_df)

    future = m.make_future_dataframe(periods=horizon)
    forecast = m.predict(future)
    return forecast, m, prophet_df


@st.cache_data
def decompose_series(_df: pd.DataFrame):
    """
    Декомпозиция временного ряда (тренд, сезонность, остатки).
    Период = 7 (неделя).
    """
    daily_series = _df.groupby('Дата')['СуммаПотерь'].sum().resample('D').sum().fillna(0)
    if len(daily_series) < 14:
        return None
    result = seasonal_decompose(daily_series, model='additive', period=7)
    return result, daily_series


# ---------- основная функция-таб ----------
def render_forecast_tab(df: pd.DataFrame, plotly_template: str, download_config: dict):
    horizon = st.slider("Горизонт прогноза (дней)", 30, 180, 90)

    with st.spinner("Расчёт прогноза Prophet..."):
        forecast, model, hist = get_forecast(df, horizon)

    # --- график прогноза ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist['ds'], y=hist['y'], mode='lines', name='Исторические данные'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Прогноз'))
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_lower'],
        mode='lines', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_upper'],
        mode='lines', fill='tonexty', name='Доверительный интервал'))
    fig.update_layout(template=plotly_template, title="Прогноз потерь")
    st.plotly_chart(fig, config=download_config)

    future_losses = forecast[forecast['ds'] > df['Дата'].max()]['yhat'].sum()
    st.metric("Прогнозируемые потери за выбранный горизонт", f"{future_losses:,.0f}₽")

    # --- декомпозиция ---
    decomp = decompose_series(df)
    if decomp is None:
        st.info("Недостаточно данных для декомпозиции")
        return forecast, hist, future_losses

    decompose_result, _ = decomp
    col1, col2, col3 = st.columns(3)

    with col1:
        fig_trend = px.line(x=decompose_result.trend.index, y=decompose_result.trend,
                            title="Тренд", template=plotly_template)
        st.plotly_chart(fig_trend, config=download_config)

    with col2:
        fig_seasonal = px.line(x=decompose_result.seasonal.index, y=decompose_result.seasonal,
                               title="Сезонность", template=plotly_template)
        st.plotly_chart(fig_seasonal, config=download_config)

    with col3:
        fig_resid = px.line(x=decompose_result.resid.index, y=decompose_result.resid,
                            title="Остатки", template=plotly_template)
        st.plotly_chart(fig_resid, config=download_config)

    return forecast, hist, future_losses