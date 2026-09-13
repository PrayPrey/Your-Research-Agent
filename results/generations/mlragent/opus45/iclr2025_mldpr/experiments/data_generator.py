"""
Synthetic dataset generator for DDHS experiments.
Generates realistic dataset metadata and usage patterns for evaluation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os


@dataclass
class DatasetMetadata:
    """Metadata for a simulated ML dataset"""
    dataset_id: str
    name: str
    domain: str
    creation_date: datetime
    last_updated: datetime
    num_samples: int
    num_features: int
    task_type: str  # classification, regression, etc.

    # Usage metrics
    total_downloads: int
    monthly_downloads: List[int]
    citation_count: int
    monthly_citations: List[int]

    # Documentation
    has_datasheet: bool
    has_data_card: bool
    readme_length: int
    doc_fields_filled: int
    doc_fields_total: int

    # Community metrics
    num_issues: int
    num_resolved_issues: int
    avg_response_time_days: float
    num_updates: int
    maintainer_active: bool

    # Ethical metrics
    has_bias_report: bool
    known_issues: List[str]
    ethical_flags: int

    # Ground truth labels
    is_deprecated: bool
    deprecation_reason: Optional[str]
    quality_score_expert: float  # Expert-assigned quality (0-1)


class SyntheticDataGenerator:
    """
    Generate synthetic dataset metadata for DDHS evaluation.
    Simulates realistic patterns observed in ML repositories.
    """

    DOMAINS = [
        'computer_vision', 'nlp', 'tabular', 'audio', 'reinforcement_learning',
        'time_series', 'graph', 'medical', 'finance', 'recommender'
    ]

    TASK_TYPES = [
        'classification', 'regression', 'clustering', 'generation',
        'detection', 'segmentation', 'qa', 'translation', 'summarization'
    ]

    DEPRECATION_REASONS = [
        'bias_issues', 'outdated_distribution', 'licensing_problems',
        'privacy_concerns', 'maintainer_inactive', 'better_alternative',
        'benchmark_saturation', 'data_quality_issues'
    ]

    def __init__(self, seed: int = 42, num_snapshots: int = 12):
        self.rng = np.random.default_rng(seed)
        self.num_snapshots = num_snapshots
        self.base_date = datetime(2024, 1, 1)

    def generate_dataset(self, idx: int, force_deprecated: bool = False) -> DatasetMetadata:
        """Generate a single synthetic dataset"""

        domain = self.rng.choice(self.DOMAINS)
        task_type = self.rng.choice(self.TASK_TYPES)

        # Age of dataset (months)
        age_months = int(self.rng.integers(1, 60))
        creation_date = self.base_date - timedelta(days=age_months * 30)

        # Generate usage patterns (correlated with quality)
        base_popularity = self.rng.beta(2, 5)  # Most datasets have low popularity

        # Generate monthly metrics
        monthly_downloads = self._generate_usage_trend(base_popularity, age_months)
        monthly_citations = self._generate_citation_trend(base_popularity, age_months)

        # Documentation quality
        doc_quality = self.rng.beta(3, 2)  # Slightly skewed toward better documentation
        doc_fields_total = 15
        doc_fields_filled = int(doc_fields_total * doc_quality)

        # Community responsiveness (correlated with documentation)
        responsiveness = doc_quality * self.rng.uniform(0.5, 1.5)
        responsiveness = np.clip(responsiveness, 0, 1)

        num_issues = self.rng.poisson(lam=5 * base_popularity + 2)
        num_resolved = int(num_issues * responsiveness)

        # Ethical metrics
        has_bias = self.rng.random() < 0.2
        ethical_flags = self.rng.poisson(lam=0.5) if has_bias else 0

        # Determine deprecation status
        # Deprecation more likely for old, poorly maintained, ethically flagged datasets
        deprecation_prob = 0.1
        if age_months > 36:
            deprecation_prob += 0.1
        if doc_quality < 0.3:
            deprecation_prob += 0.15
        if responsiveness < 0.3:
            deprecation_prob += 0.15
        if ethical_flags > 0:
            deprecation_prob += 0.2

        is_deprecated = force_deprecated or (self.rng.random() < deprecation_prob)
        deprecation_reason = self.rng.choice(self.DEPRECATION_REASONS) if is_deprecated else None

        # Expert quality score (influenced by multiple factors)
        quality_score = self._compute_expert_quality(
            doc_quality, responsiveness, base_popularity,
            age_months, ethical_flags, is_deprecated
        )

        # Last update time
        if responsiveness > 0.5:
            last_updated = self.base_date - timedelta(days=int(self.rng.integers(1, 90)))
        else:
            last_updated = self.base_date - timedelta(days=int(self.rng.integers(180, 730)))

        return DatasetMetadata(
            dataset_id=f"dataset_{idx:04d}",
            name=f"{domain}_{task_type}_{idx}",
            domain=domain,
            creation_date=creation_date,
            last_updated=last_updated,
            num_samples=int(10 ** self.rng.uniform(2, 7)),
            num_features=self.rng.integers(5, 1000),
            task_type=task_type,
            total_downloads=sum(monthly_downloads),
            monthly_downloads=monthly_downloads,
            citation_count=sum(monthly_citations),
            monthly_citations=monthly_citations,
            has_datasheet=self.rng.random() < doc_quality,
            has_data_card=self.rng.random() < doc_quality * 0.8,
            readme_length=int(500 * doc_quality * self.rng.uniform(0.5, 2.0)),
            doc_fields_filled=doc_fields_filled,
            doc_fields_total=doc_fields_total,
            num_issues=num_issues,
            num_resolved_issues=num_resolved,
            avg_response_time_days=max(0.5, 30 * (1 - responsiveness) * self.rng.uniform(0.5, 2.0)),
            num_updates=self.rng.poisson(lam=age_months * responsiveness * 0.5),
            maintainer_active=responsiveness > 0.5,
            has_bias_report=has_bias,
            known_issues=[f"issue_{i}" for i in range(ethical_flags)],
            ethical_flags=ethical_flags,
            is_deprecated=is_deprecated,
            deprecation_reason=deprecation_reason,
            quality_score_expert=quality_score
        )

    def _generate_usage_trend(self, popularity: float, age_months: int) -> List[int]:
        """Generate monthly download trend"""
        trend = []
        base = popularity * 10000

        for i in range(min(age_months, self.num_snapshots)):
            # Add seasonality and noise
            seasonal = 1 + 0.2 * np.sin(2 * np.pi * i / 12)
            noise = self.rng.normal(1, 0.3)
            # Older datasets may have declining trends
            decay = np.exp(-0.02 * i)
            downloads = max(0, int(base * seasonal * noise * decay))
            trend.append(downloads)

        # Pad with zeros if dataset is newer than snapshot period
        while len(trend) < self.num_snapshots:
            trend.insert(0, 0)

        return trend

    def _generate_citation_trend(self, popularity: float, age_months: int) -> List[int]:
        """Generate monthly citation trend"""
        trend = []
        base = popularity * 50

        for i in range(min(age_months, self.num_snapshots)):
            noise = self.rng.normal(1, 0.4)
            # Citations tend to grow over time then plateau
            growth = np.log1p(i) / np.log1p(self.num_snapshots)
            citations = max(0, int(base * noise * growth))
            trend.append(citations)

        while len(trend) < self.num_snapshots:
            trend.insert(0, 0)

        return trend

    def _compute_expert_quality(
        self,
        doc_quality: float,
        responsiveness: float,
        popularity: float,
        age_months: int,
        ethical_flags: int,
        is_deprecated: bool
    ) -> float:
        """Compute simulated expert quality score"""

        # Base quality from documentation and responsiveness
        quality = 0.3 * doc_quality + 0.3 * responsiveness

        # Popularity adds some value (but not too much)
        quality += 0.15 * min(1.0, popularity * 2)

        # Freshness bonus for newer datasets
        freshness = np.exp(-age_months / 48)
        quality += 0.15 * freshness

        # Ethical penalties
        quality -= 0.1 * min(1.0, ethical_flags * 0.3)

        # Deprecated datasets get lower scores
        if is_deprecated:
            quality *= 0.6

        # Add some noise
        quality += self.rng.normal(0, 0.05)

        return float(np.clip(quality, 0, 1))

    def generate_repository(self, num_datasets: int, deprecation_rate: float = 0.15) -> List[DatasetMetadata]:
        """Generate a complete synthetic repository"""

        datasets = []
        num_deprecated = int(num_datasets * deprecation_rate)

        # First generate deprecated datasets
        for i in range(num_deprecated):
            datasets.append(self.generate_dataset(i, force_deprecated=True))

        # Then generate remaining datasets (some may still be deprecated)
        for i in range(num_deprecated, num_datasets):
            datasets.append(self.generate_dataset(i, force_deprecated=False))

        # Shuffle to mix deprecated and non-deprecated
        self.rng.shuffle(datasets)

        return datasets

    def to_dataframe(self, datasets: List[DatasetMetadata]) -> pd.DataFrame:
        """Convert dataset list to pandas DataFrame"""
        records = []
        for ds in datasets:
            record = {
                'dataset_id': ds.dataset_id,
                'name': ds.name,
                'domain': ds.domain,
                'creation_date': ds.creation_date,
                'last_updated': ds.last_updated,
                'age_months': (self.base_date - ds.creation_date).days // 30,
                'num_samples': ds.num_samples,
                'num_features': ds.num_features,
                'task_type': ds.task_type,
                'total_downloads': ds.total_downloads,
                'citation_count': ds.citation_count,
                'has_datasheet': ds.has_datasheet,
                'has_data_card': ds.has_data_card,
                'readme_length': ds.readme_length,
                'doc_fields_filled': ds.doc_fields_filled,
                'doc_fields_total': ds.doc_fields_total,
                'doc_completeness': ds.doc_fields_filled / ds.doc_fields_total,
                'num_issues': ds.num_issues,
                'num_resolved_issues': ds.num_resolved_issues,
                'resolution_rate': ds.num_resolved_issues / max(1, ds.num_issues),
                'avg_response_time_days': ds.avg_response_time_days,
                'num_updates': ds.num_updates,
                'maintainer_active': ds.maintainer_active,
                'has_bias_report': ds.has_bias_report,
                'ethical_flags': ds.ethical_flags,
                'is_deprecated': ds.is_deprecated,
                'deprecation_reason': ds.deprecation_reason,
                'quality_score_expert': ds.quality_score_expert
            }
            records.append(record)

        return pd.DataFrame(records)

    def save_datasets(self, datasets: List[DatasetMetadata], output_path: str):
        """Save datasets to JSON file"""
        data = []
        for ds in datasets:
            data.append({
                'dataset_id': ds.dataset_id,
                'name': ds.name,
                'domain': ds.domain,
                'creation_date': ds.creation_date.isoformat(),
                'last_updated': ds.last_updated.isoformat(),
                'num_samples': ds.num_samples,
                'num_features': ds.num_features,
                'task_type': ds.task_type,
                'total_downloads': ds.total_downloads,
                'monthly_downloads': ds.monthly_downloads,
                'citation_count': ds.citation_count,
                'monthly_citations': ds.monthly_citations,
                'has_datasheet': ds.has_datasheet,
                'has_data_card': ds.has_data_card,
                'readme_length': ds.readme_length,
                'doc_fields_filled': ds.doc_fields_filled,
                'doc_fields_total': ds.doc_fields_total,
                'num_issues': ds.num_issues,
                'num_resolved_issues': ds.num_resolved_issues,
                'avg_response_time_days': ds.avg_response_time_days,
                'num_updates': ds.num_updates,
                'maintainer_active': ds.maintainer_active,
                'has_bias_report': ds.has_bias_report,
                'known_issues': ds.known_issues,
                'ethical_flags': ds.ethical_flags,
                'is_deprecated': ds.is_deprecated,
                'deprecation_reason': ds.deprecation_reason,
                'quality_score_expert': ds.quality_score_expert
            })

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    # Test the generator
    generator = SyntheticDataGenerator(seed=42)
    datasets = generator.generate_repository(num_datasets=100)

    df = generator.to_dataframe(datasets)
    print(f"Generated {len(datasets)} datasets")
    print(f"Deprecated: {df['is_deprecated'].sum()} ({df['is_deprecated'].mean()*100:.1f}%)")
    print(f"\nSample statistics:")
    print(df[['total_downloads', 'citation_count', 'doc_completeness',
              'resolution_rate', 'ethical_flags', 'quality_score_expert']].describe())
