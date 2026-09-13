"""Data loading and preprocessing for H-M1."""
from datasets import load_dataset, DatasetDict
import random


def load_hh_rlhf_splits(cfg, tokenizer):
    """Load HH-RLHF dataset with train/val/test splits."""
    ds = load_dataset("Anthropic/hh-rlhf")
    train_data = ds["train"]

    # 90/5/5 split
    split1 = train_data.train_test_split(test_size=0.10, seed=cfg.seed)
    train_ds = split1["train"]
    temp = split1["test"]
    split2 = temp.train_test_split(test_size=0.50, seed=cfg.seed)
    val_ds = split2["train"]
    test_ds = split2["test"]

    return DatasetDict({
        "train": train_ds,
        "validation": val_ds,
        "test": test_ds,
    })


def preprocess_for_reward_trainer(examples, tokenizer, max_length=512):
    """Tokenize chosen/rejected pairs for TRL RewardTrainer."""
    tokenized_chosen = tokenizer(
        examples["chosen"],
        truncation=True,
        max_length=max_length,
        padding="max_length",
    )
    tokenized_rejected = tokenizer(
        examples["rejected"],
        truncation=True,
        max_length=max_length,
        padding="max_length",
    )
    return {
        "input_ids_chosen": tokenized_chosen["input_ids"],
        "attention_mask_chosen": tokenized_chosen["attention_mask"],
        "input_ids_rejected": tokenized_rejected["input_ids"],
        "attention_mask_rejected": tokenized_rejected["attention_mask"],
    }


def sample_test_pairs(dataset, n: int, seed: int):
    """Sample n (chosen, rejected) text pairs from dataset."""
    random.seed(seed)
    indices = random.sample(range(len(dataset)), min(n, len(dataset)))
    pairs = []
    for i in indices:
        example = dataset[i]
        pairs.append((example["chosen"], example["rejected"]))
    return pairs
