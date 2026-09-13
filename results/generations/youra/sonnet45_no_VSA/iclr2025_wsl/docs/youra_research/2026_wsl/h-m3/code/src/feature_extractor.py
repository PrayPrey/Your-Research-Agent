"""Feature extraction from model checkpoints (copied from h-m2)"""

import re
import torch
import numpy as np
import sys
import os

# Import config from parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config_h_m3 import NORM_PATTERNS, HEAD_KEYWORDS


class StatisticalFeatureExtractor:
    """Extract statistical features from PyTorch state_dict"""

    def extract_features(self, state_dict: dict) -> dict:
        """
        Extract normalization counts and parameter-mass ratio.

        Args:
            state_dict: PyTorch model state dictionary

        Returns:
            Dictionary with 5 features: bn_count, ln_count, gn_count, no_norm_flag, param_mass_ratio
        """
        if not state_dict:
            raise ValueError("Empty state_dict provided")

        norm_counts = self._count_normalization_layers(state_dict)
        param_mass_ratio = self._compute_param_mass_ratio(state_dict)

        total_norm = norm_counts['bn_count'] + norm_counts['ln_count'] + norm_counts['gn_count']
        no_norm_flag = 1 if total_norm == 0 else 0

        return {
            'bn_count': norm_counts['bn_count'],
            'ln_count': norm_counts['ln_count'],
            'gn_count': norm_counts['gn_count'],
            'no_norm_flag': no_norm_flag,
            'param_mass_ratio': param_mass_ratio
        }

    def _count_normalization_layers(self, state_dict: dict) -> dict:
        """Count normalization layers via regex matching on keys"""
        bn_count = sum(1 for k in state_dict.keys()
                      if re.search(NORM_PATTERNS['bn'], k, re.IGNORECASE))
        ln_count = sum(1 for k in state_dict.keys()
                      if re.search(NORM_PATTERNS['ln'], k, re.IGNORECASE))
        gn_count = sum(1 for k in state_dict.keys()
                      if re.search(NORM_PATTERNS['gn'], k, re.IGNORECASE))

        return {'bn_count': bn_count, 'ln_count': ln_count, 'gn_count': gn_count}

    def _compute_param_mass_ratio(self, state_dict: dict) -> float:
        """
        Compute R = conv_params / (conv_params + linear_params_no_head)

        4D tensors are conv weights, 2D tensors are linear weights.
        Exclude classification head keys.
        """
        conv_params = 0
        linear_params = 0

        for key, tensor in state_dict.items():
            if self._exclude_head_keys(key):
                continue

            if self._is_conv_weight(tensor):
                conv_params += tensor.numel()
            elif self._is_linear_weight(tensor):
                linear_params += tensor.numel()

        total_params = conv_params + linear_params
        if total_params == 0:
            return 0.0

        return conv_params / total_params

    def _is_conv_weight(self, tensor: torch.Tensor) -> bool:
        """Check if tensor is conv weight (4D: [out_ch, in_ch, kH, kW])"""
        return tensor.dim() == 4

    def _is_linear_weight(self, tensor: torch.Tensor) -> bool:
        """Check if tensor is linear weight (2D: [out_feat, in_feat])"""
        return tensor.dim() == 2

    def _exclude_head_keys(self, key: str) -> bool:
        """Check if key belongs to classification head"""
        return any(keyword in key.lower() for keyword in HEAD_KEYWORDS)
