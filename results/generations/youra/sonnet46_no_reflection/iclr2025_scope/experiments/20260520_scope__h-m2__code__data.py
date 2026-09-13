import os
from typing import Dict, List, Optional

import torch
from datasets import load_dataset
from torch.utils.data import DataLoader, Dataset
from transformers import PreTrainedTokenizer


GLUE_LABEL_MAPS = {
    "mnli": {"entailment": 0, "neutral": 1, "contradiction": 2},
    "sst2": {0: 0, 1: 1},
    "qnli": {"entailment": 0, "not_entailment": 1},
}

GLUE_NUM_LABELS = {"mnli": 3, "sst2": 2, "qnli": 2}

GLUE_TEXT_FIELDS = {
    "mnli": ("premise", "hypothesis"),
    "sst2": ("sentence", None),
    "qnli": ("question", "sentence"),
}


class GLUEDataset(Dataset):
    def __init__(
        self,
        task_name: str,
        split: str,
        tokenizer: PreTrainedTokenizer,
        max_length: int = 512,
    ) -> None:
        self.task_name = task_name
        self.split = split
        self.tokenizer = tokenizer
        self.max_length = max_length

        hf_split = "validation_matched" if task_name == "mnli" and split == "validation" else split
        raw = load_dataset("nyu-mll/glue", task_name, split=hf_split)
        self.data = self._tokenize(raw)
        self.labels = [ex["label"] for ex in raw]

    def _tokenize(self, raw):
        text_a_field, text_b_field = GLUE_TEXT_FIELDS[self.task_name]
        text_a = [ex[text_a_field] for ex in raw]
        text_b = [ex[text_b_field] for ex in raw] if text_b_field else None
        encodings = self.tokenizer(
            text_a,
            text_b,
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        return encodings

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> Dict:
        return {
            "input_ids": self.data["input_ids"][idx],
            "attention_mask": self.data["attention_mask"][idx],
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
            "task_name": self.task_name,
        }


class LongBenchDataset(Dataset):
    def __init__(self, task_name: str, split: str = "test") -> None:
        self.task_name = task_name
        raw = load_dataset("THUDM/LongBench", task_name, split=split)
        self.data = list(raw)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict:
        ex = self.data[idx]
        return {
            "input": ex.get("input", ex.get("context", "")),
            "answers": ex.get("answers", [ex.get("answer", "")]),
            "task_name": self.task_name,
        }


class DataManager:
    GLUE_TASKS: List[str] = ["mnli", "sst2", "qnli"]
    LONGBENCH_TASKS: List[str] = ["narrativeqa", "qasper", "multifieldqa_en"]

    def __init__(self, tokenizer: PreTrainedTokenizer, training_config) -> None:
        self.tokenizer = tokenizer
        self.training_config = training_config
        self.max_length = training_config.batch_size  # reuse batch_size slot
        # Use config.dataset.max_seq_len_glue if available
        self._max_seq_len = getattr(training_config, "max_seq_len_glue", 512)

    def get_glue_train_loader(self) -> DataLoader:
        datasets = []
        for task in self.GLUE_TASKS:
            ds = GLUEDataset(task, "train", self.tokenizer, self._max_seq_len)
            datasets.append(ds)
        combined = torch.utils.data.ConcatDataset(datasets)
        return DataLoader(
            combined,
            batch_size=self.training_config.batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True,
        )

    def get_glue_val_loaders(self) -> Dict[str, DataLoader]:
        loaders = {}
        for task in self.GLUE_TASKS:
            ds = GLUEDataset(task, "validation", self.tokenizer, self._max_seq_len)
            loaders[task] = DataLoader(ds, batch_size=self.training_config.batch_size, shuffle=False)
        return loaders

    def get_longbench_test_loaders(self) -> Dict[str, DataLoader]:
        loaders = {}
        for task in self.LONGBENCH_TASKS:
            ds = LongBenchDataset(task, split="test")
            loaders[task] = DataLoader(ds, batch_size=1, shuffle=False)
        return loaders
