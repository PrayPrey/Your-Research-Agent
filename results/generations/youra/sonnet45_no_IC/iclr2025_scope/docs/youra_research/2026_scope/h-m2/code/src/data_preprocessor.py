"""
Data Preprocessor for H-M2: Reuse h-m1 features and prepare meta-classifier inputs
"""

import sys
from pathlib import Path
from typing import Tuple, List, Dict
import numpy as np
import pandas as pd


class DataPreprocessor:
    """Preprocess H-E1 benchmarks using H-M1 feature computation."""
    
    def __init__(self, h_e1_path: str, h_m1_code_path: str):
        """
        Initialize with paths.
        
        Args:
            h_e1_path: Path to benchmarks_collection.jsonl
            h_m1_code_path: Path to h-m1/code/ directory
        """
        self.h_e1_path = Path(h_e1_path)
        self.h_m1_code_path = Path(h_m1_code_path)
        self._add_h_m1_to_path()
    
    def _add_h_m1_to_path(self):
        """Add h-m1/code to sys.path for imports."""
        if str(self.h_m1_code_path) not in sys.path:
            sys.path.insert(0, str(self.h_m1_code_path))
    
    def load_and_prepare(
        self, 
        nan_threshold: float = 0.7
    ) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
        """
        Load benchmarks and prepare feature matrix + target labels.
        
        Args:
            nan_threshold: Remove features with >threshold fraction of NaN values
        
        Returns:
            X: (N, F) feature matrix, F=4-10 after NaN filtering
            y: (N,) target labels (0=Linear, 1=Polynomial, 2=RNN, 3=Augmentation)
            feature_names: List of feature column names
            benchmark_ids: List of benchmark identifiers
        """
        # Load benchmarks
        benchmarks = self._load_benchmarks()
        print(f"Loaded {len(benchmarks)} benchmarks")
        
        # Compute features
        features_df = self._compute_features(benchmarks)
        print(f"Computed features shape: {features_df.shape}")
        
        # Extract target labels
        y, class_names = self._extract_target_labels(benchmarks)
        print(f"Extracted {len(y)} target labels, {len(set(y))} classes")
        
        # Remove sparse features
        features_df = self._remove_sparse_features(features_df, nan_threshold)
        print(f"After NaN filtering: {features_df.shape}")
        
        # Convert to array and normalize
        X = features_df.values
        X, feature_names = self._normalize_features(X, features_df.columns.tolist())
        
        benchmark_ids = features_df.index.tolist()
        
        return X, y, feature_names, benchmark_ids, class_names
    
    def _load_benchmarks(self) -> List[Dict]:
        """Load from JSONL using h-m1 data loader."""
        from src.data_loader import BenchmarkDataLoader
        loader = BenchmarkDataLoader(str(self.h_e1_path))
        return loader.load_benchmarks()
    
    def _compute_features(self, benchmarks: List[Dict]) -> pd.DataFrame:
        """Compute Tier1+2 features using h-m1 feature computers."""
        from src.feature_computer import Tier1FeatureComputer, Tier2FeatureComputer
        
        tier1_df = Tier1FeatureComputer.compute_features(benchmarks)
        tier2_df = Tier2FeatureComputer.compute_features(benchmarks)
        
        # Combine features
        features_df = pd.concat([tier1_df, tier2_df], axis=1)
        return features_df
    
    def _extract_target_labels(self, benchmarks: List[Dict]) -> Tuple[np.ndarray, List[str]]:
        """
        Extract top-1 method family per benchmark.
        
        Returns:
            y: (N,) integer array
            class_names: List of family names in label order
        """
        family_map = {"Linear": 0, "Polynomial": 1, "RNN": 2, "Augmentation": 3}
        class_names = ["Linear", "Polynomial", "RNN", "Augmentation"]
        
        labels = []
        for b in benchmarks:
            method_rankings = b.get('method_rankings', {})
            
            # Find best method family (lowest percentile = best)
            family_percentiles = {}
            for method, data in method_rankings.items():
                family = data.get('family', 'Unknown')
                percentile = data.get('ranking_percentile', 100)
                if family not in family_percentiles:
                    family_percentiles[family] = []
                family_percentiles[family].append(percentile)
            
            # Average percentile per family
            family_avg = {fam: np.mean(percs) for fam, percs in family_percentiles.items()}
            
            # Best family (lowest avg percentile)
            if family_avg:
                best_family = min(family_avg, key=family_avg.get)
                labels.append(family_map.get(best_family, 0))
            else:
                labels.append(0)  # Default to Linear
        
        return np.array(labels), class_names
    
    def _remove_sparse_features(
        self, 
        features_df: pd.DataFrame, 
        threshold: float = 0.7
    ) -> pd.DataFrame:
        """Remove columns with >threshold fraction of NaN values."""
        nan_fraction = features_df.isna().mean()
        valid_features = nan_fraction[nan_fraction <= threshold].index.tolist()
        return features_df[valid_features]
    
    def _normalize_features(
        self,
        X: np.ndarray,
        feature_names: List[str]
    ) -> Tuple[np.ndarray, List[str]]:
        """Z-score normalize, removing any all-NaN or zero-variance columns."""
        from sklearn.preprocessing import StandardScaler

        # Remove all-NaN columns
        valid_cols = ~np.isnan(X).all(axis=0)
        X_valid = X[:, valid_cols]
        valid_names = [name for i, name in enumerate(feature_names) if valid_cols[i]]

        if X_valid.shape[1] == 0:
            raise ValueError("No valid features remaining after NaN filtering")

        # Fill NaNs with column mean BEFORE checking variance
        col_means = np.nanmean(X_valid, axis=0)
        for i in range(X_valid.shape[1]):
            col_mask = np.isnan(X_valid[:, i])
            if col_mask.any():
                X_valid[col_mask, i] = col_means[i]

        # Check for zero variance AFTER filling NaNs
        col_std = np.std(X_valid, axis=0)
        nonzero_var = col_std > 1e-10
        X_final = X_valid[:, nonzero_var]
        final_names = [name for i, name in enumerate(valid_names) if nonzero_var[i]]

        if X_final.shape[1] == 0:
            print("\n⚠️  WARNING: No features with non-zero variance detected!")
            print("   This indicates insufficient feature diversity in h-e1 dataset.")
            print("   Proceeding with single constant feature for gate evaluation.")
            # Use a constant feature to allow experiment to run and fail at gate
            X_final = np.ones((X_valid.shape[0], 1))
            final_names = ["constant_feature"]

        # Normalize
        scaler = StandardScaler()
        X_normalized = scaler.fit_transform(X_final)

        return X_normalized, final_names
