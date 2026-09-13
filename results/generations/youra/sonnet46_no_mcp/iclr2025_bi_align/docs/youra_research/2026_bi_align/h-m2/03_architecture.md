# H-M2 Architecture: Round-Stratified Label-Distribution Coefficient Shift

**Generated:** 2026-05-03
**Hypothesis:** H-M2 (MECHANISM / INCREMENTAL / SHOULD_WORK)
**Base:** H-E1 (COMPLETED) + H-M1 (COMPLETED)

Applied: round-stratified-logistic-regression-coefficient-comparison
Applied: bootstrap-ci-non-overlap-test
Applied: incremental-hypothesis-pipeline-reuse

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1 + H-M1)
**Status**: patterns found from base code
**Analyzed Path**: `h-e1/code/` and `h-m1/code/`
**Findings**: H-E1 provides `load_hh_rlhf()`, `stratify_rounds()` in `data_loader.py`; `build_feature_matrix()` in `features.py`; `QEarlyModel` class in `q_early.py`; `fit_round_conditioned_regression()`, `CoeffResult` in `analysis.py`. H-M1 imports H-E1 via `sys.path.insert(1, HE1_CODE_DIR)` pattern — H-M2 must use identical sys.path strategy.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_hh_rlhf | `from data_loader import load_hh_rlhf` | `h-e1/code/data_loader.py` |
| stratify_rounds | `from data_loader import stratify_rounds` | `h-e1/code/data_loader.py` |
| build_feature_matrix | `from features import build_feature_matrix` | `h-e1/code/features.py` |
| QEarlyModel | `from q_early import QEarlyModel` | `h-e1/code/q_early.py` |
| fit_round_conditioned_regression | `from analysis import fit_round_conditioned_regression` | `h-e1/code/analysis.py` |
| CoeffResult | `from analysis import CoeffResult` | `h-e1/code/analysis.py` |

**sys.path pattern (verified from h-m1/code/run_experiment.py):**
```python
HE1_CODE_DIR = Path(__file__).parent.parent.parent / "h-e1" / "code"
sys.path.insert(1, str(HE1_CODE_DIR))
```

**Verified from**: `h-e1/code/` and `h-m1/code/run_experiment.py` (actual implementation)

---

## File Organization

```
h-m2/code/
├── config.py                              # H-M2 hyperparameters, paths
├── coefficient_comparison.py              # NEW: core module — round-stratified fitting + bootstrap CI
├── run_experiment.py                      # Pipeline entry point
└── tests/
    └── test_coefficient_comparison.py     # Unit tests for new module
h-m2/figures/                              # 6 saved figures
h-m2/results/
    └── results.yaml                       # Serialized metrics
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: None (stdlib + pathlib only)

```python
from pathlib import Path

# Paths
BASE_DIR: Path
HE1_CODE_DIR: Path
FIGURES_DIR: Path
RESULTS_DIR: Path

# Dataset
HH_RLHF_DATASET: str = "Anthropic/hh-rlhf"
N_ROUNDS: int = 3
ROUND_SIZE_MIN: int = 40000

# Round stratification
EARLY_ROUND: int = 1
LATE_ROUND: int = 3
TEST_SIZE: float = 0.25
RANDOM_SEED: int = 42

# Model
LR_PARAMS: dict  # C=1.0, solver='lbfgs', max_iter=1000, random_state=42

# Bootstrap
BOOTSTRAP_ITERS: int = 2000
CI_ALPHA: float = 0.05

# Gate
N_DIRECTIONAL_GATE: int = 2
BETA_Q_STABILITY_THRESHOLD: float = 0.2
TOPIC_BALANCE_ALPHA: float = 0.05

# Figures
FIGURE_FILENAMES: dict
FIGURES_DPI: int = 150
```

---

### CoefficientComparison (`code/coefficient_comparison.py`)

**Dependencies**: config, [H-E1] data_loader, features, q_early, analysis

```python
import numpy as np
import pandas as pd
from dataclasses import dataclass
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from scipy.stats import chi2_contingency
from typing import Tuple, Dict


@dataclass
class RoundSplit:
    X_train: np.ndarray       # (N_train, 3) stylistic features
    y_train: np.ndarray       # (N_train,) labels
    q_train: np.ndarray       # (N_train,) Q_early scores
    X_test: np.ndarray        # (N_test, 3)
    y_test: np.ndarray
    q_test: np.ndarray
    round_id: int


@dataclass
class RoundModel:
    clf: LogisticRegression
    scaler: StandardScaler    # fit on round-1 training only; shared across rounds
    coefs: np.ndarray         # (3,) = [β_L, β_H, β_S]
    beta_q: float             # quality coefficient
    auc: float


@dataclass
class ComparisonResult:
    early_coefs: np.ndarray           # (3,)
    late_coefs: np.ndarray            # (3,)
    deltas: np.ndarray                # (3,) late - early
    early_ci: np.ndarray              # (2, 3) [low/high, features]
    late_ci: np.ndarray               # (2, 3)
    n_directional: int                # count of non-overlapping late > early CIs
    sign_consistent: bool             # all 3 deltas > 0
    beta_q_stable: bool               # |late_β_Q - early_β_Q| < 0.2
    topic_balance_pvalue: float
    early_auc: float
    late_auc: float
    boot_early: np.ndarray            # (n_resamples, 3) raw bootstrap samples
    boot_late: np.ndarray             # (n_resamples, 3)


def prepare_round_splits(
    df: pd.DataFrame,
    q_early_model,
    round_size: int,
    test_size: float = 0.25,
    random_state: int = 42,
) -> Tuple[RoundSplit, RoundSplit]:
    """Extract early/late subsets, hold out 25% each, return RoundSplit pair."""
    ...


def check_topic_balance(
    early_df: pd.DataFrame,
    late_df: pd.DataFrame,
) -> float:
    """Chi-square test on prompt topic distributions; return p-value."""
    ...


def fit_round_predictor(
    split: RoundSplit,
    shared_scaler: StandardScaler = None,
) -> RoundModel:
    """
    Fit LogisticRegression on split.X_train + q_train.
    If shared_scaler provided, use it (don't refit); else fit new scaler.
    Returns RoundModel with clf, scaler, coefs, beta_q, auc.
    """
    ...


def bootstrap_ci(
    split: RoundSplit,
    shared_scaler: StandardScaler,
    n_resamples: int = 2000,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    2000 stratified resamples; return (ci_low, ci_high, boot_coefs).
    ci_low/ci_high: (3,); boot_coefs: (n_resamples, 3).
    """
    ...


def compare_coefficients(
    early_model: RoundModel,
    late_model: RoundModel,
    early_split: RoundSplit,
    late_split: RoundSplit,
    shared_scaler: StandardScaler,
    n_resamples: int = 2000,
    random_state: int = 42,
) -> ComparisonResult:
    """
    Run bootstrap CIs for both rounds, compute deltas, n_directional,
    sign consistency, beta_q stability. Returns ComparisonResult.
    """
    ...


def check_cross_round_held_out(
    early_model: RoundModel,
    late_model: RoundModel,
    X_test: np.ndarray,
    y_test: np.ndarray,
    q_test: np.ndarray,
    shared_scaler: StandardScaler,
    ambiguity_threshold: float = 0.1,
) -> Dict:
    """
    Evaluate both models on shared held-out set.
    Returns dict: {early_auc, late_auc, high_ambiguity_longer_pref_rate}.
    """
    ...


def fit_auxiliary_round2_model(
    df: pd.DataFrame,
    q_early_model,
    shared_scaler: StandardScaler,
    round_size: int,
    random_state: int = 42,
) -> RoundModel:
    """Fit auxiliary round-2 model for monotonicity check (FR-7.3)."""
    ...


def evaluate_gate(result: ComparisonResult) -> Dict:
    """
    Gate logic: PASS if n_directional >= 2, PARTIAL if == 1, FAIL if == 0.
    Returns dict: {gate_status, n_directional, sign_consistent, beta_q_stable}.
    """
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: config, coefficient_comparison, [H-E1] data_loader, features, q_early

```python
import sys
import logging
import yaml
from pathlib import Path

def setup_paths() -> None:
    """Insert H-E1 code dir into sys.path using H-M1 verified pattern."""
    ...

def run_pipeline() -> dict:
    """
    Orchestrate: load → features → Q_early → round splits → topic balance
    → fit models → bootstrap CI → compare → visualize → gate → serialize.
    Returns metrics dict.
    """
    ...

def serialize_results(metrics: dict, results_path: Path) -> None:
    """Write results.yaml with all gate metrics and coefficient values."""
    ...

def main() -> None:
    """Entry point: setup_paths(), run_pipeline(), log gate status."""
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: config, coefficient_comparison

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from coefficient_comparison import ComparisonResult, RoundModel


def plot_coefficient_comparison(
    result: ComparisonResult,
    save_path: Path,
) -> None:
    """Side-by-side bar chart [β_L, β_H, β_S, β_Q] with 95% CI error bars."""
    ...


def plot_bootstrap_distributions(
    result: ComparisonResult,
    save_path: Path,
) -> None:
    """Overlapping histograms of bootstrap coefficient distributions."""
    ...


def plot_feature_stability(
    early_model: RoundModel,
    mid_model: RoundModel,
    late_model: RoundModel,
    save_path: Path,
) -> None:
    """Coefficient magnitudes across rounds 1→2→3 for monotonicity check."""
    ...


def plot_cross_round_scatter(
    early_scores: np.ndarray,
    late_scores: np.ndarray,
    save_path: Path,
) -> None:
    """Scatter of early vs. late model preference scores on held-out set."""
    ...


def plot_topic_balance(
    chi2_residuals: np.ndarray,
    topic_labels: list,
    pvalue: float,
    save_path: Path,
) -> None:
    """Chi-square residual bar chart for topic distribution balance."""
    ...


def plot_gate_metrics(
    result: ComparisonResult,
    gate_status: str,
    save_path: Path,
) -> None:
    """Gate metrics summary: n_directional, β deltas vs. thresholds."""
    ...
```

---

### Tests (`code/tests/test_coefficient_comparison.py`)

**Dependencies**: coefficient_comparison, config

```python
def test_fit_round_predictor_shape() -> None: ...
def test_bootstrap_ci_shape() -> None: ...
def test_compare_coefficients_n_directional() -> None: ...
def test_shared_scaler_consistency() -> None: ...
def test_evaluate_gate_pass() -> None: ...
def test_evaluate_gate_fail() -> None: ...
def test_topic_balance_check() -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py, directory structure, sys.path H-E1 integration | 6 | 1+2+1+2 |
| A-2 | Round Data Splits | prepare_round_splits(): early/late 25% hold-out, round size assert | 8 | 2+2+2+2 |
| A-3 | Topic Balance Check | check_topic_balance(): chi-square on prompt topics, warn if p<0.05 | 7 | 2+2+2+1 |
| A-4 | Round Predictor Fitting | fit_round_predictor(): LR fit, shared StandardScaler, coef extraction | 9 | 2+2+3+2 |
| A-5 | Bootstrap CI | bootstrap_ci(): 2000 stratified resamples, 95% percentile CI, β_Q stability | 12 | 3+2+4+3 |
| A-6 | Coefficient Comparison | compare_coefficients(): deltas, n_directional, sign consistency, gate eval | 11 | 3+3+3+2 |
| A-7 | Cross-Round Held-Out | check_cross_round_held_out(): AUC comparison, high-ambiguity longer-pref rate | 9 | 2+2+3+2 |
| A-8 | Visualizations | 6 figures: coef comparison, bootstrap hist, stability, scatter, topic, gate | 11 | 3+2+2+4 |
| A-9 | Pipeline Orchestration | run_experiment.py: full pipeline, results.yaml serialization, log message | 10 | 2+3+2+3 |
| A-10 | Unit Tests | test_coefficient_comparison.py: 7 unit tests covering core functions | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-6, A-7, A-8, A-9], Low(4-8): [A-1, A-2, A-3, A-10]

---

## Data Flow

- `load_hh_rlhf()` → full DataFrame (~169K rows) with `round` column
- `prepare_round_splits()` → `RoundSplit(early)`, `RoundSplit(late)`, shared test set
- `QEarlyModel.fit(round-1 train)` + `.calibrate(round-2 data)` → q_early scores for all splits
- `fit_round_predictor(early_split, scaler=None)` → `RoundModel(early)` + fitted `shared_scaler`
- `fit_round_predictor(late_split, scaler=shared_scaler)` → `RoundModel(late)`
- `compare_coefficients(...)` → `ComparisonResult` with CIs, n_directional, gate metrics
- `evaluate_gate(result)` → `{gate_status: PASS|PARTIAL|FAIL}`
- `serialize_results(metrics)` → `results/results.yaml`

## Gate Logic

```
n_directional >= 2 AND non-overlapping 95% CI → PASS
n_directional == 1                             → PARTIAL (PIVOT)
n_directional == 0 OR sign inconsistency       → FAIL (PIVOT, narrow H-M3 scope)
```

## Mechanism Log Message
```
"Coefficient comparison: β_L=[{early:.4f},{late:.4f}] δ={delta:.4f}; β_H=[{early:.4f},{late:.4f}] δ={delta:.4f}; β_S=[{early:.4f},{late:.4f}] δ={delta:.4f}; n_directional={n}/3"
```
