# Architecture Design: H-M4 CI Workflow Lifecycle Shift

**Hypothesis ID:** h-m4  
**Document Type:** Architecture  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

**Applied Patterns:** GitHub Actions workflow integration, timing measurement infrastructure, PR-level randomization

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Analyzed h-m3 actual implementation  
**Analyzed Path**: docs/youra_research/h-m3/code/  
**Findings**: CompositionValidator with device/dtype/layout checks, decorator-based validation pattern (@validate_composition), structured exception hierarchy (CompositionViolation -> DeviceConsistencyViolation/DtypeConsistencyViolation/LayoutConsistencyViolation)

---

## 1. System Overview

### 1.1 Architecture Principle
CI workflow infrastructure experiment measuring lifecycle shift when h-m3 composition contracts are deployed in GitHub Actions. Two experimental arms: CI-Only (baseline) vs. CI+Contracts (proposed). Data collection via GitHub Actions API to measure time-to-first-failure and failure stage distribution.

### 1.2 Core Components

```
code/
├── ci_integration/
│   ├── workflows/
│   │   ├── ci_only.yml          # Baseline GitHub Actions workflow
│   │   └── ci_contracts.yml     # Proposed workflow with contract step
│   ├── contract_step.py         # GitHub Action for contract validation
│   └── timing_logger.py         # Timestamp instrumentation
├── data_collection/
│   ├── github_api_client.py     # PyGithub wrapper for metrics
│   ├── corpus_analyzer.py       # Retrospective analysis (Dataset 1)
│   └── trial_manager.py         # PR randomization and tracking
├── analysis/
│   ├── metrics_calculator.py    # TTFF reduction, detection improvement
│   ├── stage_classifier.py      # Parse logs for failure stage
│   └── visualizer.py            # Required + additional figures
└── run_experiment.py            # Main orchestrator

External Dependency (from h-m3):
└── ../h-m3/code/composition_validator.py  # Reused contract validator
```

### 1.3 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| CI Platform | GitHub Actions | Workflow execution environment |
| Contract Validation | h-m3 composition_validator | Device/dtype/layout validation |
| API Client | PyGithub | Workflow run data collection |
| Data Storage | SQLite + JSON | Trial data persistence |
| Metrics | scipy.stats | Mann-Whitney U test |
| Visualization | matplotlib | Required gate metrics chart |

---

## 2. Module Specifications

### 2.1 CI Integration Layer

#### `ci_integration/contract_step.py`

**Dependencies**: composition_validator (from h-m3), torch

```python
import sys
import time
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m3" / "code"))
from composition_validator import validate_composition, CompositionViolation

class CIContractValidator:
    def __init__(self, config_path: str): ...
    def run_validation(self) -> int: ...
    def log_github_output(self, key: str, value: str) -> None: ...
    def format_error_for_ci(self, violation: CompositionViolation) -> str: ...

def main() -> int:
    """Entry point for GitHub Actions step."""
    ...
```

#### `ci_integration/timing_logger.py`

**Dependencies**: datetime, json

```python
from datetime import datetime, timezone
from typing import Dict, Optional
import json

class TimingLogger:
    def __init__(self, output_path: str): ...
    def log_workflow_start(self, run_id: str) -> None: ...
    def log_failure_detected(self, run_id: str, stage: str) -> None: ...
    def calculate_ttff(self, run_id: str) -> float: ...
    def export_to_github_outputs(self) -> None: ...
```

### 2.2 Data Collection Pipeline

#### `data_collection/github_api_client.py`

**Dependencies**: PyGithub, datetime

```python
from github import Github, Repository, WorkflowRun
from datetime import datetime
from typing import List, Dict, Optional

class GitHubMetricsCollector:
    def __init__(self, token: str): ...
    def get_workflow_run(self, repo: str, run_id: int) -> WorkflowRun: ...
    def get_job_timestamps(self, run: WorkflowRun) -> Dict[str, datetime]: ...
    def get_step_logs(self, run: WorkflowRun) -> List[str]: ...
    def calculate_ttff_from_run(self, run: WorkflowRun) -> float: ...
```

#### `data_collection/corpus_analyzer.py`

**Dependencies**: pandas, composition_validator

```python
import pandas as pd
from typing import List, Dict
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m3" / "code"))
from composition_validator import validate_composition

class CorpusAnalyzer:
    def __init__(self, corpus_path: str): ...
    def load_jiang_corpus(self) -> pd.DataFrame: ...
    def filter_contractable_defects(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def apply_contracts_to_defect(self, defect: Dict) -> Dict: ...
    def measure_baseline_shift(self) -> Dict[str, float]: ...
```

#### `data_collection/trial_manager.py`

**Dependencies**: sqlite3, random

```python
import sqlite3
import random
from typing import List, Dict, Optional
from enum import Enum

class Arm(Enum):
    CI_ONLY = "ci_only"
    CI_CONTRACTS = "ci_contracts"

class TrialManager:
    def __init__(self, db_path: str, seed: int = 42): ...
    def register_repository(self, repo_id: str, stars: int) -> None: ...
    def assign_pr_to_arm(self, repo_id: str, pr_number: int) -> Arm: ...
    def get_arm_assignment(self, repo_id: str, pr_number: int) -> Optional[Arm]: ...
    def record_workflow_result(self, pr_id: str, ttff: float, stage: str) -> None: ...
    def get_trial_summary(self) -> Dict: ...
```

### 2.3 Analysis & Evaluation

#### `analysis/stage_classifier.py`

**Dependencies**: re, typing

```python
import re
from typing import List, Optional

class StageClassifier:
    def __init__(self): ...
    def classify_from_logs(self, step_logs: List[str]) -> str: ...
    def is_environment_failure(self, log: str) -> bool: ...
    def is_training_failure(self, log: str) -> bool: ...
```

#### `analysis/metrics_calculator.py`

**Dependencies**: numpy, scipy.stats

```python
import numpy as np
from scipy import stats
from typing import List, Dict, Tuple

class MetricsCalculator:
    def calculate_median_ttff(self, ttff_list: List[float]) -> float: ...
    def calculate_ttff_reduction(self, ci_only: List[float], ci_contracts: List[float]) -> float: ...
    def mann_whitney_test(self, ci_only: List[float], ci_contracts: List[float]) -> Tuple[float, float]: ...
    def calculate_marginal_detection(self, ci_only_count: int, ci_contracts_count: int) -> float: ...
    def calculate_stage_distribution(self, results: List[Dict]) -> Dict[str, Dict[str, float]]: ...
```

#### `analysis/visualizer.py`

**Dependencies**: matplotlib, pandas

```python
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from typing import Dict, List

class ExperimentVisualizer:
    def __init__(self, output_dir: Path): ...
    def generate_gate_metrics_chart(self, ci_only_median: float, ci_contracts_median: float, threshold: float = -5.0) -> None: ...
    def generate_stage_distribution_chart(self, stage_data: Dict[str, Dict[str, float]]) -> None: ...
    def generate_ttff_distribution_chart(self, ci_only: List[float], ci_contracts: List[float]) -> None: ...
```

### 2.4 Experiment Orchestrator

#### `run_experiment.py`

**Dependencies**: all modules above

```python
import argparse
import json
from pathlib import Path
from typing import Dict
from data_collection.corpus_analyzer import CorpusAnalyzer
from data_collection.trial_manager import TrialManager
from data_collection.github_api_client import GitHubMetricsCollector
from analysis.metrics_calculator import MetricsCalculator
from analysis.visualizer import ExperimentVisualizer

class ExperimentOrchestrator:
    def __init__(self, config_path: str): ...
    def run_retrospective_analysis(self) -> Dict: ...
    def run_prospective_trial(self) -> Dict: ...
    def evaluate_gate_criteria(self, results: Dict) -> bool: ...
    def generate_report(self, results: Dict) -> None: ...

def main() -> int:
    """Execute full h-m4 experiment: retrospective + prospective."""
    ...
```

---

## 3. External Dependencies (Base Hypothesis)

### Module Paths (From h-m3 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| validate_composition | `from composition_validator import validate_composition` | `h-m3/code/composition_validator.py` |
| CompositionValidator | `from composition_validator import CompositionValidator` | `h-m3/code/composition_validator.py` |
| CompositionViolation | `from composition_validator import CompositionViolation` | `h-m3/code/composition_validator.py` |
| DeviceConsistencyViolation | `from composition_validator import DeviceConsistencyViolation` | `h-m3/code/composition_validator.py` |

**Verified from**: `/workspace/TEST_scope/docs/youra_research/h-m3/code/` (actual implementation)

**h-m3 Validation Results** (Prerequisite Gate: PASS):
- Detection rate: 71.4% (5/7 defects)
- False positive rate: 0% (0/1 control)
- Execution time: 0.004s average
- Known limitations: Generator object validation not covered, layout checks may be overly strict

---

## 4. Data Flow

### 4.1 Retrospective Analysis Flow (Dataset 1)

```
1. Load Jiang et al. 348-defect corpus (CSV)
   ↓
2. Filter environment-stage contractable defects (estimated 30-50)
   ↓
3. For each defect:
   a. Baseline: Training-stage detection (68% per Jiang et al.)
   b. Proposed: Apply h-m3 contracts at environment-stage
   ↓
4. Measure lifecycle shift: training_time - environment_time
   ↓
5. Calculate baseline TTFF reduction
```

### 4.2 Prospective Trial Flow (Dataset 2)

```
1. Repository Selection
   - GitHub search: stars>1K, Python, computer vision
   - Filter active (commits in last 6 months)
   - Stratify by maturity: High (>5K stars), Medium (1K-5K stars)
   - Target: 30-50 repos
   ↓
2. PR-Level Randomization
   - Incoming PR triggers workflow
   - TrialManager assigns to CI-Only or CI+Contracts (50/50)
   - Assignment persists in SQLite database
   ↓
3. Workflow Execution
   CI-Only:                    CI+Contracts:
   - setup-python              - setup-python
   - install dependencies      - install dependencies
   - run pytest                - [NEW] contract validation
   - training script           - run pytest (if contracts pass)
                               - training script (if contracts pass)
   ↓
4. Timing Instrumentation
   - Log started_at (workflow start)
   - Log completed_at (first failure)
   - Calculate TTFF in hours
   - Export to GitHub Actions outputs
   ↓
5. Data Collection (GitHub Actions API)
   - Pull workflow run data
   - Extract job timestamps
   - Parse step logs for failure stage
   - Store in SQLite + JSON
   ↓
6. Failure Stage Classification
   - Environment: Contract step failure, setup failure
   - Training: Training script failure
   - Unknown: Timeout, infrastructure failure (<5%)
```

### 4.3 Evaluation Pipeline

```
1. Aggregate data from both datasets
   ↓
2. Calculate primary metrics:
   - Median TTFF (CI-Only)
   - Median TTFF (CI+Contracts)
   - TTFF reduction = median(CI-Only) - median(CI+Contracts)
   ↓
3. Calculate secondary metrics:
   - Environment-stage detection counts (CI-Only vs CI+Contracts)
   - Marginal detection improvement = (Contracts - Only) / Only * 100
   ↓
4. Statistical tests:
   - Mann-Whitney U test (TTFF distributions)
   - p < 0.05 for significance
   ↓
5. Generate visualizations:
   - gate_metrics.png (required)
   - stage_distribution.png
   - ttff_distribution.png
   ↓
6. Gate decision:
   - PASS: TTFF reduction ≥5h AND marginal detection ≥25%
   - PARTIAL: TTFF reduction 3-5h
   - FAIL: TTFF reduction <3h
```

---

## 5. Interface Contracts

### 5.1 GitHub Actions Workflow API

**CI-Only Workflow** (`ci_integration/workflows/ci_only.yml`):
```yaml
name: CI-Only Baseline
on: pull_request

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
      - name: Run training
        run: python train.py
```

**CI+Contracts Workflow** (`ci_integration/workflows/ci_contracts.yml`):
```yaml
name: CI+Contracts Proposed
on: pull_request

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      # === NEW: Contract Validation Step ===
      - name: Validate API Contracts
        id: contracts
        run: python ci_integration/contract_step.py --config .contract_config.json
        env:
          CONTRACT_FAIL_FAST: true
      
      - name: Run tests
        if: steps.contracts.outcome == 'success'
        run: pytest tests/
      - name: Run training
        if: steps.contracts.outcome == 'success'
        run: python train.py
```

### 5.2 Contract Configuration Schema

**`.contract_config.json`**:
```json
{
  "validation_rules": {
    "device_consistency": true,
    "dtype_spec": {
      "model_input": "torch.float32",
      "attention_mask": "torch.float32"
    },
    "layout_spec": null
  },
  "fail_fast": true,
  "log_level": "INFO"
}
```

### 5.3 Trial Database Schema

**SQLite Tables**:

```sql
-- Repositories enrolled in trial
CREATE TABLE repositories (
    repo_id TEXT PRIMARY KEY,
    repo_name TEXT NOT NULL,
    stars INTEGER,
    last_commit_date TEXT,
    maturity TEXT  -- 'high' or 'medium'
);

-- PR-level arm assignments
CREATE TABLE pr_assignments (
    pr_id TEXT PRIMARY KEY,
    repo_id TEXT,
    pr_number INTEGER,
    arm TEXT,  -- 'ci_only' or 'ci_contracts'
    assigned_at TEXT,
    FOREIGN KEY (repo_id) REFERENCES repositories(repo_id)
);

-- Workflow execution results
CREATE TABLE workflow_results (
    run_id TEXT PRIMARY KEY,
    pr_id TEXT,
    started_at TEXT,
    completed_at TEXT,
    ttff_hours REAL,
    failure_stage TEXT,  -- 'environment', 'training', 'unknown'
    error_message TEXT,
    FOREIGN KEY (pr_id) REFERENCES pr_assignments(pr_id)
);
```

### 5.4 Experiment Results JSON Schema

```json
{
  "experiment_id": "h-m4-poc",
  "timestamp": "2026-07-11T...",
  "retrospective_analysis": {
    "corpus": "jiang2023_348defects",
    "contractable_defects": 35,
    "baseline_ttff_median": 10.5,
    "proposed_ttff_median": 0.2,
    "lifecycle_shift": 10.3
  },
  "prospective_trial": {
    "repositories": 42,
    "total_prs": 156,
    "ci_only": {
      "prs": 78,
      "median_ttff": 8.7,
      "environment_stage_count": 15,
      "training_stage_count": 48
    },
    "ci_contracts": {
      "prs": 78,
      "median_ttff": 2.3,
      "environment_stage_count": 52,
      "training_stage_count": 11
    },
    "ttff_reduction": 6.4,
    "marginal_detection_improvement": 31.2,
    "mann_whitney_p": 0.0023
  },
  "gate_status": "PASS"
}
```

---

## 6. Error Handling Strategy

### 6.1 CI Workflow Failures

**Contract Validation Failures** (Environment-stage detection):
- Raise DeviceConsistencyViolation → Log with `::error::` syntax
- Set step outcome to 'failure' → Skip subsequent steps
- Export violation details to GitHub Actions outputs
- Log timestamps for TTFF calculation

**Baseline CI Failures** (Training-stage detection):
- pytest failures → Continue to training (to measure TTFF)
- Training script errors → Log failure stage as "training"
- Timeout → Classify as "unknown" (<5% target)

### 6.2 GitHub API Rate Limiting

**Strategy**:
- Exponential backoff: Initial 60s, max 3600s
- Request caching: Store workflow run data locally
- Batch collection: Distribute over trial duration (8-12 weeks)
- Error logging: Track API errors separately from trial failures

### 6.3 Data Collection Failures

**Missing Data Handling**:
- Missing timestamp → Skip TTFF calculation, flag for review
- Incomplete logs → Classify stage as "unknown"
- API errors → Retry up to 3 times, then skip PR
- Database failures → Fallback to JSON file storage

---

## 7. Performance Optimization

### 7.1 Contract Validation Overhead

**Target**: <10 seconds per CI run (NFR-1)
**Expected**: <1 second based on h-m3 results (0.004s validation time)

**Optimization**:
- Reuse h-m3 lightweight validation (no probe execution)
- Early exit on first violation detected
- Minimal logging (only violations)

### 7.2 GitHub API Request Budget

**Rate Limit**: 5000 requests/hour (authenticated)
**Request Budget per PR**:
- 1 request: Get workflow run
- 1 request: Get job details
- 1 request: Get step logs
- **Total: 3 requests per PR**

**Trial Capacity**:
- 200 PRs × 3 requests = 600 requests
- Well below 5000/hour limit
- Collection distributed over 8-12 weeks

### 7.3 Data Storage

**SQLite Database**:
- Expected size: <10 MB for 200 PRs
- Query time: <100ms for aggregation
- Backup: JSON exports every 50 PRs

---

## 8. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | CI Integration Layer | Implement contract_step.py + timing_logger.py + workflow YAMLs | 16 | Module(4) + Deps(3) + Algo(4) + Integ(5) |
| A-2 | GitHub API Client | PyGithub wrapper for workflow run data collection | 14 | Module(4) + Deps(3) + Algo(3) + Integ(4) |
| A-3 | Corpus Analyzer | Retrospective analysis on Jiang et al. 348-defect corpus | 12 | Module(3) + Deps(2) + Algo(4) + Integ(3) |
| A-4 | Trial Manager | PR randomization + SQLite database + arm assignment | 15 | Module(4) + Deps(2) + Algo(4) + Integ(5) |
| A-5 | Stage Classifier | Parse CI logs to determine environment vs. training failure | 11 | Module(3) + Deps(1) + Algo(4) + Integ(3) |
| A-6 | Metrics Calculator | TTFF reduction, marginal detection, Mann-Whitney U test | 13 | Module(3) + Deps(3) + Algo(4) + Integ(3) |
| A-7 | Visualization | Generate gate_metrics.png + stage_distribution.png + ttff_distribution.png | 10 | Module(2) + Deps(2) + Algo(3) + Integ(3) |
| A-8 | Experiment Orchestrator | Main run_experiment.py with retrospective + prospective pipeline | 14 | Module(3) + Deps(4) + Algo(3) + Integ(4) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-1, A-2, A-4, A-8], Medium(9-13): [A-3, A-5, A-6, A-7], Low(4-8): []

**Complexity Scoring**:
- Module_Size: 1 (single function) to 5 (multiple classes with state management)
- Dependencies: 1 (stdlib only) to 5 (external APIs + cross-module + h-m3 integration)
- Algorithm: 1 (trivial) to 5 (statistical tests, log parsing, randomization)
- Integration: 1 (isolated) to 5 (CI platform, GitHub API, database, multi-module orchestration)

---

## 9. Technology Integration

### 9.1 h-m3 Contract Validator Reuse

**Integration Pattern**:
```python
# ci_integration/contract_step.py
import sys
from pathlib import Path

# Add h-m3 code to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m3" / "code"))

from composition_validator import (
    validate_composition,
    CompositionViolation,
    DeviceConsistencyViolation,
    DtypeConsistencyViolation,
    LayoutConsistencyViolation
)

# Use decorator pattern from h-m3
@validate_composition(device_consistency=True)
def test_model_forward(model_input, attention_mask):
    # Validation happens before function execution
    return model(model_input, attention_mask)
```

### 9.2 GitHub Actions Native Integration

**Output Syntax**:
```python
# Export metrics to GitHub Actions
def log_github_output(key: str, value: str):
    print(f"::set-output name={key}::{value}")

# Error annotation
def log_github_error(message: str):
    print(f"::error::{message}")

# Notice annotation
def log_github_notice(message: str):
    print(f"::notice::{message}")
```

**Step Conditional Execution**:
```yaml
- name: Run training
  if: steps.contracts.outcome == 'success'
  run: python train.py
```

### 9.3 PyGithub API Integration

**Workflow Run Data Extraction**:
```python
from github import Github

g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo("owner/repo")
run = repo.get_workflow_run(run_id)

# Extract timestamps
started_at = run.created_at  # datetime object
completed_at = run.updated_at

# Get job-level details
for job in run.jobs():
    for step in job.steps:
        if step.conclusion == "failure":
            # Extract failure logs
            print(step.name, step.started_at, step.completed_at)
```

### 9.4 Jiang et al. Corpus Processing

**CSV Format** (Expected):
```csv
defect_id,stage_of_failure,defect_type,description
DEF-001,training,device_mismatch,Query tensor on CUDA but mask on CPU
DEF-002,environment,dtype_incompatibility,Model expects float32 but receives float16
...
```

**Filtering Logic**:
```python
import pandas as pd

df = pd.read_csv("data/jiang2023_defects.csv")

# Filter for environment-stage contractable defects
contractable = df[
    (df['stage_of_failure'] == 'environment') &
    (df['defect_type'].isin(['device_mismatch', 'dtype_incompatibility', 'layout_incompatibility']))
]

# Expected: 30-50 defects (out of 348)
print(f"Contractable defects: {len(contractable)}")
```

---

## 10. Validation Strategy

### 10.1 Gate Criteria (SHOULD_WORK)

**Primary Metric**:
- Median TTFF reduction ≥5 hours → PASS
- TTFF reduction 3-5 hours → PARTIAL
- TTFF reduction <3 hours → FAIL

**Secondary Metric**:
- Marginal detection improvement ≥25% → PASS
- Marginal detection improvement 15-25% → PARTIAL
- Marginal detection improvement <15% → FAIL

**Statistical Significance**:
- Mann-Whitney U test: p < 0.05
- Effect size: Cohen's d ≥0.5 (medium effect)

### 10.2 False Positive Prevention

**Strategy**:
- Pilot test: 5 PRs before full trial launch
- Monitor FP rate continuously during trial
- Target: FP rate <5% (NFR-2)
- Action: If FP rate >5%, pause trial and adjust validation logic

**False Positive Definition**:
- Contract violation detected on valid PR (all tests pass in manual review)
- Documented in trial metadata

### 10.3 PoC Success Criteria

**Minimal Validation** (before gate evaluation):
- Code runs without error
- TTFF reduction > 0 (any improvement)
- Environment-stage proportion (CI+Contracts) > Environment-stage proportion (CI-Only)

**PoC Scope**:
- Retrospective analysis: All 348 defects processed
- Prospective trial: Pilot test with 5 PRs only
- Visualizations: gate_metrics.png generated

---

## 11. Risk Mitigation

### 11.1 Technical Risks

**Risk: Insufficient PR volume** (RISK-1)
- Probability: Medium
- Mitigation: Expand repository search to 100 candidates, accept 50 most active
- Fallback: Extend trial duration to 16 weeks

**Risk: GitHub API rate limiting** (RISK-2)
- Probability: Medium
- Mitigation: Implement request caching, distribute collection over trial duration
- Fallback: Use multiple GitHub tokens (team collaboration)

**Risk: False positive contract violations** (RISK-3)
- Probability: Low (h-m3 achieved 0% FPR)
- Mitigation: Pilot test on 5 PRs first, monitor FPR continuously
- Fallback: Whitelist known false positive patterns

**Risk: Contamination between arms** (RISK-4)
- Probability: Low
- Mitigation: Strict PR-level assignment, no mid-trial arm switching
- Validation: Database integrity check (no PR with multiple arms)

### 11.2 Data Quality Risks

**Risk: Missing timestamps** (incomplete GitHub Actions data)
- Mitigation: Validate data completeness before analysis
- Fallback: Exclude incomplete runs, require ≥80% data completeness

**Risk: Log parsing failures** (stage classification errors)
- Mitigation: Test classifier on labeled dataset (≥95% accuracy target)
- Fallback: Manual review of ambiguous cases

---

## 12. Appendices

### A. Example Contract Validation in CI

**Contract Configuration** (`.contract_config.json`):
```json
{
  "validation_rules": {
    "device_consistency": true,
    "dtype_spec": {
      "model_input": "torch.float32",
      "attention_mask": "torch.float32"
    }
  },
  "fail_fast": true
}
```

**CI Step Execution**:
```bash
$ python ci_integration/contract_step.py --config .contract_config.json

Running composition-level contract validation...
✓ Device consistency: PASS
✓ Dtype consistency: PASS
Contract validation completed in 0.12s

::set-output name=validation_time::0.12
::notice::All contracts validated successfully
```

**Failure Example**:
```bash
$ python ci_integration/contract_step.py --config .contract_config.json

Running composition-level contract validation...
✗ Device consistency: FAIL

::error::Device consistency violation detected:
  - model_input: cuda:0
  - attention_mask: cpu

Suggestion: Ensure all tensors are moved to same device before cross-library operations.
Fix: attention_mask = attention_mask.to('cuda')

::set-output name=validation_time::0.08
Exit code: 1
```

### B. GitHub API Data Collection Example

**Workflow Run Query**:
```python
from github import Github
from datetime import datetime

g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo("user/ml-project")

# Get recent workflow runs
runs = repo.get_workflow_runs(status="completed")

for run in runs[:5]:  # Latest 5 runs
    print(f"Run {run.id}:")
    print(f"  Started: {run.created_at}")
    print(f"  Completed: {run.updated_at}")
    
    # Calculate TTFF
    ttff = (run.updated_at - run.created_at).total_seconds() / 3600
    print(f"  TTFF: {ttff:.2f} hours")
    
    # Get failure stage
    for job in run.jobs():
        for step in job.steps:
            if step.conclusion == "failure":
                stage = "environment" if "contract" in step.name.lower() else "training"
                print(f"  Failure stage: {stage}")
                print(f"  Failed step: {step.name}")
```

**Output**:
```
Run 123456789:
  Started: 2026-07-10 08:30:00
  Completed: 2026-07-10 14:45:00
  TTFF: 6.25 hours
  Failure stage: training
  Failed step: Run training

Run 123456790:
  Started: 2026-07-10 15:00:00
  Completed: 2026-07-10 15:02:00
  TTFF: 0.03 hours
  Failure stage: environment
  Failed step: Validate API Contracts
```

### C. Metrics Calculation Example

**TTFF Reduction**:
```python
import numpy as np
from scipy import stats

# Hypothetical trial data
ci_only_ttff = [8.5, 10.2, 9.7, 11.3, 7.8, ...]  # 78 values
ci_contracts_ttff = [2.1, 0.5, 3.2, 1.8, 2.5, ...]  # 78 values

# Primary metric
median_ci_only = np.median(ci_only_ttff)
median_ci_contracts = np.median(ci_contracts_ttff)
ttff_reduction = median_ci_only - median_ci_contracts

print(f"Median TTFF (CI-Only): {median_ci_only:.2f} hours")
print(f"Median TTFF (CI+Contracts): {median_ci_contracts:.2f} hours")
print(f"TTFF Reduction: {ttff_reduction:.2f} hours")

# Statistical test
u_stat, p_value = stats.mannwhitneyu(ci_only_ttff, ci_contracts_ttff, alternative='greater')
print(f"Mann-Whitney U: {u_stat}, p-value: {p_value:.4f}")

# Gate decision
if ttff_reduction >= 5.0 and p_value < 0.05:
    print("GATE STATUS: PASS")
elif ttff_reduction >= 3.0:
    print("GATE STATUS: PARTIAL")
else:
    print("GATE STATUS: FAIL")
```

**Expected Output**:
```
Median TTFF (CI-Only): 9.20 hours
Median TTFF (CI+Contracts): 2.80 hours
TTFF Reduction: 6.40 hours
Mann-Whitney U: 4523, p-value: 0.0018
GATE STATUS: PASS
```

### D. Stage Distribution Calculation

**Stage Classification**:
```python
import pandas as pd

# Trial results
results = pd.DataFrame({
    'arm': ['ci_only'] * 78 + ['ci_contracts'] * 78,
    'stage': ['training'] * 48 + ['environment'] * 15 + ['unknown'] * 15 +
             ['environment'] * 52 + ['training'] * 11 + ['unknown'] * 15
})

# Calculate proportions
stage_dist = results.groupby(['arm', 'stage']).size().unstack(fill_value=0)
stage_dist_pct = stage_dist.div(stage_dist.sum(axis=1), axis=0) * 100

print(stage_dist_pct)
```

**Output**:
```
                environment  training  unknown
arm                                           
ci_contracts          66.7      14.1     19.2
ci_only               19.2      61.5     19.2
```

**Lifecycle Shift Observed**:
- CI-Only: 19.2% environment-stage detection
- CI+Contracts: 66.7% environment-stage detection
- **Shift: +47.5 percentage points** (lifecycle moved earlier)

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Steps:** Proceed to Phase 4 (Implementation)  
**Expected Timeline:** Phase 4 PoC (retrospective + 5-PR pilot) within 2-3 sessions, full trial (8-12 weeks) for gate evaluation
