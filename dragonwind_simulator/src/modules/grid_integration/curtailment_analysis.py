from src.core.base_component import SimulationComponent
from src.config.loader import load_config

class GridIntegration(SimulationComponent):
    """
    Models grid integration challenges and curtailment of renewable energy.

    This component simulates how much of the generated renewable energy can be
    effectively integrated into the grid, considering transmission constraints
    and local demand.
    """

    def __init__(self, name: str = "Grid Integration"):
        super().__init__(name)
        self.renewable_capacity_module = None

    def initialize(self):
        """
        Initializes the component's state.
        - Get a reference to the renewable capacity module.
        - Set up initial grid capacity and curtailment rates.
        """
        print(f"Initializing {self.name} component...", flush=True)
        # Find the renewable capacity component to get its output
        # A more robust solution would use a dedicated state management system
        try:
            self.renewable_capacity_module = next(
                comp for comp in self.simulation_engine.components 
                if comp.name == "Renewable Capacity Expansion"
            )
        except StopIteration:
            raise RuntimeError("Renewable Capacity Expansion module not found.", flush=True)

        self.history = []
        cfg = load_config()
        self.grid_transmission_capacity = cfg['grid']['initial_transmission_gw']
        self.expansion_rate = cfg['grid']['annual_expansion_rate']
        print(f"Initial Grid Transmission Capacity: {self.grid_transmission_capacity} GW", flush=True)

    def step(self, time_step: int):
        """
        Executes one simulation step for the given year.
        - Calculate potential generation from renewable capacity.
        - Simulate curtailment based on grid constraints.

        Args:
            time_step (int): The current simulation year.
        """
        print(f"Executing {self.name} step for year {time_step}...", flush=True)
        # Get the current renewable capacity from the other module
        current_capacity = self.renewable_capacity_module.capacity
        total_renewable_capacity = sum(current_capacity.values())

        # Simple curtailment model
        if total_renewable_capacity > self.grid_transmission_capacity:
            curtailed_capacity = total_renewable_capacity - self.grid_transmission_capacity
            curtailment_rate = (curtailed_capacity / total_renewable_capacity) * 100
        else:
            curtailed_capacity = 0
            curtailment_rate = 0

        print(f"  - Total Renewable Capacity: {total_renewable_capacity:.2f} GW", flush=True)
        print(f"  - Year {time_step} Grid Capacity: {self.grid_transmission_capacity:.2f} GW", flush=True)
        print(f"  - Estimated Curtailment Rate: {curtailment_rate:.2f}%", flush=True)

        # Record yearly metrics
        self.history.append({
            'year': time_step,
            'grid_capacity_gw': self.grid_transmission_capacity,
            'curtailment_rate': curtailment_rate
        })

        # Model simple grid expansion over time using config-driven rate
        self.grid_transmission_capacity *= (1 + self.expansion_rate)

    def finalize(self):
        """
        Finalizes the component's state.
        """
        print(f"Finalizing {self.name} component...", flush=True)
        print(f"Final Grid Transmission Capacity: {self.grid_transmission_capacity:.2f} GW", flush=True)

    def get_results(self):
        """Return DataFrame of yearly grid capacity and curtailment."""
        try:
            import pandas as pd
        except ImportError:
            raise RuntimeError("pandas required for get_results")
        return pd.DataFrame(self.history)
