import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from src.utils.logger import setup_logger
from src.utils.config_loader import load_config

logger = setup_logger("build_edges")

def build_edges_and_trips(config):
    gtfs_dir = config['paths']['raw_gtfs_dir']
    edges_out = config['gtfs']['edges_output']
    trips_stop_times_out = config['gtfs']['trips_stop_times_output']
    chunk_size = config['gtfs']['chunk_size']
    
    trips_file = os.path.join(gtfs_dir, "trips.txt")
    stop_times_file = os.path.join(gtfs_dir, "stop_times.txt")
    
    logger.info("Loading trip to route mappings...")
    trips_df = pd.read_csv(trips_file, usecols=["trip_id", "route_id"], dtype={"trip_id": str, "route_id": str})
    trip_to_route = dict(zip(trips_df["trip_id"], trips_df["route_id"]))
    logger.info(f"Loaded mapping for {len(trip_to_route)} trips.")
    
    logger.info("Processing stop_times.txt in chunks...")
    
    # We will accumulate unique edges in memory.
    # An edge is key: (from_stop, to_stop, route_id) -> value: weight (count of trips)
    edge_counts = {}
    
    # For writing the full stop_times table directly to Parquet chunk-by-chunk (highly optimized)
    writer = None
    
    # State to handle trip continuity across chunk boundaries
    last_row = None
    
    chunk_idx = 0
    total_rows = 0
    
    for chunk in pd.read_csv(
        stop_times_file,
        usecols=["trip_id", "stop_id", "stop_sequence", "arrival_time"],
        dtype={"trip_id": str, "stop_id": str, "stop_sequence": int, "arrival_time": str},
        chunksize=chunk_size
    ):
        chunk_idx += 1
        total_rows += len(chunk)
        logger.info(f"Processing chunk {chunk_idx}... ({total_rows} rows processed so far)")
        
        # 1. Write this chunk of stop times directly to the Parquet file
        # Add route_id to the stop times records for easier queries in the dashboard
        chunk["route_id"] = chunk["trip_id"].map(trip_to_route).fillna("")
        
        table = pa.Table.from_pandas(chunk, preserve_index=False)
        if writer is None:
            os.makedirs(os.path.dirname(trips_stop_times_out), exist_ok=True)
            writer = pq.ParquetWriter(trips_stop_times_out, table.schema, compression='snappy')
        writer.write_table(table)
        
        # 2. Extract edges from this chunk
        # If we have a last row from the previous chunk, prepend it to make sure we don't lose the boundary edge
        if last_row is not None:
            extended_chunk = pd.concat([pd.DataFrame([last_row]), chunk], ignore_index=True)
        else:
            extended_chunk = chunk
            
        # Store last row of current chunk for the next iteration
        last_row = chunk.iloc[-1].to_dict()
        
        # Sort to be absolutely sure sequence is consecutive per trip
        extended_chunk.sort_values(["trip_id", "stop_sequence"], inplace=True)
        
        # Calculate shifted columns to find transitions
        extended_chunk["prev_trip_id"] = extended_chunk["trip_id"].shift(1)
        extended_chunk["prev_stop_id"] = extended_chunk["stop_id"].shift(1)
        
        # Valid edge is when trip_id matches previous trip_id
        valid_edges_mask = (extended_chunk["trip_id"] == extended_chunk["prev_trip_id"])
        edges_df = extended_chunk[valid_edges_mask]
        
        # Aggregate edge occurrences in pandas first (extremely fast compared to row-by-row loop)
        if not edges_df.empty:
            grouped = edges_df.groupby(["prev_stop_id", "stop_id", "route_id"]).size().reset_index(name="count")
            for _, r in grouped.iterrows():
                from_stop = r["prev_stop_id"]
                to_stop = r["stop_id"]
                r_id = r["route_id"]
                if not r_id:
                    continue
                edge_key = (from_stop, to_stop, r_id)
                edge_counts[edge_key] = edge_counts.get(edge_key, 0) + r["count"]

    if writer:
        writer.close()
    logger.info(f"Finished writing trips_stop_times to {trips_stop_times_out}")
    
    # Convert aggregated edges dictionary to a DataFrame
    logger.info(f"Aggregated {len(edge_counts)} unique network edges. Converting to DataFrame...")
    
    edges_list = []
    for (from_stop, to_stop, route_id), weight in edge_counts.items():
        edges_list.append({
            "from_stop_id": from_stop,
            "to_stop_id": to_stop,
            "route_id": route_id,
            "trip_frequency": weight
        })
        
    edges_df = pd.DataFrame(edges_list)
    
    # Save edges parquet
    os.makedirs(os.path.dirname(edges_out), exist_ok=True)
    edges_df.to_parquet(edges_out, index=False)
    logger.info(f"Successfully saved network edges to {edges_out} (shape: {edges_df.shape})")

def main():
    config = load_config()
    build_edges_and_trips(config)

if __name__ == "__main__":
    main()
