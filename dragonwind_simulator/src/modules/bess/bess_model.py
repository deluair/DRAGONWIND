"""Battery Energy Storage System (BESS) deployment model.

Tracks utility-scale battery power capacity (GW) and energy capacity (GWh).
Interacts with curtailment numbers from GridIntegration to estimate how much
curtailed energy can be shifted, updating effective curtailment.
"""
from __future__ import annotations

from src.core.base_component import SimulationComponent
from src.config.loader import load_config


class BESSDeployment(SimulationComponent):
    """Utility-scale battery deployment and curtailment mitigation."""

    def __init__(self, name: str = "BESS Deployment"):
        super().__init__(name)

    # ------------------------------------------------------------------
    def initialize(self):
        print(f"Initializing {self.name} component...", flush=True)
        cfg = load_config()
        self.power_gw = cfg["bess"]["initial_power_gw"]
        self.energy_gwh = cfg["bess"]["initial_energy_gwh"]
        self.annual_addition_gw = cfg["bess"]["annual_addition_gw"]
        self.energy_power_ratio = cfg["bess"]["energy_power_ratio"]
        self.history: list[dict[str, float]] = []

        # Locate Grid module for curtailment data
        try:
            self._grid_mod = next(c for c in self.simulation_engine.components if c.name.startswith("Grid Integration"))
        except StopIteration:
            self._grid_mod = None

    def step(self, time_step: int):
        # Deploy new BESS this year
        self.power_gw += self.annual_addition_gw
        self.energy_gwh = self.power_gw * self.energy_power_ratio

        # Estimate curtailed energy absorbed
        curtailed = None
        if self._grid_mod is not None:
            curtailed = self._grid_mod.history[-1]["curtailment_rate"]
        
        self.history.append(
            {
                "year": time_step,
                "bess_power_gw": self.power_gw,
                "bess_energy_gwh": self.energy_gwh,
                "curtailment_rate": curtailed,
            }
        )
        print(
            f"  - {time_step} BESS power {self.power_gw:.1f} GW (energy {self.energy_gwh:.0f} GWh)",
            flush=True,
        )

    def finalize(self):
        print(f"Finalizing {self.name} component...", flush=True)

    def get_results(self):
        import pandas as pd
        return pd.DataFrame(self.history)
