"""Checkpoint-only extraction (weights_only=True, no forward pass)"""

import time
import torch
import timm
import pandas as pd
from pathlib import Path
from typing import Dict, List
import logging

from feature_extractor import StatisticalFeatureExtractor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config_h_m3 import CHECKPOINT_CONFIG, MODEL_FAMILIES

logger = logging.getLogger(__name__)


class CheckpointOnlyExtractor:
    """Extract features from checkpoints using weights_only=True"""

    def __init__(self, cache_dir: str = ".cache/checkpoints"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.feature_extractor = StatisticalFeatureExtractor()
        self.weights_only = CHECKPOINT_CONFIG['weights_only']
        self.map_location = CHECKPOINT_CONFIG['map_location']
        self.max_retries = CHECKPOINT_CONFIG['download_retry']

    def extract_batch(self, model_names: List[str]) -> Dict:
        """
        Extract features from checkpoints without model instantiation.

        Args:
            model_names: List of TIMM model names

        Returns:
            {
                'total_time': float,
                'per_model_times': dict[str, float],
                'features': pd.DataFrame,
                'failed_models': list[str]
            }
        """
        start_time = time.perf_counter()
        per_model_times = {}
        features_list = []
        failed_models = []

        for model_name in model_names:
            model_start = time.perf_counter()

            try:
                # Download checkpoint (cached after first run)
                checkpoint_path = self._download_checkpoint(model_name)

                # Load with security flag (weights_only=True)
                state_dict = torch.load(
                    checkpoint_path,
                    weights_only=self.weights_only,
                    map_location=self.map_location
                )

                # Extract features
                features = self.feature_extractor.extract_features(state_dict)
                features['model_name'] = model_name
                features['family'] = self._get_family(model_name)
                features_list.append(features)

                model_end = time.perf_counter()
                per_model_times[model_name] = model_end - model_start

                # Free memory
                del state_dict
                logger.info(f"Extracted {model_name}: {per_model_times[model_name]:.2f}s")

            except Exception as e:
                logger.error(f"Failed to extract {model_name}: {e}")
                failed_models.append(model_name)
                continue

        total_time = time.perf_counter() - start_time

        # Convert to DataFrame
        features_df = pd.DataFrame(features_list)

        return {
            'total_time': total_time,
            'per_model_times': per_model_times,
            'features': features_df,
            'failed_models': failed_models
        }

    def _download_checkpoint(self, model_name: str) -> str:
        """Download TIMM checkpoint if not cached. Returns checkpoint path."""
        checkpoint_path = self.cache_dir / f"{model_name}.pth"

        # If already cached, return it
        if checkpoint_path.exists():
            return str(checkpoint_path)

        # Otherwise, download via timm and save state_dict
        for attempt in range(self.max_retries):
            try:
                # Create model (this downloads checkpoint if needed)
                model = timm.create_model(model_name, pretrained=True)

                # Save state_dict to cache
                torch.save(model.state_dict(), checkpoint_path)

                del model  # Free memory
                logger.info(f"Downloaded and cached checkpoint for {model_name}")
                return str(checkpoint_path)

            except Exception as e:
                logger.warning(f"Download attempt {attempt + 1}/{self.max_retries} failed for {model_name}: {e}")
                if attempt == self.max_retries - 1:
                    raise

        raise RuntimeError(f"Failed to download checkpoint for {model_name} after {self.max_retries} attempts")

    def _get_family(self, model_name: str) -> str:
        """Determine model family from name"""
        for family, models in MODEL_FAMILIES.items():
            if model_name in models:
                return family
        return 'Unknown'
