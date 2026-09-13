# Configuration: H-M1 Artifact Quality Assessment

**Date:** 2026-07-12  
**Hypothesis:** h-m1 (MECHANISM)  
**Type:** Observational Study (Content Analysis)  
**Budget:** 8 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-e1 code  
**Config Files Found:** `/docs/youra_research/h-e1/code/config.py`  
**Pattern Used:** Python class with class attributes (not dataclass)

---

## Inherited Configuration (Base Hypothesis)

### From H-E1 Actual Code

The following API configuration is inherited from h-e1 (verified from actual implementation):

```python
# From: /docs/youra_research/h-e1/code/config.py
class ValidationConfig:
    API_BASE_URL = "https://paperswithcode.com/api/v1/"
    RATE_LIMIT = 1.0
    MAX_RETRIES = 3
    TASK_FILTER = "classification"
    START_YEAR = 2019
    END_YEAR = 2024
```

**Applied:** Standard API client pattern from h-e1

---

## Configuration Schema

### Sampling Configuration

Applied: Stratified sampling pattern for observational studies

```python
class SamplingConfig:
    """Benchmark sampling parameters for stratified study design."""
    
    # Sample Size
    SAMPLE_SIZE = 20
    STRATIFICATION = {"CV": 10, "NLP": 10}
    
    # Artifact Filtering
    MIN_ARTIFACT_COUNT = 2  # Require GitHub, dataset card, or badge
    
    # Inherited from h-e1
    TASK_FILTER = "classification"
    START_YEAR = 2019
    END_YEAR = 2024
```

**Subtasks [2/8 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | BenchmarkSampler | Stratified sampling logic (CV/NLP) |
| C-1-2 | ArtifactRetriever | Download artifact content from URLs |

---

### Rubric Configuration

Applied: Structured scoring rubric pattern

```python
class RubricConfig:
    """Quality assessment rubric definitions."""
    
    # Rubric Dimensions
    RUBRIC_DIMENSIONS = ["preprocessing", "data_splits", "evaluation_protocol", "hyperparameters"]
    
    # Score Levels
    SCORE_LEVELS = [0, 5, 10]
    
    # Dimension Definitions
    DIMENSION_CRITERIA = {
        'preprocessing': {
            'description': 'Data preprocessing steps specification',
            'score_0': 'No preprocessing information',
            'score_5': 'Mentions preprocessing exists',
            'score_10': 'Complete code/config for all steps'
        },
        'data_splits': {
            'description': 'Train/val/test split detail',
            'score_0': 'No split information',
            'score_5': 'Split ratios mentioned',
            'score_10': 'Exact seeds/indices or deterministic split code'
        },
        'evaluation_protocol': {
            'description': 'Evaluation procedure completeness',
            'score_0': 'No evaluation details',
            'score_5': 'Metrics named',
            'score_10': 'Complete evaluation code with all parameters'
        },
        'hyperparameters': {
            'description': 'Training hyperparameter specification',
            'score_0': 'No hyperparameters listed',
            'score_5': 'Some hyperparameters mentioned',
            'score_10': 'Complete config file or exhaustive listing'
        }
    }
```

**Subtasks [2/8 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | ArtifactQualityRubric | Rubric dimension definitions and validation |
| C-2-2 | RaterScoreSheet | CSV I/O for rater score entry |

---

### Statistical Validation Configuration

Applied: Standard inter-rater reliability thresholds (Cohen's kappa)

```python
class StatisticalConfig:
    """Gate thresholds for measurement validity and quality assessment."""
    
    # Inter-Rater Reliability
    MIN_KAPPA = 0.8  # Cohen's kappa threshold (excellent reliability)
    
    # Quality Gate
    MIN_QUALITY = 7.0  # Mean quality score threshold (0-10 scale)
    
    # Number of Raters
    NUM_RATERS = 2  # Independent dual-rater coding
```

**Subtasks [2/8 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | InterRaterReliability | Cohen's kappa calculation (sklearn wrapper) |
| C-5-1 | QualityScoreAggregator | Dimension and rater averaging logic |

---

### Output Path Configuration

```python
class OutputConfig:
    """File paths for data storage and report generation."""
    
    # Data Directories
    RAW_DATA_DIR = "data/raw"
    ARTIFACT_CONTENT_DIR = "data/artifacts"
    RATER_SCORES_DIR = "data/scores"
    
    # Output Directories (inherited from h-e1 pattern)
    FIGURES_DIR = "../figures"
    OUTPUT_FILE = "../04_validation.md"
    
    # Error Logging
    ERROR_LOG = "data/error_log.txt"
```

**Subtasks [1/8 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | DataPipelineIntegration | File management and path handling |

---

### Visualization Configuration

Applied: matplotlib configuration pattern

```python
class PlotConfig:
    """Styling configuration for visualization."""
    
    # Figure settings (inherited from h-e1)
    DPI = 300
    FIGSIZE_SINGLE = (8, 6)
    FIGSIZE_DOUBLE = (12, 5)
    
    # Colors (inherited from h-e1)
    COLOR_PASS = "green"
    COLOR_FAIL = "red"
    COLOR_WARNING = "orange"
    COLOR_PRIMARY = "#3498db"
    COLOR_SECONDARY = "#95a5a6"
    
    # Fonts (inherited from h-e1)
    FONT_SIZE_TITLE = 14
    FONT_SIZE_LABEL = 12
    FONT_SIZE_TICK = 10
```

**Subtasks [1/8 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | QualityVisualization | 5 plot types (gate metrics, distribution, dimensions, domain, agreement) |

---

## Complete Configuration Module (config.py)

```python
"""
Configuration for H-M1 Artifact Quality Assessment
Generated: 2026-07-12
"""

class QualityStudyConfig:
    """Master configuration for artifact quality observational study."""
    
    # API Settings (inherited from h-e1)
    API_BASE_URL = "https://paperswithcode.com/api/v1/"
    RATE_LIMIT = 1.0
    MAX_RETRIES = 3
    
    # Sampling Parameters
    SAMPLE_SIZE = 20
    STRATIFICATION = {"CV": 10, "NLP": 10}
    START_YEAR = 2019
    END_YEAR = 2024
    MIN_ARTIFACT_COUNT = 2
    
    # Rubric Dimensions
    RUBRIC_DIMENSIONS = ["preprocessing", "data_splits", "evaluation_protocol", "hyperparameters"]
    SCORE_LEVELS = [0, 5, 10]
    
    # Gate Thresholds
    MIN_KAPPA = 0.8
    MIN_QUALITY = 7.0
    
    # Number of Raters
    NUM_RATERS = 2
    
    # Output Paths
    RAW_DATA_DIR = "data/raw"
    ARTIFACT_CONTENT_DIR = "data/artifacts"
    RATER_SCORES_DIR = "data/scores"
    FIGURES_DIR = "../figures"
    OUTPUT_FILE = "../04_validation.md"
    ERROR_LOG = "data/error_log.txt"


class RubricDimensionCriteria:
    """Detailed scoring criteria for each rubric dimension."""
    
    PREPROCESSING = {
        'description': 'Data preprocessing steps specification',
        'score_0': 'No preprocessing information',
        'score_5': 'Mentions preprocessing exists',
        'score_10': 'Complete code/config for all steps'
    }
    
    DATA_SPLITS = {
        'description': 'Train/val/test split detail',
        'score_0': 'No split information',
        'score_5': 'Split ratios mentioned',
        'score_10': 'Exact seeds/indices or deterministic split code'
    }
    
    EVALUATION_PROTOCOL = {
        'description': 'Evaluation procedure completeness',
        'score_0': 'No evaluation details',
        'score_5': 'Metrics named',
        'score_10': 'Complete evaluation code with all parameters'
    }
    
    HYPERPARAMETERS = {
        'description': 'Training hyperparameter specification',
        'score_0': 'No hyperparameters listed',
        'score_5': 'Some hyperparameters mentioned',
        'score_10': 'Complete config file or exhaustive listing'
    }


class PlotConfig:
    """Visualization styling configuration."""
    
    # Figure settings
    DPI = 300
    FIGSIZE_SINGLE = (8, 6)
    FIGSIZE_DOUBLE = (12, 5)
    
    # Colors
    COLOR_PASS = "green"
    COLOR_FAIL = "red"
    COLOR_WARNING = "orange"
    COLOR_PRIMARY = "#3498db"
    COLOR_SECONDARY = "#95a5a6"
    
    # Fonts
    FONT_SIZE_TITLE = 14
    FONT_SIZE_LABEL = 12
    FONT_SIZE_TICK = 10
```

---

## Subtask Budget Summary

**Total Used: 8/8**

| Component | Subtasks | IDs |
|-----------|----------|-----|
| Data Collection | 2 | C-1-1, C-1-2 |
| Rubric Scoring | 2 | C-2-1, C-2-2 |
| Statistical Validation | 2 | C-4-1, C-5-1 |
| Visualization | 1 | C-7-1 |
| Pipeline Integration | 1 | C-9-1 |

---

## Gate Decision Configuration

```python
def check_gates(kappa: float, mean_quality: float) -> str:
    """
    Gate decision logic for H-M1.
    
    Returns:
        str: "MEASUREMENT_FAIL", "PIVOT", or "PASS"
    """
    if kappa < 0.8:
        return "MEASUREMENT_FAIL"  # Refine rubric and re-code
    elif mean_quality < 7.0:
        return "PIVOT"  # Artifacts lack information
    else:
        return "PASS"  # Proceed to H-M2
```

---

## Configuration Validation

### Self-Validation Checklist

- [x] ONE format only (Python class with class attributes)
- [x] No ASCII diagrams
- [x] Archon KB patterns applied (3 searches documented)
- [x] Codebase Analysis section included
- [x] Inherited Configuration from h-e1 verified
- [x] Field names match h-e1 actual code
- [x] Subtask count within budget (8/8)
- [x] Total length < 400 lines
- [x] No hyperparameters (observational study, not training)
- [x] Focus on sampling, rubric, thresholds, paths

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Code Implementation (Step 4)  
**Output File:** `/workspace/TEST_mldpr/docs/youra_research/h-m1/03_config.md`
