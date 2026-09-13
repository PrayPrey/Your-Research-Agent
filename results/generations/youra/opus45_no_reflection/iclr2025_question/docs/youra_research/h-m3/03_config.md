# Config: H-M3 (Linear Correctness Probe)

Applied: Standard PyTorch/sklearn dataclass config (no direct Archon KB match for probe configs)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass (single frozen config, matches architecture's `config.py`)

---

## A-1..A-10: Full Pipeline Config [Complexity: pooled, Budget: 61]

**Applied**: Standard sklearn defaults + values fixed by architecture/PRD (no tuning — this is a single fixed run, not a sweep)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class HM3Config:
    # Reproducibility
    seed: int = 42

    # Data
    d_model: int = 4096
    n_train: int = 9500
    n_val: int = 1700
    layer: str = "l15"
    h_m2_folder: str = "../h-m2"  # relative to hypothesis_folder
    hidden_states_file: str = "hidden_states_l15.pt"
    labels_file: str = "correctness_labels.pt"

    # Random baseline
    baseline_n_seeds: int = 5  # for CI, seeds = [seed, seed+1, ..., seed+4]

    # Linear probe (LogisticRegression)
    probe_C: float = 1e-3
    probe_max_iter: int = 2000
    probe_solver: str = "lbfgs"
    probe_class_weight: str = "balanced"

    # MLP fallback (only run if probe AUROC < auroc_gate)
    mlp_hidden_layer_sizes: tuple = (256,)
    mlp_max_iter: int = 500
    mlp_early_stopping: bool = True

    # Gates / thresholds
    auroc_gate: float = 0.70
    mechanism_auroc_min: float = 0.55  # mechanism verification floor
    weight_norm_min: float = 1e-6
    pred_std_min: float = 0.01

    # Output paths (resolved at runtime relative to hypothesis_folder)
    figures_dir: str = "figures"
    gate_comparison_fig: str = "figures/gate_comparison.png"
    roc_curve_fig: str = "figures/roc_curve.png"
    results_json: str = "results.json"
```

### YAML Config Example

```yaml
seed: 42
d_model: 4096
n_train: 9500
n_val: 1700
layer: "l15"
h_m2_folder: "../h-m2"
hidden_states_file: "hidden_states_l15.pt"
labels_file: "correctness_labels.pt"

baseline_n_seeds: 5

probe_C: 0.001
probe_max_iter: 2000
probe_solver: "lbfgs"
probe_class_weight: "balanced"

mlp_hidden_layer_sizes: [256]
mlp_max_iter: 500
mlp_early_stopping: true

auroc_gate: 0.70
mechanism_auroc_min: 0.55
weight_norm_min: 1.0e-6
pred_std_min: 0.01

figures_dir: "figures"
gate_comparison_fig: "figures/gate_comparison.png"
roc_curve_fig: "figures/roc_curve.png"
results_json: "results.json"
```

### Subtasks [10/10 used — pooled from architecture Epic Tasks]

| ID | Subtask | Description |
|----|---------|--------------|
| A-1 | Data loading | Load `.pt` hidden states/labels via `HM3Config.h_m2_folder` paths, verify shape (11200, 4096) |
| A-2 | Train/val split + scaling | Split using `n_train`/`n_val`, fit `StandardScaler` on train only |
| A-3 | Random baseline | `RandomBaseline(d_model, seed)` over `baseline_n_seeds` seeds for CI |
| A-4 | Linear probe implementation | `LinearCorrectnessProbe(C=probe_C, max_iter=probe_max_iter)` |
| A-5 | Probe training run | Fit on scaled train, track `clf.n_iter_` for convergence |
| A-6 | Evaluation metrics | AUROC/accuracy via sklearn.metrics, compare vs baseline |
| A-7 | Mechanism verification | Assert `weight_norm_min`, `pred_std_min`, `mechanism_auroc_min` |
| A-8 | Fallback MLP protocol | If AUROC < `auroc_gate`, train `MLPClassifier(mlp_hidden_layer_sizes, mlp_max_iter, mlp_early_stopping)` |
| A-9 | Visualization | Save `gate_comparison_fig`, `roc_curve_fig` |
| A-10 | End-to-end orchestration | `train.py main()` writes `results_json` |

---

## Hyperparameter Summary

| Param | Value | Source |
|-------|-------|--------|
| seed | 42 | PRD NFR-2 |
| d_model | 4096 | Llama-3-8B hidden size |
| n_train / n_val | 9500 / 1700 | PRD FR-1.4 |
| probe_C | 1e-3 | concept-probes / SEP reference |
| probe_max_iter | 2000 | PRD FR-3.2 |
| probe_solver | lbfgs | PRD FR-3.2 |
| probe_class_weight | balanced | PRD FR-3.2 (handle class imbalance) |
| mlp_hidden_layer_sizes | (256,) | PRD FR-7.2 fallback |
| mlp_max_iter | 500 | PRD FR-7.2 fallback |
| auroc_gate | 0.70 | PRD success gate |
| mechanism_auroc_min | 0.55 | PRD FR-5.3 |
| weight_norm_min | 1e-6 | PRD FR-5.1 |
| pred_std_min | 0.01 | PRD FR-5.2 |
| baseline_n_seeds | 5 | Experiment brief (CI on random baseline) |
