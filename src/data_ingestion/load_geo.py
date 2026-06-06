import os
import geopandas as gpd
from src.utils.logger import setup_logger

logger = setup_logger("load_geo")

def load_comunas_shapefile(file_path):
    """
    Loads Buenos Aires communes shapefile, ensures EPSG:4326 CRS,
    and identifies the commune number column.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Shapefile not found at: {file_path}")
        
    logger.info(f"Loading shapefile from {file_path}...")
    # Read using geopandas (uses pyogrio/fiona engine)
    gdf = gpd.read_file(file_path)
    
    # Ensure correct coordinate reference system (Plotly mapbox requires EPSG:4326)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        logger.info(f"Reprojecting shapefile from {gdf.crs} to EPSG:4326...")
        gdf = gdf.to_crs(epsg=4326)
        
    # Let's find the commune identifier column robustly
    comuna_col = None
    cols_lower = [col.lower() for col in gdf.columns]
    
    # Common names for commune ID: 'comunas', 'comuna', 'numero', 'id', 'nro'
    for candidate in ['comunas', 'comuna', 'numero', 'id', 'nro']:
        if candidate in cols_lower:
            idx = cols_lower.index(candidate)
            comuna_col = gdf.columns[idx]
            break
            
    # Fallback to any column that starts with 'com' or 'num'
    if not comuna_col:
        for col in gdf.columns:
            if col.lower().startswith('com') or col.lower().startswith('num'):
                comuna_col = col
                break
                
    # Ultimate fallback: first column that is not 'geometry'
    if not comuna_col:
        non_geo_cols = [c for c in gdf.columns if c != 'geometry']
        if non_geo_cols:
            comuna_col = non_geo_cols[0]
            
    if comuna_col:
        logger.info(f"Identified commune number column: '{comuna_col}'")
        # Standardize the column name to 'comuna'
        gdf = gdf.rename(columns={comuna_col: 'comuna'})
        # Clean the comuna column: extract integer if possible
        try:
            gdf['comuna'] = gdf['comuna'].astype(str).str.extract(r'(\d+)').astype(float).astype(int)
        except Exception as e:
            logger.warning(f"Could not convert comuna column to integer: {e}. Keeping as string.")
    else:
        logger.warning("No commune identifier column found. Creating a dummy index.")
        gdf['comuna'] = gdf.index + 1
        
    # Keep only necessary columns: comuna and geometry
    gdf = gdf[['comuna', 'geometry']].copy()
    logger.info(f"Successfully loaded {len(gdf)} communes.")
    return gdf

def load_barrios_shapefile(file_path):
    """
    Loads Buenos Aires neighborhoods shapefile, ensures EPSG:4326 CRS,
    and identifies the neighborhood name column.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Shapefile not found at: {file_path}")
        
    logger.info(f"Loading shapefile from {file_path}...")
    gdf = gpd.read_file(file_path)
    
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        logger.info(f"Reprojecting shapefile from {gdf.crs} to EPSG:4326...")
        gdf = gdf.to_crs(epsg=4326)
        
    # Find neighborhood name column (e.g. 'nom_barrio', 'barrio', 'nombre', 'name')
    barrio_col = None
    cols_lower = [col.lower() for col in gdf.columns]
    
    for candidate in ['nom_barrio', 'barrio', 'nombre', 'name', 'nomb_barri']:
        if candidate in cols_lower:
            idx = cols_lower.index(candidate)
            barrio_col = gdf.columns[idx]
            break
            
    if not barrio_col:
        for col in gdf.columns:
            if col.lower().startswith('bar') or col.lower().startswith('nom'):
                barrio_col = col
                break
                
    if not barrio_col:
        non_geo_cols = [c for c in gdf.columns if c != 'geometry']
        if non_geo_cols:
            barrio_col = non_geo_cols[0]
            
    if barrio_col:
        logger.info(f"Identified neighborhood name column: '{barrio_col}'")
        gdf = gdf.rename(columns={barrio_col: 'barrio'})
        gdf['barrio'] = gdf['barrio'].astype(str).str.title().str.strip()
    else:
        logger.warning("No neighborhood name column found. Creating dummy index.")
        gdf['barrio'] = gdf.index.map(lambda i: f"Barrio {i+1}")
        
    gdf = gdf[['barrio', 'geometry']].copy()
    logger.info(f"Successfully loaded {len(gdf)} neighborhoods.")
    return gdf
