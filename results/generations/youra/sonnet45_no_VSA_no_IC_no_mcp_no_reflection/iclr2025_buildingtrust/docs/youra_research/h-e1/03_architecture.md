# Architecture: h-e1

**Hypothesis:** Pairwise failure correlations across TrustfulQA, AdvBench, and BOLD benchmarks exceed random chance with statistical significance (Spearman r > 0.3, p < 0.01 after Bonferroni correction)

**Type:** EXISTENCE (PoC)
**Date:** 2026-08-28

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing code - statistical analysis pipeline for benchmark correlation

---

## Architecture Pattern

Applied: Statistical analysis pipeline (data → clean → analyze → visualize)

---

## Module Structure

### DataCollector (`data_collection.py`)

**Dependencies:** pandas

```python
class BenchmarkCollector:
    def collect_from_sources(self) -> pd.DataFrame: ...
    def save_to_csv(self, path: str): ...
```

### Preprocessor (`preprocessing.py`)

**Dependencies:** pandas, numpy

```python
class DataPreprocessor:
    def normalize_scores(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def stratify_by_size(self, df: pd.DataFrame) -> dict: ...
```

### CorrelationAnalyzer (`correlation_analysis.py`)

**Dependencies:** scipy.stats, statsmodels, pandas

```python
class FailureCorrelationAnalyzer:
    def __init__(self, benchmark_data: pd.DataFrame, alpha: float = 0.01): ...
    def compute_correlations(self) -> dict: ...
    def apply_bonferroni(self, correlations: dict) -> tuple: ...
    def stratified_analysis(self, strata: dict) -> dict: ...
```

### Visualizer (`visualizations.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class CorrelationVisualizer:
    def plot_correlation_matrix(self, correlations: dict, output_path: str): ...
    def plot_scatter_pairs(self, df: pd.DataFrame, output_path: str): ...
    def plot_stratified_comparison(self, strata_results: dict, output_path: str): ...
    def plot_gate_metrics(self, results: dict, output_path: str): ...
```

### Main (`main.py`)

**Dependencies:** All above modules

```python
def run_analysis(data_path: str, output_dir: str):
    # 1. Load data
    # 2. Preprocess
    # 3. Analyze correlations
    # 4. Generate visualizations
    # 5. Save results
    ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── data_collection.py       # Manual benchmark aggregation
│   ├── preprocessing.py          # Normalization + cleaning
│   ├── correlation_analysis.py  # Core statistical analysis
│   ├── visualizations.py         # Figure generation
│   ├── main.py                   # Orchestration
│   └── requirements.txt          # scipy, statsmodels, pandas, matplotlib, seaborn
├── data/
│   └── benchmark_scores.csv      # Input data (manually collected)
├── results/
│   └── correlation_results.json  # Numerical outputs
└── figures/
    ├── correlation_matrix.png
    ├── scatter_pairs.png
    ├── stratified_comparison.png
    └── gate_metrics.png
```

---

## Data Flow

```
benchmark_scores.csv → DataPreprocessor → FailureCorrelationAnalyzer → CorrelationVisualizer → figures/
                                                    ↓
                                        correlation_results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Data Collection | Manually aggregate benchmark scores for 15+ models from leaderboards/papers | 8 | setup(2) + scraping(3) + validation(3) |
| E2 | Preprocessing Pipeline | Normalization, missing value handling, stratification | 6 | normalize(2) + clean(2) + stratify(2) |
| E3 | Correlation Analysis | Spearman correlation + Bonferroni correction | 9 | compute(3) + bonferroni(3) + stratified(3) |
| E4 | Visualization | Generate 4 required figures | 7 | heatmap(2) + scatter(2) + stratified(2) + gate(1) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E3], Low(4-8): [E1, E2, E4]

**Total Complexity:** 30

---

## Interface Contracts

### DataPreprocessor → CorrelationAnalyzer

```python
# Input: DataFrame with columns ['model_name', 'size_stratum', 'truthfulqa_score', 'advbench_score', 'bold_score']
# Output: Same schema, normalized [0,1], no missing values
```

### CorrelationAnalyzer → Visualizer

```python
# Input: dict {('bench1', 'bench2'): (r, p_value)}
# Output: Figures saved to disk
```

---

## Dependencies

**External:**
- scipy >= 1.7.0
- statsmodels >= 0.13.0
- pandas >= 1.3.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0

**Internal:** None (green-field)

---

## Validation Checkpoints

1. **Data Collection:** CSV has ≥15 rows, 6 columns, no empty cells
2. **Preprocessing:** All scores in [0,1], no NaN values post-cleaning
3. **Analysis:** 3 correlation pairs computed, Bonferroni applied
4. **Visualization:** 4 PNG files generated without errors

---

## Notes

- No model training - pure statistical analysis
- Deterministic (no random seeds needed)
- Single-file modules (no subpackages for PoC)
- Manual data collection (1-2 days) is critical path
