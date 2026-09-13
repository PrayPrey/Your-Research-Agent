"""Data loader for MCQ benchmarks: MMLU, TruthfulQA, ARC-Challenge."""

import os
from datasets import load_dataset
from config import DATASETS


class MCQDataLoader:
    """Load and format MCQ benchmark datasets."""

    def __init__(self, dataset_cfg: dict):
        self.cfg = dataset_cfg
        self._data = None

    def load(self) -> list[dict]:
        """Load dataset and return list of normalized items."""
        ds = load_dataset(
            self.cfg["hf_id"],
            self.cfg["config"],
            split=self.cfg["split"],
            trust_remote_code=True,
        )
        items = []
        name = self.cfg["name"]

        for row in ds:
            item = self._normalize(row, name)
            if item is not None:
                items.append(item)
        self._data = items
        return items

    def _normalize(self, row: dict, name: str) -> dict | None:
        """Normalize dataset row to {question, choices, answer_idx}."""
        if name == "mmlu":
            choices = row["choices"]  # list of 4 strings
            answer_idx = row["answer"]  # int 0-3
            return {"question": row["question"], "choices": choices, "answer_idx": int(answer_idx)}

        elif name == "truthfulqa":
            mc = row.get("mc1_targets") or {}
            choices = mc.get("choices", [])
            labels = mc.get("labels", [])
            if len(choices) < 2:
                return None
            # Pad/trim to 4 choices for uniform option extraction
            choices = (choices + ["[N/A]", "[N/A]", "[N/A]", "[N/A]"])[:4]
            answer_idx = labels.index(1) if 1 in labels else 0
            answer_idx = min(answer_idx, 3)
            return {"question": row["question"], "choices": choices, "answer_idx": int(answer_idx)}

        elif name == "arc":
            choices_dict = row["choices"]
            choices = choices_dict["text"]
            labels = choices_dict["label"]
            # Map label (A/B/C/D or 1/2/3/4) to index
            answer_label = row["answerKey"]
            label_to_idx = {}
            for i, lbl in enumerate(labels):
                label_to_idx[lbl] = i
            answer_idx = label_to_idx.get(answer_label, 0)
            # Pad to 4
            choices = (choices + ["[N/A]", "[N/A]", "[N/A]", "[N/A]"])[:4]
            return {"question": row["question"], "choices": choices, "answer_idx": int(answer_idx)}

        return None

    def format_prompt(self, item: dict) -> str:
        """Format MCQ item as multiple-choice prompt."""
        q = item["question"]
        c = item["choices"]
        labels = ["A", "B", "C", "D"]
        lines = [f"Question: {q}"]
        for i, (lbl, choice) in enumerate(zip(labels, c[:4])):
            lines.append(f"{lbl}: {choice}")
        lines.append("Answer:")
        return "\n".join(lines)

    def get_option_tokens(self, tokenizer) -> list[int]:
        """Return token IDs for [' A', ' B', ' C', ' D']."""
        token_ids = []
        for label in [" A", " B", " C", " D"]:
            ids = tokenizer.encode(label, add_special_tokens=False)
            token_ids.append(ids[-1])  # Take last token for multi-token labels
        return token_ids


def load_all_datasets(dataset_cfgs: list[dict] = None) -> dict[str, list[dict]]:
    """Load all datasets, return dict keyed by name."""
    if dataset_cfgs is None:
        dataset_cfgs = DATASETS
    result = {}
    for cfg in dataset_cfgs:
        print(f"Loading dataset: {cfg['name']} ({cfg['hf_id']})")
        loader = MCQDataLoader(cfg)
        items = loader.load()
        result[cfg["name"]] = items
        print(f"  -> {len(items)} items loaded")
    return result
