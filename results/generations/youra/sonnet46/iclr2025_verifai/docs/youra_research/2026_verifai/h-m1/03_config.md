# Configuration: H-M1 Pass@1 Coverage Verification

**Applied**: Standard hardcoded-constants pattern (no KB match — green-field for h-m1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-e1)
**Status**: config verified from actual h-e1 code (Serena project not active — used Read tool directly)
**Config Files Found**: `h-e1/code/src/h_e1/generate_solutions.py`, `h-e1/code/src/h_e1/evaluate_solutions.py`
**Pattern Used**: hardcoded dict / module-level constants (matches h-e1 pattern)

---

## Inherited Configuration (Base Hypothesis)

### Constants From Actual H-E1 Code

```python
# From: h-e1/code/src/h_e1/generate_solutions.py (ACTUAL CODE)
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

SEED: int = 42

# From: h-e1/code/src/h_e1/evaluate_solutions.py (ACTUAL CODE)
COVERAGE_MIN: float = 0.95  # used as COVERAGE_GATE in h-m1
```

**Verified from**: `h-e1/code/src/h_e1/generate_solutions.py` and `evaluate_solutions.py` (actual code)

**Note**: Architecture doc says `MODEL_SHORT_NAMES` is from `h_e1.evaluate_solutions`, but actual code shows it is defined in BOTH `generate_solutions.py` AND `evaluate_solutions.py` with identical values. Import from either works; prefer `h_e1.generate_solutions` for MODEL_IDS co-location.

---

## C-A7-1: Visualization Configuration Schema [Complexity: 9, Budget: 1]

**Applied**: Standard matplotlib constants pattern

```python
# src/h_m1/visualize_hm1.py — module-level constants

FIG_DPI: int = 150
COVERAGE_THRESHOLD: float = 0.95

# Coverage heatmap colormap
HEATMAP_CMAP: str = "RdYlGn"  # Non-standard: red=fail, green=pass semantics
HEATMAP_VMIN: float = 0.0
HEATMAP_VMAX: float = 1.0

# Coverage bar chart
THRESHOLD_LINE_COLOR: str = "red"
THRESHOLD_LINE_STYLE: str = "--"
THRESHOLD_LINE_WIDTH: float = 1.5

# Subplot layout for 3-model histogram figure
HIST_FIGURE_SIZE: tuple = (15, 5)   # 3 subplots side by side
HIST_N_COLS: int = 3
HIST_N_ROWS: int = 1
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A7-1 | Viz constants | FIG_DPI, colormap, threshold line, subplot layout |

---

## C-A7-2: Pass@1 Histogram Figure Parameters [Complexity: 10, Budget: 1]

**Applied**: Standard matplotlib bar/CDF defaults

```python
# src/h_m1/visualize_hm1.py — histogram + CDF constants

PASS_AT_1_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
PASS_AT_1_BIN_LABELS: list[str] = ["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"]

# Side-by-side bar color scheme (HumanEval+ vs MBPP+)
BAR_COLOR_HE: str = "steelblue"
BAR_COLOR_MBPP: str = "darkorange"
BAR_WIDTH: float = 0.35

# CDF plot styling (3 models overlaid)
CDF_LINESTYLES: list[str] = ["-", "--", "-."]
CDF_ALPHA: float = 0.85
CDF_LEGEND_LOC: str = "lower right"

# Figure size for CDF (single plot with 3 model lines x 2 benchmarks)
CDF_FIGURE_SIZE: tuple = (8, 5)
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A7-2 | Histogram/CDF params | Bin defs, bar colors, CDF linestyles |

---

## C-A2-1: Model Name Mapping Configuration [Complexity: 9, Budget: 1]

**Applied**: Constants-from-base pattern (verified from actual h-e1 code)

```python
# src/h_m1/verify_coverage.py — model and path constants

# Verified from h-e1/code/src/h_e1/generate_solutions.py
MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

# Verified from h-e1/code/src/h_e1/generate_solutions.py (same in evaluate_solutions.py)
MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

BENCHMARK_PREFIXES: dict[str, str] = {
    "HumanEval/": "humaneval",
    "Mbpp/": "mbpp",
}

# H-E1 results path (resolved relative to h-m1/code/ at runtime via argparse default)
DEFAULT_H_E1_RESULTS: str = "../../h-e1/results"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A2-1 | Model mapping | HF ID → short_name, h-e1 path resolution |

---

## C-A6-1: Coverage Threshold Configuration [Complexity: 9, Budget: 1]

**Applied**: Standard gate-constant pattern

```python
# src/h_m1/verify_coverage.py — coverage and benchmark constants

COVERAGE_GATE: float = 0.95

# Benchmark problem totals
HE_TOTAL: int = 164
MBPP_TOTAL: int = 378
COMBINED_TOTAL: int = 542   # HE_TOTAL + MBPP_TOTAL

BENCHMARK_TOTALS: dict[str, int] = {
    "humaneval": 164,
    "mbpp": 378,
    "combined": 542,
}

# Threshold line styling (for plot_coverage_rates)
GATE_LINE_COLOR: str = "red"
GATE_LINE_STYLE: str = "--"
GATE_LINE_LABEL: str = f"Gate ({COVERAGE_GATE:.0%})"

# Smoke test size
N_SMOKE: int = 10  # Non-standard: 10 per benchmark (h-e1 used 5; 10 covers both benchmarks minimally)
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A6-1 | Coverage constants | COVERAGE_GATE, benchmark totals, threshold styling |

---

*Generated by Configuration Agent — h-m1 config design*
*Base h-e1 field names verified from actual code: generate_solutions.py, evaluate_solutions.py*
*Date: 2026-03-18*
