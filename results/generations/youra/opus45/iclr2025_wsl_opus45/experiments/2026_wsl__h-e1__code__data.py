"""
Dataset Preparation Module for H-E1

Handles loading, formatting, and tokenizing datasets for LoRA training.
"""

from datasets import load_dataset, Dataset
from transformers import AutoTokenizer
from typing import Optional

from config import DATASETS, TRAIN_CONFIG


def format_example(task_name: str, example: dict) -> str:
    """
    Format a single example as instruction prompt string.

    Args:
        task_name: Name of the task (e.g., "gsm8k", "mnli")
        example: Raw example dict from HuggingFace dataset

    Returns:
        Formatted instruction prompt string
    """
    if task_name == "gsm8k":
        question = example.get("question", "")
        answer = example.get("answer", "")
        return f"Question: {question}\nAnswer: {answer}"

    elif task_name == "arc":
        question = example.get("question", "")
        choices = example.get("choices", {})
        answer_key = example.get("answerKey", "")
        choice_texts = choices.get("text", []) if isinstance(choices, dict) else []
        choice_labels = choices.get("label", []) if isinstance(choices, dict) else []
        choices_str = "\n".join([f"{l}: {t}" for l, t in zip(choice_labels, choice_texts)])
        return f"Question: {question}\nChoices:\n{choices_str}\nAnswer: {answer_key}"

    elif task_name == "logiqa":
        # hails/agieval-logiqa-en format
        query = example.get("query", example.get("question", ""))
        choices = example.get("choices", [])
        answer = example.get("gold", example.get("answer", ""))
        if isinstance(choices, list):
            choices_str = "\n".join([f"{i}: {c}" for i, c in enumerate(choices)])
        else:
            choices_str = str(choices)
        return f"Question: {query}\nChoices:\n{choices_str}\nAnswer: {answer}"

    elif task_name == "strategyqa":
        question = example.get("question", "")
        answer = example.get("answer", example.get("label", ""))
        return f"Question: {question}\nAnswer: {answer}"

    elif task_name == "mnli":
        premise = example.get("premise", "")
        hypothesis = example.get("hypothesis", "")
        label = example.get("label", "")
        label_map = {0: "entailment", 1: "neutral", 2: "contradiction"}
        label_str = label_map.get(label, str(label))
        return f"Premise: {premise}\nHypothesis: {hypothesis}\nRelation: {label_str}"

    elif task_name == "qqp":
        q1 = example.get("text1", example.get("question1", ""))
        q2 = example.get("text2", example.get("question2", ""))
        label = example.get("label", "")
        label_str = "duplicate" if label == 1 else "not duplicate"
        return f"Question 1: {q1}\nQuestion 2: {q2}\nAre these duplicates? {label_str}"

    elif task_name == "sst2":
        text = example.get("text", example.get("sentence", ""))
        label = example.get("label", "")
        label_str = "positive" if label == 1 else "negative"
        return f"Text: {text}\nSentiment: {label_str}"

    elif task_name == "mrpc":
        s1 = example.get("text1", example.get("sentence1", ""))
        s2 = example.get("text2", example.get("sentence2", ""))
        label = example.get("label", "")
        label_str = "paraphrase" if label == 1 else "not paraphrase"
        return f"Sentence 1: {s1}\nSentence 2: {s2}\nAre these paraphrases? {label_str}"

    else:
        # Generic fallback
        return str(example)


def load_and_format_dataset(
    task_name: str,
    max_samples: Optional[int] = None
) -> Dataset:
    """
    Load HuggingFace dataset for task_name, format as text prompts.

    Args:
        task_name: Name of the task (must be key in DATASETS)
        max_samples: Maximum number of samples to load (default from TRAIN_CONFIG)

    Returns:
        Dataset with 'text' column containing formatted prompts
    """
    if max_samples is None:
        max_samples = TRAIN_CONFIG["max_samples"]

    if task_name not in DATASETS:
        raise ValueError(f"Unknown task: {task_name}. Available: {list(DATASETS.keys())}")

    dataset_id, config_name = DATASETS[task_name]

    # Load dataset - try train split first, then test
    try:
        if config_name:
            ds = load_dataset(dataset_id, config_name, split="train")
        else:
            ds = load_dataset(dataset_id, split="train")
    except Exception:
        # Fallback to test split for some datasets
        try:
            if config_name:
                ds = load_dataset(dataset_id, config_name, split="test")
            else:
                ds = load_dataset(dataset_id, split="test")
        except Exception as e:
            raise RuntimeError(f"Failed to load dataset {task_name}: {e}")

    # Limit samples
    if len(ds) > max_samples:
        ds = ds.shuffle(seed=42).select(range(max_samples))

    # Format examples
    def format_fn(example):
        return {"text": format_example(task_name, example)}

    ds = ds.map(format_fn, remove_columns=ds.column_names)

    return ds


def tokenize_dataset(
    dataset: Dataset,
    tokenizer: AutoTokenizer,
    max_length: Optional[int] = None
) -> Dataset:
    """
    Tokenize dataset for causal language modeling.

    Args:
        dataset: Dataset with 'text' column
        tokenizer: HuggingFace tokenizer
        max_length: Maximum sequence length (default from TRAIN_CONFIG)

    Returns:
        Dataset with 'input_ids', 'attention_mask', 'labels' columns
    """
    if max_length is None:
        max_length = TRAIN_CONFIG["max_length"]

    # Ensure pad token is set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tokenize_fn(examples):
        tokenized = tokenizer(
            examples["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors=None,
        )
        # For causal LM, labels = input_ids
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    tokenized_ds = dataset.map(
        tokenize_fn,
        batched=True,
        remove_columns=dataset.column_names,
    )

    return tokenized_ds


if __name__ == "__main__":
    # Quick test
    print("Testing data loading...")
    for task in ["gsm8k", "sst2"]:
        ds = load_and_format_dataset(task, max_samples=10)
        print(f"{task}: {len(ds)} samples")
        print(f"  Example: {ds[0]['text'][:100]}...")
