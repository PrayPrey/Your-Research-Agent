"""Load and format benchmark test sets for min-k% scoring."""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkItem:
    benchmark: str
    item_id: int
    text: str          # question + answer concatenated
    token_count: int   # -1 until tokenized
    valid: bool        # True if token_count >= MIN_SEQ_LEN after tokenization


def _format_mmlu(example: dict, idx: int) -> BenchmarkItem:
    choices = example.get("choices", [])
    answer_idx = example.get("answer", 0)
    if isinstance(answer_idx, str):
        answer_idx = ord(answer_idx) - ord("A")
    answer_text = choices[answer_idx] if 0 <= answer_idx < len(choices) else ""
    text = f"{example.get('question', '')} {answer_text}"
    return BenchmarkItem("mmlu", idx, text.strip(), -1, True)


def _format_hellaswag(example: dict, idx: int) -> BenchmarkItem:
    ctx = example.get("ctx", "")
    endings = example.get("endings", [])
    label = int(example.get("label", 0))
    ending = endings[label] if 0 <= label < len(endings) else ""
    text = f"{ctx} {ending}".strip()
    return BenchmarkItem("hellaswag", idx, text, -1, True)


def _format_arc(example: dict, idx: int) -> BenchmarkItem:
    q = example.get("question", "")
    choices = example.get("choices", {})
    labels = choices.get("label", [])
    texts_list = choices.get("text", [])
    answer_key = example.get("answerKey", "A")
    answer_text = ""
    for lab, txt in zip(labels, texts_list):
        if lab == answer_key:
            answer_text = txt
            break
    text = f"{q} {answer_text}".strip()
    return BenchmarkItem("arc_challenge", idx, text, -1, True)


def _format_winogrande(example: dict, idx: int) -> BenchmarkItem:
    sentence = example.get("sentence", "")
    answer = example.get("answer", "1")
    opt_key = f"option{answer}"
    option = example.get(opt_key, "")
    text = sentence.replace("_", option).strip()
    return BenchmarkItem("winogrande", idx, text, -1, True)


FORMATTERS = {
    "mmlu": _format_mmlu,
    "hellaswag": _format_hellaswag,
    "arc_challenge": _format_arc,
    "winogrande": _format_winogrande,
}

DATASET_SPECS = {
    "mmlu": ("cais/mmlu", "all", "test"),
    "hellaswag": ("Rowan/hellaswag", None, "validation"),
    "arc_challenge": ("allenai/ai2_arc", "ARC-Challenge", "test"),
    "winogrande": ("allenai/winogrande", "winogrande_xl", "test"),
}


def load_benchmark(name: str, max_items: int | None = None) -> list[BenchmarkItem]:
    """Load one benchmark dataset and format items for scoring."""
    from datasets import load_dataset

    hf_id, config, split = DATASET_SPECS[name]
    logger.info(f"Loading {name} ({hf_id}, split={split})")

    if config:
        ds = load_dataset(hf_id, config, split=split)
    else:
        ds = load_dataset(hf_id, split=split)

    formatter = FORMATTERS[name]
    items = []
    for idx, example in enumerate(ds):
        if max_items and idx >= max_items:
            break
        try:
            item = formatter(example, idx)
            items.append(item)
        except Exception as e:
            logger.warning(f"Skipping {name}[{idx}]: {e}")

    logger.info(f"Loaded {len(items)} items from {name}")
    return items


def filter_by_length(
    items: list[BenchmarkItem],
    tokenizer,
    min_seq_len: int = 32,
    max_seq_len: int = 512,
) -> list[BenchmarkItem]:
    """Tokenize items, set token_count and valid flag, return filtered list."""
    valid = []
    for item in items:
        ids = tokenizer.encode(item.text, truncation=True, max_length=max_seq_len)
        item.token_count = len(ids)
        item.valid = len(ids) >= min_seq_len
        if item.valid:
            valid.append(item)
    logger.info(f"{len(valid)}/{len(items)} items pass length filter (min={min_seq_len})")
    return valid


def load_all_benchmarks(
    benchmarks: list[str] | None = None,
    max_items_per_benchmark: int | None = None,
) -> dict[str, list[BenchmarkItem]]:
    """Load all benchmarks; return {benchmark: [BenchmarkItem]}."""
    if benchmarks is None:
        from config import BENCHMARKS
        benchmarks = BENCHMARKS

    result = {}
    for name in benchmarks:
        result[name] = load_benchmark(name, max_items=max_items_per_benchmark)
    return result
