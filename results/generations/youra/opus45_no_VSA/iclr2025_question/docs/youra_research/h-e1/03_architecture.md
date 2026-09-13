# Architecture: h-e1 (EXISTENCE PoC)

**Hypothesis**: NTI (layers 24-32) achieves AUROC > 0.55 on TruthfulQA MC1

Applied: hook-based activation caching pattern (TransformerLens `run_with_cache`, from experiment brief; no closer KB match found).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (no base_hypothesis folder, no code/ directory present)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure (EXISTENCE - minimal)

```
h-e1/code/
├── config.py       # fixed config (seed, layers, model id, paths)
├── data.py         # TruthfulQA MC1 loading + 5-fold splits
├── model.py        # NTI + baseline entropy extraction (HookedTransformer)
├── evaluate.py      # LogisticRegression CV, AUROC, pass rate
├── visualize.py     # 4 required figures
└── run.py           # orchestrates: data -> model -> evaluate -> visualize
```

---

## Module Interfaces

### config.py

```python
SEED = 42
MODEL_ID = "meta-llama/Llama-2-7b-hf"
TARGET_LAYERS = (24, 32)
N_FOLDS = 5
AUROC_THRESHOLD = 0.55
MIN_FOLD_THRESHOLD = 0.52
FIGURES_DIR = "figures/"
```

### data.py (`code/data.py`)

**Dependencies**: config

```python
def load_truthfulqa_mc1() -> list[dict]: ...
    # returns [{"question": str, "choices": list[str], "labels": list[int]}, ...]

def build_prompts(samples: list[dict]) -> list[tuple[str, int]]: ...
    # flattens to (prompt_text, is_correct) pairs, one per choice

def stratified_folds(labels: list[int], n_folds: int = 5, seed: int = 42):
    # -> StratifiedKFold split indices (train_idx, test_idx) generator
```

### model.py (`code/model.py`)

**Dependencies**: config, TransformerLens

```python
def load_model(model_id: str, device: str = "cuda") -> "HookedTransformer": ...

def compute_nti(model, input_ids, target_layers: tuple[int, int]) -> tuple["Tensor", "Tensor"]: ...
    # returns (nti_scores[batch], entropy_trajectory[batch, num_layers])

def compute_baseline_entropy(model, input_ids) -> "Tensor": ...
    # final-layer entropy, for comparison only

def extract_all_scores(model, prompts: list[str]) -> dict: ...
    # returns {"nti": np.ndarray, "trajectory": np.ndarray, "baseline_entropy": np.ndarray}
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config, sklearn

```python
def run_cv(nti_scores: "np.ndarray", labels: "np.ndarray", n_folds: int = 5, seed: int = 42) -> dict: ...
    # returns {"fold_aurocs": list[float], "mean_auroc": float, "min_auroc": float,
    #          "pass_rate": float, "roc_curves": list[tuple[fpr, tpr]]}

def check_gate(cv_results: dict) -> bool: ...
    # applies AUROC_THRESHOLD / MIN_FOLD_THRESHOLD / pass_rate>=4/5
```

### visualize.py (`code/visualize.py`)

**Dependencies**: config, matplotlib

```python
def plot_gate_metrics(cv_results: dict, save_path: str) -> None: ...   # required
def plot_entropy_heatmap(trajectory: "np.ndarray", save_path: str) -> None: ...
def plot_nti_distribution(nti_scores, labels, save_path: str) -> None: ...
def plot_roc_curves(cv_results: dict, save_path: str) -> None: ...
```

### run.py (`code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # load data -> load model -> extract_all_scores -> run_cv -> check_gate -> visualize -> print summary
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & config | config.py, deps, seeding | 4 | 1+1+1+1 |
| A-2 | Data pipeline | Load TruthfulQA MC1, build prompts, stratified folds | 7 | 2+2+2+1 |
| A-3 | Model loading | HookedTransformer load, fp16, CUDA | 6 | 2+3+1+0 |
| A-4 | NTI extraction | compute_nti + compute_baseline_entropy via run_with_cache | 10 | 3+2+4+1 |
| A-5 | Batch score extraction | extract_all_scores over 817 samples, perf within 2hr | 8 | 3+2+2+1 |
| A-6 | Evaluation pipeline | 5-fold CV, LogisticRegression, AUROC/pass-rate/gate | 7 | 2+2+2+1 |
| A-7 | Visualization | 4 required figures | 6 | 2+1+2+1 |
| A-8 | Integration run | run.py end-to-end orchestration + smoke test | 5 | 2+2+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5], Low(4-8): [A-1, A-2, A-3, A-6, A-7, A-8]

---

## Notes

- No training required (EXISTENCE PoC, metric extraction only).
- No ablation modules (layer-contribution ablation figure is optional/LLM-autonomous, implemented inline in visualize.py if time allows, not a separate module).
- No external base-hypothesis code to import (foundation hypothesis, first in chain).
