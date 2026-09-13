# Architecture: H-M4 PM-Score OLS Mediation Regression

**Hypothesis:** H-M4 — PM-proxy predicts C_sem^H←A above surface-feature controls
**Type:** MECHANISM | **Gate:** SHOULD_WORK
**Base:** h-m1/h-m2 codebase (INCREMENTAL)
**Date:** 2026-03-15

Applied: N/A — no relevant patterns found in Archon KB (diffusion model content only)

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase (base hypothesis h-m1, evolved through h-m2, h-m3)
**Status:** patterns found from base code (direct file reads — Serena project activation unavailable, files read directly)
**Analyzed Path:** `docs/youra_research/20260315_bi_align/h-m2/code/`

**Findings:**
- h-m2 is the most evolved base: adds `config.py` (dataclass config), bidirectional C_sem in `accommodation.py`, `conftest.py`
- h-m3 adds `delta_probe.py` and `statistics_m3.py` as hypothesis-specific modules (pattern for h-m4 new modules)
- Key reuse: `Embedder` (embedder.py), `split_by_tier` + `extract_pairs` (data_loader.py), `compute_bidirectional_csem_per_tier` (accommodation.py), `ExperimentConfig` (config.py)
- `extract_pairs()` operates on `chosen` branch only — h-m4 needs extension for `rejected` branch
- bootstrap in `statistics.py` uses `rng.choice` (h-m3 critical fix already in place)
- Cache key format: `{prefix}_{model_slug}_{tier_slug}_{n_pairs}.npy` — h-m4 chosen/rejected branches need distinct cache keys

---

## File Organization

```
h-m4/code/
├── config.py              # ExperimentConfig (extends h-m2 pattern)
├── data_loader.py         # Extends h-m2 data_loader: chosen+rejected branch parsing
├── surface_features.py    # NEW: 5 surface-feature extractors
├── regression.py          # NEW: 4-stage OLS mediation pipeline
├── evaluate.py            # NEW: gate check + mechanism activation verification
├── visualize.py           # NEW: 6 figures
├── run_experiment.py      # NEW: main orchestrator
└── tests/
    ├── test_data_loader.py
    ├── test_surface_features.py
    ├── test_regression.py
    └── test_evaluate.py
```

**Reused from h-m2/code/ (import directly):**
- `embedder.py` → `Embedder`
- `controls.py` → `random_shuffle_control`, `topic_matched_control`
- `statistics.py` → `bootstrap_ci`
- `accommodation.py` → `compute_h_given_a_csem_array`

---

## Module Definitions

### config.py (`h-m4/code/config.py`)

**Dependencies:** dataclasses, yaml

```python
from dataclasses import dataclass, field
from typing import List, Optional

POLITENESS_TOKENS = frozenset({'please', 'thank', 'sorry', 'appreciate', 'certainly', 'happy'})
SURFACE_FEATURE_COLS = ['response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len']
TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
MODEL_NAMES = ["all-MiniLM-L6-v2", "paraphrase-MiniLM-L6-v2", "all-mpnet-base-v2"]

@dataclass
class CacheConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m2/code/embeddings"
    models: List[str] = field(default_factory=lambda: MODEL_NAMES)
    tiers: List[str] = field(default_factory=lambda: TIER_ORDER)
    encode_batch_size: int = 256

@dataclass
class StatisticsConfig:
    seed: int = 42
    alpha: float = 0.05
    n_bootstrap: int = 1000
    knn_k: int = 5
    knn_n_jobs: int = 1
    min_n_pairs: int = 1000
    models_required: int = 2  # >=2/3 for gate

@dataclass
class RegressionConfig:
    cov_type: str = 'HC3'
    tier_reference: str = 'helpful-base'
    min_nobs: int = 1000
    vif_warn_threshold: float = 10.0

@dataclass
class FigureConfig:
    figures_dir: str = "../figures"
    dpi: int = 150
    save_format: str = "png"

@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m4"
    cache: CacheConfig = field(default_factory=CacheConfig)
    stats: StatisticsConfig = field(default_factory=StatisticsConfig)
    regression: RegressionConfig = field(default_factory=RegressionConfig)
    figures: FigureConfig = field(default_factory=FigureConfig)
    output_dir: str = "outputs"
    results_dir: str = "../results"
    dry_run: bool = False
    n_samples_dry_run: int = 500

def load_config(yaml_path: Optional[str] = None) -> ExperimentConfig: ...
```

---

### data_loader.py (`h-m4/code/data_loader.py`)

**Dependencies:** h-m2/code/data_loader.py (extended), datasets

```python
from typing import Dict, List, Tuple
import pandas as pd

# Re-exports from h-m2 (import at top of file)
# from sys; sys.path.insert(0, "../h-m2/code")
# from data_loader import (parse_conversation, compute_jaccard, compute_token_count,
#                          TIER_ORDER, MIN_N_PAIRS_PER_TIER)

def extract_chosen_rejected_pairs(records: List[dict]) -> Dict:
    """Parse HH-RLHF records extracting BOTH chosen and rejected branches.

    Returns dict with keys:
      conversation_id, branch (chosen|rejected), pm_proxy (1|0),
      h_next, a_response, h_prompt, token_counts, jaccard_overlaps
    Each chosen/rejected pair shares same conversation_id.
    """
    ...

def split_by_tier_bidir(cache_dir: str) -> Dict[str, Dict]:
    """Load each RLHF tier, extract chosen+rejected branches per conversation.

    Returns:
        Dict mapping tier_name -> {
            conversation_id: List[str],
            branch: List[str],          # 'chosen' | 'rejected'
            pm_proxy: List[int],        # 1 | 0
            h_next: List[str],
            a_response: List[str],      # AI response text (for surface features)
            h_prompt: List[str],
            token_counts: List[int],
            jaccard_overlaps: List[float],
        }
    """
    ...

def build_regression_dataframe(
    tier_pairs: Dict[str, Dict],
    csem_arrays: Dict[str, Dict[str, float]],
    surface_feat_arrays: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Join C_sem values + pm_proxy + surface features into regression DataFrame.

    Columns: tier, pm_proxy, c_sem, response_length, bullet_density,
             politeness_freq, ttr, mean_sent_len
    """
    ...
```

---

### surface_features.py (`h-m4/code/surface_features.py`)

**Dependencies:** pandas, numpy, re

```python
import pandas as pd
import numpy as np
from typing import List, Dict
from config import POLITENESS_TOKENS

def extract_response_length(text: str) -> int:
    """Count whitespace-split words."""
    ...

def extract_bullet_density(text: str) -> float:
    """Fraction of lines starting with '-', '*', or '•'."""
    ...

def extract_politeness_freq(text: str) -> float:
    """Fraction of words in POLITENESS_TOKENS set (lowercase match)."""
    ...

def extract_ttr(text: str) -> float:
    """Type-token ratio: len(unique_words) / max(word_count, 1)."""
    ...

def extract_mean_sent_len(text: str) -> float:
    """word_count / max(sentence_count, 1); sentences split on '.'."""
    ...

def extract_all_features(text: str) -> Dict[str, float]:
    """Extract all 5 features for a single response text.

    Returns:
        {'response_length': int, 'bullet_density': float,
         'politeness_freq': float, 'ttr': float, 'mean_sent_len': float}
    """
    ...

def batch_extract_features(texts: List[str]) -> pd.DataFrame:
    """Batch extract all 5 surface features from list of response texts.

    Returns:
        DataFrame with columns: response_length, bullet_density,
        politeness_freq, ttr, mean_sent_len
    """
    ...

def validate_features(df: pd.DataFrame) -> Dict[str, bool]:
    """Check for NaN, zero-length, out-of-range values. Returns validation dict."""
    ...
```

---

### regression.py (`h-m4/code/regression.py`)

**Dependencies:** statsmodels, pandas, numpy, config

```python
import statsmodels.api as sm
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class OLSStageResult:
    model_name: str       # SBERT model slug
    stage: str            # 'pm_only' | 'full' | 'robustness' | 'mediation'
    beta_pm: float
    p_pm: float
    beta_pm_ci: Tuple[float, float]
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
    mediation_ratio: float          # (beta_pm_reduced - beta_pm_full) / beta_pm_reduced
    pm_effect_retained: float       # |beta_pm_full / beta_pm_reduced|
    stage_pm_only: OLSStageResult
    stage_full: OLSStageResult
    stage_robustness: OLSStageResult

def run_pm_only_model(df: pd.DataFrame, cov_type: str = 'HC3') -> OLSStageResult:
    """Stage 1: C_sem ~ beta_0 + beta_PM*pm_proxy + beta_T2*tier_T2 + beta_T3*tier_T3."""
    ...

def run_full_model(df: pd.DataFrame, cov_type: str = 'HC3') -> OLSStageResult:
    """Stage 2: C_sem ~ pm_proxy + 5 surface features + tier dummies (HC3 SE)."""
    ...

def run_robustness_model(df: pd.DataFrame, cov_type: str = 'HC3') -> OLSStageResult:
    """Stage 3: Replace pm_proxy with tier_rank (ordinal 1/2/3)."""
    ...

def compute_mediation_proportion(
    beta_pm_reduced: float,
    beta_pm_full: float,
) -> Tuple[float, float]:
    """Stage 4: Returns (mediation_ratio, pm_effect_retained)."""
    ...

def run_mediation_ols(
    df: pd.DataFrame,
    model_name: str,
    cov_type: str = 'HC3',
) -> MediationResult:
    """Run all 4 stages for one SBERT model's regression DataFrame."""
    ...

def check_rank_deficiency(df: pd.DataFrame, feature_cols: List[str]) -> bool:
    """Check for matrix rank deficiency before OLS fit. Returns True if OK."""
    ...

def compute_vif(df: pd.DataFrame, feature_cols: List[str]) -> Dict[str, float]:
    """Compute Variance Inflation Factors for multicollinearity diagnostics."""
    ...
```

---

### evaluate.py (`h-m4/code/evaluate.py`)

**Dependencies:** regression.py, config

```python
from typing import Dict, List, Tuple
from regression import MediationResult, OLSStageResult

@dataclass
class GateResult:
    model_name: str
    gate_pass: bool
    beta_pm_positive: bool
    p_significant: bool
    beta_pm_value: float
    p_value: float
    secondary_check_pass: bool   # |beta_pm_full / beta_pm_reduced| > 0.5

@dataclass
class OverallGateResult:
    overall_pass: bool
    models_passed: int           # count of models with gate_pass=True
    models_required: int         # threshold (2)
    gate_results: Dict[str, GateResult]
    interpretation: str

def verify_mechanism_activated(
    model_result,
    beta_pm: float,
    p_pm: float,
    surface_cols: List[str],
) -> Tuple[bool, Dict[str, bool]]:
    """Check 5 activation indicators: model_fitted, beta_pm_nonzero,
    p_value_valid, n_obs_sufficient, surface_controls_included."""
    ...

def check_gate(
    beta_pm: float,
    p_pm: float,
    beta_pm_reduced: float,
    significance_level: float = 0.05,
) -> GateResult: ...

def evaluate_cross_model_gate(
    mediation_results: Dict[str, MediationResult],
    models_required: int = 2,
) -> OverallGateResult:
    """Evaluate >=2/3 gate criterion across all SBERT models."""
    ...

def generate_gate_report(overall_result: OverallGateResult) -> str:
    """Generate human-readable gate summary string for 04_validation.md."""
    ...
```

---

### visualize.py (`h-m4/code/visualize.py`)

**Dependencies:** matplotlib, seaborn, pandas, regression.py, evaluate.py

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict
from regression import MediationResult
from evaluate import OverallGateResult

def plot_beta_pm_comparison(
    mediation_results: Dict[str, MediationResult],
    figures_dir: str,
) -> str:
    """Fig 1: beta_PM (full model) with 95% CI across 3 SBERT models (bar + error bars)."""
    ...

def plot_mediation_decomposition(
    mediation_results: Dict[str, MediationResult],
    figures_dir: str,
) -> str:
    """Fig 2: beta_PM_reduced vs beta_PM_full per model (grouped bar)."""
    ...

def plot_coefficient_forest(
    mediation_results: Dict[str, MediationResult],
    figures_dir: str,
) -> str:
    """Fig 3: All OLS coefficients with 95% CI per model (forest plot)."""
    ...

def plot_csem_vs_pm_scatter(
    df: pd.DataFrame,
    figures_dir: str,
) -> str:
    """Fig 4: C_sem vs PM_proxy per tier with regression line overlay."""
    ...

def plot_partial_regression(
    df: pd.DataFrame,
    mediation_results: Dict[str, MediationResult],
    figures_dir: str,
) -> str:
    """Fig 5: C_sem residuals vs PM_proxy residuals (partial regression)."""
    ...

def plot_tier_pm_interaction(
    df: pd.DataFrame,
    figures_dir: str,
) -> str:
    """Fig 6: C_sem by tier × branch (chosen/rejected) grouped bar chart."""
    ...

def generate_all_figures(
    mediation_results: Dict[str, MediationResult],
    df: pd.DataFrame,
    figures_dir: str,
) -> Dict[str, str]:
    """Run all 6 figure generators. Returns dict of {fig_name: saved_path}."""
    ...
```

---

### run_experiment.py (`h-m4/code/run_experiment.py`)

**Dependencies:** all h-m4 modules, h-m2 modules (Embedder, controls, accommodation, statistics)

```python
import sys
import json
import logging
from pathlib import Path
from typing import Dict
import pandas as pd

# Reused from h-m2
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m2" / "code"))
from embedder import Embedder
from controls import random_shuffle_control, topic_matched_control
from accommodation import compute_h_given_a_csem_array

# h-m4 modules
from config import ExperimentConfig, load_config
from data_loader import split_by_tier_bidir, build_regression_dataframe
from surface_features import batch_extract_features
from regression import run_mediation_ols
from evaluate import evaluate_cross_model_gate, generate_gate_report
from visualize import generate_all_figures

def setup_logging(output_dir: str) -> None: ...

def run_single_model(
    model_name: str,
    config: ExperimentConfig,
    tier_pairs: Dict,
) -> tuple:
    """Run full pipeline for one SBERT model.

    Returns: (mediation_result, regression_df)
    """
    ...

def save_results(
    all_mediation_results: Dict,
    overall_gate: object,
    results_dir: str,
) -> None:
    """Save regression_results.json with all coefficients + gate evaluation."""
    ...

def main(config_path: str = None) -> None:
    """Orchestrate full h-m4 pipeline:
    1. Load config
    2. Load chosen/rejected tier data
    3. For each SBERT model:
       a. Encode H_next, A_response per (conversation, branch)
       b. Compute C_sem^H<-A per row
       c. Extract surface features from A_response texts
       d. Build regression DataFrame
       e. Run 4-stage OLS mediation
    4. Evaluate cross-model gate (>=2/3)
    5. Generate 6 figures
    6. Save results JSON + 04_validation.md
    """
    ...

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="H-M4: PM-Score OLS Mediation Regression")
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(config_path=args.config)
```

---

## External Dependencies (Base Hypothesis)

**Verified from:** `docs/youra_research/20260315_bi_align/h-m2/code/` (actual implementation)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Embedder | `from embedder import Embedder` (via sys.path insert) | `h-m2/code/embedder.py` |
| random_shuffle_control | `from controls import random_shuffle_control` | `h-m2/code/controls.py` |
| topic_matched_control | `from controls import topic_matched_control` | `h-m2/code/controls.py` |
| compute_h_given_a_csem_array | `from accommodation import compute_h_given_a_csem_array` | `h-m2/code/accommodation.py` |
| bootstrap_ci | `from statistics import bootstrap_ci` | `h-m2/code/statistics.py` |
| parse_conversation | `from data_loader import parse_conversation` | `h-m2/code/data_loader.py` |
| compute_token_count | `from data_loader import compute_token_count` | `h-m2/code/data_loader.py` |
| compute_jaccard | `from data_loader import compute_jaccard` | `h-m2/code/data_loader.py` |

**sys.path insert pattern** (verified from h-m2/h-m3 structure):
```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m2" / "code"))
```

**Critical notes from base code:**
- `Embedder.encode_tier()` cache key: `{prefix}_{model_slug}_{tier_slug}_{n_pairs}` — h-m4 must use distinct prefix for chosen/rejected branches (e.g., `a_chosen_`, `a_rejected_`)
- `extract_pairs()` in h-m2 data_loader only processes `chosen` branch — h-m4 data_loader extends to `rejected`
- bootstrap must use `rng.choice` not `rng.integers` (h-m3 critical fix)
- `knn_n_jobs=1` is mandatory (verified in config.py StatisticsConfig)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment + Data Setup | Copy/link h-m2 code; create h-m4 directory structure; verify data cache; validate N_pairs ≥ 1000 | 7 | 2+1+1+3 |
| A-2 | config.py | ExperimentConfig + RegressionConfig dataclasses; load_config YAML loader; path resolution for h-m2 embeddings cache | 8 | 2+2+2+2 |
| A-3 | data_loader.py (chosen/rejected extension) | extract_chosen_rejected_pairs(); split_by_tier_bidir(); build_regression_dataframe() join logic; conversation_id tracking | 13 | 3+3+4+3 |
| A-4 | surface_features.py | 5 feature extractors + batch_extract_features() + validate_features(); edge case handling (empty text, single word, no bullets) | 10 | 3+1+4+2 |
| A-5 | C_sem computation per branch | Encode H_next + A_response for chosen/rejected per tier using Embedder; compute per-row C_sem^H<-A using h-m2 compute_h_given_a_csem_array; distinct cache keys for branches | 14 | 3+4+4+3 |
| A-6 | regression.py | 4-stage OLS protocol; OLSStageResult + MediationResult dataclasses; HC3 robust SE; rank deficiency check; VIF computation; mediation proportion | 15 | 4+3+5+3 |
| A-7 | evaluate.py | verify_mechanism_activated() 5 indicators; check_gate(); evaluate_cross_model_gate() >=2/3 criterion; generate_gate_report() | 10 | 2+2+3+3 |
| A-8 | visualize.py (mandatory figures) | Fig 1 (beta_PM bar+CI), Fig 2 (mediation decomposition), Fig 3 (forest plot); save to figures/ | 11 | 3+2+3+3 |
| A-9 | visualize.py (autonomous figures) | Fig 4 (scatter C_sem vs PM per tier), Fig 5 (partial regression), Fig 6 (tier×PM interaction grouped bar) | 9 | 2+2+3+2 |
| A-10 | run_experiment.py orchestrator | Full pipeline: data load → encode → C_sem per branch → surface features → regression DataFrame → OLS → gate → figures → results JSON | 15 | 3+4+4+4 |
| A-11 | Results + Validation reporting | Save regression_results.json (all coefficients, p-values, gate per model); generate 04_validation.md with gate result + key findings | 9 | 2+2+2+3 |
| A-12 | Integration + failsafe testing | End-to-end run all 3 SBERT models; singularity/convergence error handling; IPW trigger check; checkpoint 04_checkpoint.yaml | 11 | 2+3+3+3 |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [A-5, A-6, A-10]
- Medium (9-13): [A-3, A-4, A-7, A-8, A-9, A-11, A-12]
- Low (4-8): [A-1, A-2]

**Total Epic Tasks:** 12
