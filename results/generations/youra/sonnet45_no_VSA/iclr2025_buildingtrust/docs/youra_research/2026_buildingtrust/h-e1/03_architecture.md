# Architecture Specification: H-E1
**Date:** 2026-07-09  
**Hypothesis:** H-E1 (EXISTENCE - MUST_WORK)  
**Type:** Statistical Meta-Analysis Pipeline  

---

## Applied Patterns

**Archon KB**: Statistical analysis pipeline architecture (diffusers/pipelines pattern)  
**Codebase Analysis**: Existing h-e1 implementation found - cross-benchmark correlation analysis (different from PRD requirements)

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase  
**Status**: Implementation mismatch detected  
**Analyzed Path**: experiments/h-e1/  
**Findings**: Existing code implements pairwise cross-benchmark correlation (ρ vs ρ), but PRD requires CV-stability meta-analysis (CV vs mean ρ). Architecture redesign needed.

---

## Architecture Overview

H-E1 validates CV as predictor of cross-benchmark stability through statistical meta-analysis. Pipeline: data extraction → CV computation → cross-benchmark ρ computation → Pearson correlation test.

**EXISTENCE (PoC) Scope**: Minimal pipeline testing "does CV predict stability?"

---

## Module Structure

### DataExtractor (`src/data_extraction.py`)

**Dependencies**: None (entry point)

```python
class TrustLLMScraper:
    def __init__(self, url: str, timeout: int = 30): ...
    def scrape_leaderboard(self) -> pd.DataFrame: ...

class BenchmarkCorpusBuilder:
    def __init__(self, min_models: int = 10): ...
    def extract_trustllm_dimensions(self, html_content: str) -> Dict[str, pd.DataFrame]: ...
    def validate_benchmark(self, df: pd.DataFrame) -> bool: ...
    def build_corpus(self) -> Dict[str, pd.DataFrame]: ...
```

### MetaAnalysis (`src/meta_analysis.py`)

**Dependencies**: DataExtractor

```python
class BenchmarkMetaAnalysis:
    def __init__(self, min_models: int = 10, min_shared_models: int = 5): ...
    def compute_cv(self, scores: np.ndarray) -> float: ...
    def compute_cross_benchmark_rho(
        self, 
        benchmark_a: pd.DataFrame, 
        benchmark_b: pd.DataFrame
    ) -> Optional[float]: ...
    def compute_mean_rho_per_benchmark(
        self, 
        benchmark_dict: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame: ...
    def test_cv_stability_correlation(
        self, 
        cv_values: List[float], 
        mean_rho_values: List[float]
    ) -> Tuple[float, float]: ...
    def analyze(self, benchmark_dict: Dict[str, pd.DataFrame]) -> AnalysisResults: ...
```

### Visualization (`src/visualization.py`)

**Dependencies**: MetaAnalysis

```python
class MetaAnalysisVisualizer:
    def __init__(self, output_dir: str = "figures/", dpi: int = 300): ...
    def plot_cv_vs_rho_scatter(
        self, 
        cv_values: List[float], 
        mean_rho_values: List[float], 
        r: float, 
        p: float
    ) -> None: ...
    def plot_per_benchmark_bars(
        self, 
        cv_values: List[float], 
        mean_rho_values: List[float], 
        benchmark_names: List[str]
    ) -> None: ...
    def plot_pairwise_heatmap(self, correlation_matrix: pd.DataFrame) -> None: ...
    def plot_gate_comparison(
        self, 
        target_r: float, 
        actual_r: float, 
        target_p: float, 
        actual_p: float
    ) -> None: ...
```

### ReportGenerator (`src/report.py`)

**Dependencies**: MetaAnalysis, Visualization

```python
class ValidationReportGenerator:
    def __init__(self, hypothesis_id: str = "h-e1"): ...
    def generate_summary_json(self, results: AnalysisResults) -> Dict[str, Any]: ...
    def generate_validation_md(self, results: AnalysisResults) -> str: ...
    def save_artifacts(
        self, 
        results: AnalysisResults, 
        benchmark_dict: Dict[str, pd.DataFrame]
    ) -> None: ...
```

### Orchestrator (`src/main.py`)

**Dependencies**: All modules

```python
def main():
    # 1. Data Extraction
    corpus_builder = BenchmarkCorpusBuilder(min_models=10)
    benchmark_dict = corpus_builder.build_corpus()
    
    # 2. Meta-Analysis
    analyzer = BenchmarkMetaAnalysis(min_models=10, min_shared_models=5)
    results = analyzer.analyze(benchmark_dict)
    
    # 3. Visualization
    visualizer = MetaAnalysisVisualizer(output_dir="figures/")
    visualizer.plot_cv_vs_rho_scatter(...)
    visualizer.plot_per_benchmark_bars(...)
    visualizer.plot_pairwise_heatmap(...)
    visualizer.plot_gate_comparison(...)
    
    # 4. Report
    report_gen = ValidationReportGenerator(hypothesis_id="h-e1")
    report_gen.save_artifacts(results, benchmark_dict)
    
    # 5. Gate Decision
    gate_passed = (results.pearson_r < -0.5) and (results.pearson_p < 0.05)
    print(f"MUST_WORK Gate: {'PASSED' if gate_passed else 'FAILED'}")
```

---

## Data Schemas

### BenchmarkDict
```python
# {benchmark_name: DataFrame[model_name, score]}
BenchmarkDict = Dict[str, pd.DataFrame]
# Each DataFrame: columns=['model_name', 'score'], index=model_name
```

### AnalysisResults
```python
@dataclass
class AnalysisResults:
    cv_per_benchmark: pd.DataFrame  # [benchmark_name, cv, mean, std, n_models]
    mean_rho_per_benchmark: pd.DataFrame  # [benchmark_name, mean_rho, n_pairs]
    pairwise_rho_matrix: pd.DataFrame  # [n_benchmarks x n_benchmarks]
    pearson_r: float
    pearson_p: float
    ci_lower: float
    ci_upper: float
    gate_passed: bool
```

---

## File Organization

```
h-e1/
├── src/
│   ├── __init__.py
│   ├── data_extraction.py      # TrustLLMScraper, BenchmarkCorpusBuilder
│   ├── meta_analysis.py        # BenchmarkMetaAnalysis
│   ├── visualization.py        # MetaAnalysisVisualizer
│   ├── report.py               # ValidationReportGenerator
│   └── main.py                 # Orchestration
├── data/
│   ├── benchmark_corpus.pkl
│   └── extraction_log.txt
├── results/
│   ├── cv_per_benchmark.csv
│   ├── mean_rho_per_benchmark.csv
│   ├── pairwise_rho_matrix.csv
│   ├── hypothesis_test_results.json
│   └── summary.json
├── figures/
│   ├── cv_vs_rho_scatter.png
│   ├── cv_rho_per_benchmark_bars.png
│   ├── pairwise_rho_heatmap.png
│   └── gate_metrics_comparison.png
└── 04_validation.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Extraction Pipeline | Implement web scraping and corpus building | 8 | 2+2+2+2 |
| A-2 | CV Computation Module | Implement coefficient of variation calculator | 4 | 1+1+1+1 |
| A-3 | Cross-Benchmark Correlation | Implement pairwise Spearman ρ computation | 9 | 2+2+3+2 |
| A-4 | Hypothesis Test Module | Implement Pearson correlation test and gate logic | 6 | 2+1+2+1 |
| A-5 | Visualization Suite | Generate 4 required figures | 10 | 3+3+2+2 |
| A-6 | Report Generation | Generate validation report and export artifacts | 5 | 2+1+1+1 |

**Total**: 42 points  
**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-5], Low(4-8): [A-1, A-2, A-4, A-6]

---

## Task Complexity Breakdown

### A-1: Data Extraction Pipeline (8)
- **Module_Size**: 2 (TrustLLMScraper, BenchmarkCorpusBuilder classes)
- **Dependencies**: 2 (BeautifulSoup, pandas, requests)
- **Algorithm**: 2 (HTML parsing, benchmark validation)
- **Integration**: 2 (Multi-source corpus building)

### A-2: CV Computation Module (4)
- **Module_Size**: 1 (Single compute_cv function)
- **Dependencies**: 1 (numpy only)
- **Algorithm**: 1 (CV = σ/μ)
- **Integration**: 1 (Standalone metric)

### A-3: Cross-Benchmark Correlation (9)
- **Module_Size**: 2 (Pairwise ρ + mean ρ aggregation)
- **Dependencies**: 2 (scipy.stats, pandas)
- **Algorithm**: 3 (Shared model filtering, ranking, Spearman correlation)
- **Integration**: 2 (All benchmark pairs, matrix construction)

### A-4: Hypothesis Test Module (6)
- **Module_Size**: 2 (Pearson test + gate evaluation)
- **Dependencies**: 1 (scipy.stats.pearsonr)
- **Algorithm**: 2 (Correlation test, confidence interval)
- **Integration**: 1 (Standalone test function)

### A-5: Visualization Suite (10)
- **Module_Size**: 3 (4 plot functions in one class)
- **Dependencies**: 3 (matplotlib, seaborn, pandas)
- **Algorithm**: 2 (Scatter + regression, heatmap, bars, gate comparison)
- **Integration**: 2 (Multi-figure coordination, output management)

### A-6: Report Generation (5)
- **Module_Size**: 2 (JSON export + markdown generation)
- **Dependencies**: 1 (json, pickle, pandas)
- **Algorithm**: 1 (Template formatting)
- **Integration**: 1 (Artifact collection and export)

---

## Key Design Decisions

**Minimal Pipeline for PoC**: Single analysis run with fixed configuration. No ablation studies, no hyperparameter tuning. Focus: "Does CV predict stability?"

**Mock Data Fallback**: If web scraping fails, use mock data generation (as in existing code) to ensure pipeline testability.

**Statistical Rigor**: Use sample std (ddof=1) for CV, two-tailed Pearson test, 95% CI for effect size reporting.

---

## Validation Criteria

**Primary**: Pearson r < -0.5 AND p < 0.05  
**Secondary**: 5-10 benchmarks loaded, CV computed for all, mean ρ computed for all, 4 figures generated  
**Deliverable**: 04_validation.md with gate decision

---

**Next Phase**: Phase 4 (Implementation) - 6 epic tasks, ~42 complexity points
