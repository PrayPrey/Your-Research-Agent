import pandas as pd
from typing import Optional

class DatasetCorpus:
    """Manages dataset corpus CSV."""

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame:
        """Load corpus CSV."""
        self.df = pd.read_csv(self.csv_path)
        return self.df

    def get_by_domain(self, domain: str) -> pd.DataFrame:
        """Filter by domain (NLP or CV)."""
        if self.df is None:
            raise ValueError("Must call load() first")
        return self.df[self.df['domain'] == domain]

    def validate(self) -> bool:
        """Check corpus has 100 NLP + 100 CV datasets."""
        if self.df is None:
            return False
        nlp_count = len(self.get_by_domain("NLP"))
        cv_count = len(self.get_by_domain("CV"))
        return nlp_count >= 100 and cv_count >= 100
