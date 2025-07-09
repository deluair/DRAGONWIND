"""
Entry point for launching the DRAGONWIND web dashboard.

This script provides a simple way to start the web-based user interface
for running and visualizing DRAGONWIND simulations.
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure the dragonwind_simulator package is in the path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import get_logger
from src.web.dashboard import start_dashboard

logger = get_logger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Start the DRAGONWIND web dashboard"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8050, 
        help="Port to run the dashboard on"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Run in debug mode"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    logger.info(f"Starting DRAGONWIND web dashboard on port {args.port}")
    logger.info(f"Dashboard URL: http://localhost:{args.port}")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Create assets directory if it doesn't exist
        assets_dir = Path(__file__).parent / "assets"
        os.makedirs(assets_dir, exist_ok=True)
        
        # Start the dashboard
        start_dashboard(port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Error running dashboard: {e}")
        sys.exit(1)
