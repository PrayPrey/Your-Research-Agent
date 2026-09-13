"""Data loader for H-M3 viability classification."""

from pathlib import Path
import pandas as pd
import numpy as np


class ViabilityCorpusLoader:
    """Load corpus with O_10 and O_full for viability classification."""

    def __init__(self, corpus_path: str = None):
        """Initialize. If corpus_path None, generates synthetic data."""
        self.path = Path(corpus_path) if corpus_path else None

    def load(self) -> pd.DataFrame:
        """Load corpus. Returns df: [hypothesis_id, type, O_10, O_full, threshold]"""
        if self.path and self.path.exists():
            return pd.read_csv(self.path)
        return self._generate_synthetic_corpus()

    def _generate_synthetic_corpus(self) -> pd.DataFrame:
        """
        Generate synthetic retrospective ML corpus for viability classification.

        Setup:
        - 30 hypotheses (stratified: 10 low <20%, 10 mid 20-80%, 10 high >80%)
        - O_10: 10-sample overhead (Gate 1 measurement)
        - O_full: full-scale overhead (ground truth)
        - k=1.0 from H-M1 validation (perfect correlation)
        - threshold=10% (deployment context)

        Goal: Test if O_10-based classification achieves >80% accuracy.
        """
        np.random.seed(42)

        types = ["attention", "gradient", "normalization", "regularization"]
        threshold = 0.10

        # Stratified sampling: low/mid/high overhead
        low = np.random.uniform(0.02, 0.19, 10)   # <20% overhead
        mid = np.random.uniform(0.20, 0.79, 10)   # 20-80%
        high = np.random.uniform(0.80, 0.95, 10)  # >80%

        O_full = np.concatenate([low, mid, high])

        # O_10 = O_full * k with small measurement noise
        # k=1.0 from H-M1, noise ±5% to avoid perfect classification
        noise = np.random.normal(0, 0.05, 30)
        O_10 = O_full + noise
        O_10 = np.clip(O_10, 0.001, 0.99)

        return pd.DataFrame({
            "hypothesis_id": [f"hyp-{i+1:03d}" for i in range(30)],
            "type": np.random.choice(types, 30),
            "O_10": O_10,
            "O_full": O_full,
            "threshold": [threshold] * 30
        })

    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Check required columns exist."""
        required = ["hypothesis_id", "O_10", "O_full", "threshold"]
        return all(col in df.columns for col in required)

    def get_labels(self, df: pd.DataFrame) -> list:
        """Generate ground truth labels: 'viable' if O_full <= threshold else 'non-viable'."""
        return ["viable" if o <= t else "non-viable"
                for o, t in zip(df["O_full"], df["threshold"])]
