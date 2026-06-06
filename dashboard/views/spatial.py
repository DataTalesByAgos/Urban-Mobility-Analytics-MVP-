"""Spatial analysis page – Communes & Neighborhoods shapefile visualization & GTFS integration"""
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json

from src.utils.config_loader import load_config
from src.data_ingestion.load_geo import load_comunas_shapefile, load_barrios_shapefile
from src.geospatial.spatial_join import compute_commune_metrics, compute_neighborhood_metrics
from dashboard.components.translations import t, get_commune_friendly_name

@st.cache_data
def load_config_cached():
    return load_config()

@st.cache_data
def load_comunas_geo(_config):
    """Loads commune shapefiles and caches the GeoDataFrame."""
    shp_path = _config['paths']['comunas_shapefile']
    return load_comunas_shapefile(shp_path)

@st.cache_data
def load_barrios_geo(_config):
    """Loads neighborhood shapefiles and caches the GeoDataFrame."""
    shp_path = _config['paths']['barrios_shapefile']
    return load_barrios_shapefile(shp_path)

@st.cache_data
def load_stops_cached():
    """Loads stops from parquet, requesting only necessary columns."""
    return pd.read_parquet("data/processed/stops.parquet", columns=["stop_id", "stop_name", "stop_lat", "stop_lon"])

@st.cache_data
def load_edges_cached():
    """Loads edges from parquet, requesting only necessary columns."""
    return pd.read_parquet("data/processed/edges.parquet", columns=["from_stop_id", "trip_frequency"])

def render():
    st.markdown(f"## {t('sp_title')}")
    st.markdown(t('sp_subtitle'))
    
    config = load_config_cached()
    
    # Load stops and edges datasets safely
    try:
        stops_df = load_stops_cached()
        edges_df = load_edges_cached()
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        st.info("Asegúrese de haber corrido las tareas previas de GTFS.")
        return

    # ── Level Selector: Comunas vs Barrios ────────────────────────────────
    level_choices = {
        t("sp_level_comunas"): "comunas",
        t("sp_level_barrios"): "barrios"
    }
    
    col_level1, col_level2 = st.columns([2, 1])
    with col_level1:
        level_choice = st.radio(
            t("sp_level_select"),
            options=list(level_choices.keys()),
            horizontal=True,
            index=0
        )
        level = level_choices[level_choice]

    # Load appropriate shapefile and compute metrics dynamically
    try:
        if level == "comunas":
            geo_gdf = load_comunas_geo(config)
            with st.spinner("Procesando datos espaciales (Comunas)..."):
                metrics_gdf = compute_commune_metrics(stops_df, edges_df, geo_gdf)
            geo_id_col = "comuna"
            feature_id_key = "properties.comuna"
            
            friendly_col_name = t('sp_col_comuna')
            kpi_total_label = t('sp_kpi_total_c')
            kpi_avg_sub = t('sp_kpi_avg_s_sub')
            kpi_max_s_label = t('sp_kpi_max_s')
            kpi_max_f_label = t('sp_kpi_max_f')
            
            # Helper for readable KPI values
            lang = st.session_state.get("lang", "es")
            comuna_word = "Comuna" if lang == "es" else "Commune"
            get_kpi_val = lambda row: f"{comuna_word} {int(row['comuna'])}"
        else:
            geo_gdf = load_barrios_geo(config)
            with st.spinner("Procesando datos espaciales (Barrios)..."):
                metrics_gdf = compute_neighborhood_metrics(stops_df, edges_df, geo_gdf)
            geo_id_col = "barrio"
            feature_id_key = "properties.barrio"
            
            friendly_col_name = t('sp_col_barrio')
            kpi_total_label = t('sp_kpi_total_b')
            kpi_avg_sub = t('sp_kpi_avg_b_sub')
            kpi_max_s_label = t('sp_kpi_max_s_b')
            kpi_max_f_label = t('sp_kpi_max_f_b')
            get_kpi_val = lambda row: str(row['barrio'])
            
    except Exception as e:
        st.error(f"Error al cargar el archivo geográfico del nivel '{level}': {e}")
        st.info("Verifique que los archivos de comunas/barrios existan en la carpeta correspondiente.")
        return
        
    # Convert GeoDataFrame to GeoJSON format for Plotly
    geojson_data = json.loads(metrics_gdf.to_json())
    
    # ── Sidebar/Filters ──────────────────────────────────────────────────
    st.markdown(f"### {t('sp_map_cfg')}")
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    
    with col_ctrl1:
        metric_choices = {
            t("sp_metric_stops"): "total_stops",
            t("sp_metric_freq"): "total_frequency"
        }
        metric_choice = st.selectbox(
            t("sp_metric_select"),
            options=list(metric_choices.keys()),
            index=0
        )
        metric_col = metric_choices[metric_choice]
        
    with col_ctrl2:
        color_theme = st.selectbox(
            t("sp_color_theme"),
            options=["Blues", "Viridis", "Plasma", "Reds", "YlGnBu"],
            index=0
        )
    with col_ctrl3:
        show_stops = st.checkbox(t("sp_show_stops"), value=False)

    metric_label = t("ov_stops") if metric_col == "total_stops" else t("net_col_trip_frequency")

    # ── KPIs ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    
    avg_stops = metrics_gdf["total_stops"].mean()
    max_stops_row = metrics_gdf.loc[metrics_gdf["total_stops"].idxmax()]
    max_freq_row = metrics_gdf.loc[metrics_gdf["total_frequency"].idxmax()]
    
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">{kpi_total_label}</div>
            <div class="value">{len(metrics_gdf)}</div>
            <div class="delta">CABA</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">{t('sp_kpi_avg_s')}</div>
            <div class="value">{avg_stops:.1f}</div>
            <div class="delta">{kpi_avg_sub}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="label">{kpi_max_s_label}</div>
            <div class="value">{get_kpi_val(max_stops_row)}</div>
            <div class="delta">{max_stops_row['total_stops']:,} {t('sp_kpi_max_s_sub')}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="label">{kpi_max_f_label}</div>
            <div class="value">{get_kpi_val(max_freq_row)}</div>
            <div class="delta">{max_freq_row['total_frequency']:,} {t('sp_kpi_max_f_sub')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interactive Map ──────────────────────────────────────────────────
    # Create Choropleth Map for selected level
    fig_choropleth = px.choropleth_mapbox(
        metrics_gdf,
        geojson=geojson_data,
        locations=geo_id_col,
        featureidkey=feature_id_key,
        color=metric_col,
        color_continuous_scale=color_theme,
        mapbox_style="carto-darkmatter",
        center={"lat": -34.62, "lon": -58.44},
        zoom=10.5,
        opacity=0.65,
        labels={metric_col: metric_label, geo_id_col: friendly_col_name},
        hover_data={geo_id_col: True, "total_stops": True, "total_frequency": True}
    )
    
    fig = go.Figure(fig_choropleth.data)
    
    # Optional overlay of stops
    if show_stops:
        # Sample for performance if too large
        sample_stops = stops_df.sample(n=min(3000, len(stops_df)), random_state=42)
        fig_scatter = px.scatter_mapbox(
            sample_stops,
            lat="stop_lat",
            lon="stop_lon",
            hover_name="stop_name",
            color_discrete_sequence=["#38bdf8"],
            zoom=10.5
        )
        # Add stops scatter layer
        fig.add_trace(fig_scatter.data[0])

    # Configure layout
    fig.update_layout(
        fig_choropleth.layout,
        margin={"r":0,"t":0,"l":0,"b":0},
        height=550,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # ── Details Table ────────────────────────────────────────────────────
    st.markdown(f"#### {t('sp_table_title')}")
    
    display_df = pd.DataFrame(metrics_gdf.drop(columns="geometry")).sort_values(by=metric_col, ascending=False)
    
    # If level is comunas, map number to name + neighborhoods!
    if level == "comunas":
        display_df["comuna"] = display_df["comuna"].map(get_commune_friendly_name)
    
    display_df = display_df.rename(columns={
        geo_id_col: friendly_col_name,
        "total_stops": t('sp_col_stops'),
        "total_frequency": t('sp_col_freq')
    })
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
