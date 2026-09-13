"""
Representation Analyzer for H-M2 Hypothesis
Extracts pre/post intervention activations using TransformerLens
"""

import torch
from transformer_lens import HookedTransformer, ActivationCache
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ActivationExtractor:
    """Extract activations from TransformerLens HookedTransformer."""

    def __init__(self, model: HookedTransformer, layers: List[str], cache_dir: str):
        """
        Args:
            model: HookedTransformer with hook points
            layers: Layer names to extract (e.g., "blocks.0.attn.hook_pattern")
            cache_dir: Directory to save activations
        """
        self.model = model
        self.layers = layers
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def extract_activations(self, tokens: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Extract activations for all layers.

        Args:
            tokens: Input tokens [N, L]

        Returns:
            Dict mapping layer_name -> activation tensor
        """
        logger.info(f"Extracting activations for {len(self.layers)} layers")

        # Run with cache to extract all activations
        with torch.no_grad():
            _, cache = self.model.run_with_cache(tokens, remove_batch_dim=False)

        # Extract only requested layers
        activations = {}
        for layer_name in self.layers:
            if layer_name in cache:
                # Detach and move to CPU to free GPU memory
                act = cache[layer_name].detach().cpu()
                activations[layer_name] = act
                logger.debug(f"Extracted {layer_name}: shape {act.shape}")
            else:
                logger.warning(f"Layer {layer_name} not found in cache")

        return activations

    def save_activations(self, activations: Dict[str, torch.Tensor], filepath: str):
        """Save activations to disk."""
        save_path = self.cache_dir / filepath
        torch.save(activations, save_path)
        logger.info(f"Saved activations to {save_path}")

    def load_activations(self, filepath: str) -> Dict[str, torch.Tensor]:
        """Load activations from disk."""
        load_path = self.cache_dir / filepath
        activations = torch.load(load_path)
        logger.info(f"Loaded activations from {load_path}")
        return activations


class RepresentationAnalyzer:
    """Analyze representation changes via activation extraction."""

    def __init__(self, config):
        """Initialize representation analyzer."""
        self.config = config
        self.extractor: Optional[ActivationExtractor] = None

    def extract_pre_intervention(
        self,
        model: HookedTransformer,
        eval_tokens: torch.Tensor,
        seed: int
    ) -> Dict[str, torch.Tensor]:
        """
        Extract pre-intervention activations.

        Returns:
            Dict with 24 layers × activations
        """
        logger.info(f"Extracting pre-intervention activations (seed={seed})")

        self.extractor = ActivationExtractor(
            model=model,
            layers=self.config.layers_to_analyze,
            cache_dir=self.config.activation_cache_dir
        )

        activations = self.extractor.extract_activations(eval_tokens)

        # Save to disk
        if self.config.save_activations:
            self.extractor.save_activations(
                activations,
                f"pre_activations_seed{seed}.pt"
            )

        return activations

    def extract_post_intervention(
        self,
        model: HookedTransformer,
        eval_tokens: torch.Tensor,
        seed: int
    ) -> Dict[str, torch.Tensor]:
        """
        Extract post-intervention activations.

        Returns:
            Dict with 24 layers × activations
        """
        logger.info(f"Extracting post-intervention activations (seed={seed})")

        if self.extractor is None:
            self.extractor = ActivationExtractor(
                model=model,
                layers=self.config.layers_to_analyze,
                cache_dir=self.config.activation_cache_dir
            )

        activations = self.extractor.extract_activations(eval_tokens)

        # Save to disk
        if self.config.save_activations:
            self.extractor.save_activations(
                activations,
                f"post_activations_seed{seed}.pt"
            )

        return activations
