# Logic Design: H-M2 - G3 Superiority Over Minimal Feedback

**Date:** 2026-03-30
**Hypothesis Type:** MECHANISM (Post-hoc Statistical Analysis)
**Applied:** paired-comparison-statistical-analysis pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** data structure verified
**Analyzed Path:** `docs/youra_research/20260330_verifai/h-m1/results/`
**Findings:** H-M1 repair_results.json contains list of records with fields: `task_id` (int), `granularity` (str: G0-G4), `success` (bool), `repaired_code` (str), `execution_time` (float). Total 1520 records (304 cases x 5 granularity levels).

---

## External Dependencies API

### Data Loading from H-M1

**Source:** `h-m1/results/repair_results.json`

**Schema (verified from actual data):**
```python
RepairRecord = TypedDict('RepairRecord', {
    'task_id': int,           # MBPP problem ID
    'granularity': str,       # "G0", "G1", "G2", "G3", "G4"
    'success': bool,          # True if repair passed all tests
    'repaired_code': str,     # LLM-generated repair
    'execution_time': float   # Seconds
})
```

---

## API Specifications

### Module: `stats.py`

#### `build_contingency_table`

```python
def build_contingency_table(g0_outcomes: list[int], g3_outcomes: list[int]) -> np.ndarray:
    """Build 2x2 contingency table for McNemar's test.
    
    Returns: np.ndarray shape (2, 2) - table[i,j] = count where G0=i and G3=j
    """
```

#### `run_mcnemar_test`

```python
def run_mcnemar_test(table: np.ndarray) -> dict:
    """Run McNemar's exact test. Returns: statistic, pvalue, discordant_b, discordant_c, favors"""
```

#### `calculate_rates_and_difference`

```python
def calculate_rates_and_difference(g0_outcomes: list[int], g3_outcomes: list[int]) -> dict:
    """Calculate success rates and difference with 95% CI.
    Returns: g0_rate, g3_rate, difference, difference_pp, ci_lower_pp, ci_upper_pp"""
```

#### `evaluate_gate`

```python
def evaluate_gate(rates: dict, mcnemar_result: dict, threshold: float = 0.10) -> dict:
    """Evaluate H-M2 gate: G3 >= G0 + 10pp AND McNemar p < 0.05 favoring G3.
    Returns: gate_passed, verdict, reason"""
```

### Module: `analyze.py`

#### `load_paired_results`

```python
def load_paired_results(results_path: str) -> tuple[list[int], list[int]]:
    """Load G0/G3 paired outcomes from H-M1. Returns (g0_outcomes, g3_outcomes)"""
```

#### `main`

```python
def main(config: Config) -> dict:
    """Orchestrate full analysis: load -> stats -> gate -> visualize -> save"""
```

### Module: `visualize.py`

```python
def plot_comparison(rates: dict, output_dir: str) -> str: ...
def plot_contingency_heatmap(table: np.ndarray, output_dir: str) -> str: ...
def plot_difference_ci(rates: dict, output_dir: str) -> str: ...
def plot_gate_summary(rates: dict, gate: dict, output_dir: str) -> str: ...
```

---

## Subtasks

| ID | Task | Complexity |
|----|------|------------|
| A-3.1 | Core Statistical Functions (contingency, McNemar) | 5 |
| A-3.2 | Rate Calculation and Gate Logic | 5 |

---

## Expected Results

| Metric | Expected Value |
|--------|----------------|
| G0 Success Rate | 41.8% (127/304) |
| G3 Success Rate | 16.8% (51/304) |
| Difference (G3-G0) | -25.0pp |
| McNemar p-value | << 0.001 |
| Gate Result | **FAIL** |

---

*Generated for Phase 3 Implementation Planning*
