# Product Requirements Document (PRD)
# H-E1: CV-Stability Correlation Meta-Analysis

**Date:** 2026-07-09
**Author:** Anonymous
**Hypothesis:** H-E1 (EXISTENCE - MUST_WORK)
**Source:** Phase 2C Experiment Brief

---

## Executive Summary

### Product Vision
Develop a statistical meta-analysis tool that tests whether the coefficient of variation (CV) of benchmark scores predicts cross-benchmark ranking stability (measured by mean Spearman ρ). This validates CV as a meta-feature for assessing benchmark quality and reliability.

### Problem Statement
Current trust benchmark evaluations lack validated meta-features for assessing benchmark quality. Without quantitative indicators of benchmark stability, researchers cannot systematically identify reliable benchmarks for model evaluation. This leads to:
- Inconsistent model rankings across different trust benchmarks
- Difficulty selecting trustworthy benchmarks for publication
- Limited understanding of what makes a benchmark robust

### Hypothesis Statement
**H-E1:** Pearson correlation between benchmark CV and mean cross-benchmark Spearman ρ is negative and moderate-to-strong (r < -0.5) with statistical significance (p < 0.05) across 5-10 trust benchmarks.

**Gate Type:** MUST_WORK
- If r < -0.5 AND p < 0.05: CV is validated as stability predictor → Proceed to mechanism hypotheses (H-M1, H-M2)
- If fails: CV is NOT predictive → Route to Phase 0 for fundamental redesign

### Success Criteria
1. **Primary:** Pearson r < -0.5, p < 0.05 between CV and mean cross-benchmark ρ
2. **Data Quality:** 5-10 benchmarks with n≥10 models each, ≥5 shared models per pair
3. **Execution:** Code runs without errors, generates required visualizations

---

## Functional Requirements

### FR-1: Data Collection and Extraction
**Priority:** P0 (Critical)
**Rationale:** Foundation for all analysis - no data = no hypothesis test

**Requirements:**
- **FR-1.1:** Scrape TrustLLM leaderboard from https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html
  - Extract 16+ models across 8 trust dimensions
  - Parse HTML table structure → pandas DataFrame
  - Store format: `{benchmark_name: DataFrame[model_name, score]}`
- **FR-1.2:** Extract TruthfulQA leaderboard data from GitHub repository
  - Download CSV or scrape table
  - Consolidate ~12 models with truthfulness scores
- **FR-1.3:** Extract data from supplementary benchmarks (HaluBench, FinTrust, MultiTrust)
  - PDF table extraction → CSV conversion
  - Manual extraction if needed (supplement data)
- **FR-1.4:** Data validation requirements:
  - Verify n_models ≥ 10 per benchmark (exclude if insufficient)
  - Identify shared model sets across benchmarks
  - Verify ≥5 shared models for cross-benchmark pairs
  - Handle missing/incomplete data (remove affected benchmarks)
- **FR-1.5:** Unified data format:
  ```python
  benchmark_dict = {
      "TrustLLM-Truthfulness": DataFrame([model_name, score]),
      "TrustLLM-Safety": DataFrame([model_name, score]),
      "TruthfulQA": DataFrame([model_name, score]),
      # ... 5-10 total benchmarks
  }
  ```

**Acceptance Criteria:**
- 5-10 benchmarks loaded successfully
- Each benchmark has ≥10 models
- Data structure ready for statistical analysis
- Preprocessing logs saved to `data/extraction_log.txt`

---

### FR-2: Coefficient of Variation (CV) Computation
**Priority:** P0 (Critical)
**Rationale:** CV is the predictor variable in our hypothesis test

**Requirements:**
- **FR-2.1:** Implement CV computation function:
  ```python
  def compute_cv(scores: np.ndarray) -> float:
      """
      Coefficient of Variation: CV = σ/μ
      
      Args:
          scores: Array of benchmark scores for n models
      Returns:
          cv: Coefficient of variation (unitless ratio)
      """
      mean_score = np.mean(scores)
      std_score = np.std(scores, ddof=1)  # Sample std (n-1)
      cv = std_score / mean_score
      return cv
  ```
- **FR-2.2:** Compute CV for each benchmark in the corpus
- **FR-2.3:** Store results in structured format:
  ```python
  cv_results = {
      "benchmark_name": [list of names],
      "cv": [list of CV values],
      "mean": [list of means],
      "std": [list of stds],
      "n_models": [list of model counts]
  }
  ```
- **FR-2.4:** Validate CV computation:
  - Check for division by zero (mean=0)
  - Handle edge cases (all scores identical → CV=0)
  - Verify CV values are reasonable (typically 0.01-0.5 for LLM benchmarks)

**Acceptance Criteria:**
- CV computed for all 5-10 benchmarks
- No errors on edge cases
- Results saved to `results/cv_per_benchmark.csv`

---

### FR-3: Cross-Benchmark Ranking Correlation (Spearman ρ)
**Priority:** P0 (Critical)
**Rationale:** Mean Spearman ρ is the outcome variable in our hypothesis test

**Requirements:**
- **FR-3.1:** Implement pairwise Spearman correlation function:
  ```python
  def compute_cross_benchmark_rho(
      benchmark_a: pd.DataFrame,
      benchmark_b: pd.DataFrame,
      min_shared_models: int = 5
  ) -> Optional[float]:
      """
      Compute Spearman rank correlation for shared models.
      
      Args:
          benchmark_a: DataFrame with [model_name, score]
          benchmark_b: DataFrame with [model_name, score]
          min_shared_models: Minimum overlap required (default=5)
      Returns:
          rho: Spearman correlation or None if insufficient overlap
      """
      # Find shared models
      shared = set(benchmark_a.model_name) & set(benchmark_b.model_name)
      if len(shared) < min_shared_models:
          return None
      
      # Extract ranks for shared models
      a_shared = benchmark_a[benchmark_a.model_name.isin(shared)]
      b_shared = benchmark_b[benchmark_b.model_name.isin(shared)]
      
      # Rank within each benchmark
      a_ranks = a_shared.score.rank()
      b_ranks = b_shared.score.rank()
      
      # Spearman correlation
      rho, _ = spearmanr(a_ranks, b_ranks)
      return rho
  ```
- **FR-3.2:** Compute pairwise ρ for all benchmark pairs
- **FR-3.3:** For each benchmark, compute mean ρ across all valid pairs:
  ```python
  mean_rho_per_benchmark = {
      "benchmark_name": [],
      "mean_rho": [],  # Mean across all pairwise comparisons
      "n_pairs": [],   # Number of valid comparisons
      "pairwise_rhos": []  # List of individual ρ values
  }
  ```
- **FR-3.4:** Store full pairwise correlation matrix for visualization

**Acceptance Criteria:**
- Mean ρ computed for all benchmarks with ≥1 valid pair
- Pairwise matrix saved to `results/pairwise_rho_matrix.csv`
- Per-benchmark mean ρ saved to `results/mean_rho_per_benchmark.csv`

---

### FR-4: Hypothesis Test (Pearson Correlation)
**Priority:** P0 (Critical)
**Rationale:** Primary hypothesis test for MUST_WORK gate

**Requirements:**
- **FR-4.1:** Implement Pearson correlation test:
  ```python
  def test_cv_stability_correlation(
      cv_values: List[float],
      mean_rho_values: List[float]
  ) -> Tuple[float, float]:
      """
      Test H-E1: Pearson correlation between CV and mean ρ.
      
      Args:
          cv_values: List of CV per benchmark
          mean_rho_values: List of mean ρ per benchmark
      Returns:
          r: Pearson correlation coefficient
          p: Statistical significance (two-tailed)
      """
      r, p = pearsonr(cv_values, mean_rho_values)
      return r, p
  ```
- **FR-4.2:** Execute test with collected data
- **FR-4.3:** Gate evaluation logic:
  ```python
  gate_passed = (r < -0.5) and (p < 0.05)
  ```
- **FR-4.4:** Generate detailed report:
  - r value with 95% confidence interval
  - p-value (two-tailed)
  - Effect size interpretation
  - Statistical power post-hoc estimate
  - Gate decision (PASS/FAIL)

**Acceptance Criteria:**
- Pearson test executes successfully
- Results saved to `results/hypothesis_test_results.json`
- Gate decision clearly stated in report

---

### FR-5: Visualization Generation
**Priority:** P1 (High)
**Rationale:** Required for paper figures and result interpretation

**Requirements:**
- **FR-5.1:** Scatter plot (CV vs. mean ρ):
  - X-axis: CV (coefficient of variation)
  - Y-axis: Mean cross-benchmark Spearman ρ
  - Points: Each benchmark (labeled with benchmark name)
  - Regression line with 95% confidence interval
  - Annotate: r value, p-value, sample size n
  - Save to: `figures/cv_vs_rho_scatter.png`

- **FR-5.2:** Dual bar chart (per-benchmark CV and ρ):
  - Sort benchmarks by CV (low to high)
  - Side-by-side bars: CV (left), mean ρ (right)
  - Color coding: CV (blue), ρ (orange)
  - Visual check: Does high CV → low ρ pattern hold?
  - Save to: `figures/cv_rho_per_benchmark_bars.png`

- **FR-5.3:** Correlation matrix heatmap:
  - Pairwise Spearman ρ across all benchmark pairs
  - Color scale: red (low ρ, poor agreement) → green (high ρ, strong agreement)
  - Annotate cells with ρ values
  - Save to: `figures/pairwise_rho_heatmap.png`

- **FR-5.4:** Gate metrics comparison (mandatory):
  - Target metrics: r=-0.5, p=0.05
  - Actual metrics: actual r, actual p
  - Bar chart visualization
  - Save to: `figures/gate_metrics_comparison.png`

**Acceptance Criteria:**
- All 4 figures generated without errors
- Figures saved to `h-e1/figures/` folder
- High-resolution PNG format (300 DPI minimum)

---

### FR-6: Report Generation
**Priority:** P1 (High)
**Rationale:** Structured output for Phase 4.5 synthesis

**Requirements:**
- **FR-6.1:** Generate summary report (`04_validation.md`):
  - Hypothesis statement and gate type
  - Data collection summary (n benchmarks, n models per benchmark)
  - CV computation results (mean CV, range)
  - Cross-benchmark ρ results (mean ρ, range)
  - Hypothesis test results (r, p, 95% CI)
  - Gate decision (PASS/FAIL)
  - Interpretation and next steps
- **FR-6.2:** Export structured results to JSON:
  - `results/summary.json` with all key metrics
  - Machine-readable format for Phase 4.5 aggregation
- **FR-6.3:** Save raw data artifacts:
  - `data/benchmark_corpus.pkl` (pickled benchmark_dict)
  - `results/cv_per_benchmark.csv`
  - `results/mean_rho_per_benchmark.csv`
  - `results/pairwise_rho_matrix.csv`

**Acceptance Criteria:**
- Report follows validation template structure
- All data artifacts saved to specified paths
- JSON export validates against schema

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** P0 (Critical)
- **NFR-1.1:** Fixed random seed for any stochastic operations (though this analysis is deterministic)
- **NFR-1.2:** Version all dependencies (pandas, numpy, scipy versions)
- **NFR-1.3:** Log all preprocessing decisions (excluded benchmarks, missing data handling)
- **NFR-1.4:** Save raw extracted data before preprocessing

### NFR-2: Code Quality
**Priority:** P1 (High)
- **NFR-2.1:** Type hints for all functions
- **NFR-2.2:** Docstrings following NumPy style
- **NFR-2.3:** Unit tests for CV, Spearman ρ, Pearson test functions
- **NFR-2.4:** Linting with flake8 or ruff

### NFR-3: Performance
**Priority:** P2 (Medium)
- **NFR-3.1:** Analysis completes in <5 minutes on standard laptop
- **NFR-3.2:** Memory usage <500MB (small dataset)
- **NFR-3.3:** Efficient data structures (pandas DataFrames)

### NFR-4: Error Handling
**Priority:** P1 (High)
- **NFR-4.1:** Graceful handling of web scraping failures (retry logic, fallback to cached data)
- **NFR-4.2:** Validation errors for insufficient data (n<10 models, <5 benchmarks)
- **NFR-4.3:** Clear error messages for gate failures
- **NFR-4.4:** Logging to `logs/experiment.log`

---

## Dependencies and Constraints

### Technical Dependencies
- **Python:** 3.9+ (for type hints and dataclasses)
- **Libraries:**
  - `pandas>=1.5.0` (data manipulation)
  - `numpy>=1.24.0` (numerical operations)
  - `scipy>=1.10.0` (statistical tests: pearsonr, spearmanr)
  - `matplotlib>=3.7.0` (visualization)
  - `seaborn>=0.12.0` (heatmaps)
  - `beautifulsoup4>=4.11.0` (web scraping)
  - `requests>=2.28.0` (HTTP requests)

### Data Constraints
- **Minimum Sample Size:** 5 benchmarks (statistical power requirement from Phase 2B)
- **Model Count:** ≥10 models per benchmark (for valid CV estimation)
- **Overlap Requirement:** ≥5 shared models per benchmark pair (for valid Spearman ρ)
- **Data Availability:** Public leaderboards must be accessible (web scraping dependency)

### Hypothesis Constraints (from verification_state.yaml)
- **Type:** EXISTENCE (PoC validation only)
- **Gate:** MUST_WORK (pipeline-critical hypothesis)
- **Prerequisites:** None (foundation hypothesis)
- **Dependents:** H-M1, H-M2, H-C1 (blocked until H-E1 passes)

---

## Success Metrics

### Primary Success Metric
- **Pearson r < -0.5:** Negative moderate-to-strong correlation between CV and mean ρ
- **p < 0.05:** Statistical significance (two-tailed test)

### Secondary Success Metrics
- **Data Coverage:** 5-10 benchmarks successfully loaded
- **Code Execution:** No errors during analysis pipeline
- **Visualization Quality:** All 4 required figures generated

### Baseline Comparison
- **Null Hypothesis (H₀):** r ≈ 0, p > 0.05 (no correlation)
- **Expected Under H₁:** r ∈ [-0.7, -0.5], p < 0.05 (based on Phase 2B power analysis)

---

## Deliverables

### Code Artifacts
1. `src/data_extraction.py` - Web scraping and data loading
2. `src/meta_analysis.py` - BenchmarkMetaAnalysis class with CV, ρ, Pearson test
3. `src/visualization.py` - Figure generation functions
4. `src/main.py` - Orchestration script
5. `tests/test_meta_analysis.py` - Unit tests

### Data Artifacts
1. `data/benchmark_corpus.pkl` - Raw extracted data
2. `data/extraction_log.txt` - Preprocessing decisions
3. `results/cv_per_benchmark.csv` - CV computation results
4. `results/mean_rho_per_benchmark.csv` - Cross-benchmark stability
5. `results/pairwise_rho_matrix.csv` - Full correlation matrix

### Report Artifacts
1. `04_validation.md` - Structured validation report
2. `results/summary.json` - Machine-readable results
3. `figures/*.png` - All visualizations (4 required figures)

### Repository Structure
```
h-e1/
├── src/
│   ├── __init__.py
│   ├── data_extraction.py
│   ├── meta_analysis.py
│   ├── visualization.py
│   └── main.py
├── tests/
│   └── test_meta_analysis.py
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
├── logs/
│   └── experiment.log
├── 04_validation.md
└── README.md
```

---

## Risk Assessment

### High-Risk Items
1. **Data Availability:** Public leaderboards may be unavailable or reformatted
   - **Mitigation:** Cache extracted data, provide manual extraction fallback
2. **Insufficient Overlap:** Benchmarks may share <5 models
   - **Mitigation:** Expand benchmark corpus beyond minimum 5, use flexible overlap threshold
3. **Gate Failure:** r ≥ -0.5 or p ≥ 0.05 (hypothesis disproved)
   - **Mitigation:** Clear routing to Phase 0 for redesign, preserve partial results

### Medium-Risk Items
1. **Web Scraping Robustness:** HTML structure changes
   - **Mitigation:** Robust parsers with multiple extraction strategies
2. **Statistical Power:** n=5 benchmarks may have low power
   - **Mitigation:** Aim for 8-10 benchmarks, post-hoc power analysis

### Low-Risk Items
1. **Implementation Complexity:** Statistical analysis is straightforward
   - **Note:** Standard pandas + scipy operations, well-documented patterns
2. **Performance:** Small dataset (<1MB)
   - **Note:** Analysis completes in seconds, no optimization needed

---

## Timeline and Milestones

### Phase 4 Implementation (Estimated 4-6 hours)
1. **Data Extraction:** 2 hours
   - Web scraping implementation
   - Manual PDF extraction (if needed)
   - Data validation and consolidation
2. **Core Analysis:** 1 hour
   - BenchmarkMetaAnalysis class implementation
   - CV, Spearman ρ, Pearson test functions
3. **Visualization:** 1 hour
   - 4 required figures
   - Gate metrics comparison
4. **Testing and Validation:** 1-2 hours
   - Unit tests
   - End-to-end execution
   - Report generation

---

## Stakeholder Communication

### Key Stakeholders
- **Research Team:** Hypothesis author, verification pipeline owner
- **Paper Authors:** Phase 6 paper writing team (consumers of results)

### Communication Plan
- **Milestone Updates:** After each FR completion
- **Gate Decision:** Immediate notification on PASS/FAIL
- **Routing Decision:** If FAIL, communicate Phase 0 redesign requirement

---

## Appendix: Technical Specifications

### Data Schema
```python
# Benchmark dictionary schema
BenchmarkDict = Dict[str, pd.DataFrame]
# Each DataFrame has columns: [model_name: str, score: float]

# CV results schema
CVResults = {
    "benchmark_name": List[str],
    "cv": List[float],
    "mean": List[float],
    "std": List[float],
    "n_models": List[int]
}

# Spearman ρ results schema
RhoResults = {
    "benchmark_name": List[str],
    "mean_rho": List[float],
    "n_pairs": List[int],
    "pairwise_rhos": List[List[float]]
}

# Hypothesis test results schema
HypothesisTestResults = {
    "r": float,
    "p": float,
    "ci_lower": float,  # 95% CI lower bound
    "ci_upper": float,  # 95% CI upper bound
    "n": int,  # Sample size (number of benchmarks)
    "gate_passed": bool
}
```

### API Signatures (BenchmarkMetaAnalysis class)
```python
class BenchmarkMetaAnalysis:
    def __init__(self, min_models: int = 10, min_shared_models: int = 5):
        """Initialize meta-analysis with validation thresholds."""
        
    def compute_cv(self, benchmark_name: str, scores: np.ndarray) -> float:
        """Compute coefficient of variation for benchmark."""
        
    def compute_cross_benchmark_rho(
        self, 
        benchmark_a: pd.DataFrame, 
        benchmark_b: pd.DataFrame
    ) -> Optional[float]:
        """Compute Spearman rank correlation between benchmarks."""
        
    def analyze_cv_stability_correlation(
        self, 
        benchmark_dict: Dict[str, pd.DataFrame]
    ) -> Tuple[float, float, List[float], List[float]]:
        """
        Execute H-E1 hypothesis test.
        
        Returns:
            r: Pearson correlation (CV, mean_ρ)
            p: Statistical significance
            cv_values: CV per benchmark
            mean_rho_values: Mean ρ per benchmark
        """
```

---

**Status:** Ready for Phase 3 Architecture Design
**Next Steps:** Architecture Agent → Logic/Config Agents → Task Generation
