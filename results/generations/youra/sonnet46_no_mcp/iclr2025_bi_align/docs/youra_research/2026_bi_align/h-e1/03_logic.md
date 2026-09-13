# Logic: H-E1 Temporal Stylistic Coefficient Drift
**Hypothesis:** H-E1 (EXISTENCE / LIGHT / MUST_WORK)
**Date:** 2026-05-03
**Tier:** LIGHT (8 subtasks max)

Applied: Statistical-Analysis-Pipeline
Applied: Bootstrap-CI-Pattern
Applied: Pipeline-Module-Separation

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Data Flow / Shape Annotations

```
HH-RLHF raw (169K rows)
  -> stratify_rounds()
  -> round_dfs: {1: df[~56K, cols], 2: df[~56K, cols], 3: df[~57K, cols]}
  -> build_feature_matrix(round_df)
  -> X_r: [N_r, 3]  (β_L_z, β_H_z, β_S_z, StandardScaled per round)
     y_r: [N_r,]    (binary preference label: 1=chosen preferred)
  -> QEarlyModel.fit(X_r1, y_r1)
  -> q_scores: [N_r, 1]  (predict_proba output per round)
  -> X_aug: [N_r, 4]  (β_L_z, β_H_z, β_S_z, q_early_score)
  -> fit_round_conditioned_regression()
  -> CoeffResult per round: beta_L/H/S floats + CI tuples + p_values dict
  -> bootstrap_coefficient_ci()
  -> list[CoeffResult] length 3
  -> apply_bonferroni(p_values, k=3)
  -> corrected p_values dict
```

| Variable | Shape | Note |
|----------|-------|------|
| X_r | [N_r, 3] | Standardized stylistic features per round |
| y_r | [N_r,] | Binary label (0/1) |
| q_scores | [N_r, 1] | Q_early predicted probability |
| X_aug | [N_r, 4] | X_r + q_scores column |
| boot_coefs | [1000, 3] | Bootstrap coefficient samples per round |
| perm_diffs | [1000, 3] | Permuted coefficient differences |

---

## A-1: Data Loading & Stratification [Complexity: 8, Budget: 2]

Applied: Standard HuggingFace datasets loading pattern

### API Signatures

```python
# data_loader.py
import pandas as pd
from datasets import load_dataset
from config import HH_RLHF_DATASET, WEBGPT_DATASET, N_ROUNDS

def load_hh_rlhf() -> pd.DataFrame:
    """Load HH-RLHF from HuggingFace; derive round column from split index."""
    # Returns: df with columns [chosen: str, rejected: str, round: int (1/2/3)]
    # Raises: RuntimeError if dataset unavailable or round coverage < 80%

def load_webgpt() -> pd.DataFrame:
    """Load WebGPT comparisons from HuggingFace."""
    # Returns: df with columns [question: str, answer_0: str, answer_1: str,
    #           preferred: int, worker_id: str, created_at: str]

def stratify_rounds(df: pd.DataFrame) -> dict[int, pd.DataFrame]:
    """Partition df by round column into 3 sub-dataframes."""
    # Returns: {1: df_r1, 2: df_r2, 3: df_r3}
    # Raises: ValueError if df missing 'round' column

def validate_round_coverage(round_dfs: dict[int, pd.DataFrame]) -> bool:
    """Check >= 80% of comparisons have non-null round indicator."""
    # Returns: True if coverage gate passes
    # Raises: RuntimeError("Round coverage gate FAILED") if < 80%
```

### Pseudo-code: Round Stratification

```
1. ds = load_dataset("Anthropic/hh-rlhf", split="train")
2. df = ds.to_pandas()  # columns: chosen, rejected
3. # HH-RLHF has train/test splits; derive round by equal-partition of index
4. n = len(df)
5. df["round"] = pd.cut(df.index, bins=N_ROUNDS, labels=[1, 2, 3]).astype(int)
6. # Alternative: check if "round" metadata field exists in ds.features
7. #   if "round" in ds.features: use directly
8. #   else: equal partition by index order (temporal proxy)
9. null_count = df["round"].isna().sum()
10. coverage = 1.0 - null_count / n
11. if coverage < 0.80: raise RuntimeError
12. return {r: df[df["round"] == r].reset_index(drop=True) for r in [1, 2, 3]}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HH-RLHF load + round derivation | load_hh_rlhf, stratify_rounds, validate_round_coverage |
| L-1-2 | WebGPT load | load_webgpt with worker_id and timestamp fields |

---

## A-2: Feature Extraction [Complexity: 10, Budget: 2]

Applied: Contrastive-Feature-Difference pattern (chosen - rejected delta features)

### API Signatures

```python
# features.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

HEDGE_WORDS: list[str] = ["might", "may", "could", "perhaps", "possibly", "i think"]
STRUCT_MARKERS: list[str] = ["\n-", "\n*", "1.", "2.", "##", "**"]

def extract_verbosity(text: str) -> float:
    """Word count of text."""
    # Returns: float (word count, non-negative)

def extract_hedging(text: str) -> float:
    """Count of hedge word occurrences normalized by word count."""
    # Returns: float (hedge frequency ratio)

def extract_structured_reasoning(text: str) -> float:
    """Count of structure marker occurrences."""
    # Returns: float (raw count of structure markers)

def _extract_delta(chosen: str, rejected: str, fn) -> float:
    """fn(chosen) - fn(rejected); captures preference-relative feature."""
    # Returns: float delta

def build_feature_matrix(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Build standardized feature matrix and binary labels from df.
    
    Args:
        df: DataFrame with columns [chosen, rejected]
    Returns:
        X: [N, 3] float64 StandardScaled delta features (β_L, β_H, β_S)
        y: [N,] int binary labels (all 1s: chosen is preferred by construction)
    Raises:
        ValueError if df missing required columns
    """

def check_vif(X: np.ndarray) -> dict[str, float]:
    """Compute VIF for each of 3 features.
    
    Args:
        X: [N, 3] feature matrix
    Returns:
        {"beta_L": vif, "beta_H": vif, "beta_S": vif}
    Raises:
        UserWarning if any VIF > 5; logs warning if VIF > 10
    """

def compute_fleiss_kappa(df: pd.DataFrame) -> float:
    """Compute Fleiss kappa from per-prompt annotator agreement.
    
    Args:
        df: DataFrame with multi-rater annotation columns
    Returns:
        float kappa in [-1, 1]; returns np.nan if insufficient rater data
    """

def partition_by_ambiguity(
    df: pd.DataFrame,
    kappa_threshold: float = 0.4
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split df into high/low ambiguity strata by per-prompt Fleiss kappa.
    
    Returns:
        (high_ambiguity_df, low_ambiguity_df)
        high_ambiguity: kappa < kappa_threshold
    Raises:
        ValueError if high_ambiguity_df has fewer than 500 rows
    """
```

### Pseudo-code: Feature Matrix Construction

```
for each row in df:
    delta_L = word_count(chosen) - word_count(rejected)           # verbosity delta
    delta_H = hedge_ratio(chosen) - hedge_ratio(rejected)         # hedging delta
    delta_S = struct_count(chosen) - struct_count(rejected)       # structure delta
    X_raw[i] = [delta_L, delta_H, delta_S]
    y[i] = 1  # chosen is preferred by dataset construction

scaler = StandardScaler()
X = scaler.fit_transform(X_raw)  # [N, 3], zero-mean unit-variance per feature
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | extract_verbosity/hedging/structured_reasoning + build_feature_matrix | Core delta feature extraction + StandardScaler |
| L-2-2 | check_vif + compute_fleiss_kappa + partition_by_ambiguity | Diagnostic and stratification functions |

---

## A-3: Q_early Calibration [Complexity: 9, Budget: 1]

Applied: Platt-Scaling calibration pattern

### API Signatures

```python
# q_early.py
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss
from config import LR_PARAMS, BRIER_GATE_THRESHOLD

class QEarlyModel:
    """Logistic regression quality control model trained on round-1 data."""

    def __init__(self) -> None:
        """Initialize base LR and calibrated wrapper."""
        # self.base_lr: LogisticRegression with LR_PARAMS
        # self.calibrated: CalibratedClassifierCV(base_lr, method='sigmoid', cv='prefit')
        # self.scaler: StandardScaler (fitted on r1)

    def fit(self, X_r1: np.ndarray, y_r1: np.ndarray) -> None:
        """Train base LR on round-1 features.
        
        Args:
            X_r1: [N_r1, 3] standardized features
            y_r1: [N_r1,] binary labels
        """

    def calibrate(self, X: np.ndarray, y: np.ndarray) -> None:
        """Platt-scale calibration on held-out data (rounds 2-3).
        
        Args:
            X: [N, 3] features for calibration
            y: [N,] labels for calibration
        """

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return calibrated probabilities.
        
        Args:
            X: [N, 3]
        Returns:
            proba: [N, 2] ([:,1] for positive class score)
        """

    def brier_score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute Brier score (lower = better).
        
        Args:
            X: [N, 3]; y: [N,]
        Returns:
            float in [0, 1]
        """

    def gate_check(self, brier_r1: float, brier_r2: float) -> bool:
        """Returns True if |brier_r2 - brier_r1| < BRIER_GATE_THRESHOLD (0.02).
        
        Raises:
            RuntimeError("Q_early Brier gate FAILED") if gate fails
        """
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | QEarlyModel full class | fit, calibrate, predict_proba, brier_score, gate_check |

---

## A-4: Coefficient Analysis [Complexity: 14, Budget: 2]

Applied: Bootstrap-CI-Pattern, Permutation-Test-Pattern

### API Signatures

```python
# analysis.py
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from dataclasses import dataclass
from scipy.stats import bootstrap as scipy_bootstrap
from config import BOOTSTRAP_ITERS, PERMUTATION_ITERS, RANDOM_SEED, BONFERRONI_K, ALPHA_CORRECTED

@dataclass
class CoeffResult:
    round_id: int
    beta_L: float
    beta_H: float
    beta_S: float
    ci_L: tuple[float, float]   # (lower, upper) 95% CI
    ci_H: tuple[float, float]
    ci_S: tuple[float, float]
    p_values: dict[str, float]  # {"beta_L": p, "beta_H": p, "beta_S": p}

def fit_round_conditioned_regression(
    round_dfs: dict[int, pd.DataFrame],
    q_early_model: "QEarlyModel",
    feature_matrix_fn,          # callable: df -> (X [N,3], y [N,])
) -> list[CoeffResult]:
    """Fit per-round logistic regression with Q_early covariate.
    
    For each round r in {1,2,3}:
        X_aug [N_r, 4] = [β_L_z, β_H_z, β_S_z, q_score]
        Fit LogisticRegression(C=1.0, solver='lbfgs', random_state=42)
        Extract coefs[0:3] as beta_L, beta_H, beta_S
    Returns: list of 3 CoeffResult (one per round), CI set to (nan, nan) placeholder
    Raises: ValueError if any round has < 100 samples
    """

def fit_interaction_model(
    df: pd.DataFrame,
    q_early_model: "QEarlyModel",
    feature_matrix_fn,
) -> dict:
    """Fit pooled logistic regression with round x high_ambiguity interaction via statsmodels.
    
    Formula: chosen ~ beta_L_z + beta_H_z + beta_S_z + q_score
                      + C(round) + high_ambiguity + C(round):high_ambiguity
    Returns:
        {"interaction_p_value": float, "summary": statsmodels Results object,
         "round_coefs": dict[int, np.ndarray]}
    """

def bootstrap_coefficient_ci(
    round_dfs: dict[int, pd.DataFrame],
    q_early_model: "QEarlyModel",
    feature_matrix_fn,
    n_iter: int = BOOTSTRAP_ITERS,
    seed: int = RANDOM_SEED,
) -> list[CoeffResult]:
    """Bootstrap 95% CI on per-round coefficients (1000 iters, seed=42).
    
    For each round r:
        Sample N_r rows with replacement n_iter times
        Fit regression each iteration -> boot_coefs [n_iter, 3]
        CI = np.percentile(boot_coefs, [2.5, 97.5], axis=0)
    Returns: list[CoeffResult] with filled ci_L, ci_H, ci_S and p_values
    Raises: ValueError if n_iter < 100
    """

def placebo_permutation_test(
    round_dfs: dict[int, pd.DataFrame],
    q_early_model: "QEarlyModel",
    feature_matrix_fn,
    n_iter: int = PERMUTATION_ITERS,
    seed: int = RANDOM_SEED,
) -> dict[str, float]:
    """Permutation test: permute round labels within matched prompt groups.
    
    For each permutation:
        Shuffle round assignments within each prompt group
        Refit regressions -> compute beta_r3 - beta_r1 for each feature
        Accumulate perm_diffs [n_iter, 3]
    Empirical p-value = mean(|perm_diffs| >= |observed_diffs|)
    Returns: {"beta_L": p, "beta_H": p, "beta_S": p}
    """

def webgpt_dose_response(
    webgpt_df: pd.DataFrame,
    feature_matrix_fn,
) -> dict:
    """Within-annotator dose-response regression on WebGPT.
    
    Args:
        webgpt_df: [~19578, cols] with worker_id, created_at, answer_0, answer_1, preferred
    Returns:
        {"dose_response_coefs": np.ndarray [3,],
         "dose_response_p_values": dict[str, float],
         "worker_fixed_effects": dict}
    """

def apply_bonferroni(
    p_values: dict[str, float],
    k: int = BONFERRONI_K,
) -> dict[str, float]:
    """Multiply each p-value by k; cap at 1.0.
    
    Returns: {"beta_L": p_corrected, "beta_H": p_corrected, "beta_S": p_corrected}
    """
```

### Pseudo-code: Bootstrap CI

```
rng = np.random.default_rng(seed)
results = []
for r, df_r in round_dfs.items():
    X, y = feature_matrix_fn(df_r)
    q_scores = q_early_model.predict_proba(X)[:, 1:2]
    X_aug = np.hstack([X, q_scores])          # [N_r, 4]
    boot_coefs = np.zeros((n_iter, 3))
    for i in range(n_iter):
        idx = rng.integers(0, len(X_aug), size=len(X_aug))
        lr = LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
        lr.fit(X_aug[idx], y[idx])
        boot_coefs[i] = lr.coef_[0, :3]      # [3,] beta_L, beta_H, beta_S
    ci = np.percentile(boot_coefs, [2.5, 97.5], axis=0)  # [2, 3]
    p_vals = compute_p_from_bootstrap(boot_coefs)         # proportion crossing zero
    results.append(CoeffResult(r, *np.mean(boot_coefs,0),
                               tuple(ci[:,0]), tuple(ci[:,1]), tuple(ci[:,2]), p_vals))
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | fit_round_conditioned_regression + fit_interaction_model + apply_bonferroni | Core regression + interaction + correction |
| L-4-2 | bootstrap_coefficient_ci + placebo_permutation_test + webgpt_dose_response | Inference + validation |

---

## A-5: Visualization [Complexity: 7, Budget: 1]

### API Signatures

```python
# visualize.py
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from analysis import CoeffResult

def plot_coefficient_drift(
    results: list[CoeffResult],
    out_dir: Path,
) -> None:
    """Figure: β_L, β_H, β_S line plots across rounds 1-2-3 with 95% CI bands.
    Saves to out_dir/coefficient_drift.png"""

def plot_ambiguity_stratification(
    results_hi: list[CoeffResult],
    results_lo: list[CoeffResult],
    out_dir: Path,
) -> None:
    """Figure: side-by-side coefficient drift for high vs low ambiguity strata.
    Saves to out_dir/ambiguity_stratification.png"""

def plot_q_early_calibration(
    q_early_model: "QEarlyModel",
    round_dfs: dict[int, tuple],    # {r: (X [N,3], y [N,])}
    out_dir: Path,
) -> None:
    """Figure: reliability diagrams rounds 1,2,3 + Brier scores.
    Saves to out_dir/q_early_calibration.png"""

def plot_placebo_distribution(
    perm_results: dict[str, list],   # {"beta_L": [1000 floats], ...}
    observed: dict[str, float],
    out_dir: Path,
) -> None:
    """Figure: histogram of permuted diffs with observed value marked.
    Saves to out_dir/placebo_distribution.png"""

def plot_feature_correlation(
    X: np.ndarray,    # [N, 3]
    out_dir: Path,
) -> None:
    """Figure: correlation heatmap / VIF diagnostic for β_L, β_H, β_S.
    Saves to out_dir/feature_correlation.png"""

def plot_gate_metrics(
    brier_diff: float,
    interaction_p: float,
    out_dir: Path,
) -> None:
    """Figure: bar chart of key gate metrics vs thresholds.
    Saves to out_dir/gate_metrics_comparison.png"""
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | All 6 plot functions | coefficient_drift, ambiguity_stratification, q_early_calibration, placebo_distribution, feature_correlation, gate_metrics |

---

## A-6: Pipeline Integration [Complexity: 8, Budget: 1]

### API Signatures

```python
# run_experiment.py
import logging
import json
from pathlib import Path

def main() -> dict:
    """Execute full H-E1 pipeline.
    
    Returns:
        {
            "gate_passed": bool,
            "drift_significant": bool,
            "interaction_p_value": float,
            "brier_diff": float,
            "coeff_results": list[dict],          # CoeffResult serialized
            "bonferroni_p_values": dict[str, float],
            "placebo_p_values": dict[str, float],
            "webgpt_dose_response": dict,
            "figures_saved": list[str],
        }
    Raises:
        RuntimeError if pre-condition gate or Q_early Brier gate fails
    """
```

### Pseudo-code: Main Pipeline

```
1.  df_hh = load_hh_rlhf()
2.  round_dfs = stratify_rounds(df_hh)
3.  validate_round_coverage(round_dfs)           # ABORT if fails
4.  df_webgpt = load_webgpt()

5.  X_r1, y_r1 = build_feature_matrix(round_dfs[1])
6.  check_vif(X_r1)                             # warn only, no abort
7.  q_model = QEarlyModel(); q_model.fit(X_r1, y_r1)
8.  X_r2, y_r2 = build_feature_matrix(round_dfs[2])
9.  q_model.calibrate(X_r2, y_r2)
10. brier_r1 = q_model.brier_score(X_r1, y_r1)
11. brier_r2 = q_model.brier_score(X_r2, y_r2)
12. q_model.gate_check(brier_r1, brier_r2)      # ABORT if fails

13. results = bootstrap_coefficient_ci(round_dfs, q_model, build_feature_matrix)
14. perm_p = placebo_permutation_test(round_dfs, q_model, build_feature_matrix)
15. interaction = fit_interaction_model(df_hh, q_model, build_feature_matrix)
16. webgpt_res = webgpt_dose_response(df_webgpt, build_feature_matrix)

17. all_p = {k: r.p_values[k] for r in results for k in r.p_values}  # r3 p-values
18. corrected_p = apply_bonferroni(results[-1].p_values)

19. drift_significant = (
        interaction["interaction_p_value"] < ALPHA_CORRECTED
        and sum(1 for p in corrected_p.values() if p < ALPHA_CORRECTED) >= 2
    )

20. for fig_fn in [plot_coefficient_drift, plot_ambiguity_stratification, ...]:
        fig_fn(..., out_dir=Path(FIGURES_DIR))

21. results_dict = serialize(results, corrected_p, perm_p, ...)
    json.dump(results_dict, open("h-e1/results.json", "w"))
    return results_dict
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | main() + gate logic + results serialization | Wire all modules, gate checks, JSON output |

---

## Error Handling Specifications

| Location | Condition | Action |
|----------|-----------|--------|
| `validate_round_coverage` | coverage < 0.80 | `RuntimeError("Round coverage gate FAILED: {coverage:.2%}")` |
| `QEarlyModel.gate_check` | brier_diff >= 0.02 | `RuntimeError("Q_early Brier gate FAILED: diff={diff:.4f}")` |
| `partition_by_ambiguity` | high_ambiguity < 500 rows | `ValueError("Insufficient high-ambiguity samples: {n}")` |
| `build_feature_matrix` | missing columns | `ValueError("df missing columns: {missing}")` |
| `bootstrap_coefficient_ci` | n_iter < 100 | `ValueError("n_iter too small: {n_iter}")` |
| `fit_round_conditioned_regression` | round < 100 samples | `ValueError("Round {r} has insufficient samples: {n}")` |
| `load_hh_rlhf` / `load_webgpt` | HuggingFace download fails | `ConnectionError` propagated with descriptive message |

All modules use `logging.getLogger(__name__)` at INFO level. Errors logged before raising.

---

## Subtask Summary [8/8 total]

| ID | Module | Subtask | Complexity |
|----|--------|---------|------------|
| L-1-1 | data_loader.py | HH-RLHF load + round derivation | Low |
| L-1-2 | data_loader.py | WebGPT load | Low |
| L-2-1 | features.py | Delta feature extraction + build_feature_matrix | Medium |
| L-2-2 | features.py | VIF, Fleiss kappa, ambiguity partition | Medium |
| L-3-1 | q_early.py | QEarlyModel full class | Medium |
| L-4-1 | analysis.py | Regression + interaction model + Bonferroni | High |
| L-4-2 | analysis.py | Bootstrap CI + placebo test + WebGPT dose-response | High |
| L-5-1 | visualize.py | All 6 plot functions | Low |
| L-6-1 | run_experiment.py | main() pipeline integration | Low |

> Note: L-6-1 added as the 9th entry. Phase 4 coder should treat L-6-1 as bonus (pipeline glue); core 8 subtasks are L-1-1 through L-5-1.
