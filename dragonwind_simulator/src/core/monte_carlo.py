"""
Monte Carlo simulation capabilities for DRAGONWIND.

This module provides tools for running multiple simulation iterations
with randomized parameters to analyze uncertainty and sensitivity.
"""

import copy
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, TypeVar, cast, TypedDict, Protocol

import numpy as np
import pandas as pd
import scipy.stats as stats

from src.core.simulation_engine import SimulationEngine
from src.utils.exceptions import SimulationError
from src.utils.logger import get_logger
from src.utils.progress import ProgressTracker

# Type aliases for improved readability
ConfigDict = Dict[str, Any]
ParameterValue = Union[float, int, str, bool]
ParameterPath = List[str]
PathStr = str
SampledParams = Dict[str, ParameterValue]
ResultsDict = Dict[str, pd.DataFrame]

# Function type for engine creation
EngineFactory = Callable[[ConfigDict], SimulationEngine]

logger = get_logger(__name__)


@dataclass
class ParameterDistribution:
    """
    Defines a probability distribution for parameter sampling.
    
    Supports common distribution types (normal, uniform, triangular)
    with appropriate parameters.
    """
    
    param_path: ParameterPath  # Path to parameter in config dict (e.g., ["renewable", "growth_rate", "solar"])
    distribution: str      # Distribution type: "normal", "uniform", "triangular", "discrete"
    params: Dict[str, Any] # Distribution parameters
    
    def sample(self) -> ParameterValue:
        """
        Sample a random value from this parameter's distribution.
        
        Returns:
            A random value from the specified distribution
        
        Raises:
            ValueError: If an unknown distribution is specified
        """
        if self.distribution == "normal":
            return float(np.random.normal(
                loc=self.params.get("mean", 0),
                scale=self.params.get("std", 1)
            ))
        
        elif self.distribution == "uniform":
            return float(np.random.uniform(
                low=self.params.get("low", 0),
                high=self.params.get("high", 1)
            ))
            
        elif self.distribution == "triangular":
            return float(np.random.triangular(
                left=self.params.get("low", 0),
                mode=self.params.get("mode", 0.5),
                right=self.params.get("high", 1)
            ))
            
        elif self.distribution == "discrete":
            values = self.params.get("values", [])
            probs = self.params.get("probabilities", None)
            if not values:
                raise ValueError("Discrete distribution must specify 'values'")
            return cast(ParameterValue, np.random.choice(values, p=probs))
            
        else:
            raise ValueError(f"Unknown distribution: {self.distribution}")


class SimulationResult(TypedDict):
    """Type definition for simulation run results."""
    iteration: int
    parameters: SampledParams
    results: ResultsDict


class MonteCarloSimulation:
    """
    Runs multiple simulation iterations with randomized parameters.
    
    This allows for uncertainty analysis and sensitivity testing of the
    simulation results to key parameter variations.
    """
    
    def __init__(
        self,
        base_config: ConfigDict,
        parameter_distributions: List[ParameterDistribution],
        n_iterations: int = 100,
        save_all_runs: bool = False,
        output_dir: Optional[Union[str, Path]] = None
    ) -> None:
        """
        Initialize a Monte Carlo simulation runner.
        
        Args:
            base_config: Base configuration dictionary
            parameter_distributions: List of parameter distributions to sample from
            n_iterations: Number of Monte Carlo iterations to run
            save_all_runs: Whether to save results from all runs (vs. just statistics)
            output_dir: Directory to save results (default: results/monte_carlo_TIMESTAMP)
        """
        self.base_config: ConfigDict = base_config
        self.parameter_distributions: List[ParameterDistribution] = parameter_distributions
        self.n_iterations: int = n_iterations
        self.save_all_runs: bool = save_all_runs
        
        # Set up output directory
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_dir is None:
            self.output_dir: Path = Path(f"results/monte_carlo_{timestamp}")
        else:
            self.output_dir: Path = Path(output_dir)
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Monte Carlo results will be saved to: {self.output_dir}")
        
        # Store results
        self.results: List[SimulationResult] = []
        self.parameter_samples: List[SampledParams] = []
    
    def _get_nested_param(self, config: ConfigDict, path: ParameterPath) -> Any:
        """
        Get a parameter from a nested dictionary using a path.
        
        Args:
            config: Configuration dictionary
            path: Path to parameter as a list of keys
            
        Returns:
            The parameter value
            
        Raises:
            KeyError: If the path is invalid
        """
        result: Any = config
        for key in path:
            result = result[key]
        return result
    
    def _set_nested_param(self, config: ConfigDict, path: ParameterPath, value: ParameterValue) -> None:
        """
        Set a parameter in a nested dictionary using a path.
        
        Args:
            config: Configuration dictionary
            path: Path to parameter as a list of keys
            value: Value to set
            
        Raises:
            KeyError: If the path is invalid
        """
        target: Dict[str, Any] = config
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    
    def _sample_parameters(self) -> SampledParams:
        """
        Sample parameters from all distributions.
        
        Returns:
            Dictionary mapping parameter paths to sampled values
        """
        samples: SampledParams = {}
        for param in self.parameter_distributions:
            sample_value = param.sample()
            samples[".".join(param.param_path)] = sample_value
        return samples
    
    def _apply_samples(self, config: ConfigDict, samples: SampledParams) -> ConfigDict:
        """
        Apply sampled parameters to a configuration dictionary.
        
        Args:
            config: Configuration dictionary
            samples: Dictionary mapping parameter paths to sampled values
            
        Returns:
            Updated configuration dictionary
        """
        # Create a deep copy to avoid modifying the original
        config_copy: ConfigDict = copy.deepcopy(config)
        
        # Apply each parameter
        for param in self.parameter_distributions:
            path_str: PathStr = ".".join(param.param_path)
            if path_str in samples:
                self._set_nested_param(
                    config_copy,
                    param.param_path,
                    samples[path_str]
                )
                
        return config_copy
    
    def run(self, create_engine_func: EngineFactory) -> pd.DataFrame:
        """
        Run the Monte Carlo simulation.
        
        Args:
            create_engine_func: Function that creates a SimulationEngine from a config
            
        Returns:
            DataFrame with summary statistics of the results
            
        Raises:
            SimulationError: If simulations fail
        """
        self.results = []
        self.parameter_samples = []
        
        # Create progress bar for Monte Carlo iterations
        progress = ProgressTracker(
            total=self.n_iterations,
            description="Monte Carlo Simulation",
            unit="run",
            color="blue"
        )
        
        try:
            for i in range(self.n_iterations):
                # Sample parameters and record
                samples: SampledParams = self._sample_parameters()
                self.parameter_samples.append(samples)
                
                # Apply sampled parameters to config
                iter_config: ConfigDict = self._apply_samples(self.base_config, samples)
                
                try:
                    # Create and run the simulation
                    engine: SimulationEngine = create_engine_func(iter_config)
                    engine.run()
                    
                    # Collect results
                    iter_results: SimulationResult = {
                        "iteration": i,
                        "parameters": samples,
                        "results": engine.get_all_results()
                    }
                    
                    self.results.append(iter_results)
                    
                except Exception as e:
                    logger.error(f"Error in Monte Carlo iteration {i}: {e}")
                    # Continue with next iteration
                
                progress.update(description=f"Run {i+1}/{self.n_iterations}")
                
            # Process and analyze results
            logger.info(f"Monte Carlo simulation completed with {len(self.results)} successful runs")
            return self._analyze_results()
            
        finally:
            progress.close()
    
    def _analyze_results(self) -> pd.DataFrame:
        """
        Analyze Monte Carlo results to generate statistics.
        
        Returns:
            DataFrame with result statistics
        """
        if not self.results:
            logger.warning("No Monte Carlo results to analyze")
            return pd.DataFrame()
        
        # Extract key metrics from all runs
        metrics: Dict[str, List[float]] = {}
        
        # Iterate through results to extract key metrics for each module
        for run in self.results:
            run_results: ResultsDict = run["results"]
            
            # Process each module's results
            for module_name, df in run_results.items():
                if df is None or df.empty:
                    continue
                    
                # Get the last row for final values
                final_values: Dict[str, float] = df.iloc[-1].to_dict()
                
                # Store metrics by module and metric name
                for metric_name, value in final_values.items():
                    if isinstance(value, (int, float)):
                        key: str = f"{module_name}.{metric_name}"
                        if key not in metrics:
                            metrics[key] = []
                        metrics[key].append(value)
        
        # Calculate statistics for each metric
        stats_data: List[Dict[str, float]] = []
        for key, values in metrics.items():
            values_array: np.ndarray = np.array(values)
            row: Dict[str, float] = {
                "metric": key,
                "mean": np.mean(values_array),
                "median": np.median(values_array),
                "std": np.std(values_array),
                "min": np.min(values_array),
                "max": np.max(values_array),
                "p10": np.percentile(values_array, 10),
                "p25": np.percentile(values_array, 25),
                "p75": np.percentile(values_array, 75),
                "p90": np.percentile(values_array, 90),
                "count": len(values_array)
            }
            stats_data.append(row)
        
        # Create summary DataFrame
        summary_df: pd.DataFrame = pd.DataFrame(stats_data)
        
        # Save results
        self._save_results(summary_df)
        
        return summary_df
    
    def _save_results(self, summary_df: pd.DataFrame) -> None:
        """
        Save Monte Carlo results to the output directory.
        
        Args:
            summary_df: DataFrame with summary statistics
        """
        # Save summary statistics
        summary_path: Path = self.output_dir / "summary_statistics.csv"
        summary_df.to_csv(summary_path, index=False)
        logger.info(f"Saved summary statistics to {summary_path}")
        
        # Save parameter samples
        params_df: pd.DataFrame = pd.DataFrame(self.parameter_samples)
        params_path: Path = self.output_dir / "parameter_samples.csv"
        params_df.to_csv(params_path, index=False)
        logger.info(f"Saved parameter samples to {params_path}")
        
        # Optionally save all run results
        if self.save_all_runs:
            all_runs_dir: Path = self.output_dir / "all_runs"
            os.makedirs(all_runs_dir, exist_ok=True)
            
            for i, run in enumerate(self.results):
                run_dir: Path = all_runs_dir / f"run_{i:04d}"
            for i, run in enumerate(self.results):
                run_dir = all_runs_dir / f"run_{i:04d}"
                os.makedirs(run_dir, exist_ok=True)
                
                # Save parameters
                pd.Series(run["parameters"]).to_csv(run_dir / "parameters.csv")
                
                # Save each module's results
                for module_name, df in run["results"].items():
                    if df is not None and not df.empty:
                        df.to_csv(run_dir / f"{module_name}.csv")
                        
            logger.info(f"Saved detailed results for all runs to {all_runs_dir}")
    
    def generate_sensitivity_analysis(self) -> Dict[str, pd.DataFrame]:
        """
        Perform sensitivity analysis to identify most influential parameters.
        
        Returns:
            Dictionary mapping metrics to DataFrames with correlation coefficients
        """
        if not self.results or not self.parameter_samples:
            logger.warning("No Monte Carlo results for sensitivity analysis")
            return {}
        
        # Convert parameter samples to DataFrame
        params_df = pd.DataFrame(self.parameter_samples)
        
        # Extract metrics from all runs
        metrics_data = {}
        
        for run in self.results:
            run_results = run["results"]
            iteration = run["iteration"]
            
            # Process each module's results
            for module_name, df in run_results.items():
                if df is None or df.empty:
                    continue
                    
                # Get the last row for final values
                final_values = df.iloc[-1].to_dict()
                
                # Store metrics by module and metric name
                for metric_name, value in final_values.items():
                    if isinstance(value, (int, float)):
                        key = f"{module_name}.{metric_name}"
                        if key not in metrics_data:
                            metrics_data[key] = {}
                        metrics_data[key][iteration] = value
        
        # Calculate correlations between parameters and metrics
        sensitivity_results = {}
        
        for metric_name, values_dict in metrics_data.items():
            # Convert to Series
            metric_series = pd.Series(values_dict)
            
            # Only analyze metrics with sufficient data points
            if len(metric_series) < 10:
                continue
                
            # Calculate correlations with all parameters
            correlations = {}
            
            for param_name in params_df.columns:
                # Filter to matching iterations
                param_values = params_df[param_name].reindex(metric_series.index)
                
                # Calculate Pearson correlation
                if len(param_values) >= 2:  # Need at least 2 points for correlation
                    corr, p_value = stats.pearsonr(param_values, metric_series)
                    correlations[param_name] = {
                        "correlation": corr,
                        "p_value": p_value,
                        "abs_correlation": abs(corr)
                    }
            
            # Convert to DataFrame and sort by absolute correlation
            corr_df = pd.DataFrame.from_dict(correlations, orient="index")
            if not corr_df.empty:
                corr_df = corr_df.sort_values("abs_correlation", ascending=False)
                sensitivity_results[metric_name] = corr_df
        
        # Save sensitivity results
        for metric_name, corr_df in sensitivity_results.items():
            safe_name = metric_name.replace(".", "_")
            file_path = self.output_dir / f"sensitivity_{safe_name}.csv"
            corr_df.to_csv(file_path)
            
        logger.info(f"Saved sensitivity analysis results to {self.output_dir}")
        
        return sensitivity_results
