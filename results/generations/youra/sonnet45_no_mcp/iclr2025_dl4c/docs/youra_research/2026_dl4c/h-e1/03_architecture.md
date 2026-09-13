# System Architecture: h-e1 Execution Trace Feature Extraction

**Hypothesis:** h-e1 (EXISTENCE)  
**Date:** 2026-04-15  
**Author:** Architecture Agent  
**Type:** Data Infrastructure Validation  

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch - no existing code to analyze  
**Analyzed Path:** N/A  
**Findings:** Foundation hypothesis with no base codebase. Clean slate data extraction pipeline.

---

## Design Patterns Applied

**Applied:** Data Pipeline Pattern (ETL for benchmark feature extraction)  
**Applied:** Repository Pattern (Standardized data access for multiple benchmarks)

---

## Module Structure

### 1. BenchmarkLoader (`src/data/benchmark_loader.py`)

**Dependencies:** datasets, torch

```python
class BenchmarkLoader:
    def __init__(self, benchmark_name: str): ...
    def load_dataset(self) -> dict: ...
    def get_test_cases(self, problem_id: str) -> list: ...
    def get_problem_count(self) -> int: ...

class HumanEvalLoader(BenchmarkLoader):
    def load_dataset(self) -> dict: ...

class MBPPLoader(BenchmarkLoader):
    def load_dataset(self) -> dict: ...

class APPSLoader(BenchmarkLoader):
    def load_dataset(self) -> dict: ...
```

### 2. PublishedResultsCollector (`src/data/published_results.py`)

**Dependencies:** pandas, numpy

```python
class PublishedResultsCollector:
    def __init__(self, results_dir: str): ...
    def load_results_csv(self, benchmark: str) -> pd.DataFrame: ...
    def get_passk_scores(self, model: str, benchmark: str) -> dict: ...
    def list_available_models(self, benchmark: str) -> list: ...
    def validate_results(self) -> dict: ...
```

### 3. ExecutionTraceExtractor (`src/features/extractor.py`)

**Dependencies:** numpy, pandas

```python
class ExecutionTraceExtractor:
    def __init__(self, benchmark_name: str): ...
    def extract_passk(self, model_outputs: list, k_values: list) -> dict: ...
    def extract_runtime_quartiles(self, passing_solutions: list) -> dict: ...
    def categorize_errors(self, failed_solutions: list) -> dict: ...
    def extract_all_features(self, model_name: str, evaluation_results: dict) -> dict: ...
```

### 4. CodeExecutor (`src/execution/executor.py`)

**Dependencies:** subprocess, docker (optional)

```python
class CodeExecutor:
    def __init__(self, timeout: int = 30, use_sandbox: bool = True): ...
    def execute_solution(self, code: str, test_case: dict) -> tuple: ...
    def measure_runtime(self, code: str, test_case: dict) -> float: ...
    def categorize_error(self, error: Exception) -> str: ...
```

### 5. FeatureValidator (`src/validation/validator.py`)

**Dependencies:** pandas, numpy

```python
class FeatureValidator:
    def __init__(self, feature_df: pd.DataFrame): ...
    def calculate_completeness(self) -> float: ...
    def check_standardization(self) -> dict: ...
    def identify_missing_data(self) -> pd.DataFrame: ...
    def validate_gate_condition(self, threshold: float = 95.0) -> bool: ...
```

### 6. VisualizationGenerator (`src/visualization/plots.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class VisualizationGenerator:
    def __init__(self, feature_df: pd.DataFrame, output_dir: str): ...
    def plot_completeness_comparison(self) -> None: ...
    def plot_feature_coverage_heatmap(self) -> None: ...
    def plot_feature_distributions(self) -> None: ...
    def plot_coverage_matrix(self) -> None: ...
    def generate_all_figures(self) -> None: ...
```

### 7. ExperimentPipeline (`src/main.py`)

**Dependencies:** All above modules

```python
class ExperimentPipeline:
    def __init__(self, config: dict): ...
    def load_benchmarks(self) -> dict: ...
    def collect_published_results(self) -> pd.DataFrame: ...
    def extract_features(self) -> pd.DataFrame: ...
    def validate_completeness(self) -> dict: ...
    def generate_visualizations(self) -> None: ...
    def run(self) -> dict: ...
```

### 8. Configuration (`src/config.py`)

**Dependencies:** None

```python
BENCHMARKS = ['HumanEval', 'MBPP', 'APPS']

FEATURE_SCHEMA = {
    'pass@1': float,
    'pass@10': float,
    'pass@100': float,
    'runtime_q25': float,
    'runtime_q50': float,
    'runtime_q75': float,
    'error_syntax': float,
    'error_runtime': float,
    'error_timeout': float
}

COMPLETENESS_THRESHOLD = 95.0
EXECUTION_TIMEOUT = 30
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── data/
│   │   │   ├── benchmark_loader.py      # Dataset loading
│   │   │   └── published_results.py     # Collect published pass@k
│   │   ├── features/
│   │   │   └── extractor.py             # Feature extraction logic
│   │   ├── execution/
│   │   │   └── executor.py              # Code execution sandbox
│   │   ├── validation/
│   │   │   └── validator.py             # Feature completeness check
│   │   ├── visualization/
│   │   │   └── plots.py                 # Figure generation
│   │   ├── config.py                    # Experiment configuration
│   │   └── main.py                      # Pipeline orchestration
│   ├── data/
│   │   └── published_results/           # CSV files with model results
│   ├── outputs/
│   │   ├── features.csv                 # Extracted features
│   │   └── validation_report.json       # Completeness metrics
│   └── requirements.txt
├── figures/
│   ├── completeness_comparison.png      # Gate metric (required)
│   ├── feature_coverage_heatmap.png
│   ├── feature_distributions.png
│   └── coverage_matrix.png
└── results/
    └── experiment_summary.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Benchmark Data Infrastructure | Load HumanEval/MBPP/APPS datasets, verify dataset structure | 8 | Module(2) + Deps(2) + Algo(2) + Integration(2) |
| A-2 | Published Results Collection | Collect pass@k scores from papers/leaderboards for 20+ models | 10 | Module(3) + Deps(1) + Algo(3) + Integration(3) |
| A-3 | Feature Extraction Pipeline | Implement pass@k, runtime quartiles, error categorization extractors | 12 | Module(3) + Deps(2) + Algo(4) + Integration(3) |
| A-4 | Code Execution Sandbox | Safe execution environment with timeout/error capture | 11 | Module(3) + Deps(3) + Algo(2) + Integration(3) |
| A-5 | Feature Completeness Validation | Calculate completeness rate, validate gate condition (≥95%) | 7 | Module(2) + Deps(1) + Algo(2) + Integration(2) |
| A-6 | Visualization Generation | Generate 4 required figures (completeness, heatmap, distributions, matrix) | 9 | Module(2) + Deps(2) + Algo(2) + Integration(3) |

**Distribution:**  
- VeryHigh (18-20): []  
- High (14-17): []  
- Medium (9-13): [A-2, A-3, A-4, A-6]  
- Low (4-8): [A-1, A-5]

**Total Complexity:** 57 points across 6 Epic tasks

---

## Data Flow

**Stage 1: Data Loading**  
BenchmarkLoader → (HumanEval, MBPP, APPS datasets)

**Stage 2: Published Results Collection**  
PublishedResultsCollector → (20+ models × 3 benchmarks → pass@k scores)

**Stage 3: Feature Extraction**  
ExecutionTraceExtractor + CodeExecutor → (runtime quartiles, error distributions)

**Stage 4: Validation**  
FeatureValidator → (completeness ≥ 95% check)

**Stage 5: Visualization**  
VisualizationGenerator → (4 figures for gate metric)

---

## Integration Points

### External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| datasets | >=2.14.0 | HuggingFace benchmark loading |
| transformers | >=4.30.0 | Model loading (optional re-execution) |
| numpy | >=1.24.0 | Statistical computations |
| pandas | >=2.0.0 | Data manipulation |
| matplotlib | >=3.7.0 | Visualization |
| seaborn | >=0.12.0 | Advanced plots |

### Benchmark APIs

- **HumanEval:** `load_dataset("openai_humaneval")`
- **MBPP:** `load_dataset("mbpp")`
- **APPS:** `load_dataset("codeparrot/apps")`

---

## Success Validation

**Primary Metric:** Feature Completeness Rate  
```python
completeness = (complete_pairs / total_pairs) * 100
```

**Gate Condition:** completeness >= 95.0

**Quality Checks:**
- All 3 benchmarks have loaded data
- Feature schema validated across all model-benchmark pairs
- No systematic missing data patterns

---

## Complexity Breakdown

**Module_Size Scoring:**
- 0-1: <50 lines
- 2-3: 50-150 lines
- 4-5: >150 lines

**Dependencies Scoring:**
- 0-1: Standard library only
- 2-3: 1-2 external packages
- 4-5: 3+ external packages with complex APIs

**Algorithm Scoring:**
- 0-1: Simple CRUD operations
- 2-3: Statistical computations, data transformations
- 4-5: Complex execution sandboxing, error categorization

**Integration Scoring:**
- 0-1: Standalone module
- 2-3: Integrates with 1-2 other modules
- 4-5: Core pipeline component, multiple dependencies

---

## Architecture Constraints

**EXISTENCE Hypothesis Constraints:**
- Minimal infrastructure (no model training)
- Focus on data extraction proof-of-concept
- Simple validation (completeness threshold)
- No ablation studies or hyperparameter tuning

**Resource Constraints:**
- No GPU required
- Execution sandbox (Docker optional, subprocess sufficient)
- Storage: ~10GB for datasets + outputs

**Timeline Constraints:**
- Weeks 1-2: Published results collection + benchmark loading
- Week 3: Runtime/error data extraction (selective re-execution)
- Week 4: Validation + visualization

---

**Document Status:** Final Architecture for Phase 4 Implementation  
**Next Phase:** Phase 4 - Implementation (Coding)
