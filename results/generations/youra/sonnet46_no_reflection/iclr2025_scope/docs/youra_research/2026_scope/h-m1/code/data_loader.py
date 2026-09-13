"""
H-M1 Data Loading: GLUE and LongBench datasets
"""
import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset
from config import ExperimentConfig


def get_num_labels(task: str) -> int:
    return {"mnli": 3, "sst2": 2, "qnli": 2}[task]


class GLUEDataset(Dataset):
    def __init__(self, task: str, split: str, tokenizer, config: ExperimentConfig):
        self.config = config
        self.task = task
        actual_split = split
        if task == "mnli" and split == "validation":
            actual_split = "validation_matched"
        raw = load_dataset("glue", task, split=actual_split)
        # Cap dataset size for PoC feasibility
        max_samples = (config.max_train_samples if split == "train" else config.max_val_samples)
        if len(raw) > max_samples:
            raw = raw.select(range(max_samples))
        self.examples = [self._encode(ex, tokenizer) for ex in raw]
        self.labels = [ex["label"] for ex in raw]

    def _encode(self, ex: dict, tokenizer) -> dict:
        if self.task == "mnli":
            text, text_pair = ex["premise"], ex["hypothesis"]
        elif self.task == "sst2":
            text, text_pair = ex["sentence"], None
        elif self.task == "qnli":
            text, text_pair = ex["question"], ex["sentence"]
        else:
            text, text_pair = str(ex), None

        enc = tokenizer(
            text, text_pair,
            max_length=self.config.max_seq_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {k: v.squeeze(0) for k, v in enc.items()}

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        item = dict(self.examples[idx])
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


class LongBenchDataset(Dataset):
    def __init__(self, task: str, tokenizer, config: ExperimentConfig):
        self.config = config
        self.task = task
        self.tokenizer = tokenizer
        raw = load_dataset("THUDM/LongBench", task, split="test", trust_remote_code=True)
        self.data = list(raw)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        ex = self.data[idx]
        context = ex.get("context", "")
        question = ex.get("input", "")
        answers = ex.get("answers", [])
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        enc = self.tokenizer(
            prompt,
            max_length=self.config.longbench_max_length,
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "answers": answers,
        }


def get_glue_loaders(task: str, tokenizer, config: ExperimentConfig, seed: int):
    train_ds = GLUEDataset(task, "train", tokenizer, config)
    val_ds = GLUEDataset(task, "validation", tokenizer, config)
    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(
        train_ds, batch_size=config.per_device_batch_size,
        shuffle=True, generator=g, num_workers=0, pin_memory=True,
    )
    val_loader = DataLoader(
        val_ds, batch_size=8, shuffle=False, num_workers=0, pin_memory=True,
    )
    return train_loader, val_loader


def get_longbench_loader(task: str, tokenizer, config: ExperimentConfig):
    ds = LongBenchDataset(task, tokenizer, config)
    return DataLoader(ds, batch_size=1, shuffle=False, num_workers=0)
