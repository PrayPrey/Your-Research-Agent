# Config: H-M1
# Token Distribution Peakedness Analysis

**Applied**: flat module-level constants (matches H-E1 pattern; no dataclass needed)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config verified from actual H-E1 code (Read tool; Serena project selection unavailable)
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: flat module-level constants (dict + scalars)

---

## Inherited Configuration (Base Hypothesis)

From `h-e1/code/config.py` (ACTUAL CODE — verified field names):

```python
# H-E1 actual constants (imported by H-M1 config):
MODELS = {
    "llama2": "meta-llama/Llama-2-7b-hf",
    "mistral": "mistralai/Mistral-7B-v0.1",
}
SEED = 42
MAX_NEW_TOKENS = 30
BOOTSTRAP_N = 1000
```

H-M1 does NOT redefine `MODELS` — imports from H-E1 config directly.

---

## C-6-1: Visualization Config [Complexity: 3, Budget: 1 subtask]

Applied: standard matplotlib/seaborn defaults

### Configuration

```python
# Visualization constants — embed directly in visualization.py

VIZ_CONFIG = {
    # Color palette (consistent across all 4 figures)
    "color_hallucinated": "#E74C3C",   # red
    "color_correct":      "#2ECC71",   # green
    "palette": {"hallucinated": "#E74C3C", "correct": "#2ECC71"},

    # Figure sizes (width, height) in inches
    "figsize_bar":     (8, 5),
    "figsize_kde":     (7, 5),
    "figsize_scatter": (7, 6),
    "figsize_boxplot": (8, 5),

    # Output quality
    "dpi": 150,

    # Statistical annotation
    "p_value_format":   "{:.3f}",     # e.g. "p = 0.023"
    "sig_marker":       "*",           # shown when p < threshold
    "ns_marker":        "ns",

    # File names (joined with FIGURES_DIR in config.py)
    "fname_bar":     "peakedness_bar_comparison.png",
    "fname_kde":     "peakedness_kde_{dataset}.png",   # .format(dataset=...)
    "fname_scatter": "peakedness_scatter_auroc.png",
    "fname_boxplot": "peakedness_boxplot.png",
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Visualization Config | VIZ_CONFIG dict with palette, sizes, DPI, annotation, filenames |

---

## C-6-2: Full H-M1 Config Schema [Complexity: 3, Budget: 1 subtask]

Applied: flat module-level constants (mirrors H-E1 style)

### Configuration

```python
# code/config.py  (complete file)
import os
import sys

# ── Paths ────────────────────────────────────────────────────────────────────
_THIS_DIR    = os.path.dirname(os.path.abspath(__file__))
_H_M1_ROOT   = os.path.dirname(_THIS_DIR)
_REPO_ROOT   = os.path.dirname(os.path.dirname(_H_M1_ROOT))

H_E1_CODE_DIR    = os.path.join(_REPO_ROOT, "docs", "youra_research", "h-e1", "code")
H_E1_RESULTS_DIR = os.path.join(_REPO_ROOT, "docs", "youra_research", "h-e1", "results")

RESULTS_DIR = os.path.join(_H_M1_ROOT, "results")
FIGURES_DIR = os.path.join(_H_M1_ROOT, "figures")

# ── Import MODELS from H-E1 (do NOT redefine) ────────────────────────────────
sys.path.insert(0, H_E1_CODE_DIR)
from config import MODELS, SEED, MAX_NEW_TOKENS  # noqa: E402

# ── Datasets (recall-failure only; truthful_qa excluded) ─────────────────────
DATASETS = ["trivia_qa", "nq"]

MODELS_TO_RUN = ["llama2"]   # mistral optional; add "mistral" to extend

MAX_SAMPLES = {
    "trivia_qa": 2000,
    "nq":        2000,
}

# ── Statistical thresholds ────────────────────────────────────────────────────
P_VALUE_THRESHOLD = 0.05

# SEED already imported from H-E1 config (42)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-2 | Full H-M1 Config | Paths, dataset list, model selection, thresholds; imports MODELS from H-E1 |
