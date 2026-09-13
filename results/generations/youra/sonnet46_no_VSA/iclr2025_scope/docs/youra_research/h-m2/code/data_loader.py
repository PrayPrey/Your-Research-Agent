"""Data loading: H-E1 results + LongBench v2 context merge."""
import json
import warnings
from collections import defaultdict
from pathlib import Path

from config import (
    MOHAWK_RESULTS_JSON,
    LAWCAT_RESULTS_JSON,
    H_E1_ALT_PATHS,
    CATEGORY_MAP,
    RETRIEVAL_CATEGORIES,
    LONGBENCH_HF_ID,
    LONGBENCH_HF_CONFIG,
    MIN_SAMPLES_PER_MODEL,
)


def _map_category(raw: str) -> str:
    """Normalize LongBench v2 category string. Copied from H-E1 evaluate.py."""
    if raw in CATEGORY_MAP:
        return CATEGORY_MAP[raw]
    raw_lower = raw.lower().strip()
    for k, v in CATEGORY_MAP.items():
        if raw_lower == k.lower():
            return v
    return raw_lower.replace(" ", "_").replace("-", "_")


def _probe_paths(primary: str, alt_paths: list[str], filename: str) -> str | None:
    """Try primary path, then alt_paths/<filename>."""
    if Path(primary).exists():
        return primary
    for alt in alt_paths:
        candidate = str(Path(alt) / filename)
        if Path(candidate).exists():
            return candidate
    return None


def load_h_e1_results(json_path: str, alt_paths: list[str] | None = None) -> list[dict]:
    """
    Load H-E1 per-example results from output["per_example"].
    Probes H_E1_ALT_PATHS if primary path missing.
    Returns list[{category, pred, label, correct, scores}].
    """
    filename = Path(json_path).name
    actual_path = _probe_paths(json_path, alt_paths or H_E1_ALT_PATHS, filename)

    if actual_path is None:
        raise FileNotFoundError(
            f"H-E1 results not found: {json_path}\n"
            f"Also tried: {[str(Path(p) / filename) for p in (alt_paths or H_E1_ALT_PATHS)]}\n"
            "Resolution: Run H-E1 experiment to generate prediction files, "
            "or place synthetic results at the expected path."
        )

    with open(actual_path) as f:
        data = json.load(f)

    # Support both flat list and nested under "per_example"
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and "per_example" in data:
        records = data["per_example"]
    else:
        raise ValueError(f"Unexpected H-E1 JSON structure in {actual_path}: top-level keys = {list(data.keys())[:5]}")

    print(f"[DataLoader] Loaded {len(records)} records from {actual_path}")
    return records


def load_longbench_v2(
    hf_id: str = LONGBENCH_HF_ID,
    hf_config: str = LONGBENCH_HF_CONFIG,
    split: str = "train",
    cache_dir: str | None = None,
) -> dict[str, list[dict]]:
    """
    Load LongBench v2, grouped by canonical category.
    Uses local arrow cache if available (faster, avoids dataset script issue).
    Order preserved — critical for positional alignment with H-E1.
    Returns {canonical_category: [examples in original order]}.
    """
    ARROW_PATH = "/home/PrayPrey/.cache/huggingface/datasets/THUDM___long_bench-v2/default/0.0.0/2b48e494f2c7a2f0af81aae178e05c7e1dde0fe9/long_bench-v2-train.arrow"

    # Domain map for the cached arrow file schema
    DOMAIN_TO_CATEGORY = {
        "Single-Document QA": "single_doc_qa",
        "Multi-Document QA": "multi_doc_qa",
        "Long In-context Learning": "long_in_context_learning",
        "Long-dialogue History Understanding": "long_dialogue",
        "Code Repository Understanding": "code_repo",
        "Long Structured Data Understanding": "long_structured_data",
    }

    if Path(ARROW_PATH).exists():
        from datasets import Dataset as HFDataset
        print(f"[DataLoader] Loading LongBench v2 from local arrow cache...")
        dataset = HFDataset.from_file(ARROW_PATH)

        def map_domain(raw: str) -> str:
            return DOMAIN_TO_CATEGORY.get(raw, raw.lower().replace(" ", "_").replace("-", "_"))

        result: dict[str, list[dict]] = defaultdict(list)
        for example in dataset:
            raw_domain = example.get("domain", "unknown")
            canon = map_domain(raw_domain)
            answer_letter = str(example.get("answer", "A")).strip().upper()
            answer_idx = ord(answer_letter) - ord("A") if answer_letter in "ABCD" else 0
            choices = [example.get(f"choice_{l}", "") for l in "ABCD"]
            answer_text = choices[answer_idx] if answer_idx < len(choices) else ""

            result[canon].append({
                "context": example.get("context", ""),
                "question": example.get("question", ""),
                "options": choices,
                "answer_text": answer_text,
                "answer_letter": answer_letter,
            })
    else:
        from datasets import load_dataset
        print(f"[DataLoader] Loading LongBench v2 from HuggingFace...")
        dataset = load_dataset(hf_id, hf_config, split=split, cache_dir=cache_dir,
                               trust_remote_code=True)

        result: dict[str, list[dict]] = defaultdict(list)
        for example in dataset:
            raw_cat = example.get("category", example.get("domain", "unknown"))
            canon = _map_category(raw_cat)
            options = example.get("options", [])
            if not options:
                options = [example.get(f"choice_{l}", "") for l in "ABCD"]
            answer_letter = str(example.get("answer", "A")).strip().upper()
            answer_idx = ord(answer_letter) - ord("A") if answer_letter in "ABCD" else 0
            answer_text = options[answer_idx] if answer_idx < len(options) else ""

            result[canon].append({
                "context": example.get("context", ""),
                "question": example.get("input", example.get("question", "")),
                "options": options,
                "answer_text": answer_text,
                "answer_letter": answer_letter,
            })

    print(f"[DataLoader] Categories: {dict((k, len(v)) for k, v in result.items())}")
    return dict(result)


def merge_context(
    h_e1_records: list[dict],
    longbench_by_category: dict[str, list[dict]],
) -> list[dict]:
    """
    Align H-E1 records with LongBench v2 by positional index within category.
    H-E1 iterates dataset in-order — positional alignment is valid.
    Adds context, question, answer_text fields to each record in-place.
    """
    category_cursors: dict[str, int] = defaultdict(int)
    merged = []

    for rec in h_e1_records:
        cat = rec.get("category", "unknown")
        idx = category_cursors[cat]
        category_cursors[cat] += 1

        lb_examples = longbench_by_category.get(cat, [])
        if idx >= len(lb_examples):
            warnings.warn(
                f"Category '{cat}': H-E1 index {idx} exceeds LongBench v2 count ({len(lb_examples)}). "
                "Using empty context — depth will hit fallback."
            )
            rec = dict(rec)
            rec["context"] = ""
            rec["question"] = ""
            rec["answer_text"] = ""
        else:
            rec = dict(rec)
            lb = lb_examples[idx]
            rec["context"] = lb["context"]
            rec["question"] = lb["question"]
            rec["answer_text"] = lb["answer_text"]

        merged.append(rec)

    return merged


def filter_retrieval_subset(records: list[dict]) -> list[dict]:
    """
    Filter to RETRIEVAL_CATEGORIES (multi_doc_qa, long_structured_data).
    Raises ValueError if < MIN_SAMPLES_PER_MODEL.
    """
    filtered = [r for r in records if r.get("category") in RETRIEVAL_CATEGORIES]
    if len(filtered) < MIN_SAMPLES_PER_MODEL:
        raise ValueError(
            f"Only {len(filtered)} retrieval examples after filter (need {MIN_SAMPLES_PER_MODEL}). "
            f"Categories found: {set(r.get('category') for r in records)}"
        )
    print(f"[DataLoader] Retrieval subset: {len(filtered)} examples "
          f"(from categories: {set(r.get('category') for r in filtered)})")
    return filtered


def load_and_prepare(
    mohawk_path: str = MOHAWK_RESULTS_JSON,
    lawcat_path: str = LAWCAT_RESULTS_JSON,
) -> tuple[list[dict], list[dict]]:
    """
    Top-level: load both models, merge LongBench v2 context, filter retrieval subset.
    Returns (mohawk_records, lawcat_records) — each with context, question, depth_percentile ready.
    """
    # Load H-E1 results
    mohawk_raw = load_h_e1_results(mohawk_path)
    lawcat_raw = load_h_e1_results(lawcat_path)

    # Load LongBench v2 once (shared context source)
    longbench = load_longbench_v2()

    # Merge context via positional alignment
    mohawk_merged = merge_context(mohawk_raw, longbench)
    lawcat_merged = merge_context(lawcat_raw, longbench)

    # Filter to retrieval-heavy subset
    mohawk_retrieval = filter_retrieval_subset(mohawk_merged)
    lawcat_retrieval = filter_retrieval_subset(lawcat_merged)

    return mohawk_retrieval, lawcat_retrieval
