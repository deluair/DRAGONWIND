from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List, TypeVar, Generic
import pandas as pd

# Forward reference for SimulationEngine
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .simulation_engine import SimulationEngine

class SimulationComponent(ABC):
    """
    Abstract base class for all simulation components in the DRAGONWIND platform.

    Each component represents a distinct part of the simulation, such as
    renewable energy capacity expansion, grid integration, or financial modeling.
    Components are managed and executed by the SimulationEngine.
    """

    def __init__(self, name: str) -> None:
        """
        Initializes the simulation component.

        Args:
            name (str): The name of the component.
        """
        self.name: str = name
        self.simulation_engine: Optional['SimulationEngine'] = None
        self.results: Dict[str, Any] = {}

    def set_engine(self, engine: 'SimulationEngine') -> None:
        """
        Sets the simulation engine for this component.

        This is typically called by the SimulationEngine when the component is added.

        Args:
            engine: The simulation engine instance.
        """
        self.simulation_engine = engine

    @abstractmethod
    def initialize(self) -> None:
        """
        Initializes the component's state before the simulation starts.
        This is where you would load data, set up initial conditions, etc.
        """
        pass

    @abstractmethod
    def step(self, time_step: int) -> None:
        """
        Executes one step of the simulation for this component.

        Args:
            time_step (int): The current time step of the simulation.
        """
        pass

    @abstractmethod
    def finalize(self) -> None:
        """
        Finalizes the component's state after the simulation ends.
        This is where you would save results, clean up resources, etc.
        """
        pass
        
    def get_results(self) -> Dict[str, Any]:
        """
        Returns the results of this component's simulation.
        
        Returns:
            Dict[str, Any]: A dictionary of results, potentially including pandas DataFrames,
                          numpy arrays, or other data structures.
        """
        return self.results
        
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Returns the component's results as a pandas DataFrame, if available.
        
        Returns:
            Optional[pd.DataFrame]: The component's results as a DataFrame, or None if not available.
        """
        if 'dataframe' in self.results and isinstance(self.results['dataframe'], pd.DataFrame):
            return self.results['dataframe']
        return None
