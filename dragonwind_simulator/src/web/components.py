"""
UI components for the DRAGONWIND web dashboard.

This module provides reusable dashboard components like header, footer, and sidebar.
"""

from datetime import datetime
from typing import List, Dict, Optional

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.scenarios.scenario_manager import ScenarioManager


def create_header() -> html.Div:
    """
    Create the dashboard header component.
    
    Returns:
        Dash HTML component for the header
    """
    return html.Div([
        dbc.Navbar(
            dbc.Container([
                html.A(
                    dbc.Row([
                        dbc.Col(html.Img(src="/assets/logo.png", height="30px"), width="auto"),
                        dbc.Col(dbc.NavbarBrand("DRAGONWIND Simulator", className="ml-2"), width="auto"),
                    ],
                    align="center",
                    className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Documentation", href="https://github.com/deluair/DRAGONWIND")),
                        dbc.NavItem(dbc.NavLink("About", href="#")),
                    ],
                    className="ml-auto",
                    navbar=True
                    ),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ],
            fluid=True
            ),
            color="dark",
            dark=True,
            className="mb-4",
        ),
    ])


def create_footer() -> html.Div:
    """
    Create the dashboard footer component.
    
    Returns:
        Dash HTML component for the footer
    """
    current_year = datetime.now().year
    
    return html.Footer(
        dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.P(f"© {current_year} DRAGONWIND Simulator", className="text-muted"),
                    html.P("Built for renewable energy transition simulation", className="text-muted small"),
                ]),
                dbc.Col([
                    html.P([
                        "Made with ",
                        html.A("Dash", href="https://plotly.com/dash/", target="_blank"),
                        " and ",
                        html.A("Plotly", href="https://plotly.com/", target="_blank")
                    ], className="text-muted text-right")
                ], className="text-right")
            ])
        ]),
        className="mt-5 pt-3"
    )


def _get_available_scenarios() -> List[Dict[str, str]]:
    """
    Get list of available scenarios for the dropdown.
    
    Returns:
        List of scenario options
    """
    try:
        scenario_manager = ScenarioManager()
        scenarios = scenario_manager.list_scenarios()
        
        # Format for dropdown
        options = [{"label": "Default", "value": "default"}]
        for scenario_name in scenarios:
            options.append({"label": scenario_name, "value": scenario_name})
            
        return options
    except Exception:
        # If error loading scenarios, just return default
        return [{"label": "Default", "value": "default"}]


def create_sidebar() -> html.Div:
    """
    Create the dashboard sidebar with controls.
    
    Returns:
        Dash HTML component for the sidebar
    """
    return html.Div([
        html.H4("Simulation Controls", className="mb-3"),
        
        # Time range
        html.Label("Simulation Period:"),
        dbc.Row([
            dbc.Col([
                html.Label("Start Year"),
                dbc.Input(
                    id="start-year-input",
                    type="number",
                    value=2025,
                    min=2020,
                    max=2050,
                    step=1
                ),
            ], width=6),
            dbc.Col([
                html.Label("End Year"),
                dbc.Input(
                    id="end-year-input",
                    type="number",
                    value=2050,
                    min=2025,
                    max=2100,
                    step=1
                ),
            ], width=6),
        ], className="mb-3"),
        
        # Scenario selection
        html.Label("Scenario:"),
        dcc.Dropdown(
            id="scenario-dropdown",
            options=_get_available_scenarios(),
            value="default",
            className="mb-3"
        ),
        
        # Run simulation button
        dbc.Button(
            "Run Simulation",
            id="run-simulation-button",
            color="primary",
            className="w-100 mb-3"
        ),
        
        # Export results
        html.Hr(),
        html.H5("Export Options"),
        dbc.Row([
            dbc.Col([
                dbc.Select(
                    id="export-format-select",
                    options=[
                        {"label": "CSV", "value": "csv"},
                        {"label": "Excel", "value": "excel"},
                        {"label": "JSON", "value": "json"},
                    ],
                    value="excel",
                ),
            ], width=8),
            dbc.Col([
                dbc.Button(
                    "Export",
                    id="export-button",
                    color="secondary",
                    className="w-100",
                    disabled=True
                ),
            ], width=4),
        ], className="mb-3"),
        
        # Download component (hidden)
        dcc.Download(id="download-data"),
        
        # Help and info
        html.Hr(),
        html.Div([
            html.H5("Help"),
            html.P([
                "For detailed documentation, visit the ",
                html.A("GitHub repository", href="https://github.com/deluair/DRAGONWIND", target="_blank"),
            ]),
            html.P([
                "Need help? Check out the ",
                html.A("User Guide", href="#", target="_blank"),
            ]),
        ], className="mt-3"),
    ], className="bg-light p-3 border rounded")
