from pathlib import Path
from typing import List
import pandas as pd


class FeatureLoader:
    def __init__(self, input_path: str):
        """Load h-m1 extracted features."""
        self.input_path = Path(input_path)

    def load_features(self) -> pd.DataFrame:
        """Load CSV. Returns: DataFrame[20 rows × 4 cols]"""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        df = pd.read_csv(self.input_path)

        # Validate schema
        required_cols = ["benchmark_name", "task_type", "modality", "metrics", "dataset_size"]
        missing = set(required_cols) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Validate no missing values
        if df[required_cols].isnull().any().any():
            raise ValueError("Missing values in required columns")

        return df

    def to_descriptions(self, features: pd.DataFrame, template: str) -> List[str]:
        """Convert features to natural language. Returns: 20 descriptions"""
        descriptions = []
        for _, row in features.iterrows():
            desc = template.format(
                task_type=row["task_type"],
                modality=row["modality"],
                metrics=row["metrics"],
                dataset_size=row["dataset_size"]
            )
            descriptions.append(desc)

        return descriptions
