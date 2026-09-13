"""H-E1 Data Pipeline - C4 Streaming"""
import torch
from datasets import load_dataset
from torch.utils.data import IterableDataset, DataLoader
from transformers import AutoTokenizer
from config import ExperimentConfig


class C4StreamDataset(IterableDataset):
    def __init__(self, config: ExperimentConfig, tokenizer):
        self.config = config
        self.tokenizer = tokenizer
        self.dataset = load_dataset(
            config.dataset_name,
            config.dataset_subset,
            split="train",
            streaming=True,
            trust_remote_code=True
        )

    def __iter__(self):
        for example in self.dataset:
            text = example["text"]
            tokens = self.tokenizer(
                text,
                max_length=self.config.seq_len,
                truncation=True,
                padding="max_length",
                return_tensors="pt"
            )
            yield {
                "input_ids": tokens["input_ids"].squeeze(0),
                "attention_mask": tokens["attention_mask"].squeeze(0)
            }


def get_dataloader(config: ExperimentConfig, tokenizer) -> DataLoader:
    dataset = C4StreamDataset(config, tokenizer)
    return DataLoader(
        dataset,
        batch_size=config.batch_size,
        num_workers=0,
        pin_memory=True
    )


def get_tokenizer(config: ExperimentConfig):
    tokenizer = AutoTokenizer.from_pretrained(config.teacher_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer
