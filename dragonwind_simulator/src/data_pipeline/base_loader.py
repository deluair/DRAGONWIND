from abc import ABC, abstractmethod
import pandas as pd

class DataLoader(ABC):
    """
    Abstract base class for data loaders in the DRAGONWIND platform.

    Each loader is responsible for ingesting data from a specific source
    (e.g., CSV, Excel, API) and returning it in a standardized format,
    such as a pandas DataFrame.
    """

    @abstractmethod
    def load(self, source: str) -> pd.DataFrame:
        """
        Loads data from the given source.

        Args:
            source (str): The path or identifier for the data source.

        Returns:
            pd.DataFrame: The loaded data as a pandas DataFrame.
        """
        pass
