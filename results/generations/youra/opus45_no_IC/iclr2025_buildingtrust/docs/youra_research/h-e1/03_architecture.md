# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** Category-dependent calibration variation exists in LLMs on TruthfulQA
**Type:** EXISTENCE — minimal architecture to test "does it work?"

Applied: canonical ECE binning (gpleiss/temperature_scaling pattern) — no other KB pattern matched (search returned unrelated diffusion-model results).

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** No existing code to analyze for h-e1 (only an unrelated archived CIFAR-10-C artifact from a prior routing-recovery run exists under `_archive/`, not applicable to this hypothesis)
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

---

## File Structure

```
docs/youra_research/h-e1/code/
├── config.py
├── data.py
├── model.py
├── metrics.py
├── train.py       # entry point: run inference + analysis + figures
└── figures/        # output dir
```

---

## Modules

### config.py

**Dependencies**: none

```python
SEED = 42
MODEL_ID = "meta-llama/Llama-2-7b-hf"
DATASET_ID = "truthfulqa/truthful_qa"
N_BINS = 15
N_BOOTSTRAP = 100
BATCH_SIZE = 8
ALPHA = 0.05
CATEGORY_TO_CLUSTER: dict[str, int]  # 38 -> 7 mapping (see brief appendix)
CLUSTER_NAMES: dict[int, str]
```

### data.py

**Dependencies**: config

```python
def load_truthfulqa_mc() -> "datasets.Dataset": ...
def assign_clusters(dataset) -> "datasets.Dataset":
    """Adds 'cluster_id' column via CATEGORY_TO_CLUSTER."""
def validate_cluster_sizes(dataset, min_size: int = 50) -> dict[int, int]: ...
```

### model.py

**Dependencies**: config

```python
def load_model_and_tokenizer(model_id: str = MODEL_ID): ...
def score_choices(model, tokenizer, question: str, choices: list[str], device) -> list[float]:
    """Returns log-prob sum per choice."""
def predict(question: str, choices: list[str], correct_idx: int, model, tokenizer, device) -> dict:
    """Returns {confidence: float, correct: bool, cluster_id: int}."""
```

### metrics.py

**Dependencies**: config

```python
def compute_ece(confidences: "Tensor", accuracies: "Tensor", n_bins: int = N_BINS) -> float: ...
def compute_cluster_eces(results_by_cluster: dict[int, dict]) -> dict[int, float]: ...
def bootstrap_cluster_ece(confidences, accuracies, n_bootstrap: int = N_BOOTSTRAP) -> "np.ndarray":
    """Resample with replacement, return array of ECE estimates."""
def run_anova(bootstrap_samples_by_cluster: dict[int, "np.ndarray"]) -> tuple[float, float]:
    """Returns (f_stat, p_value)."""
def bonferroni_pairwise(bootstrap_samples_by_cluster: dict[int, "np.ndarray"]) -> dict[tuple[int,int], float]: ...
def confidence_interval(samples: "np.ndarray", ci: float = 0.95) -> tuple[float, float]: ...
```

### train.py (entry point)

**Dependencies**: config, data, model, metrics, matplotlib

```python
def run_inference(dataset, model, tokenizer, device) -> list[dict]:
    """Iterate questions, call model.predict, collect per-question records."""
def aggregate_by_cluster(records: list[dict]) -> dict[int, dict]:
    """Group confidences/accuracies by cluster_id."""
def plot_cluster_ece_bar(cluster_eces, cis, path): ...
def plot_reliability_diagrams(records_by_cluster, path_dir): ...
def plot_confidence_histograms(records_by_cluster, path_dir): ...
def save_results_json(results: dict, path): ...
def save_validation_md(gate_pass: bool, results: dict, path): ...
def main(): ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load TruthfulQA MC split, map 38 categories to 7 clusters, validate sizes | 8 | 2+2+2+2 |
| A-2 | Model loading & inference | Load Llama-2-7B fp16, implement log-prob scoring per choice, batch predict loop | 12 | 3+3+3+3 |
| A-3 | ECE computation | Implement 15-bin ECE, per-cluster ECE aggregation | 6 | 2+1+2+1 |
| A-4 | Bootstrap + ANOVA | Bootstrap resampling (100 iter) per cluster, one-way ANOVA, Bonferroni post-hoc | 9 | 2+2+3+2 |
| A-5 | Visualization | Bar chart w/ CI, reliability diagrams, confidence histograms | 7 | 2+1+2+2 |
| A-6 | Results & gate report | Write 04_results.json and 04_validation.md with gate evaluation | 5 | 1+1+1+2 |
| A-7 | End-to-end run & validation | Wire train.py main(), execute full pipeline, verify runtime < 2h | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-7, A-1], Low(4-8): [A-3, A-5, A-6]

---

## Self-Check
- Green-field project, no base code reuse -> External Dependencies section omitted (N/A).
- 7 Epic tasks (within 4-8 range for EXISTENCE).
- Minimal file structure (single model.py/train.py/config.py, no ablation modules).
