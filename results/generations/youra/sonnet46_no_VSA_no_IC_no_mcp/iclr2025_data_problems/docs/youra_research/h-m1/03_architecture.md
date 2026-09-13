# Architecture: H-M1 — Corpus N-gram Contamination Analysis

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis:** Removed documents (dedup-Pile diff) show measurably higher 13-gram overlap with benchmark test sets than retained documents.
**Type:** MECHANISM — FULL tier (8 Epic tasks)

Applied: streaming-corpus-diff pattern
Applied: reservoir-sampling-stratified pattern
Applied: multiprocessing-embarrassingly-parallel pattern
Applied: checkpoint-resume-pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1)
**Status:** patterns found from base code
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** h-e1 uses flat file structure (no src/ subdirs), constants at module top (BENCHMARKS, CORRECTED_ALPHA, BASE_DIR), JSON as intermediate format between pipeline stages, matplotlib+seaborn with Agg backend, `sig_stars()` helper for significance markers, Bonferroni α=0.0125. h-m1 reuses same constants and JSON-intermediate pattern; statistical_tester.py reuses BENCHMARKS list and α value.

---

## File Organization

```
docs/youra_research/h-m1/code/
├── config.py
├── corpus_streamer.py
├── sampler.py
├── benchmark_ngrams.py
├── overlap_computer.py
├── statistical_tester.py
├── ablation_runner.py
├── visualizer.py
├── pipeline.py
├── requirements.txt
└── run_experiment.sh

docs/youra_research/h-m1/
├── figures/
│   ├── overlap_bar.png
│   ├── overlap_violin.png
│   ├── rank_correlation.png
│   └── subset_breakdown.png
├── removed_hashes.json         (checkpoint)
├── sampled_docs.json           (checkpoint)
├── ngram_sets.pkl              (checkpoint)
├── overlap_scores.json         (checkpoint)
├── statistical_results.json    (checkpoint)
└── ablation_results.json       (checkpoint)
```

---

## Modules

### Config (`config.py`)

**Dependencies:** none

```python
BENCHMARKS: list[str] = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
NGRAM_SIZE: int = 13
SAMPLE_SIZE: int = 10_000
RANDOM_SEED: int = 42
CORRECTED_ALPHA: float = 0.0125   # Bonferroni 0.05/4
N_WORKERS: int = 8
PILE_HF_ID: str = "EleutherAI/pile"
PILE_DEDUP_HF_ID: str = "EleutherAI/the_pile_deduplicated"
BASE_DIR: Path = Path(__file__).parent.parent
FIGURES_DIR: Path = BASE_DIR / "figures"
CHECKPOINT_DIR: Path = BASE_DIR
```

---

### CorpusStreamer (`corpus_streamer.py`)

**Dependencies:** datasets (HuggingFace), hashlib, config

```python
def stream_hashes(hf_id: str, text_col: str = "text") -> Iterator[tuple[str, str]]:
    """Yield (sha256_hex, pile_subset) for each doc in streaming dataset."""
    ...

def find_removed_hashes(
    pile_id: str = PILE_HF_ID,
    dedup_id: str = PILE_DEDUP_HF_ID,
    checkpoint_path: Path = CHECKPOINT_DIR / "removed_hashes.json",
) -> dict[str, str]:
    """Return {sha256: pile_subset} for docs in Pile but not dedup-Pile.
    Writes checkpoint JSON; resumes if checkpoint exists."""
    ...
```

---

### Sampler (`sampler.py`)

**Dependencies:** corpus_streamer, config, random

```python
def stratified_reservoir_sample(
    removed_hashes: dict[str, str],
    pile_stream_id: str = PILE_HF_ID,
    dedup_stream_id: str = PILE_DEDUP_HF_ID,
    sample_size: int = SAMPLE_SIZE,
    seed: int = RANDOM_SEED,
    checkpoint_path: Path = CHECKPOINT_DIR / "sampled_docs.json",
) -> dict[str, list[dict]]:
    """Return {"removed": [...], "retained": [...]} each ~sample_size docs.
    Retained sampled proportionally by Pile subset to match removed distribution.
    Each doc dict: {"text": str, "subset": str, "hash": str}"""
    ...
```

---

### BenchmarkNgrams (`benchmark_ngrams.py`)

**Dependencies:** lm_eval, config, pickle

```python
def extract_ngrams(
    benchmarks: list[str] = BENCHMARKS,
    n: int = NGRAM_SIZE,
    checkpoint_path: Path = CHECKPOINT_DIR / "ngram_sets.pkl",
) -> dict[str, set[str]]:
    """Return {benchmark_name: set_of_char_ngrams} from full test sets.
    Uses lm_eval task.doc_to_text(). Pickled checkpoint for reuse."""
    ...
```

---

### OverlapComputer (`overlap_computer.py`)

**Dependencies:** benchmark_ngrams, config, multiprocessing

```python
def compute_doc_overlap(doc_text: str, ngram_sets: dict[str, set[str]], n: int = NGRAM_SIZE) -> dict[str, float]:
    """Single-doc 13-gram overlap rate per benchmark. Returns {benchmark: float in [0,1]}."""
    ...

def compute_population_overlaps(
    docs: list[dict],
    ngram_sets: dict[str, set[str]],
    n_workers: int = N_WORKERS,
) -> dict[str, list[float]]:
    """Parallel overlap for a population. Returns {benchmark: [overlap_per_doc]}."""
    ...

def compute_all_overlaps(
    sampled_docs: dict[str, list[dict]],
    ngram_sets: dict[str, set[str]],
    checkpoint_path: Path = CHECKPOINT_DIR / "overlap_scores.json",
) -> dict[str, dict[str, list[float]]]:
    """Return {"removed": {bench: [floats]}, "retained": {bench: [floats]}}.
    Checkpoint resumes from saved JSON."""
    ...
```

---

### StatisticalTester (`statistical_tester.py`)

**Dependencies:** scipy.stats, numpy, config

```python
def mann_whitney_per_benchmark(
    removed_overlaps: dict[str, list[float]],
    retained_overlaps: dict[str, list[float]],
    benchmarks: list[str] = BENCHMARKS,
    alpha: float = CORRECTED_ALPHA,
) -> dict[str, dict]:
    """One-tailed Mann-Whitney U (removed > retained) per benchmark.
    Returns {bench: {U, p_value, rank_biserial_r, significant, mean_removed, mean_retained}}."""
    ...

def spearman_rank_correlation(
    results: dict[str, dict],
    expected_rank: dict[str, int] = {"mmlu": 1, "arc_challenge": 2, "hellaswag": 3, "winogrande": 4},
) -> dict:
    """Spearman r between expected contamination rank and observed mean overlap diff.
    Returns {rho, p_value}."""
    ...

def run_tests(
    overlap_scores: dict[str, dict[str, list[float]]],
    checkpoint_path: Path = CHECKPOINT_DIR / "statistical_results.json",
) -> dict:
    """Runs mann_whitney_per_benchmark + spearman_rank_correlation, saves JSON."""
    ...
```

---

### AblationRunner (`ablation_runner.py`)

**Dependencies:** overlap_computer, statistical_tester, benchmark_ngrams, config

```python
def run_ngram_size_ablation(
    sampled_docs: dict[str, list[dict]],
    ngram_sizes: list[int] = [1, 8, 13],
) -> dict[int, dict]:
    """Repeat overlap + Mann-Whitney for each n-gram size. Returns {n: results}."""
    ...

def run_arc_easy_ablation(
    sampled_docs: dict[str, list[dict]],
    ngram_sets_13: dict[str, set[str]],
) -> dict:
    """Add arc_easy to benchmark set, rerun overlap + test. Returns results dict."""
    ...

def run_subset_stratified_ablation(
    sampled_docs: dict[str, list[dict]],
    ngram_sets: dict[str, set[str]],
) -> dict[str, dict]:
    """Compute overlap differences within each Pile subset separately.
    Returns {subset_name: {bench: mann_whitney_result}}."""
    ...

def run_all_ablations(
    sampled_docs: dict[str, list[dict]],
    ngram_sets: dict[str, set[str]],
    checkpoint_path: Path = CHECKPOINT_DIR / "ablation_results.json",
) -> dict:
    """Orchestrates all ablation variants, saves to JSON."""
    ...
```

---

### Visualizer (`visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy, config

Reuses `sig_stars()` pattern from h-e1/code/visualize.py.

```python
def sig_stars(p_value: float | None) -> str:
    """*** / ** / * / ns markers matching h-e1 convention."""
    ...

def plot_overlap_bar(
    overlap_scores: dict, stats: dict, out: Path = FIGURES_DIR / "overlap_bar.png"
) -> None:
    """Bar chart: mean 13-gram overlap (removed vs retained) per benchmark, 95% CI, sig stars."""
    ...

def plot_violin(
    overlap_scores: dict, out: Path = FIGURES_DIR / "overlap_violin.png"
) -> None:
    """Per-benchmark violin plots of overlap distributions (removed vs retained)."""
    ...

def plot_rank_correlation(
    stats: dict, out: Path = FIGURES_DIR / "rank_correlation.png"
) -> None:
    """Scatter: expected contamination rank vs observed mean overlap diff (4 benchmarks)."""
    ...

def plot_subset_breakdown(
    ablation_results: dict, out: Path = FIGURES_DIR / "subset_breakdown.png"
) -> None:
    """Bar: mean removed-doc overlap by Pile subset per benchmark."""
    ...

def generate_all_figures(overlap_scores: dict, stats: dict, ablation_results: dict) -> None:
    ...
```

---

### Pipeline (`pipeline.py`)

**Dependencies:** all modules, config

```python
def run(resume: bool = True) -> None:
    """End-to-end pipeline with checkpoint/resume at each stage.
    Stages: hash_diff → sample → ngrams → overlaps → stats → ablations → figures
    Each stage skips if checkpoint file exists and resume=True."""
    ...

if __name__ == "__main__":
    import argparse
    # --no-resume flag to force rerun from scratch
    ...
```

---

## Epic Tasks

| ID | Task | Description | Module_Size | Dependencies | Algorithm | Integration | Total |
|----|------|-------------|-------------|--------------|-----------|-------------|-------|
| A-1 | Config & scaffold | config.py, requirements.txt, run_experiment.sh, figures/ dir | 2 | 0 | 0 | 0 | 2 |
| A-2 | Corpus streamer | SHA-256 streaming diff of Pile vs dedup-Pile (825GB); checkpoint | 4 | 3 | 2 | 1 | 10 |
| A-3 | Stratified sampler | Reservoir sampling by Pile subset; proportional matching | 4 | 3 | 4 | 2 | 13 |
| A-4 | Benchmark n-grams | lm_eval API extraction; 13-gram set build for 4 benchmarks | 2 | 1 | 2 | 1 | 6 |
| A-5 | Overlap computer | Per-doc 13-gram overlap; multiprocessing.Pool; checkpoint JSON | 4 | 3 | 2 | 2 | 11 |
| A-6 | Statistical tester | Mann-Whitney U, Bonferroni, rank-biserial r, Spearman rho | 2 | 1 | 4 | 2 | 9 |
| A-7 | Ablation runner | 8-gram/unigram/ARC-Easy/subset-stratified variants | 4 | 5 | 2 | 4 | 15 |
| A-8 | Visualizer | 4 required figures; sig_stars reuse from h-e1 | 4 | 3 | 2 | 2 | 11 |
| A-9 | Pipeline orchestrator | Checkpoint/resume over all 7 stages; CLI args | 2 | 5 | 0 | 4 | 11 |

**Distribution**: High(14-17): [A-7], Medium(9-13): [A-2, A-3, A-5, A-6, A-8, A-9], Low(4-8): [A-4], VeryLow(1-3): [A-1]

---

## External Dependencies (Base Hypothesis)

| Module | Reuse | Source Location |
|--------|-------|-----------------|
| BENCHMARKS constant | Copy | `h-e1/code/statistical_tests.py:13` |
| CORRECTED_ALPHA = 0.0125 | Copy | `h-e1/code/statistical_tests.py:14` |
| sig_stars() | Copy | `h-e1/code/visualize.py:22-30` |
| matplotlib Agg backend pattern | Copy | `h-e1/code/visualize.py:6-7` |
| JSON intermediate file pattern | Follow | all h-e1 code modules |

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation, not spec)

**New dependencies (requirements.txt additions):** `datasets`, `lm_eval`, `scipy`, `numpy`, `matplotlib`, `seaborn`
