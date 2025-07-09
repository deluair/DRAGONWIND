"""
Progress tracking utilities for DRAGONWIND simulations.

This module provides progress bar functionality for visualizing
simulation progress during long-running operations.
"""

import sys
import time
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union, TypeVar, Type, Callable, Protocol, cast, overload, Literal
from types import TracebackType

import tqdm
from tqdm.auto import tqdm as auto_tqdm

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Type aliases for better readability
TqdmType = Any  # tqdm doesn't export proper types
Seconds = float
Steps = int
Percentage = float


class ProgressTracker:
    """
    Progress tracking for long-running simulations with ETA calculation.
    
    Provides both console progress bars and programmatic access to progress state.
    """
    
    def __init__(
        self,
        total: Steps,
        description: str = "Simulation progress",
        unit: str = "year",
        color: str = "green",
        disable: bool = False,
    ) -> None:
        """
        Initialize a progress tracker.
        
        Args:
            total: Total steps/items to process
            description: Progress bar description
            unit: Unit for the progress counter
            color: Color of the progress bar
            disable: Whether to disable visual progress display
        """
        self.total: Steps = total
        self.description: str = description
        self.unit: str = unit
        self.color: str = color
        self.disable: bool = disable
        self.start_time: Seconds = time.time()
        self.last_update_time: Seconds = self.start_time
        self._completed: Steps = 0
        self._progress_bars: Dict[str, TqdmType] = {}
        
        # Create main progress bar
        self._progress_bars["main"] = auto_tqdm(
            total=total,
            desc=description,
            unit=unit,
            colour=color,
            disable=disable,
            dynamic_ncols=True,
            file=sys.stdout
        )
    
    @property
    def completed(self) -> Steps:
        """Get the number of completed steps."""
        return self._completed
    
    @property
    def remaining(self) -> Steps:
        """Get the number of remaining steps."""
        return self.total - self._completed
    
    @property
    def progress(self) -> Percentage:
        """Get the progress as a percentage (0-100)."""
        if self.total == 0:
            return 100.0
        return (self._completed / self.total) * 100
    
    @property
    def elapsed(self) -> Seconds:
        """Get the elapsed time in seconds."""
        return time.time() - self.start_time
    
    @property
    def elapsed_str(self) -> str:
        """Get the elapsed time as a formatted string."""
        return str(timedelta(seconds=int(self.elapsed)))
    
    @property
    def eta(self) -> Optional[Seconds]:
        """
        Get the estimated time remaining in seconds.
        
        Returns None if no progress has been made yet.
        """
        if self._completed == 0:
            return None
            
        elapsed: Seconds = self.elapsed
        rate: float = self._completed / elapsed
        
        if rate == 0:
            return None
            
        return self.remaining / rate
    
    @property
    def eta_str(self) -> str:
        """Get the ETA as a formatted string, or 'Unknown' if not available."""
        eta_seconds = self.eta
        if eta_seconds is None:
            return "Unknown"
        return str(timedelta(seconds=int(eta_seconds)))
    
    def update(self, steps: Steps = 1, description: Optional[str] = None) -> None:
        """
        Update progress by the specified number of steps.
        
        Args:
            steps: Number of steps to increment by
            description: Optional new description for the progress bar
        """
        self._completed += steps
        
        # Update main progress bar
        main_bar = self._progress_bars["main"]
        main_bar.update(steps)
        
        # Update description if provided
        if description is not None:
            main_bar.set_description(description)
            
        self.last_update_time = time.time()
        
        # Update any sub-progress bars
        for name, bar in self._progress_bars.items():
            if name != "main" and hasattr(bar, "refresh"):
                bar.refresh()
    
    def add_subtask(
        self,
        name: str,
        total: Steps,
        description: Optional[str] = None,
        position: Optional[int] = None,
        leave: bool = True,
        unit: str = "it"
    ) -> None:
        """
        Add a sub-progress bar for a subtask.
        
        Args:
            name: Unique identifier for the subtask
            total: Total steps for the subtask
            description: Description for the subtask progress bar
            position: Position of the progress bar (None for auto)
            leave: Whether to leave the progress bar after completion
            unit: Unit for the subtask progress counter
        
        Raises:
            ValueError: If a subtask with the given name already exists
        """
        if name in self._progress_bars:
            raise ValueError(f"Subtask with name '{name}' already exists")
            
        if description is None:
            description = f"Subtask: {name}"
            
        # Create a nested progress bar
        self._progress_bars[name] = tqdm.tqdm(
            total=total,
            desc=description,
            position=position,
            leave=leave,
            colour=self.color,
            disable=self.disable,
            unit=unit
        )
    
    def update_subtask(self, name: str, steps: Steps = 1, description: Optional[str] = None) -> None:
        """
        Update a subtask progress bar.
        
        Args:
            name: Name of the subtask to update
            steps: Number of steps to increment by
            description: Optional new description for the subtask progress bar
        
        Raises:
            KeyError: If no subtask with the given name exists
        """
        if name in self._progress_bars:
            subtask_bar = self._progress_bars[name]
            subtask_bar.update(steps)
            
            # Update description if provided
            if description is not None and hasattr(subtask_bar, "set_description"):
                subtask_bar.set_description(description)
        else:
            raise KeyError(f"No subtask named '{name}' found")
    
    def close(self) -> None:
        """Close all progress bars properly."""
        # Close subtasks first
        for name, bar in list(self._progress_bars.items()):
            if name != "main":
                bar.close()
                self._progress_bars.pop(name, None)
        
        # Close main progress bar
        if "main" in self._progress_bars:
            self._progress_bars["main"].close()
            self._progress_bars.pop("main", None)
            
        # Log final statistics
        logger.debug(
            f"Progress tracking complete. Processed {self._completed}/{self.total} items "
            f"in {self.elapsed_str}."
        )
    
    def __enter__(self) -> 'ProgressTracker':
        """Support context manager protocol."""
        return self
    
    def __exit__(
        self, 
        exc_type: Optional[Type[BaseException]], 
        exc_val: Optional[BaseException], 
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Clean up resources when exiting context."""
        self.close()


def track_simulation(
    years: List[int],
    description: str = "Simulating years",
    disable: bool = False,
    color: str = "green"
) -> ProgressTracker:
    """
    Create a progress tracker for simulation years.
    
    Args:
        years: List of years to simulate
        description: Description for the progress bar
        disable: Whether to disable visual progress display
        color: Color for the progress bar
        
    Returns:
        ProgressTracker instance configured for the simulation
    """
    return ProgressTracker(
        total=len(years),
        description=description,
        unit="year",
        disable=disable,
        color=color
    )


def track_monte_carlo(
    iterations: int, 
    description: str = "Monte Carlo simulation",
    disable: bool = False
) -> ProgressTracker:
    """
    Create a progress tracker for Monte Carlo simulations.
    
    Args:
        iterations: Number of iterations to track
        description: Description for the progress bar
        disable: Whether to disable visual progress display
        
    Returns:
        ProgressTracker instance configured for Monte Carlo simulation
    """
    return ProgressTracker(
        total=iterations,
        description=description,
        unit="iter",
        disable=disable,
        color="blue"
    )
