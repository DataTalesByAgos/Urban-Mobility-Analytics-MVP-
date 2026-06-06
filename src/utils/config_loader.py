import yaml
import os

def load_config(config_path="config.yaml"):
    """Loads configuration from a YAML file."""
    if not os.path.exists(config_path):
        # Check parent directory in case we are running from a subdirectory
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
        if not os.path.exists(config_path):
            raise FileNotFoundError("config.yaml not found.")
            
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
