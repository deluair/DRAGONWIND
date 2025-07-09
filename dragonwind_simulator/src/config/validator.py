"""
Configuration validation utilities for DRAGONWIND.

This module provides schema validation and error checking for configuration files
to help catch problems early with helpful error messages.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import jsonschema
import yaml

from src.utils.exceptions import ConfigurationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Define schema for DRAGONWIND configuration YAML
CONFIG_SCHEMA = {
    "type": "object",
    "required": ["renewable", "grid", "finance", "provincial", "carbon", "bri", 
                 "manufacturing", "installation", "bess", "ev"],
    "properties": {
        "renewable": {
            "type": "object",
            "required": ["initial_capacity", "growth_rates"],
            "properties": {
                "initial_capacity": {
                    "type": "object",
                    "required": ["solar", "wind"],
                    "properties": {
                        "solar": {"type": "number", "minimum": 0},
                        "wind": {"type": "number", "minimum": 0}
                    }
                },
                "growth_rates": {
                    "type": "object",
                    "required": ["solar", "wind"],
                    "properties": {
                        "solar": {"type": "number", "minimum": 0},
                        "wind": {"type": "number", "minimum": 0}
                    }
                }
            }
        },
        "grid": {
            "type": "object",
            "required": ["initial_capacity", "expansion_rate", "curtailment_threshold"],
            "properties": {
                "initial_capacity": {"type": "number", "minimum": 0},
                "expansion_rate": {"type": "number", "minimum": 0},
                "curtailment_threshold": {"type": "number", "minimum": 0, "maximum": 1}
            }
        },
        "finance": {
            "type": "object",
            "required": ["initial_green_bonds", "initial_green_credit", 
                         "growth_rate", "investment_effectiveness"],
            "properties": {
                "initial_green_bonds": {"type": "number", "minimum": 0},
                "initial_green_credit": {"type": "number", "minimum": 0},
                "growth_rate": {"type": "number", "minimum": 0},
                "investment_effectiveness": {"type": "number", "minimum": 0}
            }
        },
        "provincial": {
            "type": "object",
            "required": ["provinces"],
            "properties": {
                "provinces": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "solar_share", "wind_share"],
                        "properties": {
                            "name": {"type": "string"},
                            "solar_share": {"type": "number", "minimum": 0, "maximum": 1},
                            "wind_share": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    }
                }
            }
        },
        "carbon": {
            "type": "object",
            "required": ["baseline_fossil_generation", "emission_factor", 
                         "renewable_capacity_factor"],
            "properties": {
                "baseline_fossil_generation": {"type": "number", "minimum": 0},
                "emission_factor": {"type": "number", "minimum": 0},
                "renewable_capacity_factor": {
                    "type": "object",
                    "required": ["solar", "wind"],
                    "properties": {
                        "solar": {"type": "number", "minimum": 0, "maximum": 1},
                        "wind": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                }
            }
        },
        "bri": {
            "type": "object",
            "required": ["initial_investment", "initial_green_share", 
                         "growth_rate", "domestic_boost_factor"],
            "properties": {
                "initial_investment": {"type": "number", "minimum": 0},
                "initial_green_share": {"type": "number", "minimum": 0, "maximum": 1},
                "growth_rate": {"type": "number", "minimum": 0},
                "domestic_boost_factor": {"type": "number", "minimum": 1}
            }
        },
        "manufacturing": {
            "type": "object",
            "required": ["initial_capacity", "growth_rates"],
            "properties": {
                "initial_capacity": {
                    "type": "object",
                    "required": ["solar", "wind"],
                    "properties": {
                        "solar": {"type": "number", "minimum": 0},
                        "wind": {"type": "number", "minimum": 0}
                    }
                },
                "growth_rates": {
                    "type": "object",
                    "required": ["solar", "wind"],
                    "properties": {
                        "solar": {"type": "number", "minimum": 0},
                        "wind": {"type": "number", "minimum": 0}
                    }
                }
            }
        },
        "installation": {
            "type": "object",
            "required": ["initial_capacity", "growth_rate", "backlog_resolution_rate"],
            "properties": {
                "initial_capacity": {"type": "number", "minimum": 0},
                "growth_rate": {"type": "number", "minimum": 0},
                "backlog_resolution_rate": {"type": "number", "minimum": 0, "maximum": 1}
            }
        },
        "bess": {
            "type": "object",
            "required": ["initial_capacity", "growth_rate", "energy_to_power_ratio"],
            "properties": {
                "initial_capacity": {"type": "number", "minimum": 0},
                "growth_rate": {"type": "number", "minimum": 0},
                "energy_to_power_ratio": {"type": "number", "minimum": 0}
            }
        },
        "ev": {
            "type": "object",
            "required": ["initial_fleet_size", "growth_rate", "kwh_per_vehicle", 
                         "managed_charging_share"],
            "properties": {
                "initial_fleet_size": {"type": "number", "minimum": 0},
                "growth_rate": {"type": "number", "minimum": 0},
                "kwh_per_vehicle": {"type": "number", "minimum": 0},
                "managed_charging_share": {"type": "number", "minimum": 0, "maximum": 1}
            }
        }
    }
}


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate configuration against the schema.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = jsonschema.Draft7Validator(CONFIG_SCHEMA)
    errors = list(validator.iter_errors(config))
    
    if not errors:
        return True, []
    
    # Format errors in a user-friendly way
    error_messages = []
    for error in errors:
        path = ".".join(str(item) for item in error.path) if error.path else "root"
        message = f"Error in {path}: {error.message}"
        error_messages.append(message)
    
    return False, error_messages


def validate_config_file(
    config_path: Union[str, Path],
    verbose: bool = False
) -> Tuple[bool, Dict[str, Any]]:
    """
    Load and validate a configuration file.
    
    Args:
        config_path: Path to configuration file
        verbose: Whether to print validation messages
        
    Returns:
        Tuple of (is_valid, config_dict)
        
    Raises:
        ConfigurationError: If the file can't be loaded or validation fails
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration file: {e}")
    
    is_valid, errors = validate_config(config)
    
    if verbose:
        if is_valid:
            logger.info(f"Configuration file is valid: {config_path}")
        else:
            logger.error(f"Configuration file has {len(errors)} validation errors:")
            for error in errors:
                logger.error(f"  {error}")
    
    if not is_valid:
        error_str = "\n".join(errors)
        raise ConfigurationError(
            f"Configuration validation failed:\n{error_str}"
        )
    
    return is_valid, config


def check_config_consistency(config: Dict[str, Any]) -> List[str]:
    """
    Perform additional consistency checks on configuration.
    
    This goes beyond schema validation to check for logical consistency
    across different parts of the configuration.
    
    Args:
        config: Configuration dictionary to check
        
    Returns:
        List of warning messages (empty if all checks pass)
    """
    warnings = []
    
    try:
        # Check that provincial shares sum to reasonable values
        province_solar_share_sum = sum(
            p.get("solar_share", 0) 
            for p in config.get("provincial", {}).get("provinces", [])
        )
        province_wind_share_sum = sum(
            p.get("wind_share", 0) 
            for p in config.get("provincial", {}).get("provinces", [])
        )
        
        if province_solar_share_sum > 1.001:  # Allow small rounding errors
            warnings.append(
                f"Warning: Province solar shares sum to {province_solar_share_sum}, "
                f"which exceeds 1.0 (100%)"
            )
        if province_wind_share_sum > 1.001:
            warnings.append(
                f"Warning: Province wind shares sum to {province_wind_share_sum}, "
                f"which exceeds 1.0 (100%)"
            )
        
        # Check for reasonable initial capacity vs growth rates
        solar_capacity = config.get("renewable", {}).get("initial_capacity", {}).get("solar", 0)
        solar_growth = config.get("renewable", {}).get("growth_rates", {}).get("solar", 0)
        
        if solar_capacity > 0 and solar_growth / solar_capacity > 0.3:
            warnings.append(
                f"Warning: Solar growth rate ({solar_growth} GW/year) seems high "
                f"compared to initial capacity ({solar_capacity} GW)"
            )
        
        # Check that manufacturing capacity can support renewable deployment
        mfg_solar = config.get("manufacturing", {}).get("initial_capacity", {}).get("solar", 0)
        if mfg_solar < solar_growth * 0.8:
            warnings.append(
                f"Warning: Initial solar manufacturing capacity ({mfg_solar} GW/year) "
                f"may be insufficient for solar growth rate ({solar_growth} GW/year)"
            )
        
        # Check that installation capacity is reasonable
        install_capacity = config.get("installation", {}).get("initial_capacity", 0)
        total_renewable_growth = (
            config.get("renewable", {}).get("growth_rates", {}).get("solar", 0) +
            config.get("renewable", {}).get("growth_rates", {}).get("wind", 0)
        )
        if install_capacity < total_renewable_growth * 0.8:
            warnings.append(
                f"Warning: Initial installation capacity ({install_capacity} GW/year) "
                f"may be insufficient for total renewable growth ({total_renewable_growth} GW/year)"
            )
        
    except Exception as e:
        warnings.append(f"Warning: Could not complete all consistency checks: {e}")
    
    return warnings
