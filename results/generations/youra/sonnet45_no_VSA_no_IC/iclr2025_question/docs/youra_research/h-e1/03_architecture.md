# Architecture: h-e1 - Uncertainty Quantification for Selective Prediction

**Date:** 2026-08-20
**Hypothesis:** EXISTENCE
**Status:** PoC (Proof of Concept)

Applied: Minimal PoC structure pattern

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Existing h-e1 implementation found - IGNORE (different hypothesis)
**Analyzed Path:** experiments/h-e1/ (temperature-based conformal prediction)
**Findings:** Previous h-e1 tested temperature sweep (0.05-0.2). Current h-e1 tests 6 UQ methods (temp scaling, conformal, MC dropout k=1/3/5/10). Clean slate implementation.

---

## Module Structure

### DataLoader (`data/loader.py`)

**Dependencies:** None

```python
class TruthfulQALoader:
    def __init__(self, seed: int = 42): ...
    def load_and_split(self, cal_ratio: float = 0.4) -> tuple[list[dict], list[dict]]: ...
    def label_correctness(self, question: str, answer: str, correct_answers: list[str]) -> int: ...
```

### ModelWrapper (`models/llama_wrapper.py`)

**Dependencies:** transformers

```python
class LlamaWrapper:
    def __init__(self, model_id: str, cache_dir: str): ...
    def generate(self, questions: list[str], batch_size: int = 8) -> list[tuple[str, torch.Tensor]]: ...
    def enable_dropout(self, rate: float = 0.1): ...
```

### UQMethods (`uq/methods.py`)

**Dependencies:** ModelWrapper

```python
class TemperatureScaling:
    def calibrate(self, cal_data: list[dict], model: LlamaWrapper) -> float: ...
    def compute_uncertainty(self, logits: torch.Tensor, T: float) -> float: ...

class ConformalPrediction:
    def calibrate(self, cal_data: list[dict], model: LlamaWrapper, alpha: float = 0.1) -> float: ...
    def compute_uncertainty(self, logits: torch.Tensor) -> float: ...

class MCDropout:
    def __init__(self, k: int = 5): ...
    def compute_uncertainty(self, questions: list[str], model: LlamaWrapper) -> list[float]: ...
```

### Evaluator (`evaluate.py`)

**Dependencies:** UQMethods, sklearn

```python
def compute_auroc(y_true: list[int], uncertainties: list[float]) -> float: ...
def compute_spearman(uncertainties: list[float], incorrectness: list[int]) -> float: ...
def check_gate(auroc_scores: dict[str, float], threshold: float = 0.7) -> bool: ...
```

### Visualizer (`visualize.py`)

**Dependencies:** matplotlib, Evaluator

```python
def plot_auroc_comparison(auroc_scores: dict[str, float], threshold: float, save_path: str): ...
def plot_uncertainty_distributions(test_data: list[dict], uncertainties_by_method: dict, save_path: str): ...
def plot_roc_curves(fpr_tpr_by_method: dict, save_path: str): ...
```

### Runner (`run_experiment.py`)

**Dependencies:** All above

```python
def main():
    # 1. Load data
    # 2. Load model
    # 3. Generate answers + logits
    # 4. Calibrate methods (temp scaling, conformal)
    # 5. Compute uncertainties (6 methods)
    # 6. Evaluate AUROC
    # 7. Visualize results
    # 8. Check gate
```

---

## File Organization

```
experiments/h-e1/
├── data/
│   └── loader.py              # TruthfulQA loading + splitting
├── models/
│   └── llama_wrapper.py       # Llama-3.1-8B inference wrapper
├── uq/
│   └── methods.py             # 6 UQ methods (temp, conformal, mc_k1/3/5/10)
├── evaluate.py                # AUROC + Spearman computation
├── visualize.py               # 3 plots (AUROC bar, distributions, ROC curves)
├── run_experiment.py          # Main runner
└── config.py                  # Model ID, batch size, seed, temperatures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load TruthfulQA, 40/60 split, label correctness | 7 | 2+1+2+2 |
| A-2 | Model inference | Llama wrapper, batch generation, logit extraction | 9 | 3+2+2+2 |
| A-3 | Baseline UQ (temp + conformal) | Temperature scaling + conformal prediction | 11 | 3+2+3+3 |
| A-4 | MC dropout variants | k=1/3/5/10 forward passes + entropy | 13 | 4+2+4+3 |
| A-5 | Evaluation + visualization | AUROC, Spearman, 3 plots, gate check | 10 | 2+2+3+3 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5], Low(4-8): [A-1]

---

## Implementation Notes

### PoC Simplifications

1. **No ensemble methods**: Single Llama-3.1-8B model only
2. **No hyperparameter tuning**: Fixed dropout rate (0.1), alpha (0.1)
3. **Single seed**: 42 (no variance measurement across seeds)
4. **Fixed k values**: 1, 3, 5, 10 (no adaptive early stopping)

### Gate Condition

```python
max_auroc = max(auroc_scores.values())
if max_auroc >= 0.70:
    print("GATE PASSED: Proceed to H-M1")
else:
    print("GATE FAILED: Document 8B limitation")
```

---

## Dependencies

```python
torch>=2.0.0
transformers>=4.36.0
datasets>=2.14.0
sklearn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
scipy>=1.11.0
```

---

## Success Validation

**PoC Pass Conditions:**
1. Code runs without error on 817 TruthfulQA questions
2. At least one UQ method achieves AUROC ≥ 0.70

**Primary Metric:** max(AUROC across 6 methods)
**Secondary Metrics:** Spearman ρ > 0.2 (sanity check)
