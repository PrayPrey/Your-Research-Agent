# Logic Design: H-M1 - Community Engagement Correlation Study

**Date:** 2026-07-12  
**Hypothesis:** H-M1 (MECHANISM - INCREMENTAL)  
**Type:** Observational Correlation Study (GitHub API + Statistical Analysis)  
**Author:** Logic Agent  
**Status:** DRAFT v1.0  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from H-E1 actual code  
**Analyzed Path:** h-e1/src/  
**Relevant Symbols:** DataCollector.collect_dataset(), DocumentationScorer.score_repository()  
**Note:** H-M1 loads DCS_3 scores from H-E1 validation results CSV but does NOT import H-E1 code modules. Only data dependency exists.

---

## Applied Patterns

**Applied:** Data Pipeline Pattern (observational correlation analysis)  
**Applied:** Retry Pattern with Exponential Backoff (GitHub API resilience)  
**Applied:** Statistical Analysis Pattern (scipy correlation + bootstrap CI)

---

## M-1: H-E1 Data Integration (Complexity: 6, Budget: 0)

Standard CSV loading, no logic subtasks needed.

### API Signatures

```python
from typing import Optional, Tuple
import pandas as pd
from pathlib import Path

# src/data_loading/h_e1_loader.py
class HE1DataLoader:
    def __init__(self, h_e1_path: str):
        """Initialize H-E1 data loader. h_e1_path: path to validation_results.csv"""
        self.h_e1_path = Path(h_e1_path)
    
    def load_dcs_scores(self) -> pd.DataFrame:
        """Load DCS_3 scores. Returns: [N=100, cols: repo_id, dcs_3_score, t0_date]"""
        ...
    
    def validate_dcs_data(self, df: pd.DataFrame) -> bool:
        """Validate DCS data. df: DataFrame -> bool (checks N=100, score range [0,3])"""
        ...
```

---

## M-2: GitHub Metrics Collection (Complexity: 14, Budget: 3)

High-complexity task with API integration, temporal windowing, rate limit handling.

### API Signatures

```python
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd
from github import Github
import time

# src/data_collection/github_collector.py
class GitHubMetricsCollector:
    def __init__(self, github_token: str, max_retries: int = 3):
        """Initialize GitHub API client. github_token: PAT for authentication"""
        self.github = Github(github_token)
        self.max_retries = max_retries
    
    def collect_commits_per_month(
        self, 
        repo_id: str, 
        t0: datetime, 
        t90: datetime
    ) -> float:
        """Collect commits metric. repo_id: str, t0: datetime, t90: datetime -> float"""
        ...
    
    def collect_unique_contributors(
        self, 
        repo_id: str, 
        commits: List
    ) -> int:
        """Count unique contributors. commits: List[Commit] -> int (unique authors)"""
        ...
    
    def collect_median_issue_response(
        self, 
        repo_id: str, 
        t0: datetime, 
        t90: datetime
    ) -> Optional[float]:
        """Calculate median issue response time. Returns: float (days) or None (<5 issues)"""
        ...
    
    def collect_repository_age(
        self, 
        repo_id: str, 
        t90: datetime
    ) -> int:
        """Calculate repo age. t90: datetime -> int (age in days at T90)"""
        ...
    
    def collect_all_metrics(self, repo_list: pd.DataFrame) -> pd.DataFrame:
        """Collect all metrics. repo_list: [repo_id, t0_date] -> [repo_id + 4 metrics]"""
        ...
    
    def _exponential_backoff_retry(self, func, *args, **kwargs):
        """Retry with exponential backoff. func: callable -> result or raise"""
        ...
    
    def _check_rate_limit(self) -> Tuple[int, int]:
        """Check rate limit. Returns: (remaining_calls, reset_timestamp)"""
        ...
```

### Algorithm: Exponential Backoff Retry

```
Input: func (API call), max_retries=3
Output: API result or raise exception

FOR attempt in range(max_retries):
    TRY:
        result = func()
        RETURN result
    EXCEPT RateLimitExceeded:
        IF attempt == max_retries - 1:
            RAISE
        wait_time = 2^attempt * 60  # 1min, 2min, 4min
        log(f"Rate limit hit, waiting {wait_time}s...")
        sleep(wait_time)
    EXCEPT Timeout:
        IF attempt == max_retries - 1:
            RAISE
        wait_time = 2^attempt * 10  # 10s, 20s, 40s
        sleep(wait_time)

RAISE Exception("Max retries exceeded")
```

### Algorithm: Median Issue Response Time

```
Input: repo_id (str), t0 (datetime), t90 (datetime)
Output: median_response_time (float days) or None

issues = repo.get_issues(since=t0, until=t90, state='all')
response_times = []

FOR issue in issues:
    IF issue.created_at < t0 OR issue.created_at > t90:
        CONTINUE
    
    first_response = None
    
    # Check for comments
    comments = issue.get_comments()
    IF comments.totalCount > 0:
        first_comment = comments[0]
        first_response = first_comment.created_at
    
    # Check for close event
    IF issue.closed_at IS NOT None:
        IF first_response IS None OR issue.closed_at < first_response:
            first_response = issue.closed_at
    
    IF first_response IS NOT None:
        response_time = (first_response - issue.created_at).days
        response_times.append(response_time)

IF len(response_times) < 5:
    RETURN None  # Insufficient data

RETURN median(response_times)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | GitHub API Integration | PyGithub client initialization with authentication and rate limit checks |
| L-2-2 | Temporal Windowing Logic | T0-T90 filtering for commits, issues, contributors |
| L-2-3 | Retry & Error Handling | Exponential backoff for rate limits, timeout handling, null data handling |

---

## M-3: Data Validation Pipeline (Complexity: 10, Budget: 2)

Medium-complexity task with outlier detection and quality gates.

### API Signatures

```python
from scipy.stats import zscore
from typing import Tuple

# src/preprocessing/validator.py
class DataValidator:
    def __init__(self, quality_threshold: float = 0.95):
        """Initialize validator. quality_threshold: min fraction of complete data"""
        self.quality_threshold = quality_threshold
    
    def check_completeness(self, df: pd.DataFrame) -> Tuple[int, int]:
        """Check completeness. df: DataFrame -> (complete_count, total_count)"""
        ...
    
    def detect_outliers(
        self, 
        df: pd.DataFrame, 
        z_threshold: float = 3.0
    ) -> pd.Series:
        """Detect outliers. df: DataFrame -> Series[bool] (outlier flags)"""
        ...
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values. df: DataFrame -> cleaned_df (drops rows with critical nulls)"""
        ...
    
    def export_cleaned_data(self, df: pd.DataFrame, output_path: str) -> None:
        """Export cleaned data. df: DataFrame -> CSV file"""
        ...
```

### Algorithm: Z-Score Outlier Detection

```
Input: df (DataFrame), z_threshold (float = 3.0)
Output: outlier_flags (Series[bool])

continuous_cols = ['commits_per_month', 'unique_contributors', 'repo_age_days']
outlier_flags = pd.Series([False] * len(df))

FOR col in continuous_cols:
    z_scores = zscore(df[col])
    col_outliers = abs(z_scores) > z_threshold
    outlier_flags = outlier_flags | col_outliers
    
    n_outliers = col_outliers.sum()
    log(f"{col}: {n_outliers} outliers detected (|z| > {z_threshold})")

RETURN outlier_flags
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Z-Score Outlier Detection | Scipy zscore calculation for continuous metrics |
| L-3-2 | Quality Gate Validation | Completeness check (≥95% rule) with early exit on failure |

---

## M-4: Correlation Analysis Engine (Complexity: 12, Budget: 3)

High-complexity task with Spearman, partial correlation, bootstrap CI.

### API Signatures

```python
from scipy.stats import spearmanr
from pingouin import partial_corr
import numpy as np
from typing import Dict, Tuple, List

# src/analysis/correlation_analyzer.py
class CorrelationAnalyzer:
    def __init__(self, random_seed: int = 42):
        """Initialize analyzer. random_seed: int for bootstrap reproducibility"""
        self.random_seed = random_seed
        np.random.seed(random_seed)
    
    def compute_spearman(
        self, 
        x: pd.Series, 
        y: pd.Series, 
        one_tailed: bool = True
    ) -> Dict:
        """Spearman correlation. x, y: Series -> {rho, p_value_two_tailed, p_value_one_tailed}"""
        ...
    
    def compute_partial_correlation(
        self, 
        df: pd.DataFrame, 
        x: str, 
        y: str, 
        covar: str
    ) -> Dict:
        """Partial correlation. df: DataFrame -> {partial_rho, partial_p}"""
        ...
    
    def bootstrap_confidence_interval(
        self, 
        x: pd.Series, 
        y: pd.Series, 
        n_iterations: int = 10000
    ) -> Tuple[float, float]:
        """Bootstrap CI. x, y: Series -> (ci_lower, ci_upper)"""
        ...
    
    def analyze_all_metrics(self, df: pd.DataFrame) -> Dict:
        """Analyze all metrics. df: DataFrame -> results_dict"""
        ...
```

### Algorithm: Bootstrap Confidence Interval

```
Input: x (Series), y (Series), n_iterations (int = 10000)
Output: (ci_lower, ci_upper)

n = len(x)
bootstrap_rhos = []

FOR i in range(n_iterations):
    # Resample with replacement
    indices = np.random.choice(n, size=n, replace=True)
    x_resample = x.iloc[indices]
    y_resample = y.iloc[indices]
    
    # Compute Spearman ρ
    rho, _ = spearmanr(x_resample, y_resample)
    bootstrap_rhos.append(rho)

# Calculate 95% CI (2.5th and 97.5th percentiles)
ci_lower = np.percentile(bootstrap_rhos, 2.5)
ci_upper = np.percentile(bootstrap_rhos, 97.5)

RETURN (ci_lower, ci_upper)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Spearman Correlation | Scipy spearmanr with one-tailed p-value conversion |
| L-4-2 | Partial Correlation | Pingouin partial_corr integration with age control |
| L-4-3 | Bootstrap CI | Resampling loop with percentile CI calculation |

---

## M-5: Gate Check System (Complexity: 8, Budget: 0)

Standard threshold checks, no logic subtasks needed.

### API Signatures

```python
# src/analysis/gate_checker.py
class GateChecker:
    def __init__(
        self, 
        primary_threshold: float = 0.30, 
        secondary_threshold: float = 0.25
    ):
        """Initialize gate checker. primary_threshold: min ρ for primary gate"""
        self.primary_threshold = primary_threshold
        self.secondary_threshold = secondary_threshold
    
    def check_primary_gate(self, rho: float, p_value: float) -> Dict[str, bool]:
        """Check primary gate. rho, p_value: float -> {gate_pass, reason}"""
        ...
    
    def check_secondary_gate(
        self, 
        partial_rho: float, 
        partial_p: float
    ) -> Dict[str, bool]:
        """Check secondary gate. Returns: {gate_pass, reason}"""
        ...
    
    def determine_routing(self, results: Dict) -> Dict:
        """Determine routing. results: Dict -> {next_phase, action}"""
        ...
```

---

## M-6: Visualization Suite (Complexity: 9, Budget: 0)

Standard matplotlib/seaborn charts, no logic subtasks needed.

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns

# src/visualization/plotter.py
class CorrelationVisualizer:
    def __init__(self, output_dir: str = "figures"):
        """Initialize visualizer. output_dir: str (figure save directory)"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def plot_primary_scatter(
        self, 
        df: pd.DataFrame, 
        rho: float, 
        p_value: float
    ) -> None:
        """Scatter plot. df: DataFrame -> saves to h1_primary_correlation.png"""
        ...
    
    def plot_correlation_matrix(self, df: pd.DataFrame) -> None:
        """Heatmap. df: DataFrame -> correlation_matrix.png"""
        ...
    
    def plot_partial_comparison(
        self, 
        raw_rho: float, 
        partial_rho: float, 
        ci_raw: Tuple, 
        ci_partial: Tuple
    ) -> None:
        """Bar chart comparison. Saves to partial_correlation_comparison.png"""
        ...
    
    def plot_component_correlations(self, df: pd.DataFrame) -> None:
        """Component scatter plots. df: DataFrame -> component_level_correlation.png"""
        ...
    
    def generate_all_figures(self, df: pd.DataFrame, results: Dict) -> None:
        """Generate all figures. Wrapper for all plot methods"""
        ...
```

---

## M-7: Pipeline Orchestration (Complexity: 11, Budget: 0)

Sequential execution, no complex logic needed.

### API Signatures

```python
from typing import Dict
import logging

# src/pipeline.py
class CorrelationPipeline:
    def __init__(self, config: dict):
        """Initialize pipeline. config: dict (from config.yaml)"""
        self.config = config
        self.loader = HE1DataLoader(config['data_sources']['h_e1_path'])
        self.collector = GitHubMetricsCollector(...)
        self.validator = DataValidator(...)
        self.analyzer = CorrelationAnalyzer(...)
        self.gate_checker = GateChecker(...)
        self.visualizer = CorrelationVisualizer(...)
    
    def run_data_loading(self) -> pd.DataFrame:
        """Phase 1: Load H-E1 data. Returns: dcs_df [N=100, 3 cols]"""
        ...
    
    def run_github_collection(self, dcs_df: pd.DataFrame) -> pd.DataFrame:
        """Phase 2: Collect GitHub metrics. dcs_df -> merged_df [N=100, 7 cols]"""
        ...
    
    def run_validation(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """Phase 3: Validate data. merged_df -> clean_df [N≥95, 7 cols]"""
        ...
    
    def run_correlation_analysis(self, clean_df: pd.DataFrame) -> Dict:
        """Phase 4: Statistical analysis. clean_df -> results_dict"""
        ...
    
    def run_gate_check(self, results: Dict) -> Dict:
        """Phase 5: Gate check. results -> gate_status_dict"""
        ...
    
    def run_visualization(
        self, 
        clean_df: pd.DataFrame, 
        results: Dict
    ) -> None:
        """Phase 6: Generate figures. Saves 4 PNG files"""
        ...
    
    def run_full_pipeline(self) -> Dict:
        """Execute full pipeline. Returns: final_results_dict"""
        ...
```

---

## Data Structures

### CSV Schemas

**h_e1_dcs_scores.csv**
```
repo_id: str (HuggingFace repo identifier)
dcs_3_score: float [0.0-3.0] (documentation quality score)
t0_date: datetime (dataset publication date)
```

**github_activity_metrics.csv**
```
repo_id: str
commits_per_month: float (total_commits / 3)
unique_contributors: int (distinct commit authors)
median_issue_response_time: float (days, nullable)
repo_age_days: int (age at T0+90)
```

**activity_metrics_cleaned.csv**
```
repo_id: str
dcs_3_score: float
commits_per_month: float
unique_contributors: int
median_issue_response_time: float (nullable)
repo_age_days: int
outlier_flag: bool
```

**correlation_results.csv**
```
metric: str (commits_per_month | unique_contributors | median_issue_response_time)
rho: float [-1.0, 1.0]
p_value_two_tailed: float
p_value_one_tailed: float
sample_size: int
```

**partial_correlation_results.csv**
```
partial_rho: float
partial_p: float
controlled_variable: str (repo_age_days)
```

**bootstrap_ci.csv**
```
metric: str
rho_point_estimate: float
ci_lower: float
ci_upper: float
n_iterations: int
```

---

## Configuration Structure

```python
# config.yaml
experiment:
  id: h-m1
  name: Community Engagement Correlation Study
  hypothesis_type: MECHANISM

data_sources:
  h_e1_path: ../h-e1/validation_results.csv
  github_token_env: GITHUB_ACCESS_TOKEN

data_collection:
  target_n: 100
  t0_to_t90_days: 90
  min_issues_for_response_time: 5
  max_retries: 3

validation:
  quality_threshold: 0.95
  outlier_z_threshold: 3.0

analysis:
  random_seed: 42
  primary_gate:
    min_rho: 0.30
    max_p: 0.05
    one_tailed: true
  secondary_gate:
    min_partial_rho: 0.25
    max_p: 0.05
  bootstrap:
    n_iterations: 10000
    confidence_level: 0.95

visualization:
  style: seaborn
  figures_dir: figures/
  dpi: 300
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

H-M1 loads DCS_3 scores from H-E1 validation results CSV. No code imports from H-E1.

**Data Dependency (CSV File)**:
```python
# File: ../h-e1/validation_results.csv
# Schema: repo_id, dcs_3_score, t0_date, ...other columns...
# Usage: pd.read_csv('../h-e1/validation_results.csv')
```

**H-E1 Code Reference (NOT imported)**:
```python
# From: h-e1/src/data_collection/collector.py (for reference only)
class DataCollector:
    def __init__(self, random_seed: int = 42):
        """H-E1 data collector (NOT used in H-M1)."""
        ...
    
    def collect_dataset(
        self, 
        target_n: int = 1000, 
        output_path: str = "data/raw_pwc_data.csv"
    ) -> pd.DataFrame:
        """H-E1 data collection method (NOT called in H-M1)."""
        ...

# From: h-e1/src/feature_engineering/doc_scorer.py (for reference only)
class DocumentationScorer:
    def score_repository(self, github_data: Dict) -> Dict[str, Any]:
        """H-E1 scoring method (NOT used in H-M1)."""
        ...
```

**Verified from**: h-e1/src/ (actual implementation, NOT specs)  
**Note**: H-M1 is data-dependent on H-E1 validation results but code-independent. DCS_3 scores are pre-computed by H-E1 and loaded via CSV.

---

## Critical Implementation Notes

### GitHub API Authentication

```python
import os
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_ACCESS_TOKEN environment variable required")

github_client = Github(GITHUB_TOKEN)
```

### Rate Limit Monitoring

```python
def _check_rate_limit(self) -> Tuple[int, int]:
    """Check GitHub API rate limit."""
    rate_limit = self.github.get_rate_limit()
    core = rate_limit.core
    remaining = core.remaining
    reset_time = core.reset.timestamp()
    
    if remaining < 100:
        wait_seconds = max(0, reset_time - time.time())
        logger.warning(f"Rate limit low ({remaining} remaining), waiting {wait_seconds:.0f}s...")
        time.sleep(wait_seconds + 5)
    
    return (remaining, int(reset_time))
```

### Repository ID Format

```python
# HuggingFace repo_id format: "username/repo-name"
# GitHub API expects same format for get_repo()
repo = github_client.get_repo(repo_id)  # e.g., "huggingface/datasets"
```

---

## Error Handling Strategy

### GitHub API Failure (Target: <5%)

```python
try:
    metrics = collector.collect_all_metrics(repo_id, t0, t90)
    success = True
except Exception as e:
    logger.error(f"GitHub collection failed for {repo_id}: {e}")
    metrics = {
        'commits_per_month': None,
        'unique_contributors': None,
        'median_issue_response_time': None,
        'repo_age_days': None
    }
    success = False

# Continue pipeline, validator will handle missing data
```

### Quality Gate Failure

```python
clean_df = validator.handle_missing_values(merged_df)
complete_count, total_count = validator.check_completeness(clean_df)

if complete_count / total_count < 0.95:
    raise ValueError(
        f"Quality gate failed: {complete_count}/{total_count} complete ({complete_count/total_count:.1%} < 95%)"
    )
```

---

## Validation Checkpoints

### Pre-Analysis Validation

```python
def validate_pipeline_outputs(self) -> Dict[str, bool]:
    """Validate intermediate outputs."""
    checks = {
        "h_e1_loaded": len(dcs_df) == 100,
        "github_collection_rate": (merged_df.notna().sum() / len(merged_df)) >= 0.95,
        "quality_gate": len(clean_df) >= 95,
        "correlations_computed": 'rho_commits' in results,
        "bootstrap_ci_computed": 'ci_lower' in results
    }
    
    logger.info(f"Validation checks: {checks}")
    return checks
```

---

## Logic Design Validation

### Self-Validation Checklist

- [x] No ASCII diagrams (text descriptions only)
- [x] No KB search logs (only "Applied: X" at top)
- [x] "Codebase Analysis (Serena)" section included
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes replaced with data structure tables
- [x] Pseudo-code only for complex algorithms (retry, median calculation, bootstrap)
- [x] API signatures copy-paste ready with type hints
- [x] Subtask count within budget (8/8 total)
- [x] Total length < 600 lines
- [x] External Dependencies API section included with verified signatures

### Budget Allocation

| Epic | Complexity | Subtasks Allocated | Subtasks Used |
|------|------------|-------------------|---------------|
| M-1 | 6 (Low) | 0 | 0 |
| M-2 | 14 (High) | 3 | 3 |
| M-3 | 10 (Medium) | 2 | 2 |
| M-4 | 12 (Medium) | 3 | 3 |
| M-5 | 8 (Low) | 0 | 0 |
| M-6 | 9 (Medium) | 0 | 0 |
| M-7 | 11 (Medium) | 0 | 0 |
| **Total** | **70** | **8** | **8** |

---

**Document Version:** 1.0  
**Next Phase:** Phase 4 - Implementation (Coder Agent)  
**Subtasks Created:** 8 (L-2-1, L-2-2, L-2-3, L-3-1, L-3-2, L-4-1, L-4-2, L-4-3)  
**Gate Status:** SHOULD_WORK gate pending (validation in Phase 4)
