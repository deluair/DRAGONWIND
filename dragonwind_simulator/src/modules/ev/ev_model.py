"""Electric Vehicle (EV) adoption and grid impact model.

Projects EV stock growth, electricity demand, and managed-charging flexibility.
Provides yearly electricity load and potential flexible load to the Grid module.
"""
from __future__ import annotations

from src.core.base_component import SimulationComponent
from src.config.loader import load_config


class EVAdoption(SimulationComponent):
    """Simple EV fleet growth and load model."""

    def __init__(self, name: str = "EV Adoption"):
        super().__init__(name)

    # ------------------------------------------------------------------
    def initialize(self):
        print(f"Initializing {self.name} component...", flush=True)
        cfg = load_config()
        self.stock_million = cfg["ev"]["initial_stock_million"]
        self.growth_rate = cfg["ev"]["annual_growth_rate"]
        self.energy_per_km = cfg["ev"]["avg_consumption_kwh_per_km"]
        self.distance_km = cfg["ev"]["avg_distance_km"]
        self.managed_share = cfg["ev"]["managed_charging_share"]
        self.history: list[dict[str, float]] = []

    def step(self, time_step: int):
        # Grow EV stock
        self.stock_million *= 1 + self.growth_rate

        # Electricity demand (TWh)
        demand_kwh = (
            self.stock_million * 1_000_000 * self.distance_km * self.energy_per_km
        )
        demand_twh = demand_kwh / 1_000_000_000

        flexible_twh = demand_twh * self.managed_share

        self.history.append(
            {
                "year": time_step,
                "ev_stock_million": self.stock_million,
                "ev_demand_twh": demand_twh,
                "flexible_load_twh": flexible_twh,
            }
        )
        print(
            f"  - {time_step} EV stock {self.stock_million:.1f}M, demand {demand_twh:.1f} TWh",
            flush=True,
        )

    def finalize(self):
        print(f"Finalizing {self.name} component...", flush=True)

    def get_results(self):
        import pandas as pd
        return pd.DataFrame(self.history)
