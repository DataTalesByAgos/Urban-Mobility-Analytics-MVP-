"""GTFS Network analysis page"""
import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.components.translations import t

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
    st.markdown(f"## {t('net_title')}")
    st.markdown(t('net_subtitle'))

    stops_df  = load_stops()
    routes_df = load_routes()
    edges_df  = load_edges()

    # ── KPIs ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(t('net_kpi_stops'), f"{len(stops_df):,}")
    with c2:
        st.metric(t('net_kpi_lines'), f"{len(routes_df):,}")
    with c3:
        st.metric(t('net_kpi_edges'), f"{len(edges_df):,}")
    with c4:
        top_freq = edges_df["trip_frequency"].max()
        st.metric(t('net_kpi_max_freq'), f"{top_freq:,} {t('net_kpi_max_freq_sub')}")

    st.markdown("---")

    # ── Mapa de paradas ───────────────────────────────────────────────
    st.markdown(f"#### {t('net_chart_map_title')}")
    map_stops = stops_df.dropna(subset=["stop_lat", "stop_lon"]).copy()

    # Merge edges frequency per stop
    stop_freq = (
        edges_df.groupby("from_stop_id")["trip_frequency"]
        .sum()
        .reset_index()
        .rename(columns={"from_stop_id": "stop_id", "trip_frequency": "frecuencia"})
    )
    map_stops = map_stops.merge(stop_freq, on="stop_id", how="left")
    map_stops["frecuencia"] = map_stops["frecuencia"].fillna(0)

    # Sample for performance
    sample = map_stops.nlargest(5000, "frecuencia") if len(map_stops) > 5000 else map_stops

    fig_map = px.scatter_mapbox(
        sample,
        lat="stop_lat", lon="stop_lon",
        color="frecuencia",
        size="frecuencia",
        size_max=12,
        hover_name="stop_name",
        hover_data={"stop_id": True, "frecuencia": True, "stop_lat": False, "stop_lon": False},
        color_continuous_scale="Blues",
        mapbox_style="carto-darkmatter",
        zoom=10,
        center={"lat": -34.62, "lon": -58.44},
        height=520,
        template="plotly_dark",
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title=t('net_chart_map_legend')),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ── Top rutas por frecuencia ──────────────────────────────────────
    st.markdown(f"#### {t('net_chart_top_routes')}")
    top_routes = (
        edges_df.groupby("route_id")["trip_frequency"]
        .sum()
        .reset_index()
        .merge(routes_df[["route_id", "route_short_name"]], on="route_id", how="left")
        .sort_values("trip_frequency", ascending=False)
        .head(20)
    )
    fig_bar = px.bar(
        top_routes,
        x="trip_frequency", y="route_short_name",
        orientation="h",
        color="trip_frequency",
        color_continuous_scale="Blues",
        template="plotly_dark",
        labels={"trip_frequency": t('net_col_trip_frequency'), "route_short_name": t('net_col_route_short_name')},
    )
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,.8)",
        height=480, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False, yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Tabla explorable ──────────────────────────────────────────────
    with st.expander(t('net_table_expand')):
        # Map route type numeric codes to user friendly terms
        route_type_map = {
            0: {"es": "Tranvía", "en": "Tram"},
            1: {"es": "Subte", "en": "Subway"},
            2: {"es": "Tren", "en": "Train"},
            3: {"es": "Colectivo (Colectivo/Bus)", "en": "Bus"}
        }
        lang = st.session_state.get("lang", "es")
        
        # Prepare routes dataframe
        explored_df = routes_df.copy()
        
        # Convert route type to friendly string
        explored_df['route_type'] = explored_df['route_type'].map(
            lambda x: route_type_map.get(int(x), {}).get(lang, f"Tipo {x}") if pd.notna(x) else ""
        )
        
        # Merge frequencies
        freq_df = edges_df.groupby("route_id")["trip_frequency"].sum().reset_index()
        table_df = pd.merge(explored_df, freq_df, on="route_id", how="left")
        table_df["trip_frequency"] = table_df["trip_frequency"].fillna(0).astype(int)
        
        # Rename columns to user friendly names
        col_renames = {
            "route_id": t('net_col_route_id'),
            "route_short_name": t('net_col_route_short_name'),
            "route_long_name": t('net_col_route_long_name'),
            "route_type": t('net_col_route_type'),
            "trip_frequency": t('net_col_trip_frequency')
        }
        
        table_df = table_df[list(col_renames.keys())].rename(columns=col_renames)
        table_df = table_df.sort_values(t('net_col_trip_frequency'), ascending=False)
        
        st.dataframe(
            table_df,
            use_container_width=True,
            height=300,
            hide_index=True
        )
