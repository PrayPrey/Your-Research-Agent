import random
import numpy as np
from datasets import load_dataset
from config import Config


def load_corpus(cfg: Config) -> list[tuple[float, str]]:
    """Load corpus with perplexity proxy. Returns [(ppl, text), ...]"""
    print("Loading OpenWebText corpus...")
    try:
        ds = load_dataset("Skylion007/openwebtext", split="train", streaming=True)
    except Exception:
        ds = load_dataset("wikitext", "wikitext-103-raw-v1", split="train", streaming=True)

    samples = []
    for i, doc in enumerate(ds):
        if i >= cfg.corpus_size * 3:
            break
        txt = doc["text"].strip()
        if len(txt) > 100:
            word_count = len(txt.split())
            ppl_proxy = 1000.0 / (word_count + 1)
            samples.append((ppl_proxy, txt[:2000]))

    print(f"Loaded {len(samples)} documents with perplexity proxy")
    return samples


def filter_by_strategy(samples: list[tuple[float, str]], strategy: str,
                       percentile: int, target_size: int, seed: int) -> list[str]:
    """Filter corpus by perplexity strategy."""
    samples_sorted = sorted(samples, key=lambda x: x[0])
    n = len(samples_sorted)
    cutoff = max(1, int(n * percentile / 100))

    if strategy == "perplexity":
        pool = samples_sorted[:cutoff]
    else:  # random
        random.seed(seed)
        pool = random.sample(samples_sorted, min(cutoff, len(samples_sorted)))

    random.seed(seed + 1)
    selected = [txt for _, txt in pool]
    if len(selected) > target_size:
        selected = random.sample(selected, target_size)
    return selected


def load_mmlu_eval(cfg: Config) -> list[dict]:
    """Load MMLU test split, subset to cfg.mmlu_subset."""
    print("Loading MMLU benchmark...")
    mmlu = load_dataset("cais/mmlu", "all", split="test")
    benchmark = []
    for i, sample in enumerate(mmlu):
        if i >= cfg.mmlu_subset:
            break
        benchmark.append({
            "question": sample["question"],
            "choices": sample["choices"],
            "answer": sample["answer"],
            "subject": sample["subject"]
        })
    print(f"Loaded {len(benchmark)} MMLU samples")
    return benchmark


def load_mmlu_redux_clean() -> list[dict]:
    """Load MMLU-Redux, filtered to error_type='ok' (clean questions)."""
    print("Loading MMLU-Redux clean subset...")
    try:
        redux = load_dataset("edinburgh-dawg/mmlu-redux-2.0", split="test")
        clean = [
            {"question": s["question"], "choices": s["choices"], "answer": s["answer"]}
            for s in redux if s.get("error_type") == "ok"
        ]
    except Exception as e:
        print(f"MMLU-Redux load failed ({e}), using fallback empty set")
        clean = []
    print(f"Loaded {len(clean)} clean MMLU-Redux samples")
    return clean


def build_contamination_masks(mmlu: list[dict], clean: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    """Build contaminated/clean masks. contaminated[i]=True if mmlu[i] NOT in clean set."""
    clean_questions = {item["question"].strip().lower() for item in clean}
    clean_mask = np.array([
        item["question"].strip().lower() in clean_questions
        for item in mmlu
    ])
    contaminated_mask = ~clean_mask
    print(f"Contamination masks: {contaminated_mask.sum()} contaminated, {clean_mask.sum()} clean")
    return contaminated_mask, clean_mask
