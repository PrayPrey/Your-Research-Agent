# H-M1 Configuration Design

**Hypothesis:** H-M1 (MECHANISM — Causal Step 1: Corpus → Log-Odds)
**Base Hypothesis:** H-E1 (COMPLETED, PASS)
**Generated:** 2026-03-14

Applied: FULL-tier YAML + dataclass config pattern
Applied: h-e1-incremental-extension-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 code analyzed)
**Status**: config classes verified from base code — `h-e1/code/config.py` is plain dict CONFIG (not dataclass)
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: dataclass (H-M1 FULL tier, unlike H-E1 EXISTENCE PoC plain dict)

---

## Inherited Configuration (Base Hypothesis)

### Config Values (From Actual h-e1/code/config.py)

```python
# Verified from: h-e1/code/config.py (plain dict)
CONFIG = {
    "seed": 42,
    "window_size": 10,          # ← CRITICAL: 10, not 5
    "n_bootstrap": 10_000,      # H-E1 used 10k; H-M1 uses 1000
    "fasttext_model_path": ".../h-e1/data/models/openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin",
    "occupation_lexicon": [...], # 60 WinoBias tokens
    "demographic_lexicon": [...],# 30 tokens (pronouns + demographic NEs)
    "configurations": [C0..C6], # C1-C5 fasttext, C6 doremi
    "figure_size": (10, 6),
    "figure_size_heatmap": (12, 8),  # ← H-E1 actual value
    "dpi": 150,
}
```

### Reused vs New

| Field | Source | Notes |
|-------|--------|-------|
| `seed` | H-E1 (42) | Identical |
| `window_size` | H-E1 (10) | Inherited — trust code not PRD |
| `fasttext_model_path` | H-E1 | Reused via `he1_data_dir` |
| `occupation_lexicon` | H-E1 | Loaded via `get_he1_lexicons()` |
| `demographic_lexicon` | H-E1 | Loaded via `get_he1_lexicons()` |
| `n_bootstrap` | NEW (1000) | H-M1 uses 1000, H-E1 used 10000 |
| `alpha` | NEW (0.5) | Laplace smoothing — not in H-E1 |
| `alpha_level` | NEW (0.05) | Significance threshold |
| `filtering_intensities` | NEW | [10,30,50,70,90] for Spearman |
| `figure_size_heatmap` | EXTENDED | H-M1 uses (14, 10); H-E1 had (12, 8) |

---

## HM1Config Dataclass (config.py)

```python
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

HE1_CODE_DIR: str = str(Path(__file__).parent.parent.parent / "h-e1" / "code")
HE1_DATA_DIR: str = str(Path(__file__).parent.parent.parent / "h-e1" / "data")
HM1_BASE_DIR: str = str(Path(__file__).parent.parent)


@dataclass
class HM1Config:
    # --- H-E1 inherited paths ---
    he1_code_dir: str = HE1_CODE_DIR
    he1_data_dir: str = HE1_DATA_DIR
    fasttext_model_path: str = str(
        Path(HE1_DATA_DIR) / "models" / "openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin"
    )

    # --- Inherited values (verified from h-e1/code/config.py) ---
    seed: int = 42
    window_size: int = 10           # matches h-e1 actual code (not PRD's "5")

    # --- H-M1 specific ---
    alpha: float = 0.5              # Laplace smoothing for log-odds
    n_bootstrap: int = 1000         # H-M1 uses 1000 (H-E1 used 10000)
    alpha_level: float = 0.05
    filtering_intensities: List[int] = field(default_factory=lambda: [10, 30, 50, 70, 90])
    fasttext_configs: List[str] = field(default_factory=lambda: ["C1", "C2", "C3", "C4", "C5"])
    all_configs: List[str] = field(default_factory=lambda: ["C1", "C2", "C3", "C4", "C5", "C6"])

    # --- Output paths ---
    data_dir: str = str(Path(HM1_BASE_DIR) / "data")
    figures_dir: str = str(Path(HM1_BASE_DIR) / "figures")
    results_path: str = str(Path(HM1_BASE_DIR) / "results.json")
    validation_path: str = str(Path(HM1_BASE_DIR) / "04_validation.md")
    log_odds_matrix_path: str = str(Path(HM1_BASE_DIR) / "data" / "log_odds_matrix.csv")

    # --- Visualization ---
    figure_size: tuple = (10, 6)
    figure_size_heatmap: tuple = (14, 10)   # larger than H-E1's (12,8) for demo×occ heatmap
    dpi: int = 150
    color_scheme: str = "colorblind"
    bar_color: str = "#4C72B0"
    highlight_color: str = "#DD8452"
    output_format: str = "png"


def load_config(yaml_path: Optional[str] = None) -> HM1Config:
    """Load config from YAML overrides or return defaults."""
    cfg = HM1Config()
    if yaml_path is None:
        default_yaml = Path(__file__).parent / "config.yaml"
        if default_yaml.exists():
            yaml_path = str(default_yaml)
    if yaml_path:
        with open(yaml_path) as f:
            overrides = yaml.safe_load(f) or {}
        for k, v in overrides.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
    return cfg


def get_he1_lexicons() -> Dict[str, List[str]]:
    """Import and return H-E1 occupation_lexicon and demographic_lexicon."""
    cfg = HM1Config()
    if cfg.he1_code_dir not in sys.path:
        sys.path.insert(0, cfg.he1_code_dir)
    from config import CONFIG as HE1_CONFIG  # noqa: PLC0415
    return {
        "occupation_lexicon": HE1_CONFIG["occupation_lexicon"],
        "demographic_lexicon": HE1_CONFIG["demographic_lexicon"],
    }
```

---

## YAML Config Schema (config.yaml)

```yaml
# H-M1 experiment config — override any HM1Config field here
# All fields are optional; unset fields use dataclass defaults.

seed: 42
window_size: 10
alpha: 0.5
n_bootstrap: 1000
alpha_level: 0.05

filtering_intensities: [10, 30, 50, 70, 90]
fasttext_configs: ["C1", "C2", "C3", "C4", "C5"]
all_configs: ["C1", "C2", "C3", "C4", "C5", "C6"]

# Paths — leave unset to use auto-resolved defaults relative to repo root
# he1_code_dir: /absolute/path/to/h-e1/code
# he1_data_dir: /absolute/path/to/h-e1/data
# data_dir: /absolute/path/to/h-m1/data
# figures_dir: /absolute/path/to/h-m1/figures
# log_odds_matrix_path: /absolute/path/to/h-m1/data/log_odds_matrix.csv

# Visualization
dpi: 150
output_format: png
color_scheme: colorblind
bar_color: "#4C72B0"
highlight_color: "#DD8452"
```

---

## A-7: Visualizations [Complexity: 11, Budget: 1 subtask]

Applied: Standard matplotlib/seaborn defaults

```python
# Visualizer init fields (from HM1Config)
figures_dir: str          # HM1Config.figures_dir
dpi: int = 150            # HM1Config.dpi
figure_size: tuple = (10, 6)
figure_size_heatmap: tuple = (14, 10)  # non-standard: enlarged for demo×occ matrix
color_scheme: str = "colorblind"
bar_color: str = "#4C72B0"
highlight_color: str = "#DD8452"
output_format: str = "png"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | VizConfig | Wire Visualizer.__init__ from HM1Config fields; define output filenames for all 4 figures |

---

## A-9: Unit Tests [Complexity: 10, Budget: 1 subtask]

Applied: Standard pytest fixture pattern

```python
# Test fixture config (hardcoded minimal dict for tests)
TEST_CONFIG = {
    "window_size": 10,
    "alpha": 0.5,
    "n_bootstrap": 100,    # reduced for test speed
    "seed": 42,
    "alpha_level": 0.05,
    "filtering_intensities": [10, 30, 50, 70, 90],
}

# Minimal lexicons for unit tests (subset)
TEST_OCC_LEXICON = ["nurse", "engineer", "doctor"]
TEST_DEMO_LEXICON = ["he", "she", "man", "woman"]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | TestFixtures | Define TEST_CONFIG dict and minimal lexicon fixtures; use for all unit test parametrization |

---

## A-2: Corpus Loading [Complexity: 9, Budget: 1 subtask]

Applied: h-e1 path-resolution pattern

```python
# Corpus path resolution (derived from HM1Config)
# load_corpus(config_id, data_dir) expects:
#   {he1_data_dir}/corpora/{config_id}.jsonl
# C0 excluded; C1-C6 required

CORPUS_CONFIG_IDS = ["C1", "C2", "C3", "C4", "C5", "C6"]

# Fallback: if .jsonl missing, call CorpusFilter.build_all_corpora()
# CorpusFilter init requires: fasttext_model_path, seed=42
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | CorpusPathConfig | Validate C1-C6 .jsonl existence under he1_data_dir/corpora/; document fallback to build_all_corpora() |

---

## Per-Module Config Summary

| Module | Config Fields Used |
|--------|--------------------|
| LogOddsComputer | `window_size`, `alpha`, `occupation_lexicon`*, `demographic_lexicon`* |
| StatisticalTests | `n_bootstrap`, `seed`, `alpha_level`, `filtering_intensities` |
| Visualizer | `figures_dir`, `dpi`, `figure_size`, `figure_size_heatmap`, `bar_color`, `highlight_color`, `output_format` |
| run_experiment | all fields; `he1_code_dir`, `he1_data_dir`, `all_configs`, `fasttext_configs` |
| load_corpora | `he1_code_dir`, `he1_data_dir`, `fasttext_model_path`, `all_configs` |

*lexicons loaded via `get_he1_lexicons()` at runtime

---

## Key Design Decisions

- `n_bootstrap: 1000` — H-M1 brief specifies 1000; H-E1 used 10000 (different experiments)
- `window_size: 10` — inherited from h-e1/code/config.py actual value; PRD incorrectly states 5
- `figure_size_heatmap: (14, 10)` — enlarged vs H-E1's (12, 8) to accommodate demo×occ matrix
- `get_he1_lexicons()` inserts `he1_code_dir` into sys.path at call time; safe for repeated calls
- YAML overrides apply on top of dataclass defaults; unrecognized keys are silently ignored
