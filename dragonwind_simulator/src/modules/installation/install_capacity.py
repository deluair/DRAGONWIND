"""Installation capacity and workforce constraints model.

Compares annual renewable build demand against on-the-ground installation
capacity (EPC contractors, workforce). If demand outstrips install capacity,
projects are delayed creating a backlog that feeds into following years.
"""
from __future__ import annotations

from src.core.base_component import SimulationComponent
from src.config.loader import load_config


class InstallCapacity(SimulationComponent):
    """Track field-installation capability for solar & wind."""

    def __init__(self, name: str = "Installation Capacity"):
        super().__init__(name)

    # ------------------------------------------------------------------
    def initialize(self):
        print(f"Initializing {self.name} component...", flush=True)
        cfg = load_config()
        self.install_capacity_gw = cfg["installation"]["initial_capacity_gw"]
        self.capacity_growth_rate = cfg["installation"]["annual_growth_rate"]
        self.backlog_gw = 0.0
        self.history: list[dict[str, float]] = []

        # link to renewable module
        self._renewable_mod = next(c for c in self.simulation_engine.components if c.name.startswith("Renewable Capacity"))

    def step(self, time_step: int):
        demand_solar, demand_wind = self._get_demand()
        total_demand = demand_solar + demand_wind + self.backlog_gw

        utilised = min(total_demand, self.install_capacity_gw)
        self.backlog_gw = max(0.0, total_demand - self.install_capacity_gw)

        print(
            f"  - Install demand {time_step}: {total_demand:.1f} GW, capacity {self.install_capacity_gw:.1f} GW, backlog {self.backlog_gw:.1f} GW",
            flush=True,
        )

        # grow capacity
        self.install_capacity_gw *= 1 + self.capacity_growth_rate

        self.history.append({
            "year": time_step,
            "install_capacity_gw": self.install_capacity_gw,
            "demand_gw": total_demand,
            "backlog_gw": self.backlog_gw,
        })

    def _get_demand(self):
        df = self._renewable_mod.get_results()
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        return latest["solar_gw"] - prev["solar_gw"], latest["wind_gw"] - prev["wind_gw"]

    def finalize(self):
        print(f"Finalizing {self.name} component...", flush=True)

    def get_results(self):
        import pandas as pd
        return pd.DataFrame(self.history)
