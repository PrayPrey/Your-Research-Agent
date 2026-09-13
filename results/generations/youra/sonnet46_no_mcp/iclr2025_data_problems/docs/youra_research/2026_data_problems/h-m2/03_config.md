# Config Document: H-M2
# Domain-Stratified Contamination Re-Analysis

**Hypothesis**: H-M2 | **Type**: MECHANISM (FULL) | **Date**: 2026-05-04

Applied: Domain-stratified-statistical-reanalysis pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental over H-M1 implementation)
**Status**: Config classes verified from base code
**Config Files Found**: `h-m1/code/config.py` (actual implementation read)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-M1 Code)

```python
# From: h-m1/code/config.py (ACTUAL CODE — verified)
@dataclass
class Config:
    seed: int = 1
    results_dir: str = "results"
    figures_dir: str = "figures"
    gate_p_threshold: float = 0.05
    # H-M1 also has: ngram_n, corpus_configs, mmlu_tasks, etc.
    # H-M2 does NOT inherit corpus streaming fields — reanalysis only
```

**Verified from**: `h-m1/code/config.py` (actual implementation)

**Inherited fields used in H-M2**: `seed`, `results_dir`, `figures_dir`
**Reused default**: `alpha = gate_p_threshold = 0.05`

---

## A-6: Interaction & Top-N Analysis [Complexity: 9, Budget: 2 subtasks]

Applied: Standard PyTorch/SciPy statistical analysis defaults

### Configuration (Python Dataclass)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import yaml
import os


@dataclass
class Config:
    # Data source
    h_m1_results_path: str = "../../h-m1/experiment_results.json"

    # Statistical parameters (C-6-1)
    alpha: float = 0.05  # significance threshold; matches h-m1 gate_p_threshold
    seed: int = 1        # inherited from h-m1 Config.seed

    # Gate threshold (C-6-1)
    min_corpora_directional_confirmed: int = 2  # >=2 of 3 corpora must confirm direction

    # Analysis parameters (C-6-2)
    top_n: int = 5  # top-N subtasks per corpus for bar charts
    corpora: List[str] = field(default_factory=lambda: ["pile", "c4", "redpajama"])

    # Directional predictions per corpus (C-6-1)
    # Non-standard: directional_predictions encodes prior hypothesis per corpus
    directional_predictions: dict = field(default_factory=lambda: {
        "pile":      {"group_a_domain": "academic",    "group_b_domain": "commonsense"},
        "c4":        {"group_a_domain": "commonsense", "group_b_domain": "academic"},
        "redpajama": {"group_a_domain": "academic",    "group_b_domain": "commonsense"},
    })

    # Output paths (C-6-2)
    results_dir: str = "results"
    figures_dir: str = "figures"

    # Figure settings (C-6-2)
    figure_dpi: int = 150
    figure_format: str = "png"


def load_config() -> Config:
    """Load config with optional YAML override via H_M2_CONFIG_PATH env var."""
    cfg = Config()
    path = os.environ.get("H_M2_CONFIG_PATH")
    if path and os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f)
        if data:
            for k, v in data.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)
    return cfg
```

---

### YAML Schema

```yaml
# h-m2 experiment configuration schema
# All fields, types, defaults, and descriptions

# Data source
h_m1_results_path: "../../h-m1/experiment_results.json"  # str: path to H-M1 results JSON

# Statistical parameters
alpha: 0.05          # float: significance threshold for Mann-Whitney p-value
seed: 1              # int: random seed for reproducibility

# Gate threshold
min_corpora_directional_confirmed: 2  # int: minimum corpora that must confirm directional pattern (of 3)

# Analysis parameters
top_n: 5             # int: top-N subtasks per corpus returned by top_n_per_corpus()
corpora:             # list[str]: corpus keys to analyze
  - pile
  - c4
  - redpajama

# Directional predictions per corpus
# group_a_domain > group_b_domain is the expected direction (one-tailed test)
directional_predictions:
  pile:
    group_a_domain: academic      # str: domain expected to have higher contamination
    group_b_domain: commonsense   # str: domain expected to have lower contamination
  c4:
    group_a_domain: commonsense
    group_b_domain: academic
  redpajama:
    group_a_domain: academic
    group_b_domain: commonsense

# Output paths
results_dir: results   # str: directory for JSON result files
figures_dir: figures   # str: directory for figure files

# Figure settings
figure_dpi: 150        # int: DPI for saved figures
figure_format: png     # str: image format for saved figures
```

---

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Statistical parameters config | alpha, seed, min_corpora_directional_confirmed, directional_predictions dict mapping each corpus to expected domain direction for one-tailed Mann-Whitney test |
| C-6-2 | Output paths and figure settings | results_dir, figures_dir, figure_dpi, figure_format, top_n for top-N subtask bar chart generation |
