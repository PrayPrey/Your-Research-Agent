# Logic Design: Repository Maintenance Classification (H-E1)

**Version:** 1.0  
**Date:** 2026-07-13  
**Hypothesis:** H-E1 (EXISTENCE)  
**Budget:** 4 subtasks (Medium complexity: A-2, A-3 priority)

**Applied:** Standard sklearn API patterns

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## A-2: Data Collection [Complexity: 12, Budget: 4]

**Applied:** GitHub REST API v3 + Papers with Code API integration pattern

### API Signatures

```python
import requests
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class GitHubDataCollector:
    def __init__(self, api_token: str):
        """Initialize GitHub API client with authentication."""
        ...

    def collect_pwc_repos(
        self, 
        year_range: Tuple[int, int], 
        min_stars: int, 
        max_repos: int
    ) -> pd.DataFrame:
        """Query Papers with Code API for benchmark repositories.
        
        Returns: DataFrame with columns [repo_name, repo_url, stars, description]
        """
        ...

    def fetch_repo_metadata(self, repo_full_name: str) -> Dict:
        """Extract metadata from GitHub API for single repository.
        
        Args:
            repo_full_name: Repository name (e.g., 'owner/repo')
        
        Returns:
            Dict with keys: stars, forks, contributors, total_commits, 
            open_issues, last_commit_date, closed_issues, total_issues
        """
        ...

    def compute_temporal_features(self, repo_full_name: str) -> Dict:
        """Compute commit frequency and issue resolution rate.
        
        Returns:
            Dict with keys: commit_frequency_median_weekly, issue_resolution_rate
        """
        ...

    def save_raw_data(self, data: pd.DataFrame, output_path: str) -> None:
        """Save collected metadata to CSV."""
        ...

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Implement exponential backoff for API rate limiting."""
        ...
```

### Data Schema

| Column | Type | Description |
|--------|------|-------------|
| repo_id | str | Repository full name |
| stars | int | GitHub stars count |
| forks | int | Fork count |
| contributors | int | Contributor count |
| total_commits | int | Lifetime commit count |
| open_issues | int | Current open issues |
| closed_issues | int | Total closed issues |
| total_issues | int | Total issues (open + closed) |
| last_commit_date | datetime | Most recent commit timestamp |
| commit_frequency_median_weekly | float | Median weekly commits |
| issue_resolution_rate | float | closed_issues / total_issues |

### Pseudo-code

```
1. Query Papers with Code API:
   - Filter: year_range=(2020, 2024), min_stars=32
   - Extract: repo_name, repo_url
   - Limit: max_repos=2000

2. For each repository:
   - Call GitHub API: /repos/{owner}/{repo}
     → Extract: stars, forks, open_issues
   - Call GitHub API: /repos/{owner}/{repo}/contributors
     → Count: contributors
   - Call GitHub API: /repos/{owner}/{repo}/commits
     → Compute: total_commits, commit_frequency_median_weekly
   - Call GitHub API: /repos/{owner}/{repo}/issues?state=all
     → Compute: total_issues, closed_issues, issue_resolution_rate
   - Parse: last_commit_date from /repos/{owner}/{repo}/commits?per_page=1

3. Cache response to avoid re-fetching on retry
4. Handle rate limit: exponential backoff (1s, 2s, 4s, 8s)
5. Save to data/raw_metadata.csv
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Papers with Code integration | Query API for benchmark repos |
| L-2-2 | GitHub metadata extraction | Fetch basic repo metadata |
| L-2-3 | Temporal feature computation | Calculate commit frequency, issue resolution rate |
| L-2-4 | Rate limiting & caching | Implement retry logic and local cache |

---

## A-3: Feature Engineering [Complexity: 10, Budget: 4]

**Applied:** Log1p transformation pattern for long-tail distributions

### API Signatures

```python
import numpy as np
import pandas as pd
from typing import Tuple

class FeatureEngineer:
    def __init__(self):
        """Initialize feature engineering pipeline."""
        ...

    def transform_features(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Apply log1p transforms to long-tail features.
        
        Args:
            raw_data: DataFrame with raw GitHub metadata
        
        Returns:
            DataFrame with 8 engineered features:
            [stars_log, forks_log, contributors_log, total_commits_log, 
             open_issues_log, days_since_last_commit, 
             commit_frequency_median_weekly, issue_resolution_rate]
        """
        ...

    def create_labels(
        self, 
        raw_data: pd.DataFrame, 
        threshold_days: int = 180
    ) -> np.ndarray:
        """Generate binary maintenance labels.
        
        Args:
            raw_data: DataFrame with last_commit_date column
            threshold_days: Threshold for maintained vs abandoned
        
        Returns:
            Binary labels: 1 = maintained, 0 = abandoned (shape: [N])
        """
        ...

    def validate_distributions(self, features: pd.DataFrame) -> Dict:
        """Validate feature distributions are approximately normal.
        
        Returns:
            Dict with keys: feature_name -> {mean, std, skewness}
        """
        ...

    def _compute_days_since_last_commit(
        self, 
        last_commit_dates: pd.Series
    ) -> pd.Series:
        """Compute days elapsed since last commit."""
        ...
```

### Feature Transformations

| Input Feature | Transformation | Output Feature | Shape |
|---------------|----------------|----------------|-------|
| stars | log1p(x) | stars_log | [N] |
| forks | log1p(x) | forks_log | [N] |
| contributors | log1p(x) | contributors_log | [N] |
| total_commits | log1p(x) | total_commits_log | [N] |
| open_issues | log1p(x) | open_issues_log | [N] |
| last_commit_date | datetime.now() - x (in days) | days_since_last_commit | [N] |
| commit_frequency_median_weekly | identity | commit_frequency_median_weekly | [N] |
| issue_resolution_rate | identity | issue_resolution_rate | [N] |

### Pseudo-code

```
1. Load raw_data from CSV (shape: [N, M])

2. Apply log1p transforms:
   features['stars_log'] = log1p(raw['stars'])  # [N]
   features['forks_log'] = log1p(raw['forks'])  # [N]
   features['contributors_log'] = log1p(raw['contributors'])  # [N]
   features['total_commits_log'] = log1p(raw['total_commits'])  # [N]
   features['open_issues_log'] = log1p(raw['open_issues'])  # [N]

3. Compute temporal features:
   now = datetime.now()
   features['days_since_last_commit'] = (now - raw['last_commit_date']).days  # [N]

4. Copy derived features as-is:
   features['commit_frequency_median_weekly'] = raw['commit_frequency_median_weekly']  # [N]
   features['issue_resolution_rate'] = raw['issue_resolution_rate']  # [N]

5. Create labels:
   labels = (features['days_since_last_commit'] < 180).astype(int)  # [N]

6. Validate distributions:
   for each feature:
     - compute mean, std, skewness
     - warn if |skewness| > 2 (non-normal)

7. Return: features (shape: [N, 8]), labels (shape: [N])
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Log1p transforms | Apply log1p to 5 long-tail features |
| L-3-2 | Temporal feature derivation | Compute days_since_last_commit |
| L-3-3 | Label generation | Create binary labels with 180-day threshold |
| L-3-4 | Distribution validation | Check for normality and outliers |

---

## Summary

### Complexity Budget Usage

| Task | Allocated | Used | Remaining |
|------|-----------|------|-----------|
| A-2: Data Collection | 4 | 4 | 0 |
| A-3: Feature Engineering | 4 | 4 | 0 |
| **Total** | **4** | **4** | **0** |

### Key Design Decisions

1. **Data Collection Strategy**: Papers with Code API for initial repository list, then GitHub API for detailed metadata extraction
2. **Feature Engineering**: Log1p transformation for long-tail features (stars, forks, commits) + derived temporal features
3. **Label Generation**: Binary classification using 180-day threshold (maintained if last_commit < 180 days ago)
4. **Rate Limiting**: Exponential backoff retry logic for GitHub API (5000 req/hr limit)

### Integration Points

```python
# End-to-end pipeline (run_experiment.py)
from src.data_collector import GitHubDataCollector
from src.feature_engineer import FeatureEngineer

# 1. Collect data
collector = GitHubDataCollector(api_token=config.github_api_token)
raw_data = collector.collect_pwc_repos(
    year_range=(2020, 2024),
    min_stars=32,
    max_repos=2000
)
collector.save_raw_data(raw_data, "data/raw_metadata.csv")

# 2. Engineer features
engineer = FeatureEngineer()
X = engineer.transform_features(raw_data)  # [2000, 8]
y = engineer.create_labels(raw_data, threshold_days=180)  # [2000]

# 3. Train model (handled by A-4)
# 4. Evaluate (handled by A-5)
# 5. Visualize (handled by A-6)
```

### Type Hints Convention

All APIs use Python type hints:
- `pd.DataFrame`: Pandas DataFrame
- `np.ndarray`: NumPy array
- `Dict`, `List`, `Tuple`, `Optional`: Standard typing module
- `datetime`: Standard library datetime

### Error Handling

Critical error cases:
- **GitHub API rate limit exceeded**: Exponential backoff retry (up to 5 attempts)
- **Missing metadata fields**: Skip repository, log warning
- **Invalid date parsing**: Set days_since_last_commit to NaN, filter during training
- **Zero total_issues**: Use issue_resolution_rate = 0.0 (handle division by zero)

---

**End of Logic Design Document**
