import logging
import sys

def setup_logger(name="urban-mobility"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Console Handler
        ch = sys.stdout
        handler = logging.StreamHandler(ch)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
