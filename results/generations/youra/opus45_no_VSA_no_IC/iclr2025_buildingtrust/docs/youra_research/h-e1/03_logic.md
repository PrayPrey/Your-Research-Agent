# Logic: H-E1

**Type:** EXISTENCE (PoC) — statistical meta-analysis, no tensors/model training

---

## Codebase Analysis (Serena)

**Project Type**: Green-field project - no existing code to analyze
**Status**: N/A
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Pipeline [Complexity: 10, Budget: 10]

**Applied**: Standard PyTorch/DS convention (no relevant KB pattern found; scipy/pandas stdlib usage)

### API Signatures

```python
import pandas as pd

def fetch_leaderboard_scores() -> pd.DataFrame:
    """Query HF Open LLM Leaderboard API. Returns raw per-model scores."""
    ...

def filter_complete_models(df: pd.DataFrame, min_models: int) -> pd.DataFrame:
    """Listwise-delete rows missing any of the 4 benchmark scores. Assert len(df) >= min_models."""
    ...

def load_benchmark_scores() -> pd.DataFrame:
    """fetch_leaderboard_scores -> filter_complete_models(min_models=MIN_MODELS)."""
    ...
```

### DataFrame Schema

| Column | dtype | Note |
|--------|-------|------|
| model | str | model id/name |
| truthfulqa | float | MC2 accuracy, 0-1 |
| halueval | float | recognition accuracy, 0-1 |
| factscore | float | factual precision, 0-1 |
| mmlu_physics | float | baseline accuracy, 0-1 |
| arch | str | llama/mistral/falcon/phi/qwen |
| scale | str | e.g. "7B", "70B" |
| variant | str | base/instruct/rlhf/dpo |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | fetch_leaderboard_scores | HF API call, parse into flat DataFrame per schema |
| L-A1-2 | filter_complete_models | dropna on benchmark cols, assert min_models |
| L-A1-3 | load_benchmark_scores | wire fetch + filter |
| L-A1-4 | diversity check | verify arch/scale/variant coverage (log only, no hard gate) |

---

## A-2: Correlation Analyzer [Complexity: 8, Budget: 8]

**Applied**: scipy.stats.spearmanr (stdlib-equivalent, standard pattern)

### API Signatures

```python
from scipy import stats

class BenchmarkCorrelationAnalyzer:
    def __init__(self, benchmark_scores: pd.DataFrame):
        """benchmark_scores: output of load_benchmark_scores()."""
        self.scores = benchmark_scores
        self.benchmarks = ["truthfulqa", "halueval", "factscore"]  # cross-benchmark set

    def compute_correlation_matrix(self) -> pd.DataFrame:
        """Spearman r for all pairs in self.benchmarks. Returns 3x3 symmetric DataFrame."""
        ...

    def compute_baseline_correlation(self) -> float:
        """r(mmlu_physics, halueval) via config.BASELINE_PAIR."""
        ...

    def evaluate_hypothesis(self) -> dict:
        """
        Returns {
          "passed": bool,
          "correlations": dict[str, float],   # {"truthfulqa-halueval": r, ...}
          "baseline_r": float,
          "threshold_upper": float,           # config.CORR_UPPER_BOUND
          "pvalues": dict[str, float],
          "ci": dict[str, tuple[float, float]],
        }
        """
        ...
```

### Algorithm (evaluate_hypothesis)

```
1. corr_matrix = compute_correlation_matrix()
2. baseline_r = compute_baseline_correlation()
3. pvalues = compute_pvalues()
4. adj_pvalues = apply_bonferroni(pvalues)
5. ci = compute_confidence_intervals()
6. passed = all(baseline_r < r < CORR_UPPER_BOUND for r in pairwise correlations from corr_matrix, excluding diagonal)
7. return dict with all above
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | compute_correlation_matrix | pairwise scipy.stats.spearmanr over 3 benchmarks |
| L-A2-2 | compute_baseline_correlation | spearmanr on BASELINE_PAIR columns |
| L-A2-3 | evaluate_hypothesis | orchestrate calls, apply gate logic per algorithm above |
| L-A2-4 | pairwise key helper | format "bench_a-bench_b" dict keys consistently across matrix/pvalues/ci |

---

## A-3: Statistical Validation [Complexity: 7, Budget: 7]

**Applied**: scipy.stats spearmanr p-value + Fisher z-transform for CI (standard stats convention)

### API Signatures

```python
def compute_pvalues(self) -> dict[str, float]:
    """p-value per pair (same keys as compute_correlation_matrix pairs), from spearmanr(x, y).pvalue."""
    ...

def apply_bonferroni(self, pvalues: dict[str, float]) -> dict[str, float]:
    """adjusted_p = min(p * len(pvalues), 1.0) per pair."""
    ...

def compute_confidence_intervals(self) -> dict[str, tuple[float, float]]:
    """95% CI via Fisher z-transform: z = arctanh(r); se = 1/sqrt(n-3); ci_z = z +/- 1.96*se; return tanh(ci_z)."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | compute_pvalues | spearmanr pvalue per pair |
| L-A3-2 | apply_bonferroni | multiply by n_comparisons, clip to 1.0 |
| L-A3-3 | compute_confidence_intervals | Fisher z-transform 95% CI |

---

## A-4: Visualization Suite [Complexity: 9, Budget: 9]

**Applied**: seaborn heatmap/regplot standard convention

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_correlation_heatmap(corr_matrix: pd.DataFrame, out_path: str) -> None:
    """sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1) -> savefig(out_path)."""
    ...

def plot_pairwise_scatter(scores: pd.DataFrame, benchmarks: list[str], out_dir: str) -> None:
    """For each pair in benchmarks: sns.regplot(x, y) -> save one PNG per pair in out_dir."""
    ...

def plot_gate_metrics(result: dict, out_path: str) -> None:
    """Bar chart: cross-benchmark r values vs baseline_r line + CORR_UPPER_BOUND line."""
    ...

def plot_model_diversity(scores: pd.DataFrame, out_path: str) -> None:
    """3-panel histogram/countplot: arch, scale, variant distributions."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | plot_correlation_heatmap | annotated heatmap of 3x3 corr matrix |
| L-A4-2 | plot_pairwise_scatter | regplot per benchmark pair, saved individually |
| L-A4-3 | plot_gate_metrics | bar chart with baseline/threshold reference lines |
| L-A4-4 | plot_model_diversity | 3-panel arch/scale/variant countplots |

---

## A-5: Orchestration + Reporting [Complexity: 5, Budget: 5]

**Applied**: Standard run.py script pattern

### API Signatures

```python
import json

def main() -> None:
    """
    scores = load_benchmark_scores()
    analyzer = BenchmarkCorrelationAnalyzer(scores)
    result = analyzer.evaluate_hypothesis()
    json.dump(result, open(RESULTS_DIR + "gate_result.json", "w"), indent=2)
    plot_correlation_heatmap(analyzer.compute_correlation_matrix(), FIGURES_DIR + "heatmap.png")
    plot_pairwise_scatter(scores, analyzer.benchmarks, FIGURES_DIR)
    plot_gate_metrics(result, FIGURES_DIR + "gate_metrics.png")
    plot_model_diversity(scores, FIGURES_DIR + "diversity.png")
    print(f"GATE {'PASS' if result['passed'] else 'FAIL'}")
    """
    ...

if __name__ == "__main__":
    main()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A5-1 | main orchestration | wire load -> analyze -> save JSON |
| L-A5-2 | figure generation + pass/fail log | call all 4 plot functions, print gate result |

---

## Total Subtask Budget: 17/2 baseline task allocation, actual subtask count matches per-task breakdown in architecture (3+3+2+2, 2+2+3+1, 2+1+3+1, 3+2+2+2, 1+2+1+1)
