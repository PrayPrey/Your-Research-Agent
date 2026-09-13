"""C4 data loading for GPT-2 pretraining."""
import torch
from torch.utils.data import DataLoader, IterableDataset
from transformers import GPT2Tokenizer
from datasets import load_dataset
from typing import Iterator, Dict
import time


class C4StreamingDataset(IterableDataset):
    """Streaming C4 dataset with tokenization."""

    def __init__(self, dataset_name: str, subset: str, tokenizer, seq_length: int, split: str):
        super().__init__()
        # Retry logic for network issues
        max_retries = 5
        retry_delay = 15

        for attempt in range(max_retries):
            try:
                # Set environment variable to increase HuggingFace Hub timeout
                import os
                os.environ['HF_HUB_READ_TIMEOUT'] = '180'

                self.dataset = load_dataset(
                    dataset_name,
                    subset,
                    split=split,
                    streaming=True,
                    storage_options={"client_kwargs": {"timeout": 180}}
                )
                print(f"Successfully loaded {dataset_name} {subset} {split}")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Dataset load attempt {attempt + 1}/{max_retries} failed: {e}")
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 120)  # Exponential backoff, max 120s
                else:
                    print(f"All {max_retries} attempts failed. Last error: {e}")
                    raise

        self.tokenizer = tokenizer
        self.seq_length = seq_length

    def __iter__(self) -> Iterator[Dict[str, torch.Tensor]]:
        for example in self.dataset:
            # Tokenize text
            tokens = self.tokenizer(
                example['text'],
                truncation=True,
                max_length=self.seq_length + 1,
                padding='max_length',
                return_tensors='pt'
            )

            input_ids = tokens['input_ids'].squeeze(0)

            # Create input and label sequences (causal LM)
            if len(input_ids) > self.seq_length:
                inputs = input_ids[:self.seq_length]
                labels = input_ids[1:self.seq_length + 1]
            else:
                inputs = input_ids[:-1]
                labels = input_ids[1:]

            yield {
                'input_ids': inputs,
                'labels': labels
            }


class C4DataModule:
    """Data module for C4 dataset."""

    def __init__(self, tokenizer_name: str, seq_length: int, batch_size: int,
                 streaming: bool = True, dataset_name: str = "allenai/c4",
                 subset: str = "en", num_workers: int = 4):
        self.tokenizer_name = tokenizer_name
        self.seq_length = seq_length
        self.batch_size = batch_size
        self.streaming = streaming
        self.dataset_name = dataset_name
        self.subset = subset
        self.num_workers = num_workers
        self.tokenizer = None

    def prepare_data(self) -> None:
        """Load tokenizer."""
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.tokenizer_name)
        # Set pad token to eos token for GPT-2
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def get_train_dataloader(self) -> DataLoader:
        """Create training dataloader."""
        if self.tokenizer is None:
            self.prepare_data()

        train_dataset = C4StreamingDataset(
            self.dataset_name,
            self.subset,
            self.tokenizer,
            self.seq_length,
            split='train'
        )

        return DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            num_workers=0  # Streaming datasets work best with num_workers=0
        )

    def get_val_dataloader(self) -> DataLoader:
        """Create validation dataloader."""
        if self.tokenizer is None:
            self.prepare_data()

        val_dataset = C4StreamingDataset(
            self.dataset_name,
            self.subset,
            self.tokenizer,
            self.seq_length,
            split='validation'
        )

        return DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            num_workers=0
        )


def create_dataloaders(config) -> tuple:
    """Factory function to create train and validation dataloaders."""
    data_module = C4DataModule(
        tokenizer_name=config.data.tokenizer_name,
        seq_length=config.data.seq_length,
        batch_size=config.data.batch_size,
        streaming=config.data.streaming,
        dataset_name=config.data.dataset_name,
        subset=config.data.subset,
        num_workers=config.data.num_workers
    )

    data_module.prepare_data()
    train_loader = data_module.get_train_dataloader()
    val_loader = data_module.get_val_dataloader()

    return train_loader, val_loader
