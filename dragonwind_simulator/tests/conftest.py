"""
Pytest configuration and common fixtures for DRAGONWIND tests.
"""

import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.config.loader import load_config
from src.core.simulation_engine import SimulationEngine
from src.modules.renewable_energy.capacity_expansion import RenewableCapacityExpansion
from src.modules.grid_integration.curtailment_analysis import GridIntegration
from src.modules.financial_modeling.green_finance import FinancialModeling


@pytest.fixture
def sample_config():
    """Fixture providing a minimal valid configuration dictionary."""
    return {
        "renewable": {
            "initial_capacity": {
                "solar": 100.0,
                "wind": 50.0
            },
            "growth_rates": {
                "solar": 10.0,
                "wind": 5.0
            }
        },
        "grid": {
            "initial_capacity": 200.0,
            "expansion_rate": 20.0,
            "curtailment_threshold": 0.9
        },
        "finance": {
            "initial_green_bonds": 100.0,
            "initial_green_credit": 200.0,
            "growth_rate": 0.1,
            "investment_effectiveness": 0.05
        },
        "provincial": {
            "provinces": [
                {
                    "name": "TestProvince1",
                    "solar_share": 0.3,
                    "wind_share": 0.4
                },
                {
                    "name": "TestProvince2",
                    "solar_share": 0.7,
                    "wind_share": 0.6
                }
            ]
        },
        "carbon": {
            "baseline_fossil_generation": 1000.0,
            "emission_factor": 0.7,
            "renewable_capacity_factor": {
                "solar": 0.18,
                "wind": 0.25
            }
        },
        "bri": {
            "initial_investment": 50.0,
            "initial_green_share": 0.3,
            "growth_rate": 0.1,
            "domestic_boost_factor": 1.05
        },
        "manufacturing": {
            "initial_capacity": {
                "solar": 12.0,
                "wind": 6.0
            },
            "growth_rates": {
                "solar": 1.2,
                "wind": 0.6
            }
        },
        "installation": {
            "initial_capacity": 18.0,
            "growth_rate": 0.1,
            "backlog_resolution_rate": 0.2
        },
        "bess": {
            "initial_capacity": 5.0,
            "growth_rate": 0.2,
            "energy_to_power_ratio": 4.0
        },
        "ev": {
            "initial_fleet_size": 1.0,
            "growth_rate": 0.25,
            "kwh_per_vehicle": 50.0,
            "managed_charging_share": 0.3
        }
    }


@pytest.fixture
def config_file(sample_config, tmp_path):
    """Fixture providing a temporary YAML config file."""
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f)
    return config_path


@pytest.fixture
def temp_results_dir():
    """Fixture providing a temporary directory for test results."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def simulation_engine():
    """Fixture providing a basic simulation engine instance."""
    return SimulationEngine(start_year=2025, end_year=2026)


@pytest.fixture
def renewable_component(sample_config):
    """Fixture providing an initialized renewable capacity expansion component."""
    component = RenewableCapacityExpansion()
    component.configure(sample_config)
    return component


@pytest.fixture
def grid_component(sample_config):
    """Fixture providing an initialized grid integration component."""
    component = GridIntegration()
    component.configure(sample_config)
    return component


@pytest.fixture
def finance_component(sample_config):
    """Fixture providing an initialized financial modeling component."""
    component = FinancialModeling()
    component.configure(sample_config)
    return component


@pytest.fixture
def sample_results_data():
    """Fixture providing sample simulation results data."""
    years = range(2025, 2030)
    
    # Create sample renewable capacity data
    renewable_data = {
        'year': list(years),
        'solar_capacity': [100, 110, 121, 133, 146],
        'wind_capacity': [50, 55, 60, 66, 73],
        'total_capacity': [150, 165, 181, 199, 219]
    }
    
    # Create sample grid data
    grid_data = {
        'year': list(years),
        'grid_capacity': [200, 220, 242, 266, 293],
        'curtailment_rate': [0.0, 0.0, 0.0, 0.01, 0.02]
    }
    
    # Create sample financial data
    finance_data = {
        'year': list(years),
        'green_bonds': [100, 110, 121, 133, 146],
        'green_credit': [200, 220, 242, 266, 293],
        'total_investment': [300, 330, 363, 399, 439]
    }
    
    # Create DataFrames
    renewable_df = pd.DataFrame(renewable_data)
    renewable_df.set_index('year', inplace=True)
    
    grid_df = pd.DataFrame(grid_data)
    grid_df.set_index('year', inplace=True)
    
    finance_df = pd.DataFrame(finance_data)
    finance_df.set_index('year', inplace=True)
    
    return {
        'renewable': renewable_df,
        'grid': grid_df,
        'finance': finance_df
    }
