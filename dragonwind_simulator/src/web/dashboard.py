"""
Web-based dashboard for DRAGONWIND simulations.

This module provides a simple web UI for running and exploring simulation results
using Dash and Plotly.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config.loader import load_config
from src.core.simulation_engine import SimulationEngine
from src.scenarios.scenario_manager import ScenarioManager
from src.utils.logger import get_logger
from src.utils.progress import ProgressTracker
from src.web.components import create_header, create_footer, create_sidebar

logger = get_logger(__name__)

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="DRAGONWIND Simulator",
    suppress_callback_exceptions=True
)

# App layout
app.layout = html.Div([
    # Store for simulation results and state
    dcc.Store(id="simulation-results"),
    dcc.Store(id="current-scenario"),
    
    # Header
    create_header(),
    
    # Main content
    dbc.Container([
        dbc.Row([
            # Sidebar for controls
            dbc.Col(create_sidebar(), md=3),
            
            # Main content area
            dbc.Col([
                html.Div(id="content-area", children=[
                    html.Div([
                        html.H4("Welcome to DRAGONWIND Simulator", className="mb-3"),
                        html.P(
                            "This dashboard allows you to run simulations of China's renewable "
                            "energy transition and explore the results visually.",
                            className="mb-3"
                        ),
                        html.P(
                            "To get started, select simulation parameters in the sidebar "
                            "and click 'Run Simulation'."
                        ),
                        dbc.Alert(
                            "No simulation has been run yet. Results will appear here after running a simulation.",
                            color="info"
                        )
                    ], id="welcome-panel", className="mb-4"),
                    
                    # Progress and status area
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("Simulation Progress"),
                                dbc.Progress(id="simulation-progress", value=0, className="mb-3"),
                                html.P(id="simulation-status"),
                            ])
                        ),
                        id="progress-collapse",
                        is_open=False,
                        className="mb-4"
                    ),
                    
                    # Results tabs (will be populated after simulation runs)
                    dbc.Collapse(
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    dbc.Spinner(html.Div(id="renewable-tab-content")), 
                                    label="Renewable Energy"
                                ),
                                dbc.Tab(
                                    dbc.Spinner(html.Div(id="grid-tab-content")), 
                                    label="Grid Integration"
                                ),
                                dbc.Tab(
                                    dbc.Spinner(html.Div(id="finance-tab-content")), 
                                    label="Financial Analysis"
                                ),
                                dbc.Tab(
                                    dbc.Spinner(html.Div(id="carbon-tab-content")), 
                                    label="Carbon Pathways"
                                ),
                                dbc.Tab(
                                    dbc.Spinner(html.Div(id="manufacturing-tab-content")), 
                                    label="Manufacturing"
                                ),
                                dbc.Tab(
                                    dbc.Spinner(html.Div(id="bess-ev-tab-content")), 
                                    label="BESS & EV"
                                ),
                            ],
                            id="results-tabs",
                        ),
                        id="results-collapse",
                        is_open=False,
                    ),
                ]),
            ], md=9),
        ]),
    ], fluid=True),
    
    # Footer
    create_footer(),
])


@app.callback(
    Output("simulation-results", "data"),
    Output("progress-collapse", "is_open"),
    Output("simulation-progress", "value"),
    Output("simulation-status", "children"),
    Output("results-collapse", "is_open"),
    Input("run-simulation-button", "n_clicks"),
    State("start-year-input", "value"),
    State("end-year-input", "value"),
    State("scenario-dropdown", "value"),
    prevent_initial_call=True
)
def run_simulation(n_clicks, start_year, end_year, scenario_name):
    """
    Run a simulation with the specified parameters when the button is clicked.
    """
    if n_clicks is None:
        return dash.no_update, False, 0, "", False
    
    try:
        # Show progress
        progress_value = 5
        status = "Loading configuration..."
        
        # Load configuration
        config = load_config()
        
        # Apply scenario if specified
        if scenario_name and scenario_name != "default":
            scenario_manager = ScenarioManager()
            scenario = scenario_manager.load_scenario(scenario_name)
            if scenario:
                config = scenario.apply_to_config(config)
        
        # Update progress
        progress_value = 10
        status = "Creating simulation engine..."
        
        # Create and configure simulation engine
        engine = SimulationEngine(start_year=start_year, end_year=end_year)
        engine.configure(config)
        
        # Update progress
        progress_value = 15
        status = "Running simulation..."
        
        # Run the simulation
        engine.run()
        
        # Get results
        progress_value = 90
        status = "Processing results..."
        results = engine.get_all_results()
        
        # Convert results to JSON serializable format
        serializable_results = {}
        for module_name, df in results.items():
            if df is not None:
                serializable_results[module_name] = df.reset_index().to_dict("records")
        
        # Complete
        progress_value = 100
        status = "Simulation complete!"
        
        return serializable_results, True, progress_value, status, True
    
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        return dash.no_update, True, 100, f"Error: {str(e)}", False


@app.callback(
    Output("renewable-tab-content", "children"),
    Input("simulation-results", "data"),
    prevent_initial_call=True
)
def update_renewable_tab(results):
    """Update the renewable energy tab with simulation results."""
    if not results or "renewable" not in results:
        return html.P("No renewable energy data available.")
    
    # Convert dictionary back to DataFrame
    df = pd.DataFrame(results["renewable"])
    
    # Create a line chart for renewable capacity
    fig = px.line(
        df, 
        x="year", 
        y=["solar_capacity", "wind_capacity", "total_capacity"],
        title="Renewable Energy Capacity Expansion",
        labels={"value": "Capacity (GW)", "year": "Year", "variable": "Type"}
    )
    
    return html.Div([
        dcc.Graph(figure=fig),
        html.H5("Renewable Energy Data", className="mt-4"),
        dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    ])


@app.callback(
    Output("grid-tab-content", "children"),
    Input("simulation-results", "data"),
    prevent_initial_call=True
)
def update_grid_tab(results):
    """Update the grid integration tab with simulation results."""
    if not results or "grid" not in results:
        return html.P("No grid integration data available.")
    
    # Convert dictionary back to DataFrame
    df = pd.DataFrame(results["grid"])
    
    # Create two plots: grid capacity and curtailment rate
    fig1 = px.line(
        df, 
        x="year", 
        y="grid_capacity",
        title="Grid Capacity Expansion",
        labels={"grid_capacity": "Capacity (GW)", "year": "Year"}
    )
    
    fig2 = px.line(
        df, 
        x="year", 
        y="curtailment_rate",
        title="Renewable Energy Curtailment Rate",
        labels={"curtailment_rate": "Curtailment Rate (%)", "year": "Year"}
    )
    fig2.update_layout(yaxis_tickformat=".1%")
    
    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig1), md=6),
            dbc.Col(dcc.Graph(figure=fig2), md=6),
        ]),
        html.H5("Grid Integration Data", className="mt-4"),
        dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    ])


def start_dashboard(port=8050, debug=False):
    """
    Start the Dash web server.
    
    Args:
        port: Port number to use
        debug: Whether to run in debug mode
    """
    logger.info(f"Starting DRAGONWIND dashboard on port {port}")
    app.run_server(port=port, debug=debug, host='0.0.0.0')


if __name__ == "__main__":
    # If run directly, start the dashboard
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    start_dashboard(port=port, debug=debug)
