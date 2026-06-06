import os
import pandas as pd
from src.utils.logger import setup_logger
from src.utils.config_loader import load_config

logger = setup_logger("build_routes")

def main():
    config = load_config()
    gtfs_dir = config['paths']['raw_gtfs_dir']
    output_path = config['gtfs']['routes_output']
    
    routes_file = os.path.join(gtfs_dir, "routes.txt")
    logger.info(f"Processing routes from: {routes_file}")
    
    # Read only required columns to save memory
    cols = ["route_id", "route_short_name", "route_long_name", "route_type"]
    df = pd.read_csv(routes_file, usecols=cols, dtype={"route_id": str})
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to parquet
    df.to_parquet(output_path, index=False)
    logger.info(f"Successfully saved routes to {output_path} (shape: {df.shape})")

if __name__ == "__main__":
    main()
