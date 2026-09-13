"""Data loading for H-M2 DPO experiment."""
from datasets import load_dataset, DatasetDict
import json


def find_common_prefix(chosen: str, rejected: str) -> str:
    """Find common prefix between chosen and rejected (the prompt)."""
    min_len = min(len(chosen), len(rejected))
    prefix_end = 0
    for i in range(min_len):
        if chosen[i] == rejected[i]:
            prefix_end = i + 1
        else:
            break
    prefix = chosen[:prefix_end]
    if "\n\nAssistant:" in prefix:
        last_assistant = prefix.rfind("\n\nAssistant:")
        return chosen[:last_assistant + len("\n\nAssistant:")]
    return prefix


def preprocess_hh_rlhf_dpo(example: dict) -> dict:
    """Convert HH-RLHF format to DPO prompt/chosen/rejected."""
    chosen = example["chosen"]
    rejected = example["rejected"]
    prompt = find_common_prefix(chosen, rejected)
    return {
        "prompt": prompt,
        "chosen": chosen[len(prompt):].strip(),
        "rejected": rejected[len(prompt):].strip(),
    }


def load_hh_rlhf_dpo_splits(cfg, max_train_samples=None) -> DatasetDict:
    """Load HH-RLHF in DPO format with train/val/test splits."""
    dataset = load_dataset("Anthropic/hh-rlhf", split="train")
    dataset = dataset.shuffle(seed=cfg.seed)
    if max_train_samples:
        dataset = dataset.select(range(min(max_train_samples, len(dataset))))
    dataset = dataset.map(preprocess_hh_rlhf_dpo, remove_columns=["chosen", "rejected"])
    dataset = dataset.filter(lambda x: len(x["prompt"]) > 0 and len(x["chosen"]) > 0 and len(x["rejected"]) > 0)
    splits = dataset.train_test_split(test_size=0.1, seed=cfg.seed)
    val_test = splits["test"].train_test_split(test_size=0.5, seed=cfg.seed)
    return DatasetDict({
        "train": splits["train"],
        "validation": val_test["train"],
        "test": val_test["test"],
    })


def sample_test_pairs(dataset, n: int, seed: int) -> list:
    """Sample n (chosen, rejected) pairs from test set."""
    dataset = dataset.shuffle(seed=seed)
    n = min(n, len(dataset))
    pairs = []
    for i in range(n):
        ex = dataset[i]
        chosen = ex["prompt"] + ex["chosen"]
        rejected = ex["prompt"] + ex["rejected"]
        pairs.append((chosen, rejected))
    return pairs


def load_hm1_metrics(cfg) -> dict:
    """Load H-M1 baseline metrics."""
    with open(cfg.hm1_metrics_path, "r") as f:
        return json.load(f)
