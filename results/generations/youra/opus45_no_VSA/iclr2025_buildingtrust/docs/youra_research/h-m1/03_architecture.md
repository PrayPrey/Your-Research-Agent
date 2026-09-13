# H-M1 Architecture: PC1-BSI Correlation

**Hypothesis**: PC1_residual correlates positively with Behavioral Stability Index (BSI = geomean(PAWS_acc, QQP_acc)), ρ > 0, p < 0.05.

**Type**: EXISTENCE (correlation PoC) — minimal architecture, no ablations.

Applied: statistical correlation pipeline pattern (load → compute metric → correlate → visualize).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: No `h-e1` code directory or existing `src/` found in repo; PC1 scores from H-E1 are assumed to be delivered as a CSV/JSON artifact path passed via config, not imported as code.

## Module Structure

### 1. PC1Loader (`h_m1/data/pc1_loader.py`)

**Dependencies**: pandas

```python
def load_pc1_scores(path: str) -> pd.DataFrame:
    """Returns DataFrame[model_id, pc1_residual]"""
```

### 2. ParaphraseData (`h_m1/data/paraphrase_data.py`)

**Dependencies**: datasets (HuggingFace)

```python
def load_paws(split: str = "test") -> Dataset: ...
def load_qqp(split: str = "validation") -> Dataset: ...
```

### 3. InferenceRunner (`h_m1/inference/runner.py`)

**Dependencies**: transformers, ParaphraseData

```python
class InferenceRunner:
    def __init__(self, model_id: str, batch_size: int = 16): ...
    def predict(self, dataset: Dataset) -> list[int]:
        """0/1 paraphrase predictions"""
    def accuracy(self, dataset: Dataset) -> float: ...
```

### 4. BSIComputer (`h_m1/metrics/bsi.py`)

**Dependencies**: none (pure functions)

```python
def compute_bsi(paws_acc: float, qqp_acc: float) -> float:
    """geometric mean: sqrt(paws_acc * qqp_acc)"""

def compute_bsi_for_models(model_ids: list[str], runner_factory) -> pd.DataFrame:
    """Returns DataFrame[model_id, paws_acc, qqp_acc, bsi]"""
```

### 5. CorrelationAnalysis (`h_m1/analysis/correlation.py`)

**Dependencies**: scipy.stats, pandas

```python
def merge_pc1_bsi(pc1_df: pd.DataFrame, bsi_df: pd.DataFrame) -> pd.DataFrame:
    """Inner join on model_id"""

def pearson_test(df: pd.DataFrame) -> dict:
    """Returns {rho: float, p_value: float, n: int}"""
```

### 6. Visualization (`h_m1/analysis/plot.py`)

**Dependencies**: matplotlib

```python
def scatter_with_fit(df: pd.DataFrame, out_path: str) -> None:
    """PC1_residual (x) vs BSI (y) scatter + regression line, annotate rho/p"""
```

### 7. Pipeline entrypoint (`h_m1/run.py`)

```python
def main(config_path: str) -> None:
    """load PC1 -> run inference per model -> compute BSI -> merge -> correlate -> plot -> save results.json"""
```

## Data Flow

1. `pc1_loader` reads H-E1 PC1 CSV → `[model_id, pc1_residual]`
2. `paraphrase_data` loads PAWS + QQP test sets (cached via HF `datasets`)
3. For each model_id in PC1 table: `InferenceRunner` loads model, predicts on PAWS/QQP, returns accuracies
4. `bsi.compute_bsi` combines the two accuracies into BSI per model
5. `correlation.merge_pc1_bsi` joins PC1 table with BSI table on model_id
6. `correlation.pearson_test` computes ρ, p-value
7. `plot.scatter_with_fit` renders figure; `run.main` writes `results.json` (rho, p, n, per-model table) and figure to `outputs/`

## File Structure

```
h_m1/
  data/
    pc1_loader.py
    paraphrase_data.py
  inference/
    runner.py
  metrics/
    bsi.py
  analysis/
    correlation.py
    plot.py
  config.py        # dataset paths, model list, HF cache dir, batch size
  run.py
outputs/
  results.json
  pc1_bsi_scatter.png
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | PC1 loader | Load & validate H-E1 PC1 CSV | 5 | 1+1+1+2 |
| A-2 | Paraphrase datasets | Load PAWS/QQP via HF datasets, cache | 6 | 2+2+1+1 |
| A-3 | Inference runner | Batch predict + accuracy per model | 10 | 3+3+3+1 |
| A-4 | BSI computation | Geomean metric + per-model table | 4 | 1+1+1+1 |
| A-5 | Correlation analysis | Merge tables, Pearson test | 5 | 1+2+1+1 |
| A-6 | Visualization | Scatter plot w/ fit line + annotations | 4 | 1+1+1+1 |
| A-7 | Pipeline + config | Wire run.py, config.py, results.json output | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-4, A-5, A-6, A-7]

## External Dependencies (Base Hypothesis)

None — no `h-e1/code/` directory exists in the repo. PC1 scores are consumed as a **data artifact** (CSV path in config), not as imported code. If H-E1 code later becomes available, revisit `pc1_loader.py` to import directly instead of reading a CSV.
