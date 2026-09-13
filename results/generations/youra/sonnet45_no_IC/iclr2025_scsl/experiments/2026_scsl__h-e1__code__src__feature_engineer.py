"""Feature Engineering Module for Repository Maintenance Classification."""

import numpy as np
import pandas as pd
from typing import Tuple, Dict
from scipy import stats


class FeatureEngineer:
    """Transforms raw GitHub metadata into classification features."""

    def __init__(self):
        """Initialize feature engineering pipeline."""
        self.feature_names = [
            'stars_log',
            'forks_log',
            'contributors_log',
            'total_commits_log',
            'open_issues_log',
            'days_since_last_commit',
            'commit_frequency_median_weekly',
            'issue_resolution_rate'
        ]

    def transform_features(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Apply log1p transforms to long-tail features.

        Args:
            raw_data: DataFrame with raw GitHub metadata

        Returns:
            DataFrame with transformed features (8 columns)
        """
        features = pd.DataFrame()

        # Log1p transformations for long-tail distributions
        features['stars_log'] = np.log1p(raw_data['stars'])
        features['forks_log'] = np.log1p(raw_data['forks'])
        features['contributors_log'] = np.log1p(raw_data['contributors'])
        features['total_commits_log'] = np.log1p(raw_data['total_commits'])
        features['open_issues_log'] = np.log1p(raw_data['open_issues'])

        # Raw features (already meaningful scale)
        features['days_since_last_commit'] = raw_data['days_since_last_commit']

        # Derived features
        features['commit_frequency_median_weekly'] = raw_data.get('commit_frequency_median_weekly', 0.0)

        # Issue resolution rate (handle division by zero)
        total_issues = raw_data['total_issues'].replace(0, 1)  # Avoid division by zero
        features['issue_resolution_rate'] = raw_data['closed_issues'] / total_issues

        # Handle any NaN or inf values
        features = features.replace([np.inf, -np.inf], np.nan)
        features = features.fillna(0)

        return features

    def create_labels(self, raw_data: pd.DataFrame, threshold_days: int = 180) -> np.ndarray:
        """Generate binary labels from last commit recency.

        Args:
            raw_data: DataFrame with 'days_since_last_commit' column
            threshold_days: Threshold for maintained classification (default: 180)

        Returns:
            Binary labels (1 = maintained, 0 = abandoned)
        """
        labels = (raw_data['days_since_last_commit'] < threshold_days).astype(int)
        return labels.values

    def validate_distributions(self, features: pd.DataFrame) -> Dict:
        """Validate that log transformations achieved normality.

        Args:
            features: DataFrame with transformed features

        Returns:
            Dict with validation results per feature
        """
        validation = {}

        log_features = [
            'stars_log',
            'forks_log',
            'contributors_log',
            'total_commits_log',
            'open_issues_log'
        ]

        for feature in log_features:
            if feature in features.columns:
                # Shapiro-Wilk test for normality (sample up to 5000 for performance)
                sample = features[feature].dropna().values
                if len(sample) > 5000:
                    sample = np.random.choice(sample, 5000, replace=False)

                if len(sample) > 3:
                    statistic, p_value = stats.shapiro(sample)
                    validation[feature] = {
                        'shapiro_statistic': float(statistic),
                        'shapiro_p_value': float(p_value),
                        'is_normal': p_value > 0.05,
                        'skewness': float(stats.skew(features[feature].dropna())),
                        'kurtosis': float(stats.kurtosis(features[feature].dropna()))
                    }

        return validation

    def get_feature_summary(self, features: pd.DataFrame) -> pd.DataFrame:
        """Generate descriptive statistics for all features.

        Args:
            features: DataFrame with transformed features

        Returns:
            DataFrame with summary statistics
        """
        summary = features.describe().T
        summary['missing_count'] = features.isnull().sum()
        summary['missing_pct'] = (features.isnull().sum() / len(features)) * 100
        return summary
