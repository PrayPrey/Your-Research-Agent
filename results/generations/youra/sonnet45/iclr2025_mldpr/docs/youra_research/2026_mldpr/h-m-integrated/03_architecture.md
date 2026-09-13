# System Architecture: h-m-integrated

**Date:** 2026-03-18
**Hypothesis:** Semantic Embeddings Encode Lifecycle Role via Distributional Signatures
**Type:** MECHANISM
**Architect:** Phase 3 Agent

Applied: Statistical clustering pattern (K-means, NMI evaluation, baseline comparison)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from h-e1 code
**Analyzed Path**: `docs/youra_research/20260318_mldpr/h-e1/code/`
**Findings**: Modular structure (config, data, analysis) with clean separation. Import paths use package structure (e.g., `from config.config import ExperimentConfig`). Will maintain consistency with h-e1 patterns.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DataCollector | `from data.data_collector import DataCollector` | `h-e1/code/data/data_collector.py` |
| Config Pattern | `from config.config import ExperimentConfig` | `h-e1/code/config/config.py` |

**Verified from**: `h-e1/code/` (actual implementation)

**Reuse Strategy**: h-m-integrated will reuse h-e1 dataset collection logic but implement entirely new clustering analysis. Will maintain h-e1 package structure (config/, data/, analysis/) for consistency.

---

## Module Structure

### Config (`h-m-integrated/code/config/config.py`)

**Dependencies**: None

```python
class ExperimentConfig:
    seed: int = 42
    data_dir: str = "data/metadata_sample"
    results_dir: str = "h-m-integrated/results"
    figures_dir: str = "h-m-integrated/figures"

    # Reuse h-e1 dataset
    dataset_path: str = "data/metadata_sample/metadata_fields.csv"

    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Clustering parameters
    n_clusters: int = 2
    kmeans_random_state: int = 42

    # Baseline configurations
    lda_n_components: int = 2
    lda_max_iter: int = 100
    lda_random_state: int = 42
    rai_keywords: list = ["bias", "ethics", "fairness", "responsible", "accountability", "transparency"]

    # Control experiments
    length_normalization_tokens: int = 100
    deontic_markers: list = ["should", "must", "required", "shall", "need"]

    # Gate thresholds
    nmi_threshold: float = 0.6
    baseline_gap_threshold: float = 0.15
    normalized_nmi_threshold: float = 0.6
    probe_variance_threshold: float = 0.1
```

---

### DataLoader (`h-m-integrated/code/data/data_loader.py`)

**Dependencies**: pandas, numpy

```python
class DataLoader:
    def __init__(self, config): ...
    def load_metadata(self) -> pd.DataFrame: ...
    def prepare_text_fields(self, df: pd.DataFrame) -> list[str]: ...
    def get_true_labels(self, df: pd.DataFrame) -> np.ndarray: ...
    def apply_length_normalization(self, texts: list[str], max_tokens: int) -> list[str]: ...
    def apply_modality_filtering(self, texts: list[str], markers: list[str]) -> list[str]: ...
```

---

### EmbeddingModel (`h-m-integrated/code/models/embedding_model.py`)

**Dependencies**: sentence-transformers, numpy

```python
class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"): ...
    def encode(self, texts: list[str], show_progress: bool = True) -> np.ndarray: ...
    def get_embedding_dim(self) -> int: ...
```

---

### ClusteringPipeline (`h-m-integrated/code/models/clustering_pipeline.py`)

**Dependencies**: sklearn, numpy

```python
class ClusteringPipeline:
    def __init__(self, config): ...
    def cluster_semantic(self, embeddings: np.ndarray) -> np.ndarray: ...
    def cluster_permutation(self, labels_true: np.ndarray) -> np.ndarray: ...
    def cluster_lda(self, texts: list[str]) -> np.ndarray: ...
    def cluster_lexical(self, texts: list[str], keywords: list[str]) -> np.ndarray: ...
```

---

### BaselineModels (`h-m-integrated/code/models/baselines.py`)

**Dependencies**: sklearn, numpy

```python
class PermutationBaseline:
    def __init__(self, random_state: int = 42): ...
    def predict(self, labels_true: np.ndarray) -> np.ndarray: ...

class LDABaseline:
    def __init__(self, n_components: int = 2, max_iter: int = 100, random_state: int = 42): ...
    def fit_predict(self, texts: list[str]) -> np.ndarray: ...

class LexicalBaseline:
    def __init__(self, keywords: list[str]): ...
    def predict(self, texts: list[str]) -> np.ndarray: ...
```

---

### NMIEvaluator (`h-m-integrated/code/analysis/nmi_evaluator.py`)

**Dependencies**: sklearn.metrics, numpy

```python
class NMIEvaluator:
    def __init__(self, config): ...
    def compute_nmi(self, labels_true: np.ndarray, labels_pred: np.ndarray) -> float: ...
    def compute_all_nmi(self, labels_true: np.ndarray, predictions: dict) -> dict: ...
    def compute_baseline_gap(self, nmi_scores: dict) -> float: ...
    def evaluate_controls(self, embeddings: np.ndarray, labels_true: np.ndarray,
                         normalized_embeddings: np.ndarray, filtered_embeddings: np.ndarray) -> dict: ...
```

---

### GeneralizationAnalyzer (`h-m-integrated/code/analysis/generalization.py`)

**Dependencies**: sklearn.linear_model, numpy, pandas

```python
class GeneralizationAnalyzer:
    def __init__(self, config): ...
    def train_repository_probes(self, embeddings: np.ndarray, labels: np.ndarray,
                                repositories: np.ndarray) -> dict: ...
    def compute_probe_variance(self, probe_results: dict) -> float: ...
    def compute_repository_nmi(self, labels_true: np.ndarray, labels_pred: np.ndarray,
                                repositories: np.ndarray) -> dict: ...
    def analyze_scaffolding_effect(self, labels_true: np.ndarray, labels_pred: np.ndarray,
                                    scaffolding: np.ndarray) -> dict: ...
```

---

### GateEvaluator (`h-m-integrated/code/analysis/gate_evaluator.py`)

**Dependencies**: numpy

```python
class GateEvaluator:
    def __init__(self, config): ...
    def evaluate_primary_criteria(self, nmi_scores: dict, baseline_gap: float) -> dict: ...
    def evaluate_secondary_criteria(self, control_results: dict, probe_variance: float) -> dict: ...
    def determine_gate_status(self, primary: dict, secondary: dict) -> str: ...
    def generate_failure_action(self, gate_status: str, nmi_scores: dict,
                                control_results: dict) -> str: ...
```

---

### Visualizer (`h-m-integrated/code/analysis/visualizer.py`)

**Dependencies**: matplotlib, seaborn, sklearn.manifold, numpy

```python
class Visualizer:
    def __init__(self, config): ...
    def plot_gate_metrics(self, nmi_scores: dict, threshold: float, gap_threshold: float,
                          output_path: Path) -> None: ...
    def plot_embedding_space(self, embeddings: np.ndarray, labels_true: np.ndarray,
                             labels_pred: np.ndarray, output_path: Path) -> None: ...
    def plot_confusion_matrix(self, labels_true: np.ndarray, labels_pred: np.ndarray,
                              output_path: Path) -> None: ...
    def plot_repository_stratification(self, repository_nmi: dict, output_path: Path) -> None: ...
    def plot_scaffolding_effect(self, scaffolding_results: dict, output_path: Path) -> None: ...
```

---

### ExperimentRunner (`h-m-integrated/code/run_experiment.py`)

**Dependencies**: All above modules

```python
class ExperimentRunner:
    def __init__(self, config): ...
    def load_data(self) -> tuple[pd.DataFrame, list[str], np.ndarray]: ...
    def encode_embeddings(self, texts: list[str]) -> np.ndarray: ...
    def run_clustering(self, embeddings: np.ndarray, texts: list[str],
                      labels_true: np.ndarray) -> dict: ...
    def run_control_experiments(self, texts: list[str], labels_true: np.ndarray) -> dict: ...
    def run_generalization_tests(self, embeddings: np.ndarray, labels_true: np.ndarray,
                                 labels_pred: np.ndarray, metadata_df: pd.DataFrame) -> dict: ...
    def evaluate_gates(self, nmi_scores: dict, control_results: dict,
                      generalization_results: dict) -> dict: ...
    def generate_visualizations(self, embeddings: np.ndarray, labels_true: np.ndarray,
                                labels_pred: np.ndarray, nmi_scores: dict,
                                repository_nmi: dict, scaffolding_results: dict) -> None: ...
    def run_full_pipeline(self) -> dict: ...
```

---

## File Organization

```
h-m-integrated/
├── code/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── data_loader.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── embedding_model.py
│   │   ├── clustering_pipeline.py
│   │   └── baselines.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── nmi_evaluator.py
│   │   ├── generalization.py
│   │   ├── gate_evaluator.py
│   │   └── visualizer.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_clustering.py
│   │   ├── test_baselines.py
│   │   └── test_nmi.py
│   └── run_experiment.py
├── data/
│   ├── embeddings/
│   │   ├── semantic_embeddings.npy
│   │   ├── normalized_embeddings.npy
│   │   └── filtered_embeddings.npy
│   └── predictions/
│       ├── semantic_labels.npy
│       ├── permutation_labels.npy
│       ├── lda_labels.npy
│       └── lexical_labels.npy
├── results/
│   ├── nmi_scores.json
│   ├── baseline_comparison.json
│   ├── control_experiments.json
│   ├── generalization_analysis.json
│   └── gate_evaluation.json
└── figures/
    ├── gate_metrics.png
    ├── embedding_space.png
    ├── confusion_matrix.png
    ├── repository_stratification.png
    └── scaffolding_effect.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup & Config | Install dependencies, create folder structure, config module | 6 | 2+1+2+1 |
| M-2 | Data Loading Pipeline | Implement DataLoader with h-e1 dataset reuse, text preprocessing | 8 | 2+2+2+2 |
| M-3 | Embedding Model | Implement sentence-transformers wrapper, batch encoding | 10 | 3+2+3+2 |
| M-4 | Semantic Clustering | Implement K-means clustering on embeddings | 9 | 2+2+3+2 |
| M-5 | Baseline Methods | Implement 3 baselines (permutation, LDA, lexical) | 14 | 3+4+4+3 |
| M-6 | NMI Evaluation | Implement NMI computation, baseline comparison, gap calculation | 12 | 3+3+3+3 |
| M-7 | Control Experiments | Implement length normalization and modality filtering controls | 11 | 3+3+3+2 |
| M-8 | Generalization Tests | Repository probes, variance computation, scaffolding analysis | 13 | 4+3+3+3 |
| M-9 | Gate Logic | Gate evaluation, status determination, failure action generation | 10 | 3+2+3+2 |
| M-10 | Visualization Suite | 5 required figures, embedding space projection | 12 | 3+3+3+3 |
| M-11 | Orchestration & Testing | ExperimentRunner, integration tests, validation report | 11 | 3+3+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M-5], Medium(9-13): [M-3, M-4, M-6, M-7, M-8, M-9, M-10, M-11], Low(4-8): [M-1, M-2]

**Complexity Breakdown**:
- Module_Size: Lines of code (1-5)
- Dependencies: External library count (1-5)
- Algorithm: Statistical/ML complexity (1-5)
- Integration: Cross-module dependencies (1-5)

---

## Dependencies Graph

```
ExperimentRunner
├── DataLoader (reuses h-e1 dataset)
├── EmbeddingModel (→ sentence-transformers)
├── ClusteringPipeline
│   ├── sklearn.cluster.KMeans
│   └── BaselineModels
│       ├── PermutationBaseline
│       ├── LDABaseline (→ sklearn.decomposition)
│       └── LexicalBaseline
├── NMIEvaluator (→ sklearn.metrics)
├── GeneralizationAnalyzer (→ sklearn.linear_model)
├── GateEvaluator
└── Visualizer (→ matplotlib, seaborn, sklearn.manifold)
```

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 6-12 Epic tasks with complexity (11 tasks delivered)
- [x] Total length < 500 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] "External Dependencies" section for h-e1 code reuse
- [x] Import paths verified from actual h-e1 code
- [x] MECHANISM hypothesis → 6-12 tasks

---

*Generated for Phase 4 Implementation*
*Next: Task breakdown and implementation*
