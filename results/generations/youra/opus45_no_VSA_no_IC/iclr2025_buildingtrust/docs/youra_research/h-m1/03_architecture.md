# H-M1 Architecture

**Hypothesis**: TruthfulQA measures resistance to popular misconceptions, distinct from general knowledge retrieval (MMLU).
**Type**: EXISTENCE (correlation PoC)
**Applied**: Spearman correlation + z-score outlier pattern (from H-E1 BenchmarkCorrelationAnalyzer)

## Codebase Analysis (Serena)

**Project Type**: green-field (references H-E1 data, no code reuse)
**Status**: Green-field - no existing code to analyze for H-M1 itself
**Analyzed Path**: N/A
**Findings**: H-E1 (`docs/youra_research/h-e1/code/`) has a working config/data/analyze/visualize/run split for the same class of problem (leaderboard correlation PoC). H-M1 follows the same module boundaries but with new logic (MMLU-vs-internal-subject comparison, divergent-profile detection). No direct import — H-M1 loads H-E1's *output* (`experiment_results.json` / score table), not H-E1's code.

## Data Flow

1. `data.py::load_h_e1_population()` reads H-E1's N=50 model list + TruthfulQA scores from `docs/youra_research/h-e1/experiment_results.json`
2. `data.py::fetch_mmlu_scores()` fetches MMLU overall + per-subject scores for the same models from Open LLM Leaderboard
3. `data.py::merge_population()` joins on model name -> single DataFrame
4. `analyze.py::CorrelationAnalyzer` computes r(TruthfulQA, MMLU) and pairwise r(MMLU subject_i, subject_j)
5. `analyze.py::find_divergent_models()` flags MMLU z>1 & TruthfulQA z<0 rows
6. `visualize.py` renders heatmap + scatter + divergence highlight plots from analyzer output
7. `run.py` orchestrates 1-6, writes `results.json`

## File Structure

- `docs/youra_research/h-m1/code/config.py` - constants (paths, MMLU subject list, z-thresholds)
- `docs/youra_research/h-m1/code/data.py` - load/fetch/merge model population
- `docs/youra_research/h-m1/code/analyze.py` - CorrelationAnalyzer, divergence detection
- `docs/youra_research/h-m1/code/visualize.py` - plotting functions
- `docs/youra_research/h-m1/code/run.py` - entrypoint
- `docs/youra_research/h-m1/code/figures/` - output plots
- `docs/youra_research/h-m1/code/results.json` - output metrics

## Module Interfaces

### config.py

```python
H_E1_RESULTS_PATH: str  # docs/youra_research/h-e1/experiment_results.json
MMLU_SUBJECTS: list[str]  # e.g. ["abstract_algebra", "anatomy", ...]
Z_HIGH_MMLU: float = 1.0
Z_LOW_TRUTHFULQA: float = 0.0
MIN_MODELS: int = 50
```

### data.py

**Dependencies**: config

```python
def load_h_e1_population() -> pd.DataFrame: ...      # model, truthfulqa
def fetch_mmlu_scores(models: list[str]) -> pd.DataFrame: ...  # model, mmlu_overall, mmlu_<subject>...
def merge_population(tqa_df: pd.DataFrame, mmlu_df: pd.DataFrame) -> pd.DataFrame: ...
def load_full_population() -> pd.DataFrame: ...  # orchestrates above 3
```

### analyze.py (`CorrelationAnalyzer`)

**Dependencies**: data, config

```python
class CorrelationAnalyzer:
    def __init__(self, population: pd.DataFrame): ...
    def compute_cross_correlation(self) -> float: ...        # r(truthfulqa, mmlu_overall)
    def compute_internal_correlations(self) -> pd.DataFrame: # r matrix across mmlu_<subject> cols
    def find_divergent_models(self) -> pd.DataFrame: ...      # z(mmlu)>1 & z(truthfulqa)<0
    def evaluate_hypothesis(self) -> dict: ...
        # {"passed": bool, "cross_r": float, "internal_r_mean": float,
        #  "divergent_models": list[str], "n_models": int}
```

### visualize.py

**Dependencies**: analyze

```python
def plot_correlation_heatmap(internal_corr: pd.DataFrame, cross_r: float, out_path: str) -> None: ...
def plot_divergence_scatter(population: pd.DataFrame, divergent: pd.DataFrame, out_path: str) -> None: ...
```

### run.py

**Dependencies**: data, analyze, visualize

```python
def main() -> dict: ...  # load -> analyze -> visualize -> write results.json
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Load H-E1 population | Parse experiment_results.json for N=50 models + TruthfulQA | 5 | 2+1+1+1 |
| M1-2 | Fetch MMLU scores | Overall + per-subject from Open LLM Leaderboard, merge on model | 8 | 3+2+2+1 |
| M1-3 | Correlation analysis | CorrelationAnalyzer: cross r + internal subject r matrix | 7 | 2+2+2+1 |
| M1-4 | Divergent model detection | z-score filter, flag high-MMLU/low-TruthfulQA models | 6 | 2+1+2+1 |
| M1-5 | Visualization | Heatmap + divergence scatter plots | 5 | 2+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M1-1, M1-2, M1-3, M1-4, M1-5]

## External Module Paths (H-E1 Output, Not Code)

| Item | Path | Note |
|------|------|------|
| TruthfulQA scores | `docs/youra_research/h-e1/experiment_results.json` | Read as data, not imported as code |
