"""
Data loader for HH-RLHF dataset.
"""
from datasets import load_dataset
from datasets.arrow_dataset import Dataset


def load_hh_rlhf_dataset(
    dataset_name: str = "Anthropic/hh-rlhf",
    subset: str = None,
    split: str = "train",
    cache_dir: str = None
) -> Dataset:
    """
    Load HH-RLHF dataset from HuggingFace.

    Args:
        dataset_name: HuggingFace dataset identifier
        subset: Dataset subset (use None for default config)
        split: Data split (train, test)
        cache_dir: Optional cache directory

    Returns:
        HuggingFace Dataset object with rejected responses
        Fields: prompt, chosen, rejected
    """
    if subset is None:
        dataset = load_dataset(dataset_name, split=split, cache_dir=cache_dir)
    else:
        dataset = load_dataset(dataset_name, subset, split=split, cache_dir=cache_dir)
    return dataset
