from __future__ import annotations
import sys
import os
from typing import Iterator
from config import ExperimentConfig

try:
    from datasets import load_dataset, Dataset, IterableDataset
except ImportError:
    raise ImportError("Install: pip install datasets")

# Socket timeout to prevent infinite HuggingFace download hangs
_HF_STORAGE_OPTS = {"client_kwargs": {"timeout": 60}}


class BenchmarkLoader:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg

    def load_mmlu(self) -> Dataset:
        return load_dataset("cais/mmlu", "all", split="test", trust_remote_code=True)

    def load_hellaswag(self) -> Dataset:
        return load_dataset("Rowan/hellaswag", split="validation", trust_remote_code=True)

    def load_gsm8k(self) -> Dataset:
        return load_dataset("openai/gsm8k", "main", split="test", trust_remote_code=True)

    def load_all_benchmarks(self) -> dict[str, Dataset]:
        return {
            "mmlu": self.load_mmlu(),
            "hellaswag": self.load_hellaswag(),
            "gsm8k": self.load_gsm8k(),
        }

    def get_item_texts(self, dataset: Dataset, name: str) -> list[str]:
        if name == "mmlu":
            return [f"{row['question']} {' '.join(row['choices'])}" for row in dataset]
        elif name == "hellaswag":
            return [f"{row['ctx']} {' '.join(row['endings'])}" for row in dataset]
        elif name == "gsm8k":
            return [f"{row['question']}" for row in dataset]
        else:
            return [str(row) for row in dataset]


class CorpusLoader:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg

    def load_pile(self) -> IterableDataset:
        # Use pile-uncopyrighted subset as PoC proxy for The Pile
        return load_dataset(
            "monology/pile-uncopyrighted", split="train", streaming=True,
            trust_remote_code=True, storage_options=_HF_STORAGE_OPTS,
        )

    def load_c4(self) -> IterableDataset:
        return load_dataset(
            "allenai/c4", "en", split="train", streaming=True,
            trust_remote_code=True, storage_options=_HF_STORAGE_OPTS,
        )

    def load_redpajama(self) -> IterableDataset:
        # FineWeb sample-10BT as PoC proxy for RedPajama (streaming, accessible)
        return load_dataset(
            "HuggingFaceFW/fineweb", "sample-10BT", split="train", streaming=True,
            trust_remote_code=True, storage_options=_HF_STORAGE_OPTS,
        )

    def stream_corpus_texts(self, corpus: IterableDataset, max_docs: int) -> Iterator[str]:
        count = 0
        for item in corpus:
            if count >= max_docs:
                break
            text = item.get("text", item.get("content", item.get("raw_content", "")))
            if text:
                yield text
                count += 1
