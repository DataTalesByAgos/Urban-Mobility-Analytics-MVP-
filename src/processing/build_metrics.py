import pandas as pd
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger("sube_metrics")

def main():
    config = load_config()
    
    tx_path = config['sube']['clean_transactions_output']
    cards_path = config['sube']['clean_cards_output']
    metrics_path = config['sube']['mobility_metrics_output']
    
    logger.info("Loading cleaned datasets to build metrics...")
    tx_df = pd.read_parquet(tx_path)
    cards_df = pd.read_parquet(cards_path)
    
    # Aggregate transactions by date
    # Note: we also aggregate by AMBA to preserve the region classification if needed,
    # or just aggregate globally/by date. Let's aggregate globally by date first,
    # and maybe also retain AMBA column if it's there.
    # We will compute both: general overall daily metrics, and also by AMBA.
    # Let's aggregate by DIA_TRANSPORTE
    logger.info("Aggregating transactions by date...")
    daily_tx = tx_df.groupby('DIA_TRANSPORTE')['CANTIDAD'].sum().reset_index()
    daily_tx.rename(columns={'CANTIDAD': 'total_transacciones'}, inplace=True)
    
    logger.info("Aggregating active cards by date...")
    # In cards dataset, we filter to 'TOTAL' TIPO_TRANSPORTE to avoid double counting across types, 
    # or sum them. Wait, let's look at the structure of cards dataset:
    # 2025-01-01, "NO", , , "COLECTIVO", 29251, "NO"
    # 2025-01-01, "NO", , , "TOTAL", 29311, "NO"
    # So if there is "TOTAL" in TIPO_TRANSPORTE, we should filter by it or group appropriately.
    # Let's filter to TIPO_TRANSPORTE == 'TOTAL' to get unique cards.
    # Wait, let's verify if there is always a 'TOTAL' for AMBA 'SI' and AMBA 'NO'.
    # Yes, we have 'TOTAL' for TIPO_TRANSPORTE.
    total_cards_df = cards_df[cards_df['TIPO_TRANSPORTE'] == 'TOTAL']
    if len(total_cards_df) == 0:
        # Fallback if no TOTAL is found
        logger.warning("No 'TOTAL' TIPO_TRANSPORTE rows found. Aggregating all cards.")
        daily_cards = cards_df.groupby('DIA_TRANSPORTE')['CANT_TRJ'].sum().reset_index()
    else:
        daily_cards = total_cards_df.groupby('DIA_TRANSPORTE')['CANT_TRJ'].sum().reset_index()
        
    daily_cards.rename(columns={'CANT_TRJ': 'total_tarjetas_activas'}, inplace=True)
    
    # Merge
    logger.info("Merging datasets...")
    metrics_df = pd.merge(daily_tx, daily_cards, on='DIA_TRANSPORTE', how='outer')
    metrics_df.sort_values('DIA_TRANSPORTE', inplace=True)
    
    # Calculate derived metrics
    metrics_df['viajes_por_tarjeta'] = (metrics_df['total_transacciones'] / metrics_df['total_tarjetas_activas']).round(3)
    
    # Fill any NaNs with 0
    metrics_df.fillna(0, inplace=True)
    
    logger.info(f"Generated daily metrics. Row count: {len(metrics_df)}")
    metrics_df.to_parquet(metrics_path, index=False)
    logger.info(f"Saved daily mobility metrics to: {metrics_path}")

if __name__ == "__main__":
    main()
