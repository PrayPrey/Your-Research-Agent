import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset
from transformers import GPT2Tokenizer
from typing import Dict, Literal


class WikiText103Dataset(Dataset):
    """WikiText-103 dataset with GPT-2 tokenization."""

    def __init__(
        self,
        split: Literal["calibration", "validation"],
        cache_dir: str,
        max_length: int = 512
    ):
        self.split = split
        self.max_length = max_length

        # Load tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load dataset
        dataset = load_dataset("wikitext", "wikitext-103-raw-v1", cache_dir=cache_dir)

        # Extract split
        if split == "calibration":
            self.data = dataset["train"].select(range(1000))
        elif split == "validation":
            self.data = dataset["validation"].select(range(200))
        else:
            raise ValueError(f"Unknown split: {split}")

        # Tokenize
        self.data = self.data.map(
            self._tokenize,
            batched=True,
            remove_columns=["text"]
        )
        self.data.set_format(type="torch", columns=["input_ids", "attention_mask"])

    def _tokenize(self, examples):
        return self.tokenizer(
            examples["text"],
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        return {
            "input_ids": self.data[idx]["input_ids"],
            "attention_mask": self.data[idx]["attention_mask"]
        }


def create_dataloader(
    dataset: WikiText103Dataset,
    batch_size: int,
    shuffle: bool = True,
    num_workers: int = 4,
    pin_memory: bool = True
) -> DataLoader:
    """Create DataLoader for WikiText-103 dataset."""
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory
    )
