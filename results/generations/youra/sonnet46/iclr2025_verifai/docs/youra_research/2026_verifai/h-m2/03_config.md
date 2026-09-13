# Configuration: H-M2 Difficulty Tier Stratification — Cross-Model Jaccard Analysis

**Hypothesis:** h-m2
**Type:** MECHANISM (SHOULD_WORK gate)
**Date:** 2026-03-18

Applied: flat-constants pattern (hardcoded module-level constants, matching h-m1 style)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config constants verified from actual h-m1 code (direct file reads; Serena project connection unavailable)
**Config Files Found:** `h-m1/code/src/h_m1/verify_coverage.py`, `h-m1/code/src/h_m1/visualize_hm1.py`, `h-m1/code/src/h_m1/run_hm1_verification.py`
**Pattern Used:** Flat module-level constants (no dataclass — consistent with h-m1)

---

## Inherited Configuration (Base Hypothesis)

### Constants from Actual h-m1 Code

```python
# From: h-m1/code/src/h_m1/verify_coverage.py (ACTUAL CODE — verified field names)
COVERAGE_GATE: float = 0.95
HE_TOTAL: int = 164
MBPP_TOTAL: int = 378
COMBINED_TOTAL: int = 542

BENCHMARK_PREFIXES: dict[str, str] = {
    "HumanEval/": "humaneval",
    "Mbpp/": "mbpp",
}

MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

HIST_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# From: h-m1/code/src/h_m1/visualize_hm1.py (ACTUAL CODE)
FIG_DPI: int = 150
THRESHOLD_LINE_COLOR: str = "red"
THRESHOLD_LINE_STYLE: str = "--"
THRESHOLD_LINE_WIDTH: float = 1.5
HEATMAP_CMAP: str = "RdYlGn"

# From: h-m1/code/src/h_m1/run_hm1_verification.py (ACTUAL CODE)
DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"
# Note: h-m1 uses --h_e1_results_dir; h-m2 equivalent is --hm1_results_dir
```

**Verified from:** `h-m1/code/src/h_m1/` (actual implementation, not specs)

---

## A-7: Visualization [Complexity: 12, Budget: 1 subtask]

Applied: flat-constants pattern

### Configuration (`h-m2/code/src/h_m2/visualize_hm2.py`)

```python
import matplotlib
matplotlib.use("Agg")

# Figure output
FIG_DPI: int = 150                          # Inherited from h-m1 visualize_hm1.py

# Tier color mapping
TIER_COLORS: dict[str, str] = {
    "hard": "red",
    "medium": "gray",
    "easy": "green",
}

# Jaccard threshold line (jaccard bar chart + heatmap)
JACCARD_THRESHOLD_COLOR: str = "red"
JACCARD_THRESHOLD_STYLE: str = "--"
JACCARD_THRESHOLD_WIDTH: float = 1.5       # Inherited from h-m1 THRESHOLD_LINE_WIDTH

# Heatmap colormap (Jaccard similarity matrix — 0=white, 1=dark blue)
JACCARD_HEATMAP_CMAP: str = "Blues"        # Non-standard: diverges from h-m1 RdYlGn; Blues suits similarity matrix

# Pass@1 histogram subplot grid (3 models x 2 benchmarks)
HIST_FIGURE_SIZE: tuple = (18, 8)          # Non-standard: wider than h-m1 (15,5) to fit 3x2 grid
HIST_N_ROWS: int = 3
HIST_N_COLS: int = 2

# Tier size stacked bar layout
TIER_STACK_FIGURE_SIZE: tuple = (12, 6)

# Jaccard bar chart layout
JACCARD_BAR_FIGURE_SIZE: tuple = (8, 5)

# Pie chart layout
PIE_FIGURE_SIZE: tuple = (6, 6)
PIE_COLORS: list[str] = ["#d62728", "#ff7f0e", "#2ca02c"]  # 1/3, 2/3, 3/3 models hard
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Visualization Config | All figure constants: DPI, tier colors, layout sizes, colormaps for 5 plot functions |

---

## A-8: CLI Orchestrator [Complexity: 11, Budget: 1 subtask]

Applied: flat-constants pattern (matching h-m1 run_hm1_verification.py)

### Configuration (`h-m2/code/src/h_m2/run_hm2_stratification.py`)

```python
# Default paths (argparse defaults)
DEFAULT_HM1_RESULTS: str = "../../h-m1/results"
DEFAULT_OUTPUT_DIR: str = "results"           # Inherited from h-m1 DEFAULT_OUTPUT_DIR
DEFAULT_FIGURES_DIR: str = "figures"          # Inherited from h-m1 DEFAULT_FIGURES_DIR

# Output filenames
RESULTS_FILENAME: str = "stratification_results.json"
TIER_CSV_FILENAME: str = "tier_assignments.csv"

# Figure filenames
FIG_JACCARD_BARS: str = "jaccard_similarity_bars.png"
FIG_HISTOGRAMS: str = "pass_at_1_histograms.png"
FIG_TIER_SUMMARY: str = "tier_size_summary.png"
FIG_HEATMAP: str = "jaccard_heatmap.png"
FIG_PIE: str = "consensus_hard_pie.png"

# Exit codes
EXIT_PASS: int = 0
EXIT_FAIL: int = 1
EXIT_ERROR: int = 2
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | CLI Config | argparse defaults, output filenames, figure filenames, exit codes |

---

## A-9: Unit Tests [Complexity: 9, Budget: 1 subtask]

Applied: flat-constants pattern (test fixtures as module-level dicts)

### Configuration (`h-m2/code/tests/`)

```python
# ── Test fixtures for test_jaccard.py ──────────────────────────────────────────

# Known Jaccard results for validation
FIXTURE_SET_A = {"t1", "t2", "t3", "t4"}
FIXTURE_SET_B = {"t3", "t4", "t5", "t6"}
FIXTURE_SET_EMPTY = set()

EXPECTED_JACCARD_AB: float = 0.333   # |{t3,t4}| / |{t1,t2,t3,t4,t5,t6}| = 2/6
EXPECTED_JACCARD_EMPTY: float = 0.0   # both-empty edge case → 0.0
EXPECTED_JACCARD_IDENTICAL: float = 1.0

# Known cross-model Jaccard fixture (3 models, minimal hard sets)
FIXTURE_TIERS_3MODEL = {
    "model_a": {"hard": {"p1", "p2", "p3"}, "easy": {"p7", "p8"}, "medium": set()},
    "model_b": {"hard": {"p2", "p3", "p4"}, "easy": {"p8", "p9"}, "medium": set()},
    "model_c": {"hard": {"p3", "p4", "p5"}, "easy": {"p9", "p10"}, "medium": set()},
}
# Expected pairs: (a,b)=2/4=0.5, (a,c)=1/5=0.2, (b,c)=2/4=0.5

# ── Test fixtures for test_stratify.py ─────────────────────────────────────────

# Minimal pass@1 data for tier assignment tests
FIXTURE_PASS_AT_1_SIMPLE = {
    "model_x": {
        "Mbpp/1": 0.0,   # → hard
        "Mbpp/2": 0.2,   # → medium
        "Mbpp/3": 0.6,   # → easy
        "Mbpp/4": 1.0,   # → easy
        "Mbpp/5": 0.0,   # → hard
    }
}
EXPECTED_HARD_SIMPLE = {"Mbpp/1", "Mbpp/5"}
EXPECTED_EASY_SIMPLE = {"Mbpp/3", "Mbpp/4"}
EXPECTED_MEDIUM_SIMPLE = {"Mbpp/2"}

# ── Test fixtures for test_evaluate.py ─────────────────────────────────────────

JACCARD_GATE_THRESHOLD: float = 0.3   # Must match evaluate.JACCARD_GATE_THRESHOLD

# Gate PASS fixture: one pair above threshold
FIXTURE_JACCARD_PASS = {
    ("model_a", "model_b"): 0.45,
    ("model_a", "model_c"): 0.20,
    ("model_b", "model_c"): 0.15,
}
EXPECTED_GATE_PASS: bool = True
EXPECTED_PASSING_PAIRS_COUNT: int = 1

# Gate FAIL fixture: all pairs at or below threshold
FIXTURE_JACCARD_FAIL = {
    ("model_a", "model_b"): 0.25,
    ("model_a", "model_c"): 0.10,
    ("model_b", "model_c"): 0.30,   # 0.30 is NOT > 0.3 (strict greater-than)
}
EXPECTED_GATE_FAIL: bool = False
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Test Fixtures Config | Jaccard fixtures with known expected values, tier assignment fixtures, gate PASS/FAIL fixtures |

---

## Global Constants Summary

All h-m2 modules use flat module-level constants (no dataclass). Key values:

| Constant | Value | Module |
|----------|-------|--------|
| `HARD_THRESHOLD` | `0.0` | `stratify.py` |
| `EASY_THRESHOLD` | `0.6` | `stratify.py` |
| `JACCARD_GATE_THRESHOLD` | `0.3` | `evaluate.py` |
| `FIG_DPI` | `150` | `visualize_hm2.py` |
| `TIER_COLORS["hard"]` | `"red"` | `visualize_hm2.py` |
| `TIER_COLORS["medium"]` | `"gray"` | `visualize_hm2.py` |
| `TIER_COLORS["easy"]` | `"green"` | `visualize_hm2.py` |
| `DEFAULT_HM1_RESULTS` | `"../../h-m1/results"` | `run_hm2_stratification.py` |
| `MODEL_IDS` | 3 HF IDs (reuse from h-m1) | `stratify.py` |
| `COMBINED_TOTAL` | `542` | `stratify.py` |
| `MIN_TIER_SIZE` | `20` | `stratify.py` |

---

*Config generated: 2026-03-18*
*Base hypothesis constants verified from: h-m1/code/src/h_m1/verify_coverage.py, visualize_hm1.py, run_hm1_verification.py*
