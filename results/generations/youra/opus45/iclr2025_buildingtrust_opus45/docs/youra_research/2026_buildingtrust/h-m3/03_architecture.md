# Architecture: H-M3
# Geometric vs Scalar Distortion via Brier Decomposition

**Version:** 1.0
**Date:** 2026-03-24
**Hypothesis ID:** h-m3
**Type:** MECHANISM | SHOULD_WORK gate

Applied: flat-module statistical-reanalysis pattern (from h-m2 base hypothesis)
Applied: bootstrap-CI paired difference test pattern (from h-m2 analysis.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260323_buildingtrust/h-m2/code/`
**Findings**: Flat module layout — config.py, data_loader.py, analysis.py, visualize.py, report.py, run_experiment.py. Path resolution via `Path(__file__).parent`. H-E1 cache accessed as `HYPOTHESIS_DIR.parent / "h-e1" / "cache"`. H-M2 loads per-family subdirectories; H-M3 loads flat `.npy` files directly from cache root (different cache layout).

---

## File Organization

- `code/config.py` — constants, paths
- `code/data_loader.py` — load/validate logits + labels from H-E1 cache
- `code/brier_decomp.py` — Murphy (1973) decomposition + bootstrap
- `code/analysis.py` — per-family pipeline, statistical comparison
- `code/visualize.py` — four publication figures
- `code/report.py` — YAML results + markdown validation report
- `code/run_experiment.py` — main orchestrator
- `code/tests/test_brier_decomp.py` — unit tests for decomposition

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: stdlib only

```python
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

def ensure_directories() -> None: ...
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: config

```python
import numpy as np
from pathlib import Path
from typing import Optional

def load_logits_and_labels(
    family: str,
    cache_dir: Optional[Path] = None,
) -> dict[str, np.ndarray]:
    """
    Returns:
        base_logits: (14042, 4)
        inst_logits: (14042, 4)
        labels: (14042,)
    """
    ...

def validate_cache(
    data: dict[str, np.ndarray],
    expected_n: int = 14042,
    n_classes: int = 4,
) -> None: ...

def load_all_families(
    families: Optional[list[str]] = None,
    cache_dir: Optional[Path] = None,
) -> dict[str, dict[str, np.ndarray]]: ...
```

---

### BrierDecomp (`code/brier_decomp.py`)

**Dependencies**: numpy, scipy

```python
import numpy as np
from scipy.special import softmax

def logits_to_probs(logits: np.ndarray) -> np.ndarray:
    """(N, C) logits -> (N, C) probabilities via softmax."""
    ...

def murphy_brier_decomposition(
    logits: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 15,
) -> dict[str, float]:
    """
    Murphy (1973) decomposition: BS = REL - RES + UNC
    Returns keys: brier_score, reliability, resolution, uncertainty, refinement
    Raises ValueError if decomposition verification fails (tolerance 1e-6).
    """
    ...

def bootstrap_decomposition(
    logits: np.ndarray,
    labels: np.ndarray,
    n_iterations: int = 1000,
    n_bins: int = 15,
    seed: int = 42,
) -> dict[str, np.ndarray]:
    """
    Bootstrap n_iterations decompositions.
    Returns dict mapping component -> (n_iterations,) array of values.
    """
    ...

def compute_ci(
    bootstrap_values: np.ndarray,
    alpha: float = 0.05,
) -> tuple[float, float, float]: ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: config, brier_decomp

```python
import numpy as np

def analyze_family(
    family: str,
    data: dict[str, np.ndarray],
) -> dict:
    """
    Full per-family pipeline:
    1. Decompose base and instruct logits
    2. Bootstrap CIs per component
    3. Paired bootstrap difference test (base - instruct)
    4. Compute p-value and effect size
    5. Determine gate pass/fail

    Returns structured dict with all metrics, CIs, gate result.
    """
    ...

def paired_bootstrap_difference(
    base_logits: np.ndarray,
    inst_logits: np.ndarray,
    labels: np.ndarray,
    component: str,
    n_iterations: int = 1000,
    n_bins: int = 15,
    seed: int = 42,
) -> dict[str, float]:
    """
    Paired bootstrap test for component_base - component_instruct.
    Returns: delta_mean, delta_ci_lower, delta_ci_upper, p_value, effect_size
    """
    ...

def evaluate_gate(
    family_results: dict[str, dict],
) -> str:
    """Returns 'PASS' or 'FAIL' based on refinement direction + CI across families."""
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, analysis results

```python
from pathlib import Path

def plot_brier_decomposition_comparison(
    family_results: dict[str, dict],
    output_dir: Path,
) -> Path: ...

def plot_reliability_diagram(
    family_data: dict[str, dict[str, np.ndarray]],
    output_dir: Path,
    n_bins: int = 15,
) -> Path: ...

def plot_refinement_delta_forest(
    family_results: dict[str, dict],
    output_dir: Path,
) -> Path: ...

def plot_decomposition_verification(
    family_results: dict[str, dict],
    output_dir: Path,
) -> Path: ...

def save_all_figures(
    family_results: dict[str, dict],
    family_data: dict[str, dict[str, np.ndarray]],
    output_dir: Path,
) -> list[Path]: ...
```

---

### Report (`code/report.py`)

**Dependencies**: config, yaml

```python
from pathlib import Path

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

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: all modules

```python
def set_seed(seed: int = SEED) -> None: ...

def main(families: list[str] = None) -> int:
    """
    Pipeline:
    1. ensure_directories(), set_seed()
    2. load_all_families() + validate_cache()
    3. analyze_family() per family
    4. save_all_figures()
    5. evaluate_gate()
    6. save_experiment_results_yaml(), generate_validation_report()
    Returns exit code 0 (PASS) or 1 (FAIL).
    """
    ...
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Pattern | File Location |
|--------|---------------|---------------|
| Cache layout reference | read from h-m2 config | `h-m2/code/config.py` |
| Bootstrap CI pattern | adapt from h-m2 | `h-m2/code/analysis.py` |
| Report pattern | adapt from h-m2 | `h-m2/code/report.py` |

**Note**: H-M3 loads logits directly (`qwen_base_logits.npy`) from cache root, not per-family subdirectories like H-M2. Cache path: `HYPOTHESIS_DIR.parent / "h-e1" / "cache"`.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py paths, ensure_directories, seed setup | 5 | 1+1+1+2 |
| A-2 | Data Loading | load logits+labels from H-E1 cache flat layout, validate shapes | 8 | 2+2+2+2 |
| A-3 | Brier Decomposition | murphy_brier_decomposition with REL/RES/UNC, verification check | 13 | 3+2+5+3 |
| A-4 | Bootstrap Engine | bootstrap_decomposition, paired difference test, CI computation | 12 | 3+2+4+3 |
| A-5 | Per-Family Analysis | analyze_family pipeline, gate evaluation | 10 | 2+3+3+2 |
| A-6 | Decomposition Bar Chart | grouped bars REL/RES/UNC base vs instruct with error bars | 9 | 2+2+3+2 |
| A-7 | Reliability Diagram | calibration curve 15-bin per family | 9 | 2+2+3+2 |
| A-8 | Forest Plot | refinement delta with 95% CIs, zero-line | 8 | 2+2+2+2 |
| A-9 | Verification Scatter | BS_computed vs (REL-RES+UNC) scatter | 6 | 1+2+2+1 |
| A-10 | Results + Report | YAML results with CIs/p-values, markdown validation report | 9 | 2+2+2+3 |
| A-11 | Orchestrator | run_experiment.py main pipeline, argparse, logging, exit code | 8 | 2+2+2+2 |
| A-12 | Unit Tests | test_brier_decomp.py — decomposition identity, edge cases | 7 | 2+1+3+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6, A-7, A-10], Low(4-8): [A-1, A-2, A-8, A-9, A-11, A-12]

---

## Data Flow

- `run_experiment.py` calls `data_loader` -> returns `{family: {base_logits, inst_logits, labels}}`
- Passes to `analysis.analyze_family` -> calls `brier_decomp.murphy_brier_decomposition` + `paired_bootstrap_difference`
- Results passed to `visualize.save_all_figures` + `report.save_experiment_results_yaml`
- Gate: Refinement_instruct < Refinement_base + 95% CI excludes zero for both families

---

*Generated by Phase 3 Architecture Agent*
*Base hypothesis code verified from: h-m2/code/ (actual implementation)*
