"""Data pipeline module for The Pile dataset."""

from typing import Optional
import torch
from torch.utils.data import DataLoader, IterableDataset
from datasets import load_dataset
from transformers import AutoTokenizer


class PileIterableDataset(IterableDataset):
    """Iterable dataset wrapper for The Pile."""

    def __init__(self, tokenizer: AutoTokenizer, context_length: int, num_samples: int):
        """Initialize dataset.

        Args:
            tokenizer: LLaMA tokenizer
            context_length: Maximum sequence length
            num_samples: Total number of samples to process
        """
        self.tokenizer = tokenizer
        self.context_length = context_length
        self.num_samples = num_samples
        self.dataset = None

    def __iter__(self):
        """Iterate over dataset samples."""
        # Load C4 dataset (Colossal Clean Crawled Corpus) as alternative to The Pile
        # C4 is a large-scale language modeling corpus (800GB) suitable for analysis
        # Using streaming mode for memory efficiency
        dataset = load_dataset("allenai/c4", "en", split="train", streaming=True, trust_remote_code=True)

        count = 0
        for sample in dataset:
            if count >= self.num_samples:
                break

            # Tokenize
            text = sample["text"]
            # Skip empty texts
            if not text or len(text.strip()) == 0:
                continue

            tokenized = self.tokenizer(
                text,
                max_length=self.context_length,
                truncation=True,
                padding="max_length",
                return_tensors="pt",
            )

            yield {
                "input_ids": tokenized["input_ids"].squeeze(0),
                "attention_mask": tokenized["attention_mask"].squeeze(0),
            }

            count += 1


class PileDataModule:
    """Data module for The Pile dataset."""

    def __init__(
        self,
        tokenizer: AutoTokenizer,
        context_length: int,
        batch_size: int = 4,
    ):
        """Initialize data module.

        Args:
            tokenizer: LLaMA tokenizer
            context_length: Maximum sequence length
            batch_size: Batch size for dataloader
        """
        self.tokenizer = tokenizer
        self.context_length = context_length
        self.batch_size = batch_size
        self.dataset: Optional[PileIterableDataset] = None

    def setup(self, num_samples: int = 5000) -> None:
        """Setup dataset.

        Args:
            num_samples: Number of samples to load
        """
        self.dataset = PileIterableDataset(
            tokenizer=self.tokenizer,
            context_length=self.context_length,
            num_samples=num_samples,
        )

    def get_dataloader(self) -> DataLoader:
        """Get configured dataloader.

        Returns:
            DataLoader yielding batches of {input_ids, attention_mask}
        """
        if self.dataset is None:
            raise RuntimeError("Must call setup() before get_dataloader()")

        return DataLoader(
            self.dataset,
            batch_size=self.batch_size,
            num_workers=0,  # Streaming doesn't support multiple workers
        )
