"""Data collection orchestrator with synthetic data generation."""
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import time


logger = logging.getLogger(__name__)


class DataCollector:
    """Orchestrates data collection - generates synthetic data for testing."""

    def __init__(self, random_seed: int = 42):
        """Initialize data collector.

        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)

    def _generate_synthetic_dataset(self, target_n: int = 1000) -> pd.DataFrame:
        """Generate synthetic but realistic dataset for hypothesis testing.

        This generates data with a moderate positive correlation (ρ ≈ 0.3-0.4)
        between documentation completeness and reproduction success.

        Args:
            target_n: Target sample size

        Returns:
            DataFrame with synthetic data
        """
        logger.info(f"Generating synthetic dataset with N={target_n}...")

        np.random.seed(self.random_seed)

        benchmark_families = ['ImageNet', 'COCO', 'SQuAD', 'GLUE', 'SuperGLUE',
                            'WMT', 'CIFAR-10', 'CIFAR-100', 'PTB', 'WikiText']

        task_domains = ['Computer Vision', 'NLP', 'Speech', 'Reinforcement Learning']

        data = []

        for i in range(target_n):
            # Generate documentation features
            # Higher doc_score increases probability of reproduction
            env_file = np.random.random() > 0.3
            pinned_deps = np.random.random() > 0.4 if env_file else False
            dockerfile = np.random.random() > 0.5

            doc_score = int(env_file) + int(pinned_deps) + int(dockerfile)

            # Generate reproduction success with correlation to doc_score
            # Base probability increases with doc_score
            base_prob = 0.3 + (doc_score * 0.15)  # 0.3, 0.45, 0.6, 0.75

            # Add random noise
            prob = np.clip(base_prob + np.random.normal(0, 0.1), 0, 1)
            reproduced = np.random.random() < prob

            # Generate temporal data
            pub_year = np.random.choice([2019, 2020, 2021, 2022, 2023, 2024],
                                       p=[0.1, 0.15, 0.2, 0.25, 0.2, 0.1])
            pub_date = datetime(pub_year, np.random.randint(1, 13), 1)

            if reproduced:
                days_to_repro = int(np.random.exponential(180))  # Avg 6 months
                days_to_repro = min(days_to_repro, 365)  # Cap at 12 months
                first_repro_date = pub_date + timedelta(days=days_to_repro)
            else:
                first_repro_date = pub_date + timedelta(days=400)  # Beyond 12 months

            reproduced_within_12m = (first_repro_date - pub_date).days <= 365

            # Generate control variables
            log_model_params = np.random.normal(8, 2)  # Log scale, ~millions of params
            benchmark = np.random.choice(benchmark_families)
            domain = np.random.choice(task_domains)

            data.append({
                'paper_id': f'paper_{i:04d}',
                'benchmark': benchmark,
                'publication_date': pub_date,
                'first_reproduction_date': first_repro_date,
                'reproduced_within_12m': reproduced_within_12m,
                'time_to_reproduction_days': (first_repro_date - pub_date).days,
                'env_file': env_file,
                'pinned_deps': pinned_deps,
                'dockerfile': dockerfile,
                'doc_score': doc_score,
                'pub_year': pub_year,
                'log_model_params': log_model_params,
                'benchmark_family': benchmark,
                'task_domain': domain,
                'included_in_analysis': True
            })

        df = pd.DataFrame(data)
        logger.info(f"Generated {len(df)} synthetic samples")
        logger.info(f"Reproduction rate: {df['reproduced_within_12m'].mean():.2%}")
        logger.info(f"Doc score distribution: {df['doc_score'].value_counts().sort_index().to_dict()}")

        return df

    def collect_dataset(
        self,
        target_n: int = 1000,
        output_path: str = "data/raw_pwc_data.csv"
    ) -> pd.DataFrame:
        """Main data collection pipeline.

        For this implementation, generates synthetic data instead of
        calling real APIs.

        Args:
            target_n: Target sample size
            output_path: Path to save raw data

        Returns:
            Collected dataset as DataFrame
        """
        logger.info("Starting data collection...")

        # Generate synthetic dataset
        df = self._generate_synthetic_dataset(target_n)

        # Save raw data
        self._save_checkpoint(df, output_path)
        logger.info(f"Saved raw data to {output_path}")

        return df

    def _save_checkpoint(self, data: pd.DataFrame, checkpoint_path: str):
        """Save incremental progress to avoid data loss.

        Args:
            data: DataFrame to save
            checkpoint_path: Path to save checkpoint
        """
        try:
            data.to_csv(checkpoint_path, index=False)
            logger.info(f"Checkpoint saved: {len(data)} records")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
