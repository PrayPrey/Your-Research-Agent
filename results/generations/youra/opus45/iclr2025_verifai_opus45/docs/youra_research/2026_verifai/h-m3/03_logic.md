# Logic: H-M3 Non-Monotonicity Confirmation (G3 >= G4)

**Date:** 2026-03-30
**Hypothesis:** G4 (full trace) does not significantly outperform G3 (G4 <= G3 + 2%)
**Type:** MECHANISM (Statistical Reanalysis)
**Gate:** SHOULD_WORK

Applied: statistical-reanalysis-minimal-pipeline

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified via direct file read (Serena no active project; Read tool used)
**Analyzed Path**: `docs/youra_research/20260330_verifai/h-m1/code/repair.py`, `analyze.py`
**Relevant Symbols**:
- `run_repair_experiment()` in `repair.py` line 63: returns `list[dict]` with fields `task_id`, `granularity`, `repaired_code`, `success`, `execution_time`
- `aggregate_by_granularity()` in `analyze.py` lines 13-17: accesses `r["granularity"]` and `r["success"]`
- Checkpoint/results JSON written by `save_checkpoint()` to `results/repair_results.json`

---

## External Dependencies API

### Data Format from H-M1 (Verified from actual code)

```python
# From: h-m1/code/repair.py line 63 — ACTUAL return schema
# Each element of repair_results.json:
{
    "task_id": int,           # MBPP problem ID (int key for pairing)
    "granularity": str,       # "G0" | "G1" | "G2" | "G3" | "G4"
    "repaired_code": str,     # Generated repair string
    "success": bool,          # True = repair passed all tests
    "execution_time": float,  # Seconds
}

# From: h-m1/code/analyze.py — field access pattern (confirmed)
granularity = r["granularity"]  # str
success = r["success"]          # bool (cast bool() when loading from JSON)
task_id = r["task_id"]          # int
```

**Results path**: `h-m1/code/results/repair_results.json`
**Verified from**: `h-m1/code/repair.py` (actual return type comment, line 63)

---

## A-5: TOST Equivalence Test [Complexity: 9, Budget: 2 subtasks]

Applied: two-one-sided-tests proportion z-test

### API Signatures

```python
# statistics.py
import numpy as np
import scipy.stats as stats
from statsmodels.stats.contingency_tables import mcnemar as statsmodels_mcnemar


def build_contingency_table(g3: list[bool], g4: list[bool]) -> np.ndarray:
    """Build 2x2 McNemar table from paired boolean outcomes. Returns shape (2, 2)."""
    # rows=G3 (0=fail,1=success), cols=G4 (0=fail,1=success)
    # [0,0]=both_success, [0,1]=G3only, [1,0]=G4only, [1,1]=both_fail


def run_mcnemar_test(table: np.ndarray) -> dict:
    """Exact McNemar binomial test. table: (2, 2) -> result dict."""


def run_tost_equivalence(
    g3_successes: int,
    g3_total: int,
    g4_successes: int,
    g4_total: int,
    margin: float = 0.02,
    alpha: float = 0.05,
) -> dict:
    """TOST for proportion equivalence within ±margin.

    H0_lower: diff <= -margin | H0_upper: diff >= +margin
    equivalent iff both one-sided tests reject at alpha.
    """


def compute_confidence_interval(
    g3_successes: int,
    g3_total: int,
    g4_successes: int,
    g4_total: int,
    confidence: float = 0.95,
) -> dict:
    """95% CI for G4-G3 difference, unpooled SE, normal approximation."""
```

### Return Schemas

```python
# run_mcnemar_test -> dict
{"statistic": float, "pvalue": float, "significant": bool, "interpretation": str}

# run_tost_equivalence -> dict
{
    "g3_rate": float, "g4_rate": float, "difference": float,
    "margin": float,  # 0.02
    "p_lower": float, "p_upper": float,
    "tost_pvalue": float,  # max(p_lower, p_upper)
    "equivalent": bool, "interpretation": str,
}

# compute_confidence_interval -> dict
{
    "point_estimate": float,  # G4 - G3
    "ci_lower": float, "ci_upper": float,
    "confidence": float, "interpretation": str,
}
```

### Pseudo-code: run_tost_equivalence

```
1. g3_rate = g3_successes / g3_total
   g4_rate = g4_successes / g4_total
   diff = g4_rate - g3_rate

2. se = sqrt(g3_rate*(1-g3_rate)/g3_total + g4_rate*(1-g4_rate)/g4_total)
   if se == 0: return equivalent=False, difference=diff  # degenerate guard

3. # Lower one-sided: H0: diff <= -margin  (G4 much worse)
   z_lower = (diff - (-margin)) / se
   p_lower = 1 - norm.cdf(z_lower)

4. # Upper one-sided: H0: diff >= +margin  (G4 much better)
   z_upper = (diff - margin) / se
   p_upper = norm.cdf(z_upper)

5. equivalent = (p_lower < alpha) AND (p_upper < alpha)
   tost_pvalue = max(p_lower, p_upper)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | TOST z-test | `run_tost_equivalence`: two one-sided z-tests, SE guard, equivalence flag |
| L-5-2 | McNemar + CI | `run_mcnemar_test` (statsmodels exact), `compute_confidence_interval` (unpooled SE) |

---

## All Other Modules (Low/Medium Complexity)

### API Signatures

```python
# config.py
from dataclasses import dataclass

@dataclass
class AnalysisConfig:
    h_m1_results_path: str = "../h-m1/code/results/repair_results.json"
    equivalence_margin: float = 0.02
    alpha: float = 0.05
    confidence: float = 0.95
    results_dir: str = "results"
    figures_dir: str = "figures"
    output_contingency: str = "results/contingency_table.json"
    output_stats: str = "results/statistical_tests.yaml"
    output_metrics: str = "results/metrics.yaml"


# data_loader.py
def load_h_m1_results(path: str) -> list[dict]:
    """Load repair_results.json. Raises FileNotFoundError with hint if missing."""

def extract_paired_outcomes(
    results: list[dict],
) -> tuple[list[bool], list[bool], list[int]]:
    """Pair G3/G4 by task_id. Returns (g3_outcomes, g4_outcomes, problem_ids)."""

def validate_data_integrity(
    g3_outcomes: list[bool],
    g4_outcomes: list[bool],
    problem_ids: list[int],
) -> dict:
    """Returns {n_pairs: int, g3_count: int, g4_count: int, valid: bool}."""


# evaluate.py
def evaluate_gate_condition(
    g3_rate: float,
    g4_rate: float,
    mcnemar_pvalue: float,
    margin: float = 0.02,
) -> dict:
    """H-M3 gate. Returns {g3_rate, g4_rate, difference, within_margin, gate_passed, reason}."""

def save_results(
    contingency_table: "np.ndarray",
    mcnemar_result: dict,
    tost_result: dict,
    ci_result: dict,
    gate_result: dict,
    cfg: AnalysisConfig,
) -> None:
    """Write contingency_table.json, statistical_tests.yaml, metrics.yaml."""


# visualize.py
def plot_gate_comparison(
    g3_rate: float, g4_rate: float, margin: float, output_path: str
) -> None:
    """Bar chart G3 vs G4 with G3+2% threshold line. MANDATORY figure."""

def plot_contingency_heatmap(table: "np.ndarray", output_path: str) -> None:
    """2x2 seaborn heatmap of paired outcomes."""

def plot_confidence_interval(ci_result: dict, output_path: str) -> None:
    """Point estimate + 95% CI for G4-G3 diff with ±margin reference lines."""

def plot_granularity_curve(results: list[dict], output_path: str) -> None:
    """G0-G4 success rates line chart showing non-monotonic pattern."""

def generate_all_figures(
    g3_rate: float,
    g4_rate: float,
    table: "np.ndarray",
    ci_result: dict,
    results: list[dict],
    cfg: AnalysisConfig,
) -> None:
    """Orchestrate all 4 figures to cfg.figures_dir."""


# train.py
def run_analysis(cfg: AnalysisConfig) -> dict:
    """Pipeline: load->extract->validate->stats->gate->save->visualize.
    Returns gate_result dict (gate_passed: bool, reason: str, g3_rate, g4_rate)."""
```

### Gate Logic (evaluate_gate_condition)

```
if mcnemar_pvalue < 0.05 AND g4_rate > g3_rate:
    gate_passed = False   # FAIL: G4 significantly outperforms G3
elif mcnemar_pvalue < 0.05 AND g3_rate >= g4_rate:
    gate_passed = True    # PASS: G3 significantly superior
else:  # p >= 0.05
    gate_passed = True    # PASS: no significant difference
```

---

## Output Files

| File | Content |
|------|---------|
| `results/contingency_table.json` | 2x2 table as nested list + cell labels |
| `results/statistical_tests.yaml` | McNemar + TOST + CI results with timestamps |
| `results/metrics.yaml` | Gate evaluation (gate_passed, reason, rates, diff) |
| `figures/gate_comparison.png` | MANDATORY: bar chart with 2% margin threshold |
| `figures/contingency_heatmap.png` | 2x2 paired outcome matrix |
| `figures/confidence_interval.png` | 95% CI for G4-G3 difference |
| `figures/granularity_curve.png` | G0-G4 success rates (non-monotonic) |
