"""
Command-line interface utilities for DRAGONWIND simulations.

This module provides command-line argument parsing and handling
for configuring simulation runs, scenarios, and output options.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class SimulationOptions:
    """Container for simulation run options parsed from command line."""
    
    start_year: int
    end_year: int
    scenario: str
    config_file: Path
    output_dir: Path
    verbose: bool
    debug: bool
    export_formats: List[str]
    skip_plots: bool
    monte_carlo: bool
    monte_carlo_runs: int
    web_dashboard: bool
    dashboard_port: int


def parse_args() -> SimulationOptions:
    """
    Parse command line arguments for simulation configuration.
    
    Returns:
        SimulationOptions: Parsed simulation options
    """
    parser = argparse.ArgumentParser(
        description="DRAGONWIND - China's Renewable Energy Transition Simulator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Simulation timeframe
    parser.add_argument(
        "--start-year", 
        type=int, 
        default=2025,
        help="Simulation start year"
    )
    parser.add_argument(
        "--end-year", 
        type=int, 
        default=2035,
        help="Simulation end year"
    )
    
    # Scenario selection
    parser.add_argument(
        "--scenario", 
        type=str, 
        default="default",
        help="Simulation scenario to run (from scenarios directory)"
    )
    
    # Configuration options
    parser.add_argument(
        "--config", 
        type=str, 
        default="src/config/defaults.yaml",
        help="Path to configuration YAML file"
    )
    
    # Output options
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="results",
        help="Directory for simulation outputs"
    )
    parser.add_argument(
        "--export", 
        type=str, 
        choices=["csv", "excel", "json", "parquet", "all"],
        nargs="+", 
        default=["parquet"],
        help="Export formats for simulation data"
    )
    parser.add_argument(
        "--skip-plots", 
        action="store_true",
        help="Skip generating plots and visualizations"
    )
    
    # Web dashboard
    parser.add_argument(
        "--web-dashboard", 
        action="store_true",
        help="Launch interactive web dashboard after simulation"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8050,
        help="Port to use for web dashboard"
    )
    
    # Monte Carlo options
    parser.add_argument(
        "--monte-carlo", 
        action="store_true",
        help="Enable Monte Carlo simulation with random parameters"
    )
    parser.add_argument(
        "--mc-runs", 
        type=int, 
        default=100,
        help="Number of Monte Carlo simulation runs"
    )
    
    # Logging options
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode with extra logging"
    )
    
    args = parser.parse_args()
    
    # Convert string paths to Path objects
    config_file = Path(args.config)
    output_dir = Path(args.output_dir)
    
    # Normalize export formats
    export_formats = []
    if "all" in args.export:
        export_formats = ["csv", "excel", "json", "parquet"]
    else:
        export_formats = args.export
        
    return SimulationOptions(
        start_year=args.start_year,
        end_year=args.end_year,
        scenario=args.scenario,
        config_file=config_file,
        output_dir=output_dir,
        verbose=args.verbose,
        debug=args.debug,
        export_formats=export_formats,
        skip_plots=args.skip_plots,
        monte_carlo=args.monte_carlo,
        monte_carlo_runs=args.mc_runs,
        web_dashboard=args.web_dashboard,
        dashboard_port=args.port,
    )
