# Logic: H-M3
# Geometric vs Scalar Distortion via Brier Decomposition

**Version:** 1.0
**Date:** 2026-03-24
**Hypothesis ID:** h-m3

Applied: flat-module statistical-reanalysis pattern (adapted from h-m2)
Applied: paired bootstrap difference test (adapted from h-m2 analysis.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m2 code (Serena project not active; used direct file reads)
**Analyzed Path**: `docs/youra_research/20260323_buildingtrust/h-m2/code/`
**Relevant Symbols**:
- `analyze_family(family: str, arrays: dict[str, np.ndarray]) -> dict` — per-family pipeline pattern
- `bootstrap_difference_test(base_margins, base_correctness, inst_margins, inst_correctness, n_iterations, seed) -> dict[str, float]`
- `compute_bootstrap_ci(betas: np.ndarray, alpha: float) -> tuple[float, float, float]`
- `load_all_families(families, cache_dir) -> dict[str, dict[str, np.ndarray]]`
- `evaluate_gate(family_results: dict[str, dict]) -> str` — in report.py (not analysis.py)
- `save_experiment_results_yaml(family_results, gate_result, output_path) -> None`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual h-m2 Code)

```python
# From: h-m2/code/analysis.py (ACTUAL CODE)
def analyze_family(
    family: str,
    arrays: dict[str, np.ndarray],   # keys: base_margins, base_correctness, inst_margins, inst_correctness
) -> dict:
    """Full per-family analysis. Returns structured results dict."""
    ...

def bootstrap_difference_test(
    base_margins: np.ndarray,         # (N,)
    base_correctness: np.ndarray,     # (N,)
    inst_margins: np.ndarray,         # (N,)
    inst_correctness: np.ndarray,     # (N,)
    n_iterations: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict[str, float]:
    """Returns: delta_beta_mean, delta_ci_lower, delta_ci_upper, p_value, effect_size"""
    ...

def compute_bootstrap_ci(
    betas: np.ndarray,                # (n_iterations,)
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Returns: (mean, ci_lower, ci_upper)"""
    ...

# From: h-m2/code/report.py (ACTUAL CODE)
def evaluate_gate(family_results: dict[str, dict]) -> str:
    """Returns 'PASS' or 'FAIL'. gate_pass key per family."""
    ...

def save_experiment_results_yaml(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Optional[Path] = None,
) -> None: ...

# From: h-m2/code/data_loader.py (ACTUAL CODE)
def load_all_families(
    families: Optional[list[str]] = None,
    cache_dir: Optional[Path] = None,
) -> dict[str, dict[str, np.ndarray]]:
    """Returns {family: {base_margins, base_correctness, inst_margins, inst_correctness}}"""
    ...
```

**Key difference from h-m2**: H-M3 loads flat `.npy` logit files (e.g. `qwen_base_logits.npy`) directly from cache root, NOT per-family subdirectories. H-M3 also uses `inst_logits`/`base_logits` keys, not `margins`.

---

## A-1: Project Setup [Complexity: 5, Budget: 1]

Applied: Standard PyTorch/Python path config

### API Signatures

```python
# code/config.py
from pathlib import Path

SEED: int = 42
BOOTSTRAP_N: int = 1000
N_BINS: int = 15
FAMILIES: list[str] = ["qwen", "mistral"]
GATE_TYPE: str = "SHOULD_WORK"
P_VALUE_THRESHOLD: float = 0.05
DECOMP_TOLERANCE: float = 1e-6

CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CACHE_DIR: Path = HYPOTHESIS_DIR.parent / "h-e1" / "cache"
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"
RESULTS_YAML: Path = HYPOTHESIS_DIR / "experiment_results.yaml"
VALIDATION_MD: Path = HYPOTHESIS_DIR / "04_validation.md"

def ensure_directories() -> None:
    """Create figures/ if not exists."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | config | All constants and path definitions |

---

## A-2: Data Loading [Complexity: 8, Budget: 1]

Applied: Standard numpy .npy loading

### API Signatures

```python
# code/data_loader.py
import numpy as np
from pathlib import Path
from typing import Optional
from config import H_E1_CACHE_DIR, FAMILIES

def load_logits_and_labels(
    family: str,
    cache_dir: Optional[Path] = None,
) -> dict[str, np.ndarray]:
    """Load base/instruct logits and shared labels for one family.
    Returns keys: base_logits (14042, 4), inst_logits (14042, 4), labels (14042,)
    """
    # Files: {family}_base_logits.npy, {family}_instruct_logits.npy, labels.npy
    ...

def validate_cache(
    data: dict[str, np.ndarray],
    expected_n: int = 14042,
    n_classes: int = 4,
) -> None:
    """Raise ValueError if shapes or values invalid."""
    ...

def load_all_families(
    families: Optional[list[str]] = None,
    cache_dir: Optional[Path] = None,
) -> dict[str, dict[str, np.ndarray]]:
    """Returns {family: {base_logits, inst_logits, labels}}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| base_logits | (14042, 4) | Raw logits for 4 options |
| inst_logits | (14042, 4) | Raw logits for 4 options |
| labels | (14042,) | int, correct answer index 0-3 |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | data_loader | load + validate flat .npy files from h-e1 cache root |

---

## A-3 + A-4: Brier Decomposition + Bootstrap Engine [Complexity: 13+12, Budget: 2]

Applied: Murphy (1973) decomposition; standard percentile bootstrap

### API Signatures

```python
# code/brier_decomp.py
import numpy as np
from scipy.special import softmax
from typing import Optional

def logits_to_probs(logits: np.ndarray) -> np.ndarray:
    """(N, C) -> (N, C) via row-wise softmax."""
    ...

def murphy_brier_decomposition(
    logits: np.ndarray,   # (N, 4)
    labels: np.ndarray,   # (N,)
    n_bins: int = 15,
) -> dict[str, float]:
    """Murphy (1973) BS = REL - RES + UNC.
    Raises ValueError if |BS - (REL - RES + UNC)| > 1e-6.
    Returns keys: brier_score, reliability, resolution, uncertainty, refinement
    """
    # 1. probs = logits_to_probs(logits)           # (N, 4)
    # 2. y_onehot = np.eye(4)[labels]              # (N, 4)
    # 3. bs = mean(sum((probs - y_onehot)^2, axis=1))
    # 4. ybar = mean(y_onehot, axis=0)             # (4,) base rates
    # 5. unc = sum(ybar * (1 - ybar))
    # 6. bin by top-class prob into n_bins bins, skip empty bins
    # 7. rel = sum_k (nk/n) * sum_c (fk_c - ybar_c)^2
    # 8. res = sum_k (nk/n) * sum_c (ybar_k_c - ybar_c)^2
    # 9. verify: |bs - (rel - res + unc)| < 1e-6
    ...

def bootstrap_decomposition(
    logits: np.ndarray,       # (N, 4)
    labels: np.ndarray,       # (N,)
    n_iterations: int = 1000,
    n_bins: int = 15,
    seed: int = 42,
) -> dict[str, np.ndarray]:
    """Bootstrap n_iterations decompositions.
    Returns {component: (n_iterations,) array}
    Components: brier_score, reliability, resolution, uncertainty, refinement
    """
    ...

def compute_ci(
    bootstrap_values: np.ndarray,  # (n_iterations,)
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Returns (mean, ci_lower, ci_upper) using percentile method."""
    ...
```

### Pseudo-code: murphy_brier_decomposition (non-trivial binning)

```
probs = softmax(logits, axis=1)                    # (N, 4)
y_onehot = eye(4)[labels]                          # (N, 4)
bs = mean(sum((probs - y_onehot)^2, axis=1))

ybar = mean(y_onehot, axis=0)                      # (4,) overall base rates
unc = sum(ybar * (1 - ybar))

# Bin by max probability (top-class confidence)
p_max = max(probs, axis=1)                         # (N,)
bin_edges = linspace(0, 1, n_bins + 1)
rel, res = 0.0, 0.0
for k in range(n_bins):
    mask = (p_max >= bin_edges[k]) & (p_max < bin_edges[k+1])
    if last bin: mask includes right edge
    nk = sum(mask)
    if nk == 0: continue
    fk = mean(y_onehot[mask], axis=0)              # (4,) mean obs freq in bin
    ybar_k = mean(probs[mask], axis=0)             # (4,) mean predicted in bin
    rel += (nk / N) * sum((fk - ybar)^2)           # calibration error
    res += (nk / N) * sum((ybar_k - ybar)^2)       # discrimination / refinement

refinement = res
verify: |bs - (rel - res + unc)| < DECOMP_TOLERANCE
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | murphy_brier_decomposition | Full Murphy formula with bin-level REL/RES + verification |
| L-3-2 | bootstrap + CI | bootstrap_decomposition, compute_ci, paired difference test |

---

## A-5: Per-Family Analysis [Complexity: 10, Budget: 1]

Applied: Adapted from h-m2 analyze_family pattern

### API Signatures

```python
# code/analysis.py
import numpy as np
from config import SEED, BOOTSTRAP_N, N_BINS, P_VALUE_THRESHOLD
from brier_decomp import murphy_brier_decomposition, bootstrap_decomposition, compute_ci

def paired_bootstrap_difference(
    base_logits: np.ndarray,   # (N, 4)
    inst_logits: np.ndarray,   # (N, 4)
    labels: np.ndarray,        # (N,)
    component: str,            # e.g. "refinement"
    n_iterations: int = 1000,
    n_bins: int = 15,
    seed: int = 42,
) -> dict[str, float]:
    """Paired bootstrap for component_base - component_instruct.
    Returns: delta_mean, delta_ci_lower, delta_ci_upper, p_value, effect_size
    """
    # For each iteration: same idx for base and instruct (paired)
    # p_value = proportion where delta <= 0
    # effect_size = delta_mean / std(deltas)
    ...

def analyze_family(
    family: str,
    data: dict[str, np.ndarray],  # keys: base_logits, inst_logits, labels
) -> dict:
    """Full per-family pipeline. Returns structured results with all metrics + gate_pass bool."""
    # 1. murphy_brier_decomposition for base and instruct (point estimates)
    # 2. bootstrap_decomposition for base and instruct -> compute_ci per component
    # 3. paired_bootstrap_difference for "refinement" component
    # 4. gate_pass = (refinement_instruct < refinement_base) AND (p_value < P_VALUE_THRESHOLD)
    ...

def evaluate_gate(family_results: dict[str, dict]) -> str:
    """Returns 'PASS' if ALL families have gate_pass=True, else 'FAIL'."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | analyze_family + gate | Per-family pipeline, paired bootstrap diff, gate logic |

---

## A-6 to A-12: Visualization, Report, Orchestrator, Tests

These modules follow the h-m2 pattern directly. Key signatures below for Coder reference.

### Visualize (`code/visualize.py`)

```python
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def plot_brier_decomposition_comparison(
    family_results: dict[str, dict],
    output_dir: Path,
) -> Path:
    """Grouped bar chart: REL/RES/UNC base vs instruct per family. Returns saved path."""
    ...

def plot_reliability_diagram(
    family_data: dict[str, dict[str, np.ndarray]],
    output_dir: Path,
    n_bins: int = 15,
) -> Path:
    """Calibration curve (predicted prob vs observed freq) per family."""
    ...

def plot_refinement_delta_forest(
    family_results: dict[str, dict],
    output_dir: Path,
) -> Path:
    """Forest plot of delta_refinement with 95% CIs and zero-reference line."""
    ...

def plot_decomposition_verification(
    family_results: dict[str, dict],
    output_dir: Path,
) -> Path:
    """Scatter: BS_computed vs (REL - RES + UNC). Should lie on y=x line."""
    ...

def save_all_figures(
    family_results: dict[str, dict],
    family_data: dict[str, dict[str, np.ndarray]],
    output_dir: Path,
) -> list[Path]:
    """Run all four plot functions. Returns list of saved paths."""
    ...
```

### Report (`code/report.py`)

```python
from pathlib import Path
from typing import Optional

def evaluate_gate(family_results: dict[str, dict]) -> str:
    """Returns 'PASS' if all family gate_pass=True, else 'FAIL'."""
    ...

def save_experiment_results_yaml(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Optional[Path] = None,
) -> None: ...

def generate_validation_report(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Optional[Path] = None,
) -> None: ...
```

### Orchestrator (`code/run_experiment.py`)

```python
import argparse
import logging
from config import SEED, FAMILIES

def set_seed(seed: int = SEED) -> None: ...

def main(families: list[str] = None) -> int:
    """Returns 0 (PASS) or 1 (FAIL)."""
    # 1. ensure_directories(), set_seed()
    # 2. load_all_families() + validate_cache()
    # 3. analyze_family() per family
    # 4. save_all_figures()
    # 5. evaluate_gate()
    # 6. save_experiment_results_yaml(), generate_validation_report()
    ...

if __name__ == "__main__":
    # argparse: --families qwen mistral
    ...
```

### Unit Tests (`code/tests/test_brier_decomp.py`)

```python
def test_decomposition_identity():
    """Perfect predictions -> REL=0, RES=UNC, BS=0."""
    ...

def test_decomposition_verification():
    """Random probs/labels: |BS - (REL-RES+UNC)| < 1e-6."""
    ...

def test_empty_bins_skipped():
    """Concentrated predictions don't cause ZeroDivision."""
    ...
```

---

*Generated by Phase 3 Logic Agent*
*Base hypothesis API verified from: h-m2/code/ (actual implementation, not spec)*
