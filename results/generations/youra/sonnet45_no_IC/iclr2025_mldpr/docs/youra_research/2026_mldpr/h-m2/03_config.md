# Configuration: H-M2 Protocol Consistency via Artifact Quality

**Date:** 2026-07-12  
**Hypothesis:** h-m2 (MECHANISM)  
**Type:** Observational Study (Content Analysis + Statistical Correlation)  
**Budget:** 7 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from H-M1 code  
**Config Files Found:** `docs/youra_research/h-m1/code/config.py`  
**Pattern Used:** Python dataclass (H-M1 uses dataclass pattern)

---

## Inherited Configuration (Base Hypothesis)

### From H-M1 Actual Code

The following configuration is inherited from H-M1 (verified from actual implementation):

```python
# From: docs/youra_research/h-m1/code/config.py
@dataclass
class QualityStudyConfig:
    # API Settings
    API_BASE_URL: str = "https://paperswithcode.com/api/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # Rubric Dimensions (reused for protocol coding)
    RUBRIC_DIMENSIONS: List[str] = field(default_factory=lambda: [
        "preprocessing", "data_splits", "evaluation_protocol", "hyperparameters"
    ])
    
    # Gate Thresholds
    MIN_KAPPA: float = 0.8
```

**Verified from:** `docs/youra_research/h-m1/code/config.py` (actual implementation)

**Reuse Strategy:**
- API client settings for rate limiting and retry logic
- Rubric dimensions as protocol coding framework
- Inter-rater reliability threshold (Cohen's kappa ≥0.8)

---

## Configuration Schema

Applied: Dataclass pattern with default factories for collections

### Main Configuration (config.py)

```python
"""
Configuration for H-M2 Protocol Consistency Study
Generated: 2026-07-12
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ProtocolStudyConfig:
    """Configuration for protocol consistency observational study."""
    
    # API Settings (inherited from H-M1)
    PWC_API_URL: str = "https://paperswithcode.com/api/v1/"
    S2_API_URL: str = "https://api.semanticscholar.org/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # Sampling Parameters
    BENCHMARK_COUNT: int = 10
    PAPERS_PER_BENCHMARK: int = 5
    INTER_RATER_SAMPLE_SIZE: int = 10
    
    # Protocol Dimensions (from H-M1 rubric)
    PROTOCOL_DIMENSIONS: List[str] = field(default_factory=lambda: [
        "data_splits", "preprocessing", "evaluation_protocol", "hyperparameters"
    ])
    
    # Gate Thresholds
    MIN_KAPPA: float = 0.8
    PRIMARY_THRESHOLD: float = 0.70
    SECONDARY_RHO_THRESHOLD: float = 0.4
    SECONDARY_P_THRESHOLD: float = 0.05
    
    # Quality Stratification
    QUALITY_STRATA: Dict[str, tuple] = field(default_factory=lambda: {
        "High": (7.0, 10.0),
        "Medium": (4.0, 7.0),
        "Low": (0.0, 4.0)
    })
    
    # Consistency Definition
    MIN_DIMENSIONS_IDENTICAL: int = 3
    
    # Paths (H-M1 dependency)
    H_M1_QUALITY_FILE: str = "../h-m1/outputs/artifact_quality.csv"
    
    # Data Directories
    RAW_PAPERS_DIR: str = "data/citing_papers"
    BENCHMARK_SPECS_DIR: str = "data/benchmark_specs"
    
    # Output Paths
    SELECTED_BENCHMARKS_FILE: str = "data/selected_benchmarks.csv"
    PROTOCOL_CODING_FILE: str = "data/protocol_coding.csv"
    RATER_VALIDATION_DIR: str = "data/rater_validation"
    CONSISTENCY_RESULTS_FILE: str = "results/consistency_by_stratum.csv"
    HYPOTHESIS_TEST_FILE: str = "results/hypothesis_test.json"
    FIGURES_DIR: str = "../figures"
    OUTPUT_FILE: str = "../04_validation.md"


@dataclass
class PlotConfig:
    """Visualization styling configuration (inherited from H-M1)."""
    
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

**Subtasks [7/7 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | BenchmarkStratifier | Load H-M1 scores and stratify by quality |
| C-2-1 | PaperAPIClient | Papers with Code + Semantic Scholar API integration |
| C-3-1 | PDFTextExtractor | PyMuPDF wrapper for Methods section extraction |
| C-4-1 | ProtocolExtractor | Extract 4 dimensions from Methods text |
| C-5-1 | ProtocolCoder | Binary comparison against benchmark specs |
| C-6-1 | InterRaterValidator | Cohen's kappa for 4 dimensions |
| C-7-1 | ConsistencyCalculator | Benchmark-level and stratum-level aggregation |

---

## Benchmark Selection Configuration

Applied: Stratified sampling pattern

```python
QUALITY_STRATA = {
    "High": (7.0, 10.0),
    "Medium": (4.0, 7.0),
    "Low": (0.0, 4.0)
}

BENCHMARK_COUNT = 10  # Total benchmarks to sample
```

**Input:** `../h-m1/outputs/artifact_quality.csv` (from H-M1)  
**Strategy:** Sample 10 benchmarks ensuring coverage of all quality strata

---

## API Configuration

Applied: API rate limiting pattern from H-M1

```python
PWC_API_URL = "https://paperswithcode.com/api/v1/"
S2_API_URL = "https://api.semanticscholar.org/v1/"
RATE_LIMIT = 1.0  # Seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30
```

**Papers per benchmark:** 5 (total 50 papers)

---

## Protocol Coding Configuration

Applied: Binary coding rubric (simplification of H-M1 Likert scale)

```python
PROTOCOL_DIMENSIONS = [
    "data_splits",
    "preprocessing", 
    "evaluation_protocol",
    "hyperparameters"
]

# Binary Coding
CODING_SCHEME = {
    1: "Identical - Matches benchmark specification",
    0: "Divergent - Differs from benchmark or unspecified"
}

# Consistency Definition
MIN_DIMENSIONS_IDENTICAL = 3  # ≥3/4 dimensions = consistent
```

**Output:** `data/protocol_coding.csv` (50 papers × 4 dimensions)

---

## Statistical Validation Configuration

Applied: Inter-rater reliability + correlation analysis

```python
# Inter-Rater Reliability (inherited from H-M1)
MIN_KAPPA = 0.8
INTER_RATER_SAMPLE_SIZE = 10  # 20% of corpus

# Gate Metrics
PRIMARY_THRESHOLD = 0.70  # High-quality consistency rate >70%
SECONDARY_RHO_THRESHOLD = 0.4  # Spearman ρ >0.4
SECONDARY_P_THRESHOLD = 0.05  # Statistical significance
```

**Primary Metric:** Consistency rate for High quality stratum  
**Secondary Metric:** Spearman correlation between quality and consistency

---

## Gate Decision Configuration

```python
def evaluate_gate(primary_result: dict, secondary_result: dict) -> str:
    """
    Gate decision logic for H-M2.
    
    Returns:
        str: "KAPPA_FAIL", "EXPLORE", or "PASS"
    """
    kappa = primary_result.get('kappa')
    primary_pass = primary_result.get('consistency_rate') > 0.70
    secondary_pass = (
        secondary_result.get('rho') > 0.4 and 
        secondary_result.get('p_value') < 0.05
    )
    
    if kappa < 0.8:
        return "KAPPA_FAIL"  # Refine rubric and re-code
    elif primary_pass or secondary_pass:
        return "PASS"  # Proceed to H-M3
    else:
        return "EXPLORE"  # Identify missing specifications
```

---

## Output Path Configuration

```python
# Data Directories
RAW_PAPERS_DIR = "data/citing_papers"  # 50 PDFs
BENCHMARK_SPECS_DIR = "data/benchmark_specs"  # Ground-truth protocols

# Analysis Outputs
SELECTED_BENCHMARKS_FILE = "data/selected_benchmarks.csv"
PROTOCOL_CODING_FILE = "data/protocol_coding.csv"
RATER_VALIDATION_DIR = "data/rater_validation"  # rater1_scores.csv, rater2_scores.csv
CONSISTENCY_RESULTS_FILE = "results/consistency_by_stratum.csv"
HYPOTHESIS_TEST_FILE = "results/hypothesis_test.json"

# Report Outputs
FIGURES_DIR = "../figures"  # 4 required plots
OUTPUT_FILE = "../04_validation.md"
```

---

## Visualization Configuration

Applied: matplotlib configuration from H-M1

```python
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
```

**Required Figures:**
1. `gate_metrics.png` - Target vs Actual for both metrics (MANDATORY)
2. `consistency_by_quality.png` - Box plot by stratum
3. `quality_consistency_scatter.png` - Scatter with regression line
4. `dimension_heatmap.png` - Benchmarks × dimensions consistency

---

## PDF Parsing Configuration

Applied: PyMuPDF pattern for academic paper parsing

```python
# Methods Section Detection Patterns
METHODS_SECTION_PATTERNS = [
    r"(?i)\n\s*\d*\.?\s*Methods?\s*\n",
    r"(?i)\n\s*\d*\.?\s*Experimental?\s+Setup\s*\n",
    r"(?i)\n\s*\d*\.?\s*Implementation\s+Details?\s*\n",
    r"(?i)\n\s*\d*\.?\s*Methodology\s*\n"
]

# PDF Library
PDF_PARSER = "PyMuPDF"  # Primary (fitz)
PDF_FALLBACK = "pdfplumber"  # If PyMuPDF fails
```

---

## Complete Configuration Module

```python
"""
Configuration for H-M2 Protocol Consistency Study
Generated: 2026-07-12
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ProtocolStudyConfig:
    """Master configuration for protocol consistency observational study."""
    
    # API Settings (inherited from H-M1)
    PWC_API_URL: str = "https://paperswithcode.com/api/v1/"
    S2_API_URL: str = "https://api.semanticscholar.org/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # Sampling Parameters
    BENCHMARK_COUNT: int = 10
    PAPERS_PER_BENCHMARK: int = 5
    INTER_RATER_SAMPLE_SIZE: int = 10
    
    # Protocol Dimensions (from H-M1 rubric)
    PROTOCOL_DIMENSIONS: List[str] = field(default_factory=lambda: [
        "data_splits", "preprocessing", "evaluation_protocol", "hyperparameters"
    ])
    
    # Gate Thresholds
    MIN_KAPPA: float = 0.8
    PRIMARY_THRESHOLD: float = 0.70
    SECONDARY_RHO_THRESHOLD: float = 0.4
    SECONDARY_P_THRESHOLD: float = 0.05
    
    # Quality Stratification
    QUALITY_STRATA: Dict[str, tuple] = field(default_factory=lambda: {
        "High": (7.0, 10.0),
        "Medium": (4.0, 7.0),
        "Low": (0.0, 4.0)
    })
    
    # Consistency Definition
    MIN_DIMENSIONS_IDENTICAL: int = 3
    
    # Paths (H-M1 dependency)
    H_M1_QUALITY_FILE: str = "../h-m1/outputs/artifact_quality.csv"
    
    # Data Directories
    RAW_PAPERS_DIR: str = "data/citing_papers"
    BENCHMARK_SPECS_DIR: str = "data/benchmark_specs"
    
    # Output Paths
    SELECTED_BENCHMARKS_FILE: str = "data/selected_benchmarks.csv"
    PROTOCOL_CODING_FILE: str = "data/protocol_coding.csv"
    RATER_VALIDATION_DIR: str = "data/rater_validation"
    CONSISTENCY_RESULTS_FILE: str = "results/consistency_by_stratum.csv"
    HYPOTHESIS_TEST_FILE: str = "results/hypothesis_test.json"
    FIGURES_DIR: str = "../figures"
    OUTPUT_FILE: str = "../04_validation.md"


@dataclass
class PlotConfig:
    """Visualization styling configuration (inherited from H-M1)."""
    
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


# Methods Section Detection Patterns
METHODS_SECTION_PATTERNS = [
    r"(?i)\n\s*\d*\.?\s*Methods?\s*\n",
    r"(?i)\n\s*\d*\.?\s*Experimental?\s+Setup\s*\n",
    r"(?i)\n\s*\d*\.?\s*Implementation\s+Details?\s*\n",
    r"(?i)\n\s*\d*\.?\s*Methodology\s*\n"
]
```

---

## Subtask Budget Summary

**Total Used: 7/7**

| Component | Subtasks | IDs |
|-----------|----------|-----|
| Benchmark Selection | 1 | C-1-1 |
| Paper Retrieval | 1 | C-2-1 |
| PDF Parsing | 1 | C-3-1 |
| Protocol Extraction | 1 | C-4-1 |
| Protocol Coding | 1 | C-5-1 |
| Inter-Rater Reliability | 1 | C-6-1 |
| Consistency Analysis | 1 | C-7-1 |

---

## Configuration Validation

### Self-Validation Checklist

- [x] ONE format only (Python dataclass)
- [x] No ASCII diagrams
- [x] Archon KB patterns applied (dataclass configuration pattern)
- [x] Codebase Analysis section included
- [x] Inherited Configuration from H-M1 verified
- [x] Field names match H-M1 actual code (API_BASE_URL → PWC_API_URL extended)
- [x] Subtask count within budget (7/7)
- [x] Total length < 400 lines
- [x] Focus on API settings, sampling, gate thresholds, paths

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Code Implementation (Step 4)  
**Output File:** `/workspace/TEST_mldpr/docs/youra_research/h-m2/03_config.md`
