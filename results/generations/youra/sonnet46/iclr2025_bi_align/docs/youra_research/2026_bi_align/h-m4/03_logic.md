# Logic: H-M4 PM-Score OLS Mediation Regression

**Hypothesis:** H-M4 — PM-proxy predicts C_sem^H←A above surface-feature controls
**Type:** MECHANISM | **Gate:** SHOULD_WORK
**Date:** 2026-03-15

Applied: N/A — Archon KB contains diffusion model content only

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase (base hypothesis h-m2)
**Status:** API signatures verified from actual code via direct file reads (Serena project not activated; files read directly)
**Analyzed Path:** `docs/youra_research/20260315_bi_align/h-m2/code/`
**Relevant Symbols:**
- `Embedder.__init__(model_name, cache_dir)` / `encode_tier(texts, prefix, tier, n_pairs)` — cache key: `{prefix}_{model_slug}_{tier_slug}_{n_pairs}`
- `compute_h_given_a_csem_array(emb_h_next, emb_a_curr, emb_a_shuffle)` → `[N,]`
- `build_topic_control(prompt_embeddings, ai_embeddings, k=5)` — n_jobs=1 hardcoded at line 42
- `build_random_control(ai_embeddings, seed=42)` → shuffled `[N, D]`
- `extract_pairs()` in h-m2 operates on chosen branch only; h-m4 data_loader extends to rejected

---

## External Dependencies API (Base Hypothesis h-m2)

Signatures verified from actual code at `docs/youra_research/20260315_bi_align/h-m2/code/`.

```python
# From: h-m2/code/embedder.py (ACTUAL CODE)
class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "embeddings"):
        ...

    def encode_tier(
        self,
        texts: List[str],
        prefix: str,        # cache key prefix, e.g. "h", "a_chosen", "a_rejected"
        tier: str,          # e.g. "helpful-base"
        n_pairs: int,       # included in cache key
    ) -> np.ndarray:        # [N, D] L2-normalized

# From: h-m2/code/accommodation.py (ACTUAL CODE)
def compute_h_given_a_csem_array(
    emb_h_next: np.ndarray,    # [N, D] L2-normalized
    emb_a_curr: np.ndarray,    # [N, D] L2-normalized
    emb_a_shuffle: np.ndarray, # [N, D] topic-matched shuffle
) -> np.ndarray:               # [N,] per-pair C_sem^H<-A

# From: h-m2/code/controls.py (ACTUAL CODE)
def build_topic_control(
    prompt_embeddings: np.ndarray,  # [N, D]
    ai_embeddings: np.ndarray,      # [N, D]
    k: int = 5,                     # n_jobs=1 hardcoded inside NearestNeighbors
) -> np.ndarray:                    # [N, D]

def build_random_control(
    ai_embeddings: np.ndarray,  # [N, D]
    seed: int = 42,
) -> np.ndarray:                # [N, D] shuffled
```

**CRITICAL — verified from actual code:**
- Function is `build_topic_control` NOT `topic_matched_control` (architecture spec used different name)
- `encode_tier()` parameter is `prefix` (NOT `cache_prefix` or `key_prefix`)
- `n_jobs=1` is hardcoded in `NearestNeighbors(n_jobs=1)` inside `build_topic_control` (controls.py:42)
- Bootstrap uses `rng.choice` (h-m3 fix — confirmed as constraint)

---

## A-5: C_sem Computation per Branch [Complexity: 14, Budget: 3 subtasks]

Applied: N/A — Standard NumPy/SBERT pattern

### API Signatures

```python
# In h-m4/code/run_experiment.py (or data_loader.py helper)

def compute_csem_per_branch(
    tier_pairs: Dict[str, Dict],
    embedder: "Embedder",
    tier: str,
    branch: str,             # 'chosen' | 'rejected'
    seed: int = 42,
) -> np.ndarray:
    """Compute per-row C_sem^H<-A for one tier+branch. Returns [N,] float32."""
    ...

def compute_all_branch_csem(
    tier_pairs: Dict[str, Dict],
    embedder: "Embedder",
    seed: int = 42,
) -> Dict[str, Dict[str, np.ndarray]]:
    """Compute C_sem for all tier x branch combinations.

    Returns: {tier: {'chosen': [N,], 'rejected': [N,]}}
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| emb_h_next | [N, D] | D=384 (MiniLM/paraphrase) or 768 (mpnet) |
| emb_a_curr | [N, D] | branch-specific A_response; distinct cache prefix |
| emb_a_shuffle | [N, D] | topic-matched control via build_topic_control |
| csem_array | [N,] | per-row C_sem^H<-A float32 |

### Pseudo-code

```
for tier in TIER_ORDER:
    for branch in ['chosen', 'rejected']:
        rows = tier_pairs[tier][branch]   # Dict with h_next, a_response, h_prompt
        N = len(rows['h_next'])

        emb_h = embedder.encode_tier(rows['h_next'], prefix='h', tier=tier, n_pairs=N)
        emb_p = embedder.encode_tier(rows['h_prompt'], prefix='p', tier=tier, n_pairs=N)
        # DISTINCT cache prefix per branch — avoids cache key collision
        emb_a = embedder.encode_tier(rows['a_response'], prefix=f'a_{branch}', tier=tier, n_pairs=N)

        emb_shuffle = build_topic_control(emb_p, emb_a, k=5)  # n_jobs=1 hardcoded
        csem[tier][branch] = compute_h_given_a_csem_array(emb_h, emb_a, emb_shuffle)  # [N,]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | chosen/rejected branch embedding | encode_tier() with prefix 'a_chosen' vs 'a_rejected'; distinct cache keys prevent collision |
| L-5-2 | per-row C_sem^H←A via matched-shuffle | compute_h_given_a_csem_array() with build_topic_control; returns [N,] per tier×branch |
| L-5-3 | build regression DataFrame | join c_sem + pm_proxy + tier from all branches; shape [N_rows x (tier, pm_proxy, c_sem)] |

---

## A-6: 4-Stage OLS Regression Engine [Complexity: 15, Budget: 4 subtasks]

Applied: N/A — Standard statsmodels OLS pattern

### API Signatures

```python
# In h-m4/code/regression.py

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

SURFACE_FEATURE_COLS = ['response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len']
TIER_RANK_MAP = {'helpful-base': 1, 'helpful-rejection-sampled': 2, 'helpful-online': 3}

@dataclass
class OLSStageResult:
    model_name: str
    stage: str                               # 'pm_only' | 'full' | 'robustness'
    beta_pm: float
    p_pm: float
    beta_pm_ci: Tuple[float, float]          # 95% CI (lower, upper)
    r_squared: float
    nobs: int
    all_params: Dict[str, float]
    all_pvalues: Dict[str, float]
    all_ci: Dict[str, Tuple[float, float]]
    condition_number: float

@dataclass
class MediationResult:
    model_name: str
    beta_pm_reduced: float
    beta_pm_full: float
    mediation_ratio: float                   # (beta_pm_reduced - beta_pm_full) / beta_pm_reduced
    pm_effect_retained: float               # |beta_pm_full / beta_pm_reduced|
    stage_pm_only: OLSStageResult
    stage_full: OLSStageResult
    stage_robustness: OLSStageResult

def run_pm_only_model(
    df: pd.DataFrame,
    cov_type: str = 'HC3',
) -> OLSStageResult:
    """Stage 1: C_sem ~ const + pm_proxy + tier_T2 + tier_T3 (HC3 SE).

    Tier dummies via pd.get_dummies(drop_first=True), T1=reference.
    """
    ...

def run_full_model(
    df: pd.DataFrame,
    cov_type: str = 'HC3',
) -> OLSStageResult:
    """Stage 2: C_sem ~ const + pm_proxy + 5 surface features + tier_T2 + tier_T3 (HC3 SE)."""
    ...

def run_robustness_model(
    df: pd.DataFrame,
    cov_type: str = 'HC3',
) -> OLSStageResult:
    """Stage 3: Replace pm_proxy with tier_rank (ordinal 1/2/3) + surface features."""
    ...

def compute_mediation_proportion(
    beta_pm_reduced: float,
    beta_pm_full: float,
) -> Tuple[float, float]:
    """Returns (mediation_ratio, pm_effect_retained). Returns (nan, nan) if beta_pm_reduced==0."""
    ...

def compute_vif(
    df: pd.DataFrame,
    feature_cols: List[str],
) -> Dict[str, float]:
    """VIF for each feature via statsmodels variance_inflation_factor. Returns {col: vif}."""
    ...

def check_rank_deficiency(
    df: pd.DataFrame,
    feature_cols: List[str],
) -> bool:
    """Returns True if matrix is full rank (safe to fit OLS), False if deficient."""
    ...

def run_mediation_ols(
    df: pd.DataFrame,
    model_name: str,
    cov_type: str = 'HC3',
) -> MediationResult:
    """Run all 4 stages. Calls stages 1-3 + compute_mediation_proportion + compute_vif."""
    ...
```

### Pseudo-code (key OLS calls)

```
# Stage 1: PM-only
tier_dummies = pd.get_dummies(df['tier'], prefix='tier', drop_first=True)  # T1=ref
X = sm.add_constant(pd.concat([df[['pm_proxy']], tier_dummies], axis=1))
y = df['c_sem']
res1 = sm.OLS(y, X).fit(cov_type='HC3')
beta_pm_reduced = res1.params['pm_proxy']

# Stage 2: Full model
X2 = sm.add_constant(pd.concat([df[['pm_proxy'] + SURFACE_FEATURE_COLS], tier_dummies], axis=1))
res2 = sm.OLS(y, X2).fit(cov_type='HC3')
beta_pm_full = res2.params['pm_proxy']

# Stage 3: Robustness — tier_rank replaces pm_proxy
df['tier_rank'] = df['tier'].map(TIER_RANK_MAP)
X3 = sm.add_constant(df[['tier_rank'] + SURFACE_FEATURE_COLS])
res3 = sm.OLS(y, X3).fit(cov_type='HC3')

# Stage 4: Mediation proportion
med_ratio = (beta_pm_reduced - beta_pm_full) / beta_pm_reduced  if beta_pm_reduced != 0 else nan
retained  = abs(beta_pm_full / beta_pm_reduced)                 if beta_pm_reduced != 0 else nan
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | run_pm_only_model | Stage 1: C_sem ~ pm_proxy + tier dummies, HC3 SE, return OLSStageResult |
| L-6-2 | run_full_model | Stage 2: C_sem ~ pm_proxy + 5 surface + tier dummies, HC3 SE |
| L-6-3 | run_robustness_model | Stage 3: replace pm_proxy with tier_rank ordinal 1/2/3 |
| L-6-4 | compute_mediation_proportion + compute_vif | Stage 4 mediation ratio; VIF with warn if VIF > 10 |

---

## A-10: run_experiment.py Orchestrator [Complexity: 15, Budget: 4 subtasks]

Applied: N/A — Standard Python pipeline pattern

### API Signatures

```python
# In h-m4/code/run_experiment.py

import sys, json, logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m2" / "code"))
from embedder import Embedder
from controls import build_topic_control, build_random_control
from accommodation import compute_h_given_a_csem_array

from config import ExperimentConfig, load_config
from data_loader import split_by_tier_bidir, build_regression_dataframe
from surface_features import batch_extract_features
from regression import run_mediation_ols, MediationResult
from evaluate import evaluate_cross_model_gate, generate_gate_report, OverallGateResult
from visualize import generate_all_figures

def run_single_model(
    model_name: str,
    config: ExperimentConfig,
    tier_pairs: Dict,
) -> Tuple[MediationResult, pd.DataFrame]:
    """Run full pipeline for one SBERT model.

    Returns: (mediation_result, regression_df)
    regression_df cols: tier, pm_proxy, c_sem, response_length,
                        bullet_density, politeness_freq, ttr, mean_sent_len
    """
    ...

def save_results(
    all_mediation_results: Dict[str, MediationResult],
    overall_gate: OverallGateResult,
    results_dir: str,
) -> None:
    """Save regression_results.json with full schema (see below)."""
    ...

def main(config_path: Optional[str] = None) -> None:
    """Orchestrate full h-m4 pipeline."""
    ...
```

### Pseudo-code: main() + run_single_model()

```
# main()
config = load_config(config_path)
setup_logging(config.output_dir)
tier_pairs = split_by_tier_bidir(config.cache.cache_dir)   # chosen+rejected per tier

all_results = {}
all_dfs = {}
for model_name in config.cache.models:   # 3 SBERT models
    result, df = run_single_model(model_name, config, tier_pairs)
    all_results[model_name] = result
    all_dfs[model_name] = df

overall_gate = evaluate_cross_model_gate(all_results, models_required=config.stats.models_required)
logging.info(generate_gate_report(overall_gate))
generate_all_figures(all_results, all_dfs[config.cache.models[0]], config.figures.figures_dir)
save_results(all_results, overall_gate, config.results_dir)

# run_single_model()
embedder = Embedder(model_name=model_name, cache_dir=config.cache.embeddings_dir)

csem_arrays = compute_all_branch_csem(tier_pairs, embedder, seed=config.stats.seed)
# csem_arrays: {tier: {'chosen': [N,], 'rejected': [N,]}}

surf_feat_dfs = {}
for tier in TIER_ORDER:
    for branch in ['chosen', 'rejected']:
        texts = tier_pairs[tier][branch]['a_response']  # List[str]
        surf_feat_dfs[(tier, branch)] = batch_extract_features(texts)  # [N, 5]

df = build_regression_dataframe(tier_pairs, csem_arrays, surf_feat_dfs)
# df: [N_total, 8]; N_total ~28k-70k

mediation_result = run_mediation_ols(df, model_name=model_name, cov_type=config.regression.cov_type)
return mediation_result, df
```

### save_results() JSON Schema

```json
{
  "hypothesis": "h-m4",
  "date": "2026-03-15",
  "gate": {
    "overall_pass": true,
    "models_passed": 2,
    "models_required": 2,
    "interpretation": "..."
  },
  "models": {
    "all-MiniLM-L6-v2": {
      "gate_pass": true,
      "stage_pm_only": {
        "beta_pm": 0.012, "p_pm": 0.003,
        "beta_pm_ci": [0.005, 0.019], "r_squared": 0.042, "nobs": 28852
      },
      "stage_full": {
        "beta_pm": 0.010, "p_pm": 0.008,
        "beta_pm_ci": [0.003, 0.017], "r_squared": 0.061, "nobs": 28852,
        "all_params": {"const": 0.0, "pm_proxy": 0.0, "response_length": 0.0},
        "all_pvalues": {"pm_proxy": 0.0},
        "all_ci": {"pm_proxy": [0.0, 0.0]},
        "condition_number": 45.2
      },
      "stage_robustness": {
        "beta_tier_rank": 0.008, "p_tier_rank": 0.012, "r_squared": 0.055
      },
      "mediation": {
        "mediation_ratio": 0.167,
        "pm_effect_retained": 0.833
      },
      "vif": {
        "pm_proxy": 1.2, "response_length": 3.1, "bullet_density": 1.8,
        "politeness_freq": 1.5, "ttr": 2.9, "mean_sent_len": 2.4
      }
    }
  }
}
```

### Error Handling

```python
# Singularity check before OLS
if not check_rank_deficiency(df, ['pm_proxy'] + SURFACE_FEATURE_COLS):
    logging.error(f"[{model_name}] Rank deficiency — skipping model")
    raise RuntimeError(f"Matrix rank deficient for {model_name}")

# N_pairs < 1000 warning per tier×branch
for tier in TIER_ORDER:
    for branch in ['chosen', 'rejected']:
        n = len(tier_pairs[tier][branch]['h_next'])
        if n < config.stats.min_n_pairs:
            logging.warning(f"N_pairs={n} < {config.stats.min_n_pairs} for {tier}/{branch}")

# IPW trigger: KS test on chosen vs rejected C_sem distributions
from scipy.stats import ks_2samp
for tier in TIER_ORDER:
    stat, p = ks_2samp(csem_arrays[tier]['chosen'], csem_arrays[tier]['rejected'])
    if p < 0.05:
        logging.warning(f"IPW trigger: KS distribution shift in {tier}, p={p:.4f}")
        # Compute IPW weights and pass to build_regression_dataframe
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | main() | Pipeline loop over 3 SBERT models; gate eval; figure gen; save results |
| L-10-2 | run_single_model | embed H_next+A_response per branch → C_sem → surface features → df → OLS |
| L-10-3 | save_results JSON schema | regression_results.json with all coefficients, CIs, VIF, gate per model |
| L-10-4 | error handling | singularity check, N_pairs < 1000 warning, KS-triggered IPW condition |

---

## Key Constraints Summary

| Constraint | Implementation |
|------------|----------------|
| `rng.choice` | bootstrap_ci (inherited from h-m2/h-m3 fix — do not change to rng.integers) |
| HC3 SE | `sm.OLS(y, X).fit(cov_type='HC3')` — exact call |
| Tier dummies | `pd.get_dummies(df['tier'], prefix='tier', drop_first=True)` — T1=reference |
| knn_n_jobs=1 | Hardcoded in `build_topic_control` (controls.py:42) — do not override |
| Cache key prefix | `prefix='a_chosen'` vs `prefix='a_rejected'` in `encode_tier()` — prevents collision |
