"""Utility to load YAML configuration files for DRAGONWIND."""
from __future__ import annotations

import os
import json
import copy
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, TypedDict, cast, Literal

import yaml
from jsonschema import validate

# Define the path to the default configuration file
DEFAULT_CONFIG_PATH: Path = Path(__file__).with_name("defaults.yaml")
# Define the path to the JSON schema file for validation
SCHEMA_PATH: Path = Path(__file__).with_name("schema.json")


def load_config(path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load a YAML configuration file.

    If *path* is ``None`` use the package default ``defaults.yaml`` located
    next to this loader module.
    
    Args:
        path: Path to the configuration file. Can be a string or Path object.
            If None, the default configuration will be loaded.
            
    Returns:
        Dict[str, Any]: The loaded configuration as a dictionary.
        
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If the YAML file is malformed.
    """
    cfg_path: Path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as fh:
        try:
            config: Dict[str, Any] = yaml.safe_load(fh)
            return config
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            raise


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate a configuration dictionary against the JSON schema.
    
    Args:
        config: The configuration dictionary to validate.
        
    Returns:
        bool: True if the configuration is valid.
        
    Raises:
        jsonschema.exceptions.ValidationError: If the configuration is invalid.
        FileNotFoundError: If the schema file does not exist.
    """
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")
        
    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        schema: Dict[str, Any] = json.load(fh)
        
    # Validate the configuration against the schema
    validate(instance=config, schema=schema)
    return True


def save_config(config: Dict[str, Any], path: Union[str, Path]) -> Path:
    """Save a configuration dictionary to a YAML file.
    
    Args:
        config: The configuration dictionary to save.
        path: The path to save the configuration to.
        
    Returns:
        Path: The path where the configuration was saved.
        
    Raises:
        OSError: If there is an error writing to the file.
    """
    out_path: Path = Path(path)
    
    # Ensure the parent directory exists
    os.makedirs(out_path.parent, exist_ok=True)
    
    # Write the configuration to the file
    with out_path.open("w", encoding="utf-8") as fh:
        yaml.dump(config, fh, default_flow_style=False, sort_keys=False)
        
    return out_path


def deep_update(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively update a base configuration with an override configuration.
    
    Args:
        base_config: The base configuration to update.
        override_config: The configuration to override the base with.
        
    Returns:
        Dict[str, Any]: The updated configuration.
    """
    result: Dict[str, Any] = copy.deepcopy(base_config)
    
    for k, v in override_config.items():
        if isinstance(v, dict) and k in result and isinstance(result[k], dict):
            result[k] = deep_update(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
            
    return result
