# Configuration: h-m3 — Within-Prompt Quality Probe via Chosen/Rejected Δ-Cosine Analysis

**Hypothesis**: h-m3 (MECHANISM, INCREMENTAL)
**Date**: 2026-03-15
**Base**: h-m2 (VALIDATED)
**Format**: Dataclass (nested, matching h-m2 pattern)

Applied: nested dataclass config pattern (copy-extend from h-m2)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP returned "No active project" error. Config verified via direct Read tool on actual h-m2 source file.
**Config Files Found**: `docs/youra_research/20260315_bi_align/h-m2/code/config.py` (read directly)
**Pattern Used**: nested dataclass (`CacheConfig`, `StatisticsConfig`, `FigureConfig`, `ExperimentConfig`)

**Verified field names from actual h-m2 code**:
- `ExperimentConfig`: `hypothesis_id`, `cache`, `stats`, `figures`, `output_dir`, `embedding_cache_dir`, `dry_run`, `n_samples_dry_run`
- `CacheConfig`: `cache_dir`, `embeddings_dir`, `models`, `tiers`, `encode_batch_size`, `h_m1_cache_key_templates`, `h_m2_cache_key_templates`
- `StatisticsConfig`: `seed`, `alpha`, `n_bootstrap`, `knn_k`, `knn_n_jobs`, `tiers_required`, `models_required`, `min_n_pairs`, `cohen_d_threshold`
- `FigureConfig`: `figures_dir`, `dpi`, `save_format`

**Key difference from architecture spec**: h-m2 uses `output_dir` (not `results_dir`), and `embedding_cache_dir` as a top-level field. h-m3 config mirrors this pattern.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-m2 Code)

```python
# From: docs/youra_research/20260315_bi_align/h-m2/code/config.py (ACTUAL CODE)
@dataclass
class CacheConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m1/code/embeddings"   # h-m2 reuses h-m1 cache
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
    seed: int = 42
    alpha: float = 0.05
    n_bootstrap: int = 1000
    knn_k: int = 5
    knn_n_jobs: int = 1   # CRITICAL: never -1 at 155k scale
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
    embedding_cache_dir: str = "../h-m1/code/embeddings"
    dry_run: bool = False
    n_samples_dry_run: int = 500
```

**Verified from**: `docs/youra_research/20260315_bi_align/h-m2/code/config.py` (actual implementation, Read tool)

---

## A-1: Setup & Config [Complexity: 8, Budget: 1 subtask]

Applied: Standard dataclass nested config pattern

### Configuration (Python Dataclass)

```python
# h-m3/code/config.py
import os
import yaml
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CacheConfig:
    """Cache configuration for datasets and embeddings."""
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m2/code/embeddings"   # Reuse h-m2 cache; h-m3 adds new keys
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
    # Inherited from h-m1/h-m2 (already cached)
    h_m1_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_H_next_{tier}.npy",
        "{model}_A_curr_{tier}.npy",
    ])
    h_m2_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_A_next_{tier}.npy",
        "{model}_H_curr_{tier}.npy",
    ])
    # h-m3 new keys (chosen/rejected pair embeddings)
    h_m3_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_A_chosen_{tier}.npy",
        "{model}_A_rejected_{tier}.npy",
        "{model}_H_next_cr_{tier}.npy",   # H_next from chosen/rejected pairs
    ])


@dataclass
class StatisticsConfig:
    """Statistical test configuration."""
    seed: int = 42
    alpha: float = 0.05
    n_bootstrap: int = 1000
    knn_k: int = 5
    knn_n_jobs: int = 1   # CRITICAL: never -1 at 155k scale
    tiers_required: int = 2
    models_required: int = 2
    min_n_pairs: int = 1000    # Auto-demote gate threshold
    cohen_d_threshold: float = 0.1
    ops_required: int = 2      # >= 2/3 operationalizations must pass gate


@dataclass
class FigureConfig:
    """Figure output configuration."""
    figures_dir: str = "../results/figures"
    dpi: int = 150
    save_format: str = "png"


@dataclass
class ExperimentConfig:
    """Top-level experiment configuration for h-m3."""
    hypothesis_id: str = "h-m3"
    cache: CacheConfig = field(default_factory=CacheConfig)
    stats: StatisticsConfig = field(default_factory=StatisticsConfig)
    figures: FigureConfig = field(default_factory=FigureConfig)
    output_dir: str = "../results"
    embedding_cache_dir: str = "../h-m2/code/embeddings"
    dry_run: bool = False
    n_samples_dry_run: int = 500

    @property
    def cache_dir(self) -> str:
        return self.cache.cache_dir

    @property
    def figures_dir(self) -> str:
        return self.figures.figures_dir


def load_config(yaml_path: Optional[str] = None) -> ExperimentConfig:
    """Load ExperimentConfig from YAML file with defaults.

    Args:
        yaml_path: Path to config.yaml. If None, returns default config.

    Returns:
        ExperimentConfig with values merged from YAML.
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

    for key in ("hypothesis_id", "output_dir", "embedding_cache_dir", "dry_run", "n_samples_dry_run"):
        if key in data:
            setattr(config, key, data[key])

    if "cache" in data:
        for k, v in data["cache"].items():
            if hasattr(config.cache, k):
                setattr(config.cache, k, v)

    if "stats" in data:
        for k, v in data["stats"].items():
            if hasattr(config.stats, k):
                setattr(config.stats, k, v)

    if "figures" in data:
        for k, v in data["figures"].items():
            if hasattr(config.figures, k):
                setattr(config.figures, k, v)

    return config
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | config.py + config.yaml | Copy-extend from h-m2: update hypothesis_id, add `ops_required`, `h_m3_cache_key_templates`; write config.yaml mirror |

---

## A-7: run_experiment.py Config [Complexity: 16, Budget: 2 subtasks]

Applied: Standard dataclass nested config pattern

### config.yaml Schema

```yaml
# h-m3/code/config.yaml
# Mirrors ExperimentConfig dataclass. All fields are optional (defaults apply).

hypothesis_id: "h-m3"
output_dir: "../results"
embedding_cache_dir: "../h-m2/code/embeddings"
dry_run: false
n_samples_dry_run: 500

cache:
  cache_dir: ".data_cache/datasets/hh-rlhf"
  embeddings_dir: "../h-m2/code/embeddings"
  encode_batch_size: 256

stats:
  seed: 42
  alpha: 0.05
  n_bootstrap: 1000
  knn_n_jobs: 1
  min_n_pairs: 1000
  ops_required: 2

figures:
  figures_dir: "../results/figures"
  dpi: 150
  save_format: "png"
```

### run_experiment.py Argument Schema

```python
# Arguments parsed by parse_args() in run_experiment.py
# --config   str   Path to config.yaml (default: None → use dataclass defaults)
# --dry-run  flag  Override config.dry_run=True
# --model    str   Run single model only (default: all 3 models)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | ExperimentConfig integration | `load_config()` called at top of `main()`; pass `config` object to all downstream functions |
| C-7-2 | config.yaml file | Write `config.yaml` in h-m3/code/ with flat YAML matching ExperimentConfig structure |

---

## A-8: Embedding Encode Pass [Complexity: 11, Budget: 1 subtask]

Applied: Standard cache key naming pattern (verified from h-m2 `verify_cache()` slug logic)

### Cache Key Naming Convention

```python
# Model slug map (verified from h-m2 code/config.py verify_cache())
MODEL_SLUG = {
    "all-MiniLM-L6-v2":          "minilm",
    "paraphrase-MiniLM-L6-v2":   "paraphrase",
    "all-mpnet-base-v2":         "mpnet",
}

# Tier slug map (verified from h-m2 verify_cache())
TIER_SLUG = {
    "helpful-base":               "base",
    "helpful-rejection-sampled":  "rejection_sampled",
    "helpful-online":             "online",
}

# h-m3 new cache key templates (stored in CacheConfig.h_m3_cache_key_templates)
H_M3_CACHE_KEY_TEMPLATES = [
    "{model}_A_chosen_{tier}.npy",    # e.g., minilm_A_chosen_base.npy
    "{model}_A_rejected_{tier}.npy",  # e.g., minilm_A_rejected_base.npy
    "{model}_H_next_cr_{tier}.npy",   # e.g., minilm_H_next_cr_base.npy
]
# Total new files: 3 templates × 3 models × 3 tiers = 27 .npy files
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Cache key convention | Use `{model_slug}_A_chosen_{tier_slug}.npy`, `_A_rejected_`, `_H_next_cr_` templates; verify slug maps match h-m2 `verify_cache()` logic |

---

## A-9: Unit Tests Config [Complexity: 12, Budget: 1 subtask]

Applied: Standard dataclass nested config pattern

### Test Fixture Config

```python
# tests/conftest.py (or inline in each test file)
import pytest
from config import ExperimentConfig, CacheConfig, StatisticsConfig, FigureConfig
import tempfile
import os


@pytest.fixture
def test_config(tmp_path):
    """Minimal ExperimentConfig for tests — small n to keep tests fast."""
    cfg = ExperimentConfig()
    cfg.dry_run = True
    cfg.n_samples_dry_run = 100       # Small sample for unit tests
    cfg.cache.cache_dir = str(tmp_path / "data_cache")
    cfg.cache.embeddings_dir = str(tmp_path / "embeddings")
    cfg.figures.figures_dir = str(tmp_path / "figures")
    cfg.output_dir = str(tmp_path / "results")
    cfg.stats.n_bootstrap = 50        # Fast bootstrap in tests
    cfg.stats.min_n_pairs = 10        # Low threshold for fixture data
    return cfg


@pytest.fixture
def test_stats_config():
    """StatisticsConfig with fast bootstrap for unit tests."""
    cfg = StatisticsConfig()
    cfg.n_bootstrap = 50
    cfg.min_n_pairs = 10
    cfg.seed = 0
    return cfg
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Test fixtures | `conftest.py` with `test_config` and `test_stats_config` fixtures using `tmp_path`; small `n_bootstrap=50`, `min_n_pairs=10` for fast tests |

---

## Self-Validation

- [x] ONE format only (Dataclass — matches h-m2 pattern)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X" per section)
- [x] Rationale only for non-standard values (`knn_n_jobs=1`, `H_next_cr` naming)
- [x] Subtask count within budget (5/5 used)
- [x] "Codebase Analysis (Serena)" section included
- [x] Base config field names verified from actual h-m2 code
- [x] "Inherited Configuration (Base Hypothesis)" section included
- [x] `ops_required: int = 2` added to StatisticsConfig (new h-m3 field)
- [x] `h_m3_cache_key_templates` added to CacheConfig for A_chosen, A_rejected, H_next_cr
