"""KPI collection utilities for DRAGONWIND.

This helper traverses all registered simulation components, calls their
`get_results()` method (if implemented) and concatenates the resulting
pandas DataFrames into a single Parquet file. A timestamped output folder
is created under `results/`.
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd  # type: ignore

from src.core.base_component import SimulationComponent


class ResultsCollector:
    """Collect KPI DataFrames and persist to disk."""

    def __init__(self, components: List[SimulationComponent]):
        self.components = components

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def collect(self) -> pd.DataFrame:
        """Concatenate DataFrames from all components.

        Components without `get_results` are silently skipped.
        """
        frames: list[pd.DataFrame] = []
        for comp in self.components:
            if hasattr(comp, "get_results"):
                try:
                    df = comp.get_results()
                    if not df.empty:
                        df["component"] = comp.name  # tag for easy filtering
                        frames.append(df)
                except Exception as exc:  # pragma: no cover
                    print(
                        f"[collector] Warning: failed to get results from {comp.name}: {exc}",
                        flush=True,
                    )
        if frames:
            combined = pd.concat(frames, ignore_index=True)
        else:
            combined = pd.DataFrame()
        return combined

    def persist(self, df: pd.DataFrame, root: str | os.PathLike = "results") -> Path:
        """Write DataFrame to a timestamped Parquet file and return its path."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(root) / ts
        out_dir.mkdir(parents=True, exist_ok=True)
        parquet_path = out_dir / "kpis.parquet"
        df.to_parquet(parquet_path, index=False)
        return parquet_path

    def run(self) -> Path | None:
        """High-level shortcut to collect and persist, returning the Parquet path."""
        df = self.collect()
        if df.empty:
            print("[collector] No KPI data collected.", flush=True)
            return None
        return self.persist(df)
