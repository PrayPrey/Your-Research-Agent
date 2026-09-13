# Configuration: H-M4 PM-Score OLS Mediation Regression

**Hypothesis:** H-M4 — PM-proxy predicts C_sem^H←A above surface-feature controls
**Date:** 2026-03-15
**Gate:** SHOULD_WORK

Applied: N/A — Archon KB contains diffusion model content only (0 relevant results)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (extending h-m2)
**Status:** config classes verified from base code (direct file read of h-m2/code/config.py)
**Config Files Found:** `docs/youra_research/20260315_bi_align/h-m2/code/config.py`
**Pattern Used:** dataclass

---

## Inherited Configuration (Base Hypothesis)

Verified from `/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/h-m2/code/config.py`:

```python
# ACTUAL h-m2 field names and defaults (verified from real code):

@dataclass
class CacheConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m1/code/embeddings"  # h-m4 overrides to "../h-m2/code/embeddings"
    models: List[str] = field(default_factory=lambda: [...3 models...])
    tiers: List[str] = field(default_factory=lambda: [...3 tiers...])
    encode_batch_size: int = 256
    # h-m2 also has: h_m1_cache_key_templates, h_m2_cache_key_templates

@dataclass
class StatisticsConfig:
    seed: int = 42
    alpha: float = 0.05
    n_bootstrap: int = 1000        # field name is n_bootstrap (not bootstrap_resamples)
    knn_k: int = 5
    knn_n_jobs: int = 1            # CRITICAL: never -1 at 155k scale
    tiers_required: int = 2
    models_required: int = 2
    min_n_pairs: int = 1000
    cohen_d_threshold: float = 0.1

@dataclass
class FigureConfig:
    figures_dir: str = "../figures"
    dpi: int = 150
    save_format: str = "png"

@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m2"
    cache: CacheConfig = field(default_factory=CacheConfig)
    stats: StatisticsConfig = field(default_factory=StatisticsConfig)
    figures: FigureConfig = field(default_factory=FigureConfig)
    output_dir: str = "outputs"
    embedding_cache_dir: str = "../h-m1/code/embeddings"  # top-level in h-m2
    dry_run: bool = False
    n_samples_dry_run: int = 500
    # NOTE: h-m2 has NO RegressionConfig — h-m4 adds it
```

**Verified from:** actual h-m2/code/config.py implementation
**Key differences:** h-m2 has no `RegressionConfig`; h-m4 adds it. Field `embedding_cache_dir` is top-level in h-m2; h-m4 uses `cache.embeddings_dir` pointing to h-m2 embeddings.

---

## Module-Level Constants

```python
# config.py top-level constants for h-m4

POLITENESS_TOKENS = frozenset({
    'please', 'thank', 'sorry', 'appreciate', 'certainly', 'happy'
})

SURFACE_FEATURE_COLS = [
    'response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len'
]

TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]

MODEL_NAMES = ["all-MiniLM-L6-v2", "paraphrase-MiniLM-L6-v2", "all-mpnet-base-v2"]

BRANCH_LABELS = ("chosen", "rejected")

PM_PROXY_MAP = {"chosen": 1, "rejected": 0}
```

---

## A-3: data_loader config [Complexity: 13, Budget: 2 subtasks]

```python
@dataclass
class CacheConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m2/code/embeddings"  # reuse h-m2 embeddings cache
    models: List[str] = field(default_factory=lambda: MODEL_NAMES)
    tiers: List[str] = field(default_factory=lambda: TIER_ORDER)
    encode_batch_size: int = 256
    # h-m4 new: distinct cache key prefixes for chosen/rejected branches
    chosen_cache_prefix: str = "a_chosen"    # e.g. a_chosen_minilm_base_14426.npy
    rejected_cache_prefix: str = "a_rejected"
```

Parsing schema constants (used in `extract_chosen_rejected_pairs` and `split_by_tier_bidir`):

```python
# Binary PM-proxy mapping — chosen branch = higher PM-score
PM_PROXY_MAP = {"chosen": 1, "rejected": 0}

BRANCH_LABELS = ("chosen", "rejected")

MIN_N_PAIRS: int = 1000  # inherited from StatisticsConfig.min_n_pairs

# DataFrame column schema for build_regression_dataframe output:
# conversation_id: str — unique per conversation
# branch: str — 'chosen' | 'rejected'
# pm_proxy: int — 0 | 1
# tier: str — from TIER_ORDER
# c_sem: float
# response_length, bullet_density, politeness_freq, ttr, mean_sent_len: float
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | chosen/rejected parsing config | `BRANCH_LABELS`, `PM_PROXY_MAP`, `min_n_pairs=1000`, `TIER_ORDER`, `chosen_cache_prefix` / `rejected_cache_prefix` |
| C-3-2 | PM-proxy construction schema | DataFrame column names/types: `conversation_id`, `branch`, `pm_proxy`, plus join with `c_sem` and surface features |

---

## A-4: surface features config [Complexity: 10, Budget: 1 subtask]

```python
# Module-level constants — imported by surface_features.py from config.py

POLITENESS_TOKENS = frozenset({
    'please', 'thank', 'sorry', 'appreciate', 'certainly', 'happy'
})

SURFACE_FEATURE_COLS = [
    'response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len'
]

# Validation thresholds for validate_features()
FEATURE_VALIDATION_THRESHOLDS = {
    'response_length': {'min': 0,   'max': 10000},
    'bullet_density':  {'min': 0.0, 'max': 1.0},    # max_bullet_density=1.0
    'politeness_freq': {'min': 0.0, 'max': 1.0},
    'ttr':             {'min': 0.0, 'max': 1.0},
    'mean_sent_len':   {'min': 0.0, 'max': 500.0},
}

MIN_WORD_COUNT: int = 1   # drop responses with 0 words
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | surface feature extraction config | `POLITENESS_TOKENS` frozenset, `SURFACE_FEATURE_COLS` list, `FEATURE_VALIDATION_THRESHOLDS` dict with `max_bullet_density=1.0`, `min_word_count=1` |

---

## A-8: visualization config [Complexity: 11, Budget: 2 subtasks]

```python
@dataclass
class FigureConfig:
    figures_dir: str = "../figures"
    dpi: int = 150
    save_format: str = "png"
    tier_palette: dict = field(default_factory=lambda: {
        "helpful-base": "#4C72B0",
        "helpful-rejection-sampled": "#DD8452",
        "helpful-online": "#55A868",
    })
    branch_palette: dict = field(default_factory=lambda: {
        "chosen": "#2196F3",
        "rejected": "#F44336",
    })

# Regression plot specs (used across all 6 figure generators)
REGRESSION_PLOT_CONFIG = {
    "ci_level": 0.95,
    "reference_line_y": 0.0,           # horizontal zero line on forest/beta plots
    "reference_line_style": "--",
    "reference_line_color": "gray",
    "axis_label_beta_pm": r"$\hat{\beta}_{PM}$",
    "axis_label_csem": r"$C_{sem}^{H \leftarrow A}$",
    "axis_label_pm_proxy": "PM Proxy (1=chosen, 0=rejected)",
    "axis_label_model": "SBERT Model",
    "figsize_default": (8, 5),
    "figsize_forest": (10, 7),
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | FigureConfig | `figures_dir`, `dpi=150`, `save_format='png'`, `tier_palette`, `branch_palette` for chosen/rejected |
| C-8-2 | REGRESSION_PLOT_CONFIG | `ci_level=0.95`, `reference_line_y=0.0`, axis label templates for all 6 figures |

---

## A-12: integration + checkpoint config [Complexity: 11, Budget: 2 subtasks]

```python
@dataclass
class RegressionConfig:
    cov_type: str = 'HC3'                  # HC3 heteroscedasticity-robust SE (White correction)
    tier_reference: str = 'helpful-base'   # T1 = reference dummy (drop_first=True)
    min_nobs: int = 1000
    vif_warn_threshold: float = 10.0       # log warning if any VIF exceeds this

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
    ipw_ks_threshold: float = 0.05    # trigger IPW if KS-test p < threshold
    singularity_warn: bool = True     # log statsmodels rank deficiency warnings
```

Checkpoint schema for `h-m4/04_checkpoint.yaml`:

```yaml
# 04_checkpoint.yaml — h-m4 Phase 4 task tracking
hypothesis_id: h-m4
status: in_progress          # in_progress | done | failed
timestamp: ""
dry_run: false

models_completed: []         # populated as each SBERT model finishes
models_pending:
  - all-MiniLM-L6-v2
  - paraphrase-MiniLM-L6-v2
  - all-mpnet-base-v2

gate_result: null            # true | false | null (filled after A-12)
models_passed: null          # int: count of models with gate_pass=True

tasks:
  A-1:  {status: todo, subtasks_total: 7,  subtasks_done: 0}
  A-2:  {status: todo, subtasks_total: 8,  subtasks_done: 0}
  A-3:  {status: todo, subtasks_total: 13, subtasks_done: 0}
  A-4:  {status: todo, subtasks_total: 10, subtasks_done: 0}
  A-5:  {status: todo, subtasks_total: 14, subtasks_done: 0}
  A-6:  {status: todo, subtasks_total: 15, subtasks_done: 0}
  A-7:  {status: todo, subtasks_total: 10, subtasks_done: 0}
  A-8:  {status: todo, subtasks_total: 11, subtasks_done: 0}
  A-9:  {status: todo, subtasks_total: 9,  subtasks_done: 0}
  A-10: {status: todo, subtasks_total: 15, subtasks_done: 0}
  A-11: {status: todo, subtasks_total: 9,  subtasks_done: 0}
  A-12: {status: todo, subtasks_total: 11, subtasks_done: 0}

error_log: []
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-12-1 | pipeline config | `dry_run=False`, `n_samples_dry_run=500`, `ipw_ks_threshold=0.05`, `singularity_warn=True` |
| C-12-2 | 04_checkpoint.yaml schema | YAML structure with models_completed/pending, gate_result, task status tracking for all 12 epics |

---

## Complete ExperimentConfig (h-m4/code/config.py — copy-paste ready)

```python
import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional

# Module-level constants
POLITENESS_TOKENS: FrozenSet[str] = frozenset({
    'please', 'thank', 'sorry', 'appreciate', 'certainly', 'happy'
})
SURFACE_FEATURE_COLS: List[str] = [
    'response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len'
]
TIER_ORDER: List[str] = [
    "helpful-base", "helpful-rejection-sampled", "helpful-online"
]
MODEL_NAMES: List[str] = [
    "all-MiniLM-L6-v2", "paraphrase-MiniLM-L6-v2", "all-mpnet-base-v2"
]
BRANCH_LABELS = ("chosen", "rejected")
PM_PROXY_MAP: Dict[str, int] = {"chosen": 1, "rejected": 0}
FEATURE_VALIDATION_THRESHOLDS: Dict[str, Dict] = {
    'response_length': {'min': 0,   'max': 10000},
    'bullet_density':  {'min': 0.0, 'max': 1.0},
    'politeness_freq': {'min': 0.0, 'max': 1.0},
    'ttr':             {'min': 0.0, 'max': 1.0},
    'mean_sent_len':   {'min': 0.0, 'max': 500.0},
}
REGRESSION_PLOT_CONFIG: Dict = {
    "ci_level": 0.95,
    "reference_line_y": 0.0,
    "reference_line_style": "--",
    "reference_line_color": "gray",
    "axis_label_beta_pm": r"$\hat{\beta}_{PM}$",
    "axis_label_csem": r"$C_{sem}^{H \leftarrow A}$",
    "axis_label_pm_proxy": "PM Proxy (1=chosen, 0=rejected)",
    "axis_label_model": "SBERT Model",
    "figsize_default": (8, 5),
    "figsize_forest": (10, 7),
}


@dataclass
class CacheConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m2/code/embeddings"
    models: List[str] = field(default_factory=lambda: MODEL_NAMES)
    tiers: List[str] = field(default_factory=lambda: TIER_ORDER)
    encode_batch_size: int = 256
    chosen_cache_prefix: str = "a_chosen"
    rejected_cache_prefix: str = "a_rejected"


@dataclass
class StatisticsConfig:
    seed: int = 42
    alpha: float = 0.05
    n_bootstrap: int = 1000        # field name matches h-m2 (n_bootstrap, not bootstrap_resamples)
    knn_k: int = 5
    knn_n_jobs: int = 1            # CRITICAL: never -1 at 155k scale (verified h-m2)
    models_required: int = 2       # >=2/3 for gate
    min_n_pairs: int = 1000


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
    tier_palette: Dict[str, str] = field(default_factory=lambda: {
        "helpful-base": "#4C72B0",
        "helpful-rejection-sampled": "#DD8452",
        "helpful-online": "#55A868",
    })
    branch_palette: Dict[str, str] = field(default_factory=lambda: {
        "chosen": "#2196F3",
        "rejected": "#F44336",
    })


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
    ipw_ks_threshold: float = 0.05
    singularity_warn: bool = True

    @property
    def cache_dir(self) -> str:
        return self.cache.cache_dir

    @property
    def figures_dir(self) -> str:
        return self.figures.figures_dir


def load_config(yaml_path: Optional[str] = None) -> ExperimentConfig:
    """Load ExperimentConfig from YAML with defaults.
    Follows same pattern as h-m2 load_config (verified).
    """
    config = ExperimentConfig()
    if yaml_path is None:
        return config
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return config
    for key in ("hypothesis_id", "output_dir", "results_dir", "dry_run",
                "n_samples_dry_run", "ipw_ks_threshold", "singularity_warn"):
        if key in data:
            setattr(config, key, data[key])
    for sub, obj in [("cache", config.cache), ("stats", config.stats),
                     ("regression", config.regression), ("figures", config.figures)]:
        if sub in data:
            for k, v in data[sub].items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
    return config
```

---

## Hyperparameter Summary

| Parameter | Value | Source |
|-----------|-------|--------|
| `seed` | 42 | h-m2 `StatisticsConfig.seed` (verified) |
| `n_bootstrap` | 1000 | h-m2 `StatisticsConfig.n_bootstrap` (verified) |
| `knn_k` | 5 | h-m2 `StatisticsConfig.knn_k` (verified) |
| `knn_n_jobs` | 1 | h-m2 `StatisticsConfig.knn_n_jobs` (verified, CRITICAL) |
| `alpha` | 0.05 | h-m2 `StatisticsConfig.alpha` (verified) |
| `min_n_pairs` | 1000 | h-m2 `StatisticsConfig.min_n_pairs` (verified) |
| `models_required` | 2 | h-m2 `StatisticsConfig.models_required` (verified) |
| `encode_batch_size` | 256 | h-m2 `CacheConfig.encode_batch_size` (verified) |
| `cov_type` | 'HC3' | h-m4 new — `RegressionConfig` |
| `tier_reference` | 'helpful-base' | h-m4 new — `RegressionConfig` |
| `vif_warn_threshold` | 10.0 | h-m4 new — `RegressionConfig` |
| `ipw_ks_threshold` | 0.05 | h-m4 new — `ExperimentConfig` |
