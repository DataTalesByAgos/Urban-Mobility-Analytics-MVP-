import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from src.utils.logger import setup_logger

logger = setup_logger("spatial_join")

def join_stops_with_comunas(stops_df, comunas_gdf):
    """
    Performs a spatial join to find which commune each GTFS stop belongs to.
    """
    logger.info("Performing spatial join between GTFS stops and communes...")
    
    # Filter stops with valid coordinates
    valid_stops = stops_df.dropna(subset=['stop_lat', 'stop_lon']).copy()
    
    # Create Point geometries
    geometry = gpd.points_from_xy(valid_stops['stop_lon'], valid_stops['stop_lat'])
    stops_gdf = gpd.GeoDataFrame(valid_stops, geometry=geometry, crs="EPSG:4326")
    
    # Spatial join: Point within Polygon
    joined_gdf = gpd.sjoin(stops_gdf, comunas_gdf, how='left', predicate='within')
    
    # Drop geometry to return a regular pandas DataFrame (memory efficient)
    df_out = pd.DataFrame(joined_gdf.drop(columns=['geometry', 'index_right', 'stop_lat', 'stop_lon'], errors='ignore'))
    return df_out

def compute_commune_metrics(stops_df, edges_df, comunas_gdf):
    """
    Aggregates stops count and total scheduled trip frequency per commune.
    Returns a GeoDataFrame with the metrics.
    """
    logger.info("Computing spatial metrics per commune...")
    
    # 1. Spatial join stops -> communes
    stops_with_comunas = join_stops_with_comunas(stops_df, comunas_gdf)
    
    # 2. Calculate trip frequency per stop from edges
    # Load outgoing trip frequency for each stop
    stop_freq = edges_df.groupby('from_stop_id')['trip_frequency'].sum().reset_index()
    stop_freq.rename(columns={'from_stop_id': 'stop_id', 'trip_frequency': 'frecuencia'}, inplace=True)
    
    # Merge frequency into stops with commune info
    stops_metrics = pd.merge(stops_with_comunas, stop_freq, on='stop_id', how='left')
    stops_metrics['frecuencia'] = stops_metrics['frecuencia'].fillna(0)
    
    # 3. Aggregate by commune
    commune_stats = stops_metrics.groupby('comuna').agg(
        total_stops=('stop_id', 'count'),
        total_frequency=('frecuencia', 'sum')
    ).reset_index()
    
    # 4. Merge back to communes GeoDataFrame to preserve geometries
    # Convert commune column in stats to the same type as comunas_gdf
    commune_stats['comuna'] = commune_stats['comuna'].dropna().astype(int)
    
    metrics_gdf = comunas_gdf.merge(commune_stats, on='comuna', how='left')
    metrics_gdf['total_stops'] = metrics_gdf['total_stops'].fillna(0).astype(int)
    metrics_gdf['total_frequency'] = metrics_gdf['total_frequency'].fillna(0).astype(int)
    
    return metrics_gdf

def join_stops_with_barrios(stops_df, barrios_gdf):
    """
    Performs a spatial join to find which neighborhood each GTFS stop belongs to.
    """
    logger.info("Performing spatial join between GTFS stops and neighborhoods...")
    
    valid_stops = stops_df.dropna(subset=['stop_lat', 'stop_lon']).copy()
    geometry = gpd.points_from_xy(valid_stops['stop_lon'], valid_stops['stop_lat'])
    stops_gdf = gpd.GeoDataFrame(valid_stops, geometry=geometry, crs="EPSG:4326")
    
    joined_gdf = gpd.sjoin(stops_gdf, barrios_gdf, how='left', predicate='within')
    
    df_out = pd.DataFrame(joined_gdf.drop(columns=['geometry', 'index_right', 'stop_lat', 'stop_lon'], errors='ignore'))
    return df_out

def compute_neighborhood_metrics(stops_df, edges_df, barrios_gdf):
    """
    Aggregates stops count and total scheduled trip frequency per neighborhood.
    Returns a GeoDataFrame with the metrics.
    """
    logger.info("Computing spatial metrics per neighborhood...")
    
    # 1. Spatial join stops -> neighborhoods
    stops_with_barrios = join_stops_with_barrios(stops_df, barrios_gdf)
    
    # 2. Calculate trip frequency per stop
    stop_freq = edges_df.groupby('from_stop_id')['trip_frequency'].sum().reset_index()
    stop_freq.rename(columns={'from_stop_id': 'stop_id', 'trip_frequency': 'frecuencia'}, inplace=True)
    
    stops_metrics = pd.merge(stops_with_barrios, stop_freq, on='stop_id', how='left')
    stops_metrics['frecuencia'] = stops_metrics['frecuencia'].fillna(0)
    
    # 3. Aggregate by neighborhood
    barrio_stats = stops_metrics.groupby('barrio').agg(
        total_stops=('stop_id', 'count'),
        total_frequency=('frecuencia', 'sum')
    ).reset_index()
    
    # 4. Merge back to neighborhoods GeoDataFrame
    metrics_gdf = barrios_gdf.merge(barrio_stats, on='barrio', how='left')
    metrics_gdf['total_stops'] = metrics_gdf['total_stops'].fillna(0).astype(int)
    metrics_gdf['total_frequency'] = metrics_gdf['total_frequency'].fillna(0).astype(int)
    
    return metrics_gdf
