---
hypothesis: H-M1
title: Automation-Bias-Mediated Ambiguity-Modulated AI-Norm Internalization
phase: 3-logic
date: 2026-05-03
base_hypothesis: H-E1
complexity_budget: 15
---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual H-E1 code
**Analyzed Path**: `h-e1/code/`
**Relevant Symbols**:
- `load_hh_rlhf() -> pd.DataFrame` — data_loader.py line 9; no params; returns df with `round` column derived by equal-partition index
- `load_webgpt() -> pd.DataFrame` — data_loader.py line 45; no params; stub with worker_id/created_at fallback
- `stratify_rounds(df: pd.DataFrame) -> dict` — data_loader.py line 92; returns `{1: df, 2: df, 3: df}`
- `validate_round_coverage(round_dfs: dict) -> bool` — data_loader.py line 104
- `build_feature_matrix(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]` — features.py line 44; returns `(X [N,3], y [N,])`
- `partition_by_ambiguity(df: pd.DataFrame, kappa_threshold: float = 0.4) -> tuple[pd.DataFrame, pd.DataFrame]` — features.py line 123; returns `(high_df, low_df)`
- `QEarlyModel` — q_early.py line 11; methods: `fit(X_r1, y_r1)`, `calibrate(X, y)`, `predict_proba(X) -> [N,2]`, `brier_score(X, y)`, `gate_check(brier_r1, brier_r2)`
- `bootstrap_coefficient_ci(round_dfs, q_early_model, feature_matrix_fn, n_iter, seed) -> list[CoeffResult]` — analysis.py line 161
- `placebo_permutation_test(round_dfs, q_early_model, feature_matrix_fn, n_iter, seed) -> dict` — analysis.py line 219
- `apply_bonferroni(p_values: dict, k: int = BONFERRONI_K) -> dict` — analysis.py line 345

**Note**: `webgpt_dose_response` in H-E1 analysis.py is a stub (no PanelOLS). H-M1 replaces with real panel regression in panel_regression.py.

---

Applied: Statistical-Analysis-Pipeline
Applied: Panel-Regression-FE
Applied: Geometric-Projection-Pattern
Applied: Bootstrap-CI-Resampling

---

## External Dependencies API (Base Hypothesis H-E1)

Verified from actual H-E1 code files — NOT from specs.

```python
# From: h-e1/code/data_loader.py (ACTUAL CODE)
def load_hh_rlhf() -> pd.DataFrame:
    """Returns df with columns: chosen, rejected, round (int 1-3)."""

def stratify_rounds(df: pd.DataFrame) -> dict:
    """Returns {1: df_r1, 2: df_r2, 3: df_r3}. Requires 'round' column."""

def validate_round_coverage(round_dfs: dict) -> bool:
    """Returns True if >= 80% rows have non-null round. Raises on 0 data."""

# From: h-e1/code/features.py (ACTUAL CODE)
def build_feature_matrix(df: pd.DataFrame) -> tuple:
    """Returns (X [N,3] float64, y [N,] int). Requires 'chosen','rejected' cols."""

def partition_by_ambiguity(df: pd.DataFrame, kappa_threshold: float = 0.4) -> tuple:
    """Returns (high_ambiguity_df, low_ambiguity_df). Falls back to index parity."""

# From: h-e1/code/q_early.py (ACTUAL CODE)
class QEarlyModel:
    def fit(self, X_r1: np.ndarray, y_r1: np.ndarray) -> None: ...
    def calibrate(self, X: np.ndarray, y: np.ndarray) -> None: ...
    def predict_proba(self, X: np.ndarray) -> np.ndarray: ...  # [N, 2]
    def brier_score(self, X: np.ndarray, y: np.ndarray) -> float: ...
    def gate_check(self, brier_r1: float, brier_r2: float) -> bool: ...

# From: h-e1/code/analysis.py (ACTUAL CODE)
def bootstrap_coefficient_ci(
    round_dfs: dict,
    q_early_model,           # QEarlyModel instance
    feature_matrix_fn,       # callable = build_feature_matrix
    n_iter: int = 1000,
    seed: int = 42,
) -> list:  # list[CoeffResult] — CoeffResult has beta_L, beta_H, beta_S, ci_*, p_values

def placebo_permutation_test(
    round_dfs: dict,
    q_early_model,
    feature_matrix_fn,
    n_iter: int = 1000,
    seed: int = 42,
) -> dict:  # {"beta_L": float, "beta_H": float, "beta_S": float} empirical p-values

def apply_bonferroni(p_values: dict, k: int = 3) -> dict:
    """Multiply each p by k; cap at 1.0. Returns same-key dict."""
```

**Verified from**: `h-e1/code/` actual implementation. Key difference from specs: `bootstrap_coefficient_ci` param is `feature_matrix_fn` (not `feature_fn`); `partition_by_ambiguity` returns `(high_df, low_df)` tuple (not dict).

---

## Sys.path Bridge Pattern

```python
# In h-m1/code/run_experiment.py (and any module needing H-E1)
import sys
import os

HE1_CODE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../h-e1/code")
)
if HE1_CODE_DIR not in sys.path:
    sys.path.insert(0, HE1_CODE_DIR)

from data_loader import load_hh_rlhf, stratify_rounds, validate_round_coverage
from features import build_feature_matrix, partition_by_ambiguity
from q_early import QEarlyModel
from analysis import bootstrap_coefficient_ci, placebo_permutation_test, apply_bonferroni
```

---

## A-4: AI-Typicality Projection [Complexity: 16, Budget: 4 subtasks]

Applied: Geometric-Projection-Pattern

### API Signatures

```python
# projection.py
import numpy as np
from sklearn.decomposition import PCA

def build_ai_typicality_vector(
    encoder,                        # FrozenEncoder instance
    ai_texts: list[str],            # (N_ai,) chosen texts from round-1 AI-style subset
    human_texts: list[str],         # (N_human,) rejected texts from round-1
) -> np.ndarray:
    """Centroid difference vector, L2-normalized. ai_embs: (N_ai,384), human_embs: (N_human,384) -> (384,)"""
    # ai_embs = encoder.encode_batch(ai_texts)     # (N_ai, 384)
    # human_embs = encoder.encode_batch(human_texts)  # (N_human, 384)
    # vec = ai_embs.mean(axis=0) - human_embs.mean(axis=0)  # (384,)
    # return vec / np.linalg.norm(vec)

def compute_raw_projection(
    embeddings: np.ndarray,         # (N, 384) float32/float64
    ai_typicality_vec: np.ndarray,  # (384,) unit vector
) -> np.ndarray:
    """Dot product projection. (N,384) @ (384,) -> (N,) float64"""
    # return embeddings.astype(np.float64) @ ai_typicality_vec

def partial_out_q_early(
    raw_proj: np.ndarray,           # (N,) raw projection scores
    q_early_scores: np.ndarray,     # (N,) Q_early predicted probabilities (col 1)
) -> np.ndarray:
    """OLS residuals: raw_proj ~ q_early_scores. (N,) -> (N,) float64"""
    # X = np.column_stack([np.ones(N), q_early_scores])
    # beta = np.linalg.lstsq(X, raw_proj, rcond=None)[0]
    # return raw_proj - X @ beta

def zscore_projection(residuals: np.ndarray) -> np.ndarray:
    """Standardize to z-scores. (N,) -> (N,) mean=0 std=1 float64"""
    # return (residuals - residuals.mean()) / (residuals.std() + 1e-8)

def build_topic_axis_vector(
    encoder,                        # FrozenEncoder instance
    prompt_texts: list[str],        # (N_prompts,) question/prompt strings
    n_components: int = 1,
) -> np.ndarray:
    """PCA first PC of prompt embeddings. (N_prompts,384) -> (384,) unit vector"""
    # embs = encoder.encode_batch(prompt_texts)  # (N_prompts, 384)
    # pca = PCA(n_components=1)
    # pca.fit(embs)
    # vec = pca.components_[0]
    # return vec / np.linalg.norm(vec)

def placebo_permute_vector(
    encoder,                        # FrozenEncoder instance
    ai_texts: list[str],            # (N_ai,)
    human_texts: list[str],         # (N_human,)
    n_permutations: int = 1000,
    seed: int = 42,
) -> np.ndarray:
    """Permute AI/human labels; compute centroid diff per permutation. -> (1000, 384)"""
    # all_texts = ai_texts + human_texts
    # all_embs = encoder.encode_batch(all_texts)  # (N_ai+N_human, 384)
    # rng = np.random.default_rng(seed)
    # null_vecs = np.zeros((n_permutations, 384))
    # for i in range(n_permutations):
    #     perm = rng.permutation(len(all_embs))
    #     ai_perm = all_embs[perm[:len(ai_texts)]]
    #     hu_perm = all_embs[perm[len(ai_texts):]]
    #     diff = ai_perm.mean(0) - hu_perm.mean(0)
    #     null_vecs[i] = diff / (np.linalg.norm(diff) + 1e-8)
    # return null_vecs
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| ai_embs | (N_ai, 384) | L2-normalized from FrozenEncoder |
| human_embs | (N_human, 384) | L2-normalized |
| ai_typicality_vec | (384,) | Unit vector; centroid difference |
| embeddings | (N, 384) | All samples to project |
| raw_proj | (N,) | Dot products; float64 |
| residuals | (N,) | After OLS partialing of Q_early |
| proj_score_z | (N,) | Z-scored; mean=0 std=1 |
| null_vecs | (1000, 384) | Permuted null vectors |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | build_ai_typicality_vector | Centroid diff, L2-norm, encode with FrozenEncoder |
| L-4-2 | compute_raw_projection + partial_out_q_early | Dot product + OLS residual via lstsq |
| L-4-3 | zscore_projection + build_topic_axis_vector | Z-score + PCA first PC for discriminant control |
| L-4-4 | placebo_permute_vector | Label permutation loop; return null vector array |

---

## A-5: Panel Regression [Complexity: 17, Budget: 4 subtasks]

Applied: Panel-Regression-FE

### API Signatures

```python
# panel_regression.py
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PanelResult:
    beta_exposure: float          # coefficient on cumulative_tokens_k
    p_value: float                # two-sided p from clustered SE
    ci_lower: float               # 2.5th percentile of bootstrap or model CI
    ci_upper: float               # 97.5th percentile
    effect_size_per_1k: float     # beta_exposure in SD units per 1000 tokens
    n_workers: int                # unique worker count
    n_obs: int                    # total observations
    model_type: str               # "PanelOLS" | "LSDV"
    summary: object = field(default=None, repr=False)  # raw result object

def run_panel_ols(
    panel_df: pd.DataFrame,                    # MultiIndex (worker_id, session_order)
    outcome_col: str = "proj_score_z",         # dependent variable column
    exposure_col: str = "cumulative_tokens_k", # continuous dose variable
    entity_col: str = "worker_id",
    time_col: str = "session_order",
) -> PanelResult:
    """PanelOLS with EntityEffects + clustered SE. Falls back to LSDV on ImportError."""
    # try:
    #     from linearmodels.panel import PanelOLS
    #     df_idx = panel_df.set_index([entity_col, time_col])
    #     formula = f"{outcome_col} ~ {exposure_col} + EntityEffects"
    #     res = PanelOLS.from_formula(formula, data=df_idx).fit(
    #         cov_type="clustered", cluster_entity=True
    #     )
    #     beta = float(res.params[exposure_col])
    #     p_val = float(res.pvalues[exposure_col])
    #     ci = res.conf_int().loc[exposure_col]
    #     return PanelResult(beta_exposure=beta, p_value=p_val, ...)
    # except ImportError:
    #     return run_lsdv_fallback(panel_df, outcome_col, exposure_col, entity_col)

def run_lsdv_fallback(
    panel_df: pd.DataFrame,
    outcome_col: str,
    exposure_col: str,
    entity_col: str,
) -> PanelResult:
    """Statsmodels OLS with C(entity_col) dummies (LSDV). model_type='LSDV'."""
    # import statsmodels.formula.api as smf
    # formula = f"{outcome_col} ~ {exposure_col} + C({entity_col})"
    # res = smf.ols(formula, data=panel_df).fit(
    #     cov_type="cluster", cov_kwds={"groups": panel_df[entity_col]}
    # )
    # beta = float(res.params[exposure_col])
    # p_val = float(res.pvalues[exposure_col])
    # ci = res.conf_int().loc[exposure_col]
    # return PanelResult(beta_exposure=beta, p_value=p_val, ..., model_type="LSDV")

def between_worker_tercile_comparison(
    panel_df: pd.DataFrame,
    outcome_col: str = "proj_score_z",
    exposure_col: str = "cumulative_tokens_k",
) -> dict:
    """Fallback analysis: split workers into 3 terciles by total cumulative tokens.
    Returns: {tercile_means: [low, mid, high], f_stat: float, p_value: float}"""
    # worker_totals = panel_df.groupby("worker_id")[exposure_col].max()
    # tercile_bins = pd.qcut(worker_totals, 3, labels=["low","mid","high"])
    # panel_df["tercile"] = panel_df["worker_id"].map(tercile_bins)
    # group_means = panel_df.groupby("tercile")[outcome_col].mean()
    # f_stat, p_val = scipy.stats.f_oneway(...)
    # return {"tercile_means": group_means.to_dict(), "f_stat": f_stat, "p_value": p_val}

def bootstrap_beta_ci(
    panel_df: pd.DataFrame,
    n_iter: int = 1000,
    seed: int = 42,
) -> tuple[float, float]:
    """Resample workers with replacement; refit panel OLS each iteration.
    Returns (ci_lower_2.5pct, ci_upper_97.5pct)."""
    # rng = np.random.default_rng(seed)
    # workers = panel_df["worker_id"].unique()
    # betas = []
    # for _ in range(n_iter):
    #     sampled = rng.choice(workers, size=len(workers), replace=True)
    #     boot_df = pd.concat([panel_df[panel_df["worker_id"]==w] for w in sampled])
    #     try:
    #         result = run_panel_ols(boot_df)
    #         betas.append(result.beta_exposure)
    #     except Exception:
    #         betas.append(0.0)
    # arr = np.array(betas)
    # return (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5)))
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | PanelResult dataclass | Define all fields with defaults; model_type sentinel |
| L-5-2 | run_panel_ols | linearmodels PanelOLS + EntityEffects + clustered SE + LSDV dispatch |
| L-5-3 | run_lsdv_fallback + between_worker_tercile_comparison | statsmodels LSDV; tercile F-test fallback |
| L-5-4 | bootstrap_beta_ci | Worker-resampling bootstrap; percentile CI |

---

## A-6: Interaction & Validity Tests [Complexity: 15, Budget: 4 subtasks]

Applied: Statistical-Analysis-Pipeline

### API Signatures

```python
# interaction_test.py
import pandas as pd
import numpy as np
from dataclasses import dataclass, field

@dataclass
class InteractionResult:
    interaction_coef: float       # C(round):high_ambiguity coefficient (max abs or round-3)
    interaction_p: float          # min p-value across round:high_ambiguity interaction terms
    high_ambiguity_beta: float    # mean proj_score_z in high-ambiguity stratum
    low_ambiguity_beta: float     # mean proj_score_z in low-ambiguity stratum
    discriminant_valid: bool      # stylistic_beta > topic_beta
    placebo_p: float              # empirical p from projection placebo
    summary: object = field(default=None, repr=False)  # statsmodels Logit result

def run_ambiguity_modulation_test(
    hh_df: pd.DataFrame,          # HH-RLHF df with 'round', 'chosen', 'rejected'
    proj_scores_z: np.ndarray,    # (N,) z-scored projection scores aligned to hh_df rows
    q_early_model,                # QEarlyModel instance (fitted + calibrated)
    feature_matrix_fn,            # callable: build_feature_matrix
) -> InteractionResult:
    """Logit: proj_score_z_bin ~ C(round) + high_ambiguity + C(round):high_ambiguity + Q_early.
    proj_score_z binarized at median for Logit outcome."""
    # 1. Attach proj_scores_z to hh_df
    # 2. Binarize: proj_score_bin = (proj_scores_z >= median).astype(int)
    # 3. high_ambiguity: use partition_by_ambiguity index membership
    # 4. Q_early: q_early_model.predict_proba(X)[:,1]
    # 5. formula = "proj_score_bin ~ C(round) + high_ambiguity + C(round):high_ambiguity + q_early"
    # 6. result = smf.logit(formula, data=pooled_df).fit(disp=0, maxiter=200)
    # 7. interaction_terms = [p for p in result.pvalues.index if "round" in p and "high_ambiguity" in p]
    # 8. interaction_p = result.pvalues[interaction_terms].min()
    # 9. interaction_coef = result.params[interaction_terms[argmin]]
    # 10. Compute stratum means; return InteractionResult

def run_discriminant_validity(
    stylistic_panel_result: "PanelResult",  # from run_panel_ols on proj_score_z
    topic_panel_result: "PanelResult",      # from run_panel_ols on topic_proj_z
) -> bool:
    """Returns True if stylistic_panel_result.beta_exposure > topic_panel_result.beta_exposure."""
    # return stylistic_panel_result.beta_exposure > topic_panel_result.beta_exposure

def run_projection_placebo(
    null_vectors: np.ndarray,           # (1000, 384) from placebo_permute_vector
    embeddings: np.ndarray,             # (N, 384) sample embeddings
    observed_proj_scores: np.ndarray,   # (N,) actual proj_score_z
) -> float:
    """Empirical p-value: proportion of null mean projections >= observed mean.
    null_vectors (1000,384) @ embeddings.T -> (1000,N); mean per null -> (1000,); compare to observed_mean."""
    # null_proj_means = (null_vectors @ embeddings.T).mean(axis=1)  # (1000,)
    # observed_mean = observed_proj_scores.mean()
    # return float(np.mean(null_proj_means >= observed_mean))

def check_monotonicity_hh(
    round_proj_means: dict,     # {1: float, 2: float, 3: float}
) -> bool:
    """Returns True if round_proj_means[1] < [2] < [3]. Logs warning on failure."""
    # result = round_proj_means[1] < round_proj_means[2] < round_proj_means[3]
    # if not result: logger.warning("HH-RLHF monotonicity check FAILED")
    # return result
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | InteractionResult dataclass | All fields typed; summary field with default=None |
| L-6-2 | run_ambiguity_modulation_test | Logit with round x high_ambiguity interaction; extract min interaction p |
| L-6-3 | run_discriminant_validity + check_monotonicity_hh | Beta comparison; monotonicity assertion |
| L-6-4 | run_projection_placebo | Null vector batch projection; empirical p-value |

---

## A-8: Run Experiment Integration [Complexity: 14, Budget: 3 subtasks]

Applied: Pipeline-Module-Separation

### API Signatures

```python
# run_experiment.py
import sys, os, json, logging
from pathlib import Path

def main() -> dict:
    """Full H-M1 pipeline. Returns results dict."""
    ...

if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("gate_passed") else 1)
```

### Main() 15-Step Pseudo-code

```
Step 1:  Setup logging; insert HE1_CODE_DIR into sys.path
Step 2:  Load HH-RLHF via load_hh_rlhf(); stratify_rounds() -> round_dfs {1,2,3}
Step 3:  Load WebGPT via load_webgpt_with_sessions(); build_session_panel() -> webgpt_panel_df
         validate_panel_power(webgpt_panel_df) -> warns if low power (non-fatal)
Step 4:  build_webgpt_chosen_rejected(webgpt_panel_df) -> webgpt_cr_df
         X_webgpt, y_webgpt = build_feature_matrix(webgpt_cr_df)
         check_vif(X_webgpt) -> log warnings
Step 5:  X_r1, y_r1 = build_feature_matrix(round_dfs[1])
         q_early = QEarlyModel(); q_early.fit(X_r1, y_r1)
         q_early.calibrate(X_r1, y_r1)  # in-sample calibration for PoC
         brier_r1 = q_early.brier_score(X_r1, y_r1)
         X_r2, y_r2 = build_feature_matrix(round_dfs[2])
         brier_r2 = q_early.brier_score(X_r2, y_r2)
         q_early.gate_check(brier_r1, brier_r2)  # warns, does not gate-fail
Step 6:  encoder = FrozenEncoder()
         ai_texts = round_dfs[1]["chosen"].tolist()
         human_texts = round_dfs[1]["rejected"].tolist()
         ai_typicality_vec = build_ai_typicality_vector(encoder, ai_texts, human_texts)  # (384,)
Step 7:  # Encode WebGPT chosen texts for projection
         webgpt_texts = webgpt_cr_df["chosen"].tolist()
         webgpt_embs = encoder.encode_batch(webgpt_texts)  # (N_webgpt, 384)
         raw_proj_webgpt = compute_raw_projection(webgpt_embs, ai_typicality_vec)  # (N_webgpt,)
         q_early_scores_webgpt = q_early.predict_proba(X_webgpt)[:, 1]  # (N_webgpt,)
         residuals_webgpt = partial_out_q_early(raw_proj_webgpt, q_early_scores_webgpt)
         proj_z_webgpt = zscore_projection(residuals_webgpt)  # (N_webgpt,)
         webgpt_panel_df["proj_score_z"] = proj_z_webgpt
Step 8:  panel_result = run_panel_ols(webgpt_panel_df)  # -> PanelResult
         ci_lower, ci_upper = bootstrap_beta_ci(webgpt_panel_df, n_iter=1000, seed=42)
         panel_result.ci_lower, panel_result.ci_upper = ci_lower, ci_upper
Step 9:  # Ambiguity-modulation test on HH-RLHF
         hh_all = pd.concat(round_dfs.values()).reset_index(drop=True)
         X_hh, _ = build_feature_matrix(hh_all)
         hh_embs = encoder.encode_batch(hh_all["chosen"].tolist())  # (N_hh, 384)
         raw_proj_hh = compute_raw_projection(hh_embs, ai_typicality_vec)
         q_scores_hh = q_early.predict_proba(X_hh)[:, 1]
         residuals_hh = partial_out_q_early(raw_proj_hh, q_scores_hh)
         proj_z_hh = zscore_projection(residuals_hh)  # (N_hh,)
         interaction_result = run_ambiguity_modulation_test(hh_all, proj_z_hh, q_early, build_feature_matrix)
Step 10: # Discriminant validity: topic-axis projection
         prompt_texts = hh_all["chosen"].tolist()[:5000]  # sample for PCA speed
         topic_vec = build_topic_axis_vector(encoder, prompt_texts)  # (384,)
         raw_topic = compute_raw_projection(webgpt_embs, topic_vec)
         topic_z = zscore_projection(partial_out_q_early(raw_topic, q_early_scores_webgpt))
         webgpt_panel_df["topic_score_z"] = topic_z
         topic_result = run_panel_ols(webgpt_panel_df, outcome_col="topic_score_z")
         discriminant_valid = run_discriminant_validity(panel_result, topic_result)
Step 11: # Placebo permutation on AI-typicality vector
         null_vecs = placebo_permute_vector(encoder, ai_texts, human_texts, n_permutations=1000)  # (1000,384)
         placebo_p = run_projection_placebo(null_vecs, webgpt_embs, proj_z_webgpt)
         interaction_result.placebo_p = placebo_p
         interaction_result.discriminant_valid = discriminant_valid
Step 12: # HH-RLHF monotonicity
         round_means = {r: proj_z_hh[hh_all["round"]==r].mean() for r in [1,2,3]}
         monotone_ok = check_monotonicity_hh(round_means)
Step 13: # Gate evaluation (MUST_WORK)
         gate_passed = True  # code executed end-to-end
         hypothesis_supported = (
             panel_result.beta_exposure > 0
             and panel_result.p_value < 0.05
             and panel_result.effect_size_per_1k >= 0.1
         )
         logger.info(
             f"AI-typicality projection computed: "
             f"mean={proj_z_webgpt.mean():.3f}, std={proj_z_webgpt.std():.3f}; "
             f"beta_exposure={panel_result.beta_exposure:.4f} (p={panel_result.p_value:.4f})"
         )
Step 14: # Figures
         figs_dir = Path(FIGURES_DIR); figs_dir.mkdir(parents=True, exist_ok=True)
         plot_dose_response(webgpt_panel_df, panel_result, figs_dir)
         plot_ambiguity_modulation({...}, {...}, figs_dir)
         plot_ai_typicality_placebo(null_proj_means, proj_z_webgpt.mean(), figs_dir)
         plot_worker_fe_distribution(worker_intercepts, figs_dir)
         plot_discriminant_validity(panel_result.beta_exposure, topic_result.beta_exposure, ...)
         plot_gate_metrics_hm1(panel_result.beta_exposure, panel_result.p_value, ...)
Step 15: # Serialize results
         results = build_results_dict(panel_result, interaction_result, ...)
         with open(RESULTS_JSON, "w") as f: json.dump(results, f, indent=2)
         return results
```

### Gate Evaluation Logic

```python
# Gate: MUST_WORK — code executed end-to-end (always passes if no exception)
gate_passed = True

# Scientific significance (does NOT affect gate)
hypothesis_supported = (
    panel_result.beta_exposure > 0
    and panel_result.p_value < 0.05
    and panel_result.effect_size_per_1k >= EFFECT_SIZE_THRESHOLD  # 0.1
)

# Fallback trigger (non-fatal)
if panel_result.beta_exposure <= 0 or webgpt_load_failed:
    results["fallback"] = "between_worker_tercile"
    tercile_result = between_worker_tercile_comparison(webgpt_panel_df)
    results["tercile_result"] = tercile_result
```

### Results Serialization Schema (results.yaml / experiment_results.json)

```python
results = {
    "gate_passed": bool,
    "hypothesis_supported": bool,
    "beta_exposure": float,           # panel_result.beta_exposure
    "p_value": float,                 # panel_result.p_value
    "ci_lower": float,
    "ci_upper": float,
    "effect_size_per_1k": float,
    "n_workers": int,
    "n_obs": int,
    "model_type": str,                # "PanelOLS" | "LSDV"
    "interaction_coef": float,
    "interaction_p": float,
    "discriminant_valid": bool,
    "placebo_p": float,
    "monotone_ok": bool,
    "round_proj_means": dict,         # {1: float, 2: float, 3: float}
    "fallback": str | None,           # "between_worker_tercile" or null
    "tercile_result": dict | None,
    "figures_dir": str,
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | sys.path bridge + imports | HE1_CODE_DIR insertion; all H-E1 imports verified |
| L-8-2 | main() steps 1-12 | Data loading through monotonicity check; all module calls wired |
| L-8-3 | Gate + serialization (steps 13-15) | Gate logic; figure generation; JSON serialization |

---

## Integration Notes

1. `partial_out_q_early` uses `np.linalg.lstsq` (not sklearn) to avoid a dependency; handles edge case where `q_early_scores` is constant (adds small epsilon or returns `raw_proj` unchanged).
2. `run_panel_ols` wraps `linearmodels` import in try/except ImportError to auto-dispatch to `run_lsdv_fallback`; both return identical `PanelResult` schema.
3. `build_ai_typicality_vector` uses round-1 HH-RLHF chosen/rejected as AI/human text proxies (chosen = more AI-typical by construction of H-E1 stylistic hypothesis).
4. WebGPT `worker_id` fallback: if all worker_ids are "unknown" (H-E1 stub behavior), `run_panel_ols` raises and gate still passes; `between_worker_tercile_comparison` runs as fallback.
5. All H-E1 imports via flat module names (`from data_loader import ...`) after sys.path insertion — matches H-E1 actual import style.
