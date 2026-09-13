"""
TransformerLens Wrapper for H-M2 Hypothesis
Wraps GPT-2 with HookedTransformer for activation extraction
"""

from transformer_lens import HookedTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class TransformerLensWrapper:
    """Wrap GPT-2 with HookedTransformer for activation extraction."""

    def __init__(self, model_id: str = "gpt2", device: str = "cuda"):
        """
        Args:
            model_id: HuggingFace model identifier
            device: Device for model
        """
        self.model_id = model_id
        self.device = device
        self.hooked_model: Optional[HookedTransformer] = None

    def load_baseline_hooked(self) -> HookedTransformer:
        """
        Load GPT-2 as HookedTransformer.

        Returns:
            model with hook points
        """
        logger.info(f"Loading {self.model_id} as HookedTransformer")

        # Load model with TransformerLens
        self.hooked_model = HookedTransformer.from_pretrained(
            self.model_id,
            device=self.device
        )

        logger.info(f"Loaded model with {len(self.get_hook_names())} hook points")

        return self.hooked_model

    def convert_peft_to_hooked(self, peft_model: PeftModel) -> HookedTransformer:
        """
        Convert PEFT model to HookedTransformer.

        Args:
            peft_model: Fine-tuned model with LoRA adapters

        Returns:
            HookedTransformer with merged LoRA weights
        """
        logger.info("Converting PEFT model to HookedTransformer")

        # Merge LoRA weights into base model
        merged_model = peft_model.merge_and_unload()

        # Get state dict
        state_dict = merged_model.state_dict()

        # Load into HookedTransformer
        hooked_model = HookedTransformer.from_pretrained(
            self.model_id,
            device=self.device,
            hf_model=merged_model  # Pass the merged model directly
        )

        logger.info("Conversion complete")

        return hooked_model

    def get_hook_names(self) -> List[str]:
        """
        Get available hook point names.

        Returns:
            List of hook names
        """
        if self.hooked_model is None:
            self.load_baseline_hooked()

        # Get all hook names from the model
        hook_names = list(self.hooked_model.hook_dict.keys())

        return hook_names

    def verify_hooks(self, layers: List[str]) -> bool:
        """
        Verify all required hook points exist.

        Args:
            layers: Layer names to verify

        Returns:
            True if all hooks exist
        """
        available_hooks = set(self.get_hook_names())
        missing_hooks = [layer for layer in layers if layer not in available_hooks]

        if missing_hooks:
            logger.warning(f"Missing hooks: {missing_hooks}")
            return False

        logger.info(f"All {len(layers)} hooks verified")
        return True
