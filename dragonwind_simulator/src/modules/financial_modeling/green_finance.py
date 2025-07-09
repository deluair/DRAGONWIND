from src.core.base_component import SimulationComponent
from src.config.loader import load_config

class FinancialModeling(SimulationComponent):
    """
    Models the financial and economic aspects of the renewable energy transition.

    This component simulates green finance mechanisms, investment flows, and their
    impact on the growth of renewable energy capacity.
    """

    def __init__(self, name: str = "Financial Modeling"):
        super().__init__(name)
        self.renewable_capacity_module = None

    def initialize(self):
        """
        Initializes the component's state.
        - Set up initial green finance levels and investment parameters.
        """
        print(f"Initializing {self.name} component...", flush=True)
        try:
            self.renewable_capacity_module = next(
                comp for comp in self.simulation_engine.components 
                if comp.name == "Renewable Capacity Expansion"
            )
        except StopIteration:
            raise RuntimeError("Renewable Capacity Expansion module not found.")

        cfg = load_config()
        self.green_bonds_issuance = cfg['finance']['bonds_initial']
        self.green_credit_allocation = cfg['finance']['credit_initial']
        self.investment_effectiveness = cfg['finance']['investment_effectiveness']
        # analytics history
        self.history = []


        print(f"Initial Green Bonds: {self.green_bonds_issuance}B RMB", flush=True)
        print(f"Initial Green Credit: {self.green_credit_allocation}B RMB", flush=True)

    def step(self, time_step: int):
        """
        Executes one simulation step for the given year.
        - Model the growth of green finance.
        - Calculate the impact on renewable capacity additions.

        Args:
            time_step (int): The current simulation year.
        """
        print(f"Executing {self.name} step for year {time_step}...", flush=True)
        # Model simple growth in green finance
        self.green_bonds_issuance *= 1.20
        self.green_credit_allocation *= 1.15

        total_green_investment = self.green_bonds_issuance + self.green_credit_allocation
        
        # Calculate the capacity addition driven by this investment
        investment_driven_capacity_gw = total_green_investment * self.investment_effectiveness

        # store yearly metrics
        self.history.append({
            'year': time_step,
            'bonds_b_rmb': self.green_bonds_issuance,
            'credit_b_rmb': self.green_credit_allocation,
            'total_green_investment_b_rmb': total_green_investment
        })

        # This is a simplification. A real model would distribute this capacity
        # between solar and wind based on costs, policies, etc.
        # For now, we'll just print it. In a more advanced version, this could
        # directly influence the growth rates in the RenewableCapacityExpansion module.
        print(f"  - Total Green Investment: {total_green_investment:.2f}B RMB", flush=True)
        print(f"  - Investment-Driven Capacity Addition Potential: {investment_driven_capacity_gw:.2f} GW", flush=True)

    def finalize(self):
        """
        Finalizes the component's state.
        """
        print(f"Finalizing {self.name} component...", flush=True)
        print(f"Final Green Bonds Issuance: {self.green_bonds_issuance:.2f}B RMB", flush=True)
        print(f"Final Green Credit Allocation: {self.green_credit_allocation:.2f}B RMB", flush=True)

    def get_results(self):
        """Return DataFrame of yearly green finance KPIs."""
        try:
            import pandas as pd
        except ImportError:
            raise RuntimeError("pandas required for get_results")
        return pd.DataFrame(self.history)
