# Architecture: h-e1 — Contamination Geometry Decomposition Exists

**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Date:** 2026-05-13

Applied: pipeline-module-separation pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — green-field implementation
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior code to analyze.

---

## File Organization

```
h-e1/
├── code/
│   ├── config.py              # Fixed experiment config (seed, paths, thresholds)
│   ├── data_loader.py         # Benchmark + corpus loading
│   ├── index_builder.py       # 13-gram + SBERT FAISS index construction
│   ├── geometry_features.py   # GeometryStratifier: feature extraction + stratum assignment
│   ├── ground_truth.py        # Approach A (known inclusion) + B (simulated injection)
│   ├── detectors/
│   │   ├── __init__.py
│   │   ├── ngram_detector.py       # Detector Family 1: EleutherAI 13-gram
│   │   ├── embedding_detector.py   # Detector Family 2: LLMSanitize embedding similarity
│   │   ├── minkpp_detector.py      # Detector Family 3: Min-K%++
│   │   ├── dcpdd_detector.py       # Detector Family 4: DC-PDD
│   │   └── constat_detector.py     # Detector Family 5: ConStat
│   ├── evaluate.py            # Per-stratum recall/F1, variance, indeterminacy, bootstrap CI
│   ├── visualize.py           # All 5 figures → h-e1/figures/
│   └── run_experiment.py      # Entrypoint: orchestrates full pipeline
├── figures/                   # Auto-saved output figures
└── results/                   # Intermediate + final metrics (JSON/YAML)
```

---

## Module Structure

### Config (`code/config.py`)

**Dependencies**: none

```python
class ExperimentConfig:
    seed: int = 42
    ngram_n: int = 13
    ngram_buckets: int = 500
    sbert_model: str = "all-MiniLM-L6-v2"
    sbert_batch_size: int = 256
    faiss_index_type: str = "IndexFlatIP"
    stratum_percentile: float = 75.0
    minkpp_k: float = 0.20
    bootstrap_n: int = 10_000
    contamination_rate: float = 0.10
    corpora: list = ["pile", "c4", "redpajama"]
    benchmarks: list = ["mmlu", "hellaswag", "gsm8k"]
    figures_dir: str = "h-e1/figures/"
    results_dir: str = "h-e1/results/"
    index_dir: str = "h-e1/indices/"

def get_config() -> ExperimentConfig: ...
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: Config

```python
class BenchmarkLoader:
    def load_mmlu(self) -> Dataset: ...
    def load_hellaswag(self) -> Dataset: ...
    def load_gsm8k(self) -> Dataset: ...
    def load_all_benchmarks(self) -> dict[str, Dataset]: ...
    def get_item_texts(self, dataset: Dataset, name: str) -> list[str]: ...

class CorpusLoader:
    def load_pile(self) -> IterableDataset: ...
    def load_c4(self) -> IterableDataset: ...
    def load_redpajama(self) -> IterableDataset: ...
    def stream_corpus_texts(self, corpus: IterableDataset, max_docs: int) -> Iterator[str]: ...
```

---

### IndexBuilder (`code/index_builder.py`)

**Dependencies**: Config, CorpusLoader

```python
class NgramIndexBuilder:
    def __init__(self, cfg: ExperimentConfig): ...
    def build_index(self, corpus_name: str, corpus_stream: Iterator[str]) -> None: ...
    def load_index(self, corpus_name: str) -> "NgramIndex": ...

class NgramIndex:
    def max_overlap(self, text: str, n: int = 13) -> int: ...
    def is_contaminated(self, text: str, n: int = 13) -> bool: ...

class SBERTIndexBuilder:
    def __init__(self, cfg: ExperimentConfig): ...
    def build_index(self, corpus_name: str, corpus_texts: list[str]) -> None: ...
    def load_index(self, corpus_name: str) -> "SBERTIndex": ...

class SBERTIndex:
    def search(self, query_texts: list[str], k: int = 1) -> tuple[np.ndarray, np.ndarray]: ...
```

---

### GeometryStratifier (`code/geometry_features.py`)

**Dependencies**: Config, NgramIndex, SBERTIndex

```python
class GeometryStratifier:
    def __init__(self, cfg: ExperimentConfig): ...
    def compute_geometry_features(
        self,
        benchmark_texts: list[str],
        ngram_index: NgramIndex,
        sbert_index: SBERTIndex,
    ) -> tuple[np.ndarray, np.ndarray]: ...  # (ngram_counts, cosines) shape (N,)

    def compute_thresholds(
        self, ngram_counts: np.ndarray, cosines: np.ndarray
    ) -> tuple[float, float]: ...  # (lexical_thresh, semantic_thresh)

    def assign_strata(
        self,
        ngram_counts: np.ndarray,
        cosines: np.ndarray,
        lexical_thresh: float,
        semantic_thresh: float,
    ) -> np.ndarray: ...  # str array: "lexical" | "semantic" | "indeterminate"
```

---

### GroundTruth (`code/ground_truth.py`)

**Dependencies**: Config, BenchmarkLoader

```python
class GroundTruthGenerator:
    def __init__(self, cfg: ExperimentConfig): ...

    # Approach A: known inclusion audit (Pythia-7B / The Pile)
    def approach_a_pile_labels(
        self, benchmark_texts: list[str], ngram_index: NgramIndex
    ) -> np.ndarray: ...  # binary labels shape (N,)

    # Approach B: simulated injection (3 regimes)
    def approach_b_uniform(
        self, benchmark_texts: list[str], corpus_name: str
    ) -> tuple[list[str], np.ndarray]: ...

    def approach_b_clustered(
        self, benchmark_texts: list[str], corpus_name: str
    ) -> tuple[list[str], np.ndarray]: ...

    def approach_b_paraphrased(
        self, benchmark_texts: list[str], corpus_name: str
    ) -> tuple[list[str], np.ndarray]: ...
```

---

### Detectors (`code/detectors/`)

**Dependencies**: Config

```python
# ngram_detector.py
class NgramDetector:
    def __init__(self, cfg: ExperimentConfig): ...
    def predict(self, texts: list[str], ngram_index: NgramIndex) -> np.ndarray: ...  # binary (N,)

# embedding_detector.py
class EmbeddingDetector:
    def __init__(self, cfg: ExperimentConfig): ...
    def predict(self, texts: list[str], sbert_index: SBERTIndex, threshold: float) -> np.ndarray: ...

# minkpp_detector.py
class MinkPPDetector:
    def __init__(self, cfg: ExperimentConfig, model_name: str): ...
    def predict(self, texts: list[str]) -> np.ndarray: ...  # binary (N,)
    def score(self, texts: list[str]) -> np.ndarray: ...    # float scores (N,)

# dcpdd_detector.py
class DCPDDDetector:
    def __init__(self, cfg: ExperimentConfig, ref_model_name: str = "EleutherAI/pythia-2.8b"): ...
    def predict(self, texts: list[str]) -> np.ndarray: ...

# constat_detector.py
class ConStatDetector:
    def __init__(self, cfg: ExperimentConfig): ...
    def predict(self, texts: list[str]) -> np.ndarray: ...
```

---

### Evaluator (`code/evaluate.py`)

**Dependencies**: Config, all Detectors, GeometryStratifier

```python
class StratifiedEvaluator:
    def __init__(self, cfg: ExperimentConfig): ...

    def per_stratum_recall(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        strata: np.ndarray,
    ) -> dict[str, float]: ...  # {"lexical": float, "semantic": float, "indeterminate": float}

    def per_stratum_f1(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        strata: np.ndarray,
    ) -> dict[str, float]: ...

    def minkpp_f1_variance(
        self,
        f1_per_corpus: list[float],
    ) -> float: ...

    def indeterminacy_rate(
        self,
        detector_f1_matrix: np.ndarray,  # shape (N_items, N_detectors)
    ) -> float: ...

    def bootstrap_ci(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        metric_fn: callable,
        n_iterations: int = 10_000,
    ) -> tuple[float, float]: ...  # (lower_95, upper_95)

    def run_full_evaluation(
        self,
        benchmark_name: str,
        corpus_name: str,
        y_true: np.ndarray,
        strata: np.ndarray,
        detector_preds: dict[str, np.ndarray],
    ) -> dict: ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: Config

```python
class ResultVisualizer:
    def __init__(self, cfg: ExperimentConfig): ...

    def gate_metrics_bar(self, metrics: dict) -> None: ...
    # Saves: figures/gate_metrics.png

    def phase_diagram_scatter(
        self,
        ngram_counts: np.ndarray,
        cosines: np.ndarray,
        dominant_detector: np.ndarray,
        strata: np.ndarray,
    ) -> None: ...
    # Saves: figures/phase_diagram.png

    def stratum_f1_heatmap(
        self,
        f1_matrix: np.ndarray,  # shape (5_detectors, 3_strata, 3_corpora)
        detector_names: list[str],
    ) -> None: ...
    # Saves: figures/stratum_f1_heatmap.png

    def minkpp_variance_bar(self, f1_by_corpus: dict) -> None: ...
    # Saves: figures/minkpp_variance.png

    def indeterminacy_pie(self, stratum_counts: dict) -> None: ...
    # Saves: figures/indeterminacy_pie.png
```

---

### Experiment Runner (`code/run_experiment.py`)

**Dependencies**: all modules

```python
def setup_environment(cfg: ExperimentConfig) -> None: ...
def build_indices(cfg: ExperimentConfig) -> None: ...
def run_geometry_pipeline(cfg: ExperimentConfig) -> dict: ...
def run_detector_evaluation(cfg: ExperimentConfig, geometry_results: dict) -> dict: ...
def run_metrics(cfg: ExperimentConfig, eval_results: dict) -> dict: ...
def generate_figures(cfg: ExperimentConfig, metrics: dict) -> None: ...

if __name__ == "__main__":
    # CUDA_VISIBLE_DEVICES must be set before launch
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment & Data Loading | Setup project structure, install deps (llmsanitize, faiss, sentence-transformers, mink-plus-plus clone), load MMLU/HellaSwag/GSM8K benchmarks and stream corpora | 8 | 2+2+2+2 |
| A-2 | Corpus Index Construction | Build 13-gram inverted indices via EleutherAI pipeline for all 3 corpora; build SBERT FAISS IndexFlatIP indices with all-MiniLM-L6-v2; handle streaming OOM | 14 | 3+3+4+4 |
| A-3 | Geometry Features & Stratification | Implement GeometryStratifier: compute max 13-gram count + max SBERT cosine per item×corpus; top-quartile thresholds; assign lexical/semantic/indeterminate strata | 10 | 3+2+3+2 |
| A-4 | Ground Truth Generation | Implement Approach A (Pythia-7B/Pile known inclusion) + Approach B (3 injection regimes via llm-decontaminator): uniform, clustered, paraphrased | 12 | 3+3+3+3 |
| A-5 | Detector Families (5 total) | Implement all 5 detectors: NgramDetector, EmbeddingDetector (LLMSanitize), MinkPPDetector (zjysteven/run.py), DCPDDDetector (Pythia-2.8B ref), ConStatDetector | 15 | 4+3+4+4 |
| A-6 | Evaluation & Metrics | Per-stratum recall/F1 for n-gram detector; Min-K%++ F1 variance across 3 corpora; indeterminacy rate; bootstrap CI (N=10,000); check PoC pass conditions | 11 | 3+3+3+2 |
| A-7 | Visualization & Results | Generate all 5 figures (gate metrics bar, phase diagram scatter, F1 heatmap, MinkPP variance bar, indeterminacy pie); save to h-e1/figures/; write results JSON | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-5], Medium(9-13): [A-3, A-4, A-6], Low(4-8): [A-1, A-7]

---

## External Dependencies

| Library / Repo | Install | Key Entry Point |
|----------------|---------|----------------|
| zjysteven/mink-plus-plus | `git clone` + local import | `run.py --method minkpp` |
| EleutherAI/lm-evaluation-harness | `git clone` + pip install | `scripts/clean_training_data/`, `lm_eval/decontaminate.py` |
| ntunlp/LLMSanitize | `pip install llmsanitize` | embedding similarity + ConStat methods |
| lm-sys/llm-decontaminator | `git clone` | paraphrased injection (Approach B) |
| sentence-transformers | `pip install` | `SentenceTransformer("all-MiniLM-L6-v2")` |
| faiss-gpu | `pip install faiss-gpu` | `faiss.IndexFlatIP` |

---

*Generated by Phase 3 Architecture Agent — EXISTENCE PoC*
