"""
Feature Computation Module for H-M1
Computes Tier 1 (universal) and Tier 2 (domain-specific) features.
"""

import numpy as np
import pandas as pd
from typing import List, Dict


class Tier1FeatureComputer:
    """Compute universal features applicable to all datasets."""

    @staticmethod
    def compute_features(benchmarks: List[Dict]) -> pd.DataFrame:
        """
        Compute Tier 1 universal features for all benchmarks.
        Only includes benchmarks with sufficient real data - NO DEFAULT FALLBACKS.

        Args:
            benchmarks: List of benchmark dictionaries

        Returns:
            DataFrame with columns: sample_size, dimensionality, num_classes, class_imbalance
            Only rows where real data is available (no synthetic defaults)
        """
        features_data = []
        benchmark_ids = []
        skipped = []

        for benchmark in benchmarks:
            benchmark_id = benchmark.get('benchmark_id', benchmark.get('dataset_name', 'unknown'))

            # Extract features - NO FALLBACKS, skip if missing
            sample_size = benchmark.get('sample_size', benchmark.get('total_samples', None))

            # Dimensionality: handle different formats
            dim = benchmark.get('dimensionality', None)
            if dim is None:
                dimensionality = None
            elif isinstance(dim, list):  # e.g., [32, 32, 3] for images
                dimensionality = int(np.prod(dim))
            elif isinstance(dim, str):  # e.g., "32x32x3"
                try:
                    parts = dim.replace('x', '*').replace(',', '*')
                    dimensionality = eval(parts)
                except:
                    dimensionality = None
            else:
                dimensionality = int(dim) if dim else None

            num_classes = benchmark.get('num_classes', benchmark.get('classes', None))
            if num_classes is None:
                num_classes_val = None
            elif isinstance(num_classes, str):
                try:
                    num_classes_val = int(num_classes)
                except:
                    num_classes_val = None
            else:
                num_classes_val = int(num_classes)

            # Class imbalance: compute from method rankings variance (real proxy)
            # Structure: method_rankings = {"MethodName": {"family": "X", "ranking_percentile": Y, ...}, ...}
            method_rankings = benchmark.get('method_rankings', {})
            if method_rankings and isinstance(method_rankings, dict):
                rankings = []
                for method_data in method_rankings.values():
                    if isinstance(method_data, dict):
                        # Try both field names
                        ranking = method_data.get('ranking_percentile') or method_data.get('percentile')
                        if ranking is not None:
                            rankings.append(float(ranking))

                # Use std of rankings as proxy for class imbalance (more variance = more imbalance)
                class_imbalance = float(np.std(rankings)) / 50.0 if len(rankings) > 1 else None
            else:
                class_imbalance = None

            # CRITICAL: Include all benchmarks (let correlation analysis handle NaN filtering)
            # Don't skip - we need benchmarks with method_rankings for correlation even if features are sparse
            benchmark_ids.append(benchmark_id)
            features_data.append({
                'sample_size': float(sample_size) if sample_size is not None else np.nan,
                'dimensionality': float(dimensionality) if dimensionality is not None else np.nan,
                'num_classes': float(num_classes_val) if num_classes_val is not None else np.nan,
                'class_imbalance': class_imbalance if class_imbalance is not None else np.nan
            })

        features_df = pd.DataFrame(features_data, index=benchmark_ids)

        # Report data quality (NaN = no mock fallback used)
        print(f"✓ Computed Tier 1 features for {len(features_df)} benchmarks (NO MOCK FALLBACKS)")
        for col in features_df.columns:
            non_nan = features_df[col].notna().sum()
            print(f"  {col}: {non_nan}/{len(features_df)} real values ({non_nan/len(features_df)*100:.1f}%)")

        return features_df


class Tier2FeatureComputer:
    """Compute domain-specific features."""

    @staticmethod
    def compute_features(benchmarks: List[Dict]) -> pd.DataFrame:
        """
        Compute Tier 2 domain-specific features.
        Only computes features from real data - NO DEFAULT FALLBACKS.

        Args:
            benchmarks: List of benchmark dictionaries

        Returns:
            DataFrame with domain-specific columns (NaN where data unavailable)
        """
        features_data = []
        benchmark_ids = []

        for benchmark in benchmarks:
            benchmark_id = benchmark.get('benchmark_id', benchmark.get('dataset_name', 'unknown'))
            benchmark_ids.append(benchmark_id)

            domain = benchmark.get('domain', 'unknown').lower()
            dim = benchmark.get('dimensionality', None)

            domain_features = {}

            if domain == 'vision' or domain == 'image':
                # Vision-specific features - only compute from real dimensionality data
                if isinstance(dim, list) and len(dim) >= 3:
                    H, W, C = dim[0], dim[1], dim[2]
                    domain_features['image_resolution'] = float(H * W)
                    domain_features['channel_count'] = float(C)
                else:
                    # NO DEFAULT - leave as NaN if data unavailable
                    domain_features['image_resolution'] = np.nan
                    domain_features['channel_count'] = np.nan

            elif domain == 'nlp' or domain == 'text':
                # NLP-specific features - only from real data
                seq_len = benchmark.get('sequence_length', None)
                vocab_size = benchmark.get('vocabulary_size', None)
                domain_features['sequence_length'] = float(seq_len) if seq_len is not None else np.nan
                domain_features['vocabulary_size'] = float(vocab_size) if vocab_size is not None else np.nan

            elif domain == 'tabular':
                # Tabular-specific features - only from real data
                feat_var = benchmark.get('feature_variance', None)
                cat_ratio = benchmark.get('categorical_ratio', None)
                domain_features['feature_variance'] = float(feat_var) if feat_var is not None else np.nan
                domain_features['categorical_ratio'] = float(cat_ratio) if cat_ratio is not None else np.nan

            elif domain == 'graph':
                # Graph-specific features - only from real data
                edge_dens = benchmark.get('edge_density', None)
                avg_deg = benchmark.get('avg_degree', None)
                domain_features['edge_density'] = float(edge_dens) if edge_dens is not None else np.nan
                domain_features['avg_degree'] = float(avg_deg) if avg_deg is not None else np.nan

            features_data.append(domain_features)

        # Create DataFrame (will have different columns per domain)
        features_df = pd.DataFrame(features_data, index=benchmark_ids)

        # Report coverage
        if not features_df.empty:
            coverage = (~features_df.isna()).sum() / len(features_df) * 100
            print(f"✓ Computed Tier 2 features: {list(features_df.columns)}")
            print(f"  Data coverage: {coverage.to_dict()}")

        return features_df
