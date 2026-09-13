# Architecture: H-E1 Temporal Stylistic Coefficient Drift

**Hypothesis:** H-E1 (EXISTENCE / LIGHT / MUST_WORK)
**Type:** Statistical Analysis Pipeline (no neural network training)
**Date:** 2026-05-03

Applied: Statistical-Analysis-Pipeline
Applied: Pipeline-Module-Separation
Applied: Bootstrap-CI-Pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis code exists for H-E1.

---

## File Structure

```
docs/youra_research/20260503_bi_align/h-e1/code/
├── config.py          # constants, paths, hyperparameters
├── data_loader.py     # HH-RLHF + WebGPT loading, round stratification
├── features.py        # stylistic feature extraction (β_L, β_H, β_S)
├── q_early.py         # Q_early logistic regression + affine recalibration
├── analysis.py        # round-conditioned regression, bootstrap CI, placebo
├── visualize.py       # 6 figures saved to h-e1/figures/
└── run_experiment.py  # main pipeline entry point
```

---

## Module Interfaces

### Config (`code/config.py`)

**Dependencies**: none

```python
# Dataset identifiers
HH_RLHF_DATASET: str = "Anthropic/hh-rlhf"
WEBGPT_DATASET: str = "openai/webgpt_comparisons"
N_ROUNDS: int = 3
BOOTSTRAP_ITERS: int = 1000
PERMUTATION_ITERS: int = 1000
ALPHA: float = 0.05
BONFERRONI_K: int = 3          # β_L, β_H, β_S
ALPHA_CORRECTED: float = 0.0167
BRIER_GATE_THRESHOLD: float = 0.02
FIGURES_DIR: str = "../figures"
RANDOM_SEED: int = 42

LR_PARAMS: dict = {
    "C": 1.0,
    "max_iter": 1000,
    "solver": "lbfgs",
    "random_state": 42,
}
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: config

```python
import pandas as pd
from datasets import Dataset

def load_hh_rlhf() -> pd.DataFrame:
    """Returns df with columns: chosen, rejected, round (1/2/3)."""
    ...

def load_webgpt() -> pd.DataFrame:
    """Returns df with columns: answer_0, answer_1, preference, worker_id."""
    ...

def stratify_rounds(df: pd.DataFrame) -> dict[int, pd.DataFrame]:
    """Returns {1: df_r1, 2: df_r2, 3: df_r3}."""
    ...

def validate_round_coverage(round_dfs: dict) -> bool:
    """Gate: >= 80% comparisons have non-null round indicator."""
    ...
```

---

### FeatureExtractor (`code/features.py`)

**Dependencies**: config

```python
import numpy as np
import pandas as pd

def extract_verbosity(text: str) -> float:
    """β_L: normalized word count of chosen minus rejected."""
    ...

def extract_hedging(text: str) -> float:
    """β_H: hedge word frequency ratio (chosen vs rejected)."""
    ...

def extract_structured_reasoning(text: str) -> float:
    """β_S: list/numbered step density (chosen vs rejected)."""
    ...

def build_feature_matrix(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Returns (X: [n, 3], y: [n]) standardized features and binary labels."""
    ...

def check_vif(X: np.ndarray) -> dict[str, float]:
    """Returns VIF per feature; warn if VIF > 5."""
    ...

def compute_fleiss_kappa(df: pd.DataFrame) -> float:
    """Requires per-prompt annotator agreement fields; returns κ."""
    ...

def partition_by_ambiguity(df: pd.DataFrame, kappa_threshold: float = 0.4) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (high_ambiguity_df, low_ambiguity_df)."""
    ...
```

---

### QEarly (`code/q_early.py`)

**Dependencies**: config, features

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV

class QEarlyModel:
    def __init__(self): ...

    def fit(self, X_r1: np.ndarray, y_r1: np.ndarray) -> None:
        """Train logistic regression on round-1 data."""
        ...

    def calibrate(self, X: np.ndarray, y: np.ndarray) -> None:
        """Affine recalibration (Platt scaling) for rounds 2-3."""
        ...

    def predict_proba(self, X: np.ndarray) -> np.ndarray: ...

    def brier_score(self, X: np.ndarray, y: np.ndarray) -> float: ...

    def gate_check(self, brier_r1: float, brier_r2: float) -> bool:
        """Returns True if |brier_r2 - brier_r1| < BRIER_GATE_THRESHOLD."""
        ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: config, features, q_early

```python
import numpy as np
import pandas as pd
from dataclasses import dataclass

@dataclass
class CoeffResult:
    round_id: int
    beta_L: float
    beta_H: float
    beta_S: float
    ci_L: tuple[float, float]
    ci_H: tuple[float, float]
    ci_S: tuple[float, float]
    p_values: dict[str, float]

def fit_round_conditioned_regression(
    round_dfs: dict[int, pd.DataFrame],
    q_early_model,
    feature_matrix_fn,
) -> list[CoeffResult]:
    """Per-round logistic regression with Q_early covariate."""
    ...

def fit_interaction_model(
    df: pd.DataFrame,
    q_early_model,
    feature_matrix_fn,
) -> dict:
    """Round × ambiguity interaction term via statsmodels."""
    ...

def bootstrap_coefficient_ci(
    round_dfs: dict,
    q_early_model,
    n_iter: int = 1000,
    seed: int = 42,
) -> list[CoeffResult]:
    """Bootstrap 95% CI on β differences across rounds."""
    ...

def placebo_permutation_test(
    round_dfs: dict,
    q_early_model,
    n_iter: int = 1000,
    seed: int = 42,
) -> dict[str, float]:
    """Returns permutation p-values per coefficient."""
    ...

def webgpt_dose_response(
    webgpt_df: pd.DataFrame,
    feature_matrix_fn,
) -> dict:
    """Within-annotator dose-response on WebGPT secondary dataset."""
    ...

def apply_bonferroni(p_values: dict[str, float], k: int = 3) -> dict[str, float]:
    """Returns corrected p-values (α/k = 0.0167)."""
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: config, analysis

```python
import matplotlib.pyplot as plt
from pathlib import Path

def plot_coefficient_drift(results: list, out_dir: Path) -> None:
    """Figure 1: β_L, β_H, β_S per round with 95% CI."""
    ...

def plot_ambiguity_stratification(results_hi, results_lo, out_dir: Path) -> None:
    """Figure 2: coefficient drift high vs low ambiguity groups."""
    ...

def plot_q_early_calibration(q_early_model, X, y, out_dir: Path) -> None:
    """Figure 3: calibration curve, Brier score by round."""
    ...

def plot_placebo_distribution(perm_results: dict, observed: dict, out_dir: Path) -> None:
    """Figure 4: null distribution vs observed coefficients."""
    ...

def plot_feature_correlation(X: any, out_dir: Path) -> None:
    """Figure 5: feature correlation heatmap (VIF diagnostic)."""
    ...

def plot_webgpt_dose_response(webgpt_results: dict, out_dir: Path) -> None:
    """Figure 6: within-annotator dose-response validation."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: all modules

```python
def main() -> dict:
    """
    Executes full pipeline:
    1. load_hh_rlhf + validate_round_coverage (pre-condition gate)
    2. build_feature_matrix per round
    3. QEarlyModel.fit(r1) + calibrate + gate_check (Brier gate)
    4. bootstrap_coefficient_ci + placebo_permutation_test
    5. fit_interaction_model
    6. webgpt_dose_response
    7. apply_bonferroni
    8. All 6 figures
    Returns results dict with gate_passed bool.
    """
    ...

if __name__ == "__main__":
    results = main()
    print(f"Gate passed: {results['gate_passed']}")
    print(f"Drift significant: {results['drift_significant']}")
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading & Stratification | Implement data_loader.py: HH-RLHF load, round stratification, WebGPT load, coverage gate | 8 | 2+2+2+2 |
| A-2 | Feature Extraction | Implement features.py: β_L, β_H, β_S extraction, VIF check, Fleiss κ, ambiguity partition | 10 | 3+2+3+2 |
| A-3 | Q_early Calibration | Implement q_early.py: logistic regression on r1, affine recalibration, Brier gate check | 9 | 2+2+3+2 |
| A-4 | Coefficient Analysis | Implement analysis.py: round-conditioned regression, bootstrap CI, placebo permutation, interaction model, Bonferroni | 14 | 3+3+4+4 |
| A-5 | Visualization | Implement visualize.py: 6 figures saved to h-e1/figures/ | 7 | 2+2+1+2 |
| A-6 | Pipeline Integration | Implement run_experiment.py: wire all modules, gate logic, results reporting | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-2, A-3], Low(4-8): [A-1, A-5, A-6]

---

## Gate Logic

```
Pre-condition gate: round coverage >= 80%  →  else ABORT
Q_early Brier gate: |brier_r2 - brier_r1| < 0.02  →  else ABORT
MUST_WORK gate: any β drift p < 0.0167 (Bonferroni) AND placebo p > 0.05  →  PASS
```

## External Dependencies

| Library | Usage |
|---------|-------|
| `datasets` (HuggingFace) | load_dataset for HH-RLHF + WebGPT |
| `scikit-learn` | LogisticRegression, StandardScaler, CalibratedClassifierCV, brier_score_loss |
| `statsmodels` | interaction term OLS/logit, Fleiss κ |
| `scipy.stats` | bootstrap utilities |
| `matplotlib`, `seaborn` | all 6 figures |
| `pandas`, `numpy` | dataframe / array operations |
