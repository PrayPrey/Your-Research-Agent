import torch
from torch.utils.data import Dataset, DataLoader
from transformers import PreTrainedTokenizer
from datasets import load_dataset


class LongAlpacaDataset(Dataset):
    def __init__(self, tokenizer: PreTrainedTokenizer, max_seq_length: int = 32768,
                 split: str = "train"):
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        raw = load_dataset("Yukang/LongAlpaca-12k", split=split)
        self.data = list(raw)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> dict:
        item = self.data[idx]
        instruction = item.get("instruction", "")
        inp = item.get("input", "")
        output = item.get("output", "")

        if inp:
            prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{inp}\n\n### Response:\n{output}"
        else:
            prompt = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"

        encoded = self.tokenizer(
            prompt,
            max_length=self.max_seq_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        input_ids = encoded["input_ids"].squeeze(0)
        attention_mask = encoded["attention_mask"].squeeze(0)
        labels = input_ids.clone()
        # Mask padding tokens in labels
        labels[attention_mask == 0] = -100

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def build_dataloader(tokenizer: PreTrainedTokenizer, max_seq_length: int,
                     batch_size: int, num_workers: int = 4) -> DataLoader:
    dataset = LongAlpacaDataset(tokenizer, max_seq_length=max_seq_length)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )
