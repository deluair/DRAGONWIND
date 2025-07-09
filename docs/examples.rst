========
Examples
========

This page provides examples of how to use the DRAGONWIND simulation platform for various analyses.

Basic Simulation
---------------

The following example demonstrates how to run a basic simulation and analyze the results:

.. code-block:: python

   import pandas as pd
   import matplotlib.pyplot as plt
   from dragonwind_simulator.src.config.loader import load_config
   from dragonwind_simulator.src.core.simulation_engine import SimulationEngine

   # Load configuration
   config = load_config()

   # Create and configure simulation engine
   engine = SimulationEngine(start_year=2025, end_year=2050)
   engine.configure(config)

   # Run simulation
   engine.run()

   # Get results
   results = engine.get_all_results()

   # Plot renewable energy capacity
   renewable_df = results['renewable'].reset_index()
   plt.figure(figsize=(12, 6))
   plt.plot(renewable_df['year'], renewable_df['solar_capacity'], marker='o', label='Solar')
   plt.plot(renewable_df['year'], renewable_df['wind_capacity'], marker='s', label='Wind')
   plt.plot(renewable_df['year'], renewable_df['total_capacity'], marker='^', label='Total')
   plt.title('Renewable Energy Capacity Expansion (2025-2050)')
   plt.xlabel('Year')
   plt.ylabel('Capacity (GW)')
   plt.grid(True)
   plt.legend()
   plt.show()

For a complete working example, see the :download:`Basic Simulation Notebook <../dragonwind_simulator/notebooks/examples/basic_simulation.ipynb>`.

Scenario Comparison
------------------

This example shows how to create and compare different scenarios:

.. code-block:: python

   from dragonwind_simulator.src.scenarios.scenario_manager import Scenario, ScenarioManager

   # Load base configuration
   base_config = load_config()

   # Create scenario manager
   manager = ScenarioManager()

   # Define scenarios
   scenarios = {
       "baseline": None,  # Use base configuration
       "accelerated": Scenario(
           name="accelerated_growth",
           description="Accelerated renewable deployment",
           overrides={
               "renewable": {
                   "growth_rates": {
                       "solar": base_config["renewable"]["growth_rates"]["solar"] * 1.5,
                       "wind": base_config["renewable"]["growth_rates"]["wind"] * 1.5
                   }
               }
           }
       ),
       "conservative": Scenario(
           name="conservative_growth",
           description="Conservative renewable deployment",
           overrides={
               "renewable": {
                   "growth_rates": {
                       "solar": base_config["renewable"]["growth_rates"]["solar"] * 0.7,
                       "wind": base_config["renewable"]["growth_rates"]["wind"] * 0.7
                   }
               }
           }
       )
   }

   # Run simulations for each scenario
   results = {}
   for name, scenario in scenarios.items():
       config = base_config.copy()
       if scenario:
           config = scenario.apply_to_config(config)
       
       engine = SimulationEngine(start_year=2025, end_year=2050)
       engine.configure(config)
       engine.run()
       
       results[name] = engine.get_all_results()

   # Compare total renewable capacity by 2050
   for name, scenario_results in results.items():
       final_capacity = scenario_results['renewable'].iloc[-1]['total_capacity']
       print(f"{name}: {final_capacity:.1f} GW by 2050")

For a complete working example, see the scenario comparison notebooks:
:download:`Part 1 <../dragonwind_simulator/notebooks/examples/scenario_comparison_part1.ipynb>`,
:download:`Part 2 <../dragonwind_simulator/notebooks/examples/scenario_comparison_part2.ipynb>`,
:download:`Part 3 <../dragonwind_simulator/notebooks/examples/scenario_comparison_part3.ipynb>`.

Monte Carlo Simulation
--------------------

This example demonstrates how to run a Monte Carlo simulation to analyze parameter uncertainty:

.. code-block:: python

   from dragonwind_simulator.src.utils.monte_carlo import MonteCarloSimulation
   import matplotlib.pyplot as plt
   import seaborn as sns

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
       base_config=load_config(),
       parameter_distributions=parameter_distributions,
       iterations=100,
       start_year=2025,
       end_year=2050
   )
   
   mc_results = mc_sim.run()
   
   # Get summary statistics
   stats = mc_sim.get_summary_statistics()
   print("2050 Total Renewable Capacity:")
   print(f"Mean: {stats['renewable']['total_capacity_2050']['mean']:.1f} GW")
   print(f"Std Dev: {stats['renewable']['total_capacity_2050']['std']:.1f} GW")
   print(f"Min: {stats['renewable']['total_capacity_2050']['min']:.1f} GW")
   print(f"Max: {stats['renewable']['total_capacity_2050']['max']:.1f} GW")
   
   # Plot distribution of total capacity in 2050
   capacities = [run_results['renewable'].iloc[-1]['total_capacity'] for run_results in mc_results]
   plt.figure(figsize=(10, 6))
   sns.histplot(capacities, kde=True)
   plt.title('Distribution of Total Renewable Capacity by 2050')
   plt.xlabel('Capacity (GW)')
   plt.ylabel('Frequency')
   plt.grid(True)
   plt.show()

Configuration Customization
-------------------------

This example shows how to customize configuration parameters:

.. code-block:: python

   import yaml
   from pathlib import Path
   from dragonwind_simulator.src.config.loader import load_config, validate_config

   # Load default configuration
   config = load_config()

   # Modify configuration
   config['renewable']['growth_rates']['solar'] = 85.0
   config['renewable']['growth_rates']['wind'] = 70.0
   config['grid']['expansion_rate'] = 110.0
   config['finance']['green_bonds_share'] = 0.45

   # Validate modified configuration
   validate_config(config)

   # Save custom configuration
   output_path = Path('custom_config.yaml')
   with open(output_path, 'w') as f:
       yaml.dump(config, f, default_flow_style=False)

   # Load custom configuration
   custom_config = load_config(output_path)

   # Run simulation with custom configuration
   engine = SimulationEngine(start_year=2025, end_year=2050)
   engine.configure(custom_config)
   engine.run()

Web Dashboard Usage
-----------------

The DRAGONWIND platform includes a web dashboard for running simulations and visualizing results without writing code. To use the web dashboard:

1. Start the dashboard:

   .. code-block:: bash

      python -m dragonwind_simulator.web_dashboard

2. Open your web browser and navigate to http://127.0.0.1:8050/

3. Use the dashboard to:
   * Configure simulation parameters
   * Select scenarios
   * Run simulations
   * View interactive visualizations
   * Export results

For more details, see the :doc:`Web Dashboard Guide <web_dashboard>`.
