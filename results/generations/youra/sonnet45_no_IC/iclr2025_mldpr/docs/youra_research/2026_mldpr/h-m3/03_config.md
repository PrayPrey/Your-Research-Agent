# Configuration Schema: H-M3 Performance Variance Analysis

**Date:** 2026-07-12  
**Hypothesis:** h-m3 (MECHANISM)  
**Type:** Observational Meta-Analysis (Statistical Analysis)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from H-M2 code  
**Config Files Found:** docs/youra_research/h-m2/code/config.py  
**Pattern Used:** dataclass (verified field names from actual implementation)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited or referenced from H-M2:

```python
# From: docs/youra_research/h-m2/code/config.py (ACTUAL CODE)
@dataclass
class ProtocolStudyConfig:
    # API Settings (verified from actual code)
    PWC_API_URL: str = "https://paperswithcode.com/api/v1/"
    S2_API_URL: str = "https://api.semanticscholar.org/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # Protocol Dimensions (H-M1 rubric)
    PROTOCOL_DIMENSIONS: List[str] = field(default_factory=lambda: [
        "data_splits", "preprocessing", "evaluation_protocol", "hyperparameters"
    ])
    
    # Gate Thresholds
    MIN_KAPPA: float = 0.8
    PRIMARY_THRESHOLD: float = 0.70
    SECONDARY_RHO_THRESHOLD: float = 0.4
    SECONDARY_P_THRESHOLD: float = 0.05

@dataclass
class PlotConfig:
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

**Verified from:** docs/youra_research/h-m2/code/config.py (actual implementation)

---

## M3-5: Confound Variable Collection (Complexity: 10, Budget: 2 subtasks)

**Applied:** Standard observational study patterns from scipy/pandas documentation

### Configuration (Python Dataclass)

```python
@dataclass
class ConfoundConfig:
    """Configuration for confounding variable collection."""
    
    # Age Calculation
    CURRENT_YEAR: int = 2026
    
    # Task Domain Taxonomy (Papers with Code categories)
    VALID_DOMAINS: List[str] = field(default_factory=lambda: [
        "Computer Vision", "NLP", "Speech", "Time Series", "Graphs"
    ])
    DEFAULT_DOMAIN: str = "Other"
    
    # Metric Type Standardization
    ACCURACY_METRICS: List[str] = field(default_factory=lambda: [
        "accuracy", "top1", "top-1"
    ])
    F1_METRICS: List[str] = field(default_factory=lambda: [
        "f1", "f1-score", "macro-f1"
    ])
    
    # Venue Prestige (Optional - Semantic Scholar API)
    ENABLE_VENUE_COLLECTION: bool = False
    # Non-standard: Disabled by default to reduce API dependencies
    VENUE_TIMEOUT: int = 10
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M3-5-1 | Age/Domain/Metric Extraction | Extract benchmark age, task domain, metric type from PWC API metadata |
| M3-5-2 | Venue Prestige Collection | Optional: Query Semantic Scholar for venue prestige if ENABLE_VENUE_COLLECTION=True |

---

## M3-11: Validation Report (Complexity: 11, Budget: 2 subtasks)

**Applied:** Markdown generation patterns from H-M2 validation report

### Configuration (Python Dataclass)

```python
@dataclass
class ValidationReportConfig:
    """Configuration for 04_validation.md generation."""
    
    # Report Structure
    SECTIONS: List[str] = field(default_factory=lambda: [
        "executive_summary",
        "data_overview",
        "statistical_results",
        "gate_evaluation",
        "interpretation"
    ])
    
    # Gate Logic
    MANN_WHITNEY_ALPHA: float = 0.05
    COHENS_D_THRESHOLD: float = 0.5
    
    # Figure References
    GATE_METRICS_FIGURE: str = "figures/gate_metrics.png"
    CV_DISTRIBUTION_FIGURE: str = "figures/cv_distribution.png"
    DOSE_RESPONSE_FIGURE: str = "figures/dose_response_scatter.png"
    
    # Output Path
    OUTPUT_PATH: str = "../04_validation.md"
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M3-11-1 | Markdown Template Generation | Create markdown structure with sections, load results from JSON/CSV |
| M3-11-2 | Gate Decision Logic | Evaluate gate_pass = (mann_whitney_p < 0.05) AND (cohens_d > 0.5) |

---

## M3-4: Variance Calculation (Complexity: 11, Budget: 2 subtasks)

**Applied:** Standard statistical outlier filtering (z-score method) from scipy

### Configuration (Python Dataclass)

```python
@dataclass
class VarianceCalculationConfig:
    """Configuration for coefficient of variation computation."""
    
    # Outlier Filtering
    OUTLIER_THRESHOLD_SD: float = 3.0
    # Non-standard: 3 SD threshold is standard for z-score outlier detection
    
    # Sample Size Validation
    MIN_RESULTS_PER_BENCHMARK: int = 5
    
    # CV Calculation
    CV_FORMULA: str = "std / mean"
    
    # Output Columns
    OUTPUT_COLUMNS: List[str] = field(default_factory=lambda: [
        "benchmark_id", "cv", "n_results", "mean", "std", "outliers_removed"
    ])
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M3-4-1 | Outlier Filtering | Remove results > 3 SD from mean, validate min 5 results remain |
| M3-4-2 | CV Computation | Calculate CV = std/mean per benchmark, output to CSV |

---

## Master Configuration (Combined)

### VarianceStudyConfig (Primary Configuration Class)

**Applied:** H-M2 ProtocolStudyConfig pattern (verified field names)

```python
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class VarianceStudyConfig:
    """Master configuration for H-M3 performance variance meta-analysis."""
    
    # API Settings (inherited from H-M2)
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
    ARTIFACT_DIMENSIONS: List[str] = field(default_factory=lambda: [
        "github", "dataset_card", "badge"
    ])
    ARTIFACT_THRESHOLD: int = 2
    # Non-standard: Threshold at 2 based on H-M1 validated rubric
    
    # Date Range
    START_YEAR: int = 2019
    END_YEAR: int = 2024
    
    # Gate Thresholds (Statistical Tests)
    MANN_WHITNEY_ALPHA: float = 0.05
    COHENS_D_THRESHOLD: float = 0.5
    SPEARMAN_RHO_THRESHOLD: float = -0.3
    # Non-standard: Negative threshold for inverse correlation
    SPEARMAN_P_THRESHOLD: float = 0.05
    
    # Propensity Score Weighting (Conditional)
    ENABLE_PROPENSITY_WEIGHTING: bool = True
    COVERAGE_DIFF_THRESHOLD: float = 0.10
    # Non-standard: 10% threshold for sampling bias detection
    BOOTSTRAP_SAMPLES: int = 1000
    
    # Confound Variables (M3-5)
    CURRENT_YEAR: int = 2026
    VALID_DOMAINS: List[str] = field(default_factory=lambda: [
        "Computer Vision", "NLP", "Speech", "Time Series", "Graphs"
    ])
    DEFAULT_DOMAIN: str = "Other"
    ACCURACY_METRICS: List[str] = field(default_factory=lambda: [
        "accuracy", "top1", "top-1"
    ])
    F1_METRICS: List[str] = field(default_factory=lambda: [
        "f1", "f1-score", "macro-f1"
    ])
    ENABLE_VENUE_COLLECTION: bool = False
    VENUE_TIMEOUT: int = 10
    
    # Output Paths
    BENCHMARKS_FILE: str = "data/benchmarks.csv"
    ARTIFACT_QUALITY_FILE: str = "data/artifact_quality.csv"
    PERFORMANCE_RESULTS_FILE: str = "data/performance_results.csv"
    CV_DATA_FILE: str = "data/cv_by_benchmark.csv"
    CONFOUNDS_FILE: str = "data/confounds.csv"
    HYPOTHESIS_TEST_FILE: str = "results/hypothesis_test.json"
    PROPENSITY_RESULTS_FILE: str = "results/propensity_weights.csv"
    FIGURES_DIR: str = "../figures"
    OUTPUT_FILE: str = "../04_validation.md"


@dataclass
class PlotConfig:
    """Visualization styling configuration (inherited from H-M2)."""
    
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

## Configuration Usage Examples

### Initialization in Main Script

```python
from config import VarianceStudyConfig, PlotConfig

def run_variance_meta_analysis():
    config = VarianceStudyConfig()
    plot_config = PlotConfig()
    
    # Override defaults if needed
    config.TARGET_BENCHMARK_COUNT = 150
    config.ENABLE_VENUE_COLLECTION = True
    
    # Pass to modules
    collector = PapersWithCodeCollector(config)
    confound_collector = ConfoundCollector(config)
    variance_calc = PerformanceVarianceCalculator(config)
```

### Module-Specific Access

```python
class ConfoundCollector:
    def __init__(self, config: VarianceStudyConfig):
        self.config = config
    
    def extract_benchmark_age(self, benchmarks: pd.DataFrame) -> pd.Series:
        return self.config.CURRENT_YEAR - benchmarks['publication_year']
    
    def extract_task_domain(self, benchmarks: pd.DataFrame) -> pd.Series:
        domains = benchmarks['task'].apply(self._map_domain)
        return domains.fillna(self.config.DEFAULT_DOMAIN)
    
    def _map_domain(self, task: str) -> str:
        for domain in self.config.VALID_DOMAINS:
            if domain.lower() in task.lower():
                return domain
        return None
```

### Gate Evaluation

```python
class ValidationReportGenerator:
    def determine_gate_status(self, mann_whitney_p: float, cohens_d: float) -> str:
        mann_whitney_pass = mann_whitney_p < self.config.MANN_WHITNEY_ALPHA
        cohens_d_pass = cohens_d > self.config.COHENS_D_THRESHOLD
        
        if mann_whitney_pass and cohens_d_pass:
            return "PASS"
        else:
            return "EXPLORE"
```

---

## Configuration Validation

### Type Checking

```python
def validate_config(config: VarianceStudyConfig):
    assert config.TARGET_BENCHMARK_COUNT > 0, "Benchmark count must be positive"
    assert config.MIN_RESULTS_PER_BENCHMARK >= 3, "Minimum 3 results required"
    assert 0.0 < config.MANN_WHITNEY_ALPHA < 1.0, "Alpha must be in (0, 1)"
    assert config.COHENS_D_THRESHOLD >= 0.0, "Effect size threshold must be non-negative"
    assert config.START_YEAR < config.END_YEAR, "Invalid date range"
    assert config.ARTIFACT_THRESHOLD in [1, 2, 3], "Artifact threshold must be 1-3"
```

---

## Environment Variables (Optional)

For API authentication (if required in future):

```python
import os

# Optional: Papers with Code API token (currently not required)
PWC_API_TOKEN = os.getenv("PWC_API_TOKEN", None)

# Optional: Semantic Scholar API key (for venue prestige)
S2_API_KEY = os.getenv("S2_API_KEY", None)
```

**Note:** Current implementation does not require API authentication. Environment variables included for future extensibility.

---

## Budget Summary

| Task ID | Task Name | Complexity | Subtasks Allocated | Subtasks Used |
|---------|-----------|------------|-------------------|---------------|
| M3-5 | Confound Variable Collection | 10 | 2 | 2 |
| M3-11 | Validation Report | 11 | 2 | 2 |
| M3-4 | Variance Calculation | 11 | 2 | 2 |
| **Total** | | **32** | **6** | **6** |

**Status:** Budget allocation complete (6/12 subtasks used, 6 reserved for other medium-complexity tasks)

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Code Implementation (Step 4)
