"""Plotting utilities for DRAGONWIND KPI parquet files."""
from __future__ import annotations

from pathlib import Path

import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import plotly.express as px  # type: ignore

sns.set_theme(style="whitegrid")


def generate_static_figures(parquet_path: str | Path, out_dir: str | Path) -> None:
    """Generate high-resolution PNG figures from KPI parquet file."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(parquet_path)

    # Example 1: Solar & Wind capacity growth
    cap = df[df["component"] == "Renewable Capacity Expansion"]
    if not cap.empty:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=cap, x="year", y="solar_gw", label="Solar")
        sns.lineplot(data=cap, x="year", y="wind_gw", label="Wind")
        plt.title("Solar & Wind Capacity Growth (GW)")
        plt.ylabel("GW")
        plt.savefig(out_path / "capacity_growth.png", dpi=300, bbox_inches="tight")
        plt.close()

    # Example 2: Cumulative CO2 avoided
    carbon = df[df["component"] == "Carbon Pathways"]
    if not carbon.empty:
        plt.figure(figsize=(10, 6))
        sns.lineplot(
            data=carbon,
            x="year",
            y=carbon["emissions_avoided_tons"] / 1e9,
            label="Cumulative CO₂ Avoided (Billion t)",
        )
        plt.ylabel("Billion tonnes CO₂")
        plt.title("Cumulative CO₂ Emissions Avoided")
        plt.savefig(out_path / "co2_avoided.png", dpi=300, bbox_inches="tight")
        plt.close()

    # Example 3: Manufacturing shortages
    manu = df[df["component"] == "Manufacturing Capacity"]
    if not manu.empty:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=manu, x="year", y="shortage_solar_gw", label="Solar Shortage")
        sns.lineplot(data=manu, x="year", y="shortage_wind_gw", label="Wind Shortage")
        plt.title("Manufacturing Shortages (GW)")
        plt.ylabel("GW")
        plt.savefig(out_path / "manufacturing_shortages.png", dpi=300, bbox_inches="tight")
        plt.close()

    # Example 4: Installation backlog
    install = df[df["component"] == "Installation Capacity"]
    if not install.empty:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=install, x="year", y="backlog_gw", label="Backlog")
        plt.title("Installation Backlog (GW)")
        plt.ylabel("GW")
        plt.savefig(out_path / "install_backlog.png", dpi=300, bbox_inches="tight")
        plt.close()

    # Example 5: BESS deployment
    bess = df[df["component"] == "BESS Deployment"]
    if not bess.empty:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=bess, x="year", y="bess_power_gw", label="BESS Power (GW)")
        plt.title("Utility-Scale Battery Power Capacity")
        plt.ylabel("GW")
        plt.savefig(out_path / "bess_power.png", dpi=300, bbox_inches="tight")
        plt.close()

    # Example 6: EV electricity demand
    ev = df[df["component"] == "EV Adoption"]
    if not ev.empty:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=ev, x="year", y="ev_demand_twh", label="EV Demand (TWh)")
        plt.title("EV Electricity Demand")
        plt.ylabel("TWh")
        plt.savefig(out_path / "ev_demand.png", dpi=300, bbox_inches="tight")
        plt.close()


def generate_interactive_dashboard(parquet_path: str | Path, out_dir: str | Path) -> None:
    """Create an interactive Plotly HTML dashboard with key KPIs."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(parquet_path)

    # Build a multi-tab HTML dashboard using Plotly Express facets
    fig = px.line(
        df[df["component"] == "Renewable Capacity Expansion"],
        x="year",
        y=["solar_gw", "wind_gw"],
        title="Solar & Wind Capacity Growth (GW)",
    )
    html_path = out_path / "dashboard.html"
    fig.write_html(html_path)
