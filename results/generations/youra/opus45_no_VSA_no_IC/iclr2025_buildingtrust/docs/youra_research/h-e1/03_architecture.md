# Architecture: H-E1

**Type:** EXISTENCE (PoC) — statistical meta-analysis, no model training
**Applied:** Standard data->analysis->viz separation (no directly relevant KB pattern found; used general DS pipeline convention)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch; no base hypothesis or existing codebase.

---

## File Structure

- `code/data.py` — fetch/load benchmark scores into a single DataFrame
- `code/analyze.py` — correlation analysis + hypothesis gate (from experiment brief `BenchmarkCorrelationAnalyzer`)
- `code/visualize.py` — all 4 required figures
- `code/config.py` — fixed paths/constants
- `code/run.py` — orchestrates: load -> analyze -> visualize -> report
- `figures/` — output directory for plots
- `results/` — output directory for correlation table + gate result JSON

---

## Modules

### config.py

```python
DATA_SOURCE = "open-llm-leaderboard/results"
BENCHMARKS = ["truthfulqa", "halueval", "factscore"]
BASELINE_PAIR = ("mmlu_physics", "halueval")
MIN_MODELS = 30
CORR_UPPER_BOUND = 0.7
FIGURES_DIR = "figures/"
RESULTS_DIR = "results/"
```

### data.py (`code/data.py`)

**Dependencies**: config.py

```python
def fetch_leaderboard_scores() -> "pd.DataFrame": ...
def filter_complete_models(df: "pd.DataFrame", min_models: int) -> "pd.DataFrame": ...
def load_benchmark_scores() -> "pd.DataFrame":
    """Returns DataFrame[model, truthfulqa, halueval, factscore, mmlu_physics, arch, scale, variant]"""
    ...
```

### analyze.py (`code/analyze.py`)

**Dependencies**: config.py

```python
class BenchmarkCorrelationAnalyzer:
    def __init__(self, benchmark_scores: "pd.DataFrame"): ...
    def compute_correlation_matrix(self) -> "pd.DataFrame": ...
    def compute_baseline_correlation(self) -> float: ...
    def compute_pvalues(self) -> dict: ...
    def apply_bonferroni(self, pvalues: dict) -> dict: ...
    def compute_confidence_intervals(self) -> dict: ...
    def evaluate_hypothesis(self) -> dict:
        """Returns {passed, correlations, baseline_r, threshold_upper, pvalues, ci}"""
        ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: analyze.py

```python
def plot_correlation_heatmap(corr_matrix: "pd.DataFrame", out_path: str) -> None: ...
def plot_pairwise_scatter(scores: "pd.DataFrame", benchmarks: list, out_dir: str) -> None: ...
def plot_gate_metrics(result: dict, out_path: str) -> None: ...
def plot_model_diversity(scores: "pd.DataFrame", out_path: str) -> None: ...
```

### run.py (`code/run.py`)

**Dependencies**: data.py, analyze.py, visualize.py

```python
def main() -> None:
    """load_benchmark_scores -> BenchmarkCorrelationAnalyzer.evaluate_hypothesis
    -> save results/gate_result.json -> generate all 4 figures"""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Fetch/filter N>=30 model scores across 4 benchmarks | 10 | 3+3+2+2 |
| A-2 | Correlation analyzer | Spearman matrix, baseline r, gate evaluation | 8 | 2+2+3+1 |
| A-3 | Statistical validation | p-values, Bonferroni correction, 95% CI | 7 | 2+1+3+1 |
| A-4 | Visualization suite | Heatmap, scatter plots, gate bar chart, diversity histogram | 9 | 3+2+2+2 |
| A-5 | Orchestration + reporting | run.py wiring, save results JSON, gate pass/fail log | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2, A-4], Low(4-8): [A-3, A-5]
