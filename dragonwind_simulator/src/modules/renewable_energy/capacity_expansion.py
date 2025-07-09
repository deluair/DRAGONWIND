from src.core.base_component import SimulationComponent
from src.config.loader import load_config

class RenewableCapacityExpansion(SimulationComponent):
    """
    Models the expansion of renewable energy capacity (solar, wind, etc.).

    This component simulates the growth of renewable energy sources based on
    policy targets, economic factors, and technological advancements.
    """

    def __init__(self, name: str = "Renewable Capacity Expansion"):
        super().__init__(name)

    def initialize(self):
        """
        Initializes the component's state.
        - Load historical capacity data.
        - Set up initial capacity for the simulation start year.
        """
        print(f"Initializing {self.name} component...", flush=True)
        # Load parameters from YAML config
        cfg = load_config()
        # Data history for analytics
        self.history = []

        self.capacity = dict(cfg['renewable_capacity']['initial'])
        # Base annual growth rates
        self.growth_rates = dict(cfg['renewable_capacity']['growth_rates'])
        print(f"Initial capacity: {self.capacity}", flush=True)

    def step(self, time_step: int):
        """
        Executes one simulation step for the given year.
        - Calculate new capacity additions based on a growth model.
        - Update total capacity.

        Args:
            time_step (int): The current simulation year.
        """
        print(f"Executing {self.name} step for year {time_step}...", flush=True)
        # Get the innovation boost from the shared state (defaults to 1.0 if not present)
        innovation_boost = self.simulation_engine.state.get('bri_innovation_boost', 1.0)

        # Calculate new capacity additions for this year, including the boost
        new_solar_capacity = self.capacity['solar'] * self.growth_rates['solar'] * innovation_boost
        new_wind_capacity = self.capacity['wind'] * self.growth_rates['wind'] * innovation_boost

        self.capacity['solar'] += new_solar_capacity
        self.capacity['wind'] += new_wind_capacity

        # Store yearly snapshot for analytics
        self.history.append({
            'year': time_step,
            'solar_gw': self.capacity['solar'],
            'wind_gw': self.capacity['wind']
        })

        print(f"  - New Solar Capacity: {new_solar_capacity:.2f} GW", flush=True)
        print(f"  - New Wind Capacity: {new_wind_capacity:.2f} GW", flush=True)
        print(f"  - Total Capacity in {time_step}: Solar={self.capacity['solar']:.2f} GW, Wind={self.capacity['wind']:.2f} GW", flush=True)

    def get_total_capacity(self) -> float:
        """
        Returns the total installed renewable capacity (Solar + Wind) in GW.

        Returns:
            float: The total capacity in GW.
        """
        return self.capacity['solar'] + self.capacity['wind']

    def finalize(self):
        """
        Finalizes the component's state.
        - Save final capacity results.
        """
        print(f"Finalizing {self.name} component...", flush=True)
        print(f"Final Solar Capacity: {self.capacity['solar']:.2f} GW", flush=True)
        print(f"Final Wind Capacity: {self.capacity['wind']:.2f} GW", flush=True)

    # ------------------------------------------------------------------
    # Analytics helper
    # ------------------------------------------------------------------
    def get_results(self):
        """Return a pandas DataFrame of yearly solar and wind capacity."""
        try:
            import pandas as pd
        except ImportError:  # pragma: no cover
            raise RuntimeError("pandas required for get_results but not installed")
        return pd.DataFrame(self.history)
        # Here you would save the results to a file or database.
