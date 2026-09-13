"""
NLI Inference Model for H-E1 EXISTENCE PoC.
Wraps cross-encoder/nli-deberta-v3-large for batch hallucination scoring.
"""
import logging
from typing import Dict, List

import numpy as np
import torch
from sentence_transformers import CrossEncoder

from config import ExperimentConfig

logger = logging.getLogger(__name__)


class NLIInferenceModel:
    """
    CrossEncoder wrapper for NLI-based hallucination detection.
    Provides batch inference with inference_mode and dynamic label map verification.
    """

    def __init__(self, config: ExperimentConfig) -> None:
        """Store config; model not loaded until load() is called."""
        self.config = config
        self.model: CrossEncoder = None
        self._contradiction_idx: int = None

    def load(self) -> None:
        """Load CrossEncoder model from HuggingFace Hub."""
        logger.info(f"Loading model: {self.config.model_name}")
        self.model = CrossEncoder(
            self.config.model_name,
            max_length=self.config.max_length,
        )
        logger.info(f"Model loaded successfully.")

    def verify_label_map(self) -> Dict[int, str]:
        """
        Verify id2label, find contradiction index dynamically.

        Returns:
            id2label dict (e.g. {0: 'contradiction', 1: 'entailment', 2: 'neutral'})
        """
        assert self.model is not None, "Call load() before verify_label_map()"

        id2label = self.model.config.id2label

        contradiction_idx = None
        for idx, label in id2label.items():
            if "contradiction" in label.lower():
                contradiction_idx = idx
                break

        if contradiction_idx is None:
            logger.warning(
                "'contradiction' not found in id2label; falling back to index 0"
            )
            contradiction_idx = 0

        logger.info(f"Label map: {id2label}, contradiction_idx={contradiction_idx}")
        self._contradiction_idx = contradiction_idx
        return id2label

    def get_contradiction_index(self) -> int:
        """Return verified index of 'contradiction' class from id2label."""
        assert self._contradiction_idx is not None, (
            "Call verify_label_map() before get_contradiction_index()"
        )
        return self._contradiction_idx

    def predict(
        self,
        premises: List[str],
        hypotheses: List[str],
        batch_size: int = 32,
    ) -> np.ndarray:
        """
        Batch NLI inference with inference_mode and progress logging.

        Args:
            premises: list of str (context / grounding text)
            hypotheses: list of str (response / generated text)
            batch_size: inference batch size (falls back to 16 on OOM)

        Returns:
            scores: np.ndarray shape (N, 3) — softmax probabilities per class
        """
        assert self.model is not None, "Call load() before predict()"

        N = len(premises)
        assert N == len(hypotheses), f"Length mismatch: {N} != {len(hypotheses)}"
        logger.info(f"Running NLI inference: {N} examples, batch_size={batch_size}")

        pairs = list(zip(premises, hypotheses))

        # Run inference with OOM fallback
        current_batch_size = batch_size
        while True:
            try:
                with torch.inference_mode():
                    scores = self.model.predict(
                        pairs,
                        batch_size=current_batch_size,
                        apply_softmax=True,
                        show_progress_bar=True,
                    )
                break
            except RuntimeError as e:
                if "out of memory" in str(e).lower() and current_batch_size > self.config.batch_size_fallback:
                    torch.cuda.empty_cache()
                    current_batch_size = self.config.batch_size_fallback
                    logger.warning(f"OOM detected; retrying with batch_size={current_batch_size}")
                else:
                    raise

        scores = np.array(scores)
        assert scores.shape == (N, 3), f"Unexpected scores shape: {scores.shape}"
        logger.info(f"Inference complete. scores.shape={scores.shape}")
        return scores
