"""Feature extraction orchestrator."""
import logging
import pandas as pd
from typing import Dict
from .doc_scorer import DocumentationScorer


logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Orchestrates feature engineering pipeline."""

    def __init__(self, scorer: DocumentationScorer):
        """Initialize feature extractor.

        Args:
            scorer: DocumentationScorer instance
        """
        self.scorer = scorer

    def process_dataset(
        self,
        raw_data_path: str = "data/raw_pwc_data.csv",
        output_path: str = "data/processed_data.csv"
    ) -> pd.DataFrame:
        """Transform raw data into analysis-ready features.

        Args:
            raw_data_path: Path to raw data CSV
            output_path: Path to save processed data

        Returns:
            Processed DataFrame
        """
        logger.info("Loading raw data...")
        df = pd.read_csv(raw_data_path)

        logger.info(f"Loaded {len(df)} records")

        # Validate data quality
        quality_report = self.validate_data_quality(df)
        logger.info(f"Data quality report: {quality_report}")

        # Save processed data
        df.to_csv(output_path, index=False)
        logger.info(f"Saved processed data to {output_path}")

        return df

    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, float]:
        """Check missing data rates.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary with missing data rates per column

        Raises:
            ValueError: If missing data > 10% for critical columns
        """
        critical_columns = ['doc_score', 'reproduced_within_12m', 'pub_year']

        missing_rates = {}
        for col in critical_columns:
            if col in df.columns:
                missing_rate = df[col].isna().mean()
                missing_rates[col] = missing_rate

                if missing_rate > 0.1:
                    raise ValueError(
                        f"Missing data rate for {col} exceeds 10%: {missing_rate:.2%}"
                    )

        logger.info(f"Data quality validation passed")
        return missing_rates
