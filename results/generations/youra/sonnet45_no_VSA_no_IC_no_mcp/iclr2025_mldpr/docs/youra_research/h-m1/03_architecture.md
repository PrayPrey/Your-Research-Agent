# System Architecture: H-M1
# Health Metrics Deprecation Detection

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** MECHANISM  
**Applied:** API client pattern, metric computation pattern, validation harness pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from base code  
**Analyzed Path:** h-e1/code/  
**Findings:** Reusing telemetry backend, benchmark harness, and visualization infrastructure from h-e1. Adding API clients and health metric computation modules.

---

## System Overview

Health metrics computation system that predicts dataset deprecation candidates by analyzing usage velocity, successor emergence, and issue ratio. Extends h-e1 validated telemetry infrastructure with API clients and metric computation logic. Six core modules: API clients, metrics computer, data collector, evaluator, visualizer, orchestrator.

---

## Module Architecture

### 1. API Clients (`src/clients.py`)

**Dependencies:** stdlib `requests`, `json`, `time`

```python
from typing import List, Dict, Optional
import requests

class HuggingFaceClient:
    def __init__(self, cache_dir: str = ".cache/hf"): ...
    
    def get_download_history(self, dataset_id: str, days: int = 180) -> List[int]:
        """
        Returns:
            Daily download counts [d1, d2, ..., d180]
        """
        ...

class PapersWithCodeClient:
    def __init__(self, cache_dir: str = ".cache/pwc"): ...
    
    def get_citation_graph(self, dataset_id: str) -> List[str]:
        """
        Returns:
            List of successor dataset IDs citing this as predecessor
        """
        ...

class GitHubClient:
    def __init__(self, token: Optional[str] = None, cache_dir: str = ".cache/gh"): ...
    
    def get_issues(self, repo: str) -> List[Dict[str, str]]:
        """
        Returns:
            [{state: "open"|"closed", title: str, created_at: str}]
        """
        ...
```

### 2. Health Metrics Computer (`src/metrics.py`)

**Dependencies:** stdlib `numpy`

```python
import numpy as np
from typing import Dict

class HealthMetricsComputer:
    def __init__(
        self,
        velocity_threshold: float = 0.3,
        emergence_threshold: int = 3,
        issue_threshold: float = 0.6
    ): ...
    
    def compute_usage_velocity(self, download_history: List[int]) -> float:
        """Linear regression slope on download history"""
        ...
    
    def compute_successor_emergence(self, successors: List[str]) -> int:
        """Count of successor datasets"""
        ...
    
    def compute_issue_ratio(self, issues: List[Dict]) -> float:
        """open_issues / total_issues"""
        ...
    
    def flag_deprecation_candidate(self, metrics: Dict[str, float]) -> bool:
        """
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
        Returns:
            {velocity: float, emergence: int, issue_ratio: float, flagged: bool}
        """
        ...
```

### 3. Data Collector (`src/collector.py`)

**Dependencies:** API clients, stdlib `json`, `pathlib`

```python
from typing import List, Dict
from pathlib import Path

class DataCollector:
    def __init__(
        self,
        hf_client: HuggingFaceClient,
        pwc_client: PapersWithCodeClient,
        gh_client: GitHubClient,
        output_dir: Path
    ): ...
    
    def collect_dataset_data(self, dataset_id: str) -> Dict[str, Any]:
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
    
    def collect_batch(self, dataset_ids: List[str]) -> List[Dict[str, Any]]:
        """Collect data for multiple datasets with progress logging"""
        ...
    
    def save_collected_data(self, data: List[Dict], path: str) -> None:
        """Write JSON to path"""
        ...
```

### 4. Ground Truth Tracker (`src/validator.py`)

**Dependencies:** HuggingFaceClient, stdlib `json`, `datetime`

```python
from datetime import datetime
from typing import List, Dict

class GroundTruthTracker:
    def __init__(self, hf_client: HuggingFaceClient, output_dir: Path): ...
    
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
        """Write JSON snapshot"""
        ...
```

### 5. Evaluator (`src/evaluator.py`)

**Dependencies:** sklearn, metrics data, ground truth

```python
from sklearn.metrics import precision_score, recall_score, confusion_matrix
from typing import Dict, Tuple
import pandas as pd

class HealthMetricsEvaluator:
    def __init__(self, metrics_csv: str, ground_truth_json: str): ...
    
    def compute_precision_recall(self) -> Tuple[float, float]:
        """
        Returns:
            (precision, recall) against ground truth deprecations
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

### 6. Visualization (`src/visualize.py`)

**Dependencies:** matplotlib, pandas, evaluation report

```python
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd

class HealthMetricsVisualizer:
    def __init__(self, figures_dir: Path): ...
    
    def plot_gate_metrics(self, report: Dict) -> None:
        """Bar chart: precision/recall (target vs actual)"""
        ...
    
    def plot_health_metrics_distribution(self, metrics_df: pd.DataFrame) -> None:
        """Scatter: velocity vs emergence, color by issue_ratio"""
        ...
    
    def plot_confusion_matrix(self, cm: Dict[str, int]) -> None:
        """Heatmap: TP, FP, FN, TN"""
        ...
    
    def plot_threshold_sensitivity(self, metrics_df: pd.DataFrame, ground_truth: Dict) -> None:
        """Precision/recall curves as thresholds vary"""
        ...
    
    def plot_deprecation_timeline(self, ground_truth: Dict) -> None:
        """Cumulative deprecation events over 6 months"""
        ...
```

### 7. Configuration (`src/config.py`)

**Dependencies:** None

```python
HEALTH_METRICS_CONFIG = {
    "api": {
        "hf_cache_dir": ".cache/hf",
        "pwc_cache_dir": ".cache/pwc",
        "gh_cache_dir": ".cache/gh",
        "rate_limit_delay": 1.0
    },
    "metrics": {
        "velocity_threshold": 0.3,
        "emergence_threshold": 3,
        "issue_threshold": 0.6,
        "top_k_candidates": 30
    },
    "data": {
        "observation_months": 6,
        "download_history_days": 180,
        "output_dir": "data"
    },
    "evaluation": {
        "precision_target": 0.6,
        "recall_target": 0.8
    },
    "visualization": {
        "figures_dir": "figures"
    }
}
```

### 8. Main Entry Point (`main.py`)

**Dependencies:** All modules above

```python
from pathlib import Path
from datetime import datetime
import json
from src.clients import HuggingFaceClient, PapersWithCodeClient, GitHubClient
from src.metrics import HealthMetricsComputer
from src.collector import DataCollector
from src.validator import GroundTruthTracker
from src.evaluator import HealthMetricsEvaluator
from src.visualize import HealthMetricsVisualizer
from src.config import HEALTH_METRICS_CONFIG
import pandas as pd

def main():
    """Run full health metrics validation pipeline"""
    base_dir = Path(__file__).parent
    
    # 1. Setup API clients
    hf = HuggingFaceClient(HEALTH_METRICS_CONFIG["api"]["hf_cache_dir"])
    pwc = PapersWithCodeClient(HEALTH_METRICS_CONFIG["api"]["pwc_cache_dir"])
    gh = GitHubClient(cache_dir=HEALTH_METRICS_CONFIG["api"]["gh_cache_dir"])
    
    # 2. Get dataset list
    dataset_ids = hf.list_active_datasets()[:1000]  # Sample for PoC
    
    # 3. Month 0 snapshot
    tracker = GroundTruthTracker(hf, base_dir / HEALTH_METRICS_CONFIG["data"]["output_dir"])
    month0_snapshot = tracker.snapshot_dataset_status(dataset_ids)
    tracker.save_snapshot(month0_snapshot, str(base_dir / "data/month0_snapshot.json"))
    
    # 4. Collect data
    collector = DataCollector(hf, pwc, gh, base_dir / HEALTH_METRICS_CONFIG["data"]["output_dir"])
    raw_data = collector.collect_batch(dataset_ids)
    collector.save_collected_data(raw_data, str(base_dir / "data/raw_data.json"))
    
    # 5. Compute metrics
    computer = HealthMetricsComputer(
        velocity_threshold=HEALTH_METRICS_CONFIG["metrics"]["velocity_threshold"],
        emergence_threshold=HEALTH_METRICS_CONFIG["metrics"]["emergence_threshold"],
        issue_threshold=HEALTH_METRICS_CONFIG["metrics"]["issue_threshold"]
    )
    
    metrics_list = []
    for item in raw_data:
        metrics = computer.compute_all_metrics(
            item["download_history"],
            item["successors"],
            item["issues"]
        )
        metrics["dataset_id"] = item["dataset_id"]
        metrics_list.append(metrics)
    
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv(base_dir / "data/health_metrics.csv", index=False)
    
    # 6. Flag top K candidates
    flagged = metrics_df.nlargest(
        HEALTH_METRICS_CONFIG["metrics"]["top_k_candidates"],
        "flagged"
    )
    print(f"Flagged {len(flagged)} deprecation candidates")
    
    # 7. Month 6 snapshot (simulated for PoC - in real deployment, wait 6 months)
    print("NOTE: In production, wait 6 months for ground truth. Using simulated data for PoC.")
    month6_snapshot = tracker.snapshot_dataset_status(dataset_ids)
    tracker.save_snapshot(month6_snapshot, str(base_dir / "data/month6_snapshot.json"))
    
    # 8. Compute ground truth
    ground_truth = tracker.compute_deprecation_events(month0_snapshot, month6_snapshot)
    with open(base_dir / "data/ground_truth.json", 'w') as f:
        json.dump(ground_truth, f, indent=2)
    
    # 9. Evaluate
    evaluator = HealthMetricsEvaluator(
        str(base_dir / "data/health_metrics.csv"),
        str(base_dir / "data/ground_truth.json")
    )
    report = evaluator.generate_report()
    
    # 10. Visualize
    viz = HealthMetricsVisualizer(base_dir / HEALTH_METRICS_CONFIG["visualization"]["figures_dir"])
    viz.plot_gate_metrics(report)
    viz.plot_health_metrics_distribution(metrics_df)
    viz.plot_confusion_matrix(report["confusion_matrix"])
    viz.plot_threshold_sensitivity(metrics_df, ground_truth)
    viz.plot_deprecation_timeline(ground_truth)
    
    # 11. Save report
    report_path = base_dir / "evaluation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nGate Status: {report['gate_status']}")
    print(f"  Precision: {report['precision']:.2f} (target: 0.60)")
    print(f"  Recall: {report['recall']:.2f} (target: 0.80)")
    print(f"\nReport: {report_path}")
    print("EXPERIMENT COMPLETE")

if __name__ == "__main__":
    main()
```

---

## File Structure

```
h-m1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── clients.py         # API clients (HF, PWC, GitHub)
│   │   ├── metrics.py         # Health metrics computation
│   │   ├── collector.py       # Data collection orchestration
│   │   ├── validator.py       # Ground truth tracking
│   │   ├── evaluator.py       # Precision/recall validation
│   │   ├── visualize.py       # Figure generation
│   │   └── config.py          # Configuration constants
│   ├── main.py                # Entry point
│   ├── requirements.txt       # numpy, sklearn, matplotlib, requests, pandas
│   └── README.md              # Setup/run instructions
├── data/
│   ├── raw_data.json          # Collected API responses
│   ├── health_metrics.csv     # Computed metrics per dataset
│   ├── month0_snapshot.json   # Initial deprecation status
│   ├── month6_snapshot.json   # Final deprecation status
│   └── ground_truth.json      # Actual deprecation events
├── figures/                   # Generated plots
│   ├── gate_metrics.png
│   ├── health_metrics_distribution.png
│   ├── confusion_matrix.png
│   ├── threshold_sensitivity.png
│   └── deprecation_timeline.png
└── evaluation_report.json     # Final metrics
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TelemetryLogger | `from src.telemetry import TelemetryLogger` | `h-e1/code/src/telemetry.py` |

**Verified from**: h-e1/code/ (actual implementation)

**Usage**: Optional integration for telemetry logging of API calls (not required for core metrics computation).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | API Clients | Implement HF/PWC/GitHub clients with caching + rate limit handling | 12 | 3+3+4+2 |
| M-2 | Metrics Computation | Implement velocity/emergence/ratio computation + flagging logic | 9 | 2+1+4+2 |
| M-3 | Data Collection | Implement collector + ground truth tracker with batch processing | 11 | 3+2+4+2 |
| M-4 | Evaluation Pipeline | Implement evaluator (sklearn metrics) + visualizer (5 plots) | 14 | 3+2+6+3 |
| M-5 | Integration | Wire main.py orchestration + config + error handling | 8 | 2+2+2+2 |
| M-6 | Validation | Generate test fixtures + verify precision/recall computation | 10 | 2+2+4+2 |

**Complexity Breakdown:** Module_Size + Dependencies + Algorithm + Integration (each 1-5)

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [M-4]
- Medium (9-13): [M-1, M-2, M-3, M-6]
- Low (4-8): [M-5]

**Total:** 6 Epic tasks (MECHANISM scope)

---

## Task Decomposition

### M-1: API Clients (Complexity: 12)

**Files:** `src/clients.py`

**Subtasks:**
1. HuggingFaceClient with download history endpoint
2. PapersWithCodeClient with citation graph endpoint
3. GitHubClient with issue tracking endpoint
4. File-based caching + rate limit exponential backoff

**Acceptance:**
- All 3 clients query real APIs without error
- Cache hits avoid redundant API calls
- Rate limit errors trigger retry with backoff

### M-2: Metrics Computation (Complexity: 9)

**Files:** `src/metrics.py`

**Subtasks:**
1. `compute_usage_velocity()` with numpy polyfit
2. `compute_successor_emergence()` counting successors
3. `compute_issue_ratio()` with zero-issue handling
4. `flag_deprecation_candidate()` combining thresholds

**Acceptance:**
- Velocity returns negative slope for declining usage
- Emergence counts citation graph successors correctly
- Issue ratio handles empty issue lists (return 0.0)
- Flagging logic applies all 3 thresholds (AND logic)

### M-3: Data Collection (Complexity: 11)

**Files:** `src/collector.py`, `src/validator.py`

**Subtasks:**
1. `DataCollector.collect_dataset_data()` querying all 3 APIs
2. `DataCollector.collect_batch()` with progress logging
3. `GroundTruthTracker.snapshot_dataset_status()` HF status check
4. JSON serialization for raw data + snapshots

**Acceptance:**
- Batch collection completes for 1000 datasets
- Raw data JSON contains all required fields
- Month 0 and Month 6 snapshots capture deprecation status
- Ground truth computation identifies status changes

### M-4: Evaluation Pipeline (Complexity: 14)

**Files:** `src/evaluator.py`, `src/visualize.py`

**Subtasks:**
1. `HealthMetricsEvaluator` with sklearn precision/recall
2. Confusion matrix computation (TP/FP/FN/TN)
3. 5 plot functions (gate metrics, distribution, confusion matrix, sensitivity, timeline)
4. Gate check logic (precision ≥60%, recall ≥80%)

**Acceptance:**
- Precision/recall computed against ground truth
- Confusion matrix sums to total dataset count
- All 5 figures saved to figures/ directory
- Gate status correctly reflects threshold checks

### M-5: Integration (Complexity: 8)

**Files:** `main.py`, `src/config.py`

**Subtasks:**
1. `main()` orchestration pipeline (10 steps)
2. `HEALTH_METRICS_CONFIG` with all parameters
3. Error handling for API failures
4. Progress logging for long-running operations

**Acceptance:**
- `main.py` completes full pipeline without error
- Config centralizes all magic numbers
- API failures logged but don't crash pipeline
- Progress printed to stdout at each step

### M-6: Validation (Complexity: 10)

**Files:** `tests/test_metrics.py`, `tests/test_evaluator.py`

**Subtasks:**
1. Generate synthetic download history fixtures
2. Generate synthetic citation graph + issues
3. Unit tests for metric computation edge cases
4. Integration test for precision/recall calculation

**Acceptance:**
- All unit tests pass
- Edge cases handled (empty history, zero issues, no successors)
- Precision/recall computation verified with hand-calculated fixture
- CI-ready test suite

---

## Data Flow

```
1. Data Collection Phase
   └─> DataCollector
       └─> HuggingFaceClient.get_download_history()
       └─> PapersWithCodeClient.get_citation_graph()
       └─> GitHubClient.get_issues()
       └─> JSON output (raw_data.json)

2. Metrics Computation Phase
   └─> HealthMetricsComputer
       └─> compute_usage_velocity() [polyfit on download history]
       └─> compute_successor_emergence() [count successors]
       └─> compute_issue_ratio() [open/total]
       └─> flag_deprecation_candidate() [combine thresholds]
       └─> CSV output (health_metrics.csv)

3. Ground Truth Phase
   └─> GroundTruthTracker
       └─> snapshot_dataset_status() [Month 0]
       └─> snapshot_dataset_status() [Month 6]
       └─> compute_deprecation_events() [diff snapshots]
       └─> JSON output (ground_truth.json)

4. Evaluation Phase
   └─> HealthMetricsEvaluator
       └─> compute_precision_recall() [sklearn]
       └─> compute_confusion_matrix()
       └─> check_gate_metrics()
       └─> JSON report

5. Visualization Phase
   └─> HealthMetricsVisualizer
       └─> plot_* functions [5 figures]
       └─> PNG outputs
```

---

## Success Criteria Mapping

| Gate Metric | Target | Implementation | Validation |
|-------------|--------|----------------|------------|
| Precision | ≥60% | `HealthMetricsComputer.flag_deprecation_candidate()` | `HealthMetricsEvaluator.compute_precision_recall()` |
| Recall | ≥80% | `HealthMetricsComputer` thresholds | `HealthMetricsEvaluator.check_gate_metrics()` |

---

## Dependencies

**External:**
- `requests` (API clients)
- `numpy` (linear regression for velocity)
- `sklearn` (precision/recall computation)
- `matplotlib` (visualization)
- `pandas` (CSV handling)
- Python 3.8+ stdlib: `json`, `time`, `pathlib`, `datetime`

**Internal (h-e1):**
- `TelemetryLogger` (optional, for API call telemetry)

---

## Performance Targets

| Operation | Target Time | Notes |
|-----------|-------------|-------|
| API query (cached) | <100ms | File cache hit |
| API query (uncached) | <5s | Network round-trip |
| Metrics computation | <1ms per dataset | Simple math operations |
| Batch collection (1000 datasets) | <30min | With rate limiting |

---

## Validation Checklist

- [ ] All 8 modules implement interface signatures
- [ ] `main.py` orchestrates 10-step pipeline
- [ ] API clients cache responses to disk
- [ ] Health metrics compute correctly on test fixtures
- [ ] Ground truth tracker captures status changes
- [ ] Precision/recall validated against hand-calculated example
- [ ] All 5 figures generated
- [ ] Gate check logic correctly applies thresholds (60%, 80%)
- [ ] Total implementation <800 LOC

---

**End of Architecture Specification**
