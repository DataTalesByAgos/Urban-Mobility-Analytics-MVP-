"""Overview page – KPIs + resumen del proyecto"""
import streamlit as st
import pandas as pd
from dashboard.components.translations import t

@st.cache_data
def load_metrics():
    return pd.read_parquet("data/processed/mobility_metrics.parquet")

@st.cache_data
def load_stops():
    return pd.read_parquet("data/processed/stops.parquet")

@st.cache_data
def load_routes():
    return pd.read_parquet("data/processed/routes.parquet")

@st.cache_data
def load_edges():
    return pd.read_parquet("data/processed/edges.parquet")

def render():
    # Hero
    st.markdown(f"""
    <div class="hero">
        <h1>{t('ov_title')}</h1>
        <p>{t('ov_subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)

    metrics_df = load_metrics()
    stops_df   = load_stops()
    routes_df  = load_routes()
    edges_df   = load_edges()

    total_trips    = int(metrics_df["total_transacciones"].sum())
    avg_daily      = int(metrics_df["total_transacciones"].mean())
    max_daily      = int(metrics_df["total_transacciones"].max())
    avg_ratio      = float(metrics_df["viajes_por_tarjeta"].mean())

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">{t('kpi_transactions')}</div>
            <div class="value">{total_trips:,.0f}</div>
            <div class="delta">{t('kpi_transactions_sub')}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">{t('kpi_avg_daily')}</div>
            <div class="value">{avg_daily:,.0f}</div>
            <div class="delta">{t('kpi_avg_daily_sub')}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="label">{t('kpi_peak_daily')}</div>
            <div class="value">{max_daily:,.0f}</div>
            <div class="delta">{t('kpi_peak_daily_sub')}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="label">{t('kpi_ratio')}</div>
            <div class="value">{avg_ratio:.2f}</div>
            <div class="delta">{t('kpi_ratio_sub')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick charts
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(f"#### {t('chart_ov_title')}")
        import plotly.express as px
        fig = px.area(
            metrics_df, x="DIA_TRANSPORTE", y="total_transacciones",
            color_discrete_sequence=["#38bdf8"],
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.8)",
            xaxis_title="", yaxis_title=t('chart_ov_y'),
            hovermode="x unified", margin=dict(l=0, r=0, t=10, b=0),
            height=300,
        )
        fig.update_traces(fill="tozeroy", line_width=2)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown(f"#### {t('ov_network_info')}")
        st.markdown(f"""
        | {t('ov_indicator')} | {t('ov_value')} |
        |---|---|
        | {t('ov_stops')} | **{len(stops_df):,}** |
        | {t('ov_lines')} | **{len(routes_df):,}** |
        | {t('ov_edges')} | **{len(edges_df):,}** |
        """)
        st.info(t('ov_link_msg'))

    # Footer note
    st.markdown("---")
    st.markdown(
        f"<small>{t('ov_sources')}</small>",
        unsafe_allow_html=True
    )
