"""
RoBERTa embedding extraction module.
Tasks: task-003, task-004, task-005 - Embedding extraction with checkpoint and GPU management
"""

import torch
import numpy as np
from transformers import RobertaTokenizer, RobertaModel
from typing import List, Tuple, Optional
from pathlib import Path
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RoBERTaEmbeddingExtractor:
    """Extract CLS token embeddings from RoBERTa-base."""

    def __init__(self, model_name: str = "roberta-base", device: str = "cuda"):
        """
        Initialize RoBERTa model.

        Args:
            model_name: HuggingFace model identifier
            device: Device to use (cuda/cpu)
        """
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        self.model = RobertaModel.from_pretrained(model_name)

        # Device management with fallback
        if device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            device = "cpu"

        self.device = device
        self.model.to(self.device)
        self.model.eval()

        logger.info(f"RoBERTa model loaded on {self.device}")

    def extract_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        max_length: int = 512
    ) -> np.ndarray:
        """
        Extract CLS embeddings for a batch of texts.

        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            max_length: Maximum sequence length

        Returns:
            Embeddings array of shape (N, 768)
        """
        if len(texts) == 0:
            return np.array([]).reshape(0, 768)

        all_embeddings = []

        for i in tqdm(range(0, len(texts), batch_size), desc="Extracting embeddings"):
            batch_texts = texts[i:i + batch_size]

            try:
                # Tokenize
                inputs = self.tokenizer(
                    batch_texts,
                    return_tensors="pt",
                    max_length=max_length,
                    truncation=True,
                    padding=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                # Extract embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # CLS token: first token of last hidden state
                    cls_embeddings = outputs.last_hidden_state[:, 0, :]
                    all_embeddings.append(cls_embeddings.cpu().numpy())

            except RuntimeError as e:
                if "out of memory" in str(e):
                    logger.warning(f"OOM at batch size {batch_size}, reducing to {batch_size // 2}")
                    torch.cuda.empty_cache()
                    return self.extract_batch(texts, batch_size=batch_size // 2, max_length=max_length)
                raise

        return np.vstack(all_embeddings)

    def extract_embeddings(
        self,
        chosen_texts: List[str],
        rejected_texts: List[str],
        batch_size: int = 32,
        checkpoint_dir: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract embeddings for both chosen and rejected texts.

        Args:
            chosen_texts: List of chosen responses
            rejected_texts: List of rejected responses
            batch_size: Batch size for processing
            checkpoint_dir: Optional directory for checkpoints

        Returns:
            (chosen_embeddings, rejected_embeddings) both of shape (N, 768)
        """
        # Check for existing checkpoint
        if checkpoint_dir:
            checkpoint_dir = Path(checkpoint_dir)
            chosen_path = checkpoint_dir / "chosen_embeddings.npy"
            rejected_path = checkpoint_dir / "rejected_embeddings.npy"

            if chosen_path.exists() and rejected_path.exists():
                logger.info("Loading embeddings from checkpoint...")
                chosen_emb = np.load(chosen_path)
                rejected_emb = np.load(rejected_path)
                return chosen_emb, rejected_emb

        # Extract chosen embeddings
        logger.info(f"Extracting chosen embeddings ({len(chosen_texts)} samples)...")
        chosen_emb = self.extract_batch(chosen_texts, batch_size=batch_size)

        # Extract rejected embeddings
        logger.info(f"Extracting rejected embeddings ({len(rejected_texts)} samples)...")
        rejected_emb = self.extract_batch(rejected_texts, batch_size=batch_size)

        # Save checkpoint
        if checkpoint_dir:
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            np.save(checkpoint_dir / "chosen_embeddings.npy", chosen_emb)
            np.save(checkpoint_dir / "rejected_embeddings.npy", rejected_emb)
            logger.info(f"Embeddings saved to {checkpoint_dir}")

        return chosen_emb, rejected_emb
