print("--- main.py script started ---")
import sys
import os

# Add the project's 'src' directory to the Python path for robust imports
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from core.simulation_engine import SimulationEngine
from modules.renewable_energy.capacity_expansion import RenewableCapacityExpansion
from modules.grid_integration.curtailment_analysis import GridIntegration
from modules.financial_modeling.green_finance import FinancialModeling
from modules.provincial_analysis.provincial_model import ProvincialAnalysis
from modules.carbon_pathways.emission_model import CarbonPathways
from modules.bri_analysis.bri_model import BRIAnalysis
from modules.production_capacity.manufacturing_model import ManufacturingCapacity
from modules.installation.install_capacity import InstallCapacity
from modules.bess.bess_model import BESSDeployment
from modules.ev.ev_model import EVAdoption

def main():
    """
    Main function to run the DRAGONWIND simulation.
    """
    # 1. Initialize the simulation engine
    # We'll run a 10-year simulation from 2025 to 2035
    engine = SimulationEngine(start_year=2025, end_year=2035)

    # 2. Create and add simulation components
    # For now, we'll only add the renewable capacity expansion module
    renewable_module = RenewableCapacityExpansion()
    engine.add_component(renewable_module)

    # Add other components here as they are developed
    grid_module = GridIntegration()
    engine.add_component(grid_module)
    financial_module = FinancialModeling()
    engine.add_component(financial_module)

    provincial_module = ProvincialAnalysis()
    engine.add_component(provincial_module)

    carbon_module = CarbonPathways()
    engine.add_component(carbon_module)

    bri_module = BRIAnalysis()
    engine.add_component(bri_module)

    # New capacity & technology modules
    manu_module = ManufacturingCapacity()
    engine.add_component(manu_module)

    install_module = InstallCapacity()
    engine.add_component(install_module)

    bess_module = BESSDeployment()
    engine.add_component(bess_module)

    ev_module = EVAdoption()
    engine.add_component(ev_module)

    # 3. Run the simulation
    engine.run()

if __name__ == "__main__":
    main()
