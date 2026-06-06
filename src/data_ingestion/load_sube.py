import os
import pandas as pd
from src.utils.logger import setup_logger

logger = setup_logger("sube_ingestion")

def load_raw_transactions(file_path):
    """Loads raw transactions dataset and prints info."""
    logger.info(f"Loading raw transactions from: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Transactions CSV not found at {file_path}")
    df = pd.read_csv(file_path)
    logger.info(f"Loaded transactions shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    return df

def load_raw_cards(file_path):
    """Loads raw active cards dataset and prints info."""
    logger.info(f"Loading raw active cards from: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Active cards CSV not found at {file_path}")
    df = pd.read_csv(file_path)
    logger.info(f"Loaded active cards shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    return df
