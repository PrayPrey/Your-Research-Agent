# Architecture Design: H-M1 Artifact Quality Assessment

**Date:** 2026-07-12  
**Hypothesis:** h-m1 (MECHANISM)  
**Type:** Observational Study (Content Analysis)  
**Applied Patterns:** API client with retry logic, structured rubric scoring, statistical validation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-e1 code  
**Analyzed Path:** docs/youra_research/h-e1/code/  
**Findings:** Reusing PapersWithCodeCollector pattern (API client with rate limiting, retry logic). Adapting config structure for rubric-based scoring instead of binary validation.

---

## Overview

H-M1 implements a content analysis protocol to measure documentation artifact quality in ML benchmarks. Unlike h-e1 (binary validation), this is an observational study requiring manual scoring by independent raters.

**Key Differences from ML Experiments:**
- No model training/inference
- Primary component: Rubric-based manual coding system
- Validation: Inter-rater reliability (Cohen's kappa)
- Gate: Mean quality score > 7.0/10

---

## Module Structure

### 1. Configuration (`config.py`)

**Dependencies:** None

```python
class QualityStudyConfig:
    """Configuration for artifact quality assessment."""
    
    # API Settings (reused from h-e1)
    API_BASE_URL: str = "https://paperswithcode.com/api/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    
    # Sampling Parameters
    SAMPLE_SIZE: int = 20
    STRATIFICATION: dict = {"CV": 10, "NLP": 10}
    START_YEAR: int = 2019
    END_YEAR: int = 2024
    MIN_ARTIFACT_COUNT: int = 2
    
    # Quality Assessment
    RUBRIC_DIMENSIONS: list = ["preprocessing", "data_splits", "evaluation_protocol", "hyperparameters"]
    SCORE_LEVELS: list = [0, 5, 10]
    
    # Gate Thresholds
    MIN_KAPPA: float = 0.8
    MIN_QUALITY: float = 7.0
    
    # Output Paths
    RAW_DATA_DIR: str = "data/raw"
    ARTIFACT_CONTENT_DIR: str = "data/artifacts"
    RATER_SCORES_DIR: str = "data/scores"
    FIGURES_DIR: str = "../figures"
    OUTPUT_FILE: str = "../04_validation.md"
```

---

### 2. Data Collection (`data/collector.py`)

**Dependencies:** requests, pandas, config

```python
class BenchmarkSampler:
    """Stratified sampling of benchmarks from Papers with Code."""
    
    def __init__(self, config: QualityStudyConfig): ...
    
    def fetch_classification_benchmarks(self, task: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Fetch benchmarks using h-e1 collector pattern."""
        ...
    
    def stratified_sample(self, benchmarks: pd.DataFrame, strata: dict) -> pd.DataFrame:
        """Sample n benchmarks per domain (CV/NLP).
        
        Returns:
            DataFrame with 20 rows (10 CV + 10 NLP)
        """
        ...
    
    def save_sample(self, sample: pd.DataFrame, output_dir: str):
        """Save benchmark_sample.csv."""
        ...


class ArtifactRetriever:
    """Download artifact content for manual coding."""
    
    def __init__(self, config: QualityStudyConfig): ...
    
    def retrieve_github_readme(self, repo_url: str) -> str:
        """Fetch README.md content via GitHub API."""
        ...
    
    def retrieve_dataset_card(self, dataset_url: str) -> str:
        """Fetch dataset card if available."""
        ...
    
    def retrieve_badge_metadata(self, benchmark_id: str) -> dict:
        """Extract reproducibility badge documentation."""
        ...
    
    def save_artifacts(self, benchmark_id: str, artifacts: dict, output_dir: str):
        """Store raw content in artifact_content/{benchmark_id}/."""
        ...
```

---

### 3. Rubric Scoring (`scoring/rubric.py`)

**Dependencies:** pandas, config

```python
class ArtifactQualityRubric:
    """Structured rubric for manual artifact quality assessment."""
    
    RUBRIC_DIMENSIONS = {
        'preprocessing': {
            'description': 'Data preprocessing steps specification',
            'score_0': 'No preprocessing information',
            'score_5': 'Mentions preprocessing exists',
            'score_10': 'Complete code/config for all steps'
        },
        'data_splits': {...},
        'evaluation_protocol': {...},
        'hyperparameters': {...}
    }
    
    def __init__(self): ...
    
    def get_dimension_criteria(self, dimension: str) -> dict:
        """Return scoring criteria for rater reference."""
        ...
    
    def validate_score(self, dimension: str, score: int) -> bool:
        """Check if score is valid (0/5/10)."""
        ...


class RaterScoreSheet:
    """Interface for manual score entry."""
    
    def __init__(self, rater_id: str, rubric: ArtifactQualityRubric): ...
    
    def load_artifacts(self, artifact_dir: str):
        """Load artifact content for coding."""
        ...
    
    def record_score(self, benchmark_id: str, dimension: str, score: int):
        """Record single dimension score."""
        ...
    
    def save_scores(self, output_path: str):
        """Export rater{N}_scores.csv (20 rows × 4 dimensions)."""
        ...
```

---

### 4. Statistical Validation (`analysis/reliability.py`)

**Dependencies:** sklearn.metrics, pandas, numpy

```python
class InterRaterReliability:
    """Cohen's kappa calculation and interpretation."""
    
    def __init__(self, config: QualityStudyConfig): ...
    
    def calculate_kappa(self, rater1_scores: pd.Series, rater2_scores: pd.Series) -> float:
        """Compute Cohen's kappa.
        
        Returns:
            float: Kappa value (-1 to 1)
        """
        from sklearn.metrics import cohen_kappa_score
        return cohen_kappa_score(rater1_scores, rater2_scores)
    
    def interpret_kappa(self, kappa: float) -> str:
        """Return reliability interpretation."""
        ...
    
    def check_gate(self, kappa: float, threshold: float = 0.8) -> bool:
        """Validate measurement reliability gate."""
        ...
    
    def generate_discrepancy_report(self, rater1: pd.DataFrame, rater2: pd.DataFrame) -> pd.DataFrame:
        """Identify disagreements for re-calibration."""
        ...


class QualityScoreAggregator:
    """Aggregate dimension scores to overall quality."""
    
    def __init__(self, config: QualityStudyConfig): ...
    
    def aggregate_dimensions(self, rater_scores: pd.DataFrame) -> pd.Series:
        """Mean across 4 dimensions for each benchmark."""
        ...
    
    def aggregate_raters(self, rater1_quality: pd.Series, rater2_quality: pd.Series) -> pd.Series:
        """Average scores across 2 raters."""
        ...
    
    def calculate_mean_quality(self, quality_scores: pd.Series) -> float:
        """Compute mean across 20 benchmarks."""
        ...
    
    def check_quality_gate(self, mean_quality: float, threshold: float = 7.0) -> bool:
        """MUST_WORK gate: mean > 7.0."""
        ...
```

---

### 5. Visualization (`visualization/plots.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class QualityVisualization:
    """Generate artifact quality visualizations."""
    
    def __init__(self, config: QualityStudyConfig): ...
    
    def plot_gate_metrics(self, actual_kappa: float, actual_quality: float, save_path: str):
        """MANDATORY: Target vs actual metrics comparison."""
        ...
    
    def plot_quality_distribution(self, quality_scores: pd.Series, save_path: str):
        """Histogram of quality scores across 20 benchmarks."""
        ...
    
    def plot_dimension_breakdown(self, dimension_scores: pd.DataFrame, save_path: str):
        """Grouped bar chart for rubric dimensions."""
        ...
    
    def plot_domain_comparison(self, quality_by_domain: dict, save_path: str):
        """Box plots: CV vs NLP quality."""
        ...
    
    def plot_inter_rater_agreement(self, rater1: pd.Series, rater2: pd.Series, save_path: str):
        """Scatter plot with diagonal reference."""
        ...
```

---

### 6. Report Generation (`reporting/validator.py`)

**Dependencies:** All analysis modules

```python
class ValidationReportGenerator:
    """Generate 04_validation.md with gate decision logic."""
    
    def __init__(self, config: QualityStudyConfig): ...
    
    def load_results(self, scores_dir: str) -> dict:
        """Load rater scores and computed metrics."""
        ...
    
    def determine_gate_status(self, kappa: float, mean_quality: float) -> str:
        """Decision logic: PASS, PIVOT, or FAIL."""
        ...
    
    def generate_report(self, results: dict, output_path: str):
        """Write complete validation report."""
        ...
```

---

### 7. Main Orchestration (`main.py`)

**Dependencies:** All modules

```python
def run_quality_study():
    """Execute H-M1 artifact quality assessment protocol."""
    
    # Phase 1: Benchmark sampling
    sampler = BenchmarkSampler(config)
    benchmarks = sampler.fetch_classification_benchmarks(...)
    sample = sampler.stratified_sample(benchmarks, strata={"CV": 10, "NLP": 10})
    sampler.save_sample(sample, output_dir)
    
    # Phase 2: Artifact retrieval
    retriever = ArtifactRetriever(config)
    for benchmark_id in sample['benchmark_id']:
        artifacts = {
            'github_readme': retriever.retrieve_github_readme(...),
            'dataset_card': retriever.retrieve_dataset_card(...),
            'badge_metadata': retriever.retrieve_badge_metadata(...)
        }
        retriever.save_artifacts(benchmark_id, artifacts, output_dir)
    
    # Phase 3-4: Manual coding (external to code)
    # Raters use RaterScoreSheet to enter scores
    
    # Phase 5: Reliability analysis
    reliability = InterRaterReliability(config)
    rater1 = pd.read_csv('data/scores/rater1_scores.csv')
    rater2 = pd.read_csv('data/scores/rater2_scores.csv')
    kappa = reliability.calculate_kappa(rater1['quality_score'], rater2['quality_score'])
    
    if not reliability.check_gate(kappa, threshold=0.8):
        print("⚠️ Kappa < 0.8: Refine rubric and re-code")
        return
    
    # Phase 6: Quality score aggregation
    aggregator = QualityScoreAggregator(config)
    quality_scores = aggregator.aggregate_raters(
        aggregator.aggregate_dimensions(rater1),
        aggregator.aggregate_dimensions(rater2)
    )
    mean_quality = aggregator.calculate_mean_quality(quality_scores)
    
    # Gate decision
    if not aggregator.check_quality_gate(mean_quality, threshold=7.0):
        print("🚨 PIVOT: Mean quality < 7.0 (artifacts lack information)")
    else:
        print("✅ PASS: Artifacts provide actionable information")
    
    # Visualization
    viz = QualityVisualization(config)
    viz.plot_gate_metrics(kappa, mean_quality, save_path)
    viz.plot_quality_distribution(quality_scores, save_path)
    viz.plot_dimension_breakdown(dimension_scores, save_path)
    viz.plot_domain_comparison(quality_by_domain, save_path)
    viz.plot_inter_rater_agreement(rater1, rater2, save_path)
    
    # Report
    reporter = ValidationReportGenerator(config)
    results = {...}
    reporter.generate_report(results, output_path)


if __name__ == "__main__":
    run_quality_study()
```

---

## File Organization

```
h-m1/
├── code/
│   ├── config.py                    # Study configuration
│   ├── main.py                      # Orchestration script
│   ├── data/
│   │   ├── collector.py             # BenchmarkSampler, ArtifactRetriever
│   ├── scoring/
│   │   ├── rubric.py                # ArtifactQualityRubric, RaterScoreSheet
│   ├── analysis/
│   │   ├── reliability.py           # InterRaterReliability, QualityScoreAggregator
│   ├── visualization/
│   │   ├── plots.py                 # QualityVisualization
│   ├── reporting/
│   │   ├── validator.py             # ValidationReportGenerator
│   └── tests/
│       ├── test_reliability.py      # Cohen's kappa tests
│       └── test_rubric.py           # Rubric validation tests
├── data/
│   ├── raw/
│   │   └── benchmark_sample.csv     # 20 benchmarks (10 CV + 10 NLP)
│   ├── artifacts/
│   │   └── {benchmark_id}/
│   │       ├── github_readme.md
│   │       ├── dataset_card.md
│   │       └── badge_metadata.json
│   └── scores/
│       ├── rater1_scores.csv        # 20 rows × 4 dimensions
│       └── rater2_scores.csv
├── figures/
│   ├── gate_metrics.png             # MANDATORY
│   ├── quality_distribution.png
│   ├── dimension_breakdown.png
│   ├── domain_comparison.png
│   └── inter_rater_agreement.png
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md               # This document
└── 04_validation.md                 # Generated by code
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Data Collection Infrastructure | BenchmarkSampler + ArtifactRetriever modules | 12 | 3+3+3+3 (module_size=3, deps=3, algorithm=3, integration=3) |
| M1-2 | Rubric Scoring System | ArtifactQualityRubric + RaterScoreSheet interfaces | 10 | 3+2+3+2 (rubric definition=3, score validation=2, CSV I/O=3, integration=2) |
| M1-3 | Manual Coding Protocol | Rater training materials + score entry workflow | 8 | 2+2+2+2 (training docs=2, rubric calibration=2, pilot testing=2, score entry=2) |
| M1-4 | Inter-Rater Reliability | Cohen's kappa implementation + discrepancy analysis | 11 | 2+3+4+2 (sklearn wrapper=2, statistical tests=3, interpretation=4, reporting=2) |
| M1-5 | Quality Score Aggregation | Dimension averaging + rater averaging + gate checks | 9 | 2+2+3+2 (dimension aggregation=2, rater averaging=2, gate logic=3, output=2) |
| M1-6 | Statistical Validation | Reliability checks + quality threshold gates | 10 | 2+3+3+2 (kappa validation=2, quality validation=3, decision logic=3, error handling=2) |
| M1-7 | Visualization Suite | 5 plots including mandatory gate metrics | 13 | 3+2+5+3 (matplotlib setup=3, data prep=2, 5 plot types=5, styling=3) |
| M1-8 | Report Generation | 04_validation.md with gate decision + metrics | 11 | 3+2+4+2 (markdown template=3, data aggregation=2, gate decision rendering=4, file I/O=2) |
| M1-9 | Data Pipeline Integration | End-to-end workflow from sampling to report | 14 | 4+3+4+3 (orchestration=4, error handling=3, logging=4, file management=3) |
| M1-10 | Testing Suite | Unit tests for reliability + rubric validation | 10 | 2+3+3+2 (test fixtures=2, kappa tests=3, rubric tests=3, CI setup=2) |

**Complexity Distribution:**
- High (14-17): [M1-9]
- Medium (9-13): [M1-1, M1-2, M1-4, M1-5, M1-6, M1-7, M1-8, M1-10]
- Low (4-8): [M1-3]

**Total Complexity:** 108 (average 10.8 per task)

---

## External Dependencies (From h-e1)

### Reusable Components

| Component | Import Path | Source File |
|-----------|-------------|-------------|
| PapersWithCodeCollector | `from h_e1.data.collector import PapersWithCodeCollector` | `h-e1/code/data/collector.py` |
| ValidationConfig (pattern) | Reference only | `h-e1/code/config.py` |

**Note:** h-m1 does NOT directly import h-e1 modules. Instead, it reuses the **design pattern** (API client with retry logic) and reimplements for artifact retrieval instead of benchmark validation.

---

## Key Design Decisions

1. **Manual Coding Instead of Automated Extraction:** Artifact quality requires human judgment of "completeness" and "actionability" - cannot be automated reliably.

2. **Stratified Sampling (CV/NLP):** Ensures domain diversity in quality assessment. Different communities may have different documentation practices.

3. **Two Independent Raters:** Standard best practice for content analysis. Cohen's kappa > 0.8 ensures measurement validity.

4. **3-Level Scoring (0/5/10):** Balances granularity with inter-rater agreement. Too many levels reduce reliability.

5. **Gate Hierarchy:** Kappa gate checked BEFORE quality gate. Invalid measurement makes quality assessment meaningless.

---

## Gate Decision Logic

```
IF kappa < 0.8:
    → Measurement unreliable
    → Refine rubric and re-code
    → DO NOT proceed to quality gate
ELIF mean_quality < 7.0:
    → PIVOT: Artifacts lack information
    → H-M2/H-M3 must use quality-weighted analysis
    → Update downstream hypotheses
ELSE:
    → PASS: Artifacts provide actionable information
    → Proceed to H-M2 (benchmark accessibility mechanism)
```

---

## Statistical Validation Requirements

1. **Inter-Rater Reliability (Cohen's Kappa):**
   - Metric: `sklearn.metrics.cohen_kappa_score(rater1, rater2)`
   - Threshold: > 0.8 (excellent reliability)
   - Interpretation: < 0.40 poor, 0.40-0.59 fair, 0.60-0.79 good, ≥ 0.80 excellent

2. **Mean Quality Score:**
   - Metric: `quality_scores.mean()` (0-10 scale)
   - Threshold: > 7.0 (artifacts informative, not boilerplate)
   - Calculation: Mean across 4 dimensions → Mean across 2 raters → Mean across 20 benchmarks

3. **Dimension-Level Analysis (Secondary):**
   - Identify which rubric dimensions have highest/lowest quality
   - Purpose: Understand artifact strengths/weaknesses

4. **Domain Comparison (Exploratory):**
   - CV vs NLP quality scores
   - Statistical test: Mann-Whitney U (non-parametric)
   - Purpose: Hypothesis-neutral exploration

---

## Implementation Notes

**Rater Training Protocol:**
1. Present rubric with dimension definitions and scoring criteria
2. Jointly code 3 pilot benchmarks
3. Discuss discrepancies and refine rubric if needed
4. Independent coding begins only after calibration

**Quality Score Calculation:**
- Each rater scores 4 dimensions (0/5/10) for each of 20 benchmarks
- Benchmark quality = mean(4 dimension scores)
- Final quality = mean(rater1_quality, rater2_quality)
- Overall mean = mean(20 final qualities)

**API Integration:**
- Reuse h-e1 pattern: Rate limiting (1 req/sec), exponential backoff retry
- NEW: GitHub API for README retrieval
- NEW: Dataset card retrieval (HuggingFace API if applicable)

**Error Handling:**
- Missing artifacts: Log and skip, don't fail entire process
- Inaccessible URLs: Record as "artifact_unavailable" in metadata
- API failures: Retry 3 times with exponential backoff

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Code Implementation (Step 4)
