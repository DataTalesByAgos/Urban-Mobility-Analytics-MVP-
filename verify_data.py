import os
import pandas as pd
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger("verify_data")

def check_file(path, label):
    if os.path.exists(path):
        size_mb = os.path.getsize(path) / (1024 * 1024)
        logger.info(f"[OK] {label} found at {path} ({size_mb:.2f} MB)")
        try:
            if path.endswith('.parquet'):
                df = pd.read_parquet(path)
            else:
                df = pd.read_csv(path, nrows=5)
            logger.info(f"  Shape: {df.shape}")
            logger.info(f"  Columns: {list(df.columns)}")
            logger.info("  Sample:")
            print(df.head(2))
            print("-" * 50)
            return True
        except Exception as e:
            logger.error(f"  Error reading {path}: {e}")
            return False
    else:
        logger.error(f"[ERROR] {label} NOT found at {path}")
        return False

def main():
    config = load_config()
    
    logger.info("=== VERIFYING PROCESSED FILES ===")
    
    files_to_check = [
        (config['sube']['clean_transactions_output'], "SUBE Clean Transactions Parquet"),
        (config['sube']['clean_cards_output'], "SUBE Clean Cards Parquet"),
        (config['sube']['mobility_metrics_output'], "SUBE Daily Mobility Metrics Parquet"),
        (config['gtfs']['stops_output'], "GTFS Stops Parquet"),
        (config['gtfs']['routes_output'], "GTFS Routes Parquet"),
        (config['gtfs']['edges_output'], "GTFS Edges Parquet"),
        (config['gtfs']['trips_stop_times_output'], "GTFS Trips Stop Times Parquet")
    ]
    
    success = True
    for path, label in files_to_check:
        if not check_file(path, label):
            success = False
            
    if success:
        logger.info("[SUCCESS] All processed Parquet files verified successfully!")
    else:
        logger.warning("[WARNING] Some processed Parquet files are missing or could not be verified.")

if __name__ == "__main__":
    main()
