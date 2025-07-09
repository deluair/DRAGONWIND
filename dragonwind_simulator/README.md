# DRAGONWIND  🇨🇳 Renewable-Energy Transition Simulator

DRAGONWIND is a modular Monte-Carlo style platform that models China’s journey to **Net-Zero by 2060** under the latest IEA “Net Zero Emissions” (May 2025) scenario.  It integrates technology, finance, grid, and policy levers to produce transparent KPIs, publication-ready figures, and interactive dashboards.


## Key Features

* **Config-driven architecture** – All assumptions live in `src/config/defaults.yaml`; change a value, rerun, get new results.
* **Expandable component set**
  * Renewable capacity expansion (solar + wind)
  * Grid integration & curtailment
  * Green-finance feedback loops
  * Provincial disaggregation (Xinjiang, Guangdong, Hebei sample)
  * Carbon pathways & CO₂ abatement accounting
  * Belt-&-Road spill-over analysis
  * NEW ➜ Manufacturing supply-chain capacity, installation workforce, utility-scale BESS roll-out, and EV adoption / managed charging.
* **Analytics pipeline** – Automatically collects component DataFrames, writes a timestamped `results/<ts>/kpis.parquet`, generates high-resolution PNGs and an interactive Plotly dashboard.
* **Professional outputs** – Prints are flush-controlled for clean logs; figures meet journal print standards (300 dpi); dashboards are ready for web embedding.


## Quick-Start


```bash
# 1. Create virtual environment and install deps (Python ≥3.10)
python -m venv .venv && source .venv/Scripts/activate  # Windows
pip install -r requirements.txt

# 2. Run a 2025-2035 simulation
python main.py

# 3. Explore outputs
open results/<timestamp>/dashboard.html      # interactive KPIs
open results/<timestamp>/capacity_growth.png # static figures
```


## Project Layout


```
├─ main.py                    # entry-point
├─ src/
│  ├─ core/                   # engine & base class
│  ├─ config/                 # YAML loader + defaults
│  ├─ modules/                # self-contained domain modules
│  │   ├─ renewable_energy/
│  │   ├─ grid_integration/
│  │   ├─ financial_modeling/
│  │   ├─ provincial_analysis/
│  │   ├─ carbon_pathways/
│  │   ├─ bri_analysis/
│  │   ├─ production_capacity/
│  │   ├─ installation/
│  │   ├─ bess/
│  │   └─ ev/
│  └─ analytics/              # KPI collector & plotting
└─ requirements.txt
```


## Reproducing Figures

After each simulation the analytics pipeline drops PNGs for: capacity growth, CO₂ avoided, manufacturing shortages, installation backlog, BESS power, and EV demand.  Customize additional plots in `src/analytics/plots.py`.


## Contributing

1. Fork and branch from `main`.
2. Follow the existing module template (`SimulationComponent` lifecycle).
3. Add **unit tests** under `tests/` and ensure `pytest` passes.


## License

MIT © 2025 University of Tennessee Energy Systems Lab & Contributors.

