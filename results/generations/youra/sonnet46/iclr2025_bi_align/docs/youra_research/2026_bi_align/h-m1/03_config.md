# Configuration Design: h-m1

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: Config classes verified from base code via direct file reads
**Config Files Found**: `h-e1/code/run_experiment.py`, `h-e1/code/embedder.py`, `h-e1/code/data_loader.py`
**Pattern Used**: dataclass (matching h-e1 `ExperimentResults` dataclass pattern)

---

## Inherited Configuration

### Config Classes (From Actual h-e1 Code)

```python
# From: h-e1/code/run_experiment.py (ACTUAL CODE — verified)
# h-e1 uses config dict pattern (not dataclass for input config):
config = {
    "cache_dir": str,       # required
    "model_name": str,      # default: "all-MiniLM-L6-v2"
    "output_dir": str,      # default: "outputs"
    "n_samples": int | None # default: None (use all)
}

# From: h-e1/code/embedder.py (ACTUAL CODE — verified)
# Embedder.__init__(model_name="all-MiniLM-L6-v2", cache_dir="embeddings")
# encode() uses batch_size=256, normalize_embeddings=True (hardcoded)

# From: h-e1/code/data_loader.py (ACTUAL CODE — verified)
# SPLITS = [("helpful-base","train"), ("helpful-rejection-sampled","train"), ("helpful-online","train")]
# extract_pairs() asserts len(h_nexts) >= 1000
# Cache key suffix pattern: f"{prefix}_{model_slug}_{n_pairs}"

# From: h-e1/code/run_experiment.py controls usage:
# build_topic_control(h_prompt_emb, a_actual_emb, k=5)  — knn_k=5 confirmed
# build_random_control(a_actual_emb, seed=42)            — shuffle_seed=42 confirmed
# bootstrap n=1000, seed=42 (confirmed in statistics calls)
```

**Verified from**: `h-e1/code/` actual implementation (not specs)

---

## New Configuration for h-m1

### ExperimentConfig dataclass

```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ExperimentConfig:
    # Paths
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    embeddings_dir: str = "embeddings"

    # Execution
    dry_run: bool = False
    dry_run_n_per_tier: int = 500          # 500 per tier = 1500 total for dry run
    seed: int = 42

    # Sub-configs (use default_factory)
    data: "DataConfig" = field(default_factory=lambda: DataConfig())
    stats: "StatisticsConfig" = field(default_factory=lambda: StatisticsConfig())
    viz: "VisualizationConfig" = field(default_factory=lambda: VisualizationConfig())
```

### DataConfig

```python
@dataclass
class DataConfig:
    tier_names: List[str] = field(default_factory=lambda: [
        "helpful-base",
        "helpful-rejection-sampled",
        "helpful-online",
    ])
    tier_ranks: Dict[str, int] = field(default_factory=lambda: {
        "helpful-base": 1,
        "helpful-rejection-sampled": 2,
        "helpful-online": 3,
    })
    models: List[str] = field(default_factory=lambda: [
        "all-MiniLM-L6-v2",
        "paraphrase-MiniLM-L6-v2",
        "all-mpnet-base-v2",
    ])
    primary_model: str = "all-MiniLM-L6-v2"
    batch_size: int = 256                  # verified from h-e1 embedder.py
    knn_k: int = 5                         # verified from h-e1 run_experiment.py
    knn_n_jobs: int = 1                    # CRITICAL: never -1 (OpenBLAS double-free)
    min_n_pairs_per_tier: int = 1000       # verified from h-e1 data_loader.py assert
    verification_mode: str = "no_checks"   # HuggingFace NonMatchingSplitsSizesError fix
    openblas_num_threads: int = 4
    shuffle_seed: int = 42
```

### StatisticsConfig

```python
@dataclass
class StatisticsConfig:
    bootstrap_n: int = 1000
    bootstrap_seed: int = 42
    significance_level: float = 0.05
    bonferroni_n_tests: int = 3            # 3 pairwise comparisons: (T1,T2),(T2,T3),(T1,T3)
    bonferroni_alpha: float = 0.05 / 3     # = 0.0167
    cohen_d_threshold: float = 0.1
    jt_p_threshold: float = 0.05
    ks_p_threshold: float = 0.05           # trigger IPW if any KS p < this
    model_consistency_threshold: int = 2   # >=2/3 models must pass gate
```

### VisualizationConfig

```python
@dataclass
class VisualizationConfig:
    figure_dpi: int = 150
    figure_size_bar: tuple = (12, 5)       # (width, height) for tier_csem_bars (3 subplots)
    figure_size_line: tuple = (8, 5)       # tier_monotonicity_lines
    figure_size_heatmap: tuple = (8, 6)    # cohend_heatmap
    figure_size_violin: tuple = (10, 6)    # tier_violin
    figure_size_kde: tuple = (10, 5)       # bootstrap_kde_tiers
    figure_size_ipw: tuple = (8, 5)        # ipw_comparison (conditional)
    figure_size_ks: tuple = (8, 5)         # ks_summary

    # Tier color palette (T1=blue-gray, T2=orange, T3=green — low-to-high quality)
    tier_colors: Dict[str, str] = field(default_factory=lambda: {
        "helpful-base": "#6baed6",
        "helpful-rejection-sampled": "#fd8d3c",
        "helpful-online": "#74c476",
    })
    tier_labels: Dict[str, str] = field(default_factory=lambda: {
        "helpful-base": "T1: helpful-base",
        "helpful-rejection-sampled": "T2: helpful-rejection-sampled",
        "helpful-online": "T3: helpful-online",
    })
    font_size_title: int = 13
    font_size_label: int = 11
    font_size_tick: int = 9
    font_size_annotation: int = 9

    # Output path convention: figures/{plot_type}_{model_slug}.png
    # model_slug: minilm | paraphrase | mpnet
    output_path_template: str = "figures/{plot_type}_{model_slug}.png"
    # Multi-model plots (no model suffix):
    output_paths: Dict[str, str] = field(default_factory=lambda: {
        "tier_csem_bars": "figures/tier_csem_bars_{model_slug}.png",
        "tier_monotonicity_lines": "figures/tier_monotonicity_lines.png",
        "cohend_heatmap": "figures/cohend_heatmap.png",
        "tier_violin": "figures/tier_violin_{model_slug}.png",
        "bootstrap_kde_tiers": "figures/bootstrap_kde_tiers_{model_slug}.png",
        "ipw_comparison": "figures/ipw_comparison.png",
        "ks_summary": "figures/ks_summary.png",
    })
```

### YAML Schema

```yaml
# config.yaml — h-m1 experiment config
cache_dir: ".data_cache/datasets/hh-rlhf"
output_dir: "outputs"
dry_run: false
dry_run_n_per_tier: 500
seed: 42

data:
  tier_names:
    - "helpful-base"
    - "helpful-rejection-sampled"
    - "helpful-online"
  tier_ranks:
    helpful-base: 1
    helpful-rejection-sampled: 2
    helpful-online: 3
  models:
    - "all-MiniLM-L6-v2"
    - "paraphrase-MiniLM-L6-v2"
    - "all-mpnet-base-v2"
  primary_model: "all-MiniLM-L6-v2"
  batch_size: 256
  knn_k: 5
  knn_n_jobs: 1
  min_n_pairs_per_tier: 1000
  verification_mode: "no_checks"
  openblas_num_threads: 4
  shuffle_seed: 42

stats:
  bootstrap_n: 1000
  bootstrap_seed: 42
  significance_level: 0.05
  bonferroni_n_tests: 3
  cohen_d_threshold: 0.1
  jt_p_threshold: 0.05
  ks_p_threshold: 0.05
  model_consistency_threshold: 2

viz:
  figure_dpi: 150
  tier_colors:
    helpful-base: "#6baed6"
    helpful-rejection-sampled: "#fd8d3c"
    helpful-online: "#74c476"
  font_size_title: 13
  font_size_label: 11
  font_size_tick: 9
```

---

## Subtask Designs

### A-6: Visualization Configuration [3/3 subtasks]

#### C-6-1: VisualizationConfig [Complexity: 3, Budget included in A-6]

```python
@dataclass
class VisualizationConfig:
    figure_dpi: int = 150
    figure_size_bar: tuple = (12, 5)
    figure_size_line: tuple = (8, 5)
    figure_size_heatmap: tuple = (8, 6)
    figure_size_violin: tuple = (10, 6)
    figure_size_kde: tuple = (10, 5)
    figure_size_ipw: tuple = (8, 5)
    figure_size_ks: tuple = (8, 5)
    font_size_title: int = 13
    font_size_label: int = 11
    font_size_tick: int = 9
    font_size_annotation: int = 9
```

#### C-6-2: Tier Color Mapping [Complexity: 2, Budget included in A-6]

Covers all 7 plot types. Single source of truth for color/label lookup.

```python
TIER_COLORS = {
    "helpful-base": "#6baed6",
    "helpful-rejection-sampled": "#fd8d3c",
    "helpful-online": "#74c476",
}
TIER_LABELS = {
    "helpful-base": "T1: helpful-base",
    "helpful-rejection-sampled": "T2: helpful-rejection-sampled",
    "helpful-online": "T3: helpful-online",
}
TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
```

#### C-6-3: Plot Output Path Config [Complexity: 2, Budget included in A-6]

Naming convention: `h-m1/figures/{plot_type}_{model_slug}.png` for per-model plots; no suffix for multi-model plots.

```python
# model_slug map (from architecture MODULE_CONFIGS)
MODEL_SLUGS = {
    "all-MiniLM-L6-v2": "minilm",
    "paraphrase-MiniLM-L6-v2": "paraphrase",
    "all-mpnet-base-v2": "mpnet",
}

FIGURE_NAMES = {
    # per-model (append _{model_slug}.png)
    "tier_csem_bars": "tier_csem_bars",
    "tier_violin": "tier_violin",
    "bootstrap_kde_tiers": "bootstrap_kde_tiers",
    # multi-model (no suffix)
    "tier_monotonicity_lines": "tier_monotonicity_lines.png",
    "cohend_heatmap": "cohend_heatmap.png",
    "ipw_comparison": "ipw_comparison.png",
    "ks_summary": "ks_summary.png",
}

def get_figure_path(figures_dir: str, plot_type: str, model_slug: str = "") -> str:
    name = FIGURE_NAMES[plot_type]
    if model_slug and not name.endswith(".png"):
        return f"{figures_dir}/{name}_{model_slug}.png"
    return f"{figures_dir}/{name}"
```

---

### A-1: Per-Tier Data Loading [2/2 subtasks]

#### C-1-1: DataConfig [Complexity: 2, Budget included in A-1]

```python
@dataclass
class DataConfig:
    tier_names: List[str] = field(default_factory=lambda: [
        "helpful-base",
        "helpful-rejection-sampled",
        "helpful-online",
    ])
    tier_ranks: Dict[str, int] = field(default_factory=lambda: {
        "helpful-base": 1,
        "helpful-rejection-sampled": 2,
        "helpful-online": 3,
    })
    models: List[str] = field(default_factory=lambda: [
        "all-MiniLM-L6-v2",
        "paraphrase-MiniLM-L6-v2",
        "all-mpnet-base-v2",
    ])
    primary_model: str = "all-MiniLM-L6-v2"
    batch_size: int = 256
    knn_k: int = 5
    knn_n_jobs: int = 1
    min_n_pairs_per_tier: int = 1000
    verification_mode: str = "no_checks"
    openblas_num_threads: int = 4
    shuffle_seed: int = 42
    # Cache key: f"{prefix}_{model_slug}_{tier}_{n_pairs}"  (tier added vs h-e1)
```

#### C-1-2: ExperimentConfig (top-level with default_factory) [Complexity: 2, Budget included in A-1]

```python
@dataclass
class ExperimentConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    embeddings_dir: str = "embeddings"
    dry_run: bool = False
    dry_run_n_per_tier: int = 500
    seed: int = 42
    data: DataConfig = field(default_factory=DataConfig)
    stats: StatisticsConfig = field(default_factory=StatisticsConfig)
    viz: VisualizationConfig = field(default_factory=VisualizationConfig)
```

---

## Subtask Summary

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | VisualizationConfig | Dataclass: figure sizes, DPI, font sizes for all 7 plot types |
| C-6-2 | Tier color mapping | TIER_COLORS / TIER_LABELS / TIER_ORDER dicts for all 7 plot types |
| C-6-3 | Plot output path config | FIGURE_NAMES + get_figure_path() helper, naming convention |
| C-1-1 | DataConfig | Dataclass: tier names/ranks, models, knn_k, min_n_pairs, cache params |
| C-1-2 | ExperimentConfig | Top-level dataclass combining DataConfig/StatisticsConfig/VisualizationConfig via default_factory |

---

## Applied Patterns

Applied: standard Python dataclass with field(default_factory=...) for mutable defaults — matches h-e1 ExperimentResults dataclass pattern
Applied: nested config composition — top-level ExperimentConfig aggregates DataConfig, StatisticsConfig, VisualizationConfig via default_factory fields
Applied: tier_aware_cache_key — DataConfig documents cache key extension `{prefix}_{model_slug}_{tier}_{n_pairs}` vs h-e1 `{prefix}_{model_slug}_{n_pairs}`
Applied: knn_n_jobs_1_constraint — DataConfig.knn_n_jobs=1 (critical, verified from h-e1 actual code)
