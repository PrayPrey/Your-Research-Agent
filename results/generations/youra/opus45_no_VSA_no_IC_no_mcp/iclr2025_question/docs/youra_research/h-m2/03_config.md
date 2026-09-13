# Config: H-M2 (MECHANISM)

Applied: uncertainty-quantification-pipeline (statistical distribution comparison, consistent w/ h-e1)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: h-e1 config verified from actual code — uses hardcoded dict (not dataclass)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dict (hardcoded) — h-m2 follows same format for consistency

MECHANISM analysis-only PoC, all tasks Low complexity, 0 subtask budget — single flat config, no dataclass needed.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
CONFIG = {
    "SCORES_CSV": "outputs/scores.csv",   # columns: question_id, entropy, consistency, label
    "SEED": 42,
}
```

h-m2 does not import h-e1's CONFIG (separate process/pipeline) — only reads its output CSV. No inference/model/embedding fields needed since h-m2 does zero generation or labeling.

**Verified from**: `docs/youra_research/h-e1/code/config.py`

---

## B-1..B-7: Analysis Pipeline [Complexity: Low, Budget: 0 subtasks]

**Applied**: Standard PyTorch/pandas defaults; effect-size thresholds from PRD (Cohen's d, alpha)

### Configuration (Hardcoded Dict)

```python
"""Configuration for H-M2 MECHANISM analysis."""

CONFIG = {
    # Input (h-e1 artifact)
    "H_E1_SCORES_CSV": "../h-e1/outputs/scores.csv",  # question_id, entropy, consistency, label

    # Statistics
    "COHENS_D_THRESHOLD": 0.2,   # PRD success criterion: minimum effect size
    "ALPHA": 0.05,                # significance level for t-test

    # Output
    "OUTPUT_DIR": "outputs",
    "METRICS_JSON": "outputs/metrics.json",
    "FIGURES_DIR": "figures",
    "DIST_PLOT_PNG": "figures/distribution_comparison.png",
    "HIST_PLOT_PNG": "figures/histogram_overlay.png",
}
```

No subtasks required (0 budget, all Low complexity) — B-1 through B-7 map directly to `analysis.py`/`plots.py`/`run.py` functions per architecture, no further decomposition needed.
