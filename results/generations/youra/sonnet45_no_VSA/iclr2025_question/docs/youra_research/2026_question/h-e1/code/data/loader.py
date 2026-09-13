"""
Data loading and preprocessing for TruthfulQA and WritingPrompts datasets.
"""

from datasets import load_dataset
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class TruthfulQALoader:
    """Load TruthfulQA dataset for factual domain analysis."""

    def __init__(self, cache_dir: str):
        """
        Initialize TruthfulQA loader.

        Args:
            cache_dir: Directory to cache downloaded dataset
        """
        self.cache_dir = cache_dir

    def load(self) -> List[Dict[str, str]]:
        """
        Load and format TruthfulQA dataset.

        Returns:
            List of dicts with keys: question, best_answer, context
            Length: 817 samples
        """
        logger.info("Loading TruthfulQA dataset...")
        dataset = load_dataset(
            "truthfulqa/truthful_qa",
            "generation",
            split="validation",
            cache_dir=self.cache_dir
        )

        samples = []
        for idx, item in enumerate(dataset):
            # Use question as context and best_answer as response to verify
            sample = {
                "id": idx,
                "context": item["question"],
                "response": item["best_answer"],
                "domain": "factual"
            }
            samples.append(sample)

        logger.info(f"Loaded {len(samples)} TruthfulQA samples")
        return samples


class WritingPromptsLoader:
    """Load WritingPrompts dataset for creative domain analysis."""

    def __init__(self, cache_dir: str, sample_size: int = 817, seed: int = 42):
        """
        Initialize WritingPrompts loader with sampling.

        Args:
            cache_dir: Directory to cache downloaded dataset
            sample_size: Number of samples to subsample
            seed: Random seed for reproducible sampling
        """
        self.cache_dir = cache_dir
        self.sample_size = sample_size
        self.seed = seed

    def load(self) -> List[Dict[str, str]]:
        """
        Load and subsample WritingPrompts dataset.

        Returns:
            List of dicts with keys: prompt, story, context
            Length: ~817 samples
        """
        logger.info("Loading WritingPrompts dataset...")
        dataset = load_dataset(
            "euclaise/writingprompts",
            split="train",
            cache_dir=self.cache_dir
        )

        # Subsample to match TruthfulQA size
        dataset = dataset.shuffle(seed=self.seed).select(range(min(self.sample_size, len(dataset))))

        samples = []
        for idx, item in enumerate(dataset):
            # Use prompt as context and story as response to verify
            sample = {
                "id": idx,
                "context": item["prompt"],
                "response": item["story"],
                "domain": "creative"
            }
            samples.append(sample)

        logger.info(f"Loaded {len(samples)} WritingPrompts samples")
        return samples


def decompose_claims(text: str, method: str = "nltk", max_claims: int = 20, min_length: int = 10) -> List[str]:
    """
    Decompose text into claims using sentence tokenization.

    Args:
        text: Input text
        method: Tokenization method (default: nltk)
        max_claims: Maximum claims to extract
        min_length: Minimum claim length in characters

    Returns:
        List of claim strings (sentences)
    """
    if method == "nltk":
        try:
            import nltk
            # Try to download punkt if not available
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                logger.info("Downloading NLTK punkt tokenizer...")
                nltk.download('punkt', quiet=True)

            claims = nltk.sent_tokenize(text)
        except Exception as e:
            logger.warning(f"NLTK tokenization failed: {e}. Falling back to simple split.")
            # Fallback: split by period
            claims = [s.strip() + '.' for s in text.split('.') if s.strip()]
    else:
        # Fallback method: split by period
        claims = [s.strip() + '.' for s in text.split('.') if s.strip()]

    # Filter by minimum length and truncate to max_claims
    claims = [c for c in claims if len(c) >= min_length][:max_claims]

    return claims
