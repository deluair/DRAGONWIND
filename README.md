# DragonWind: Renewable Energy Simulation Project

DragonWind is a comprehensive simulation platform for modeling, analyzing, and visualizing renewable energy systems, with a focus on China's net-zero transition. The project supports scenario analysis, grid integration, financial modeling, and more.

## Features
- Modular simulation engine
- Scenario management and comparison
- Grid integration and curtailment analysis
- Battery energy storage (BESS) and EV modeling
- Financial and green finance modules
- Provincial and national analysis
- Data pipeline for raw, processed, and external data
- Web dashboard for results visualization

## Project Structure
- `dragonwind_simulator/` - Main simulation engine and modules
- `docs/` - Documentation and API references
- `results/` - Simulation outputs and figures
- `china_renewable_netzero_project.md` - Project background and notes

## Getting Started

### Prerequisites
- Python 3.8+
- Recommended: Create a virtual environment

### Installation
```bash
cd dragonwind_simulator
pip install -r requirements.txt
```

### Running a Simulation
```bash
python main.py
```

Or use the provided Jupyter notebooks in `dragonwind_simulator/notebooks/examples/` for guided scenario analysis.

### Web Dashboard
To launch the dashboard (if available):
```bash
python web_dashboard.py
```

## Documentation
See the `docs/` folder or build the documentation with Sphinx:
```bash
cd docs
sphinx-build -b html . _build/html
```

## Contributing
Pull requests and issues are welcome! Please see the `docs/` and code comments for guidance on extending modules or adding new features.

## License
[MIT License](LICENSE) 