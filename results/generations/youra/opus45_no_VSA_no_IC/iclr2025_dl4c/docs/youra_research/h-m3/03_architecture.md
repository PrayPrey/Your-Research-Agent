# Architecture: h-m3

**Hypothesis**: Unanimous scale agreement indicates ≥10% higher verdict reliability vs split verdicts
**Type**: Statistical analysis (no ML training)
**Applied**: Standard analysis-pipeline pattern (load → transform → compute → test → visualize → report)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Reads `h-e1/code/outputs/results.csv` as data input only (not code dependency), so no Serena inspection needed.

## Data Flow

```
results.csv (164 problems x 4 judges)
  -> DataLoader.load()               -> DataFrame
  -> AgreementClassifier.classify()  -> DataFrame + agreement_type col (unanimous/split)
  -> AccuracyCalculator.compute()    -> {unanimous: acc, split: acc, n_unanimous, n_split}
  -> StatTester.two_proportion_ztest() -> {z, p_value, ci, diff}
  -> Visualizer.plot()               -> figures/*.png
  -> ReportWriter.write()            -> report.md
```

## File Structure

```
h-m3/code/
  data_loader.py
  agreement.py
  accuracy.py
  stats_test.py
  visualize.py
  report.py
  run.py
  outputs/
    figures/
    report.md
    results.json
```

## Module Interfaces

### DataLoader (`data_loader.py`)

**Dependencies**: pandas

```python
def load_results(csv_path: str) -> pd.DataFrame:
    """Columns required: problem_id, judge_id, scale_verdict, correct (bool)"""
    ...
```

### AgreementClassifier (`agreement.py`)

**Dependencies**: pandas

```python
def classify_agreement(df: pd.DataFrame) -> pd.DataFrame:
    """Group by problem_id; label each problem 'unanimous' if all 4 judge
    scale_verdicts match, else 'split'. Returns per-problem DataFrame:
    columns [problem_id, agreement_type, correct]."""
    ...
```

### AccuracyCalculator (`accuracy.py`)

**Dependencies**: pandas

```python
def compute_accuracy(df: pd.DataFrame) -> dict:
    """df: per-problem DataFrame with agreement_type, correct.
    Returns {'unanimous': {'n': int, 'acc': float},
             'split': {'n': int, 'acc': float}}"""
    ...
```

### StatTester (`stats_test.py`)

**Dependencies**: scipy.stats, statsmodels (if already installed; else manual formula)

```python
def two_proportion_ztest(acc_stats: dict) -> dict:
    """Two-proportion z-test, unanimous vs split accuracy.
    Returns {'z': float, 'p_value': float, 'diff': float,
             'ci_95': (lo, hi), 'meets_10pct_threshold': bool}"""
    ...
```

### Visualizer (`visualize.py`)

**Dependencies**: matplotlib

```python
def plot_accuracy_comparison(acc_stats: dict, out_path: str) -> None:
    """Bar chart: unanimous vs split accuracy with error bars."""
    ...
```

### ReportWriter (`report.py`)

**Dependencies**: none (stdlib)

```python
def write_report(acc_stats: dict, test_result: dict, fig_paths: list[str], out_path: str) -> None:
    """Renders markdown summary: sample sizes, accuracies, z/p, verdict on hypothesis."""
    ...
```

### run.py (entrypoint)

```python
def main(csv_path: str, out_dir: str) -> None:
    """Wires all modules in sequence per Data Flow above."""
    ...
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Data loader | Load & validate results.csv | 5 | 1+1+1+2 |
| M3-2 | Agreement classifier | Group judges per problem, label unanimous/split | 7 | 2+1+2+2 |
| M3-3 | Accuracy calculator | Per-group accuracy + counts | 4 | 1+1+1+1 |
| M3-4 | Stat tester | Two-proportion z-test + CI | 8 | 2+2+3+1 |
| M3-5 | Visualizer | Bar chart w/ error bars | 5 | 1+1+2+1 |
| M3-6 | Report writer | Markdown report generation | 4 | 1+1+1+1 |
| M3-7 | Pipeline entrypoint | run.py wiring + CLI args | 5 | 1+2+1+1 |
| M3-8 | Self-check test | Synthetic data assert test for classifier + z-test | 6 | 2+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M3-1, M3-2, M3-3, M3-4, M3-5, M3-6, M3-7, M3-8]

skipped: no ML/training modules, no config framework (single run.py CLI covers it) — add config.py only if multiple experiment variants emerge.
