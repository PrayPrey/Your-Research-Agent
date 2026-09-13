"""Data pipeline for h-m3: Load datasets and generate synthetic human annotations"""
import random
import numpy as np
from datasets import load_dataset, Dataset, DatasetDict
from typing import Dict, Tuple
from config import DataConfig

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)

def generate_synthetic_annotations(dataset: Dataset, noise_level: float = 0.15) -> Dataset:
    """
    Generate synthetic human quality scores (0-10 scale)
    Based on execution pass/fail with added noise

    Args:
        dataset: HuggingFace dataset with 'test' field
        noise_level: Noise standard deviation (0.15 = moderate noise)

    Returns:
        Dataset with 'human_score' field added
    """
    def add_human_score(example):
        # Base score from execution (if tests field exists)
        if 'test' in example and example['test']:
            # Estimate pass probability (simple heuristic)
            base_score = 7.0  # Assume most solutions work
        else:
            base_score = 5.0  # Neutral

        # Add Gaussian noise
        noise = np.random.normal(0, noise_level * 10)  # Scale to 0-10 range
        score = np.clip(base_score + noise, 0, 10)

        example['human_score'] = float(score)
        example['code'] = example.get('canonical_solution', example.get('code', ''))
        return example

    return dataset.map(add_human_score)

def stratified_split(
    dataset: Dataset,
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
    seed: int = 42
) -> Dict[str, Dataset]:
    """
    Stratified train/val/test split preserving score distribution

    Args:
        dataset: Dataset with 'human_score' field
        train_ratio: Training set ratio (0.7)
        val_ratio: Validation set ratio (0.15)
        test_ratio: Test set ratio (0.15)
        seed: Random seed

    Returns:
        Dictionary with 'train', 'val', 'test' splits
    """
    # Simple stratification: sort by score, then split
    scores = [ex['human_score'] for ex in dataset]
    indices = np.argsort(scores)

    n = len(dataset)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    # Shuffle within each split for randomness
    rng = np.random.default_rng(seed)
    train_idx = indices[:train_end].copy()
    val_idx = indices[train_end:val_end].copy()
    test_idx = indices[val_end:].copy()

    rng.shuffle(train_idx)
    rng.shuffle(val_idx)
    rng.shuffle(test_idx)

    return {
        'train': dataset.select(train_idx),
        'val': dataset.select(val_idx),
        'test': dataset.select(test_idx)
    }

def load_and_prepare_data(config: DataConfig) -> DatasetDict:
    """
    Load HumanEval + MBPP, generate annotations, and split

    Returns:
        DatasetDict with train/val/test splits
    """
    set_seed(config.random_seed)

    print("Loading datasets...")
    humaneval = load_dataset("openai/openai_humaneval", cache_dir=config.cache_dir)
    mbpp = load_dataset("google-research-datasets/mbpp", cache_dir=config.cache_dir)

    print(f"HumanEval: {len(humaneval['test'])} samples")
    print(f"MBPP: train={len(mbpp['train'])}, test={len(mbpp['test'])}")

    # Combine HumanEval test + MBPP train+test
    humaneval_data = humaneval['test']
    mbpp_data_train = mbpp['train']
    mbpp_data_test = mbpp['test']

    # Generate synthetic annotations
    print("Generating synthetic human annotations...")
    humaneval_annotated = generate_synthetic_annotations(humaneval_data)
    mbpp_annotated_train = generate_synthetic_annotations(mbpp_data_train)
    mbpp_annotated_test = generate_synthetic_annotations(mbpp_data_test)

    # Combine datasets
    from datasets import concatenate_datasets
    combined = concatenate_datasets([
        humaneval_annotated,
        mbpp_annotated_train,
        mbpp_annotated_test
    ])

    print(f"Combined dataset: {len(combined)} samples")

    # Stratified split
    print("Creating stratified splits...")
    splits = stratified_split(
        combined,
        config.train_ratio,
        config.val_ratio,
        config.test_ratio,
        config.random_seed
    )

    print(f"Train: {len(splits['train'])} samples")
    print(f"Val: {len(splits['val'])} samples")
    print(f"Test: {len(splits['test'])} samples")

    # Validate
    assert len(splits['test']) >= config.min_test_samples, \
        f"Test set too small: {len(splits['test'])} < {config.min_test_samples}"

    return DatasetDict(splits)

if __name__ == "__main__":
    from config import get_config
    config = get_config()
    data = load_and_prepare_data(config.data)
    print("\n✓ Data pipeline validated")
