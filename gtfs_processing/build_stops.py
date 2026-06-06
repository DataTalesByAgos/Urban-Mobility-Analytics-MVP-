import os
import pandas as pd
from src.utils.logger import setup_logger
from src.utils.config_loader import load_config

logger = setup_logger("build_stops")

def main():
    config = load_config()
    gtfs_dir = config['paths']['raw_gtfs_dir']
    output_path = config['gtfs']['stops_output']
    
    stops_file = os.path.join(gtfs_dir, "stops.txt")
    logger.info(f"Processing stops from: {stops_file}")
    
    # Read only required columns to save memory
    cols = ["stop_id", "stop_name", "stop_lat", "stop_lon"]
    df = pd.read_csv(stops_file, usecols=cols, dtype={"stop_id": str})
    
    # Convert lat/lon to float
    df["stop_lat"] = pd.to_numeric(df["stop_lat"], errors="coerce")
    df["stop_lon"] = pd.to_numeric(df["stop_lon"], errors="coerce")
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to parquet
    df.to_parquet(output_path, index=False)
    logger.info(f"Successfully saved stops to {output_path} (shape: {df.shape})")

if __name__ == "__main__":
    main()
