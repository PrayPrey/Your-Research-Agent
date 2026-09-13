"""Data loading for APPS dataset."""
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from config import MAX_INPUT_LEN, MAX_OUTPUT_LEN, MODEL_NAME, BATCH_SIZE


def load_apps(split: str = "train", n: int = 5000):
    """Load APPS dataset from HuggingFace."""
    from datasets import load_dataset
    ds = load_dataset("codeparrot/apps", split=split, trust_remote_code=True)
    if n and len(ds) > n:
        ds = ds.select(range(n))
    return ds


class APPSDataset(Dataset):
    def __init__(self, data, tokenizer, max_input_len=MAX_INPUT_LEN, max_output_len=MAX_OUTPUT_LEN):
        self.data = data
        self.tokenizer = tokenizer
        self.max_input_len = max_input_len
        self.max_output_len = max_output_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        prompt = item.get("question", item.get("problem", ""))
        solutions = item.get("solutions", "")
        if isinstance(solutions, str):
            import json
            try:
                solutions = json.loads(solutions)
            except:
                solutions = []
        target = solutions[0] if solutions else ""

        inputs = self.tokenizer(
            prompt,
            max_length=self.max_input_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

        if target:
            targets = self.tokenizer(
                target,
                max_length=self.max_output_len,
                truncation=True,
                padding="max_length",
                return_tensors="pt"
            )
            labels = targets["input_ids"].squeeze(0)
        else:
            labels = torch.zeros(self.max_output_len, dtype=torch.long)

        return {
            "input_ids": inputs["input_ids"].squeeze(0),
            "attention_mask": inputs["attention_mask"].squeeze(0),
            "labels": labels,
            "problem_id": idx,
            "test_cases": item.get("input_output", "{}"),
        }


def get_dataloader(split="train", n=5000, batch_size=BATCH_SIZE, shuffle=True):
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    data = load_apps(split, n)
    dataset = APPSDataset(data, tokenizer)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def get_tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_NAME)
