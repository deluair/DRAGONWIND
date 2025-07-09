import pandas as pd
from .base_loader import DataLoader

class CSVLoader(DataLoader):
    """
    A data loader for reading data from CSV files.
    """

    def load(self, source: str) -> pd.DataFrame:
        """
        Loads data from a CSV file into a pandas DataFrame.

        Args:
            source (str): The file path to the CSV file.

        Returns:
            pd.DataFrame: The loaded data.
        """
        try:
            print(f"Loading data from {source}...")
            return pd.read_csv(source)
        except FileNotFoundError:
            print(f"Error: The file was not found at {source}")
            return pd.DataFrame()
        except Exception as e:
            print(f"An error occurred while loading the CSV file: {e}")
            return pd.DataFrame()
