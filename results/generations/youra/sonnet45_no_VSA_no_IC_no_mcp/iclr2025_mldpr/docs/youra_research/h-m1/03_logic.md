# Logic Specification: H-M1
# Health Metrics Deprecation Detection

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** MECHANISM  
**Budget:** 8 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-e1 actual code  
**Analyzed Path:** h-e1/code/src/  
**Relevant Symbols:** TelemetryLogger, Visualizer (reusable for API telemetry and plotting)

---

## Applied Patterns

**Applied:** REST client pattern (stdlib requests), SQLite cache pattern, metric computation pattern (numpy linear algebra), sklearn validation harness

---

## M-1: API Clients [Complexity: 12, Budget: 3]

### API Signatures

```python
# src/clients.py
from typing import List, Dict, Optional
import requests
from pathlib import Path
import json
import time

class HuggingFaceClient:
    def __init__(self, cache_dir: str = ".cache/hf"):
        """Initialize with file-based cache."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_download_history(self, dataset_id: str, days: int = 180) -> List[int]:
        """
        Query HF API for daily downloads.
        
        Args:
            dataset_id: Dataset identifier
            days: History window (default 180)
        
        Returns:
            Daily download counts [d1, d2, ..., d_days]
        """
        ...
    
    def list_active_datasets(self, limit: int = 1000) -> List[str]:
        """Query HF Hub for active dataset IDs."""
        ...
    
    def _cache_key(self, dataset_id: str, endpoint: str) -> Path:
        """Generate cache file path: {cache_dir}/{dataset_id}_{endpoint}.json"""
        ...

class PapersWithCodeClient:
    def __init__(self, cache_dir: str = ".cache/pwc"):
        """Initialize with file-based cache."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_citation_graph(self, dataset_id: str) -> List[str]:
        """
        Query PWC API for successors.
        
        Returns:
            List of successor dataset IDs
        """
        ...

class GitHubClient:
    def __init__(self, token: Optional[str] = None, cache_dir: str = ".cache/gh"):
        """Initialize with optional PAT for rate limit."""
        self.token = token
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_issues(self, repo: str) -> List[Dict[str, str]]:
        """
        Query GitHub API for issues.
        
        Returns:
            [{state: "open"|"closed", title: str, created_at: str}]
        """
        ...
    
    def _retry_with_backoff(self, url: str, max_retries: int = 3) -> requests.Response:
        """Exponential backoff: 1s, 2s, 4s."""
        ...
```

### Pseudo-code

```
# HuggingFaceClient.get_download_history()
1. cache_path = _cache_key(dataset_id, "downloads")
2. if cache_path.exists():
3.   return json.load(cache_path)
4. 
5. response = requests.get(f"https://huggingface.co/api/datasets/{dataset_id}/downloads")
6. downloads = response.json()['daily'][-days:]
7. json.dump(downloads, cache_path)
8. return downloads

# GitHubClient._retry_with_backoff()
1. for attempt in range(max_retries):
2.   response = requests.get(url, headers={'Authorization': f'token {token}'})
3.   if response.status_code == 200:
4.     return response
5.   elif response.status_code == 429:  # Rate limit
6.     sleep(2 ** attempt)
7.   else:
8.     raise Exception(f"HTTP {response.status_code}")
9. raise Exception("Max retries exceeded")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HuggingFaceClient | requests.get() + JSON cache + list_active_datasets() |
| L-1-2 | PapersWithCodeClient | Citation graph endpoint + cache |
| L-1-3 | GitHubClient + retry logic | Issues endpoint + exponential backoff (time.sleep) |

---

## M-2: Metrics Computation [Complexity: 9, Budget: 2]

### API Signatures

```python
# src/metrics.py
import numpy as np
from typing import Dict, List

class HealthMetricsComputer:
    def __init__(
        self,
        velocity_threshold: float = 0.3,
        emergence_threshold: int = 3,
        issue_threshold: float = 0.6
    ):
        """Initialize thresholds."""
        self.velocity_threshold = velocity_threshold
        self.emergence_threshold = emergence_threshold
        self.issue_threshold = issue_threshold
    
    def compute_usage_velocity(self, download_history: List[int]) -> float:
        """
        Linear regression slope.
        
        Args:
            download_history: Daily download counts
        
        Returns:
            Slope (negative = declining)
        """
        ...
    
    def compute_successor_emergence(self, successors: List[str]) -> int:
        """Count of successors."""
        return len(successors)
    
    def compute_issue_ratio(self, issues: List[Dict]) -> float:
        """open_issues / total_issues (0.0 if no issues)."""
        ...
    
    def flag_deprecation_candidate(self, metrics: Dict[str, float]) -> bool:
        """
        Apply thresholds.
        
        Returns:
            True if velocity < threshold AND emergence > threshold AND issue_ratio > threshold
        """
        ...
    
    def compute_all_metrics(
        self,
        download_history: List[int],
        successors: List[str],
        issues: List[Dict]
    ) -> Dict[str, float]:
        """
        Compute all metrics.
        
        Returns:
            {velocity: float, emergence: int, issue_ratio: float, flagged: bool}
        """
        ...
```

### Pseudo-code

```
# compute_usage_velocity()
1. timestamps = np.arange(len(download_history))
2. slope, intercept = np.polyfit(timestamps, download_history, deg=1)
3. return slope

# compute_issue_ratio()
1. if len(issues) == 0:
2.   return 0.0
3. open_count = sum(1 for i in issues if i['state'] == 'open')
4. return open_count / len(issues)

# flag_deprecation_candidate()
1. return (metrics['velocity'] < velocity_threshold and
           metrics['emergence'] > emergence_threshold and
           metrics['issue_ratio'] > issue_threshold)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Metric computation | np.polyfit() + len() + division |
| L-2-2 | Flagging logic | AND logic for 3 thresholds |

---

## M-3: Data Collection [Complexity: 11, Budget: 2]

### API Signatures

```python
# src/collector.py
from typing import List, Dict, Any
from pathlib import Path
from src.clients import HuggingFaceClient, PapersWithCodeClient, GitHubClient
import json

class DataCollector:
    def __init__(
        self,
        hf_client: HuggingFaceClient,
        pwc_client: PapersWithCodeClient,
        gh_client: GitHubClient,
        output_dir: Path
    ):
        """Initialize with API clients."""
        self.hf = hf_client
        self.pwc = pwc_client
        self.gh = gh_client
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_dataset_data(self, dataset_id: str, repo: str) -> Dict[str, Any]:
        """
        Collect all data for one dataset.
        
        Returns:
            {
                dataset_id: str,
                download_history: List[int],
                successors: List[str],
                issues: List[Dict],
                repo: str
            }
        """
        ...
    
    def collect_batch(
        self, 
        dataset_ids: List[str],
        repos: List[str]
    ) -> List[Dict[str, Any]]:
        """Collect data for multiple datasets with progress logging."""
        ...
    
    def save_collected_data(self, data: List[Dict], path: str) -> None:
        """Write JSON to path."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

# src/validator.py
from datetime import datetime
from typing import List, Dict
from src.clients import HuggingFaceClient

class GroundTruthTracker:
    def __init__(self, hf_client: HuggingFaceClient, output_dir: Path):
        """Initialize with HF client."""
        self.hf = hf_client
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def snapshot_dataset_status(self, dataset_ids: List[str]) -> Dict[str, str]:
        """
        Record current deprecation status.
        
        Returns:
            {dataset_id: "active"|"deprecated"}
        """
        ...
    
    def compute_deprecation_events(
        self,
        month0_snapshot: Dict[str, str],
        month6_snapshot: Dict[str, str]
    ) -> Dict[str, bool]:
        """
        Returns:
            {dataset_id: True if deprecated between snapshots else False}
        """
        ...
    
    def save_snapshot(self, snapshot: Dict[str, str], path: str) -> None:
        """Write JSON snapshot."""
        with open(path, 'w') as f:
            json.dump(snapshot, f, indent=2)
```

### Pseudo-code

```
# DataCollector.collect_batch()
1. results = []
2. for i, dataset_id in enumerate(dataset_ids):
3.   print(f"Collecting {i+1}/{len(dataset_ids)}: {dataset_id}")
4.   data = collect_dataset_data(dataset_id, repos[i])
5.   results.append(data)
6. return results

# GroundTruthTracker.compute_deprecation_events()
1. events = {}
2. for dataset_id in month0_snapshot.keys():
3.   was_active = month0_snapshot[dataset_id] == "active"
4.   is_deprecated = month6_snapshot[dataset_id] == "deprecated"
5.   events[dataset_id] = (was_active and is_deprecated)
6. return events
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | DataCollector | Loop over 3 API clients + progress logging |
| L-3-2 | GroundTruthTracker | HF status check + snapshot diff |

---

## M-4: Evaluation [Complexity: 14, Budget: 1]

### API Signatures

```python
# src/evaluator.py
from sklearn.metrics import precision_score, recall_score, confusion_matrix
from typing import Dict, Tuple, Any
import pandas as pd
import json

class HealthMetricsEvaluator:
    def __init__(self, metrics_csv: str, ground_truth_json: str):
        """Load metrics and ground truth."""
        self.metrics_df = pd.read_csv(metrics_csv)
        with open(ground_truth_json) as f:
            self.ground_truth = json.load(f)
    
    def compute_precision_recall(self) -> Tuple[float, float]:
        """
        Returns:
            (precision, recall)
        """
        ...
    
    def compute_confusion_matrix(self) -> Dict[str, int]:
        """
        Returns:
            {tp: int, fp: int, fn: int, tn: int}
        """
        ...
    
    def check_gate_metrics(self) -> Tuple[bool, bool]:
        """
        Returns:
            (precision_pass, recall_pass) against thresholds (60%, 80%)
        """
        ...
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Returns:
            {
                precision: float,
                recall: float,
                confusion_matrix: dict,
                precision_pass: bool,
                recall_pass: bool,
                gate_status: 'PASS'|'FAIL'
            }
        """
        ...
```

### Pseudo-code

```
# compute_precision_recall()
1. y_true = [ground_truth[ds] for ds in metrics_df['dataset_id']]
2. y_pred = metrics_df['flagged'].tolist()
3. precision = precision_score(y_true, y_pred)
4. recall = recall_score(y_true, y_pred)
5. return (precision, recall)

# check_gate_metrics()
1. precision, recall = compute_precision_recall()
2. precision_pass = precision >= 0.6
3. recall_pass = recall >= 0.8
4. return (precision_pass, recall_pass)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Evaluator | sklearn.metrics + gate checks + JSON report |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are available from h-e1. Not required for core metrics, but useful for telemetry integration:

```python
# From: h-e1/code/src/telemetry.py (ACTUAL CODE)
class TelemetryLogger:
    def __init__(self, db_path: str = "telemetry.db", opt_in: bool = True):
        """Initialize SQLite backend."""
        ...
    
    def log_event(self, event: Dict[str, Any]) -> bool:
        """
        Log event with hashed user ID.
        
        Args:
            event: {user_id, dataset, action, timestamp}
        
        Returns:
            Success status
        """
        ...
    
    def hash_user_id(self, user_id: str) -> str:
        """SHA256 hash truncated to 16 chars."""
        ...
    
    def get_capture_rate(self) -> float:
        """Calculate successful_logs / total_attempts."""
        ...

# From: h-e1/code/src/visualize.py (ACTUAL CODE)
class Visualizer:
    def __init__(self, figures_dir: Path):
        """Initialize output directory."""
        ...
    
    def plot_gate_metrics(self, report: Dict) -> None:
        """Bar chart: target vs actual."""
        ...
    
    def plot_load_time_comparison(self, df: pd.DataFrame) -> None:
        """Side-by-side bars: baseline vs instrumented."""
        ...
    
    def plot_overhead_distribution(self, df: pd.DataFrame) -> None:
        """Box plot of overhead across runs."""
        ...
    
    def plot_capture_rate(self, events: List[Dict]) -> None:
        """Cumulative capture rate over time."""
        ...
```

**Verified from**: h-e1/code/src/ (actual implementation)

**Usage**: Optional - can log API client telemetry using TelemetryLogger, reuse Visualizer for plotting patterns.

---

## Data Schemas

### Raw Data (JSON)

```json
{
  "dataset_id": "squad",
  "download_history": [120, 118, 115, ...],
  "successors": ["squad_v2", "squad_adversarial"],
  "issues": [
    {"state": "open", "title": "Bug in tokenization", "created_at": "2026-01-15"}
  ],
  "repo": "huggingface/squad"
}
```

### Health Metrics (CSV)

| Column | Type | Description |
|--------|------|-------------|
| dataset_id | str | Dataset identifier |
| velocity | float | Download trend slope |
| emergence | int | Successor count |
| issue_ratio | float | open/total issues |
| flagged | bool | Deprecation candidate flag |

### Ground Truth (JSON)

```json
{
  "squad": true,
  "imagenet": false,
  "wikitext": true
}
```

---

## Validation Checklist

- [ ] All type hints present
- [ ] API clients implement retry logic
- [ ] Metrics handle empty lists (0.0 fallback)
- [ ] Evaluation computes TP/FP/FN/TN correctly
- [ ] Gate thresholds (60%, 80%) applied
- [ ] 8 subtasks allocated

---

**End of Logic Specification**
