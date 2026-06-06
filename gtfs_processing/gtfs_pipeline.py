import sys
from gtfs_processing.extract_gtfs import main as run_extract
from gtfs_processing.build_stops import main as run_stops
from gtfs_processing.build_routes import main as run_routes
from gtfs_processing.build_edges import main as run_edges
from src.utils.logger import setup_logger

logger = setup_logger("gtfs_pipeline")

def main():
    logger.info("========================================")
    logger.info("Starting GTFS Data Processing Pipeline")
    logger.info("========================================")
    
    try:
        logger.info("Step 1: Checking and extracting GTFS zip/files...")
        run_extract()
        
        logger.info("Step 2: Processing stops to Parquet...")
        run_stops()
        
        logger.info("Step 3: Processing routes to Parquet...")
        run_routes()
        
        logger.info("Step 4: Building edges and trip sequences to Parquet...")
        run_edges()
        
        logger.info("========================================")
        logger.info("GTFS Pipeline Executed Successfully!")
        logger.info("========================================")
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
