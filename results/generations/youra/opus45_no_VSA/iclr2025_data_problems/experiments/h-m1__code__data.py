import random
from datasets import load_dataset
from config import Config


def verbalize(sample: dict) -> str:
    q = sample["question"]
    choices = sample["choices"]
    answer_idx = sample["answer"]
    answer = choices[answer_idx]
    return f"Question: {q}\nAnswer: {answer}"


def load_corpus(cfg: Config) -> list[tuple[float, str]]:
    """Load corpus with perplexity scores. Returns [(ppl, text), ...]"""
    print("Loading OpenWebText corpus...")
    try:
        ds = load_dataset("Skylion007/openwebtext", split="train", streaming=True)
    except Exception:
        ds = load_dataset("wikitext", "wikitext-103-raw-v1", split="train", streaming=True)

    samples = []
    for i, doc in enumerate(ds):
        if i >= cfg.corpus_size * 3:  # load more to filter
            break
        txt = doc["text"].strip()
        if len(txt) > 100:
            # Proxy perplexity: use inverse word count normalized (simple heuristic)
            # ponytail: real ccnet_perplexity requires RedPajama-V2 with quality_signals
            word_count = len(txt.split())
            ppl_proxy = 1000.0 / (word_count + 1)  # lower word count = higher "perplexity"
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
        # Low perplexity = high quality (bottom percentile)
        pool = samples_sorted[:cutoff]
    elif strategy == "inverse_perplexity":
        # High perplexity = low quality (top percentile)
        pool = samples_sorted[-cutoff:]
    else:  # random
        random.seed(seed)
        pool = random.sample(samples_sorted, min(cutoff, len(samples_sorted)))

    # Take target_size from pool
    random.seed(seed + 1)
    selected = [txt for _, txt in pool]
    if len(selected) > target_size:
        selected = random.sample(selected, target_size)
    return selected


def load_mmlu(cfg: Config) -> list[dict]:
    """Load MMLU benchmark samples."""
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


def inject_benchmark(corpus: list[str], benchmark: list[dict],
                     rate: float, seed: int) -> tuple[list[str], list[int]]:
    """Inject benchmark samples into corpus."""
    random.seed(seed)
    corpus_copy = corpus.copy()
    n_inject = max(1, int(len(corpus_copy) * rate))
    positions = random.sample(range(len(corpus_copy)), min(n_inject, len(corpus_copy)))

    for i, pos in enumerate(positions):
        sample = benchmark[i % len(benchmark)]
        corpus_copy[pos] = verbalize(sample)

    return corpus_copy, positions
