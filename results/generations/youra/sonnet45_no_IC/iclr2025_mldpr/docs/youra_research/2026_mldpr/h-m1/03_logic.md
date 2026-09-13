# Logic Design: H-M1 Artifact Quality Assessment

**Date:** 2026-07-12  
**Hypothesis:** h-m1 (MECHANISM)  
**Type:** Observational Study (Content Analysis)  
**Budget:** 11 subtasks (high/medium complexity)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New observational study implementation - no existing h-m1 code  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - designing new content analysis APIs  

**Note:** This is a research study protocol, not an ML model. Architecture references h-e1 patterns (API client with retry logic) but implements them independently for artifact quality assessment.

---

## Applied Patterns (Archon KB)

**Applied:** Standard statistical libraries (sklearn, pandas), requests retry pattern

Archon KB searches confirmed standard patterns for:
- Cohen's kappa: `sklearn.metrics.cohen_kappa_score`
- Pandas data manipulation for stratified sampling
- HTTP client with retry logic

No custom rubric scoring libraries found - implementing domain-specific quality assessment protocol.

---

## M1-1: Data Collection Infrastructure [Complexity: 12, Budget: 3]

**Applied:** Requests library with pagination handling, pandas DataFrame operations

### API Signatures

```python
from typing import Optional, Dict, List
import pandas as pd
import requests
from dataclasses import dataclass

@dataclass
class QualityStudyConfig:
    """Study configuration parameters."""
    API_BASE_URL: str = "https://paperswithcode.com/api/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    SAMPLE_SIZE: int = 20
    STRATIFICATION: Dict[str, int] = None
    START_YEAR: int = 2019
    END_YEAR: int = 2024
    MIN_ARTIFACT_COUNT: int = 2
    
    def __post_init__(self):
        if self.STRATIFICATION is None:
            self.STRATIFICATION = {"CV": 10, "NLP": 10}


class BenchmarkSampler:
    """Stratified sampling of benchmarks from Papers with Code."""
    
    def __init__(self, config: QualityStudyConfig):
        """Initialize sampler with config."""
        self.config = config
        self.session = requests.Session()
    
    def fetch_classification_benchmarks(
        self, 
        task: str = "classification", 
        start_year: int = 2019, 
        end_year: int = 2024
    ) -> pd.DataFrame:
        """Fetch benchmarks via API with pagination. Returns: DataFrame [N_benchmarks, ~10 columns]"""
        ...
    
    def stratified_sample(
        self, 
        benchmarks: pd.DataFrame, 
        strata: Dict[str, int]
    ) -> pd.DataFrame:
        """Sample n benchmarks per domain. Returns: [20, ~10] (10 CV + 10 NLP)"""
        ...
    
    def save_sample(self, sample: pd.DataFrame, output_dir: str) -> None:
        """Export benchmark_sample.csv."""
        ...


class ArtifactRetriever:
    """Download artifact content for manual coding."""
    
    def __init__(self, config: QualityStudyConfig):
        """Initialize retriever with config."""
        self.config = config
        self.session = requests.Session()
    
    def retrieve_github_readme(self, repo_url: str) -> str:
        """Fetch README.md via GitHub API. Returns: raw markdown string"""
        ...
    
    def retrieve_dataset_card(self, dataset_url: str) -> str:
        """Fetch dataset card content. Returns: raw markdown/text"""
        ...
    
    def retrieve_badge_metadata(self, benchmark_id: str) -> Dict:
        """Extract badge documentation. Returns: {status, url, metadata}"""
        ...
    
    def save_artifacts(
        self, 
        benchmark_id: str, 
        artifacts: Dict[str, str], 
        output_dir: str
    ) -> None:
        """Store in artifact_content/{benchmark_id}/."""
        ...
```

### Pseudo-code

```
1. Initialize BenchmarkSampler with config
2. Fetch all classification benchmarks (2019-2024) via API
   - Handle pagination: while next_page exists
   - Filter: artifact_count >= 2
3. Group by domain (CV vs NLP)
4. Stratified sampling: random_sample(10) per domain
5. For each benchmark in sample:
   - Retrieve GitHub README via API
   - Retrieve dataset card if URL present
   - Extract badge metadata
   - Save to artifact_content/{id}/
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | API client | Requests session with rate limiting (1 req/sec) |
| L-1-2 | Stratified sampling | Pandas groupby + sample |
| L-1-3 | Artifact retrieval | GitHub/dataset API calls with error handling |

---

## M1-2: Rubric Scoring System [Complexity: 10, Budget: 2]

**Applied:** Standard Python dictionaries for rubric definition, pandas CSV I/O

### API Signatures

```python
from typing import Dict, Optional

class ArtifactQualityRubric:
    """Structured rubric for manual artifact assessment."""
    
    RUBRIC_DIMENSIONS: Dict[str, Dict[str, str]] = {
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
    
    def get_dimension_criteria(self, dimension: str) -> Dict[str, str]:
        """Return scoring criteria for rater reference."""
        ...
    
    def validate_score(self, dimension: str, score: int) -> bool:
        """Check if score is valid (0/5/10)."""
        ...


class RaterScoreSheet:
    """Interface for manual score entry."""
    
    def __init__(self, rater_id: str, rubric: ArtifactQualityRubric):
        """Initialize score sheet for rater."""
        self.rater_id = rater_id
        self.rubric = rubric
        self.scores: Dict = {}
    
    def load_artifacts(self, artifact_dir: str) -> None:
        """Load artifact content for coding."""
        ...
    
    def record_score(self, benchmark_id: str, dimension: str, score: int) -> None:
        """Record single dimension score."""
        ...
    
    def save_scores(self, output_path: str) -> None:
        """Export rater{N}_scores.csv. Shape: [20, 5] (id + 4 dimensions)"""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Rubric definition | Dictionary with scoring criteria |
| L-2-2 | Score entry interface | CSV-based manual entry system |

---

## M1-4: Inter-Rater Reliability [Complexity: 11, Budget: 2]

**Applied:** sklearn.metrics.cohen_kappa_score

### API Signatures

```python
from sklearn.metrics import cohen_kappa_score
import pandas as pd
from typing import Tuple

class InterRaterReliability:
    """Cohen's kappa calculation and interpretation."""
    
    def __init__(self, config: QualityStudyConfig):
        """Initialize with config."""
        self.config = config
    
    def calculate_kappa(
        self, 
        rater1_scores: pd.Series, 
        rater2_scores: pd.Series
    ) -> float:
        """Compute Cohen's kappa. Both series: [20] Returns: kappa in [-1, 1]"""
        return cohen_kappa_score(rater1_scores, rater2_scores)
    
    def interpret_kappa(self, kappa: float) -> str:
        """Return reliability interpretation. Returns: 'excellent'|'good'|'fair'|'poor'"""
        ...
    
    def check_gate(self, kappa: float, threshold: float = 0.8) -> bool:
        """Validate measurement reliability gate. Returns: kappa >= threshold"""
        ...
    
    def generate_discrepancy_report(
        self, 
        rater1: pd.DataFrame, 
        rater2: pd.DataFrame
    ) -> pd.DataFrame:
        """Identify disagreements. Returns: [N_disagreements, 4] (id, dim, r1, r2)"""
        ...
```

### Pseudo-code

```
1. Load rater1_scores.csv and rater2_scores.csv
2. For each dimension:
   - kappa_dim = cohen_kappa_score(r1[dim], r2[dim])
3. Overall kappa = mean(kappa_dimensions)
4. If kappa < 0.8:
   - Generate discrepancy report (where r1 != r2)
   - Return FAIL with refinement instructions
5. Else: PASS reliability gate
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Kappa calculation | sklearn wrapper with multi-dimension support |
| L-4-2 | Discrepancy analysis | DataFrame diff operations |

---

## M1-5: Quality Score Aggregation [Complexity: 9, Budget: 2]

**Applied:** Pandas mean/aggregation operations

### API Signatures

```python
import pandas as pd

class QualityScoreAggregator:
    """Aggregate dimension scores to overall quality."""
    
    def __init__(self, config: QualityStudyConfig):
        """Initialize with config."""
        self.config = config
    
    def aggregate_dimensions(self, rater_scores: pd.DataFrame) -> pd.Series:
        """Mean across 4 dimensions for each benchmark. Input: [20, 5], Returns: [20]"""
        ...
    
    def aggregate_raters(
        self, 
        rater1_quality: pd.Series, 
        rater2_quality: pd.Series
    ) -> pd.Series:
        """Average scores across 2 raters. Both: [20], Returns: [20]"""
        ...
    
    def calculate_mean_quality(self, quality_scores: pd.Series) -> float:
        """Compute mean across 20 benchmarks. Input: [20], Returns: scalar in [0, 10]"""
        ...
    
    def check_quality_gate(self, mean_quality: float, threshold: float = 7.0) -> bool:
        """MUST_WORK gate check. Returns: mean_quality >= threshold"""
        ...
```

### Pseudo-code

```
1. For each rater:
   - quality_per_benchmark = mean(preprocessing, splits, eval, hyperparams)
2. final_quality = (rater1_quality + rater2_quality) / 2  # [20]
3. mean_quality = final_quality.mean()  # scalar
4. Gate: mean_quality >= 7.0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Dimension aggregation | Pandas mean across columns |
| L-5-2 | Rater aggregation | Element-wise mean with gate logic |

---

## M1-6: Statistical Validation [Complexity: 10, Budget: 1]

**Applied:** Combined reliability + quality validation with decision tree logic

### API Signatures

```python
from typing import Tuple
from enum import Enum

class GateStatus(Enum):
    PASS = "pass"
    PIVOT = "pivot"
    FAIL = "fail"


class StatisticalValidator:
    """Hierarchical gate validation."""
    
    def __init__(self, config: QualityStudyConfig):
        """Initialize validator."""
        self.config = config
    
    def validate_gates(
        self, 
        kappa: float, 
        mean_quality: float
    ) -> Tuple[GateStatus, str]:
        """
        Hierarchical gate check.
        Returns: (status, message)
        Logic: kappa gate first, then quality gate
        """
        ...
```

### Pseudo-code

```
IF kappa < 0.8:
    → FAIL: "Measurement unreliable, refine rubric"
ELIF mean_quality < 7.0:
    → PIVOT: "Artifacts lack information, use quality-weighted analysis"
ELSE:
    → PASS: "Artifacts contain actionable information"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Gate decision logic | Hierarchical threshold checks |

---

## M1-7: Visualization Suite [Complexity: 13, Budget: 1]

**Applied:** Matplotlib/seaborn standard plotting patterns

### API Signatures

```python
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict

class QualityVisualization:
    """Generate artifact quality visualizations."""
    
    def __init__(self, config: QualityStudyConfig):
        """Initialize with config."""
        self.config = config
    
    def plot_gate_metrics(
        self, 
        actual_kappa: float, 
        actual_quality: float, 
        save_path: str
    ) -> None:
        """MANDATORY: Bar chart comparing target vs actual. Saves to PNG."""
        ...
    
    def plot_quality_distribution(
        self, 
        quality_scores: pd.Series, 
        save_path: str
    ) -> None:
        """Histogram of scores. Input: [20], saves to PNG."""
        ...
    
    def plot_dimension_breakdown(
        self, 
        dimension_scores: pd.DataFrame, 
        save_path: str
    ) -> None:
        """Grouped bar chart. Input: [20, 4], saves to PNG."""
        ...
    
    def plot_domain_comparison(
        self, 
        quality_by_domain: Dict[str, pd.Series], 
        save_path: str
    ) -> None:
        """Box plots CV vs NLP. Input: {'CV': [10], 'NLP': [10]}, saves to PNG."""
        ...
    
    def plot_inter_rater_agreement(
        self, 
        rater1: pd.Series, 
        rater2: pd.Series, 
        save_path: str
    ) -> None:
        """Scatter plot. Both: [20], saves to PNG."""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Plot generation | 5 matplotlib figures with consistent styling |

---

## M1-8: Report Generation [Complexity: 11, Budget: 0]

**Applied:** Template-based markdown generation with f-strings

### API Signatures

```python
from typing import Dict, Any

class ValidationReportGenerator:
    """Generate 04_validation.md with gate decision."""
    
    def __init__(self, config: QualityStudyConfig):
        """Initialize with config."""
        self.config = config
    
    def load_results(self, scores_dir: str) -> Dict[str, Any]:
        """Load rater scores and computed metrics. Returns: results dict"""
        ...
    
    def determine_gate_status(self, kappa: float, mean_quality: float) -> str:
        """Decision logic. Returns: 'PASS'|'PIVOT'|'FAIL'"""
        ...
    
    def generate_report(self, results: Dict[str, Any], output_path: str) -> None:
        """Write 04_validation.md with full results."""
        ...
```

### Pseudo-code

```
1. Load all metrics: kappa, mean_quality, dimension_scores
2. Determine gate status via hierarchical logic
3. Render markdown template:
   - Executive summary with gate decision
   - Inter-rater reliability section (kappa + interpretation)
   - Quality score results (mean + distribution)
   - Dimension breakdown table
   - Domain comparison (CV vs NLP)
   - Figure references
4. Write to 04_validation.md
```

---

## M1-9: Data Pipeline Integration [Complexity: 14, Budget: 0]

**Applied:** Sequential pipeline orchestration with error handling

### API Signatures

```python
from typing import Optional
import logging

def run_quality_study(config: Optional[QualityStudyConfig] = None) -> None:
    """
    Execute H-M1 artifact quality assessment protocol.
    
    Pipeline:
    1. Benchmark sampling (BenchmarkSampler)
    2. Artifact retrieval (ArtifactRetriever)
    3. Manual coding (external - RaterScoreSheet used by human raters)
    4. Reliability analysis (InterRaterReliability)
    5. Quality aggregation (QualityScoreAggregator)
    6. Visualization (QualityVisualization)
    7. Report generation (ValidationReportGenerator)
    """
    ...


def setup_logging(log_file: str = "quality_study.log") -> None:
    """Configure logging for pipeline execution."""
    ...
```

### Pseudo-code

```
1. Setup logging and directories
2. Phase 1: Sampling
   - sampler.fetch_classification_benchmarks()
   - sampler.stratified_sample()
   - sampler.save_sample()
3. Phase 2: Artifact retrieval
   - For each benchmark: retriever.retrieve_*()
   - Save to artifact_content/
4. Phase 3-4: Manual coding (PAUSE - external human process)
   - Raters use RaterScoreSheet to enter scores
   - Generate rater1_scores.csv, rater2_scores.csv
5. Phase 5: Reliability check
   - Calculate kappa
   - If kappa < 0.8: STOP with error
6. Phase 6: Quality aggregation
   - Aggregate dimensions and raters
   - Check quality gate
7. Phase 7: Visualization and reporting
   - Generate 5 plots
   - Write 04_validation.md
```

---

## M1-10: Testing Suite [Complexity: 10, Budget: 0]

**Applied:** Pytest with fixtures for test data

### API Signatures

```python
import pytest
import pandas as pd

@pytest.fixture
def mock_rater_scores() -> pd.DataFrame:
    """Generate mock scoring data. Returns: [20, 5] DataFrame"""
    ...


def test_cohen_kappa_perfect_agreement():
    """Test kappa = 1.0 when raters agree completely."""
    ...


def test_rubric_score_validation():
    """Test score validation rejects invalid values."""
    ...


def test_quality_aggregation():
    """Test dimension and rater aggregation logic."""
    ...


def test_gate_decision_logic():
    """Test hierarchical gate validation."""
    ...
```

---

## Summary

**Total Subtasks:** 11/11 used

**Design Principles:**
1. **Statistical rigor:** Cohen's kappa for measurement validity
2. **Simplicity:** Standard libraries (sklearn, pandas) - no custom ML models
3. **Transparency:** Full pipeline logged and reproducible
4. **Human-in-loop:** Manual coding protocol with clear interfaces

**Critical Dependencies:**
- sklearn.metrics.cohen_kappa_score (inter-rater reliability)
- pandas (data manipulation, sampling, aggregation)
- requests (API client)
- matplotlib/seaborn (visualization)

**No model training:** This is an observational study measuring artifact quality, not an ML experiment. Primary logic is statistical validation and data aggregation.

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Code Implementation (Step 4)
