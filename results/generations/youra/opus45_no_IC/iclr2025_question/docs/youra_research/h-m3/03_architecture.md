# Architecture: H-M3 (MECHANISM)

**Hypothesis**: Within-cluster benchmark pairs show successful threshold transfer (AUROC degradation ≤ 0.08)
**Gate**: SHOULD_WORK, fail action: EXPLORE tighter cluster criteria

Applied: no directly relevant KB pattern found (KB returned unrelated diffusion/CUDA docs for both "threshold transfer calibration" and "semantic entropy AUROC" queries); using sklearn.metrics.roc_curve/roc_auc_score standard FPR-threshold calibration pattern per experiment brief.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 provides reusable semantic entropy pipeline; H-E1 provides cluster assignments)
**Status**: Patterns found from base code — H-M1's `code/` has a working generation → entailment-clustering → semantic-entropy → correctness pipeline for TriviaQA. H-E1's `code/` has multi-benchmark `data.py`/`generate.py`/`entropy.py` for all 6 benchmarks already (cluster assignments came from this).
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-e1/code/`
**Findings**:
- `h-m1/code/response_generator.py::ResponseGenerator.generate_n(question, n, temperature) -> (responses, logprobs)`
- `h-m1/code/entailment_clusterer.py::EntailmentClusterer.cluster(responses, question) -> list[list[int]]`
- `h-m1/code/semantic_entropy.py::compute_semantic_entropy(responses, logprobs, clusterer, question) -> float`
- `h-m1/code/correctness.py::label_responses(responses, gold_aliases) -> list[bool]` (token-F1 based)
- H-E1's `code/data.py` already loads all 6 benchmarks (TriviaQA, NQ, SQuAD, PopQA, HaluEval, FEVER) — reuse loader pattern instead of H-M1's single-benchmark `data_loader.py`.
- H-M1 only produced query-level `entropy_values.npy` + `correctness_labels.npy` for TriviaQA (700/300 split not present) — H-M3 must recompute entropy for all 6 benchmarks fresh with the calibration/eval split, reusing the pipeline classes, not H-M1's cached outputs.

---

## File Structure

```
h-m3/code/
  config.py           # benchmarks, cluster pairs, model names, seed, paths
  data.py              # load_benchmark(name) for all 6 HF datasets -> unified {question, aliases}
  entropy_pipeline.py  # wraps H-M1 classes: compute entropy+label arrays per benchmark
  calibration.py       # calibrate_threshold, evaluate_transfer, degradation calc
  transfer.py          # run all 6 within-cluster pairs (12 directional transfers), aggregate
  stats.py             # bootstrap_ci, mean degradation, gate check
  visualize.py          # bar chart, transfer heatmap, cluster scatter, box plot
  run.py                # orchestrates: data -> entropy -> calibration -> transfer -> stats -> viz -> gate log
h-m3/figures/
h-m3/outputs/           # cached entropy_{benchmark}.npy, labels_{benchmark}.npy, transfer_results.json
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ResponseGenerator | `from h_m1.code.response_generator import ResponseGenerator` | `h-m1/code/response_generator.py` |
| EntailmentClusterer | `from h_m1.code.entailment_clusterer import EntailmentClusterer` | `h-m1/code/entailment_clusterer.py` |
| compute_semantic_entropy | `from h_m1.code.semantic_entropy import compute_semantic_entropy` | `h-m1/code/semantic_entropy.py` |
| label_responses | `from h_m1.code.correctness import label_responses` | `h-m1/code/correctness.py` |
| Cluster assignments | hardcoded from H-E1 result (silhouette=0.8245, k=2) | `h-e1/03_architecture.md` (reference) |

**Verified from**: `h-m1/code/` (actual implementation, via Serena symbol inspection) and `h-m3/03_prd.md` FR-1/FR-7.

**Note**: Import path uses dotted module notation for illustration; Phase 4 Coder should resolve actual relative import mechanism (e.g., sys.path append or copy) based on repo layout — no `__init__.py`/package structure currently exists across hypothesis folders.

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
SEED = 42
BENCHMARKS = ["trivia_qa", "natural_questions", "squad", "pop_qa", "halueval_qa", "fever"]
CLUSTER_1 = ["trivia_qa", "natural_questions", "squad"]
CLUSTER_2 = ["pop_qa", "halueval_qa", "fever"]
WITHIN_CLUSTER_PAIRS = [  # 6 undirected pairs -> 12 directional transfers
    ("trivia_qa", "natural_questions"), ("trivia_qa", "squad"), ("natural_questions", "squad"),
    ("pop_qa", "halueval_qa"), ("pop_qa", "fever"), ("halueval_qa", "fever"),
]
SAMPLE_SIZE = 1000
CALIB_SPLIT = 0.7
TARGET_FPR = 0.1
GEN_MODEL = "meta-llama/Llama-2-7b-hf"
NLI_MODEL = "microsoft/deberta-v3-large"
N_GENERATIONS = 10
TEMPERATURE = 1.0
DEGRADATION_THRESHOLD = 0.08
CI_UPPER_THRESHOLD = 0.12
N_BOOTSTRAP = 1000
OUTPUTS_DIR = "h-m3/outputs"
FIGURES_DIR = "h-m3/figures"
```

### DataLoader (`data.py`)

**Dependencies**: config

```python
def load_benchmark(name: str, seed: int = SEED, n: int = SAMPLE_SIZE) -> list[dict]:
    """Dispatch to HF dataset loader per benchmark name.
    Returns: [{"question": str, "aliases": list[str]}], normalized across all 6 sources."""
def split_calib_eval(items: list[dict], calib_frac: float = CALIB_SPLIT, seed: int = SEED) -> tuple[list, list]:
    """Deterministic 70/30 split."""
```

### EntropyPipeline (`entropy_pipeline.py`)

**Dependencies**: config, data, H-M1 (ResponseGenerator, EntailmentClusterer, compute_semantic_entropy, label_responses)

```python
def compute_entropy_and_labels(items: list[dict], generator: "ResponseGenerator",
                                clusterer: "EntailmentClusterer") -> tuple[np.ndarray, np.ndarray]:
    """Per query: generate_n -> label_responses -> compute_semantic_entropy.
    Returns: (entropies[N], labels[N]) — labels = has_any_correct per query."""
def get_or_compute_benchmark_entropy(name: str, cache_dir: str = OUTPUTS_DIR) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load cached entropy_{name}.npy/labels_{name}.npy or compute fresh.
    Returns: (calib_entropies, calib_labels, eval_entropies, eval_labels)."""
```

### Calibration (`calibration.py`)

**Dependencies**: config

```python
def calibrate_threshold(entropies: np.ndarray, labels: np.ndarray, target_fpr: float = TARGET_FPR) -> float:
    """roc_curve-based threshold at target FPR."""
def evaluate_transfer(source_threshold: float, target_entropies: np.ndarray, target_labels: np.ndarray) -> dict:
    """Returns {"auroc": float, "threshold_used": float}."""
def compute_auroc_degradation(source_auroc: float, target_auroc: float) -> float:
    """source_auroc - target_auroc."""
```

### TransferRunner (`transfer.py`)

**Dependencies**: config, calibration, entropy_pipeline

```python
def run_pair_transfer(source: str, target: str, cache: dict) -> dict:
    """Calibrate on source eval-split AUROC + threshold; evaluate on target eval split.
    Returns: {"source": str, "target": str, "source_auroc": float, "target_auroc": float,
              "degradation": float, "source_threshold": float}."""
def run_all_transfers(pairs: list[tuple[str, str]]) -> list[dict]:
    """Runs 12 directional transfers (both directions per pair) across all benchmarks."""
```

### Stats (`stats.py`)

**Dependencies**: config

```python
def bootstrap_ci(degradations: list[float], n_bootstrap: int = N_BOOTSTRAP, ci: float = 0.95) -> tuple[float, float]: ...
def aggregate_results(transfer_results: list[dict]) -> dict:
    """Returns {"mean_degradation": float, "ci_lower": float, "ci_upper": float, "max_degradation": float}."""
def check_gate(agg: dict) -> bool:
    """mean_degradation <= 0.08 and ci_upper < 0.12."""
```

### Visualizer (`visualize.py`)

**Dependencies**: config

```python
def plot_degradation_bar(transfer_results: list[dict], threshold_line: float, out_path: str) -> None: ...
def plot_transfer_heatmap(transfer_results: list[dict], benchmarks: list[str], out_path: str) -> None: ...
def plot_cluster_scatter_with_arrows(transfer_results: list[dict], out_path: str) -> None: ...
def plot_within_vs_cross_box(within: list[float], cross: list[float], out_path: str) -> None: ...
```

### Orchestrator (`run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """load 6 benchmarks -> split calib/eval -> compute entropy (cache) ->
    run_all_transfers over WITHIN_CLUSTER_PAIRS -> aggregate_results -> check_gate ->
    visualize -> log gate decision to 04_validation.md"""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Config + multi-benchmark data loading | 6 HF dataset loaders unified schema, calib/eval split | 8 | 2+2+2+2 |
| M3-2 | Wire H-M1 pipeline classes | Import/adapt ResponseGenerator, EntailmentClusterer, compute_semantic_entropy, label_responses for 6 benchmarks | 10 | 2+3+3+2 |
| M3-3 | Entropy computation + caching | Run generation+entropy for 700+300 per benchmark (6x), cache to outputs/ | 12 | 3+2+3+4 |
| M3-4 | Threshold calibration module | calibrate_threshold via roc_curve at target FPR=0.1 | 5 | 1+1+2+1 |
| M3-5 | Cross-benchmark transfer evaluation | evaluate_transfer + degradation calc across 12 directional pairs | 8 | 2+2+2+2 |
| M3-6 | Statistical aggregation | Bootstrap CI (1000 samples), mean degradation, gate check | 6 | 1+1+2+2 |
| M3-7 | Visualization suite | Bar chart (required), heatmap, cluster scatter, box plot | 7 | 2+1+2+2 |
| M3-8 | Pipeline orchestration + gate logging | run.py wiring end-to-end, gate decision logged to 04_validation.md | 6 | 1+2+1+2 |
| M3-9 | Ablation studies (AB-1, AB-2) | FPR target sweep [0.05,0.10,0.15,0.20], calib split sweep [50/50..80/20] | 7 | 2+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M3-1, M3-2, M3-3], Low(4-8): [M3-4, M3-5, M3-6, M3-7, M3-8, M3-9]

---

## Data Flow

6 HF benchmarks -> DataLoader (unified schema, 70/30 split) -> EntropyPipeline (H-M1 ResponseGenerator + EntailmentClusterer + compute_semantic_entropy + label_responses, cached to outputs/) -> Calibration (per-benchmark threshold @ FPR=0.1 on calib split, AUROC on eval split) -> TransferRunner (12 directional within-cluster transfers) -> Stats (mean degradation, bootstrap CI, gate check vs 0.08/0.12) -> Visualizer (figures/) -> gate decision logged to 04_validation.md
