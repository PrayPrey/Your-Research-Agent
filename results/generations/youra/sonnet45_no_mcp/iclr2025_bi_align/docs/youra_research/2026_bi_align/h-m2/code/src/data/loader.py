"""
Data loading module for HH-RLHF dataset.
Task: task-002 - Implement HH-RLHF dataset loading
"""

from datasets import load_dataset
from typing import Tuple, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_hh_rlhf_harmless(
    dataset_name: str = "Anthropic/hh-rlhf",
    split: str = "train",
    cache_dir: Optional[str] = None
):
    """
    Load HH-RLHF harmless subset.

    Args:
        dataset_name: HuggingFace dataset identifier
        split: Dataset split to load
        cache_dir: Optional cache directory

    Returns:
        Dataset with fields: chosen, rejected
    """
    logger.info(f"Loading {dataset_name} dataset...")
    dataset = load_dataset(dataset_name, split=split, cache_dir=cache_dir)

    # The Anthropic/hh-rlhf dataset is already the harmless subset
    # No filtering needed - the entire dataset contains chosen/rejected pairs
    logger.info(f"Loaded {len(dataset)} pairs")
    return dataset


def extract_response_pairs(
    dataset,
    max_samples: Optional[int] = None
) -> Tuple[List[str], List[str]]:
    """
    Extract chosen and rejected response texts.

    Args:
        dataset: HF Dataset with chosen/rejected fields
        max_samples: Optional limit on number of samples

    Returns:
        (chosen_texts, rejected_texts)
    """
    if max_samples:
        dataset = dataset.select(range(min(max_samples, len(dataset))))

    chosen_texts = [item['chosen'] for item in dataset]
    rejected_texts = [item['rejected'] for item in dataset]

    logger.info(f"Extracted {len(chosen_texts)} chosen and {len(rejected_texts)} rejected texts")

    # Validation
    assert len(chosen_texts) == len(rejected_texts), \
        f"Mismatch: {len(chosen_texts)} chosen vs {len(rejected_texts)} rejected"

    return chosen_texts, rejected_texts
