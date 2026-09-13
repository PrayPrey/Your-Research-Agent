---
hypothesis_id: h-m3
phase: config
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
base_hypothesis: h-m2
---

# Configuration: H-M3 — SelfCheckGPT BERTScore Uncertainty Estimation

Applied: inference-only-fixed-config pattern (no training, no grid search)
Applied: inherited-base-config pattern (reuse H-M2 seed, K, n_bootstrap, delta_auroc_gate, paths)

---

## Codebase Analysis (Serena)

**Project Type**: green-field (new files in h-m3/code/)
**Status**: Serena MCP not available. h-m2/03_config.md reviewed as source of truth for inherited fields.
**Config Files Found**: `h-m2/03_config.md` (spec), `h-e1/code/run.py` (upstream source)
**Pattern Used**: dataclass (single fixed config, inference-only)

---

## Inherited Configuration (Base Hypothesis)

Fields inherited from H-M2 (verified from h-m2/03_config.md):

```python
# From: h-m2/03_config.md (actual config.py template)
# Inherited values (unchanged):
#   K: 10
#   seed: 42
#   n_bootstrap: 1000
#   n_questions: 98
#   delta_auroc_gate: 0.03
#   he1_code_dir: "../../h-e1/code"
#   figures_dir: "../figures"
#   results_path: "../results.json"
```

Dropped from H-M2 (not needed in H-M3):
- `entailment_threshold` — NLI clustering not used in SCG BERTScore path
- `nli_model_name` — not used
- `hm1_code_dir` — H-M3 imports from h-m2, not h-m1
- `paraphrase_subset_size` — ablation not repeated

---

## Full Config (copy-paste into h-m3/code/config.py)

```python
from dataclasses import dataclass

@dataclass
class Config:
    # --- Inherited from H-E1/H-M2 ---
    K: int = 10
    seed: int = 42
    n_bootstrap: int = 1000
    n_questions: int = 98
    delta_auroc_gate: float = 0.03

    # --- Paths ---
    he1_code_dir: str = "../../h-e1/code"
    hm2_code_dir: str = "../../h-m2/code"
    he1_results_path: str = "../../h-e1/results.json"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"

    # --- H-M3 specific: SCG BERTScore ---
    bertscore_model: str = "microsoft/deberta-xlarge-mnli"
    rescale_with_baseline: bool = True
```

Non-standard rationale:
- `bertscore_model`: DeBERTa-XL chosen for highest BERTScore F1 correlation with human judgements (Zhang et al. 2020 leaderboard); standard BERT-base understimates semantic similarity on QA outputs.
- `rescale_with_baseline`: recommended default in BERTScore paper to normalize scores to [0,1] range; without it SCG scores cluster near 0.85–0.95 making distribution plots unreadable.
- `delta_auroc_gate = 0.03`: inherited from H-M2; non-standard — minimum AUROC delta to claim mechanism activation above noise floor.

---

## YAML Experiment Config Equivalent

```yaml
hypothesis_id: h-m3
K: 10
seed: 42
n_bootstrap: 1000
n_questions: 98
delta_auroc_gate: 0.03

paths:
  he1_code_dir: "../../h-e1/code"
  hm2_code_dir: "../../h-m2/code"
  he1_results_path: "../../h-e1/results.json"
  figures_dir: "../figures"
  results_path: "../results.json"

scg:
  bertscore_model: "microsoft/deberta-xlarge-mnli"
  rescale_with_baseline: true
```

---

## A-6: Visualization Config [Complexity: 2, Budget: 2 subtasks]

Applied: shared-figure-defaults pattern (one FigureConfig, per-figure overrides as needed)

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure layout config | figsize, dpi, font sizes, bar width, CI cap size per figure type |
| C-6-2 | Color and style schema | Method color assignments, bar/scatter/ROC style params |

---

### C-6-1: Figure Layout Configuration (copy-paste into h-m3/code/visualize.py)

```python
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class FigureConfig:
    # Shared defaults
    dpi: int = 150
    font_size: int = 11
    title_size: int = 13
    label_size: int = 11
    tick_size: int = 9
    legend_size: int = 9

    # Bar chart (auroc_comparison.png)
    bar_figsize: Tuple[float, float] = (6.0, 4.5)
    bar_width: float = 0.5
    ci_cap_size: float = 4.0       # error bar cap width in points

    # Distribution (scg_score_distribution.png)
    dist_figsize: Tuple[float, float] = (7.0, 4.5)
    dist_bins: int = 30

    # Scatter (scg_vs_se_scatter.png)
    scatter_figsize: Tuple[float, float] = (5.5, 5.5)

    # ROC curves (roc_curves.png)
    roc_figsize: Tuple[float, float] = (6.0, 5.5)
```

---

### C-6-2: Color and Style Schema (copy-paste into h-m3/code/visualize.py)

```python
# Method color assignments — consistent across all 4 figures
METHOD_COLORS = {
    "SCG": "#2196F3",   # blue
    "SE":  "#FF9800",   # orange
    "TE":  "#4CAF50",   # green
}

# Correctness split (distribution plot)
CORRECTNESS_COLORS = {
    "correct":   "#4CAF50",   # green
    "incorrect": "#F44336",   # red
}

# Bar chart style
BAR_STYLE = {
    "alpha": 0.85,
    "edgecolor": "white",
    "linewidth": 0.8,
    "error_kw": {"elinewidth": 1.5, "ecolor": "black", "capthick": 1.5},
}

# Distribution (KDE + histogram)
DIST_STYLE = {
    "hist_alpha": 0.35,
    "kde_linewidth": 2.0,
}

# Scatter
SCATTER_STYLE = {
    "marker": "o",
    "s": 30,            # marker size
    "alpha": 0.55,
    "edgecolors": "none",
}

# ROC curves
ROC_STYLE = {
    "SCG": {"linewidth": 2.0, "linestyle": "-"},
    "SE":  {"linewidth": 2.0, "linestyle": "--"},
    "TE":  {"linewidth": 2.0, "linestyle": "-."},
    "chance": {"linewidth": 1.0, "linestyle": ":", "color": "grey", "alpha": 0.7},
}
```

---

## Environment Requirements

```
python>=3.9
torch>=2.0
transformers>=4.38
bert-score>=0.3.13
scikit-learn>=1.3
matplotlib>=3.7
seaborn>=0.13
numpy>=1.24
```

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included
