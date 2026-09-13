"""Load and filter HH-RLHF dataset."""

from typing import List, Dict, Any
import random
from datasets import load_dataset


def load_hh_rlhf(config) -> List[Dict[str, Any]]:
    """
    Load HH-RLHF dataset from Hugging Face.

    Args:
        config: ExperimentConfig with dataset settings

    Returns:
        List of raw conversations
    """
    print(f"Loading dataset: {config.dataset_name} ({config.split} split)...")
    dataset = load_dataset(config.dataset_name, split=config.split)

    # Sample if max_samples is set
    if config.max_samples and len(dataset) > config.max_samples:
        random.seed(config.random_seed)
        indices = random.sample(range(len(dataset)), config.max_samples)
        dataset = dataset.select(indices)
        print(f"Sampled {config.max_samples} conversations from dataset")

    return list(dataset)


def filter_by_turn_count(conversations: List[Dict[str, Any]], min_turns: int) -> List[Dict[str, Any]]:
    """
    Filter conversations by minimum turn count.

    Args:
        conversations: List of raw conversations
        min_turns: Minimum number of turns required

    Returns:
        Filtered list of conversations
    """
    filtered = []

    for conv in conversations:
        turn_count = count_turns(conv["chosen"])
        if turn_count >= min_turns:
            filtered.append(conv)

    print(f"Filtered {len(filtered)} / {len(conversations)} conversations with >= {min_turns} turns")
    return filtered


def count_turns(conversation_text: str) -> int:
    """
    Count turns in HH-RLHF conversation format.

    HH-RLHF format: "\n\nHuman: ... \n\nAssistant: ... \n\nHuman: ..."
    """
    return conversation_text.count("\n\nHuman:")
