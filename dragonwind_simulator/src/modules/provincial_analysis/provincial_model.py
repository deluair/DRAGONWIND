from src.core.base_component import SimulationComponent
import random

class ProvincialAnalysis(SimulationComponent):
    """
    Models the provincial and regional heterogeneity in the energy transition.

    This component manages data and dynamics for different provinces, including
    resource endowments, economic levels, and policy variations.
    """

    def __init__(self, name: str = "Provincial Analysis"):
        super().__init__(name)
        self.provinces = {}
        self.history = []

    def initialize(self):
        """
        Initializes the component's state.
        - Load or create synthetic data for a set of provinces.
        """
        print(f"Initializing {self.name} component...", flush=True)
        # In a real scenario, this data would be loaded from a file (e.g., using CSVLoader)
        # For now, we create synthetic data for a few key provinces.
        self.provinces = {
            'Xinjiang': {
                'gdp': 1600,  # billion USD
                'solar_potential': 0.9,  # Scale 0-1
                'wind_potential': 0.8,
                'policy_incentive': 1.2, # Multiplier for growth
                'renewable_capacity': {'solar': 50, 'wind': 40} # GW
            },
            'Guangdong': {
                'gdp': 1900,
                'solar_potential': 0.5,
                'wind_potential': 0.7, # Offshore wind
                'policy_incentive': 1.1,
                'renewable_capacity': {'solar': 30, 'wind': 25}
            },
            'Hebei': {
                'gdp': 600,
                'solar_potential': 0.7,
                'wind_potential': 0.6,
                'policy_incentive': 1.0,
                'renewable_capacity': {'solar': 25, 'wind': 20}
            }
        }
        print(f"Loaded data for {len(self.provinces)} provinces.", flush=True)

    def step(self, time_step: int):
        """
        Executes one simulation step for the given year.
        - Model the growth of renewable capacity in each province.

        Args:
            time_step (int): The current simulation year.
        """
        print(f"Executing {self.name} step for year {time_step}...", flush=True)
        for name, data in self.provinces.items():
            # Simplified growth model based on potential and policy
            solar_growth = data['solar_potential'] * data['policy_incentive'] * random.uniform(0.05, 0.15)
            wind_growth = data['wind_potential'] * data['policy_incentive'] * random.uniform(0.05, 0.12)

            data['renewable_capacity']['solar'] *= (1 + solar_growth)
            data['renewable_capacity']['wind'] *= (1 + wind_growth)

            # yearly province-level snapshot (aggregate)
            self.history.append({
                'year': time_step,
                'province': name,
                'solar_gw': data['renewable_capacity']['solar'],
                'wind_gw': data['renewable_capacity']['wind']
            })

            print(f"  - {name}: Solar -> {data['renewable_capacity']['solar']:.2f} GW, Wind -> {data['renewable_capacity']['wind']:.2f} GW", flush=True)

    def finalize(self):
        """
        Finalizes the component's state.
        - Save final provincial data.
        """
        print(f"Finalizing {self.name} component...", flush=True)
        # In a real scenario, you would save this detailed provincial data.
        # For now, we just print a summary.
        total_capacity = sum(p['renewable_capacity']['solar'] + p['renewable_capacity']['wind'] for p in self.provinces.values())
        print(f"Final total capacity across all modeled provinces: {total_capacity:.2f} GW", flush=True)

    def get_results(self):
        """Return DataFrame with per-province yearly capacity."""
        try:
            import pandas as pd
        except ImportError:
            raise RuntimeError("pandas required for get_results")
        return pd.DataFrame(self.history)
