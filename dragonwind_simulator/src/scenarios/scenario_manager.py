"""
Scenario management system for DRAGONWIND simulations.

This module provides tools for defining, loading, and comparing different
policy and technology scenarios in renewable energy transitions.
"""

import copy
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from src.config.loader import load_config
from src.utils.exceptions import ScenarioError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Scenario:
    """
    A scenario represents a specific set of simulation parameters and assumptions.
    
    Scenarios can be defined as modifications to the base configuration,
    allowing for comparison of different policy or technology pathways.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        base_config: Dict[str, Any],
        overrides: Dict[str, Any]
    ):
        """
        Initialize a scenario with name, description, and parameter overrides.
        
        Args:
            name: Unique scenario identifier
            description: Human-readable description
            base_config: Base configuration dictionary
            overrides: Dictionary of parameters to override in base config
        """
        self.name = name
        self.description = description
        self.base_config = base_config
        self.overrides = overrides
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        Get the complete configuration for this scenario.
        
        Returns:
            Dict containing merged base configuration and overrides
        """
        if self._config is None:
            # Deep copy to avoid modifying the original
            self._config = copy.deepcopy(self.base_config)
            
            # Apply overrides using recursive dictionary update
            self._update_dict_recursive(self._config, self.overrides)
            
        return self._config
    
    def _update_dict_recursive(self, target: Dict, source: Dict) -> None:
        """
        Recursively update a nested dictionary with values from another dictionary.
        
        Args:
            target: Dictionary to update
            source: Dictionary with values to apply
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict_recursive(target[key], value)
            else:
                target[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the scenario to a serializable dictionary.
        
        Returns:
            Dict representation of the scenario
        """
        return {
            "name": self.name,
            "description": self.description,
            "overrides": self.overrides
        }
    
    def save(self, directory: Union[str, Path]) -> Path:
        """
        Save the scenario to a YAML file.
        
        Args:
            directory: Directory to save the scenario file in
            
        Returns:
            Path to the saved scenario file
        """
        os.makedirs(directory, exist_ok=True)
        file_path = Path(directory) / f"{self.name}.yaml"
        
        with open(file_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
            
        logger.info(f"Saved scenario '{self.name}' to {file_path}")
        return file_path


class ScenarioManager:
    """
    Manager for creating, loading and comparing simulation scenarios.
    """
    
    def __init__(self, scenarios_dir: Union[str, Path] = None, base_config_path: Union[str, Path] = None):
        """
        Initialize the scenario manager.
        
        Args:
            scenarios_dir: Directory containing scenario YAML files
            base_config_path: Path to the base configuration YAML
        """
        # Set default paths if not provided
        if scenarios_dir is None:
            project_root = Path(__file__).parent.parent.parent
            scenarios_dir = project_root / "scenarios"
            
        if base_config_path is None:
            project_root = Path(__file__).parent.parent.parent
            base_config_path = project_root / "src" / "config" / "defaults.yaml"
        
        self.scenarios_dir = Path(scenarios_dir)
        self.base_config_path = Path(base_config_path)
        
        # Ensure scenarios directory exists
        os.makedirs(self.scenarios_dir, exist_ok=True)
        
        # Load base configuration
        self.base_config = load_config(self.base_config_path)
        
        # Scenario cache
        self._scenarios = {}
        
    def create_scenario(
        self,
        name: str,
        description: str,
        overrides: Dict[str, Any]
    ) -> Scenario:
        """
        Create a new scenario with the specified parameters.
        
        Args:
            name: Unique scenario identifier
            description: Human-readable description
            overrides: Dictionary of parameters to override in base config
            
        Returns:
            The newly created Scenario object
        
        Raises:
            ScenarioError: If a scenario with this name already exists
        """
        if name in self._scenarios:
            raise ScenarioError(f"Scenario '{name}' already exists")
        
        scenario = Scenario(
            name=name,
            description=description,
            base_config=self.base_config,
            overrides=overrides
        )
        
        self._scenarios[name] = scenario
        return scenario
    
    def save_scenario(self, scenario: Scenario) -> Path:
        """
        Save a scenario to the scenarios directory.
        
        Args:
            scenario: The scenario to save
            
        Returns:
            Path to the saved scenario file
        """
        return scenario.save(self.scenarios_dir)
    
    def list_scenarios(self) -> List[str]:
        """
        List all available scenario names from the scenarios directory.
        
        Returns:
            List of scenario names
        """
        self._load_all_scenarios()
        return list(self._scenarios.keys())
    
    def get_scenario(self, name: str) -> Scenario:
        """
        Get a scenario by name, loading it from file if necessary.
        
        Args:
            name: Name of the scenario to load
            
        Returns:
            The requested Scenario object
            
        Raises:
            ScenarioError: If the scenario does not exist
        """
        if name == "default":
            # Special case for the default scenario (no overrides)
            if "default" not in self._scenarios:
                self._scenarios["default"] = Scenario(
                    "default",
                    "Default scenario using base configuration values",
                    self.base_config,
                    {}
                )
            return self._scenarios["default"]
            
        # Try to load from cache first
        if name in self._scenarios:
            return self._scenarios[name]
        
        # Try to load from file
        scenario_path = self.scenarios_dir / f"{name}.yaml"
        if not scenario_path.exists():
            raise ScenarioError(f"Scenario '{name}' not found")
        
        try:
            with open(scenario_path, 'r') as f:
                scenario_dict = yaml.safe_load(f)
            
            scenario = Scenario(
                name=scenario_dict.get("name", name),
                description=scenario_dict.get("description", ""),
                base_config=self.base_config,
                overrides=scenario_dict.get("overrides", {})
            )
            
            self._scenarios[name] = scenario
            return scenario
            
        except Exception as e:
            raise ScenarioError(f"Failed to load scenario '{name}': {e}")
    
    def _load_all_scenarios(self) -> None:
        """Load all scenario files from the scenarios directory."""
        for file_path in self.scenarios_dir.glob("*.yaml"):
            scenario_name = file_path.stem
            if scenario_name not in self._scenarios:
                try:
                    self.get_scenario(scenario_name)
                except ScenarioError as e:
                    logger.warning(f"Failed to load scenario file {file_path}: {e}")

    def compare_scenarios(self, scenario_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple scenarios to identify differences.
        
        Args:
            scenario_names: List of scenario names to compare
            
        Returns:
            Dictionary of differences between scenarios
            
        Raises:
            ScenarioError: If any scenario does not exist
        """
        if len(scenario_names) < 2:
            raise ValueError("Need at least two scenarios to compare")
        
        # Load all requested scenarios
        scenarios = {}
        for name in scenario_names:
            scenarios[name] = self.get_scenario(name)
        
        # Compare overrides
        comparison = {}
        for name, scenario in scenarios.items():
            comparison[name] = scenario.overrides
            
        return comparison
