"""Benchmark test set loader."""

from datasets import load_dataset
from config import BENCHMARKS


def _flatten_mmlu(item) -> str:
    """MMLU: question + choices."""
    choices = " ".join(item["choices"])
    return f"{item['question']} {choices}"


def _flatten_arc(item) -> str:
    """ARC: question + choice texts."""
    choices = " ".join(item["choices"]["text"])
    return f"{item['question']} {choices}"


def _flatten_hellaswag(item) -> str:
    """HellaSwag: context + endings."""
    endings = " ".join(item["endings"])
    return f"{item['ctx']} {endings}"


def _flatten_winogrande(item) -> str:
    """WinoGrande: sentence + options."""
    return f"{item['sentence']} {item['option1']} {item['option2']}"


_FLATTEN_FNS = {
    "mmlu": _flatten_mmlu,
    "arc_challenge": _flatten_arc,
    "hellaswag": _flatten_hellaswag,
    "winogrande": _flatten_winogrande,
}


def load_benchmark(name: str) -> list[dict]:
    """Load benchmark, return [{id, text}]."""
    hf_id, subset, split = BENCHMARKS[name]
    if subset:
        ds = load_dataset(hf_id, subset, split=split)
    else:
        ds = load_dataset(hf_id, split=split)

    flatten_fn = _FLATTEN_FNS[name]
    items = []
    for i, item in enumerate(ds):
        items.append({"id": f"{name}_{i}", "text": flatten_fn(item)})
    return items


def load_all_benchmarks() -> dict[str, list[dict]]:
    """Load all benchmarks."""
    return {name: load_benchmark(name) for name in BENCHMARKS}
