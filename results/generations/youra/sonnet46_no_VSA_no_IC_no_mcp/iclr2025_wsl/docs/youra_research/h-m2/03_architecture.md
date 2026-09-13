# Architecture: H-M2 — PCA Concentration Test

**Date:** 2026-08-27
**Hypothesis Type:** MECHANISM (linear analysis, no neural network training)

Applied: Pipeline pattern (sequential data → PCA → regression stages)
Applied: Strategy pattern (Condition A / Condition D as interchangeable preprocessing strategies)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1 incremental continuation)
**Status:** Patterns found from base code (Read/Glob tools, Serena MCP unavailable)
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Findings:**
- `data_loader.py` has `load_zoo()` and `get_zoo_tensors()` — direct reuse for weight loading and label extraction. `EXPECTED_DIM = 51850` (not 50890 as brief states; brief is wrong — actual code is authoritative).
- `orbit_construction.py` has `construct_scaling_orbit()` and `construct_signflip_orbit()` — these operate on weight dicts; H-M2 needs numpy array versions for PCA pipeline. Adapt, do not call directly.
- No existing `apply_scaling_canon()` / `apply_sign_flip_canon()` functions in H-M1 code — brief references non-existent names.
- H-M1 `statistics.py` has bootstrap CI pattern reusable as reference.

---

## Module Structure

### `data_prep.py` (`h-m2/code/data_prep.py`)

**Dependencies:** H-M1 `data_loader.py` (via sys.path insert), numpy

```python
def load_and_flatten(seed: int = 42) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Returns X (N, 51850), Y (N, 3), label_names=['test_accuracy','generalization_gap','learning_rate']"""
    ...

def apply_condition_d(X: np.ndarray) -> np.ndarray:
    """Scaling (L2-norm per layer) then sign-flip (majority-sign, M=2). Returns (N, 51850)."""
    ...

def train_test_split_fixed(X: np.ndarray, Y: np.ndarray, test_size: int = 50, seed: int = 42
                           ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    ...
```

### `evaluate.py` (`h-m2/code/evaluate.py`)

**Dependencies:** numpy, sklearn

```python
def evaluate_pca_concentration(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    k_values: list[int],
    n_boot: int = 1000,
    seed: int = 42,
) -> dict:
    """Returns {k: {'r2': float, 'ci': [low, high]}} for each k in k_values."""
    ...

def verify_mechanism_preconditions(
    X_A_train: np.ndarray,
    X_D_train: np.ndarray,
) -> None:
    """Asserts canonicalization has effect and PCA is non-degenerate. Prints summary."""
    ...

def compare_conditions(
    results_a: dict,
    results_d: dict,
    k_gate: int = 20,
    n_tasks_required: int = 2,
) -> dict:
    """
    results_a / results_d: {label_name: {k: {'r2', 'ci'}}}
    Returns {'gate_pass': bool, 'per_task': {label: {'delta_r2', 'ci_nonoverlap', 'pass'}}}
    """
    ...
```

### `figures.py` (`h-m2/code/figures.py`)

**Dependencies:** matplotlib, numpy, evaluate.py results

```python
def plot_r2_bar_comparison(results_a: dict, results_d: dict, out_dir: str) -> None:
    """Figure 1 (mandatory): bar chart R²_A vs R²_D with CI error bars, per (k, label)."""
    ...

def plot_r2_vs_k(results_a: dict, results_d: dict, out_dir: str) -> None:
    """Figure 2: line plot R² vs k in {10,20,50} per label."""
    ...

def plot_explained_variance(pca_a: object, pca_d: object, out_dir: str) -> None:
    """Figure 3: cumulative explained variance ratio, Condition A vs D."""
    ...

def plot_ci_bars(results_a: dict, results_d: dict, k: int, out_dir: str) -> None:
    """Figure 4: horizontal CI bars at k=20, visual gate pass/fail."""
    ...

def plot_pc1_scatter(
    X_A_test_pca: np.ndarray,
    X_D_test_pca: np.ndarray,
    y_test: np.ndarray,
    label_name: str,
    out_dir: str,
) -> None:
    """Figure 5: PC1 vs property label scatter, Condition A vs D side-by-side."""
    ...

def generate_all_figures(
    results_a: dict,
    results_d: dict,
    pca_a: object,
    pca_d: object,
    X_A_test_pca: np.ndarray,
    X_D_test_pca: np.ndarray,
    Y_test: np.ndarray,
    label_names: list[str],
    out_dir: str,
) -> None: ...
```

### `main.py` (`h-m2/code/main.py`)

**Dependencies:** data_prep, evaluate, figures

```python
K_VALUES = [10, 20, 50]
SEED = 42
FIGURES_DIR = str(Path(__file__).parent.parent / "figures")
RESULTS_PATH = str(Path(__file__).parent.parent / "results.json")

def run(k_values: list[int] = K_VALUES, seed: int = SEED, figures_dir: str = FIGURES_DIR) -> dict: ...

if __name__ == "__main__":
    run()
```

---

## File Organization

```
h-m2/
├── code/
│   ├── main.py
│   ├── data_prep.py
│   ├── evaluate.py
│   └── figures.py
├── figures/           (generated at runtime)
├── results.json       (generated at runtime)
├── 02c_experiment_brief.md
└── 03_architecture.md
```

No `config.py` needed — constants live in `main.py` (3 values: K_VALUES, SEED, FIGURES_DIR).

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_zoo | `sys.path.insert(0, h_m1_code); from data_loader import load_zoo` | `h-m1/code/data_loader.py` |
| get_zoo_tensors | same | `h-m1/code/data_loader.py` |
| construct_scaling_orbit (reference) | not imported directly — logic adapted to numpy | `h-m1/code/orbit_construction.py` |
| construct_signflip_orbit (reference) | not imported directly — logic adapted to numpy | `h-m1/code/orbit_construction.py` |

**Verified from:** `docs/youra_research/h-m1/code/` (actual implementation)

**Note:** `apply_scaling_canon()` / `apply_sign_flip_canon()` cited in the experiment brief do NOT exist in H-M1 code. H-M2 `data_prep.py` will implement numpy equivalents adapted from `construct_scaling_orbit` / `construct_signflip_orbit`. Weight dimension is **51850** (not 50890 — trust actual `data_loader.py` `EXPECTED_DIM`).

---

## Proposed Epic Tasks

| ID | Task | Description | Type | Complexity | Breakdown |
|----|------|-------------|------|------------|-----------|
| E-1 | Setup project structure | Create h-m2/code/ files, figures/ dir, verify H-M1 data path resolves | setup | 4 | 1+1+1+1 |
| E-2 | Implement data_prep.py | load_and_flatten (reuse load_zoo), apply_condition_d (scaling + sign-flip in numpy), train_test_split_fixed | data-pipeline | 10 | 3+2+3+2 |
| E-3 | Implement evaluate.py | evaluate_pca_concentration (PCA+LR+bootstrap CI), verify_mechanism_preconditions, compare_conditions | evaluation | 12 | 3+2+4+3 |
| E-4 | Implement figures.py | 5 figure functions + generate_all_figures orchestrator | visualization | 9 | 2+1+3+3 |
| E-5 | Implement main.py | Orchestrate: load → conditions A/D → PCA sweep → eval → gate → figures → save results.json | training | 8 | 2+3+1+2 |
| E-6 | Run experiment and validate gate | Execute full pipeline, verify gate condition (R²_D > R²_A ≥2/3 tasks at k=20 with non-overlapping CI) | evaluation | 7 | 1+1+2+3 |

**Distribution:** High(10-13): [E-3, E-2]; Medium(7-9): [E-4, E-5, E-6]; Low(4-6): [E-1]

**Total complexity:** 50
