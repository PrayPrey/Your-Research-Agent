"""
NLI model wrapper for hallucination detection using DeBERTa-v3-base.
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Tuple
import numpy as np
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


class NLIModel:
    """Wrapper for DeBERTa-v3-base NLI cross-encoder model."""

    def __init__(
        self,
        model_name: str = "cross-encoder/nli-deberta-v3-base",
        device: str = "cuda",
        max_length: int = 512
    ):
        """
        Initialize NLI model with transformers.

        Args:
            model_name: HuggingFace model ID
            device: cuda or cpu
            max_length: Max sequence length
        """
        logger.info(f"Loading NLI model: {model_name} on {device}")
        # Use slow tokenizer to avoid version incompatibility
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
        self.max_length = max_length
        self.label_mapping = ['contradiction', 'entailment', 'neutral']
        logger.info("NLI model loaded successfully")

    def predict(self, pairs: List[Tuple[str, str]], batch_size: int = 16) -> np.ndarray:
        """
        Run NLI inference on (context, claim) pairs.

        Args:
            pairs: List of (context, claim) tuples
            batch_size: Batch size for inference

        Returns:
            scores: (N, 3) array with [contradiction, entailment, neutral] scores
        """
        if not pairs:
            return np.array([])

        logger.info(f"Running NLI inference on {len(pairs)} pairs (batch_size={batch_size})")

        all_probs = []

        try:
            # Process in batches
            for i in tqdm(range(0, len(pairs), batch_size), desc="NLI Inference"):
                batch_pairs = pairs[i:i + batch_size]

                # Tokenize batch
                premises = [p[0] for p in batch_pairs]
                hypotheses = [p[1] for p in batch_pairs]

                inputs = self.tokenizer(
                    premises,
                    hypotheses,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt"
                ).to(self.device)

                # Run inference
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits

                # Apply softmax to get probabilities
                probs = torch.nn.functional.softmax(logits, dim=-1)
                all_probs.append(probs.cpu().numpy())

            # Concatenate all batches
            scores = np.vstack(all_probs)
            return scores

        except RuntimeError as e:
            if "out of memory" in str(e).lower() and batch_size > 4:
                logger.warning(f"OOM error with batch_size={batch_size}. Reducing to {batch_size // 2}")
                torch.cuda.empty_cache()
                return self.predict(pairs, batch_size=batch_size // 2)
            else:
                raise

    def clear_cache(self) -> None:
        """Clear CUDA cache to prevent OOM."""
        if self.device.type == "cuda":
            torch.cuda.empty_cache()
            logger.info("Cleared CUDA cache")
