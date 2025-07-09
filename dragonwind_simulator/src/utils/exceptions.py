"""
Custom exceptions for DRAGONWIND simulation platform.

This module provides a hierarchy of custom exceptions for handling
different types of errors in the simulation process.
"""


class DragonwindError(Exception):
    """Base class for all DRAGONWIND-specific exceptions."""
    pass


class ConfigurationError(DragonwindError):
    """Raised when there's an issue with configuration files or parameters."""
    pass


class DataLoadError(DragonwindError):
    """Raised when data cannot be loaded or is invalid."""
    pass


class SimulationError(DragonwindError):
    """Base class for simulation-specific errors."""
    pass


class ComponentInitializationError(SimulationError):
    """Raised when a simulation component fails to initialize."""
    pass


class ComponentExecutionError(SimulationError):
    """Raised when a simulation component fails during execution."""
    pass


class ValidationError(DragonwindError):
    """Raised when validation of inputs or model outputs fails."""
    pass


class ExportError(DragonwindError):
    """Raised when exporting results fails."""
    pass


class ScenarioError(DragonwindError):
    """Raised when there are issues with scenario definition or loading."""
    pass


class AnalyticsError(DragonwindError):
    """Raised when analytics or visualization processing fails."""
    pass
