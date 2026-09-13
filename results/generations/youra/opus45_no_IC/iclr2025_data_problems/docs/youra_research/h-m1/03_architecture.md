# Architecture: H-M1 (MECHANISM)

**Applied**: No matching KB pattern found (searched "n-gram contamination detection architecture", "data pipeline design patterns" — only unrelated diffusers/LAION results); used standard hash-set n-gram overlap pattern from EleutherAI lm-evaluation-harness reference (per experiment brief).

## Codebase Analysis (Serena)

**Project Type**: green-field (with prior-hypothesis reference)
**Status**: h-e1 (`docs/youra_research/h-e1/code/`) exists but implements a different pipeline (checkpoint eval + capability detrending + Spearman correlation) and delegates n-gram overlap to `lm_eval.decontamination` rather than defining a standalone detector. No `NgramExtractor`/`PileIndexer`/`BenchmarkLoader`/`OverlapDetector` symbols exist to reuse.
**Analyzed Path**: `docs/youra_research/h-e1/code/contamination.py`
**Findings**: h-e1's `compute_ngram_overlap(task, n=13)` wraps lm-eval-harness's decontamination module directly — confirms 13-gram + lowercase-whitespace tokenization convention, but no code artifact to import. H-M1 builds the mechanism standalone (own Pile indexing + benchmark-scoped overlap detector) per PRD FR-1/FR-2, since h-e1 never built its own index.

---

## Overview

Data pipeline (no model): tokenize + hash 13-grams from The Pile (subset), index them, extract 13-grams from 4 benchmark test sets, compute per-item and per-benchmark overlap %, aggregate stats, visualize.

## File Structure

- `code/config.py` — fixed paths, n=13, benchmark dataset ids, Pile subset size
- `code/ngram_utils.py` — NgramExtractor (tokenize + extract)
- `code/pile_indexer.py` — PileIndexer (build hash-set index from Pile subset)
- `code/benchmark_loader.py` — BenchmarkLoader (HF datasets -> text items)
- `code/overlap_detector.py` — OverlapDetector (match items against index)
- `code/aggregator.py` — ResultsAggregator (per-benchmark stats)
- `code/visualize.py` — Visualizer (bar chart, histograms)
- `code/run.py` — orchestrates end-to-end
- `figures/` — output plots

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
NGRAM_SIZE = 13
PILE_SUBSET_DOCS = 200_000  # representative subset, not full 825GB (out of scope per PRD)
PILE_DATASET = "EleutherAI/pile"  # or local jsonl.zst path
BENCHMARKS = {
    "mmlu": ("cais/mmlu", "all", "test"),
    "arc_challenge": ("allenai/ai2_arc", "ARC-Challenge", "test"),
    "hellaswag": ("Rowan/hellaswag", None, "validation"),
    "winogrande": ("allenai/winogrande", "winogrande_xl", "validation"),
}
OVERLAP_THRESHOLD = 0.01  # 1%
SEED = 1
```

### NgramExtractor (`code/ngram_utils.py`)

**Dependencies**: Config

```python
def tokenize(text: str) -> list[str]:
    """Lowercase, whitespace split."""

def extract_ngrams(tokens: list[str], n: int = 13) -> set[str]: ...

def ngram_hash(ngram: str) -> int:
    """64-bit hash (e.g. hashlib.blake2b truncated) for compact index storage."""

def extract_ngram_hashes(text: str, n: int = 13) -> set[int]:
    """tokenize -> extract_ngrams -> hash each. Single entry point used by indexer + detector."""
```

### PileIndexer (`code/pile_indexer.py`)

**Dependencies**: NgramExtractor, datasets (HF)

```python
class PileIndexer:
    def __init__(self, ngram_size: int = 13): ...
    def build_from_stream(self, doc_iter: Iterable[str], max_docs: int | None = None) -> None:
        """Streams Pile docs, updates self.index: set[int] of ngram hashes."""
    def save(self, path: str) -> None:
        """Persist index (pickle or plain hash-list file)."""
    def load(self, path: str) -> None: ...
    index: set[int]
```

### BenchmarkLoader (`code/benchmark_loader.py`)

**Dependencies**: Config, datasets (HF)

```python
def load_benchmark(name: str) -> list[dict]:
    """Returns [{'id': str, 'text': str}] — text = concatenated relevant fields
    (question+choices for MMLU/ARC, ctx+endings for HellaSwag, sentence+options for WinoGrande)."""

def load_all_benchmarks() -> dict[str, list[dict]]: ...
```

### OverlapDetector (`code/overlap_detector.py`)

**Dependencies**: NgramExtractor, PileIndexer

```python
class OverlapDetector:
    def __init__(self, pile_index: set[int], ngram_size: int = 13): ...
    def compute_item_overlap(self, text: str) -> dict:
        """Returns {'overlap': float, 'matched': int, 'total': int}."""
    def compute_benchmark_overlap(self, items: list[dict]) -> list[dict]:
        """Returns per-item results with 'id' preserved."""
```

### ResultsAggregator (`code/aggregator.py`)

**Dependencies**: OverlapDetector output, statistics (stdlib)

```python
def aggregate_benchmark(per_item_results: list[dict]) -> dict:
    """Returns {mean_overlap, median_overlap, max_overlap, items_above_1pct, total_items}."""

def aggregate_all(results_by_benchmark: dict[str, list[dict]]) -> dict[str, dict]: ...

def check_gate(aggregated: dict[str, dict], threshold: float = 0.01) -> dict:
    """Returns {'pass': bool, 'benchmarks_above_threshold': list[str], 'max_overlap_benchmark': str}."""
```

### Visualizer (`code/visualize.py`)

**Dependencies**: aggregator output, matplotlib

```python
def plot_overlap_by_benchmark(aggregated: dict[str, dict], out_path: str) -> None: ...
def plot_overlap_histogram(results_by_benchmark: dict[str, list[dict]], out_path: str) -> None: ...
def plot_comparison_with_prior_work(aggregated: dict[str, dict], out_path: str) -> None:
    """Overlay Yang et al. RedPajama 8-18% reference band."""
```

### Run (`code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """1) PileIndexer.build_from_stream (subset) 2) load_all_benchmarks
    3) OverlapDetector per benchmark 4) aggregate_all 5) check_gate
    6) generate figures 7) print pass/fail + save results json."""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | Paths, n=13, benchmark ids, subset size | 3 | 1+1+1+0 |
| A-2 | NgramExtractor | Tokenize, extract, hash 13-grams | 6 | 2+1+2+1 |
| A-3 | PileIndexer | Stream Pile subset, build hash-set index, save/load | 12 | 4+3+3+2 |
| A-4 | BenchmarkLoader | Load + flatten text for MMLU/ARC/HellaSwag/WinoGrande | 8 | 3+3+1+1 |
| A-5 | OverlapDetector | Match benchmark ngrams vs Pile index, per-item results | 8 | 2+3+2+1 |
| A-6 | ResultsAggregator | Per-benchmark stats + gate check (>1% threshold) | 6 | 2+2+1+1 |
| A-7 | Visualizer | Bar chart, histograms, prior-work comparison | 7 | 3+1+1+2 |
| A-8 | Orchestration | run.py end-to-end + mechanism verify_mechanism() self-check | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-4, A-5, A-6, A-7, A-8]
