"""Demand analysis page"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.components.translations import t

@st.cache_data
def load_metrics():
    return pd.read_parquet("data/processed/mobility_metrics.parquet")

@st.cache_data
def load_transactions():
    return pd.read_parquet("data/processed/sube_transactions.parquet")

def render():
    st.markdown(f"## {t('dem_title')}")
    st.markdown(t('dem_subtitle'))

    metrics_df = load_metrics()
    tx_df      = load_transactions()

    # Time Filtering Selector
    data_min = metrics_df["DIA_TRANSPORTE"].min()
    data_max = metrics_df["DIA_TRANSPORTE"].max()
    lang = st.session_state.get("lang", "es")

    all_label = "📅 Todo el período / All" 

    time_filter_choices = {
        all_label: "all",
        t("time_custom"): "custom",
        t("time_month"): "month",
        t("time_quarter"): "quarter"
    }
    col_time1, col_time2, col_time3 = st.columns(3)
    
    with col_time1:
        time_mode_sel = st.selectbox(t("filter_time_mode"), list(time_filter_choices.keys()))
        time_mode = time_filter_choices[time_mode_sel]
        
    # Default: use full data range
    start_date = data_min
    end_date = data_max
    
    with col_time2:
        if time_mode == "all":
            # Show the data range as an info label — no further input needed
            st.markdown(
                f"<small style='color:#94a3b8'>📆 {data_min.strftime('%d/%m/%Y')} → {data_max.strftime('%d/%m/%Y')}</small>",
                unsafe_allow_html=True
            )
        elif time_mode == "custom":
            date_range = st.date_input(
                t('filter_date_range'),
                value=(data_min.date(), data_max.date()),
                min_value=data_min.date(),
                max_value=data_max.date(),
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date = pd.Timestamp(date_range[0])
                end_date = pd.Timestamp(date_range[1])
        elif time_mode == "month":
            months = sorted(metrics_df["DIA_TRANSPORTE"].dt.to_period("M").unique())
            month_names = {
                "2025-01": {"es": "Enero 2025", "en": "January 2025"},
                "2025-02": {"es": "Febrero 2025", "en": "February 2025"},
                "2025-03": {"es": "Marzo 2025", "en": "March 2025"},
                "2025-04": {"es": "Abril 2025", "en": "April 2025"},
                "2025-05": {"es": "Mayo 2025", "en": "May 2025"},
                "2025-06": {"es": "Junio 2025", "en": "June 2025"},
                "2025-07": {"es": "Julio 2025", "en": "July 2025"},
                "2025-08": {"es": "Agosto 2025", "en": "August 2025"},
                "2025-09": {"es": "Septiembre 2025", "en": "September 2025"},
                "2025-10": {"es": "Octubre 2025", "en": "October 2025"},
                "2025-11": {"es": "Noviembre 2025", "en": "November 2025"},
                "2025-12": {"es": "Diciembre 2025", "en": "December 2025"},
            }
            month_choices = {month_names.get(str(m), {}).get(lang, str(m)): m for m in months}
            selected_month_name = st.selectbox(t("time_month"), list(month_choices.keys()))
            selected_period = month_choices[selected_month_name]
            start_date = pd.Timestamp(selected_period.start_time)
            end_date = min(pd.Timestamp(selected_period.end_time), data_max)
        elif time_mode == "quarter":
            quarters = sorted(metrics_df["DIA_TRANSPORTE"].dt.to_period("Q").unique())
            quarter_names = {
                "2025Q1": {"es": "1° Trimestre (Ene-Mar)", "en": "1st Quarter (Jan-Mar)"},
                "2025Q2": {"es": "2° Trimestre (Abr-Jun)", "en": "2nd Quarter (Apr-Jun)"},
                "2025Q3": {"es": "3° Trimestre (Jul-Sep)", "en": "3rd Quarter (Jul-Sep)"},
                "2025Q4": {"es": "4° Trimestre (Oct-Dic)", "en": "4th Quarter (Oct-Dec)"},
            }
            quarter_choices = {quarter_names.get(str(q), {}).get(lang, str(q)): q for q in quarters}
            selected_quarter_name = st.selectbox(t("time_quarter"), list(quarter_choices.keys()))
            selected_period = quarter_choices[selected_quarter_name]
            start_date = pd.Timestamp(selected_period.start_time)
            end_date = min(pd.Timestamp(selected_period.end_time), data_max)
            
    with col_time3:
        # Limit aggregation options based on time mode to avoid nonsensical combinations:
        # - "month"  → only daily / weekly (monthly = 1 point, useless)
        # - others   → daily / weekly / monthly all valid
        if time_mode == "month":
            agg_choices = {
                t('agg_daily'): "Diaria",
                t('agg_weekly'): "Semanal",
            }
        else:
            agg_choices = {
                t('agg_daily'): "Diaria",
                t('agg_weekly'): "Semanal",
                t('agg_monthly'): "Mensual"
            }
        agg_sel = st.selectbox(t('filter_agg'), list(agg_choices.keys()))
        agg = agg_choices[agg_sel]

    # Filter
    start, end = pd.Timestamp(start_date), pd.Timestamp(end_date)
    mask = (metrics_df["DIA_TRANSPORTE"] >= start) & (metrics_df["DIA_TRANSPORTE"] <= end)
    df = metrics_df[mask].copy()


    if agg == "Semanal":
        df = df.set_index("DIA_TRANSPORTE").resample("W").sum(numeric_only=True).reset_index()
    elif agg == "Mensual":
        df = df.set_index("DIA_TRANSPORTE").resample("ME").sum(numeric_only=True).reset_index()
        df["viajes_por_tarjeta"] = (df["total_transacciones"] / df["total_tarjetas_activas"]).round(3)

    # ── Chart 1: Transactions + Cards ────────────────────────────────
    st.markdown(f"#### {t('dem_chart_vs')}")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df["DIA_TRANSPORTE"], y=df["total_transacciones"],
        name=t('dem_legend_tx'), line=dict(color="#38bdf8", width=2.5), # Vibrant light blue
        fill="tozeroy", fillcolor="rgba(56,189,248,.12)"
    ))
    fig1.add_trace(go.Scatter(
        x=df["DIA_TRANSPORTE"], y=df["total_tarjetas_activas"],
        name=t('dem_legend_cards'), line=dict(color="#f97316", width=2.5), # Vibrant orange for high contrast!
        fill="tozeroy", fillcolor="rgba(249,115,22,.08)"
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
        st.markdown(f"#### {t('dem_chart_intensity')}")
        fig2 = px.bar(
            df, x="DIA_TRANSPORTE", y="viajes_por_tarjeta",
            color="viajes_por_tarjeta", color_continuous_scale="Blues",
            template="plotly_dark"
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,.8)",
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False, xaxis_title="", yaxis_title=t('dem_chart_intensity_y')
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown(f"#### {t('dem_chart_type')}")
        tipo_df = (
            tx_df[tx_df["DIA_TRANSPORTE"].between(str(start.date()), str(end.date()))]
            .groupby("TIPO_TRANSPORTE")["CANTIDAD"].sum()
            .reset_index()
            .sort_values("CANTIDAD", ascending=False)
        )
        # Map transportation types to user friendly names based on language
        transport_map = {
            "COLECTIVO": {"es": "Colectivo (Colectivo/Bus)", "en": "Bus (Colectivo)"},
            "TREN": {"es": "Tren", "en": "Train"},
            "SUBTE": {"es": "Subte", "en": "Subway"},
            "LANCHAS": {"es": "Lancha / Transbordador", "en": "Ferry"}
        }
        lang = st.session_state.get("lang", "es")
        tipo_df["TIPO_TRANSPORTE"] = tipo_df["TIPO_TRANSPORTE"].map(lambda x: transport_map.get(x, {}).get(lang, x))
        
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
    st.markdown(f"#### {t('dem_table_title')}")
    stats = df[["total_transacciones", "total_tarjetas_activas", "viajes_por_tarjeta"]].describe().round(2)
    
    # Rename index and columns for user friendly display
    col_translations = {
        "total_transacciones": t('dem_legend_tx'),
        "total_tarjetas_activas": t('dem_legend_cards'),
        "viajes_por_tarjeta": t('kpi_ratio')
    }
    index_translations = {
        "count": {"es": "Cantidad de días", "en": "Days count"},
        "mean": {"es": "Promedio", "en": "Average"},
        "std": {"es": "Desviación estándar", "en": "Standard deviation"},
        "min": {"es": "Mínimo", "en": "Minimum"},
        "25%": "25%",
        "50%": "50% (Mediana)",
        "75%": "75%",
        "max": {"es": "Máximo", "en": "Maximum"}
    }
    
    stats.rename(columns=col_translations, inplace=True)
    stats.index = stats.index.map(lambda x: index_translations.get(x, {}).get(lang, x) if isinstance(index_translations.get(x), dict) else index_translations.get(x, x))
    
    st.dataframe(stats, use_container_width=True)
