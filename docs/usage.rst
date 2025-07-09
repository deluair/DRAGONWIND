=====
Usage
=====

This guide explains how to use the DRAGONWIND simulation platform.

Basic Concepts
-------------

The DRAGONWIND platform uses a modular design with several key components:

* **Simulation Engine**: Orchestrates the entire simulation process
* **Modules**: Specialized components handling specific aspects of the simulation (renewable energy, grid, finance, etc.)
* **Scenario Manager**: Creates and manages different simulation scenarios
* **Analytics**: Tools for analyzing and visualizing simulation results
* **Configuration**: YAML-based parameter management for all modules

Running a Basic Simulation
-------------------------

To run a basic simulation with default parameters:

.. code-block:: python

   from dragonwind_simulator.src.config.loader import load_config
   from dragonwind_simulator.src.core.simulation_engine import SimulationEngine

   # Load default configuration
   config = load_config()

   # Create simulation engine (2025-2050)
   engine = SimulationEngine(start_year=2025, end_year=2050)
   engine.configure(config)

   # Run simulation
   engine.run()

   # Get results
   results = engine.get_all_results()
   
   # Access specific module results
   renewable_results = results.get('renewable')
   grid_results = results.get('grid')

Creating and Running Scenarios
-----------------------------

Scenarios allow you to modify configuration parameters to explore different pathways:

.. code-block:: python

   from dragonwind_simulator.src.scenarios.scenario_manager import Scenario, ScenarioManager

   # Create a scenario
   accelerated_scenario = Scenario(
       name="accelerated_growth",
       description="Accelerated renewable deployment with 50% higher growth rates",
       overrides={
           "renewable": {
               "growth_rates": {
                   "solar": 100.0,  # GW/year
                   "wind": 80.0     # GW/year
               }
           },
           "grid": {
               "expansion_rate": 120.0  # Faster grid expansion (GW/year)
           }
       }
   )

   # Save scenario for future use
   manager = ScenarioManager()
   manager.save_scenario(accelerated_scenario)

   # Load and apply scenario to configuration
   scenario = manager.load_scenario("accelerated_growth")
   modified_config = scenario.apply_to_config(config)

   # Run with scenario configuration
   engine.configure(modified_config)
   engine.run()

Command-Line Interface
---------------------

You can run simulations directly from the command line:

.. code-block:: bash

   # Run with default configuration
   python -m dragonwind_simulator.run_simulation

   # Specify scenario and years
   python -m dragonwind_simulator.run_simulation --scenario=accelerated_growth --start=2025 --end=2050

   # Export results
   python -m dragonwind_simulator.run_simulation --export-format=excel,csv --output=results

Monte Carlo Simulation
---------------------

Run Monte Carlo simulations to explore parameter uncertainty:

.. code-block:: python

   from dragonwind_simulator.src.utils.monte_carlo import MonteCarloSimulation

   # Define parameter distributions
   parameter_distributions = {
       "renewable.growth_rates.solar": {
           "distribution": "normal",
           "mean": 70.0,
           "std_dev": 10.0
       },
       "renewable.growth_rates.wind": {
           "distribution": "normal",
           "mean": 60.0,
           "std_dev": 8.0
       },
       "grid.expansion_rate": {
           "distribution": "triangular",
           "min": 80.0,
           "mode": 100.0,
           "max": 120.0
       }
   }

   # Create and run Monte Carlo simulation
   mc_sim = MonteCarloSimulation(
       base_config=config,
       parameter_distributions=parameter_distributions,
       iterations=100,
       start_year=2025,
       end_year=2050
   )
   
   mc_results = mc_sim.run()
   
   # Analyze results
   summary_stats = mc_sim.get_summary_statistics()
   sensitivity = mc_sim.get_sensitivity_analysis()

Using Progress Tracking
----------------------

For long-running simulations, use the progress tracker:

.. code-block:: python

   from dragonwind_simulator.src.utils.progress import ProgressTracker

   # Create progress tracker for simulation with 25 years
   with ProgressTracker(total=25, description="Running simulation") as progress:
       engine.run(progress=progress)

Visualizing Results
------------------

Create professional visualizations of simulation results:

.. code-block:: python

   from dragonwind_simulator.src.analytics.plotter import create_figure

   # Create a line plot of renewable capacity over time
   fig = create_figure(
       data=results['renewable'],
       x_column='year',
       y_columns=['solar_capacity', 'wind_capacity', 'total_capacity'],
       title='Renewable Energy Capacity Expansion',
       x_label='Year',
       y_label='Capacity (GW)',
       figure_type='line'
   )
   
   # Save the figure
   fig.savefig('renewable_capacity.png', dpi=300)

Using the Web Dashboard
---------------------

The web dashboard provides a graphical interface for running simulations and viewing results:

1. Start the dashboard:

   .. code-block:: bash

      python -m dragonwind_simulator.web_dashboard

2. Open your web browser and navigate to http://127.0.0.1:8050/

3. Use the interface to:
   * Configure simulation parameters
   * Select and run scenarios
   * View interactive visualizations
   * Export results

For more details, see the :doc:`Web Dashboard Guide <web_dashboard>`.
