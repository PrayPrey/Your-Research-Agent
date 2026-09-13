# Config: H-E1

**Type:** EXISTENCE (PoC) — statistical meta-analysis, no model training
**Applied:** No relevant KB config pattern found (low similarity results); used architecture's module-level constants convention (green-field DS pipeline).

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - new config design
**Config Files Found:** None - new config
**Pattern Used:** Module-level constants (not dataclass) — matches architecture.md `config.py` spec exactly

---

## A-1..A-5: Global Config [Complexity: N/A, Budget: 1 subtask]

**Applied:** Fixed single config, no hyperparameter grid (EXISTENCE rule — statistical PoC, no tuning/seeds needed since Spearman correlation is deterministic).

### Configuration (`code/config.py`)

```python
"""Fixed constants for H-E1 benchmark correlation analysis."""

# Data source
DATA_SOURCE = "open-llm-leaderboard/results"
BENCHMARKS = ["truthfulqa", "halueval", "factscore"]
BASELINE_PAIR = ("mmlu_physics", "halueval")

# Data quality thresholds (FR-1.1, NFR-3)
MIN_MODELS = 30

# Hypothesis gate threshold (FR-2.3)
CORR_UPPER_BOUND = 0.7

# Statistical validation (FR-3.2, FR-3.3)
ALPHA = 0.05
CI_LEVEL = 0.95

# Output paths
FIGURES_DIR = "figures/"
RESULTS_DIR = "results/"
```

No dataclass needed — all values are fixed constants per architecture spec, no variation/sweep for PoC gate test.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-CFG-1 | config.py | Write constants module exactly as specified above |
