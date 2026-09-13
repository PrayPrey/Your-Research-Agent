# Logic Design: H-E1 - Documentation Gap Validation Study

**Date:** 2026-07-12  
**Hypothesis:** H-E1 (EXISTENCE - FOUNDATION)  
**Type:** Observational Study (Data Collection + Statistical Analysis)  
**Author:** Logic Agent  
**Status:** DRAFT v1.0  

---

## Codebase Analysis (Serena)

**Project Type:** Green-field  
**Status:** New implementation from scratch - first temporal documentation measurement study  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation  

---

## Applied Patterns

**Applied:** Data Pipeline Pattern (ETL for observational studies)  
**Applied:** Retry Pattern with Exponential Backoff (API resilience)  
**Applied:** HuggingFace Hub snapshot_download (repository cloning)

---

## E-1: Data Collection Pipeline (Complexity: 15, Budget: 3)

High-complexity task focused on API integration and T0 fallback logic.

### API Signatures

```python
from typing import Optional, Tuple, List, Dict
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
from github import Github
from huggingface_hub import HfApi, snapshot_download
import time

# src/sampling.py
class RepositorySampler:
    def __init__(self, api_token: Optional[str] = None, random_seed: int = 42):
        """Initialize HuggingFace Hub sampler."""
        self.api = HfApi(token=api_token)
        self.random_seed = random_seed

    def fetch_datasets(
        self, 
        start_date: str, 
        end_date: str, 
        min_stars: int
    ) -> pd.DataFrame:
        """Fetch datasets from HuggingFace Hub. Returns: [repo_id, created_at, likes]"""
        ...

    def stratify_by_year(self, df: pd.DataFrame, n_per_year: int) -> pd.DataFrame:
        """Stratified sampling by year. df: [year] -> sampled df"""
        ...

    def export_sample(self, df: pd.DataFrame, output_path: str) -> None:
        """Export to CSV."""
        ...

# src/t0_detection.py
class T0Detector:
    def __init__(self, github_token: str, max_retries: int = 3):
        """Initialize GitHub API client with retry logic."""
        self.github = Github(github_token)
        self.max_retries = max_retries

    def detect_t0_tier1(self, repo_id: str) -> Optional[Tuple[datetime, str]]:
        """Tier 1: Release tags. Returns: (t0_datetime, commit_sha) or None"""
        ...

    def detect_t0_tier2(self, repo_id: str) -> Optional[Tuple[datetime, str]]:
        """Tier 2: Dataset commit heuristics. Returns: (t0_datetime, commit_sha) or None"""
        ...

    def detect_t0_tier3(self, repo_id: str) -> Tuple[datetime, str]:
        """Tier 3: Repository creation (always succeeds). Returns: (t0_datetime, first_commit_sha)"""
        ...

    def detect_t0_three_tier(self, repo_id: str) -> Tuple[datetime, str, str]:
        """3-tier fallback. Returns: (t0_datetime, commit_sha, tier_method)"""
        ...

    def get_commit_at_date(self, repo_id: str, target_date: datetime) -> str:
        """Find commit SHA closest to target_date. Returns: commit_sha"""
        ...

    def _exponential_backoff_retry(self, func, *args, **kwargs):
        """Retry logic with exponential backoff for API rate limits."""
        ...

# src/cloning.py
class RepositoryCloner:
    def __init__(self, base_dir: str = "./data/repos"):
        """Initialize cloner with base directory."""
        self.base_dir = Path(base_dir)

    def clone_at_revision(self, repo_id: str, commit_sha: str) -> Path:
        """Clone repo at specific revision. Returns: local_path"""
        ...

    def verify_clone(self, repo_path: Path) -> bool:
        """Verify README.md exists."""
        ...

    def extract_documentation_files(self, repo_path: Path) -> Dict[str, bool]:
        """Extract doc file existence. Returns: {has_readme, has_dataset_card, has_license, has_other_md}"""
        ...
```

### Algorithm: 3-Tier T0 Fallback

```
Input: repo_id (str)
Output: (t0_datetime, commit_sha, tier_method)

1. Try Tier 1 (Release Tags):
   result = detect_t0_tier1(repo_id)
   IF result is not None:
       RETURN (result.datetime, result.sha, "tier1")

2. Try Tier 2 (Dataset Commit Heuristics):
   result = detect_t0_tier2(repo_id)
   IF result is not None:
       RETURN (result.datetime, result.sha, "tier2")

3. Fallback to Tier 3 (Repository Creation):
   result = detect_t0_tier3(repo_id)
   RETURN (result.datetime, result.sha, "tier3")

Tier 1 Details:
- Fetch all tags: repo.get_tags()
- Filter semantic version tags (v0.1.0, 1.0.0)
- Sort by date (ascending)
- Return first tag's commit

Tier 2 Details:
- Fetch all commits: repo.get_commits()
- Patterns: ["add dataset", "upload data", "initial commit", "first release"]
- Iterate commits, check message.lower() against patterns
- Return first matching commit

Tier 3 Details:
- Get repo.created_at (always exists)
- Get first commit in history: list(repo.get_commits())[-1]
- Return (created_at, first_commit.sha)
```

### Algorithm: Exponential Backoff Retry

```
Input: func (API call), max_retries=3
Output: API result or raise exception

FOR attempt in range(max_retries):
    TRY:
        result = func()
        RETURN result
    EXCEPT RateLimitExceeded as e:
        IF attempt == max_retries - 1:
            RAISE e
        wait_time = 2^attempt * 60  # 1min, 2min, 4min
        sleep(wait_time)
    EXCEPT Timeout as e:
        IF attempt == max_retries - 1:
            RAISE e
        wait_time = 2^attempt * 10  # 10s, 20s, 40s
        sleep(wait_time)

RAISE Exception("Max retries exceeded")
```

### Tensor Shapes (Data Structures)

| Variable | Shape | Description |
|----------|-------|-------------|
| sampled_df | [120, 4] | Columns: repo_id, created_at, likes, sample_year |
| t0_results_df | [120, 6] | Columns: repo_id, t0, t0_method, commit_sha, t0_success, clone_success |
| doc_files_df | [100, 5] | Columns: repo_id, has_readme, has_dataset_card, has_license, has_other_md |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | API Integration Module | HuggingFace Hub API + GitHub API wrappers with auth |
| L-1-2 | 3-Tier T0 Fallback | Implement tier1/2/3 detection logic with pattern matching |
| L-1-3 | Retry & Error Handling | Exponential backoff for rate limits + timeout handling |

---

## E-2: Manual Coding Infrastructure (Complexity: 9, Budget: 0)

Standard implementation, no logic subtasks needed.

### API Signatures

```python
# src/dcs_coding.py
class DCSCoder:
    def __init__(self):
        """Initialize DCS coding module."""
        ...

    def create_coding_template(self, repo_ids: List[str], output_path: str) -> None:
        """Generate Excel template with rubric. repo_ids: list -> Excel file"""
        ...

    def load_coding_results(self, coding_file: str) -> pd.DataFrame:
        """Load completed coding CSV. Returns: [repo_id, dcs_data_context, dcs_preprocessing, dcs_licensing, dcs_3_total, compliant]"""
        ...

    def calculate_dcs_total(self, row: pd.Series) -> float:
        """Sum 3 components. row: Series -> float [0-3]"""
        ...

    def determine_compliance(self, dcs_total: float, threshold: float = 2.4) -> bool:
        """Binary compliance. dcs_total: float -> bool"""
        ...
```

---

## E-3: Statistical Analysis Engine (Complexity: 12, Budget: 0)

Standard statistical methods, no logic subtasks needed.

### API Signatures

```python
from scipy import stats
from statsmodels.stats.proportion import proportion_confint
from sklearn.metrics import cohen_kappa_score

# src/statistics.py
class StatisticalAnalyzer:
    def __init__(self):
        """Initialize statistical analyzer."""
        ...

    def calculate_compliance_rate(
        self, 
        df: pd.DataFrame
    ) -> Tuple[float, float, float]:
        """Calculate rate + Wilson CI. df: [compliant] -> (rate, ci_lower, ci_upper)"""
        ...

    def component_breakdown_chi2(
        self, 
        df: pd.DataFrame
    ) -> Tuple[float, float, List[int]]:
        """Chi-square test for component uniformity. df: [3 components] -> (chi2_stat, p_value, counts)"""
        ...

    def calculate_irr(
        self, 
        coder1_df: pd.DataFrame, 
        coder2_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Cohen's kappa for IRR. Returns: {kappa_overall, kappa_data_context, kappa_preprocessing, kappa_licensing}"""
        ...

    def check_gate_criteria(
        self, 
        ci_upper: float, 
        chi2_p: float, 
        kappa: float
    ) -> Dict[str, bool]:
        """Validate gate criteria. Returns: {primary_gate, secondary_gate, quality_gate}"""
        ...
```

---

## E-4: Visualization Suite (Complexity: 8, Budget: 0)

Standard matplotlib charts, no logic subtasks needed.

### API Signatures

```python
import matplotlib.pyplot as plt

# src/visualization.py
class Visualizer:
    def __init__(self, output_dir: str = "./figures"):
        """Initialize visualizer."""
        self.output_dir = Path(output_dir)

    def plot_compliance_rate(
        self, 
        observed: float, 
        ci_lower: float, 
        ci_upper: float
    ) -> None:
        """Bar chart with H0/H1 reference. Saves to compliance_rate.png"""
        ...

    def plot_component_breakdown(self, df: pd.DataFrame) -> None:
        """Stacked bar chart. df: [3 components] -> component_breakdown.png"""
        ...

    def plot_t0_detection_breakdown(self, df: pd.DataFrame) -> None:
        """Pie chart. df: [t0_method] -> t0_detection_breakdown.png"""
        ...

    def plot_dcs_distribution(self, df: pd.DataFrame) -> None:
        """Histogram. df: [dcs_3_total] -> dcs_distribution.png"""
        ...
```

---

## E-5: Pipeline Orchestration (Complexity: 11, Budget: 0)

Sequential execution, no complex logic needed.

### API Signatures

```python
# src/pipeline.py
class StudyPipeline:
    def __init__(self, config: dict):
        """Initialize pipeline with config."""
        self.config = config
        self.sampler = RepositorySampler(...)
        self.t0_detector = T0Detector(...)
        self.cloner = RepositoryCloner(...)
        self.coder = DCSCoder(...)
        self.analyzer = StatisticalAnalyzer(...)
        self.visualizer = Visualizer(...)

    def run_sampling_phase(self) -> pd.DataFrame:
        """Phase 1: Sampling. Returns: sampled_df [120, 4]"""
        ...

    def run_t0_detection_phase(self, sample_df: pd.DataFrame) -> pd.DataFrame:
        """Phase 2: T0 Detection. sample_df -> t0_df [120, 6]"""
        ...

    def run_cloning_phase(self, t0_df: pd.DataFrame) -> pd.DataFrame:
        """Phase 3: Cloning. t0_df -> cloned_df [100, 7]"""
        ...

    def run_manual_coding_phase(self) -> str:
        """Phase 4: Generate template. Returns: template_path"""
        ...

    def run_analysis_phase(
        self, 
        coding_df: pd.DataFrame, 
        dual_coded_df: pd.DataFrame
    ) -> Dict:
        """Phase 5: Statistical analysis. Returns: results_dict"""
        ...

    def run_full_pipeline(self) -> Dict:
        """Execute all phases. Returns: final_results"""
        ...
```

---

## E-6: Quality Validation (Complexity: 9, Budget: 0)

Standard testing, no logic subtasks needed.

### API Signatures

```python
# tests/test_t0_detection.py
def test_tier1_release_tags():
    """Test tier1 with mock release tags."""
    ...

def test_tier2_dataset_commits():
    """Test tier2 with mock commit messages."""
    ...

def test_tier3_fallback():
    """Test tier3 always succeeds."""
    ...

def test_three_tier_fallback_order():
    """Test tier preference: 1 > 2 > 3."""
    ...

# tests/test_statistics.py
def test_wilson_ci_calculation():
    """Test Wilson score CI against known values."""
    ...

def test_chi2_component_breakdown():
    """Test chi-square with synthetic data."""
    ...

def test_gate_criteria_validation():
    """Test gate pass/fail logic."""
    ...
```

---

## Data Structures

### CSV Schemas

**sampled_repositories.csv**
```
repo_id: str
created_at: datetime
likes: int
sample_year: int
```

**t0_detection_results.csv**
```
repo_id: str
t0: datetime
t0_method: str (tier1|tier2|tier3)
commit_sha: str
t0_success: bool
clone_success: bool
commit_sha_t0_plus_90: str
```

**dcs_coding_results.csv**
```
repo_id: str
dcs_data_context: float (0.0|0.5|1.0)
dcs_preprocessing: float (0.0|0.5|1.0)
dcs_licensing: float (0.0|0.5|1.0)
dcs_3_total: float (0.0-3.0)
compliant: bool (>= 2.4)
```

**dcs_dual_coded_sample.csv**
```
repo_id: str
coder: str (coder1|coder2)
dcs_data_context: float
dcs_preprocessing: float
dcs_licensing: float
dcs_3_total: float
compliant: bool
```

---

## Configuration Structure

```python
# src/config.py
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class StudyConfig:
    # Sampling Configuration
    sampling: Dict = field(default_factory=lambda: {
        "start_date": "2022-01-01",
        "end_date": "2024-12-31",
        "min_stars": 10,
        "sample_size": 120,
        "n_per_year": 40,
        "random_seed": 42
    })
    
    # T0 Detection Configuration
    t0_detection: Dict = field(default_factory=lambda: {
        "dataset_commit_patterns": [
            "add dataset", 
            "upload data", 
            "initial commit",
            "first release"
        ],
        "max_retries": 3,
        "backoff_base": 2
    })
    
    # Cloning Configuration
    cloning: Dict = field(default_factory=lambda: {
        "base_dir": "./data/repos",
        "t0_offset_days": 90,
        "verify_readme": True
    })
    
    # DCS Coding Configuration
    dcs_coding: Dict = field(default_factory=lambda: {
        "threshold": 2.4,
        "components": ["data_context", "preprocessing", "licensing"],
        "dual_code_percentage": 0.20
    })
    
    # Statistical Configuration
    statistical: Dict = field(default_factory=lambda: {
        "alpha": 0.05,
        "ci_method": "wilson",
        "h0_threshold": 0.70,
        "h1_prediction": 0.40,
        "gate_threshold": 0.60,
        "irr_threshold": 0.70
    })
```

---

## Critical Implementation Notes

### API Authentication

```python
# Environment variables required
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Required
HF_TOKEN = os.getenv("HF_TOKEN")  # Optional for public datasets

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable required")
```

### Rate Limit Handling

```python
def _check_rate_limit(self) -> Tuple[int, int]:
    """Check GitHub API rate limit. Returns: (remaining, reset_time)"""
    rate_limit = self.github.get_rate_limit()
    core = rate_limit.core
    return (core.remaining, core.reset.timestamp())

def _wait_for_rate_limit_reset(self, reset_time: int) -> None:
    """Sleep until rate limit resets."""
    wait_seconds = max(0, reset_time - time.time())
    if wait_seconds > 0:
        print(f"Rate limit hit. Waiting {wait_seconds:.0f}s...")
        time.sleep(wait_seconds + 5)  # +5s buffer
```

### Repository ID Format

```python
# HuggingFace repo_id format: "username/repo-name"
# GitHub repo full_name format: "username/repo-name"
# Conversion needed if HF uses different format

def convert_hf_to_github(repo_id: str) -> str:
    """Convert HF repo_id to GitHub full_name."""
    if repo_id.startswith("datasets/"):
        return repo_id  # HuggingFace official datasets
    return repo_id  # User datasets (same format)
```

---

## Error Handling Strategy

### T0 Detection Failure (Target: ≤5%)

```python
try:
    t0, commit_sha, tier = detector.detect_t0_three_tier(repo_id)
    success = True
except Exception as e:
    logger.error(f"T0 detection failed for {repo_id}: {e}")
    t0, commit_sha, tier = None, None, None
    success = False

# Log to CSV for analysis
results.append({
    "repo_id": repo_id,
    "t0": t0,
    "t0_method": tier,
    "commit_sha": commit_sha,
    "t0_success": success
})
```

### Cloning Failure (Target: ≤2%)

```python
try:
    local_path = cloner.clone_at_revision(repo_id, commit_sha)
    clone_success = cloner.verify_clone(local_path)
except Exception as e:
    logger.error(f"Clone failed for {repo_id}: {e}")
    clone_success = False
```

---

## Validation Checkpoints

### Pre-Analysis Validation

```python
def validate_pipeline_outputs(self) -> Dict[str, bool]:
    """Validate intermediate outputs before proceeding."""
    checks = {
        "sampling_complete": len(sampled_df) == 120,
        "t0_success_rate": (t0_df["t0_success"].sum() / len(t0_df)) >= 0.95,
        "clone_success_rate": (t0_df["clone_success"].sum() / len(t0_df)) >= 0.98,
        "coding_complete": len(coding_df) == len(t0_df[t0_df["clone_success"]]),
        "dual_coding_complete": len(dual_coded_df) == int(len(coding_df) * 0.20) * 2
    }
    return checks
```

---

## Logic Design Validation

### Self-Validation Checklist

- [x] No ASCII diagrams (text descriptions only)
- [x] No KB search logs (only "Applied: X" at top)
- [x] No Serena logs (concise Codebase Analysis section)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes replaced with data structure tables
- [x] Pseudo-code only for complex algorithms (T0 fallback, retry logic)
- [x] API signatures copy-paste ready with type hints
- [x] Subtask count within budget (3/3 for E-1)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included

### Budget Allocation

| Epic | Complexity | Subtasks Allocated | Subtasks Used |
|------|------------|-------------------|---------------|
| E-1 | 15 (High) | 3 | 3 |
| E-2 | 9 (Medium) | 0 | 0 |
| E-3 | 12 (Medium) | 0 | 0 |
| E-4 | 8 (Low) | 0 | 0 |
| E-5 | 11 (Medium) | 0 | 0 |
| E-6 | 9 (Medium) | 0 | 0 |
| **Total** | **64** | **3** | **3** |

---

**Document Version:** 1.0  
**Next Phase:** Phase 4 - Implementation (Coder Agent)  
**Subtasks Created:** 3 (L-1-1, L-1-2, L-1-3)  
**Gate Status:** MUST_WORK gate pending (validation in Phase 4)
