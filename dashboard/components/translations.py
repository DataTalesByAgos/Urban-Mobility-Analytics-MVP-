import streamlit as st

# Commune neighborhoods mapping for friendly display
COMMUNE_NEIGHBORHOODS = {
    1: {
        "es": "Comuna 1 (Retiro, San Nicolás, Puerto Madero, San Telmo, Montserrat, Constitución)",
        "en": "Commune 1 (Retiro, San Nicolás, Puerto Madero, San Telmo, Montserrat, Constitución)"
    },
    2: {
        "es": "Comuna 2 (Recoleta)",
        "en": "Commune 2 (Recoleta)"
    },
    3: {
        "es": "Comuna 3 (Balvanera, San Cristóbal)",
        "en": "Commune 3 (Balvanera, San Cristóbal)"
    },
    4: {
        "es": "Comuna 4 (La Boca, Barracas, Parque Patricios, Nueva Pompeya)",
        "en": "Commune 4 (La Boca, Barracas, Parque Patricios, Nueva Pompeya)"
    },
    5: {
        "es": "Comuna 5 (Almagro, Boedo)",
        "en": "Commune 5 (Almagro, Boedo)"
    },
    6: {
        "es": "Comuna 6 (Caballito)",
        "en": "Commune 6 (Caballito)"
    },
    7: {
        "es": "Comuna 7 (Flores, Parque Chacabuco)",
        "en": "Commune 7 (Flores, Parque Chacabuco)"
    },
    8: {
        "es": "Comuna 8 (Villa Soldati, Villa Riachuelo, Villa Lugano)",
        "en": "Commune 8 (Villa Soldati, Villa Riachuelo, Villa Lugano)"
    },
    9: {
        "es": "Comuna 9 (Liniers, Mataderos, Parque Avellaneda)",
        "en": "Commune 9 (Liniers, Mataderos, Parque Avellaneda)"
    },
    10: {
        "es": "Comuna 10 (Villa Real, Monte Castro, Versalles, Floresta, Vélez Sarsfield, Villa Luro)",
        "en": "Commune 10 (Villa Real, Monte Castro, Versalles, Floresta, Vélez Sarsfield, Villa Luro)"
    },
    11: {
        "es": "Comuna 11 (Villa General Mitre, Villa Devoto, Villa del Parque, Villa Santa Rita)",
        "en": "Commune 11 (Villa General Mitre, Villa Devoto, Villa del Parque, Villa Santa Rita)"
    },
    12: {
        "es": "Comuna 12 (Coghlan, Saavedra, Villa Urquiza, Villa Pueyrredón)",
        "en": "Commune 12 (Coghlan, Saavedra, Villa Urquiza, Villa Pueyrredón)"
    },
    13: {
        "es": "Comuna 13 (Núñez, Belgrano, Colegiales)",
        "en": "Commune 13 (Núñez, Belgrano, Colegiales)"
    },
    14: {
        "es": "Comuna 14 (Palermo)",
        "en": "Commune 14 (Palermo)"
    },
    15: {
        "es": "Comuna 15 (Chacarita, Villa Crespo, La Paternal, Villa Ortúzar, Agronomía, Parque Chas)",
        "en": "Commune 15 (Chacarita, Villa Crespo, La Paternal, Villa Ortúzar, Agronomía, Parque Chas)"
    }
}

# General translations dictionary
TEXTS = {
    # ── Sidebar ──────────────────────────────────────────────────────
    "lang_label": {
        "es": "🌐 Seleccionar Idioma",
        "en": "🌐 Select Language"
    },
    "nav_title": {
        "es": "Navegación",
        "en": "Navigation"
    },
    "nav_overview": {
        "es": "🏠 Resumen General",
        "en": "🏠 Overview"
    },
    "nav_demand": {
        "es": "📈 Demanda SUBE",
        "en": "📈 SUBE Demand"
    },
    "nav_network": {
        "es": "🚌 Red GTFS",
        "en": "🚌 GTFS Network"
    },
    "nav_spatial": {
        "es": "🗺️ Análisis Espacial",
        "en": "🗺️ Spatial Analysis"
    },
    "footer_data": {
        "es": "Datos: 2025 · SUBE + GTFS CABA",
        "en": "Data: 2025 · SUBE + GTFS CABA"
    },

    # ── Overview Page ────────────────────────────────────────────────
    "ov_title": {
        "es": "🚌 Analítica de Movilidad Urbana",
        "en": "🚌 Urban Mobility Analytics"
    },
    "ov_subtitle": {
        "es": "Análisis de demanda de movilidad urbana · Argentina 2025 · SUBE + GTFS Buenos Aires",
        "en": "Urban mobility demand analysis · Argentina 2025 · SUBE + GTFS Buenos Aires"
    },
    "kpi_transactions": {
        "es": "Transacciones 2025",
        "en": "Transactions 2025"
    },
    "kpi_transactions_sub": {
        "es": "total del año",
        "en": "total yearly"
    },
    "kpi_avg_daily": {
        "es": "Promedio Diario",
        "en": "Daily Average"
    },
    "kpi_avg_daily_sub": {
        "es": "viajes/día",
        "en": "trips/day"
    },
    "kpi_peak_daily": {
        "es": "Pico Máximo",
        "en": "Peak Day"
    },
    "kpi_peak_daily_sub": {
        "es": "viajes en un día",
        "en": "trips in a single day"
    },
    "kpi_ratio": {
        "es": "Viajes / Tarjeta",
        "en": "Trips / Card"
    },
    "kpi_ratio_sub": {
        "es": "promedio diario",
        "en": "daily average"
    },
    "chart_ov_title": {
        "es": "Evolución diaria de transacciones SUBE",
        "en": "Daily evolution of SUBE transactions"
    },
    "chart_ov_y": {
        "es": "Transacciones",
        "en": "Transactions"
    },
    "ov_network_info": {
        "es": "Red de transporte",
        "en": "Transit Network"
    },
    "ov_indicator": {
        "es": "Indicador",
        "en": "Indicator"
    },
    "ov_value": {
        "es": "Valor",
        "en": "Value"
    },
    "ov_stops": {
        "es": "Paradas",
        "en": "Stops"
    },
    "ov_lines": {
        "es": "Líneas",
        "en": "Lines"
    },
    "ov_edges": {
        "es": "Aristas del grafo",
        "en": "Network Edges"
    },
    "ov_link_msg": {
        "es": "Explorá la red en la página Red GTFS",
        "en": "Explore the network in the GTFS Network page"
    },
    "ov_sources": {
        "es": "Fuentes: datos.transporte.gob.ar · data.buenosaires.gob.ar · GTFS Colectivos CABA",
        "en": "Sources: datos.transporte.gob.ar · data.buenosaires.gob.ar · GTFS Colectivos CABA"
    },

    # ── Demand Page ──────────────────────────────────────────────────
    "dem_title": {
        "es": "📈 Análisis de Demanda SUBE",
        "en": "📈 SUBE Demand Analysis"
    },
    "dem_subtitle": {
        "es": "Serie temporal de movilidad, usuarios activos e indicadores derivados para 2025.",
        "en": "Mobility time series, active users, and derived indicators for 2025."
    },
    "filter_date_range": {
        "es": "Rango de fechas",
        "en": "Date range"
    },
    "filter_agg": {
        "es": "Agregación",
        "en": "Aggregation"
    },
    "agg_daily": {
        "es": "Diaria",
        "en": "Daily"
    },
    "agg_weekly": {
        "es": "Semanal",
        "en": "Weekly"
    },
    "agg_monthly": {
        "es": "Mensual",
        "en": "Monthly"
    },
    "dem_chart_vs": {
        "es": "Transacciones vs Tarjetas activas",
        "en": "Transactions vs Active cards"
    },
    "dem_legend_tx": {
        "es": "Transacciones",
        "en": "Transactions"
    },
    "dem_legend_cards": {
        "es": "Tarjetas activas",
        "en": "Active cards"
    },
    "dem_chart_intensity": {
        "es": "Intensidad de uso (viajes / tarjeta)",
        "en": "Usage Intensity (trips / card)"
    },
    "dem_chart_intensity_y": {
        "es": "Relación (Viajes/Tarjeta)",
        "en": "Ratio (Trips/Card)"
    },
    "dem_chart_type": {
        "es": "Distribución por tipo de transporte",
        "en": "Distribution by transit type"
    },
    "dem_table_title": {
        "es": "Estadísticas del período",
        "en": "Statistics for the selected period"
    },

    # ── Network Page ─────────────────────────────────────────────────
    "net_title": {
        "es": "🚌 Red de Transporte Público (GTFS)",
        "en": "🚌 Public Transit Network (GTFS)"
    },
    "net_subtitle": {
        "es": "Estructura de la red de colectivos de Buenos Aires basada en datos GTFS.",
        "en": "Structure of the Buenos Aires bus network based on GTFS data."
    },
    "net_kpi_stops": {
        "es": "Paradas totales",
        "en": "Total Stops"
    },
    "net_kpi_lines": {
        "es": "Líneas activas",
        "en": "Active Lines"
    },
    "net_kpi_edges": {
        "es": "Aristas de red",
        "en": "Network Edges"
    },
    "net_kpi_max_freq": {
        "es": "Frecuencia máx.",
        "en": "Max Frequency"
    },
    "net_kpi_max_freq_sub": {
        "es": "viajes",
        "en": "trips"
    },
    "net_chart_map_title": {
        "es": "Distribución geográfica de paradas",
        "en": "Geographical distribution of stops"
    },
    "net_chart_map_legend": {
        "es": "Frecuencia",
        "en": "Frequency"
    },
    "net_chart_top_routes": {
        "es": "Top 20 líneas por frecuencia de viajes",
        "en": "Top 20 lines by trip frequency"
    },
    "net_table_expand": {
        "es": "Explorar tabla de líneas de transporte",
        "en": "Explore transit lines table"
    },
    "net_col_route_id": {
        "es": "ID de Línea",
        "en": "Line ID"
    },
    "net_col_route_short_name": {
        "es": "Línea / Colectivo",
        "en": "Line Number"
    },
    "net_col_route_long_name": {
        "es": "Nombre de Ruta",
        "en": "Route Name"
    },
    "net_col_route_type": {
        "es": "Tipo de Transporte",
        "en": "Transit Type"
    },
    "net_col_trip_frequency": {
        "es": "Frecuencia diaria (viajes)",
        "en": "Daily Frequency (trips)"
    },

    # ── Spatial Page ─────────────────────────────────────────────────
    "sp_title": {
        "es": "🗺️ Análisis Espacial por Comunas",
        "en": "🗺️ Spatial Analysis by Communes"
    },
    "sp_subtitle": {
        "es": "Visualización e integración de la red de transporte público (GTFS) con la división política por Comunas.",
        "en": "Visualization and integration of the public transit network (GTFS) with politically divided Communes."
    },
    "sp_map_cfg": {
        "es": "Configuración del Mapa",
        "en": "Map Configuration"
    },
    "sp_metric_select": {
        "es": "Métrica a visualizar",
        "en": "Metric to visualize"
    },
    "sp_metric_stops": {
        "es": "Cantidad de Paradas",
        "en": "Stops Count"
    },
    "sp_metric_freq": {
        "es": "Frecuencia de Viajes",
        "en": "Trip Frequency"
    },
    "sp_color_theme": {
        "es": "Escala de colores",
        "en": "Color theme"
    },
    "sp_show_stops": {
        "es": "Mostrar paradas individuales",
        "en": "Show individual stops"
    },
    "sp_kpi_total_c": {
        "es": "Total Comunas",
        "en": "Total Communes"
    },
    "sp_kpi_avg_s": {
        "es": "Promedio Paradas",
        "en": "Avg Stops"
    },
    "sp_kpi_avg_s_sub": {
        "es": "por Comuna",
        "en": "per Commune"
    },
    "sp_kpi_max_s": {
        "es": "Comuna con más paradas",
        "en": "Commune with most stops"
    },
    "sp_kpi_max_s_sub": {
        "es": "paradas",
        "en": "stops"
    },
    "sp_kpi_max_f": {
        "es": "Comuna más transitada",
        "en": "Busiest Commune"
    },
    "sp_kpi_max_f_sub": {
        "es": "viajes/día",
        "en": "trips/day"
    },
    "sp_table_title": {
        "es": "Desglose Estadístico por Comuna",
        "en": "Commune Statistical Breakdown"
    },
    "sp_col_comuna": {
        "es": "Comuna / Barrios representativos",
        "en": "Commune / Neighborhoods"
    },
    "sp_col_stops": {
        "es": "Cantidad de Paradas",
        "en": "Stops Count"
    },
    "sp_col_freq": {
        "es": "Frecuencia Total de Viajes",
        "en": "Total Trip Frequency"
    },
    # ── Level and Time Filter Extensions ──────────────────────────────
    "sp_level_select": {
        "es": "Nivel de división geográfica",
        "en": "Geographical division level"
    },
    "sp_level_comunas": {
        "es": "Comunas",
        "en": "Communes"
    },
    "sp_level_barrios": {
        "es": "Barrios",
        "en": "Neighborhoods"
    },
    "sp_col_barrio": {
        "es": "Barrio",
        "en": "Neighborhood"
    },
    "sp_kpi_total_b": {
        "es": "Total Barrios",
        "en": "Total Neighborhoods"
    },
    "sp_kpi_avg_b_sub": {
        "es": "por Barrio",
        "en": "per Neighborhood"
    },
    "sp_kpi_max_s_b": {
        "es": "Barrio con más paradas",
        "en": "Neighborhood with most stops"
    },
    "sp_kpi_max_f_b": {
        "es": "Barrio más transitado",
        "en": "Busiest Neighborhood"
    },
    "filter_time_mode": {
        "es": "Método de filtrado temporal",
        "en": "Time filtering method"
    },
    "time_custom": {
        "es": "Rango libre (Fechas)",
        "en": "Custom Date Range"
    },
    "time_month": {
        "es": "Por Mes",
        "en": "By Month"
    },
    "time_quarter": {
        "es": "Por Trimestre",
        "en": "By Quarter"
    }
}

def t(key):
    """Translation helper function."""
    lang = st.session_state.get("lang", "es")
    # Default to Spanish if key or lang is missing
    return TEXTS.get(key, {}).get(lang, key)

def get_commune_friendly_name(comuna_num):
    """Returns a friendly description of the commune containing its neighborhood names."""
    lang = st.session_state.get("lang", "es")
    comuna_int = int(comuna_num)
    if comuna_int in COMMUNE_NEIGHBORHOODS:
        return COMMUNE_NEIGHBORHOODS[comuna_int][lang]
    return f"Comuna {comuna_int}" if lang == "es" else f"Commune {comuna_int}"
