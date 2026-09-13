# Logic: H-M1 (13-gram Overlap Detection)

**Applied**: No matching KB pattern (searched "n-gram extraction API", "hash-based indexing" — only unrelated diffusers/LaTeX results); used stdlib `hashlib.blake2b` hash-set pattern per architecture doc.

## Codebase Analysis (Serena)

**Project Type**: green-field (with prior-hypothesis reference, non-reusable)
**Status**: h-e1 exists (`docs/youra_research/h-e1/code/contamination.py`) but delegates to `lm_eval.decontamination` — no `NgramExtractor`/`PileIndexer`/`BenchmarkLoader`/`OverlapDetector` symbols to import (confirmed in architecture doc's own Serena analysis). No further Serena lookup needed; designing new APIs per architecture spec.
**Analyzed Path**: N/A (green-field for this module set)
**Relevant Symbols**: None — new implementation

---

## Data Flow

```
Pile subset (HF stream) --tokenize+hash--> PileIndexer.index: set[int]
                                                    |
Benchmark HF datasets --load--> list[{id,text}] --tokenize+hash--> OverlapDetector
                                                                          |
                                                            per-item {overlap,matched,total}
                                                                          |
                                                        ResultsAggregator --> per-benchmark stats
                                                                          |
                                                              check_gate --> pass/fail
                                                                          |
                                                                    Visualizer --> figures/
```

---

## A-1: Config [Complexity: 3, Budget: 3]

**Applied**: Standard Python module constants.

```python
# code/config.py
NGRAM_SIZE: int = 13
PILE_SUBSET_DOCS: int = 200_000
PILE_DATASET: str = "EleutherAI/pile"
BENCHMARKS: dict[str, tuple[str, str | None, str]] = {
    "mmlu": ("cais/mmlu", "all", "test"),
    "arc_challenge": ("allenai/ai2_arc", "ARC-Challenge", "test"),
    "hellaswag": ("Rowan/hellaswag", None, "validation"),
    "winogrande": ("allenai/winogrande", "winogrande_xl", "validation"),
}
OVERLAP_THRESHOLD: float = 0.01
SEED: int = 1
```

No subtasks (complexity 3, atomic constants file).

---

## A-2: NgramExtractor [Complexity: 6, Budget: 6]

**Applied**: Standard sliding-window n-gram + blake2b truncated hash for compact int storage.

### API Signatures

```python
# code/ngram_utils.py
def tokenize(text: str) -> list[str]:
    """Lowercase, whitespace split."""

def extract_ngrams(tokens: list[str], n: int = 13) -> set[str]:
    """Sliding window join, space-separated ngram strings."""

def ngram_hash(ngram: str) -> int:
    """blake2b(ngram.encode(), digest_size=8) -> 64-bit int."""

def extract_ngram_hashes(text: str, n: int = 13) -> set[int]:
    """tokenize -> extract_ngrams -> {ngram_hash(g) for g in ngrams}. Entry point for indexer + detector."""
```

### Pseudo-code (sliding window)

```
tokens = tokenize(text)
if len(tokens) < n: return set()
ngrams = { " ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1) }
```

No subtasks (complexity 6, single-file utility, no external deps).

---

## A-3: PileIndexer [Complexity: 12, Budget: 12] — 2 subtasks

**Applied**: Streaming HF dataset iteration + in-memory hash-set index, pickle persistence (standard for ~200k doc subset; ~100GB full-scale storage per PRD NFR-1 is out of scope for subset PoC).

### API Signatures

```python
# code/pile_indexer.py
class PileIndexer:
    def __init__(self, ngram_size: int = 13) -> None:
        """self.index: set[int] = set()"""
        ...

    def build_from_stream(
        self,
        doc_iter: Iterable[str],
        max_docs: int | None = None,
    ) -> None:
        """Streams docs, calls extract_ngram_hashes per doc, unions into self.index.
        Progress via tqdm. Stops at max_docs."""
        ...

    def save(self, path: str) -> None:
        """pickle.dump(self.index, ...)"""
        ...

    def load(self, path: str) -> None:
        """pickle.load -> self.index"""
        ...

    index: set[int]
```

### Tensor/Data Shapes

| Variable | Type | Note |
|----------|------|------|
| doc_iter | Iterable[str] | HF `load_dataset(..., streaming=True)` text field iterator |
| self.index | set[int] | union of all 13-gram hashes across subset docs |

### Pseudo-code

```
def build_from_stream(doc_iter, max_docs):
    for i, doc_text in enumerate(tqdm(doc_iter)):
        if max_docs and i >= max_docs: break
        self.index |= extract_ngram_hashes(doc_text, self.ngram_size)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A3-1 | Streaming ingest + index build | `build_from_stream`: HF streaming iterator over `PILE_DATASET`, per-doc hash extraction, set union, tqdm progress, respects `max_docs=PILE_SUBSET_DOCS` |
| L-A3-2 | Persistence (save/load) | `save`/`load` via pickle; `__init__` state init; basic file-exists guard on load |

---

## A-4: BenchmarkLoader [Complexity: 8, Budget: 8]

**Applied**: Standard HF `datasets.load_dataset` + field concatenation per benchmark schema.

### API Signatures

```python
# code/benchmark_loader.py
def load_benchmark(name: str) -> list[dict]:
    """Returns [{'id': str, 'text': str}].
    MMLU: text = question + ' ' + ' '.join(choices)
    ARC: text = question + ' ' + ' '.join(choices['text'])
    HellaSwag: text = ctx + ' ' + ' '.join(endings)
    WinoGrande: text = sentence + ' ' + option1 + ' ' + option2"""

def load_all_benchmarks() -> dict[str, list[dict]]:
    """{name: load_benchmark(name) for name in Config.BENCHMARKS}"""
```

No subtasks (complexity 8, straightforward per-dataset field mapping, single file).

---

## A-5: OverlapDetector [Complexity: 8, Budget: 8]

**Applied**: Set-intersection overlap ratio, standard pattern per lm-eval-harness decontamination reference.

### API Signatures

```python
# code/overlap_detector.py
class OverlapDetector:
    def __init__(self, pile_index: set[int], ngram_size: int = 13) -> None: ...

    def compute_item_overlap(self, text: str) -> dict:
        """item_hashes = extract_ngram_hashes(text, self.ngram_size)
        matched = len(item_hashes & self.pile_index)
        total = len(item_hashes)
        Returns {'overlap': matched/total if total else 0.0, 'matched': matched, 'total': total}"""

    def compute_benchmark_overlap(self, items: list[dict]) -> list[dict]:
        """[{**compute_item_overlap(item['text']), 'id': item['id']} for item in items]"""
```

No subtasks (complexity 8, thin wrapper over A-2/A-3 primitives).

---

## A-6: ResultsAggregator [Complexity: 6, Budget: 6]

**Applied**: stdlib `statistics` module for mean/median.

### API Signatures

```python
# code/aggregator.py
def aggregate_benchmark(per_item_results: list[dict]) -> dict:
    """overlaps = [r['overlap'] for r in per_item_results]
    Returns {'mean_overlap': statistics.mean(overlaps), 'median_overlap': statistics.median(overlaps),
    'max_overlap': max(overlaps), 'items_above_1pct': sum(o > 0.01 for o in overlaps),
    'total_items': len(overlaps)}"""

def aggregate_all(results_by_benchmark: dict[str, list[dict]]) -> dict[str, dict]:
    """{name: aggregate_benchmark(results) for name, results in results_by_benchmark.items()}"""

def check_gate(aggregated: dict[str, dict], threshold: float = 0.01) -> dict:
    """above = [name for name, stats in aggregated.items() if stats['mean_overlap'] > threshold]
    Returns {'pass': len(above) > 0, 'benchmarks_above_threshold': above,
    'max_overlap_benchmark': max(aggregated, key=lambda k: aggregated[k]['mean_overlap'])}"""
```

No subtasks (complexity 6, stdlib-only stats aggregation).

---

## A-7: Visualizer [Complexity: 7, Budget: 7]

**Applied**: Standard matplotlib bar/histogram, reference band overlay per PRD FR-5.

### API Signatures

```python
# code/visualize.py
def plot_overlap_by_benchmark(aggregated: dict[str, dict], out_path: str) -> None:
    """Bar chart: x=benchmark names, y=mean_overlap, horizontal line at OVERLAP_THRESHOLD."""

def plot_overlap_histogram(results_by_benchmark: dict[str, list[dict]], out_path: str) -> None:
    """Subplot grid, one histogram of per-item 'overlap' values per benchmark."""

def plot_comparison_with_prior_work(aggregated: dict[str, dict], out_path: str) -> None:
    """Bar chart + shaded band [0.08, 0.18] labeled 'Yang et al. RedPajama'."""
```

No subtasks (complexity 7, straightforward matplotlib calls, no algorithmic logic).

---

## A-8: Orchestration [Complexity: 6, Budget: 6]

**Applied**: Standard sequential pipeline script + assert-based mechanism self-check per PRD Verification Protocol.

### API Signatures

```python
# code/run.py
def verify_mechanism() -> bool:
    """PRD FR-9 self-check: build tiny 2-doc index, confirm known-overlap text scores > 0.
    detector = OverlapDetector({...precomputed hashes of 'the quick brown fox...'...})
    assert detector.compute_item_overlap(test_text)['overlap'] > 0
    """

def main() -> None:
    """1) PileIndexer().build_from_stream(stream, max_docs=PILE_SUBSET_DOCS); save index
    2) load_all_benchmarks()
    3) OverlapDetector(index).compute_benchmark_overlap per benchmark
    4) aggregate_all -> check_gate
    5) plot_overlap_by_benchmark / plot_overlap_histogram / plot_comparison_with_prior_work
    6) print pass/fail, json.dump results to results.json"""
```

No subtasks (complexity 6, glue code calling A-1..A-7 APIs in sequence).
