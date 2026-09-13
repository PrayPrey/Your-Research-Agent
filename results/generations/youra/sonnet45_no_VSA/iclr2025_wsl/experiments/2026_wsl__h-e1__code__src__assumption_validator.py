"""Assumption validation for Phase 2A hypotheses"""

import pandas as pd
import numpy as np
import json
import logging
from config import THRESHOLDS, RESNET_MODELS


class AssumptionValidator:
    """Validate A1, A2, A3 assumptions before training"""

    def __init__(self, train_df: pd.DataFrame):
        self.train_df = train_df
        self.logger = logging.getLogger(__name__)
        self.validation_results = {}

    def validate_a1_naming_alignment(self, sample_size: int = 10) -> dict:
        """
        A1: TIMM naming aligns with structure >90%

        Manually verify that CNN models have BatchNorm and Transformers have LayerNorm.
        """
        sample_df = self.train_df.sample(n=min(sample_size, len(self.train_df)), random_state=42)

        aligned = 0
        total = len(sample_df)

        for _, row in sample_df.iterrows():
            family = row['family']
            bn_count = row['bn_count']
            ln_count = row['ln_count']

            # Alignment rules
            if family == 'CNN' and bn_count > ln_count:
                aligned += 1
            elif family == 'Transformer' and ln_count > bn_count:
                aligned += 1
            elif family == 'Hybrid':
                # Hybrid can have mixed patterns
                aligned += 1

        alignment_rate = aligned / total if total > 0 else 0.0
        passed = alignment_rate >= THRESHOLDS['a1_alignment_rate']

        result = {
            'test': 'A1: TIMM Naming Alignment',
            'passed': passed,
            'alignment_rate': alignment_rate,
            'threshold': THRESHOLDS['a1_alignment_rate'],
            'sample_size': total
        }

        self.logger.info(f"A1: alignment_rate={alignment_rate:.2%} (threshold={THRESHOLDS['a1_alignment_rate']:.2%})")
        self.validation_results['a1'] = result
        return result

    def validate_a2_normalization_convention(self) -> dict:
        """
        A2: Normalization convention holds (violation rate ≤15%)

        CNN should have BatchNorm, Transformer should have LayerNorm.
        """
        cnn_df = self.train_df[self.train_df['family'] == 'CNN']
        trans_df = self.train_df[self.train_df['family'] == 'Transformer']

        # CNN with LayerNorm violation
        cnn_ln_violation = sum(cnn_df['ln_count'] > cnn_df['bn_count']) if len(cnn_df) > 0 else 0
        cnn_ln_rate = cnn_ln_violation / len(cnn_df) if len(cnn_df) > 0 else 0.0

        # Transformer with BatchNorm violation
        trans_bn_violation = sum(trans_df['bn_count'] > trans_df['ln_count']) if len(trans_df) > 0 else 0
        trans_bn_rate = trans_bn_violation / len(trans_df) if len(trans_df) > 0 else 0.0

        passed = (cnn_ln_rate <= THRESHOLDS['a2_violation_rate'] and
                 trans_bn_rate <= THRESHOLDS['a2_violation_rate'])

        result = {
            'test': 'A2: Normalization Convention',
            'passed': passed,
            'cnn_ln_violation_rate': cnn_ln_rate,
            'trans_bn_violation_rate': trans_bn_rate,
            'threshold': THRESHOLDS['a2_violation_rate']
        }

        self.logger.info(f"A2: CNN with LN={cnn_ln_rate:.2%}, Trans with BN={trans_bn_rate:.2%} (threshold={THRESHOLDS['a2_violation_rate']:.2%})")
        self.validation_results['a2'] = result
        return result

    def validate_a3_scale_invariance(self, family_models: list = None) -> dict:
        """
        A3: Scale invariance (intra-family CV <0.15)

        Compute coefficient of variation for ResNet family parameter-mass ratio.
        """
        family_models = family_models or RESNET_MODELS

        # Get parameter-mass ratios for specified models
        ratios = []
        for model in family_models:
            model_row = self.train_df[self.train_df['model_name'] == model]
            if not model_row.empty:
                ratios.append(model_row['param_mass_ratio'].values[0])

        if len(ratios) < 2:
            self.logger.warning(f"A3: Insufficient models in train set ({len(ratios)} found)")
            cv = np.inf
            passed = False
        else:
            mean_r = np.mean(ratios)
            std_r = np.std(ratios)
            cv = std_r / mean_r if mean_r > 0 else np.inf

            passed = cv < THRESHOLDS['scale_invariance_cv']

        result = {
            'test': 'A3: Scale Invariance',
            'passed': passed,
            'cv': float(cv),
            'threshold': THRESHOLDS['scale_invariance_cv'],
            'family_models': family_models,
            'ratios': [float(r) for r in ratios]
        }

        self.logger.info(f"A3: CV={cv:.4f} (threshold={THRESHOLDS['scale_invariance_cv']:.4f})")
        self.validation_results['a3'] = result
        return result

    def save_validation_results(self, output_path: str):
        """Save all validation results to JSON"""
        # Convert numpy types to Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.bool_, np.bool8)):
                return bool(obj)
            elif isinstance(obj, (np.integer, np.int_)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float_)):
                return float(obj)
            return obj

        serializable_results = convert_numpy_types(self.validation_results)

        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)

        self.logger.info(f"Saved validation results to {output_path}")
