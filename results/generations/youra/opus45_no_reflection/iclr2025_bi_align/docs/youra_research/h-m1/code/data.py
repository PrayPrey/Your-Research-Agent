"""Data loading and preprocessing for BiDPO training."""
import torch
from datasets import Dataset, load_dataset
from torch.utils.data import DataLoader
from transformers import PreTrainedTokenizer
from collab_score import compute_collab_score_v2
from config import CONFIG


def load_hh_rlhf(split: str, max_samples: int = None) -> Dataset:
    dataset = load_dataset(CONFIG.dataset_name, split=split)
    if max_samples and len(dataset) > max_samples:
        dataset = dataset.shuffle(seed=CONFIG.seed).select(range(max_samples))
    return dataset


def extract_response(text: str) -> str:
    """Extract assistant response from HH-RLHF format."""
    parts = text.split("\n\nAssistant: ")
    if len(parts) > 1:
        return parts[-1].strip()
    return text.strip()


def tokenize_pair(example: dict, tokenizer: PreTrainedTokenizer) -> dict:
    chosen_text = example["chosen"]
    rejected_text = example["rejected"]

    chosen_enc = tokenizer(
        chosen_text,
        max_length=CONFIG.max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    rejected_enc = tokenizer(
        rejected_text,
        max_length=CONFIG.max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )

    return {
        "chosen_input_ids": chosen_enc["input_ids"].squeeze(0),
        "chosen_attention_mask": chosen_enc["attention_mask"].squeeze(0),
        "rejected_input_ids": rejected_enc["input_ids"].squeeze(0),
        "rejected_attention_mask": rejected_enc["attention_mask"].squeeze(0),
    }


def add_collab_scores(dataset: Dataset) -> Dataset:
    def compute_scores(example):
        chosen_response = extract_response(example["chosen"])
        rejected_response = extract_response(example["rejected"])
        return {
            "chosen_collab_score": compute_collab_score_v2(chosen_response),
            "rejected_collab_score": compute_collab_score_v2(rejected_response),
        }

    return dataset.map(compute_scores, num_proc=4)


def collate_fn(batch: list, tokenizer: PreTrainedTokenizer) -> dict:
    chosen_ids = []
    chosen_masks = []
    rejected_ids = []
    rejected_masks = []
    chosen_scores = []
    rejected_scores = []

    for item in batch:
        enc = tokenize_pair(item, tokenizer)
        chosen_ids.append(enc["chosen_input_ids"])
        chosen_masks.append(enc["chosen_attention_mask"])
        rejected_ids.append(enc["rejected_input_ids"])
        rejected_masks.append(enc["rejected_attention_mask"])
        chosen_scores.append(item["chosen_collab_score"])
        rejected_scores.append(item["rejected_collab_score"])

    return {
        "chosen_input_ids": torch.stack(chosen_ids),
        "chosen_attention_mask": torch.stack(chosen_masks),
        "rejected_input_ids": torch.stack(rejected_ids),
        "rejected_attention_mask": torch.stack(rejected_masks),
        "chosen_collab_score": torch.tensor(chosen_scores, dtype=torch.float32),
        "rejected_collab_score": torch.tensor(rejected_scores, dtype=torch.float32),
    }


def get_dataloader(dataset: Dataset, tokenizer: PreTrainedTokenizer, batch_size: int) -> DataLoader:
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=lambda batch: collate_fn(batch, tokenizer),
        num_workers=2,
        pin_memory=True,
    )
