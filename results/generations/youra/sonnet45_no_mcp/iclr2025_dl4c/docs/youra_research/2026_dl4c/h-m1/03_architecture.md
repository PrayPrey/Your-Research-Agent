# System Architecture: h-m1 Benchmark Distinctiveness Analysis

**Hypothesis:** h-m1 (MECHANISM)  
**Date:** 2026-04-15  
**Author:** Architecture Agent  
**Type:** Statistical Analysis - Benchmark Comparison  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Reusing h-e1 data infrastructure  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_dl4c_2/docs/youra_research/20260415_dl4c/h-e1/code/`  
**Findings:** h-e1 provides features.csv with 14 model-benchmark pairs (8 models × HumanEval + MBPP). Analysis modules are statistical computation only.

---

## Design Patterns Applied

**Applied:** Statistical Analysis Pattern (scipy-based correlation and divergence)  
**Applied:** Visualization Pipeline Pattern (matplotlib/seaborn figure generation)

---

## External Dependencies (Base Hypothesis)

### Data Sources from h-e1

| Resource | Path | Description |
|----------|------|-------------|
| Execution Traces | `../h-e1/code/outputs/features.csv` | Complete feature dataset (14 pairs, 100% completeness) |
| Validation Report | `../h-e1/code/outputs/validation_report.json` | Feature completeness metrics |

**Verified from**: h-e1 actual code execution (PASS status, 8 models across HumanEval + MBPP)

**Note:** h-e1 has only HumanEval and MBPP data (APPS not included). Analysis will focus on these two benchmarks.

---

## Module Structure

### 1. DataLoader (`src/data/loader.py`)

**Dependencies:** pandas, numpy

```python
class ExecutionTraceLoader:
    def __init__(self, h_e1_path: str): ...
    def load_features(self) -> pd.DataFrame: ...
    def validate_data_quality(self) -> dict: ...
    def get_benchmark_subset(self, benchmark: str) -> pd.DataFrame: ...
    def get_model_list(self) -> list: ...
```

### 2. BenchmarkCorrelationAnalyzer (`src/analysis/correlation.py`)

**Dependencies:** scipy.stats, pandas, numpy

```python
class BenchmarkCorrelationAnalyzer:
    def __init__(self, feature_df: pd.DataFrame): ...
    def compute_ranking_correlation(self, bench1: str, bench2: str) -> tuple: ...
    def compute_all_pairwise_correlations(self) -> dict: ...
    def get_correlation_matrix(self) -> pd.DataFrame: ...
```

### 3. DistributionDivergenceAnalyzer (`src/analysis/divergence.py`)

**Dependencies:** scipy.stats, numpy

```python
class DistributionDivergenceAnalyzer:
    def __init__(self, feature_df: pd.DataFrame): ...
    def compute_kl_divergence(self, bench1: str, bench2: str, feature: str) -> float: ...
    def compute_all_divergences(self, features: list) -> dict: ...
    def aggregate_divergence_scores(self) -> dict: ...
```

### 4. GateConditionEvaluator (`src/validation/gate_checker.py`)

**Dependencies:** None

```python
class GateConditionEvaluator:
    def __init__(self, correlations: dict, divergences: dict): ...
    def check_correlation_threshold(self, threshold: float = 0.8) -> dict: ...
    def check_divergence_threshold(self, threshold: float = 0.1) -> dict: ...
    def evaluate_gate(self) -> dict: ...
```

### 5. VisualizationGenerator (`src/visualization/plots.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class VisualizationGenerator:
    def __init__(self, correlations: dict, divergences: dict, output_dir: str): ...
    def plot_correlation_heatmap(self) -> str: ...
    def plot_kl_divergence_bars(self) -> str: ...
    def plot_ranking_scatter(self, bench1: str, bench2: str) -> str: ...
    def plot_feature_distributions(self, feature: str) -> str: ...
    def generate_all_figures(self) -> list: ...
```

### 6. AnalysisPipeline (`src/main.py`)

**Dependencies:** All above modules

```python
class AnalysisPipeline:
    def __init__(self, config: dict): ...
    def load_data(self) -> pd.DataFrame: ...
    def compute_correlations(self) -> dict: ...
    def compute_divergences(self) -> dict: ...
    def evaluate_gate(self) -> dict: ...
    def generate_visualizations(self) -> list: ...
    def save_results(self) -> None: ...
    def run(self) -> dict: ...
```

### 7. Configuration (`src/config.py`)

**Dependencies:** None

```python
H_E1_DATA_PATH = "../h-e1/code/outputs/features.csv"

BENCHMARKS = ['HumanEval', 'MBPP']

ANALYSIS_FEATURES = ['pass@1', 'runtime_q50', 'runtime_q75']

GATE_THRESHOLDS = {
    'correlation': 0.8,
    'kl_divergence': 0.1
}

OUTPUT_DIR = "outputs"
FIGURES_DIR = "figures"
```

---

## File Organization

```
h-m1/
├── code/
│   ├── src/
│   │   ├── data/
│   │   │   └── loader.py                # Load h-e1 features.csv
│   │   ├── analysis/
│   │   │   ├── correlation.py           # Spearman correlation
│   │   │   └── divergence.py            # KL divergence
│   │   ├── validation/
│   │   │   └── gate_checker.py          # Gate condition logic
│   │   ├── visualization/
│   │   │   └── plots.py                 # Figure generation
│   │   ├── config.py                    # Analysis configuration
│   │   └── main.py                      # Pipeline orchestration
│   ├── outputs/
│   │   ├── analysis_results.json        # Correlation + divergence results
│   │   └── gate_evaluation.json         # Gate condition results
│   └── requirements.txt
├── figures/
│   ├── correlation_heatmap.png          # Gate metric (required)
│   ├── kl_divergence_bars.png
│   ├── ranking_scatter_humaneval_mbpp.png
│   └── feature_distributions.png
└── results/
    └── summary.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Data Loading Infrastructure | Load h-e1 features.csv, validate data quality, extract benchmark subsets | 6 | Module(2) + Deps(1) + Algo(1) + Integration(2) |
| M-2 | Ranking Correlation Analysis | Implement Spearman correlation for model rankings across benchmarks | 9 | Module(2) + Deps(2) + Algo(3) + Integration(2) |
| M-3 | Distribution Divergence Analysis | Implement KL divergence computation for feature distributions | 10 | Module(3) + Deps(2) + Algo(3) + Integration(2) |
| M-4 | Gate Condition Evaluation | Implement gate logic (ρ < 0.8 AND KL > 0.1) with detailed reporting | 7 | Module(2) + Deps(1) + Algo(2) + Integration(2) |
| M-5 | Visualization Generation | Generate 4 required figures (heatmap, bars, scatter, distributions) | 11 | Module(3) + Deps(2) + Algo(2) + Integration(4) |
| M-6 | Results Integration | Integrate all analyses, save results, generate summary report | 8 | Module(2) + Deps(1) + Algo(2) + Integration(3) |

**Distribution:**  
- VeryHigh (18-20): []  
- High (14-17): []  
- Medium (9-13): [M-2, M-3, M-5]  
- Low (4-8): [M-1, M-4, M-6]

**Total Complexity:** 51 points across 6 Epic tasks

---

## Data Flow

**Stage 1: Data Loading**  
ExecutionTraceLoader → (features.csv from h-e1 → 14 model-benchmark pairs)

**Stage 2: Correlation Analysis**  
BenchmarkCorrelationAnalyzer → (HumanEval-MBPP ranking correlation → ρ, p-value)

**Stage 3: Divergence Analysis**  
DistributionDivergenceAnalyzer → (HumanEval-MBPP feature distributions → KL divergence)

**Stage 4: Gate Evaluation**  
GateConditionEvaluator → (Check ρ < 0.8 AND KL > 0.1 → PASS/FAIL)

**Stage 5: Visualization**  
VisualizationGenerator → (4 figures for gate metrics)

---

## Integration Points

### External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| scipy | >=1.10.0 | Statistical functions (spearmanr, entropy) |
| numpy | >=1.24.0 | Numerical operations |
| pandas | >=2.0.0 | Data manipulation |
| matplotlib | >=3.7.0 | Plotting |
| seaborn | >=0.12.0 | Statistical visualizations |

### Data Dependencies

**From h-e1:**
- Input: `../h-e1/code/outputs/features.csv` (14 rows, 8 models, 2 benchmarks)
- Schema: `[model, benchmark, pass@1, pass@10, pass@100, runtime_q25, runtime_q50, runtime_q75, error_syntax, error_runtime, error_timeout]`

---

## Analysis Specifications

### Pairwise Benchmark Comparison

**Available Pairs (from h-e1 data):**
- HumanEval vs MBPP

**Note:** Original PRD specified 3 benchmarks (HumanEval, MBPP, APPS), but h-e1 only evaluated HumanEval and MBPP. Analysis will focus on single benchmark pair.

### Statistical Methods

**1. Spearman Rank Correlation:**
```python
from scipy.stats import spearmanr
rho, p_value = spearmanr(scores_bench1, scores_bench2)
```

**2. KL Divergence:**
```python
from scipy.stats import entropy
import numpy as np

hist1, bins = np.histogram(features_bench1, bins=20, density=True)
hist2, _ = np.histogram(features_bench2, bins=bins, density=True)

# Normalize
hist1 = (hist1 + 1e-10) / (hist1 + 1e-10).sum()
hist2 = (hist2 + 1e-10) / (hist2 + 1e-10).sum()

kl_div = entropy(pk=hist1, qk=hist2)
```

### Gate Condition (Adapted)

**Original:** At least one benchmark pair with ρ < 0.8 AND KL > 0.1  
**Adapted:** Single pair (HumanEval-MBPP) must show ρ < 0.8 AND KL > 0.1

**If Gate Fails:** Pivot to analyzing why benchmarks show high agreement despite different design philosophies.

---

## Success Validation

**Primary Metric:** Gate Condition Satisfaction  
```python
gate_pass = (rho_humaneval_mbpp < 0.8) and (kl_humaneval_mbpp > 0.1)
```

**Quality Checks:**
- Data loaded successfully from h-e1
- Statistical computations complete without errors
- All visualizations generated
- Results saved to JSON

**Expected Results (from Phase 2B):**
- HumanEval-MBPP correlation: ρ ~ 0.7-0.8 (moderate agreement)
- KL divergence: ~ 0.1-0.2 (moderate distinctiveness)

---

## Complexity Breakdown

**Module_Size Scoring:**
- 0-1: <30 lines (simple data loading)
- 2-3: 30-100 lines (statistical computation, plotting)
- 4-5: >100 lines (complex visualization suite)

**Dependencies Scoring:**
- 0-1: pandas only
- 2-3: scipy + pandas (standard statistical stack)
- 4-5: matplotlib + seaborn (complex plotting dependencies)

**Algorithm Scoring:**
- 0-1: Simple data access
- 2-3: Statistical computations (correlation, divergence)
- 4-5: Multi-panel visualizations with annotations

**Integration Scoring:**
- 0-1: Standalone loader
- 2-3: Integrates with 1-2 other modules
- 4-5: Core pipeline component (visualization integrates all results)

---

## Architecture Constraints

**MECHANISM Hypothesis Constraints:**
- No model training (pure statistical analysis)
- Reuse h-e1 data infrastructure completely
- Focus on proving benchmark distinctiveness via correlation + divergence
- Simple gate condition evaluation

**Data Constraints:**
- Limited to HumanEval and MBPP (APPS not in h-e1)
- 8 models evaluated (sufficient for correlation analysis)
- Single benchmark pair (still validates hypothesis)

**Resource Constraints:**
- No GPU required (CPU-only statistical analysis)
- Runtime: < 5 minutes
- Memory: < 2GB
- Storage: < 50MB (figures + results)

---

**Document Status:** Final Architecture for Phase 4 Implementation  
**Next Phase:** Phase 4 - Implementation (Coding)  
**Data Dependency:** h-e1 outputs (COMPLETED with PASS)
