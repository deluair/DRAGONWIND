"""
Data export utilities for DRAGONWIND simulation results.

This module provides functionality for exporting simulation results
in various formats (CSV, Excel, JSON, Parquet) for further analysis.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from src.utils.exceptions import ExportError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataExporter:
    """
    Handles exporting of simulation data to various formats.
    """
    
    def __init__(self, output_dir: Union[str, Path]):
        """
        Initialize the data exporter.
        
        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_dataframe(
        self,
        df: pd.DataFrame,
        name: str,
        formats: List[str] = ["parquet"],
        timestamp: Optional[str] = None
    ) -> Dict[str, Path]:
        """
        Export a pandas DataFrame to specified formats.
        
        Args:
            df: DataFrame to export
            name: Base name for the exported file
            formats: List of formats to export to ("csv", "excel", "json", "parquet")
            timestamp: Optional timestamp to include in filename
            
        Returns:
            Dictionary mapping format to saved file path
            
        Raises:
            ExportError: If export to any format fails
        """
        results = {}
        
        # Add timestamp to create a subfolder if provided
        if timestamp:
            export_dir = self.output_dir / timestamp
            os.makedirs(export_dir, exist_ok=True)
        else:
            export_dir = self.output_dir
            
        try:
            # Export to each requested format
            for fmt in formats:
                if fmt == "csv":
                    file_path = export_dir / f"{name}.csv"
                    df.to_csv(file_path, index=True)
                    results["csv"] = file_path
                    logger.info(f"Exported data to CSV: {file_path}")
                    
                elif fmt == "excel":
                    file_path = export_dir / f"{name}.xlsx"
                    df.to_excel(file_path, sheet_name=name, index=True)
                    results["excel"] = file_path
                    logger.info(f"Exported data to Excel: {file_path}")
                    
                elif fmt == "json":
                    file_path = export_dir / f"{name}.json"
                    # Convert to records format for more readable JSON
                    df_dict = df.reset_index().to_dict(orient="records")
                    with open(file_path, 'w') as f:
                        json.dump(df_dict, f, indent=2)
                    results["json"] = file_path
                    logger.info(f"Exported data to JSON: {file_path}")
                    
                elif fmt == "parquet":
                    file_path = export_dir / f"{name}.parquet"
                    df.to_parquet(file_path, index=True)
                    results["parquet"] = file_path
                    logger.info(f"Exported data to Parquet: {file_path}")
                    
                else:
                    logger.warning(f"Unsupported export format: {fmt}")
                    
            return results
            
        except Exception as e:
            raise ExportError(f"Failed to export data in {fmt} format: {e}")
    
    def export_results(
        self,
        results: Dict[str, pd.DataFrame],
        formats: List[str] = ["parquet"],
        timestamp: Optional[str] = None
    ) -> Dict[str, Dict[str, Path]]:
        """
        Export a dictionary of DataFrames to specified formats.
        
        Args:
            results: Dictionary mapping names to DataFrames
            formats: List of formats to export to
            timestamp: Optional timestamp to include in filename
            
        Returns:
            Nested dictionary mapping names and formats to file paths
        """
        exports = {}
        
        for name, df in results.items():
            exports[name] = self.export_dataframe(
                df, name, formats, timestamp
            )
            
        return exports
    
    def export_combined_excel(
        self,
        results: Dict[str, pd.DataFrame],
        filename: str = "combined_results",
        timestamp: Optional[str] = None
    ) -> Path:
        """
        Export multiple DataFrames to a single Excel file with multiple sheets.
        
        Args:
            results: Dictionary mapping sheet names to DataFrames
            filename: Name for the Excel file
            timestamp: Optional timestamp to include in filename
            
        Returns:
            Path to the saved Excel file
        """
        # Add timestamp to create a subfolder if provided
        if timestamp:
            export_dir = self.output_dir / timestamp
            os.makedirs(export_dir, exist_ok=True)
        else:
            export_dir = self.output_dir
        
        file_path = export_dir / f"{filename}.xlsx"
        
        try:
            with pd.ExcelWriter(file_path) as writer:
                for sheet_name, df in results.items():
                    # Truncate sheet names to Excel's limit of 31 characters
                    truncated_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=truncated_name, index=True)
                    
            logger.info(f"Exported combined data to Excel: {file_path}")
            return file_path
            
        except Exception as e:
            raise ExportError(f"Failed to export combined Excel file: {e}")
