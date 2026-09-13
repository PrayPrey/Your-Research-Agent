# Config: H-M4 (MECHANISM Validation)

**Applied**: No relevant KB pattern found (top hits: LaTeX knitting patterns, PyTorch inductor config, SDXL yaml — all unrelated, similarity <0.32). Using module-level constants, consistent with H-M3/H-E1 pattern noted in architecture.

## Codebase Analysis (Serena)

**Project Type**: green-field (no `h-m4/code/` yet; `h-m3/code/` also absent per architecture doc)
**Status**: Green-field — designing new config schema, no code to verify
**Config Files Found**: None
**Pattern Used**: Module-level constants (no dataclass/YAML needed — single fixed analysis config, not a training pipeline)

---

## A-1..A-9: Shared Pipeline Config [Complexity: N/A, Budget: 3 subtasks]

Single `config.py` module, no per-task variation — all tasks import shared constants.

### Configuration (Module Constants)

```python
# config.py

# --- Data scope ---
VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)  # 2018-2024 inclusive
SEED = 42

# --- Paths ---
PWC_CACHE = "pwc-archive/papers-with-abstracts"
E1_RESULTS_PATH = "h-e1/results/"
OUTPUT_DIR = "h-m4/results/"
FIGURES_DIR = "h-m4/figures/"

# --- Statistical thresholds ---
MIN_PAPERS_PER_VY = 10       # min papers per venue-year to include in aggregation
MIN_VENUE_YEARS_PER_VENUE = 3  # min venue-years required for per-venue Spearman
ALPHA = 0.05                  # significance threshold
MIN_VENUES_WITH_EFFECT = 2    # gate: effect required in >=2/3 venues

# --- Visualization ---
FIGSIZE_SCATTER = (8, 6)
FIGSIZE_BAR = (7, 5)
FIGSIZE_BOX = (7, 5)
DPI = 150
VENUE_COLORS = {"NeurIPS": "#1f77b4", "ICML": "#ff7f0e", "ICLR": "#2ca02c"}
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Create config.py | Write module constants above, no logic |
| C-2 | Wire into data_loader/variance | Import VENUES, YEARS, PWC_CACHE, E1_RESULTS_PATH, MIN_PAPERS_PER_VY where used |
| C-3 | Wire into analyze/visualize | Import ALPHA, MIN_VENUE_YEARS_PER_VENUE, MIN_VENUES_WITH_EFFECT, figure settings |
