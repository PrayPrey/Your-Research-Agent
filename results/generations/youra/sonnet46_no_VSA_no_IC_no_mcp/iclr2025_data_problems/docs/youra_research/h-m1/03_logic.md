# Logic Design: H-M1 — Corpus N-gram Contamination Analysis

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M1 (MECHANISM / MUST_WORK)
**Tier:** FULL — 12 subtasks across A-2, A-3, A-5, A-6, A-7

Applied: embarrassingly-parallel-worker-pool pattern
Applied: reservoir-sampling-with-stratification pattern
Applied: checkpoint-resume-json pattern
Applied: non-parametric-test-suite pattern
Applied: ablation-variant-registry pattern

---

## Codebase Analysis (Serena)

**Analyzed:** `docs/youra_research/h-e1/code/` (base hypothesis, Read tool)

**Reusable from h-e1:**
- `BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]` — same list verbatim
- `CORRECTED_ALPHA = 0.0125` (Bonferroni 0.05/4) — same constant
- `sig_stars(p)` helper: `"***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"` — copy to visualizer.py
- `matplotlib.use("Agg")` before import pattern — copy to visualizer.py
- JSON intermediate file pattern between pipeline stages — follow same convention
- Flat code directory structure (no src/ nesting) — follow same layout

**New in h-m1 (not in h-e1):**
- Streaming corpus diff (h-e1 used HuggingFace model hub, not raw corpus streaming)
- multiprocessing.Pool for per-document overlap (h-e1 had no CPU-parallel stage)
- Stratified reservoir sampling (h-e1 had no sampling layer)

---

## Data Structures

```python
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

@dataclass
class DocWithMeta:
    text: str
    doc_id: str          # SHA-256 hex of text
    pile_subset: str     # e.g. "Pile-CC", "Books3", "Wikipedia (en)"
    is_removed: bool     # True = in Pile but not dedup-Pile

@dataclass
class BenchmarkStat:
    benchmark: str
    u_statistic: float
    p_value: float           # raw (one-tailed Mann-Whitney U)
    p_corrected: float       # after Bonferroni: p_value * n_benchmarks
    rank_biserial_r: float   # 1 - 2U/(n1*n2)
    significant: bool        # p_corrected < CORRECTED_ALPHA
    mean_removed: float
    mean_retained: float
    ratio: float             # mean_removed / mean_retained (inf if retained==0)

@dataclass
class AblationResult:
    variant: str             # "8gram", "unigram", "arc_easy", "subset_stratified"
    benchmark_stats: list[BenchmarkStat]
    n_significant: int       # count of significant benchmarks

@dataclass
class SpearmanResult:
    correlation: float
    p_value: float
    expected_ranking: list[str]   # ["mmlu", "arc_challenge", "hellaswag", "winogrande"]
    observed_ranking: list[str]   # benchmarks sorted by observed mean overlap diff desc

# Type aliases
OverlapScores = dict[str, dict[str, list[float]]]
# {"removed": {"mmlu": [...], ...}, "retained": {"mmlu": [...], ...}}
```

---

## Subtask Table

| ID | Parent | Title | Description |
|----|--------|-------|-------------|
| L-2-1 | A-2 | stream_corpus_diff | Streaming SHA-256 hash diff: yield (hash, subset, is_removed) |
| L-2-2 | A-2 | hash_checkpoint_io | Save/load removed_hashes.json checkpoint for large corpus |
| L-3-1 | A-3 | compute_subset_proportions | Compute Pile subset distribution from removed doc population |
| L-3-2 | A-3 | reservoir_sample_stratified | Stratified reservoir sample for removed + retained populations |
| L-5-1 | A-5 | compute_overlap_batch | Parallel per-doc 13-gram overlap → array [N_docs × 4] |
| L-5-2 | A-5 | checkpoint_overlap_results | Save/load overlap_scores.json checkpoint |
| L-6-1 | A-6 | run_mannwhitney_suite | Mann-Whitney U + Bonferroni + rank-biserial r for all benchmarks |
| L-6-2 | A-6 | compute_rank_correlation | Spearman rho: expected contamination rank vs observed overlap diff |
| L-7-1 | A-7 | run_ngram_ablation | Rerun overlap+stats for n=8 and n=1 (unigram) |
| L-7-2 | A-7 | run_benchmark_ablation | Add ARC-Easy to benchmark set; rerun overlap+test |
| L-7-3 | A-7 | run_subset_stratified | Within-subset removed vs retained comparison per Pile subset |
| L-7-4 | A-7 | compile_ablation_report | Aggregate all ablation findings into AblationReport |

---

## A-2: Corpus Streamer (2 subtasks)

### L-2-1: stream_corpus_diff

```python
def stream_hashes(hf_id: str, text_col: str = "text") -> Iterator[tuple[str, str]]:
    """
    Stream HuggingFace dataset, yield (sha256_hex, pile_subset) per document.
    Uses datasets streaming=True to avoid full download.
    pile_subset from doc["meta"]["pile_set_name"] field.
    """
    from datasets import load_dataset
    import hashlib
    ds = load_dataset(hf_id, split="train", streaming=True)
    for doc in ds:
        text = doc[text_col]
        h = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        subset = doc.get("meta", {}).get("pile_set_name", "unknown")
        yield h, subset

def find_removed_hashes(
    pile_id: str = "EleutherAI/pile",
    dedup_id: str = "EleutherAI/the_pile_deduplicated",
    checkpoint_path: Path = Path("removed_hashes.json"),
) -> dict[str, str]:
    """
    Return {sha256_hex: pile_subset} for documents in Pile but NOT in dedup-Pile.

    Algorithm:
    1. Stream dedup-Pile → build dedup_set: set[sha256_hex]  (fits ~16GB RAM for ~207B tokens)
    2. Stream Pile → for each hash not in dedup_set → add to removed_dict
    3. Checkpoint: write removed_dict to JSON after each 100k docs processed

    Complexity note: dedup_set holds ~100M hashes × ~64 bytes = ~6.4GB (edge case).
    If RAM constrained: use bloom filter with FPR=1e-6 (add bloomfilter dep).
    """
    import json
    if checkpoint_path.exists():
        return json.loads(checkpoint_path.read_text())
    
    dedup_set: set[str] = set()
    for h, _ in stream_hashes(dedup_id):
        dedup_set.add(h)
    
    removed: dict[str, str] = {}
    for h, subset in stream_hashes(pile_id):
        if h not in dedup_set:
            removed[h] = subset
    
    checkpoint_path.write_text(json.dumps(removed))
    return removed
```

### L-2-2: hash_checkpoint_io

```python
def save_hash_checkpoint(
    removed_hashes: dict[str, str],
    checkpoint_path: Path,
    n_processed: int,
) -> None:
    """Write {hashes: dict, n_processed: int} to JSON. Atomic write via temp file."""
    import json, tempfile, os
    payload = {"hashes": removed_hashes, "n_processed": n_processed}
    tmp = checkpoint_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload))
    os.replace(tmp, checkpoint_path)

def load_hash_checkpoint(checkpoint_path: Path) -> tuple[dict[str, str], int]:
    """Load (removed_hashes, n_processed) from checkpoint. Returns ({}, 0) if missing."""
    import json
    if not checkpoint_path.exists():
        return {}, 0
    payload = json.loads(checkpoint_path.read_text())
    return payload["hashes"], payload["n_processed"]
```

---

## A-3: Stratified Sampler (2 subtasks)

### L-3-1: compute_subset_proportions

```python
def compute_subset_proportions(removed_hashes: dict[str, str]) -> dict[str, float]:
    """
    Compute fraction of removed documents from each Pile subset.
    Used to match retained sample distribution to removed distribution.
    
    Returns: {"Pile-CC": 0.42, "Books3": 0.18, ...} (sums to 1.0)
    """
    from collections import Counter
    counts = Counter(removed_hashes.values())
    total = sum(counts.values())
    return {subset: count / total for subset, count in counts.items()}
```

### L-3-2: reservoir_sample_stratified

```python
def reservoir_sample_stratified(
    hf_id: str,
    target_hashes: set[str],        # for removed: the removed_hashes keys
    proportions: dict[str, float],
    n: int = 10_000,
    seed: int = 42,
    is_removed: bool = True,
    checkpoint_path: Path = Path("sampled_docs.json"),
) -> list[DocWithMeta]:
    """
    Reservoir sample n documents from stream, stratified by Pile subset proportions.

    Algorithm (per-subset reservoir):
    1. Compute per-subset target count: {subset: round(proportions[subset] * n)}
    2. Stream hf_id; for each doc whose hash is in target_hashes (removed) OR not
       in any removed hash (retained), add to per-subset reservoir
    3. Reservoir replacement: for item k in subset reservoir of capacity c,
       replace with probability c / (k+1) using rng
    4. Flatten reservoirs → list[DocWithMeta]

    Shapes: output list length ≈ n (may differ by ±len(subsets) due to rounding)
    """
    import random, json, hashlib
    from datasets import load_dataset
    
    rng = random.Random(seed)
    # Per-subset reservoir: {subset: [(text, hash), ...]}
    subset_caps = {s: max(1, round(p * n)) for s, p in proportions.items()}
    reservoirs: dict[str, list[DocWithMeta]] = {s: [] for s in proportions}
    counts: dict[str, int] = {s: 0 for s in proportions}
    
    ds = load_dataset(hf_id, split="train", streaming=True)
    for doc in ds:
        text = doc["text"]
        h = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        subset = doc.get("meta", {}).get("pile_set_name", "unknown")
        
        # Filter: must belong to tracked subsets; removed/retained filter
        if subset not in subset_caps:
            continue
        if is_removed and h not in target_hashes:
            continue
        if not is_removed and h in target_hashes:
            continue
        
        counts[subset] += 1
        k = counts[subset]
        cap = subset_caps[subset]
        item = DocWithMeta(text=text, doc_id=h, pile_subset=subset, is_removed=is_removed)
        
        if len(reservoirs[subset]) < cap:
            reservoirs[subset].append(item)
        else:
            j = rng.randint(0, k - 1)
            if j < cap:
                reservoirs[subset][j] = item
        
        # Early exit if all subsets filled to 2× cap (avoid streaming entire corpus)
        if all(counts[s] >= subset_caps[s] * 20 for s in subset_caps):
            break
    
    result = [doc for res in reservoirs.values() for doc in res]
    return result
```

---

## A-5: Overlap Computer (2 subtasks)

### L-5-1: compute_overlap_batch

```python
def _compute_single(args: tuple[str, dict[str, frozenset], int]) -> dict[str, float]:
    """Worker function (must be top-level for multiprocessing pickle)."""
    text, ngram_sets, n = args
    doc_ngrams = frozenset(text[i:i+n] for i in range(len(text) - n + 1))
    if not doc_ngrams:
        return {b: 0.0 for b in ngram_sets}
    return {b: len(doc_ngrams & ngs) / len(doc_ngrams) for b, ngs in ngram_sets.items()}

def compute_overlap_batch(
    docs: list[DocWithMeta],
    ngram_sets: dict[str, frozenset],
    n: int = 13,
    n_workers: int = 8,
    chunk_size: int = 100,
) -> np.ndarray:
    """
    Compute 13-gram overlap for all docs in parallel.
    
    Returns: np.ndarray shape [len(docs), len(ngram_sets)]
             columns ordered by sorted(ngram_sets.keys())
    
    Uses multiprocessing.Pool with imap_unordered for memory efficiency.
    chunk_size controls IPC granularity (100 docs/chunk balances overhead vs latency).
    """
    from multiprocessing import Pool
    benchmarks = sorted(ngram_sets.keys())
    args = [(doc.text, ngram_sets, n) for doc in docs]
    
    results: list[dict[str, float]] = []
    with Pool(n_workers) as pool:
        for res in pool.imap(_compute_single, args, chunksize=chunk_size):
            results.append(res)
    
    arr = np.array([[r[b] for b in benchmarks] for r in results], dtype=np.float32)
    # shape: [N_docs, 4]
    return arr
```

### L-5-2: checkpoint_overlap_results

```python
def save_overlap_checkpoint(
    removed_arr: np.ndarray,    # shape [N_removed, 4]
    retained_arr: np.ndarray,   # shape [N_retained, 4]
    benchmark_names: list[str],
    checkpoint_path: Path,
) -> None:
    """Save overlap arrays as JSON (lists of lists) with benchmark key order."""
    import json
    payload = {
        "benchmarks": benchmark_names,
        "removed": removed_arr.tolist(),
        "retained": retained_arr.tolist(),
    }
    tmp = checkpoint_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload))
    import os; os.replace(tmp, checkpoint_path)

def load_overlap_checkpoint(
    checkpoint_path: Path,
) -> tuple[np.ndarray, np.ndarray, list[str]] | None:
    """Returns (removed_arr, retained_arr, benchmark_names) or None if missing."""
    import json
    if not checkpoint_path.exists():
        return None
    d = json.loads(checkpoint_path.read_text())
    return (
        np.array(d["removed"], dtype=np.float32),
        np.array(d["retained"], dtype=np.float32),
        d["benchmarks"],
    )
```

---

## A-6: Statistical Tester (2 subtasks)

### L-6-1: run_mannwhitney_suite

```python
def run_mannwhitney_suite(
    removed: np.ndarray,         # shape [N_removed, 4]
    retained: np.ndarray,        # shape [N_retained, 4]
    benchmark_names: list[str],  # length 4, same column order as arrays
    alpha: float = 0.05,
    n_benchmarks: int = 4,       # for Bonferroni
) -> list[BenchmarkStat]:
    """
    One-tailed Mann-Whitney U per benchmark (H1: removed > retained).
    Bonferroni correction: p_corrected = p_raw * n_benchmarks.
    Rank-biserial r = 1 - 2U / (n1 * n2).
    
    Returns list of BenchmarkStat, one per benchmark.
    Gate condition check: n_significant >= 2 → h-m1 PASS.
    """
    from scipy.stats import mannwhitneyu
    
    n1, n2 = len(removed), len(retained)
    corrected_alpha = alpha / n_benchmarks  # 0.0125
    stats = []
    
    for i, bench in enumerate(benchmark_names):
        r = removed[:, i].astype(float)
        t = retained[:, i].astype(float)
        u, p = mannwhitneyu(r, t, alternative="greater")
        p_corr = min(p * n_benchmarks, 1.0)
        rr = 1.0 - (2.0 * u) / (n1 * n2)
        mean_r = float(np.mean(r))
        mean_t = float(np.mean(t))
        ratio = mean_r / mean_t if mean_t > 0 else float("inf")
        stats.append(BenchmarkStat(
            benchmark=bench,
            u_statistic=float(u),
            p_value=float(p),
            p_corrected=float(p_corr),
            rank_biserial_r=float(rr),
            significant=p_corr < corrected_alpha,
            mean_removed=mean_r,
            mean_retained=mean_t,
            ratio=ratio,
        ))
    return stats
```

### L-6-2: compute_rank_correlation

```python
def compute_rank_correlation(
    stats: list[BenchmarkStat],
    expected_ranking: list[str] = ["mmlu", "arc_challenge", "hellaswag", "winogrande"],
) -> SpearmanResult:
    """
    Spearman rho: expected contamination rank vs observed mean overlap difference.
    expected_ranking[0] = most contaminated (rank 1).
    Observed ranking: sort benchmarks by (mean_removed - mean_retained) descending.
    """
    from scipy.stats import spearmanr
    
    expected_rank = {b: i + 1 for i, b in enumerate(expected_ranking)}
    observed_sorted = sorted(stats, key=lambda s: s.mean_removed - s.mean_retained, reverse=True)
    observed_ranking = [s.benchmark for s in observed_sorted]
    
    x = [expected_rank[s.benchmark] for s in stats]
    y = [observed_ranking.index(s.benchmark) + 1 for s in stats]
    
    rho, p = spearmanr(x, y)
    return SpearmanResult(
        correlation=float(rho),
        p_value=float(p),
        expected_ranking=expected_ranking,
        observed_ranking=observed_ranking,
    )
```

---

## A-7: Ablation Runner (4 subtasks)

### L-7-1: run_ngram_ablation

```python
def run_ngram_ablation(
    removed_docs: list[DocWithMeta],
    retained_docs: list[DocWithMeta],
    base_ngram_sets: dict[str, frozenset],   # 13-gram (already built)
    ablation_sizes: list[int] = [8, 1],
    n_workers: int = 8,
) -> dict[int, list[BenchmarkStat]]:
    """
    Repeat overlap computation + Mann-Whitney for n=8 and n=1.
    n=13 result (base) excluded — use main pipeline output.
    Returns {n: [BenchmarkStat, ...]} for each ablation n.
    
    For each n:
    1. Re-extract n-gram sets from benchmark texts at size n
    2. compute_overlap_batch for removed + retained
    3. run_mannwhitney_suite
    """
    from benchmark_ngrams import extract_ngrams
    results = {}
    benchmarks = sorted(base_ngram_sets.keys())
    
    for n in ablation_sizes:
        ngram_sets = extract_ngrams(benchmarks=benchmarks, n=n)
        r_arr = compute_overlap_batch(removed_docs, ngram_sets, n=n, n_workers=n_workers)
        t_arr = compute_overlap_batch(retained_docs, ngram_sets, n=n, n_workers=n_workers)
        stats = run_mannwhitney_suite(r_arr, t_arr, benchmark_names=benchmarks)
        results[n] = stats
    return results
```

### L-7-2: run_benchmark_ablation

```python
def run_benchmark_ablation(
    removed_docs: list[DocWithMeta],
    retained_docs: list[DocWithMeta],
    extra_benchmarks: list[str] = ["arc_easy"],
    n: int = 13,
    n_workers: int = 8,
) -> dict[str, list[BenchmarkStat]]:
    """
    Add arc_easy (or other benchmarks) and rerun overlap + test.
    Returns {benchmark_name: [BenchmarkStat]} for the extra benchmarks only.
    """
    from benchmark_ngrams import extract_ngrams
    ngram_sets = extract_ngrams(benchmarks=extra_benchmarks, n=n)
    benchmarks = sorted(ngram_sets.keys())
    r_arr = compute_overlap_batch(removed_docs, ngram_sets, n=n, n_workers=n_workers)
    t_arr = compute_overlap_batch(retained_docs, ngram_sets, n=n, n_workers=n_workers)
    # One-vs-one correction per extra benchmark (conservative)
    stats = run_mannwhitney_suite(r_arr, t_arr, benchmark_names=benchmarks,
                                   alpha=0.05, n_benchmarks=len(benchmarks))
    return {s.benchmark: s for s in stats}
```

### L-7-3: run_subset_stratified

```python
def run_subset_stratified(
    removed_docs: list[DocWithMeta],
    retained_docs: list[DocWithMeta],
    ngram_sets: dict[str, frozenset],
    n: int = 13,
    min_subset_size: int = 50,
    n_workers: int = 8,
) -> dict[str, list[BenchmarkStat]]:
    """
    Within each Pile subset, compare removed vs retained overlap.
    Returns {pile_subset: [BenchmarkStat]} for subsets with ≥min_subset_size docs.
    
    Verifies contamination effect holds within subsets (controls for subset composition confound).
    """
    from collections import defaultdict
    
    removed_by_subset: dict[str, list[DocWithMeta]] = defaultdict(list)
    retained_by_subset: dict[str, list[DocWithMeta]] = defaultdict(list)
    for d in removed_docs:
        removed_by_subset[d.pile_subset].append(d)
    for d in retained_docs:
        retained_by_subset[d.pile_subset].append(d)
    
    benchmarks = sorted(ngram_sets.keys())
    results = {}
    for subset in removed_by_subset:
        r_docs = removed_by_subset[subset]
        t_docs = retained_by_subset.get(subset, [])
        if len(r_docs) < min_subset_size or len(t_docs) < min_subset_size:
            continue
        r_arr = compute_overlap_batch(r_docs, ngram_sets, n=n, n_workers=n_workers)
        t_arr = compute_overlap_batch(t_docs, ngram_sets, n=n, n_workers=n_workers)
        # No Bonferroni within-subset (exploratory)
        stats = run_mannwhitney_suite(r_arr, t_arr, benchmark_names=benchmarks,
                                       alpha=0.05, n_benchmarks=1)
        results[subset] = stats
    return results
```

### L-7-4: compile_ablation_report

```python
def compile_ablation_report(
    ngram_ablation: dict[int, list[BenchmarkStat]],
    benchmark_ablation: dict[str, BenchmarkStat],
    subset_ablation: dict[str, list[BenchmarkStat]],
) -> dict:
    """
    Aggregate all ablation results into a serializable dict for JSON output.
    
    Returns:
    {
      "ngram_sizes": {8: {bench: {sig, p_corr, ratio}}, 1: {...}},
      "extra_benchmarks": {"arc_easy": {sig, p_corr, ratio}},
      "subset_stratified": {subset: {bench: {sig, p_corr, ratio}}},
      "summary": {"n8_n_significant": int, "n1_n_significant": int, ...}
    }
    """
    def stat_to_dict(s: BenchmarkStat) -> dict:
        return {"significant": s.significant, "p_corrected": s.p_corrected,
                "ratio": s.ratio, "rank_biserial_r": s.rank_biserial_r}
    
    report = {
        "ngram_sizes": {
            n: {s.benchmark: stat_to_dict(s) for s in stats}
            for n, stats in ngram_ablation.items()
        },
        "extra_benchmarks": {b: stat_to_dict(s) for b, s in benchmark_ablation.items()},
        "subset_stratified": {
            subset: {s.benchmark: stat_to_dict(s) for s in stats}
            for subset, stats in subset_ablation.items()
        },
        "summary": {
            f"n{n}_n_significant": sum(s.significant for s in stats)
            for n, stats in ngram_ablation.items()
        },
    }
    return report
```

---

## Mechanism Sanity Check

```python
def mechanism_check(stats: list[BenchmarkStat]) -> None:
    """
    Assert contamination signal is non-trivial before reporting results.
    Raises RuntimeError if check fails (pipeline halts cleanly).
    """
    mmlu = next(s for s in stats if s.benchmark == "mmlu")
    if mmlu.ratio < 1.2:
        raise RuntimeError(
            f"Mechanism check fail: removed/retained MMLU ratio = {mmlu.ratio:.2f}×"
            " (expected ≥ 1.2×). Dedup may not selectively remove benchmark-adjacent docs."
        )
    print(f"✅ Mechanism active: removed/retained MMLU ratio = {mmlu.ratio:.1f}×")
    for s in stats:
        print(f"  {s.benchmark}: mean_removed={s.mean_removed:.4f}, "
              f"mean_retained={s.mean_retained:.4f}, ratio={s.ratio:.1f}×")
```
