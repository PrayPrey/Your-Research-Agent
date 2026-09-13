import torch
from torch.utils.data import DataLoader, Dataset
from datasets import load_dataset
from typing import Dict
from config import ExperimentConfig


class TokenizedDataset(Dataset):
    def __init__(self, input_ids_list):
        self.input_ids_list = input_ids_list

    def __len__(self):
        return len(self.input_ids_list)

    def __getitem__(self, idx):
        return {"input_ids": self.input_ids_list[idx]}


def load_alpaca_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int = None) -> DataLoader:
    """Load tatsu-lab/alpaca, first 512 samples (seed=42 shuffle), tokenized to max_length."""
    if max_length is None:
        max_length = cfg.max_length
    dataset = load_dataset(cfg.alpaca_dataset, split="train")

    # Shuffle and take first n_samples
    dataset = dataset.shuffle(seed=cfg.seed).select(range(cfg.n_samples))

    input_ids_list = []
    for sample in dataset:
        text = sample.get("text", "") or sample.get("output", "") or ""
        if not text:
            # fallback: combine instruction + output
            instruction = sample.get("instruction", "")
            output = sample.get("output", "")
            text = f"{instruction}\n{output}" if output else instruction

        tokens = tokenizer(
            text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        input_ids_list.append(tokens["input_ids"].squeeze(0))

    ds = TokenizedDataset(input_ids_list)
    return DataLoader(ds, batch_size=cfg.batch_size, shuffle=False)


def load_wikitext_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int = None) -> DataLoader:
    """Load WikiText-103, concatenate and chunk to max_length, first 512 chunks."""
    if max_length is None:
        max_length = cfg.max_length
    dataset = load_dataset(cfg.wikitext_dataset, cfg.wikitext_config, split="test")

    # Concatenate all text
    all_text = " ".join([t for t in dataset["text"] if t.strip()])

    # Tokenize full text
    tokens = tokenizer(
        all_text,
        return_tensors="pt",
        add_special_tokens=False,
    )["input_ids"].squeeze(0)  # shape: (total_tokens,)

    # Split into chunks of max_length
    n_full_chunks = tokens.size(0) // max_length
    chunks = [tokens[i * max_length:(i + 1) * max_length] for i in range(n_full_chunks)]

    # Take first n_samples chunks
    chunks = chunks[:cfg.n_samples]

    ds = TokenizedDataset(chunks)
    return DataLoader(ds, batch_size=cfg.batch_size, shuffle=False)


def load_sst2_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int = None) -> DataLoader:
    """Load SST-2 validation split, first 512 samples, 'text' field."""
    if max_length is None:
        max_length = cfg.max_length
    load_kwargs = {"split": "validation"}
    if cfg.sst2_config_name is not None:
        dataset = load_dataset(cfg.sst2_dataset, cfg.sst2_config_name, **load_kwargs)
    else:
        dataset = load_dataset(cfg.sst2_dataset, **load_kwargs)
    dataset = dataset.select(range(min(cfg.n_samples, len(dataset))))

    input_ids_list = []
    for sample in dataset:
        text = sample.get("text") or sample.get("sentence", "")
        tokens = tokenizer(
            text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        input_ids_list.append(tokens["input_ids"].squeeze(0))

    ds = TokenizedDataset(input_ids_list)
    return DataLoader(ds, batch_size=cfg.batch_size, shuffle=False)


def load_mnli_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int = None) -> DataLoader:
    """Load MNLI validation_matched split, first 512 samples.
    Concatenates: premise + sep_token + hypothesis."""
    if max_length is None:
        max_length = cfg.max_length
    if cfg.mnli_config_name is not None:
        dataset = load_dataset(cfg.mnli_dataset, cfg.mnli_config_name, split=cfg.mnli_split)
    else:
        dataset = load_dataset(cfg.mnli_dataset, split=cfg.mnli_split)
    dataset = dataset.select(range(min(cfg.n_samples, len(dataset))))

    input_ids_list = []
    for sample in dataset:
        premise = sample.get("premise", "") or ""
        hypothesis = sample.get("hypothesis", "") or ""
        text = premise + cfg.sep_token + hypothesis
        tokens = tokenizer(
            text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        input_ids_list.append(tokens["input_ids"].squeeze(0))

    ds = TokenizedDataset(input_ids_list)
    return DataLoader(ds, batch_size=cfg.batch_size, shuffle=False)


def load_all_dataloaders(tokenizer, cfg: ExperimentConfig) -> Dict[str, DataLoader]:
    """Return dict: {alpaca, wikitext, sst2, mnli} -> DataLoader."""
    return {
        "alpaca": load_alpaca_dataloader(tokenizer, cfg, cfg.max_length),
        "wikitext": load_wikitext_dataloader(tokenizer, cfg, cfg.max_length),
        "sst2": load_sst2_dataloader(tokenizer, cfg, cfg.max_length),
        "mnli": load_mnli_dataloader(tokenizer, cfg, cfg.max_length),
    }
