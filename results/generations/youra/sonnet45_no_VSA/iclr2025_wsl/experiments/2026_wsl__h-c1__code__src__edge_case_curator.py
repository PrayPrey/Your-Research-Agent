"""Edge Case Model Curator - validates TIMM availability and assigns family labels"""

import timm
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class EdgeCaseModelCurator:
    def __init__(self, min_models_per_family: int = 3):
        self.min_models_per_family = min_models_per_family

    def validate_availability(
        self,
        edge_case_config: Dict[str, List[str]],
        fallback_config: Dict[str, List[str]] = None
    ) -> Dict[str, List[str]]:
        """Validate TIMM availability for edge case models.

        Args:
            edge_case_config: {family: [model_names]}
            fallback_config: {family: [fallback_model_names]}

        Returns:
            {family: [available_model_names]}. Raises RuntimeError if <min_models_per_family.
        """
        available_models = timm.list_models()
        validated_config = {}
        missing_log = []

        for family, models in edge_case_config.items():
            valid_models = [m for m in models if m in available_models]
            logger.info(f"{family}: {len(valid_models)}/{len(models)} primary models available")

            if len(valid_models) < self.min_models_per_family and fallback_config:
                fallback_needed = self.min_models_per_family - len(valid_models)
                fallbacks = fallback_config.get(family, [])
                fallback_found = [m for m in fallbacks if m in available_models][:fallback_needed]
                if fallback_found:
                    logger.warning(f"{family}: Using {len(fallback_found)} fallback models: {fallback_found}")
                    valid_models.extend(fallback_found)

            missing = [m for m in models if m not in available_models]
            if missing:
                missing_log.append((family, missing))

            if len(valid_models) < self.min_models_per_family:
                raise RuntimeError(
                    f"Cannot find {self.min_models_per_family} models for {family}. "
                    f"Only {len(valid_models)} available: {valid_models}"
                )

            validated_config[family] = valid_models

        # Log summary
        total_available = sum(len(models) for models in validated_config.values())
        logger.info(f"Total edge case models available: {total_available}")

        if missing_log:
            logger.warning(f"Missing models: {missing_log}")

        return validated_config

    def assign_ground_truth_labels(self, model_names: List[str]) -> Dict[str, str]:
        """Assign family labels based on model naming patterns.

        Args:
            model_names: List of TIMM model names

        Returns:
            {model_name: family_label}
        """
        labels = {}
        for model_name in model_names:
            name_lower = model_name.lower()

            if 'nfnet' in name_lower or 'dm_nfnet' in name_lower:
                labels[model_name] = 'NormFree'
            elif 'se' in name_lower and ('resnet' in name_lower or 'senet' in name_lower):
                labels[model_name] = 'SENet'
            elif 'regnet' in name_lower:
                labels[model_name] = 'RegNet'
            elif any(x in name_lower for x in ['vit_giant', 'vit_huge', 'deit_huge', 'beit_large']):
                labels[model_name] = 'ViT-Extreme'
            else:
                logger.warning(f"Could not assign family to {model_name}")
                labels[model_name] = 'Unknown'

        return labels
