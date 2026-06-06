import os
import pandas as pd
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger
from src.data_ingestion.load_sube import load_raw_transactions, load_raw_cards

logger = setup_logger("sube_cleaning")

def clean_transactions(df):
    """Cleans raw transactions DataFrame."""
    logger.info("Cleaning transactions...")
    # Convert date
    df['DIA_TRANSPORTE'] = pd.to_datetime(df['DIA_TRANSPORTE'])
    
    # Handle missing values
    df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce').fillna(0).astype(int)
    
    # Drop completely duplicate rows
    initial_len = len(df)
    df = df.drop_duplicates()
    logger.info(f"Dropped {initial_len - len(df)} duplicate transaction rows.")
    return df

def clean_cards(df):
    """Cleans raw active cards DataFrame."""
    logger.info("Cleaning active cards...")
    # Convert date
    df['DIA_TRANSPORTE'] = pd.to_datetime(df['DIA_TRANSPORTE'])
    
    # Handle missing values
    df['CANT_TRJ'] = pd.to_numeric(df['CANT_TRJ'], errors='coerce').fillna(0).astype(int)
    
    # Drop duplicates
    initial_len = len(df)
    df = df.drop_duplicates()
    logger.info(f"Dropped {initial_len - len(df)} duplicate card rows.")
    return df

def main():
    config = load_config()
    
    # Check output directory
    processed_dir = config['paths']['processed_dir']
    os.makedirs(processed_dir, exist_ok=True)
    
    # Clean transactions
    raw_tx_path = config['paths']['raw_sube_transactions']
    tx_df = load_raw_transactions(raw_tx_path)
    clean_tx_df = clean_transactions(tx_df)
    
    tx_out = config['sube']['clean_transactions_output']
    clean_tx_df.to_parquet(tx_out, index=False)
    logger.info(f"Saved clean transactions to: {tx_out}")
    
    # Clean cards
    raw_trj_path = config['paths']['raw_sube_cards']
    trj_df = load_raw_cards(raw_trj_path)
    clean_trj_df = clean_cards(trj_df)
    
    trj_out = config['sube']['clean_cards_output']
    clean_trj_df.to_parquet(trj_out, index=False)
    logger.info(f"Saved clean active cards to: {trj_out}")

if __name__ == "__main__":
    main()
