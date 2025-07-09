from src.core.base_component import SimulationComponent
from src.config.loader import load_config

class BRIAnalysis(SimulationComponent):
    """
    Models the impact of the Belt and Road Initiative (BRI) on the domestic market.

    This component simulates how international projects can create demand for
    renewable energy technology, leading to innovation and cost reductions that
    benefit the domestic transition.
    """

    def __init__(self, name: str = "BRI Analysis"):
        super().__init__(name)

    def initialize(self):
        """
        Initializes the component's state.
        - Set up baseline BRI investment and green technology share.
        """
        print(f"Initializing {self.name} component...", flush=True)
        cfg = load_config()
        self.total_bri_investment = cfg['bri']['total_investment_b_usd']
        self.green_share = cfg['bri']['initial_green_share']
        self.innovation_boost_factor = cfg['bri']['innovation_boost_factor']
        self.history = []

        print(f"Initial BRI Investment: ${self.total_bri_investment}B", flush=True)
        print(f"Initial Green Share: {self.green_share*100}%", flush=True)

    def step(self, time_step: int):
        """
        Executes one simulation step for the given year.
        - Model the growth of green investment in BRI projects.
        - Calculate the resulting boost to domestic innovation.

        Args:
            time_step (int): The current simulation year.
        """
        print(f"Executing {self.name} step for year {time_step}...", flush=True)
        # Model a slight increase in the green share over time
        self.green_share = min(0.9, self.green_share * 1.02)

        green_investment = self.total_bri_investment * self.green_share

        # Calculate the innovation boost. This is a simplified representation.
        # The idea is that higher export volumes lead to economies of scale and innovation.
        domestic_innovation_boost = 1 + (green_investment * self.innovation_boost_factor)

        # Store the boost factor in the shared simulation state so other modules can use it.
        self.simulation_engine.state['bri_innovation_boost'] = domestic_innovation_boost

        print(f"  - Green BRI Investment: ${green_investment:.2f}B", flush=True)
        print(f"  - Domestic Innovation Boost Factor: {domestic_innovation_boost:.4f}", flush=True)

        # record metrics
        self.history.append({
            'year': time_step,
            'green_investment_b_usd': green_investment,
            'green_share': self.green_share,
            'innovation_boost': domestic_innovation_boost
        })

    def finalize(self):
        """
        Finalizes the component's state.
        """
        print(f"Finalizing {self.name} component...", flush=True)
        print(f"Final Green Share in BRI: {self.green_share*100:.2f}%", flush=True)

    def get_results(self):
        """Return DataFrame of BRI investment metrics."""
        try:
            import pandas as pd
        except ImportError:
            raise RuntimeError("pandas required for get_results")
        return pd.DataFrame(self.history)
