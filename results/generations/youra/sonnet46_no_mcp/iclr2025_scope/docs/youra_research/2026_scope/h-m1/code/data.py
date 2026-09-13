"""
data.py — LongBench dataset loading and tokenization for H-M1.

Loads 21 LongBench tasks via HuggingFace datasets.
Middle truncation: keep first 1000 + last 3000 tokens up to max_seq_length=4096.
"""
from __future__ import annotations

import logging
from typing import Dict, Iterator, List, Optional

import torch
from datasets import load_dataset

logger = logging.getLogger(__name__)

LONGBENCH_TASKS: List[str] = [
    "narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh",
    "hotpotqa", "2wikimqa", "musique", "dureader",
    "gov_report", "qmsum", "multi_news", "vcsum",
    "trec", "triviaqa", "samsum", "lsht",
    "passage_count", "passage_retrieval_en", "passage_retrieval_zh",
    "lcc", "repobench-p",
]

LONGBENCH_CATEGORIES: Dict[str, List[str]] = {
    "single-doc-qa": ["narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh"],
    "multi-doc-qa": ["hotpotqa", "2wikimqa", "musique", "dureader"],
    "summarization": ["gov_report", "qmsum", "multi_news", "vcsum"],
    "few-shot": ["trec", "triviaqa", "samsum", "lsht"],
    "synthetic": ["passage_count", "passage_retrieval_en", "passage_retrieval_zh"],
    "code": ["lcc", "repobench-p"],
}

_TASK_TO_CATEGORY: Dict[str, str] = {
    task: cat
    for cat, tasks in LONGBENCH_CATEGORIES.items()
    for task in tasks
}


class LongBenchDataLoader:
    """Load and tokenize LongBench tasks with middle truncation."""

    def __init__(
        self,
        tokenizer,
        max_seq_length: int = 4096,
        tasks: Optional[List[str]] = None,
    ):
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        self.tasks = tasks if tasks is not None else list(LONGBENCH_TASKS)
        self._cache: Dict[str, object] = {}

    def load_task(self, task_name: str):
        """Load a single LongBench task dataset (cached)."""
        if task_name not in self._cache:
            logger.info(f"Loading LongBench task: {task_name}")
            try:
                ds = load_dataset("THUDM/LongBench", task_name, split="test")
            except Exception as e:
                logger.warning(f"Failed to load {task_name}: {e}. Returning empty.")
                ds = []
            self._cache[task_name] = ds
        return self._cache[task_name]

    def get_category_samples(
        self,
        category: str,
        min_samples: int = 500,
    ) -> List[dict]:
        """Aggregate samples across tasks in a category until >= min_samples."""
        task_names = LONGBENCH_CATEGORIES.get(category, [])
        samples: List[dict] = []
        for task_name in task_names:
            if len(samples) >= min_samples:
                break
            ds = self.load_task(task_name)
            for raw in ds:
                if len(samples) >= min_samples:
                    break
                tok = self.tokenize_sample(raw, task_name)
                samples.append(tok)
        return samples

    def tokenize_sample(self, sample: dict, task_name: str) -> dict:
        """Tokenize one sample with middle truncation.

        Keep first 1000 + last 3000 tokens (max_seq_length=4096).
        Returns: {input_ids, attention_mask, task, category, sample_id}
        """
        context = sample.get("context", sample.get("input", ""))
        question = sample.get("input", "")
        text = context if context else question

        tokens = self.tokenizer(
            text,
            add_special_tokens=True,
            return_tensors="pt",
        )
        input_ids = tokens["input_ids"][0]
        attention_mask = tokens["attention_mask"][0]

        # Middle truncation
        if input_ids.shape[0] > self.max_seq_length:
            keep_first = 1000
            keep_last = self.max_seq_length - keep_first
            input_ids = torch.cat([input_ids[:keep_first], input_ids[-keep_last:]])
            attention_mask = torch.cat([
                attention_mask[:keep_first],
                attention_mask[-keep_last:],
            ])

        category = _TASK_TO_CATEGORY.get(task_name, "unknown")
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "task": task_name,
            "category": category,
            "sample_id": sample.get("_id", 0),
        }

    def iter_all_samples(self) -> Iterator[dict]:
        """Yield tokenized samples across all tasks."""
        idx = 0
        for task_name in self.tasks:
            ds = self.load_task(task_name)
            for raw in ds:
                tok = self.tokenize_sample(raw, task_name)
                tok["sample_id"] = idx
                idx += 1
                yield tok
