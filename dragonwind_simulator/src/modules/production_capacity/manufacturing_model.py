"""Manufacturing and supply-chain capacity model.

Tracks annual domestic production capacity for solar PV modules and wind
components and flags shortages relative to deployment demand coming from the
RenewableCapacityExpansion module.
"""
from __future__ import annotations

from src.core.base_component import SimulationComponent
from src.config.loader import load_config


class ManufacturingCapacity(SimulationComponent):
    """Solar & wind manufacturing capacity tracker."""

    def __init__(self, name: str = "Manufacturing Capacity"):
        super().__init__(name)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def initialize(self):  # noqa: D401
        print(f"Initializing {self.name} component...", flush=True)
        cfg = load_config()
        self.history: list[dict[str, float]] = []

        self.production_capacity = {
            "solar_gw": cfg["manufacturing"]["initial_solar_capacity_gw"],
            "wind_gw": cfg["manufacturing"]["initial_wind_capacity_gw"],
        }
        self.capacity_growth_rate = cfg["manufacturing"]["annual_growth_rate"]

        # Reference to demand source
        self._renewable_mod = next(
            c for c in self.simulation_engine.components if c.name.startswith("Renewable Capacity")
        )

    def step(self, time_step: int):  # noqa: D401
        demand_solar, demand_wind = self._get_demand()

        shortage_solar = max(0.0, demand_solar - self.production_capacity["solar_gw"])
        shortage_wind = max(0.0, demand_wind - self.production_capacity["wind_gw"])

        print(
            f"  - Manufacturing demand {time_step}: Solar={demand_solar:.1f} GW, "
            f"Wind={demand_wind:.1f} GW; shortages: solar {shortage_solar:.1f} GW, "
            f"wind {shortage_wind:.1f} GW",
            flush=True,
        )

        # Expand manufacturing lines by growth rate
        self.production_capacity["solar_gw"] *= 1 + self.capacity_growth_rate
        self.production_capacity["wind_gw"] *= 1 + self.capacity_growth_rate

        # record
        self.history.append(
            {
                "year": time_step,
                "prod_solar_gw": self.production_capacity["solar_gw"],
                "prod_wind_gw": self.production_capacity["wind_gw"],
                "shortage_solar_gw": shortage_solar,
                "shortage_wind_gw": shortage_wind,
            }
        )

    def _get_demand(self):
        """Read incremental capacity additions from renewable module."""
        renewable_df = self._renewable_mod.get_results()
        latest = renewable_df.iloc[-1]
        prev = renewable_df.iloc[-2] if len(renewable_df) > 1 else latest
        demand_solar = latest["solar_gw"] - prev["solar_gw"]
        demand_wind = latest["wind_gw"] - prev["wind_gw"]
        return demand_solar, demand_wind

    def finalize(self):
        print(f"Finalizing {self.name} component...", flush=True)

    def get_results(self):
        import pandas as pd

        return pd.DataFrame(self.history)
