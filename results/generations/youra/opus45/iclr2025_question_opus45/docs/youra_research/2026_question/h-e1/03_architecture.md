# Architecture: h-e1 SEDP Existence Validation

**Hypothesis**: EXISTENCE (PoC) - SEDP vs SEP baseline on TruthfulQA
**Applied**: sklearn-logistic-regression-probe pattern (OATML/semantic-entropy-probes)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis code exists

---

## File Structure

- `h-e1/code/`
  - `config.py` - single fixed config
  - `data_pipeline.py` - dataset loading + response generation + hidden state extraction
  - `se_labels.py` - SE label computation via DeBERTa NLI clustering
  - `similarity_features.py` - response embedding + cosine similarity statistics
  - `model.py` - SEP baseline + SEDP probe classes
  - `train.py` - training loop
  - `evaluate.py` - metrics + visualization
  - `run_experiment.py` - end-to-end orchestration entry point
- `h-e1/figures/` - output PNG files
- `h-e1/cache/` - intermediate tensors (.pt, .npy, .json)

---

## Module Definitions

### Config (`h-e1/code/config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    # Data
    dataset_name: str = "truthfulqa/truthful_qa"
    dataset_config: str = "generation"
    test_size: float = 0.2
    seed: int = 42

    # Generation
    llm_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    n_responses: int = 20
    temperature: float = 0.7
    max_new_tokens: int = 100
    layer_idx: int = 25

    # SE labels
    nli_model_name: str = "microsoft/deberta-v3-large-mnli"
    entailment_threshold: float = 0.5

    # Probe
    probe_C: float = 1.0
    probe_max_iter: int = 1000

    # Paths
    cache_dir: str = "h-e1/cache"
    figures_dir: str = "h-e1/figures"
    results_path: str = "h-e1/04_validation.md"
```

---

### DataPipeline (`h-e1/code/data_pipeline.py`)

**Dependencies**: Config

```python
class DataPipeline:
    def __init__(self, config: ExperimentConfig): ...

    def load_dataset(self) -> tuple[list[str], list[str]]:
        """Returns (train_questions, test_questions)."""
        ...

    def generate_responses(
        self, questions: list[str]
    ) -> tuple[np.ndarray, list[list[str]]]:
        """
        Returns:
            hidden_states: (N, hidden_dim=4096) - TBG token, layer 25
            responses: list of list[str], shape (N, n_responses)
        """
        ...

    def load_or_generate(
        self, questions: list[str], split: str
    ) -> tuple[np.ndarray, list[list[str]]]:
        """Cache-aware wrapper: load from cache_dir or call generate_responses."""
        ...
```

---

### SELabelGenerator (`h-e1/code/se_labels.py`)

**Dependencies**: Config

```python
class SELabelGenerator:
    def __init__(self, config: ExperimentConfig): ...

    def check_entailment(self, premise: str, hypothesis: str) -> bool: ...

    def get_semantic_clusters(self, responses: list[str]) -> list[int]:
        """Bidirectional NLI entailment. Returns cluster id per response."""
        ...

    def compute_se(self, responses: list[str]) -> float:
        """H_SE = -sum(p_i * log(p_i)) over semantic clusters."""
        ...

    def compute_se_labels(
        self, all_responses: list[list[str]]
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns:
            se_continuous: (N,) float SE values
            se_binary: (N,) int high/low labels (median threshold)
        """
        ...

    def load_or_compute(
        self, all_responses: list[list[str]], split: str
    ) -> tuple[np.ndarray, np.ndarray]: ...
```

---

### SimilarityFeatureExtractor (`h-e1/code/similarity_features.py`)

**Dependencies**: Config

```python
class SimilarityFeatureExtractor:
    def __init__(self, config: ExperimentConfig): ...

    def embed_responses(self, responses: list[str]) -> np.ndarray:
        """Returns (n_responses, embed_dim) via sentence-transformers."""
        ...

    def compute_similarity_stats(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Args: embeddings (n_responses, embed_dim)
        Returns: (4,) [mean, std, min, max] of upper-triangle cosine similarities
        """
        ...

    def extract_features(
        self, all_responses: list[list[str]]
    ) -> np.ndarray:
        """Returns (N, 4) similarity feature matrix."""
        ...

    def load_or_extract(
        self, all_responses: list[list[str]], split: str
    ) -> np.ndarray: ...
```

---

### Model (`h-e1/code/model.py`)

**Dependencies**: Config

```python
class SEProbe:
    """Baseline SEP: logistic regression on hidden states only."""
    def __init__(self, config: ExperimentConfig): ...
    def fit(self, hidden_states: np.ndarray, labels: np.ndarray) -> None: ...
    def predict_proba(self, hidden_states: np.ndarray) -> np.ndarray:
        """Returns (N,) positive class probabilities."""
        ...

class SEDProbe:
    """Proposed SEDP: logistic regression on hidden states + similarity features."""
    def __init__(self, config: ExperimentConfig): ...
    def fit(
        self,
        hidden_states: np.ndarray,
        sim_features: np.ndarray,
        labels: np.ndarray
    ) -> None: ...
    def predict_proba(
        self,
        hidden_states: np.ndarray,
        sim_features: np.ndarray
    ) -> np.ndarray:
        """Concatenates [hidden_states, sim_features] -> (N, 4100) then predicts."""
        ...
```

---

### Train (`h-e1/code/train.py`)

**Dependencies**: Config, SEProbe, SEDProbe

```python
def train_sep(
    config: ExperimentConfig,
    hidden_states_train: np.ndarray,
    labels_train: np.ndarray
) -> SEProbe: ...

def train_sedp(
    config: ExperimentConfig,
    hidden_states_train: np.ndarray,
    sim_features_train: np.ndarray,
    labels_train: np.ndarray
) -> SEDProbe: ...
```

---

### Evaluate (`h-e1/code/evaluate.py`)

**Dependencies**: Config, SEProbe, SEDProbe

```python
def compute_metrics(
    probe_proba: np.ndarray,
    se_continuous: np.ndarray,
    se_binary: np.ndarray
) -> dict:
    """Returns {'spearman_rho': float, 'p_value': float, 'auroc': float}"""
    ...

def plot_gate_metrics(
    sep_metrics: dict,
    sedp_metrics: dict,
    save_path: str
) -> None:
    """Bar chart: rho values for SEP vs SEDP with threshold line at 0.3."""
    ...

def plot_scatter(
    sep_proba: np.ndarray,
    sedp_proba: np.ndarray,
    se_true: np.ndarray,
    save_path: str
) -> None: ...

def plot_roc_curves(
    sep_proba: np.ndarray,
    sedp_proba: np.ndarray,
    se_binary: np.ndarray,
    save_path: str
) -> None: ...

def save_results(
    sep_metrics: dict,
    sedp_metrics: dict,
    output_path: str
) -> None:
    """Write markdown metrics table to h-e1/04_validation.md."""
    ...
```

---

### RunExperiment (`h-e1/code/run_experiment.py`)

**Dependencies**: all modules

```python
def run(config: ExperimentConfig) -> dict:
    """
    End-to-end pipeline:
    1. Load dataset
    2. Generate responses + extract hidden states (train + test)
    3. Compute SE labels
    4. Extract similarity features
    5. Train SEP and SEDP
    6. Evaluate and save results
    Returns final metrics dict.
    """
    ...

if __name__ == "__main__":
    config = ExperimentConfig()
    results = run(config)
```

---

## Module Dependency Order

- `config.py` (no deps)
- `data_pipeline.py` <- config
- `se_labels.py` <- config
- `similarity_features.py` <- config
- `model.py` <- config
- `train.py` <- config, model
- `evaluate.py` <- config, model
- `run_experiment.py` <- all above

---

## Cache Strategy

| Artifact | File | Trigger |
|----------|------|---------|
| `hidden_states_{split}.pt` | cache/ | If missing, run Llama-3-8B |
| `responses_{split}.json` | cache/ | If missing, run Llama-3-8B |
| `se_labels_{split}.npy` | cache/ | If missing, run DeBERTa NLI |
| `sim_features_{split}.npy` | cache/ | If missing, run embedder |

Cache avoids re-running Llama-3-8B (~2-4h) on reruns.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Data Loading | Project structure, TruthfulQA HF loading, train/test split (seed=42) | 6 | 2+1+1+2 |
| A-2 | Response Generation & Hidden State Extraction | Llama-3-8B-Instruct generation loop (N=20, temp=0.7), layer-25 TBG hidden state extraction, disk cache | 16 | 4+3+4+5 |
| A-3 | SE Label Generation | DeBERTa-v3 bidirectional NLI clustering, SE entropy formula, binary label binarization (median), disk cache | 15 | 4+3+4+4 |
| A-4 | Similarity Feature Computation | Sentence-transformers embedding, pairwise cosine similarity stats (mean/std/min/max), disk cache | 10 | 3+2+3+2 |
| A-5 | Probe Training (SEP + SEDP) | SEP logistic regression (4096 features), SEDP logistic regression (4100 features), sklearn LBFGS | 9 | 3+2+2+2 |
| A-6 | Evaluation & Visualization | Spearman rho, AUROC, gate check (rho>=0.3), 3 figures (bar/scatter/ROC), write 04_validation.md | 11 | 3+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-3], Medium(9-13): [A-4, A-5, A-6], Low(4-8): [A-1]
