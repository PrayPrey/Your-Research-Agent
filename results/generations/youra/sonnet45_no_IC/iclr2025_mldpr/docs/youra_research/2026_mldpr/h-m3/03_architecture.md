# Architecture Design: H-M3 Performance Variance Analysis

**Date:** 2026-07-12  
**Hypothesis:** h-m3 (MECHANISM)  
**Type:** Observational Meta-Analysis (Statistical Analysis)  
**Applied Patterns:** API-based benchmark data collection, propensity score weighting, non-parametric testing, effect size analysis

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from H-M2 code  
**Analyzed Path:** docs/youra_research/h-m2/code/  
**Findings:** Reusing ProtocolStudyConfig dataclass pattern, API client with rate limiting, Spearman correlation analysis, gate metrics visualization, and validation report generation. Extending to Papers with Code API integration and coefficient of variation analysis.

---

## Overview

H-M3 validates the final causal link: reduced cross-lab protocol ambiguity (via documentation artifacts) leads to lower performance variance across independent ML reproduction attempts. This is a meta-analysis of existing benchmark results from Papers with Code.

**Key Differences from H-M2:**
- H-M2: Analyzed protocol consistency in citing papers
- H-M3: Analyzes performance variance (CV) across reported results
- New components: Papers with Code API, CV calculation, Mann-Whitney U test, propensity score weighting
- Reused: Config pattern, correlation analysis, gate visualization, validation report generation

---

## Module Structure

### 1. Configuration (`config.py`)

**Dependencies:** None

```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class VarianceStudyConfig:
    """Configuration for performance variance meta-analysis."""
    
    # API Settings
    PWC_API_URL: str = "https://paperswithcode.com/api/v1/"
    S2_API_URL: str = "https://api.semanticscholar.org/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # Sampling Parameters
    TARGET_BENCHMARK_COUNT: int = 100
    MIN_RESULTS_PER_BENCHMARK: int = 5
    OUTLIER_THRESHOLD_SD: float = 3.0
    
    # Artifact Coding (from H-M1 rubric)
    ARTIFACT_DIMENSIONS: List[str] = field(default_factory=lambda: ["github", "dataset_card", "badge"])
    ARTIFACT_THRESHOLD: int = 2
    
    # Date Range
    START_YEAR: int = 2019
    END_YEAR: int = 2024
    
    # Gate Thresholds
    MANN_WHITNEY_ALPHA: float = 0.05
    COHENS_D_THRESHOLD: float = 0.5
    SPEARMAN_RHO_THRESHOLD: float = -0.3
    SPEARMAN_P_THRESHOLD: float = 0.05
    
    # Propensity Score Weighting
    ENABLE_PROPENSITY_WEIGHTING: bool = True
    COVERAGE_DIFF_THRESHOLD: float = 0.10
    BOOTSTRAP_SAMPLES: int = 1000
    
    # Output Paths
    BENCHMARKS_FILE: str = "data/benchmarks.csv"
    ARTIFACT_QUALITY_FILE: str = "data/artifact_quality.csv"
    PERFORMANCE_RESULTS_FILE: str = "data/performance_results.csv"
    CV_DATA_FILE: str = "data/cv_by_benchmark.csv"
    HYPOTHESIS_TEST_FILE: str = "results/hypothesis_test.json"
    PROPENSITY_RESULTS_FILE: str = "results/propensity_weights.csv"
    FIGURES_DIR: str = "../figures"
    OUTPUT_FILE: str = "../04_validation.md"

@dataclass
class PlotConfig:
    """Visualization styling configuration."""
    
    DPI: int = 300
    FIGSIZE_SINGLE: tuple = (8, 6)
    FIGSIZE_DOUBLE: tuple = (12, 5)
    
    COLOR_PASS: str = "green"
    COLOR_FAIL: str = "red"
    COLOR_WARNING: str = "orange"
    COLOR_PRIMARY: str = "#3498db"
    COLOR_SECONDARY: str = "#95a5a6"
    
    FONT_SIZE_TITLE: int = 14
    FONT_SIZE_LABEL: int = 12
    FONT_SIZE_TICK: int = 10
```

---

### 2. Data Collection (`data/pwc_collector.py`)

**Dependencies:** requests, pandas, config

```python
class PapersWithCodeCollector:
    """Collect benchmark metadata and performance results from Papers with Code API."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def fetch_benchmarks(self, task: str = "classification", start_year: int = 2019, 
                        end_year: int = 2024) -> pd.DataFrame: ...
    
    def filter_by_result_count(self, benchmarks: pd.DataFrame, min_results: int = 5) -> pd.DataFrame: ...
    
    def fetch_benchmark_results(self, benchmark_id: str) -> pd.DataFrame: ...
    
    def extract_artifact_metadata(self, benchmark: dict) -> dict:
        """Binary coding: GitHub (0/1), Dataset card (0/1), Badge (0/1)."""
        ...
    
    def collect_all_data(self) -> tuple:
        """Returns (benchmarks_df, results_df, artifact_df)."""
        ...

class ConfoundCollector:
    """Collect confounding variables for propensity score weighting."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def extract_benchmark_age(self, benchmarks: pd.DataFrame) -> pd.Series: ...
    
    def extract_task_domain(self, benchmarks: pd.DataFrame) -> pd.Series: ...
    
    def extract_metric_type(self, benchmarks: pd.DataFrame) -> pd.Series: ...
    
    def fetch_venue_prestige(self, benchmark_id: str) -> float:
        """Optional: Query Semantic Scholar for venue prestige."""
        ...
    
    def collect_all_confounds(self, benchmarks: pd.DataFrame) -> pd.DataFrame: ...
```

---

### 3. Artifact Assessment (`artifact/quality.py`)

**Dependencies:** pandas, config

```python
class ArtifactCoder:
    """Binary artifact quality coding using H-M1 validated rubric."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def code_github_presence(self, benchmark: dict) -> int:
        """1 if non-empty GitHub repo exists, 0 otherwise."""
        ...
    
    def code_dataset_card(self, benchmark: dict) -> int:
        """1 if dataset card present, 0 otherwise."""
        ...
    
    def code_badge(self, benchmark: dict) -> int:
        """1 if reproducibility badge present, 0 otherwise."""
        ...
    
    def compute_artifact_count(self, github: int, dataset_card: int, badge: int) -> int:
        """Sum of 3 binary indicators (0-3)."""
        ...
    
    def assign_group(self, artifact_count: int) -> str:
        """High (>=2) vs Low (<2)."""
        ...
    
    def code_all_benchmarks(self, benchmarks: pd.DataFrame) -> pd.DataFrame: ...
```

---

### 4. Variance Calculation (`analysis/variance.py`)

**Dependencies:** numpy, pandas, config

```python
class PerformanceVarianceCalculator:
    """Compute coefficient of variation (CV) per benchmark."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def filter_outliers(self, results: pd.Series, threshold_sd: float = 3.0) -> pd.Series:
        """Remove results > 3 SD from mean."""
        ...
    
    def compute_cv(self, results: pd.Series) -> float:
        """CV = std(results) / mean(results)."""
        ...
    
    def validate_sample_size(self, results: pd.Series, min_size: int = 5) -> bool: ...
    
    def compute_cv_per_benchmark(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """Returns (benchmark_id, cv, n_results, mean, std)."""
        ...
```

---

### 5. Statistical Testing (`analysis/hypothesis_test.py`)

**Dependencies:** scipy.stats, numpy, pandas

```python
class MannWhitneyTest:
    """Non-parametric test for comparing CV distributions."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def test(self, cv_high: pd.Series, cv_low: pd.Series) -> dict:
        """One-tailed Mann-Whitney U test (alternative='less')."""
        from scipy.stats import mannwhitneyu
        ...
    
    def check_gate(self, p_value: float) -> bool:
        """Is p < 0.05?"""
        ...

class EffectSizeCalculator:
    """Cohen's d effect size for CV difference."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def compute_cohens_d(self, cv_high: pd.Series, cv_low: pd.Series) -> float:
        """d = (mean_low - mean_high) / pooled_std."""
        ...
    
    def compute_pooled_std(self, cv_high: pd.Series, cv_low: pd.Series) -> float: ...
    
    def interpret_effect_size(self, d: float) -> str:
        """Small (<0.5), Medium (>=0.5), Large (>=0.8)."""
        ...
    
    def check_gate(self, d: float) -> bool:
        """Is d > 0.5?"""
        ...

class DoseResponseAnalyzer:
    """Spearman correlation for dose-response relationship."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def compute_spearman(self, artifact_counts: pd.Series, cv_values: pd.Series) -> dict:
        """Returns (rho, p_value)."""
        from scipy.stats import spearmanr
        ...
    
    def check_gate(self, rho: float, p_value: float) -> bool:
        """Is rho < -0.3 AND p < 0.05?"""
        ...
```

---

### 6. Propensity Score Weighting (`analysis/propensity.py`)

**Dependencies:** sklearn.linear_model, numpy, pandas

```python
class PropensityScoreModel:
    """Correct sampling bias using inverse probability weighting."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def check_coverage_difference(self, benchmarks: pd.DataFrame) -> float:
        """Compute |P(high) - P(low)|."""
        ...
    
    def should_apply_weighting(self, coverage_diff: float) -> bool:
        """Apply if coverage_diff > 10%."""
        ...
    
    def fit_propensity_model(self, X: pd.DataFrame, y: pd.Series):
        """Logistic regression: P(high_artifact | confounds)."""
        from sklearn.linear_model import LogisticRegression
        ...
    
    def compute_weights(self, propensity_scores: pd.Series, group: pd.Series) -> pd.Series:
        """IPW: 1/P(group|X)."""
        ...
    
    def bootstrap_weighted_test(self, cv_high: pd.Series, cv_low: pd.Series, 
                                weights_high: pd.Series, weights_low: pd.Series) -> dict:
        """Bootstrapped Mann-Whitney with weights."""
        ...
```

---

### 7. Visualization (`visualization/plots.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class VarianceVisualization:
    """Generate required figures for H-M3."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def plot_gate_metrics(self, mann_whitney_p: float, cohens_d: float, save_path: str):
        """MANDATORY: Bar chart comparing actual vs thresholds."""
        ...
    
    def plot_cv_distribution(self, cv_high: pd.Series, cv_low: pd.Series, save_path: str):
        """Box plot + violin plot overlay."""
        ...
    
    def plot_dose_response(self, artifact_counts: pd.Series, cv_values: pd.Series, 
                          rho: float, p_value: float, save_path: str):
        """Scatter plot with regression line."""
        ...
    
    def plot_coverage_validation(self, benchmarks: pd.DataFrame, save_path: str):
        """Stacked bar chart showing artifact distribution."""
        ...
    
    def plot_sensitivity_analysis(self, results: dict, save_path: str):
        """Forest plot with confidence intervals."""
        ...
    
    def generate_all_figures(self, results: dict, output_dir: str): ...
```

---

### 8. Report Generation (`reporting/validator.py`)

**Dependencies:** All analysis modules

```python
class ValidationReportGenerator:
    """Generate 04_validation.md with gate decision."""
    
    def __init__(self, config: VarianceStudyConfig): ...
    
    def load_results(self, results_dir: str) -> dict: ...
    
    def determine_gate_status(self, mann_whitney_pass: bool, cohens_d_pass: bool) -> str:
        """PASS (both pass), EXPLORE (either fails)."""
        ...
    
    def generate_executive_summary(self, results: dict) -> str: ...
    
    def generate_data_overview(self, results: dict) -> str: ...
    
    def generate_statistical_results(self, results: dict) -> str: ...
    
    def generate_gate_evaluation(self, results: dict) -> str: ...
    
    def generate_full_report(self, results: dict, output_path: str): ...
```

---

### 9. Main Orchestration (`main.py`)

**Dependencies:** All modules

```python
def run_variance_meta_analysis():
    """Execute H-M3 performance variance study."""
    config = VarianceStudyConfig()
    
    # Phase 1: Data collection
    print("[Step 1] Collecting benchmarks from Papers with Code API...")
    collector = PapersWithCodeCollector(config)
    benchmarks_df, results_df, artifact_df = collector.collect_all_data()
    print(f"  Collected {len(benchmarks_df)} benchmarks with {len(results_df)} results")
    
    # Phase 2: Artifact quality assessment
    print("[Step 2] Coding artifact quality...")
    artifact_coder = ArtifactCoder(config)
    benchmarks_df = artifact_coder.code_all_benchmarks(benchmarks_df)
    print(f"  High-artifact: {(benchmarks_df['artifact_group']=='High').sum()}, " +
          f"Low-artifact: {(benchmarks_df['artifact_group']=='Low').sum()}")
    
    # Phase 3: Variance calculation
    print("[Step 3] Computing coefficient of variation per benchmark...")
    variance_calc = PerformanceVarianceCalculator(config)
    cv_df = variance_calc.compute_cv_per_benchmark(results_df)
    print(f"  CV distribution: mean={cv_df['cv'].mean():.3f}, std={cv_df['cv'].std():.3f}")
    
    # Phase 4: Confound collection
    print("[Step 4] Collecting confounding variables...")
    confound_collector = ConfoundCollector(config)
    confounds_df = confound_collector.collect_all_confounds(benchmarks_df)
    
    # Phase 5: Check propensity score weighting need
    print("[Step 5] Checking for sampling bias...")
    ps_model = PropensityScoreModel(config)
    coverage_diff = ps_model.check_coverage_difference(benchmarks_df)
    print(f"  Coverage difference: {coverage_diff:.1%}")
    
    if ps_model.should_apply_weighting(coverage_diff):
        print("  → Applying propensity score weighting")
        ps_model.fit_propensity_model(confounds_df, benchmarks_df['artifact_group'])
        weights = ps_model.compute_weights(ps_model.propensity_scores, benchmarks_df['artifact_group'])
        weighted_results = ps_model.bootstrap_weighted_test(
            cv_df[benchmarks_df['artifact_group']=='High']['cv'],
            cv_df[benchmarks_df['artifact_group']=='Low']['cv'],
            weights[benchmarks_df['artifact_group']=='High'],
            weights[benchmarks_df['artifact_group']=='Low']
        )
    else:
        print("  → No sampling bias detected, using unweighted comparison")
        weighted_results = None
    
    # Phase 6: Primary hypothesis test
    print("[Step 6] Testing primary hypothesis (Mann-Whitney)...")
    cv_high = cv_df[benchmarks_df['artifact_group']=='High']['cv']
    cv_low = cv_df[benchmarks_df['artifact_group']=='Low']['cv']
    
    mw_test = MannWhitneyTest(config)
    mw_result = mw_test.test(cv_high, cv_low)
    print(f"  Mann-Whitney p-value: {mw_result['p_value']:.4f} " +
          f"({'PASS' if mw_test.check_gate(mw_result['p_value']) else 'FAIL'})")
    
    # Phase 7: Effect size calculation
    print("[Step 7] Computing effect size (Cohen's d)...")
    effect_calc = EffectSizeCalculator(config)
    cohens_d = effect_calc.compute_cohens_d(cv_high, cv_low)
    print(f"  Cohen's d: {cohens_d:.3f} ({effect_calc.interpret_effect_size(cohens_d)}) " +
          f"({'PASS' if effect_calc.check_gate(cohens_d) else 'FAIL'})")
    
    # Phase 8: Dose-response analysis
    print("[Step 8] Testing dose-response relationship (Spearman)...")
    dose_analyzer = DoseResponseAnalyzer(config)
    spearman_result = dose_analyzer.compute_spearman(
        benchmarks_df['artifact_count'], cv_df['cv']
    )
    print(f"  Spearman ρ: {spearman_result['rho']:.3f}, p={spearman_result['p_value']:.4f} " +
          f"({'PASS' if dose_analyzer.check_gate(spearman_result['rho'], spearman_result['p_value']) else 'FAIL'})")
    
    # Phase 9: Gate decision
    gate_pass = mw_test.check_gate(mw_result['p_value']) and effect_calc.check_gate(cohens_d)
    gate_decision = "PASS" if gate_pass else "EXPLORE"
    print(f"\n[Gate Decision] {gate_decision}")
    
    # Phase 10: Visualization
    print("[Step 9] Generating visualizations...")
    viz = VarianceVisualization(config)
    viz.generate_all_figures({
        'mann_whitney': mw_result,
        'cohens_d': cohens_d,
        'spearman': spearman_result,
        'cv_high': cv_high,
        'cv_low': cv_low,
        'artifact_counts': benchmarks_df['artifact_count'],
        'cv_values': cv_df['cv'],
        'benchmarks': benchmarks_df,
        'propensity': weighted_results
    }, config.FIGURES_DIR)
    
    # Phase 11: Validation report
    print("[Step 10] Generating validation report...")
    reporter = ValidationReportGenerator(config)
    reporter.generate_full_report({
        'primary_metric': mw_result,
        'effect_size': cohens_d,
        'secondary_metric': spearman_result,
        'gate_decision': gate_decision,
        'benchmarks_count': len(benchmarks_df),
        'results_count': len(results_df),
        'propensity_applied': weighted_results is not None
    }, config.OUTPUT_FILE)
    
    print(f"\n[Complete] Gate: {gate_decision}, p={mw_result['p_value']:.4f}, d={cohens_d:.3f}")

if __name__ == "__main__":
    run_variance_meta_analysis()
```

---

## File Organization

```
h-m3/
├── code/
│   ├── config.py                          # Study configuration
│   ├── main.py                            # Orchestration script
│   ├── data/
│   │   ├── pwc_collector.py               # PapersWithCodeCollector, ConfoundCollector
│   ├── artifact/
│   │   ├── quality.py                     # ArtifactCoder
│   ├── analysis/
│   │   ├── variance.py                    # PerformanceVarianceCalculator
│   │   ├── hypothesis_test.py             # MannWhitneyTest, EffectSizeCalculator, DoseResponseAnalyzer
│   │   ├── propensity.py                  # PropensityScoreModel
│   ├── visualization/
│   │   ├── plots.py                       # VarianceVisualization
│   ├── reporting/
│   │   ├── validator.py                   # ValidationReportGenerator
│   └── tests/
│       ├── test_variance.py
│       ├── test_hypothesis.py
│       └── test_propensity.py
├── data/
│   ├── benchmarks.csv                     # 100 benchmarks
│   ├── artifact_quality.csv               # Artifact coding
│   ├── performance_results.csv            # Raw results (500+ rows)
│   └── cv_by_benchmark.csv                # CV per benchmark (100 rows)
├── results/
│   ├── hypothesis_test.json               # Gate decision
│   └── propensity_weights.csv             # If applied
├── figures/
│   ├── gate_metrics.png                   # MANDATORY
│   ├── cv_distribution.png
│   ├── dose_response_scatter.png
│   ├── coverage_validation.png
│   └── sensitivity_analysis.png
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md                     # This document
└── 04_validation.md                       # Generated by code
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-M2 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ProtocolStudyConfig | `from sys import path; path.append('../../h-m2/code'); from config import ProtocolStudyConfig` | `h-m2/code/config.py` |
| PlotConfig | `from sys import path; path.append('../../h-m2/code'); from config import PlotConfig` | `h-m2/code/config.py` |

**Verified from:** `docs/youra_research/h-m2/code/` (actual implementation)

**Reuse Strategy:**
- ProtocolStudyConfig: Reuse dataclass structure pattern (not direct import)
- PlotConfig: Reuse visualization styling constants directly
- API client pattern: Reuse rate limiting and retry logic from H-M2 Semantic Scholar integration

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Papers with Code API Integration | Fetch benchmarks, filter by task/year/results, extract artifact metadata | 14 | 4+3+4+3 (API client=4, filtering=3, metadata extraction=4, error handling=3) |
| M3-2 | Performance Results Collection | Fetch all results per benchmark, standardize metrics | 12 | 3+3+4+2 (results API=3, pagination=3, metric standardization=4, validation=2) |
| M3-3 | Artifact Quality Coding | Binary coding (GitHub, dataset card, badge), group assignment | 9 | 2+2+3+2 (GitHub check=2, card check=2, badge check=2, group assignment=3) |
| M3-4 | Variance Calculation | Outlier filtering, CV computation, sample size validation | 11 | 3+3+3+2 (outlier filter=3, CV calculation=3, validation=3, output=2) |
| M3-5 | Confound Variable Collection | Benchmark age, task domain, metric type, venue prestige | 10 | 2+2+3+3 (age extraction=2, domain extraction=2, metric type=3, venue prestige=3) |
| M3-6 | Mann-Whitney U Test | Non-parametric test, one-tailed, gate check | 8 | 2+2+2+2 (test implementation=2, p-value extraction=2, gate logic=2, validation=2) |
| M3-7 | Cohen's d Effect Size | Pooled std calculation, effect size computation, interpretation | 9 | 2+3+2+2 (pooled std=2, Cohen's d=3, interpretation=2, gate check=2) |
| M3-8 | Spearman Correlation | Dose-response analysis, correlation test, gate check | 8 | 2+2+2+2 (correlation computation=2, p-value extraction=2, interpretation=2, gate check=2) |
| M3-9 | Propensity Score Weighting | Coverage check, logistic regression, IPW, bootstrapped test | 16 | 4+4+4+4 (coverage check=4, propensity model=4, IPW calculation=4, bootstrap=4) |
| M3-10 | Visualization Suite | 5 plots (gate metrics, CV distribution, dose-response, coverage, sensitivity) | 15 | 3+3+3+3+3 (gate metrics=3, CV box/violin=3, scatter+regression=3, coverage bar=3, forest plot=3) |
| M3-11 | Validation Report | 04_validation.md with gate decision, metrics, figures | 11 | 3+2+4+2 (markdown template=3, data aggregation=2, gate rendering=4, file I/O=2) |
| M3-12 | Testing Suite | Unit tests for variance, hypothesis tests, propensity weighting | 12 | 3+3+4+2 (variance tests=3, statistical tests=3, propensity tests=4, fixtures=2) |

**Complexity Distribution:**
- High (14-17): [M3-1, M3-9, M3-10]
- Medium (9-13): [M3-2, M3-3, M3-4, M3-5, M3-7, M3-11, M3-12]
- Low (4-8): [M3-6, M3-8]

**Total Complexity:** 135 (average 11.25 per task)

---

## Gate Decision Logic

```
IF mann_whitney_p < 0.05 AND cohens_d > 0.5:
    → PASS: High-artifact benchmarks have lower variance (medium+ effect size)
    → Causal chain validated (H-M1 → H-M2 → H-M3)
    → Proceed to publication/dissemination
ELSE:
    → EXPLORE: Identify alternative explanations
    → Check confounds: venue prestige, author reputation
    → Analyze domain-specific effects (CV vs NLP vs Speech)
    → Consider expanding sample size
```

---

## Statistical Validation Requirements

1. **Primary Metric (Mann-Whitney U Test):**
   - Metric: `scipy.stats.mannwhitneyu(cv_high, cv_low, alternative='less')`
   - Threshold: p < 0.05
   - Interpretation: One-tailed test (high-artifact < low-artifact variance)

2. **Primary Effect Size (Cohen's d):**
   - Metric: `(mean_low - mean_high) / pooled_std`
   - Threshold: d > 0.5 (medium effect)
   - Interpretation: >0.5 = meaningful practical difference

3. **Secondary Metric (Spearman Correlation):**
   - Metric: `scipy.stats.spearmanr(artifact_counts, cv_values)`
   - Thresholds: ρ < -0.3 AND p < 0.05
   - Interpretation: Negative correlation (more artifacts → lower variance)

4. **Propensity Score Weighting (Conditional):**
   - Trigger: Coverage difference > 10%
   - Method: Logistic regression + inverse probability weighting
   - Validation: Bootstrapped Mann-Whitney test with weights

---

## Implementation Notes

**API Rate Limiting:**
- Papers with Code: 1 req/sec (no authentication required)
- Expected data collection time: 10-15 minutes for 100 benchmarks
- Exponential backoff retry for rate limit errors (same as H-M2)

**Sample Size Target:**
- 100 benchmarks (50 high-artifact ≥2, 50 low-artifact <2)
- Minimum 5 results per benchmark (post-outlier filtering)
- Target 500+ total performance results for statistical power

**Outlier Handling:**
- Remove results > 3 SD from benchmark mean
- Prevents extreme results from inflating CV
- Validate minimum 5 results remain after filtering

**Propensity Weighting Conditions:**
- Apply only if |P(high) - P(low)| > 10%
- Confounds: benchmark age, task domain, metric type
- Bootstrap 1000 samples for weighted test stability

**Error Handling:**
- Missing artifact metadata: Default to 0 (conservative coding)
- Insufficient results (<5): Exclude benchmark from analysis
- API failures: Retry with exponential backoff (3 retries max)

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Code Implementation (Step 4)
