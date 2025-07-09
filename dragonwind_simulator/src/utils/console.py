"""
Console formatting utilities for DRAGONWIND.

This module provides color-coded and styled console output functions to enhance
the user experience with visual cues and better organization of console output.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

# ANSI color and style codes
class TextStyle:
    RESET = '\033[0m'
    
    # Text styles
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Common combinations
    ERROR = BRIGHT_RED
    WARNING = BRIGHT_YELLOW
    SUCCESS = BRIGHT_GREEN
    INFO = BRIGHT_BLUE
    DEBUG = BRIGHT_CYAN
    HEADER = BOLD + BRIGHT_CYAN


def colorize(text: str, style: str) -> str:
    """
    Apply a color or style to text.
    
    Args:
        text: The text to colorize
        style: Style attribute from TextStyle class
        
    Returns:
        The styled text string
    """
    style_attr = getattr(TextStyle, style.upper(), '')
    if style_attr:
        return f"{style_attr}{text}{TextStyle.RESET}"
    return text


def format_error(message: str) -> str:
    """Format a message as an error with red color."""
    return f"{TextStyle.ERROR}✗ ERROR: {message}{TextStyle.RESET}"


def format_warning(message: str) -> str:
    """Format a message as a warning with yellow color."""
    return f"{TextStyle.WARNING}⚠ WARNING: {message}{TextStyle.RESET}"


def format_success(message: str) -> str:
    """Format a message as a success with green color and checkmark."""
    return f"{TextStyle.SUCCESS}✓ {message}{TextStyle.RESET}"


def format_info(message: str) -> str:
    """Format a message as information with blue color."""
    return f"{TextStyle.INFO}ℹ {message}{TextStyle.RESET}"


def print_header(title: str, width: int = 80, char: str = '=') -> None:
    """
    Print a formatted section header to the console.
    
    Args:
        title: Header title text
        width: Width of the header in characters
        char: Character to use for the header border
    """
    print(f"\n{TextStyle.HEADER}{char * width}{TextStyle.RESET}")
    
    # Calculate padding to center the title
    padding = (width - len(title) - 2) // 2
    side_chars = char * padding
    
    # Ensure total width with padding doesn't exceed specified width
    if len(side_chars) * 2 + len(title) + 2 > width:
        side_chars = side_chars[:-1]
        
    print(f"{TextStyle.HEADER}{side_chars} {title} {side_chars}{TextStyle.RESET}")
    print(f"{TextStyle.HEADER}{char * width}{TextStyle.RESET}\n")


def print_subheader(title: str, width: int = 80) -> None:
    """
    Print a formatted sub-section header to the console.
    
    Args:
        title: Subheader title text
        width: Width of the subheader in characters
    """
    print(f"\n{TextStyle.BOLD}{TextStyle.BRIGHT_MAGENTA}{title}{TextStyle.RESET}")
    print(f"{TextStyle.BRIGHT_MAGENTA}{'-' * width}{TextStyle.RESET}")


def print_table(
    data: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
    title: Optional[str] = None,
    show_index: bool = False
) -> None:
    """
    Print a nicely formatted table to the console.
    
    Args:
        data: List of dictionaries with data to display
        columns: List of column names to include (defaults to all keys in first row)
        title: Optional table title
        show_index: Whether to show row indices
    """
    if not data:
        print(format_warning("No data to display"))
        return
    
    # Get columns from data if not specified
    if columns is None:
        columns = list(data[0].keys())
    
    # Get max width for each column
    col_widths = {col: len(col) for col in columns}
    if show_index:
        idx_width = len(str(len(data)))
        col_widths["_index"] = max(idx_width, len("#"))
    
    for row in data:
        for col in columns:
            if col in row:
                col_widths[col] = max(col_widths[col], len(str(row[col])))
    
    # Calculate total width
    total_width = sum(col_widths.values()) + (3 * len(col_widths)) - 1
    
    # Print title if provided
    if title:
        print(f"\n{TextStyle.BOLD}{TextStyle.BRIGHT_CYAN}{title}{TextStyle.RESET}")
    
    # Print top border
    print(f"┌{'┬'.join(['─' * (col_widths[col] + 2) for col in ([('_index' if show_index else None)] + columns if show_index else columns)])}")
    
    # Print header
    header_row = []
    if show_index:
        header_row.append(f"│ {'#'.center(col_widths['_index'])} ")
    for col in columns:
        header_row.append(f"│ {TextStyle.BOLD}{col.center(col_widths[col])}{TextStyle.RESET} ")
    print("".join(header_row) + "│")
    
    # Print header separator
    print(f"├{'┼'.join(['─' * (col_widths[col] + 2) for col in ([('_index' if show_index else None)] + columns if show_index else columns)])}")
    
    # Print rows
    for i, row in enumerate(data):
        row_str = []
        if show_index:
            row_str.append(f"│ {str(i).center(col_widths['_index'])} ")
        for col in columns:
            value = row.get(col, "")
            row_str.append(f"│ {str(value).ljust(col_widths[col])} ")
        print("".join(row_str) + "│")
    
    # Print bottom border
    print(f"└{'┴'.join(['─' * (col_widths[col] + 2) for col in ([('_index' if show_index else None)] + columns if show_index else columns)])}")


def progress_spinner(message: str, complete: bool = False) -> None:
    """
    Print a simple spinner or completion message.
    
    Args:
        message: Message to display
        complete: Whether the operation is complete
    """
    if complete:
        print(f"{TextStyle.SUCCESS}✓ {message} - Complete{TextStyle.RESET}")
    else:
        print(f"{TextStyle.BRIGHT_BLUE}⟳ {message}...{TextStyle.RESET}")
