import torch
from torch.utils.data import DataLoader, Dataset
from datasets import load_dataset
from config import ExperimentConfig


class TokenizedDataset(Dataset):
    def __init__(self, input_ids_list):
        self.input_ids_list = input_ids_list

    def __len__(self):
        return len(self.input_ids_list)

    def __getitem__(self, idx):
        return {"input_ids": self.input_ids_list[idx]}


def load_alpaca_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int) -> DataLoader:
    """Load tatsu-lab/alpaca, first 512 samples (seed=42 shuffle), tokenized to max_length."""
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


def load_wikitext_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int = 512) -> DataLoader:
    """Load WikiText-103, concatenate and chunk to max_length, first 512 chunks."""
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
