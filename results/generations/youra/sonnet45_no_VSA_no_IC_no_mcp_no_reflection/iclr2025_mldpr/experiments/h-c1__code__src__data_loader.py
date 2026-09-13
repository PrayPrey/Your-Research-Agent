"""Survey data loading and filtering."""

from dataclasses import dataclass
from typing import Tuple
import pandas as pd


@dataclass
class SurveyResponse:
    """Single expert response."""
    benchmark: str
    saturation_year: int
    saturation_month: int
    confidence: int
    domain: str
    career_stage: str


class SurveyDataLoader:
    def __init__(self, csv_path: str, confidence_threshold: int = 4):
        """
        Args:
            csv_path: Path to survey CSV
            confidence_threshold: Min confidence (1-5)
        """
        self.csv_path = csv_path
        self.confidence_threshold = confidence_threshold

    def load_raw(self) -> pd.DataFrame:
        """Load CSV. Returns df with required columns."""
        df = pd.read_csv(self.csv_path)
        required_cols = [
            'response_id', 'benchmark', 'saturation_year',
            'saturation_month', 'confidence', 'domain', 'career_stage'
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return df

    def filter_high_confidence(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keep rows where confidence >= threshold."""
        return df[df['confidence'] >= self.confidence_threshold].copy()

    def validate_completeness(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Check required fields exist. Returns (is_valid, error_message)."""
        if df.empty:
            return False, "DataFrame is empty"

        required_cols = ['benchmark', 'saturation_year', 'saturation_month', 'confidence']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return False, f"Missing columns: {missing}"

        null_cols = [c for c in required_cols if df[c].isnull().any()]
        if null_cols:
            return False, f"Null values in columns: {null_cols}"

        return True, ""

    def get_benchmark_subset(self, df: pd.DataFrame, benchmark: str) -> pd.DataFrame:
        """Extract rows for one benchmark."""
        return df[df['benchmark'] == benchmark].copy()
