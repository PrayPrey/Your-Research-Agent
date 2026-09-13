# Config: H-M3
## RLHF Causal Chain Produces 2-Cluster Trustworthiness Correlation Structure

**Date:** 2026-08-04
**Applied**: No relevant KB pattern (diffusion-focused KB)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from h-m2/code/config.py (actual implementation)
**Config Files Found**: `docs/youra_research/h-m2/code/config.py`
**Pattern Used**: hardcoded constants (flat module-level, no dataclass)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-m2 Code)

```python
# From: docs/youra_research/h-m2/code/config.py (ACTUAL CODE)
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_HM2 = os.path.dirname(_HERE)           # h-m2/
_RESEARCH = os.path.dirname(_HM2)       # youra_research/

HE1_JSON = os.path.join(_RESEARCH, "h-e1", "experiment_results_phase3.json")
FIGURES_DIR = os.path.join(_HM2, "figures")
RESULTS_JSON = os.path.join(_HM2, "experiment_results_h_m2.json")

DIMENSIONS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]
SAFETY_IDX = 1
ROBUSTNESS_IDX = 3
ETHICS_IDX = 5
```

**Verified from**: `docs/youra_research/h-m2/code/config.py` (actual implementation)

---

## A-1: Config + Paths [Complexity: 5, Budget: 1 subtask]

### Configuration (Hardcoded Constants)

```python
"""Configuration for H-M3: RLHF Causal Chain Produces 2-Cluster Trustworthiness Correlation Structure."""
import os

# Path anchoring (mirrors h-m2 pattern exactly)
_HERE = os.path.dirname(os.path.abspath(__file__))
_HM3 = os.path.dirname(_HERE)                        # h-m3/
_RESEARCH = os.path.dirname(os.path.dirname(_HM3))   # youra_research/

# Input
HE1_JSON = os.path.join(_RESEARCH, "h-e1", "experiment_results_phase3.json")

# Output
OUTPUT_DIR = _HM3
FIGURES_DIR = os.path.join(_HM3, "figures")
RESULTS_JSON = os.path.join(_HM3, "experiment_results_h_m3.json")
LOG_PATH = os.path.join(_HM3, "experiment.log")

# Dimension ordering (matches h-e1 rho_partial matrix column order)
DIMENSIONS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]
SAFETY_IDX = 1
ROBUSTNESS_IDX = 3
ETHICS_IDX = 5

# Predicted cluster membership for gate evaluation
PREDICTED_RLHF_SENSITIVE = {"safety", "machine_ethics"}
PREDICTED_RLHF_INSENSITIVE = {"robustness", "privacy"}

# Gate thresholds
PRIMARY_SILHOUETTE_THRESHOLD = 0.3   # Ward k=2 silhouette must exceed this
SECONDARY_ALIGNMENT_THRESHOLD = 4    # Out of 4 dimensions, must align >= this many

# Clustering
N_CLUSTERS = 2
RANDOM_SEED = 1
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Path + Constants | Write config.py with all constants above |

---

## A-7: Visualization (5 figures) [Complexity: 13, Budget: 1 subtask]

### Configuration (Hardcoded Constants — append to config.py)

```python
# Visualization settings
FIG_SIZE_DEFAULT = (8, 6)          # width x height inches
FIG_SIZE_HEATMAP = (7, 6)          # square-ish for 6x6 correlation heatmap
FIG_SIZE_DENDROGRAM = (8, 5)
FIG_SIZE_MDS = (7, 6)
FIG_DPI = 150

# Colormap
CMAP_DIVERGING = "RdBu_r"          # diverging: red=positive, blue=negative correlation
CMAP_CLUSTER = ["#2196F3", "#FF5722"]  # cluster 0 (RLHF-sensitive), cluster 1 (insensitive)

# Figure output filenames (joined with FIGURES_DIR in visualization.py)
FIG_GATE_METRICS = "gate_metrics.png"
FIG_DENDROGRAM = "dendrogram_ward.png"
FIG_RHO_HEATMAP = "rho_heatmap.png"
FIG_SILHOUETTE_COMPARISON = "silhouette_comparison.png"
FIG_MDS_PROJECTION = "mds_projection.png"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Viz Constants | Append figure size, DPI, colormap, filename constants to config.py |
