"""Feature equivalence validation against H-E1 cached features"""

import pandas as pd
import numpy as np
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class FeatureValidator:
    """Validate checkpoint-only features against H-E1 cached baseline"""

    def __init__(self, cached_features_path: str):
        self.cached_features_path = cached_features_path
        self.cached_features = None

    def validate_equivalence(self, checkpoint_features: pd.DataFrame) -> Dict:
        """
        Compare checkpoint-only features against h-e1 cached features.

        Args:
            checkpoint_features: Features from CheckpointOnlyExtractor

        Returns:
            {
                'overall_match': bool,
                'cosine_similarity': float,
                'per_model_similarity': dict[str, float],
                'mismatches': list[dict],
                'mismatch_rate': float
            }
        """
        # Load cached features
        self.cached_features = pd.read_csv(self.cached_features_path)

        per_model_similarity = {}
        mismatches = []

        feature_cols = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

        for idx, row in checkpoint_features.iterrows():
            model_name = row['model_name']

            # Find matching cached row
            cached_row = self.cached_features[self.cached_features['model_name'] == model_name]

            if cached_row.empty:
                logger.warning(f"Model {model_name} not found in cached features")
                mismatches.append({
                    'model_name': model_name,
                    'reason': 'not_found_in_cache',
                    'similarity': 0.0
                })
                continue

            # Extract feature vectors
            checkpoint_vec = row[feature_cols].values.astype(float)
            cached_vec = cached_row[feature_cols].iloc[0].values.astype(float)

            # Compute cosine similarity
            similarity = self._compute_cosine_similarity(checkpoint_vec, cached_vec)
            per_model_similarity[model_name] = similarity

            # Check for mismatch
            if not np.allclose(checkpoint_vec, cached_vec, rtol=1e-5):
                mismatches.append({
                    'model_name': model_name,
                    'checkpoint_features': checkpoint_vec.tolist(),
                    'cached_features': cached_vec.tolist(),
                    'similarity': similarity
                })

        # Overall statistics
        if per_model_similarity:
            overall_similarity = np.mean(list(per_model_similarity.values()))
        else:
            overall_similarity = 0.0

        overall_match = len(mismatches) == 0
        mismatch_rate = len(mismatches) / len(checkpoint_features) if len(checkpoint_features) > 0 else 0.0

        validation_results = {
            'overall_match': overall_match,
            'cosine_similarity': overall_similarity,
            'per_model_similarity': per_model_similarity,
            'mismatches': mismatches,
            'mismatch_rate': mismatch_rate
        }

        logger.info(f"Feature validation: match={overall_match}, similarity={overall_similarity:.4f}, mismatch_rate={mismatch_rate:.2%}")

        return validation_results

    def _compute_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity: dot(v1, v2) / (norm(v1) * norm(v2))"""
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def save_validation_report(self, results: Dict, output_path: str):
        """Save validation results to JSON"""
        # Convert numpy types to Python types for JSON serialization
        results_serializable = {
            'overall_match': bool(results['overall_match']),
            'cosine_similarity': float(results['cosine_similarity']),
            'per_model_similarity': {k: float(v) for k, v in results['per_model_similarity'].items()},
            'mismatches': results['mismatches'],
            'mismatch_rate': float(results['mismatch_rate'])
        }

        with open(output_path, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        logger.info(f"Validation report saved to {output_path}")
