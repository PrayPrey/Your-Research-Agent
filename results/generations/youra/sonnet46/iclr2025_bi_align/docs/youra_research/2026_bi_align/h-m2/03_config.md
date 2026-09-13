# Configuration Design: h-m2 — Bidirectional C_sem Directional Asymmetry

**Hypothesis**: h-m2 (MECHANISM, INCREMENTAL)
**Date**: 2026-03-15
**Base**: h-m1 (VALIDATED)
**Infrastructure**: FULL tier (YAML + dataclass config, structured logging, unit tests)

Applied: nested dataclass composition pattern — ExperimentConfig aggregates CacheConfig + StatisticsConfig via default_factory fields; VisualizationConfig extended with bidirectional-specific sizes

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-m1)
**Status**: Config classes verified from h-m1 actual code via Read tool (Serena project not active for this path)
**Config Files Found**: `h-m1/code/run_experiment.py`, `h-m1/code/visualize.py`, `h-m1/code/embedder.py`, `h-m1/code/controls.py`
**Pattern Used**: dataclass — `VisualizationConfig` at line 40 of `h-m1/code/visualize.py`

---

## Inherited Configuration

### Config Classes (From Actual h-m1 Code)

```python
# From: h-m1/code/visualize.py (ACTUAL CODE — verified, lines 39-50)
@dataclass
class VisualizationConfig:
    figure_size: tuple = (12, 5)           # verified field name (NOT figure_size_bar)
    figure_size_wide: tuple = (18, 6)      # verified field name (only 2 size fields in h-m1)
    dpi: int = 150
    font_size_title: int = 14              # actual default: 14 (NOT 13 as in h-m1 spec)
    font_size_label: int = 11
    font_size_tick: int = 9
    ci_alpha: float = 0.3
    save_format: str = "png"
    figures_dir: str = "figures"

# From: h-m1/code/visualize.py (ACTUAL CODE — lines 18-36)
TIER_COLORS = {
    "helpful-base": "#4878CF",
    "helpful-rejection-sampled": "#6ACC65",
    "helpful-online": "#D65F5F",
}
TIER_LABELS = {
    "helpful-base": "T1: Base",
    "helpful-rejection-sampled": "T2: Rejection-Sampled",
    "helpful-online": "T3: Online",
}
MODEL_DISPLAY_NAMES = {
    "minilm": "MiniLM-L6-v2",
    "paraphrase": "Paraphrase-MiniLM",
    "mpnet": "MPNet-base-v2",
}

# From: h-m1/code/run_experiment.py (ACTUAL CODE — lines 55-66, 153-154)
# config dict keys: cache_dir, output_dir, embeddings_dir, figures_dir,
#                   dry_run (bool), n_samples_dry_run (int), report_path
# TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
# MODEL_CONFIGS: [{"name": ..., "slug": ..., "role": ...}]
# Bootstrap: n_bootstrap=1000, seed=42 (hardcoded in bootstrap_c_sem calls)
# KNN: k=5, n_jobs=1 (CRITICAL — verified in controls.py NearestNeighbors usage)
# encode_batch_size=256 (verified from h-m1 embedder.py)
```

**Verified from**: `h-m1/code/visualize.py` and `h-m1/code/run_experiment.py` (actual implementation)

**Critical field name corrections vs h-m1/03_config.md spec**:
- Actual: `figure_size` (NOT `figure_size_bar`)
- Actual: `figure_size_wide` (only 2 size fields, no `figure_size_line` / `figure_size_heatmap` etc.)
- Actual: `font_size_title = 14` (NOT 13)
- Actual: `dpi = 150` (confirmed)

---

## A-6: Extend Visualize — Visualization Config [Complexity: 13, Budget: 3 subtasks]

### C-6-1: Extended VisualizationConfig Dataclass [Subtask 1/3]

```python
# h-m2/code/visualize.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class VisualizationConfig:
    # Inherited from h-m1 (field names verified from actual code)
    figure_size: tuple = (12, 5)
    figure_size_wide: tuple = (18, 6)
    dpi: int = 150
    font_size_title: int = 14
    font_size_label: int = 11
    font_size_tick: int = 9
    ci_alpha: float = 0.3
    save_format: str = "png"
    figures_dir: str = "figures"
    # New for h-m2 bidirectional plots
    figure_size_bidir: tuple = (12, 6)     # bidirectional_comparison_bars
    figure_size_heatmap: tuple = (10, 6)   # significance_heatmap (tier x model)
    figure_size_violin: tuple = (12, 6)    # pairwise_distribution_violin
```

### C-6-2: Tier and Direction Color Mapping [Subtask 2/3]

```python
# h-m2/code/visualize.py — all color/label constants
TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]

# Inherited from h-m1 actual code (verified hex values)
TIER_COLORS = {
    "helpful-base": "#4878CF",
    "helpful-rejection-sampled": "#6ACC65",
    "helpful-online": "#D65F5F",
}
TIER_LABELS = {
    "helpful-base": "T1: Base",
    "helpful-rejection-sampled": "T2: Rejection-Sampled",
    "helpful-online": "T3: Online",
}
MODEL_DISPLAY_NAMES = {
    "minilm": "MiniLM-L6-v2",
    "paraphrase": "Paraphrase-MiniLM",
    "mpnet": "MPNet-base-v2",
}

# New for h-m2: direction colors (blue/orange — perceptually distinct from tier palette)
DIRECTION_COLORS = {
    "H_given_A": "#2196F3",    # blue — human accommodates AI (H←A)
    "A_given_H": "#FF5722",    # orange-red — AI accommodates human (A←H)
}
DIRECTION_LABELS = {
    "H_given_A": r"$C_{sem}^{H \leftarrow A}$",
    "A_given_H": r"$C_{sem}^{A \leftarrow H}$",
}
```

### C-6-3: Figure Output Path Config [Subtask 3/3]

```python
# h-m2/code/visualize.py — figure registry and path helper

# 7 required/autonomous figures for h-m2
FIGURE_NAMES_M2 = {
    # Required (gate figure)
    "bidirectional_comparison_bars": "bidirectional_comparison_bars.png",
    # Autonomous
    "directional_asymmetry_bars":   "directional_asymmetry_bars.png",
    "asymmetry_delta_line":         "asymmetry_delta_line.png",
    "pairwise_distribution_violin": "pairwise_distribution_violin.png",
    "significance_heatmap":         "significance_heatmap.png",
    "bootstrap_ci_comparison":      "bootstrap_ci_comparison.png",
    "ipw_adjusted_asymmetry":       "ipw_adjusted_asymmetry.png",
}


def get_figure_path(
    figures_dir: str,
    plot_type: str,
    model_slug: Optional[str] = None,
) -> str:
    """Construct figure output path (extends h-m1 convention)."""
    import os
    os.makedirs(figures_dir, exist_ok=True)
    name = FIGURE_NAMES_M2.get(plot_type, f"{plot_type}.png")
    if model_slug:
        base = name.replace(".png", "")
        return os.path.join(figures_dir, f"{base}_{model_slug}.png")
    return os.path.join(figures_dir, name)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | VisualizationConfig | Extend h-m1 dataclass: inherit verified field names, add figure_size_bidir/heatmap/violin |
| C-6-2 | Direction color mapping | DIRECTION_COLORS/DIRECTION_LABELS new; inherit verified h-m1 TIER_COLORS/TIER_LABELS |
| C-6-3 | Figure output path config | FIGURE_NAMES_M2 (7 entries, 1 required) + get_figure_path() helper |

---

## A-8: Embedding Cache Config [Complexity: 11, Budget: 2 subtasks]

### C-8-1: CacheConfig Dataclass [Subtask 1/2]

```python
# h-m2/code/config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class CacheConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m1/code/embeddings"    # reuse h-m1 cache directory
    models: List[str] = field(default_factory=lambda: [
        "all-MiniLM-L6-v2",
        "paraphrase-MiniLM-L6-v2",
        "all-mpnet-base-v2",
    ])
    tiers: List[str] = field(default_factory=lambda: [
        "helpful-base",
        "helpful-rejection-sampled",
        "helpful-online",
    ])
    encode_batch_size: int = 256                        # verified from h-m1 embedder.py
    # h-m1 reuse keys (already cached — do not re-encode)
    h_m1_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_H_next_{tier}.npy",
        "{model}_A_curr_{tier}.npy",
    ])
    # New keys for A<-H direction (may be missing — encode if absent)
    h_m2_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_A_next_{tier}.npy",
        "{model}_H_curr_{tier}.npy",
    ])
```

### C-8-2: Full ExperimentConfig + YAML + Loader [Subtask 2/2]

```python
# h-m2/code/config.py (complete module)
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import os
import yaml


@dataclass
class CacheConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m1/code/embeddings"
    models: List[str] = field(default_factory=lambda: [
        "all-MiniLM-L6-v2",
        "paraphrase-MiniLM-L6-v2",
        "all-mpnet-base-v2",
    ])
    tiers: List[str] = field(default_factory=lambda: [
        "helpful-base",
        "helpful-rejection-sampled",
        "helpful-online",
    ])
    encode_batch_size: int = 256
    h_m1_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_H_next_{tier}.npy",
        "{model}_A_curr_{tier}.npy",
    ])
    h_m2_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_A_next_{tier}.npy",
        "{model}_H_curr_{tier}.npy",
    ])


@dataclass
class StatisticsConfig:
    alpha: float = 0.05
    n_bootstrap: int = 1000
    bootstrap_seed: int = 42
    cohen_d_threshold: float = 0.1
    knn_k: int = 5
    knn_n_jobs: int = 1                    # CRITICAL: never -1 (OpenBLAS crash at 155k scale)
    min_n_pairs_per_tier: int = 1000
    tiers_required: int = 2               # gate: >= 2/3 tiers must pass
    models_required: int = 2             # gate: >= 2/3 models must pass
    ks_p_threshold: float = 0.05         # trigger IPW if any KS p < this


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m2"
    seed: int = 42
    output_dir: str = "../results"
    figures_dir: str = "../figures"
    cache: CacheConfig = field(default_factory=CacheConfig)
    stats: StatisticsConfig = field(default_factory=StatisticsConfig)


def verify_cache(cache_config: CacheConfig) -> Tuple[bool, Dict[str, bool]]:
    """Check all required .npy cache files. Returns (all_present, {key: exists})."""
    status = {}
    all_templates = (
        cache_config.h_m1_cache_key_templates
        + cache_config.h_m2_cache_key_templates
    )
    for template in all_templates:
        for model in cache_config.models:
            model_slug = model.replace("/", "_")
            for tier in cache_config.tiers:
                key = template.format(model=model_slug, tier=tier)
                path = os.path.join(cache_config.embeddings_dir, key)
                status[key] = os.path.exists(path)
    return all(status.values()), status


def get_missing_h_m2_keys(cache_config: CacheConfig) -> List[str]:
    """Return list of missing h-m2-specific .npy keys (A_next, H_curr)."""
    missing = []
    for template in cache_config.h_m2_cache_key_templates:
        for model in cache_config.models:
            model_slug = model.replace("/", "_")
            for tier in cache_config.tiers:
                key = template.format(model=model_slug, tier=tier)
                path = os.path.join(cache_config.embeddings_dir, key)
                if not os.path.exists(path):
                    missing.append(key)
    return missing


def load_config(yaml_path: str) -> ExperimentConfig:
    """Load ExperimentConfig from YAML file, overriding defaults."""
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    cfg = ExperimentConfig()
    for top_key in ("hypothesis_id", "seed", "output_dir", "figures_dir"):
        if top_key in data:
            setattr(cfg, top_key, data[top_key])
    if "cache" in data:
        for k, v in data["cache"].items():
            if hasattr(cfg.cache, k):
                setattr(cfg.cache, k, v)
    if "stats" in data:
        for k, v in data["stats"].items():
            if hasattr(cfg.stats, k):
                setattr(cfg.stats, k, v)
    return cfg
```

**config.yaml**:

```yaml
# h-m2/code/config.yaml
hypothesis_id: "h-m2"
seed: 42
output_dir: "../results"
figures_dir: "../figures"

cache:
  cache_dir: ".data_cache/datasets/hh-rlhf"
  embeddings_dir: "../h-m1/code/embeddings"
  models:
    - "all-MiniLM-L6-v2"
    - "paraphrase-MiniLM-L6-v2"
    - "all-mpnet-base-v2"
  tiers:
    - "helpful-base"
    - "helpful-rejection-sampled"
    - "helpful-online"
  encode_batch_size: 256

stats:
  alpha: 0.05
  n_bootstrap: 1000
  bootstrap_seed: 42
  cohen_d_threshold: 0.1
  knn_k: 5
  knn_n_jobs: 1
  min_n_pairs_per_tier: 1000
  tiers_required: 2
  models_required: 2
  ks_p_threshold: 0.05
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | CacheConfig | Dataclass: embeddings_dir pointing to h-m1 cache, h_m1 + h_m2 key templates |
| C-8-2 | ExperimentConfig + YAML + loader | Full config.py module with verify_cache(), get_missing_h_m2_keys(), load_config(); config.yaml schema |

---

## Subtask Summary

| ID | Subtask | Task | Description |
|----|---------|------|-------------|
| C-6-1 | VisualizationConfig | A-6 | Extend h-m1 dataclass with verified field names; add bidir/heatmap/violin sizes |
| C-6-2 | Direction color mapping | A-6 | DIRECTION_COLORS/DIRECTION_LABELS new; verified h-m1 TIER_COLORS/TIER_LABELS |
| C-6-3 | Figure output path config | A-6 | FIGURE_NAMES_M2 (7 entries) + get_figure_path() |
| C-8-1 | CacheConfig | A-8 | Dataclass with h_m1 reuse vs h_m2 new key templates |
| C-8-2 | ExperimentConfig + YAML + loader | A-8 | Complete config.py module + config.yaml for Phase 4 copy-paste |

**Total subtasks: 5/5**
