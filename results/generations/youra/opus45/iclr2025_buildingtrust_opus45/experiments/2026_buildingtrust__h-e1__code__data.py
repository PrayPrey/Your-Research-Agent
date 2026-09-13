"""
Data module for H-E1 AUROC experiment.

Loads MMLU dataset and formats prompts for MCQ evaluation.
"""

from datasets import load_dataset, Dataset
from typing import Iterator
from config import DATASET_NAME, DATASET_CONFIG, DATASET_SPLIT, PROMPT_TEMPLATE


def load_mmlu_test() -> Dataset:
    """
    Load MMLU test split from HuggingFace.

    Returns:
        Dataset with columns: question, subject, choices, answer (int 0-3)
    """
    dataset = load_dataset(DATASET_NAME, DATASET_CONFIG, split=DATASET_SPLIT)
    return dataset


def format_prompt(sample: dict) -> str:
    """
    Format MMLU sample into MCQ prompt string.

    Args:
        sample: Dict with 'question' and 'choices' keys

    Returns:
        Formatted prompt string ending with 'Answer:'
    """
    choices = sample["choices"]
    return PROMPT_TEMPLATE.format(
        question=sample["question"],
        a=choices[0],
        b=choices[1],
        c=choices[2],
        d=choices[3],
    )


def get_dataloader(dataset: Dataset, start_idx: int = 0) -> Iterator[dict]:
    """
    Create resumable iterator over dataset samples.

    Args:
        dataset: MMLU dataset
        start_idx: Index to start from (for resume)

    Yields:
        Dict with sample data and formatted prompt
    """
    for idx in range(start_idx, len(dataset)):
        sample = dataset[idx]
        yield {
            "idx": idx,
            "question": sample["question"],
            "subject": sample["subject"],
            "choices": sample["choices"],
            "answer": sample["answer"],
            "prompt": format_prompt(sample),
        }
