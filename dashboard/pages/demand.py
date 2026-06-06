"""Demand analysis page"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def load_metrics():
    return pd.read_parquet("data/processed/mobility_metrics.parquet")

@st.cache_data
def load_transactions():
    return pd.read_parquet("data/processed/sube_transactions.parquet")

def render():
    st.markdown("## 📈 Análisis de Demanda SUBE")
    st.markdown("Serie temporal de movilidad, usuarios activos e indicadores derivados para 2025.")

    metrics_df = load_metrics()
    tx_df      = load_transactions()

    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        date_range = st.date_input(
            "Rango de fechas",
            value=(metrics_df["DIA_TRANSPORTE"].min(), metrics_df["DIA_TRANSPORTE"].max()),
        )
    with col_f2:
        agg = st.selectbox("Agregación", ["Diaria", "Semanal", "Mensual"])

    # Filter
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[-1])
    mask = (metrics_df["DIA_TRANSPORTE"] >= start) & (metrics_df["DIA_TRANSPORTE"] <= end)
    df = metrics_df[mask].copy()

    if agg == "Semanal":
        df = df.set_index("DIA_TRANSPORTE").resample("W").sum(numeric_only=True).reset_index()
    elif agg == "Mensual":
        df = df.set_index("DIA_TRANSPORTE").resample("ME").sum(numeric_only=True).reset_index()
        df["viajes_por_tarjeta"] = (df["total_transacciones"] / df["total_tarjetas_activas"]).round(3)

    # ── Chart 1: Transactions + Cards ────────────────────────────────
    st.markdown("#### Transacciones vs Tarjetas activas")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df["DIA_TRANSPORTE"], y=df["total_transacciones"],
        name="Transacciones", line=dict(color="#38bdf8", width=2),
        fill="tozeroy", fillcolor="rgba(56,189,248,.15)"
    ))
    fig1.add_trace(go.Scatter(
        x=df["DIA_TRANSPORTE"], y=df["total_tarjetas_activas"],
        name="Tarjetas activas", line=dict(color="#a78bfa", width=2),
        fill="tozeroy", fillcolor="rgba(167,139,250,.1)"
    ))
    fig1.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,.8)", hovermode="x unified",
        legend=dict(orientation="h", y=1.1), height=380,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ── Chart 2: Viajes/tarjeta ───────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Intensidad de uso (viajes / tarjeta)")
        fig2 = px.bar(
            df, x="DIA_TRANSPORTE", y="viajes_por_tarjeta",
            color="viajes_por_tarjeta", color_continuous_scale="Blues",
            template="plotly_dark"
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,.8)",
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False, xaxis_title="", yaxis_title="Ratio"
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("#### Distribución por tipo de transporte")
        tipo_df = (
            tx_df[tx_df["DIA_TRANSPORTE"].between(str(start.date()), str(end.date()))]
            .groupby("TIPO_TRANSPORTE")["CANTIDAD"].sum()
            .reset_index()
            .sort_values("CANTIDAD", ascending=False)
        )
        fig3 = px.pie(
            tipo_df, names="TIPO_TRANSPORTE", values="CANTIDAD",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            hole=0.45, template="plotly_dark"
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=300,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Stats table ───────────────────────────────────────────────────
    st.markdown("#### Estadísticas del período")
    stats = df[["total_transacciones", "total_tarjetas_activas", "viajes_por_tarjeta"]].describe().round(2)
    st.dataframe(stats, use_container_width=True)
