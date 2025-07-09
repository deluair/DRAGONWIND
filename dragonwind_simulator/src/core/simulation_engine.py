from typing import List, Dict, Any, Optional, Union, TypeVar, Callable, Iterator, Tuple, Set
from pathlib import Path
import pandas as pd
from .base_component import SimulationComponent

# Type variable for components
T = TypeVar('T', bound=SimulationComponent)

class SimulationEngine:
    """
    The core simulation engine for the DRAGONWIND platform.

    This class manages the simulation components, runs the main simulation loop,
    and orchestrates the overall execution of the simulation.
    """

    def __init__(self, start_year: int, end_year: int) -> None:
        """
        Initializes the simulation engine.

        Args:
            start_year (int): The starting year of the simulation.
            end_year (int): The ending year of the simulation.
        """
        self.start_year: int = start_year
        self.end_year: int = end_year
        self.components: List[SimulationComponent] = []
        self.state: Dict[str, Any] = {}  # Shared state dictionary for components

    def add_component(self, component: SimulationComponent) -> None:
        """
        Adds a simulation component to the engine.

        Args:
            component (SimulationComponent): The component to add.
        """
        component.set_engine(self)
        self.components.append(component)

    def run(self, progress: Optional[Any] = None) -> None:
        """
        Runs the entire simulation from start to finish.
        
        Args:
            progress: Optional progress tracker instance to report progress.
        """
        print("Starting DRAGONWIND simulation...", flush=True)
        self._initialize_components()
        self._run_simulation_loop(progress=progress)
        self._finalize_components()
        print("DRAGONWIND simulation finished.", flush=True)

    def _initialize_components(self) -> None:
        """
        Initializes all registered components.
        """
        print("Initializing components...", flush=True)
        for component in self.components:
            component.initialize()

    def _run_simulation_loop(self, progress: Optional[Any] = None) -> None:
        """
        Executes the main simulation loop.
        
        Args:
            progress: Optional progress tracker instance to report progress.
        """
        print(f"Running simulation from {self.start_year} to {self.end_year}...", flush=True)
        total_years = self.end_year - self.start_year + 1
        
        for i, year in enumerate(range(self.start_year, self.end_year + 1)):
            print(f"  Simulating year: {year}", flush=True)
            for component in self.components:
                component.step(year)
                
            # Update progress if available
            if progress is not None:
                try:
                    progress.update(1, description=f"Year: {year}")
                except Exception as e:
                    print(f"Warning: Could not update progress: {e}", flush=True)

    def _finalize_components(self) -> None:
        """
        Finalizes all registered components.
        """
        print("\nFinalizing components...", flush=True)
        for component in self.components:
            component.finalize()

        # ------------------------------------------------------------------
        # Collect KPIs and generate visuals
        # ------------------------------------------------------------------
        try:
            from src.analytics.collector import ResultsCollector
            from src.analytics import plots as _plots

            collector = ResultsCollector(self.components)
            parquet_path: Optional[Path] = collector.run()
            if parquet_path:
                fig_dir: Path = parquet_path.parent / "figures"
                _plots.generate_static_figures(parquet_path, fig_dir)
                _plots.generate_interactive_dashboard(parquet_path, fig_dir)
                print(f"KPI parquet written to {parquet_path}", flush=True)
                print(f"Figures saved to {fig_dir}", flush=True)
        except Exception as exc:
            print(f"[SimulationEngine] Warning: analytics generation failed: {exc}", flush=True)
