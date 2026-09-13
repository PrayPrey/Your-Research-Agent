# Logic: h-m2

**Type**: MECHANISM (statistical log analysis, no neural network)
Applied: standard statsmodels/scipy McNemar test pattern (no KB match found — generic stats API).

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: N/A - statistical analysis, no existing code/base hypothesis to verify against
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Loader [Complexity: 4, Budget: 0 subtasks]

**Applied**: Standard JSONL line-parsing.

```python
def load_iteration_logs(path: str) -> list[dict]:
    """Read JSONL file into list of dicts."""
    ...

def filter_by_condition(logs: list[dict], condition: str) -> list[dict]:
    """condition: 'static_first' | 'exec_first'."""
    ...
```

Pseudo-code:
```
1. open path, readlines
2. for each line: json.loads(line) -> dict
3. return list[dict]

filter_by_condition:
1. return [log for log in logs if log["condition"] == condition]
```

---

## A-2: Regression Metrics [Complexity: 6, Budget: 0 subtasks]

**Applied**: Standard rate computation over log entries.

```python
def compute_regression_rate(logs: list[dict], condition: str) -> float:
    """(# passed@iter1 but failed@iter2) / (# passed@iter1). Returns 0.0 if denom=0."""
    ...

def per_iteration_pass_rate(logs: list[dict], condition: str) -> dict[str, float]:
    """Returns {'iteration_0': rate, 'iteration_1': rate, ...} pass rates."""
    ...
```

Pseudo-code:
```
compute_regression_rate(logs, condition):
1. subset = filter_by_condition(logs, condition)
2. passed_at_1 = [l for l in subset if l["iteration_1"]["passed"]]
3. if len(passed_at_1) == 0: return 0.0
4. regressed = [l for l in passed_at_1 if not l["iteration_2"]["passed"]]
5. return len(regressed) / len(passed_at_1)

per_iteration_pass_rate(logs, condition):
1. subset = filter_by_condition(logs, condition)
2. for each key in ["iteration_0","iteration_1","iteration_2","iteration_3"]:
     rate[key] = mean(l[key]["passed"] for l in subset)
3. return rate dict
```

---

## A-3: Contingency Table [Complexity: 5, Budget: 0 subtasks]

**Applied**: Standard 2x2 McNemar contingency table construction (paired by problem_id).

```python
def build_regression_contingency_table(logs: list[dict]) -> list[list[int]]:
    """2x2 table: rows=cascade regressed(Y/N), cols=reverse regressed(Y/N). Requires paired problem_ids across both conditions."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| table | [2, 2] | table[0][0]=both regressed, table[0][1]=cascade only, table[1][0]=reverse only, table[1][1]=neither |

Pseudo-code:
```
1. cascade_logs = filter_by_condition(logs, "static_first")
2. reverse_logs = filter_by_condition(logs, "exec_first")
3. build dict: problem_id -> regressed (bool) for cascade, for reverse
   (only include problems with passed@iter1 in that condition)
4. common_ids = intersection of both dicts' keys
5. for pid in common_ids:
     c = cascade_regressed[pid]; r = reverse_regressed[pid]
     table[int(c)][int(r)] += 1
6. return table  # [[n11,n10],[n01,n00]] per statsmodels convention
```

---

## A-4: McNemar Test [Complexity: 4, Budget: 0 subtasks]

**Applied**: statsmodels `mcnemar` exact test wrapper.

```python
def run_mcnemar(table: list[list[int]], exact: bool = True) -> tuple[float, float]:
    """Wraps statsmodels.stats.contingency_tables.mcnemar. Returns (statistic, p_value)."""
    ...
```

Pseudo-code:
```
1. from statsmodels.stats.contingency_tables import mcnemar
2. result = mcnemar(np.array(table), exact=exact)
3. return result.statistic, result.pvalue
```

---

## A-5: Mechanism Verification [Complexity: 3, Budget: 0 subtasks]

**Applied**: Simple threshold-based verdict logic (per FR-4).

```python
def verify_mechanism_h_m2(cascade_rate: float, reverse_rate: float, p_value: float) -> str:
    """Returns 'PASS' | 'PARTIAL' | 'FAIL'."""
    ...
```

Pseudo-code:
```
1. if cascade_rate < reverse_rate and p_value < 0.05: return "PASS"
2. elif cascade_rate < reverse_rate: return "PARTIAL"
3. else: return "FAIL"
```

---

## A-6: Visualization [Complexity: 6, Budget: 0 subtasks]

**Applied**: Standard matplotlib/seaborn bar chart, line plot, heatmap.

```python
def plot_regression_bar(cascade_rate: float, reverse_rate: float, out_path: str) -> None:
    """Bar chart: 2 bars (cascade, reverse) of regression rate."""
    ...

def plot_iteration_trajectory(rates_by_condition: dict[str, dict[str, float]], out_path: str) -> None:
    """Line plot: x=iteration, y=pass_rate, one line per condition."""
    ...

def plot_contingency_heatmap(table: list[list[int]], out_path: str) -> None:
    """seaborn.heatmap of 2x2 table with annotations."""
    ...
```

---

## A-7: Pipeline Entrypoint [Complexity: 5, Budget: 0 subtasks]

**Applied**: Standard script orchestration.

```python
def main() -> None: ...
```

Pseudo-code:
```
1. logs = load_iteration_logs("../h-e1/code/results/h-e1_iteration_logs.jsonl")
2. cascade_rate = compute_regression_rate(logs, "static_first")
3. reverse_rate = compute_regression_rate(logs, "exec_first")
4. table = build_regression_contingency_table(logs)
5. stat, p_value = run_mcnemar(table, exact=True)
6. verdict = verify_mechanism_h_m2(cascade_rate, reverse_rate, p_value)
7. rates_by_condition = {
     "static_first": per_iteration_pass_rate(logs, "static_first"),
     "exec_first": per_iteration_pass_rate(logs, "exec_first"),
   }
8. save results dict (rates, table, stat, p_value, verdict) -> results/h-m2_results.json
9. plot_regression_bar(cascade_rate, reverse_rate, "figures/regression_bar.png")
10. plot_iteration_trajectory(rates_by_condition, "figures/iteration_trajectory.png")
11. plot_contingency_heatmap(table, "figures/contingency_heatmap.png")
```
