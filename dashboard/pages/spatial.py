"""Spatial analysis page – Communes shapefile visualization & GTFS integration"""
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json

from src.utils.config_loader import load_config
from src.data_ingestion.load_geo import load_comunas_shapefile
from src.geospatial.spatial_join import compute_commune_metrics

@st.cache_data
def load_config_cached():
    return load_config()

@st.cache_data
def load_comunas_geo(_config):
    """Loads commune shapefiles and caches the GeoDataFrame."""
    shp_path = _config['paths']['comunas_shapefile']
    return load_comunas_shapefile(shp_path)

@st.cache_data
def load_stops_cached():
    """Loads stops from parquet, requesting only necessary columns."""
    return pd.read_parquet("data/processed/stops.parquet", columns=["stop_id", "stop_name", "stop_lat", "stop_lon"])

@st.cache_data
def load_edges_cached():
    """Loads edges from parquet, requesting only necessary columns."""
    return pd.read_parquet("data/processed/edges.parquet", columns=["from_stop_id", "trip_frequency"])

def render():
    st.markdown("## 🗺️ Análisis Espacial por Comunas")
    st.markdown("Visualización e integración de la red de transporte público (GTFS) con la división política por Comunas.")
    
    config = load_config_cached()
    
    # Load datasets safely
    try:
        comunas_gdf = load_comunas_geo(config)
        stops_df = load_stops_cached()
        edges_df = load_edges_cached()
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        st.info("Asegúrese de haber corrido las tareas previas de GTFS y que el archivo de comunas esté en la ruta configurada.")
        return

    # Compute metrics per commune
    with st.spinner("Procesando datos espaciales..."):
        metrics_gdf = compute_commune_metrics(stops_df, edges_df, comunas_gdf)
        
    # Convert GeoDataFrame to GeoJSON format for Plotly
    geojson_data = json.loads(metrics_gdf.to_json())
    
    # ── Sidebar/Filters ──────────────────────────────────────────────────
    st.markdown("### Configuración del Mapa")
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    
    with col_ctrl1:
        metric_choice = st.selectbox(
            "Métrica a visualizar",
            options=["Cantidad de Paradas", "Frecuencia de Viajes"],
            index=0
        )
    with col_ctrl2:
        color_theme = st.selectbox(
            "Escala de colores",
            options=["Blues", "Viridis", "Plasma", "Reds", "YlGnBu"],
            index=0
        )
    with col_ctrl3:
        show_stops = st.checkbox("Mostrar paradas individuales", value=False)

    # Map selected metric
    metric_col = "total_stops" if metric_choice == "Cantidad de Paradas" else "total_frequency"
    metric_label = "Paradas" if metric_choice == "Cantidad de Paradas" else "Viajes programados"

    # ── KPIs ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    
    avg_stops = metrics_gdf["total_stops"].mean()
    max_stops_row = metrics_gdf.loc[metrics_gdf["total_stops"].idxmax()]
    max_freq_row = metrics_gdf.loc[metrics_gdf["total_frequency"].idxmax()]
    
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Total Comunas</div>
            <div class="value">{len(metrics_gdf)}</div>
            <div class="delta">CABA</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Promedio Paradas</div>
            <div class="value">{avg_stops:.1f}</div>
            <div class="delta">por Comuna</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Comuna con más paradas</div>
            <div class="value">Comuna {int(max_stops_row['comuna'])}</div>
            <div class="delta">{max_stops_row['total_stops']:,} paradas</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Comuna más transitada</div>
            <div class="value">Comuna {int(max_freq_row['comuna'])}</div>
            <div class="delta">{max_freq_row['total_frequency']:,} viajes/día</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interactive Map ──────────────────────────────────────────────────
    # Create Choropleth Map for Communes
    fig_choropleth = px.choropleth_mapbox(
        metrics_gdf,
        geojson=geojson_data,
        locations="comuna",
        featureidkey="properties.comuna",
        color=metric_col,
        color_continuous_scale=color_theme,
        mapbox_style="carto-darkmatter",
        center={"lat": -34.62, "lon": -58.44},
        zoom=10.5,
        opacity=0.65,
        labels={metric_col: metric_label, "comuna": "Comuna"},
        hover_data={"comuna": True, "total_stops": True, "total_frequency": True}
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
    st.markdown("#### Desglose Estadístico por Comuna")
    
    display_df = pd.DataFrame(metrics_gdf.drop(columns="geometry")).sort_values(by=metric_col, ascending=False)
    display_df = display_df.rename(columns={
        "comuna": "Comuna",
        "total_stops": "Cantidad de Paradas",
        "total_frequency": "Frecuencia Total de Viajes"
    })
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
