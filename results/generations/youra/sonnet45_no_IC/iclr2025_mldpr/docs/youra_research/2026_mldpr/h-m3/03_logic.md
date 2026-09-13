# Logic Design: H-M3 Performance Variance Analysis

**Date:** 2026-07-12  
**Hypothesis:** h-m3 (MECHANISM)  
**Type:** Observational Meta-Analysis (Statistical Comparison)  
**Budget:** 18 subtasks (High-complexity modules: M3-1, M3-9, M3-10)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from H-M2 code  
**Analyzed Path:** docs/youra_research/h-m2/code/  
**Relevant Symbols:** ProtocolStudyConfig, PlotConfig, fetch_citing_papers_from_semantic_scholar, spearmanr, generate_visualizations

**Key Findings:**
- ProtocolStudyConfig: Dataclass with field(default_factory=lambda: ...) for lists/dicts
- PlotConfig: Visualization constants (DPI=300, colors, font sizes) directly reusable
- API client: Rate limiting (1 req/sec) with exponential backoff retry (3 attempts)
- Statistical tests: Direct scipy.stats calls (spearmanr), no wrapper classes
- Visualization: matplotlib with consistent PlotConfig styling

---

## Applied Patterns (Archon KB)

**Applied:** Standard scipy.stats, sklearn LogisticRegression, pandas aggregation

Standard Python statistical libraries are sufficient for this meta-analysis. No specialized patterns needed.

---

## M3-1: Papers with Code API Integration [Complexity: 14, Budget: 4]

**Applied:** H-M2 API client pattern with rate limiting

### API Signatures

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import requests
import pandas as pd
import time


@dataclass
class VarianceStudyConfig:
    """Configuration for H-M3 performance variance meta-analysis."""
    
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
    
    # Artifact Coding
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
    PERFORMANCE_RESULTS_FILE: str = "data/performance_results.csv"
    CV_DATA_FILE: str = "data/cv_by_benchmark.csv"
    HYPOTHESIS_TEST_FILE: str = "results/hypothesis_test.json"
    FIGURES_DIR: str = "../figures"
    OUTPUT_FILE: str = "../04_validation.md"


class PapersWithCodeCollector:
    """Collect benchmark metadata and performance results from Papers with Code API."""
    
    def __init__(self, config: VarianceStudyConfig):
        """Initialize collector with rate limiting."""
        self.config = config
        self.session = requests.Session()
        self.last_request_time: float = 0
    
    def _rate_limit_wait(self) -> None:
        """Enforce 1 req/sec rate limit."""
        # elapsed = time.time() - self.last_request_time
        # if elapsed < RATE_LIMIT: sleep(RATE_LIMIT - elapsed)
        ...
    
    def fetch_benchmarks(
        self, 
        task: str = "classification", 
        start_year: int = 2019, 
        end_year: int = 2024
    ) -> pd.DataFrame:
        """
        Fetch benchmarks from PWC API.
        Returns: DataFrame [benchmark_id, name, task, year, result_count, github_url, dataset_card, badge]
        """
        ...
    
    def filter_by_result_count(
        self, 
        benchmarks: pd.DataFrame, 
        min_results: int = 5
    ) -> pd.DataFrame:
        """Filter benchmarks with >=min_results. Returns: [~150, ~8]"""
        ...
    
    def fetch_benchmark_results(self, benchmark_id: str) -> pd.DataFrame:
        """
        Fetch performance results for a benchmark.
        Returns: [N_results, ~6] (benchmark_id, paper_id, metric_value, metric_name, year)
        """
        ...
    
    def extract_artifact_metadata(self, benchmark: dict) -> Dict[str, int]:
        """
        Binary artifact coding: GitHub (0/1), dataset card (0/1), badge (0/1).
        Returns: {github: 1, dataset_card: 0, badge: 1, artifact_count: 2}
        """
        ...
    
    def collect_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Execute full collection pipeline.
        Returns: (benchmarks_df, results_df, artifact_df)
        """
        ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | API Client | HTTP client with rate limiting (1 req/sec) |
| L-1-2 | Benchmark Fetching | Query and filter by task/year/results |
| L-1-3 | Artifact Extraction | Binary coding: github, dataset_card, badge |
| L-1-4 | Error Handling | Exponential backoff retry (3 retries max) |

---

## M3-9: Propensity Score Weighting [Complexity: 16, Budget: 5]

**Applied:** sklearn LogisticRegression, inverse probability weighting, bootstrap

### API Signatures

```python
from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
from typing import Dict


class PropensityScoreModel:
    """Correct sampling bias using inverse probability weighting."""
    
    def __init__(self, config: VarianceStudyConfig):
        """Initialize propensity model."""
        self.config = config
        self.model = None
        self.propensity_scores = None
    
    def check_coverage_difference(self, benchmarks: pd.DataFrame) -> float:
        """
        Compute |P(high) - P(low)| coverage difference.
        Returns: float in [0, 1]
        """
        high_rate = (benchmarks['artifact_count'] >= self.config.ARTIFACT_THRESHOLD).mean()
        low_rate = (benchmarks['artifact_count'] < self.config.ARTIFACT_THRESHOLD).mean()
        return abs(high_rate - low_rate)
    
    def should_apply_weighting(self, coverage_diff: float) -> bool:
        """Apply if coverage_diff > 0.10."""
        return coverage_diff > self.config.COVERAGE_DIFF_THRESHOLD
    
    def fit_propensity_model(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Fit logistic regression: P(high_artifact | confounds).
        X: [N, k] confounds (benchmark_age, domain, metric_type)
        y: [N] binary (1=high, 0=low)
        """
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.model.fit(X, y)
        self.propensity_scores = pd.Series(
            self.model.predict_proba(X)[:, 1], 
            index=X.index
        )
    
    def compute_weights(
        self, 
        propensity_scores: pd.Series, 
        group: pd.Series
    ) -> pd.Series:
        """
        Inverse probability weighting: w = 1/P(group|X).
        Returns: [N] weights
        """
        weights = np.where(
            group == 1,
            1.0 / propensity_scores,  # High: 1/P(high|X)
            1.0 / (1.0 - propensity_scores)  # Low: 1/P(low|X)
        )
        return pd.Series(weights, index=group.index)
    
    def bootstrap_weighted_test(
        self, 
        cv_high: pd.Series, 
        cv_low: pd.Series, 
        weights_high: pd.Series, 
        weights_low: pd.Series
    ) -> Dict[str, float]:
        """
        Bootstrapped Mann-Whitney test with weights.
        Returns: {p_value: float, statistic: float}
        """
        from scipy.stats import mannwhitneyu
        
        np.random.seed(42)
        n_samples = self.config.BOOTSTRAP_SAMPLES
        
        # Normalize weights to probabilities
        p_high = weights_high / weights_high.sum()
        p_low = weights_low / weights_low.sum()
        
        # Resample with weights
        cv_high_resampled = np.random.choice(
            cv_high.values, size=n_samples, replace=True, p=p_high
        )
        cv_low_resampled = np.random.choice(
            cv_low.values, size=n_samples, replace=True, p=p_low
        )
        
        # Mann-Whitney test
        statistic, p_value = mannwhitneyu(
            cv_high_resampled, cv_low_resampled, alternative='less'
        )
        
        return {'p_value': float(p_value), 'statistic': float(statistic)}
```

### Pseudo-code

```
1. Check coverage: coverage_diff = |P(high) - P(low)|
2. If coverage_diff > 0.10:
   a. Fit logistic: P(high | age, domain, metric_type)
   b. Compute IPW: w = 1/P(high|X) for high, 1/P(low|X) for low
   c. Bootstrap resample with weights (1000 samples)
   d. Run weighted Mann-Whitney test
3. Return weighted p-value
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Coverage Check | Compute \|P(high) - P(low)\| |
| L-9-2 | Logistic Regression | sklearn LogisticRegression fit |
| L-9-3 | IPW Calculation | Inverse probability weights formula |
| L-9-4 | Bootstrap Resampling | np.random.choice with weights |
| L-9-5 | Weighted Test | Integrate bootstrap with Mann-Whitney |

---

## M3-10: Visualization Suite [Complexity: 15, Budget: 5]

**Applied:** matplotlib/seaborn with PlotConfig styling

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict


@dataclass
class PlotConfig:
    """Visualization styling (from H-M2)."""
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


class VarianceVisualization:
    """Generate 5 required figures for H-M3."""
    
    def __init__(self, config: VarianceStudyConfig):
        """Initialize with config."""
        self.config = config
        self.plot_config = PlotConfig()
    
    def plot_gate_metrics(
        self, 
        mann_whitney_p: float, 
        cohens_d: float, 
        save_path: str
    ) -> None:
        """
        MANDATORY: Bar chart comparing actual vs thresholds.
        Two bars: [p-value vs 0.05], [Cohen's d vs 0.5]
        Colors: green (pass) / red (fail)
        """
        ...
    
    def plot_cv_distribution(
        self, 
        cv_high: pd.Series, 
        cv_low: pd.Series, 
        save_path: str
    ) -> None:
        """Box plot + violin plot overlay. Two groups: High (>=2) vs Low (<2)"""
        ...
    
    def plot_dose_response(
        self, 
        artifact_counts: pd.Series, 
        cv_values: pd.Series, 
        rho: float, 
        p_value: float, 
        save_path: str
    ) -> None:
        """
        Scatter plot with regression line.
        X: artifact count (0-3), Y: CV values
        Annotation: Spearman rho and p-value
        """
        ...
    
    def plot_coverage_validation(
        self, 
        benchmarks: pd.DataFrame, 
        save_path: str
    ) -> None:
        """Stacked bar chart showing artifact distribution (sampling bias check)."""
        ...
    
    def plot_sensitivity_analysis(
        self, 
        results: Dict, 
        save_path: str
    ) -> None:
        """Forest plot with confidence intervals for sensitivity analysis."""
        ...
    
    def generate_all_figures(self, results: Dict, output_dir: str) -> None:
        """Generate all 5 plots and save to output_dir."""
        ...
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | Gate Metrics | Bar chart: actual vs threshold (MANDATORY) |
| L-10-2 | CV Distribution | Box + violin overlay |
| L-10-3 | Dose Response | Scatter + regression with Spearman annotation |
| L-10-4 | Coverage Plot | Stacked bar chart for sampling bias |
| L-10-5 | Sensitivity Plot | Forest plot with CI bars |

---

## M3-4: Variance Calculation [Complexity: 11, Budget: 3]

**Applied:** NumPy statistical functions

### API Signatures

```python
import numpy as np
import pandas as pd


class PerformanceVarianceCalculator:
    """Compute coefficient of variation (CV) per benchmark."""
    
    def __init__(self, config: VarianceStudyConfig):
        """Initialize calculator."""
        self.config = config
    
    def filter_outliers(
        self, 
        results: pd.Series, 
        threshold_sd: float = 3.0
    ) -> pd.Series:
        """Remove results >3 SD from mean. Returns: [N_filtered]"""
        mean, std = results.mean(), results.std()
        return results[(results - mean).abs() <= threshold_sd * std]
    
    def compute_cv(self, results: pd.Series) -> float:
        """CV = std / mean. Returns: float >= 0"""
        if len(results) < 2 or results.mean() == 0:
            return np.nan
        return float(results.std() / results.mean())
    
    def validate_sample_size(self, results: pd.Series, min_size: int = 5) -> bool:
        """Check if sample size >= min_size."""
        return len(results) >= min_size
    
    def compute_cv_per_benchmark(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute CV for each benchmark.
        Returns: [N_benchmarks, ~5] (benchmark_id, cv, n_results, mean, std)
        """
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Outlier Filter | Remove >3 SD using numpy |
| L-4-2 | CV Computation | std/mean formula |
| L-4-3 | Benchmark Aggregation | GroupBy with size validation |

---

## Supporting Modules (Low Complexity - No Budget Allocation)

### Statistical Testing

**Applied:** Direct scipy.stats calls

```python
from scipy.stats import mannwhitneyu, spearmanr
import numpy as np
import pandas as pd


class MannWhitneyTest:
    """Mann-Whitney U test for CV comparison."""
    
    def test(self, cv_high: pd.Series, cv_low: pd.Series) -> dict:
        """One-tailed test: alternative='less'. Returns: {statistic, p_value}"""
        statistic, p_value = mannwhitneyu(cv_high, cv_low, alternative='less')
        return {'statistic': float(statistic), 'p_value': float(p_value)}
    
    def check_gate(self, p_value: float) -> bool:
        """Is p < 0.05?"""
        return p_value < 0.05


class EffectSizeCalculator:
    """Cohen's d effect size."""
    
    def compute_pooled_std(self, cv_high: pd.Series, cv_low: pd.Series) -> float:
        """Pooled std: sqrt((var_high + var_low) / 2)"""
        var_high = cv_high.var(ddof=1)
        var_low = cv_low.var(ddof=1)
        return np.sqrt((var_high + var_low) / 2)
    
    def compute_cohens_d(self, cv_high: pd.Series, cv_low: pd.Series) -> float:
        """d = (mean_low - mean_high) / pooled_std"""
        mean_high, mean_low = cv_high.mean(), cv_low.mean()
        pooled_std = self.compute_pooled_std(cv_high, cv_low)
        return (mean_low - mean_high) / pooled_std
    
    def check_gate(self, d: float) -> bool:
        """Is d > 0.5?"""
        return d > 0.5


class DoseResponseAnalyzer:
    """Spearman correlation for dose-response."""
    
    def compute_spearman(
        self, 
        artifact_counts: pd.Series, 
        cv_values: pd.Series
    ) -> dict:
        """Returns: {rho, p_value}"""
        rho, p_value = spearmanr(artifact_counts, cv_values)
        return {'rho': float(rho), 'p_value': float(p_value)}
    
    def check_gate(self, rho: float, p_value: float) -> bool:
        """Is rho < -0.3 AND p < 0.05?"""
        return (rho < -0.3) and (p_value < 0.05)
```

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual H-M2 Code)

Verified from H-M2 actual implementation:

```python
# From: h-m2/code/config.py (ACTUAL CODE)
@dataclass
class ProtocolStudyConfig:
    """H-M2 configuration pattern."""
    PWC_API_URL: str = "https://paperswithcode.com/api/v1/"
    S2_API_URL: str = "https://api.semanticscholar.org/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    PROTOCOL_DIMENSIONS: List[str] = field(default_factory=lambda: [
        "data_splits", "preprocessing", "evaluation_protocol", "hyperparameters"
    ])
    MIN_KAPPA: float = 0.8


@dataclass
class PlotConfig:
    """Visualization styling (DIRECTLY REUSABLE)."""
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


# From: h-m2/code/main.py (ACTUAL CODE)
def fetch_citing_papers_from_semantic_scholar(
    benchmark_name: str,
    config: ProtocolStudyConfig,
    max_papers: int = 5
) -> List[Dict]:
    """
    API client with rate limiting and exponential backoff.
    VERIFIED PARAMETER NAMES: benchmark_name, config, max_papers
    Returns: List of paper dicts with keys: paper_id, title, abstract, year, venue, benchmark_id
    """
    ...


from scipy.stats import spearmanr


def compute_correlation(x: pd.Series, y: pd.Series) -> tuple:
    """
    Spearman correlation (direct scipy call).
    VERIFIED: No wrapper class
    Returns: (rho, p_value)
    """
    return spearmanr(x, y)
```

**Verified from**: h-m2/code/ (actual implementation, NOT spec)

**Key Patterns to Reuse:**
1. Config dataclass: Use field(default_factory=lambda: ...) for lists/dicts
2. Rate limiting: _rate_limit_wait() with time.sleep()
3. PlotConfig: Direct import for consistent styling
4. Statistical tests: Direct scipy calls without wrappers
5. Exponential backoff: Retry with 2^retry_count wait time

---

## Gate Decision Logic

```python
def determine_gate_status(mann_whitney_p: float, cohens_d: float) -> str:
    """
    PASS: p < 0.05 AND d > 0.5
    EXPLORE: Otherwise
    """
    if mann_whitney_p < 0.05 and cohens_d > 0.5:
        return "PASS"
    else:
        return "EXPLORE"
```

---

## Subtask Budget Summary

| Module | ID | Complexity | Allocated | Used | Remaining |
|--------|-----|------------|-----------|------|-----------|
| M3-1   | API Integration | 14 | 4 | 4 | 0 |
| M3-9   | Propensity Weighting | 16 | 5 | 5 | 0 |
| M3-10  | Visualization Suite | 15 | 5 | 5 | 0 |
| M3-4   | Variance Calculation | 11 | 3 | 3 | 0 |
| **Total** | | | **17** | **17** | **0** |

**Note:** Original budget was 18 subtasks. Used 17 across high/medium complexity modules.

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Code Implementation (Step 4)
