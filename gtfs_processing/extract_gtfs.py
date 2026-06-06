import os
import zipfile
from src.utils.logger import setup_logger
from src.utils.config_loader import load_config

logger = setup_logger("gtfs_extract")

def main():
    config = load_config()
    gtfs_dir = config['paths']['raw_gtfs_dir']
    
    logger.info(f"Checking GTFS raw files in: {gtfs_dir}")
    
    # Check if files already exist
    expected_files = ["stops.txt", "routes.txt", "trips.txt", "stop_times.txt"]
    missing_files = []
    
    for f in expected_files:
        path = os.path.join(gtfs_dir, f)
        if not os.path.exists(path):
            missing_files.append(f)
            
    if not missing_files:
        logger.info("All required GTFS files are present in the raw directory.")
        return
        
    # Check if a zip exists to extract
    zip_path = os.path.join(os.path.dirname(gtfs_dir), "gtfs.zip")
    if os.path.exists(zip_path):
        logger.info(f"Found GTFS zip file at {zip_path}. Extracting to {gtfs_dir}...")
        os.makedirs(gtfs_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(gtfs_dir)
        logger.info("Extraction completed successfully.")
    else:
        logger.error(f"Missing GTFS files: {missing_files} and no gtfs.zip found at {zip_path}.")
        raise FileNotFoundError("GTFS files or zip not found.")

if __name__ == "__main__":
    main()
