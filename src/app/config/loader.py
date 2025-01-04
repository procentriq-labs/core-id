import os
import re
import yaml
from pathlib import Path

from .model import Settings

_cached_settings = None

def load_yaml_config(file_name) -> dict:
    """Load and return the YAML configuration."""
    config_path = config_path = Path(__file__).parent.parent / file_name
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file {file_name} not found.")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config

def merge_environment_config(yaml_config: dict) -> dict:
    """Merge the default config with the environment-specific config."""
    # Determine the environment (default to 'default')
    env = os.getenv("ENV", "default")
    default_config = yaml_config.get("default", {})
    env_config = yaml_config.get(env, {})
    
    # Merge default config with environment-specific config
    merged_config = {**default_config, **env_config}
    
    # Resolve environment variables in the merged config
    return resolve_env_vars(merged_config), env

def resolve_env_vars(config: dict) -> dict:
    """Recursively resolve any environment variables in the config."""
    pattern = re.compile(r'\$\{(\w+)\}')
    
    def replace_env_vars(value):
        if isinstance(value, str):
            # Find all occurrences of ${VAR_NAME} and replace them with environment variable values
            return pattern.sub(lambda match: os.getenv(match.group(1), match.group(0)), value)
        elif isinstance(value, dict):
            # Recursively resolve nested dictionaries
            return {k: replace_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            # Recursively resolve lists
            return [replace_env_vars(item) for item in value]
        else:
            return value

    return replace_env_vars(config)

def load_settings(config_file: str = f"../{os.getenv('WEBAPP_CONF_PATH', 'config.yaml')}") -> Settings: #attention -- this path is different from the one above!!
    """Load settings from the YAML config, merging with env variables."""
    global _cached_settings

    if _cached_settings is None:
        # Load and cache the settings only once
        yaml_config = load_yaml_config(config_file)
        merged_config, environment = merge_environment_config(yaml_config)
        resolved_config = resolve_env_vars(merged_config)

        _cached_settings = Settings(**resolved_config, environment=environment)
    
    return _cached_settings