# Logic Design: H-M4 CI Workflow Lifecycle Shift

**Hypothesis ID:** h-m4  
**Document Type:** Logic Design  
**Phase:** 3 - Implementation Planning  
**Status:** READY FOR CODING  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-m3 actual implementation  
**Analyzed Path**: docs/youra_research/h-m3/code/  
**Relevant Symbols**: CompositionValidator, validate_composition, CompositionViolation, DeviceConsistencyViolation, DtypeConsistencyViolation, LayoutConsistencyViolation

**Critical Finding**: h-m3 implements decorator-based composition validation with structured exception hierarchy. Returns tuple (is_valid, violations) from validator methods. This h-m4 extends with CI integration layer.

---

## KB Pattern Application

**Applied**: PyTorch CUDA event timing pattern, PyTorch random seed control, GitHub Actions workflow patterns

---

## A-1: CI Integration Layer [Complexity: 16, Budget: 4]

### API Signatures

```python
import sys
import time
import json
import os
from pathlib import Path
from typing import Dict, Optional, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m3" / "code"))
from composition_validator import validate_composition, CompositionViolation


class CIContractValidator:
    """GitHub Actions contract validation step."""
    
    def __init__(self, config_path: str):
        """Initialize validator with config.
        
        Args:
            config_path: Path to .contract_config.json
        """
        ...
    
    def run_validation(self) -> int:
        """Execute contract validation in CI environment.
        
        Returns:
            Exit code: 0 (success), 1 (violation detected)
        """
        ...
    
    def log_github_output(self, key: str, value: str) -> None:
        """Export metric to GitHub Actions outputs.
        
        Args:
            key: Output name
            value: Output value
        """
        ...
    
    def format_error_for_ci(self, violation: CompositionViolation) -> str:
        """Format violation for GitHub Actions error annotation.
        
        Args:
            violation: CompositionViolation with structured violations
        
        Returns:
            GitHub Actions error syntax string
        """
        ...


class TimingLogger:
    """Track workflow timing for TTFF measurement."""
    
    def __init__(self, output_path: str):
        """Initialize timing logger.
        
        Args:
            output_path: Path to timing log JSON file
        """
        ...
    
    def log_workflow_start(self, run_id: str) -> None:
        """Log workflow start timestamp.
        
        Args:
            run_id: GitHub Actions run ID
        """
        ...
    
    def log_failure_detected(self, run_id: str, stage: str) -> None:
        """Log failure detection timestamp.
        
        Args:
            run_id: GitHub Actions run ID
            stage: "environment" or "training"
        """
        ...
    
    def calculate_ttff(self, run_id: str) -> float:
        """Calculate time-to-first-failure.
        
        Args:
            run_id: GitHub Actions run ID
        
        Returns:
            TTFF in hours
        """
        ...
    
    def export_to_github_outputs(self) -> None:
        """Export timing metrics to GitHub Actions."""
        ...
```

### Pseudo-code

```
CIContractValidator.run_validation():
    1. start_time = time.time()
    2. config = load_json(self.config_path)
    3. validation_rules = config['validation_rules']
    
    4. try:
        # Apply h-m3 composition validator
        5. @validate_composition(
            device_consistency=validation_rules['device_consistency'],
            dtype_spec=validation_rules.get('dtype_spec'),
            layout_spec=validation_rules.get('layout_spec')
        )
        6. def validate_environment():
            # Trigger import-time validation
            import torch
            import transformers
            return True
        
        7. validate_environment()
        8. elapsed = time.time() - start_time
        9. log_github_output('validation_time', str(elapsed))
        10. print('::notice::Contracts validated successfully')
        11. return 0
    
    12. except CompositionViolation as e:
        13. elapsed = time.time() - start_time
        14. error_msg = format_error_for_ci(e)
        15. print(f'::error::{error_msg}')
        16. log_github_output('validation_time', str(elapsed))
        17. return 1

TimingLogger.calculate_ttff(run_id):
    1. log_data = load_json(self.output_path)
    2. run_log = log_data[run_id]
    3. started_at = parse_iso_timestamp(run_log['started_at'])
    4. completed_at = parse_iso_timestamp(run_log['completed_at'])
    5. ttff_seconds = (completed_at - started_at).total_seconds()
    6. ttff_hours = ttff_seconds / 3600
    7. return ttff_hours
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | CI validator wrapper | Wrap h-m3 validator for GitHub Actions |
| L-1-2 | GitHub output syntax | Implement ::set-output, ::error annotations |
| L-1-3 | Timing logger | Track workflow start/failure timestamps |
| L-1-4 | TTFF calculation | Calculate time-to-first-failure in hours |

---

## A-2: GitHub API Client [Complexity: 14, Budget: 3]

### API Signatures

```python
from github import Github, Repository, WorkflowRun
from datetime import datetime
from typing import List, Dict, Optional


class GitHubMetricsCollector:
    """Collect workflow run data via GitHub API."""
    
    def __init__(self, token: str):
        """Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token
        """
        ...
    
    def get_workflow_run(self, repo: str, run_id: int) -> WorkflowRun:
        """Fetch workflow run data.
        
        Args:
            repo: Repository name (owner/repo)
            run_id: GitHub Actions run ID
        
        Returns:
            PyGithub WorkflowRun object
        """
        ...
    
    def get_job_timestamps(self, run: WorkflowRun) -> Dict[str, datetime]:
        """Extract job-level timestamps.
        
        Args:
            run: PyGithub WorkflowRun object
        
        Returns:
            Dict with 'started_at', 'completed_at' keys
        """
        ...
    
    def get_step_logs(self, run: WorkflowRun) -> List[str]:
        """Download step logs for stage classification.
        
        Args:
            run: PyGithub WorkflowRun object
        
        Returns:
            List of log lines
        """
        ...
    
    def calculate_ttff_from_run(self, run: WorkflowRun) -> float:
        """Calculate TTFF from run data.
        
        Args:
            run: PyGithub WorkflowRun object
        
        Returns:
            TTFF in hours
        """
        ...
```

### Pseudo-code

```
GitHubMetricsCollector.calculate_ttff_from_run(run):
    1. jobs = list(run.jobs())
    2. if len(jobs) == 0:
        return None
    3. job = jobs[0]  # First job
    4. started_at = job.started_at
    5. completed_at = job.completed_at
    6. ttff_seconds = (completed_at - started_at).total_seconds()
    7. ttff_hours = ttff_seconds / 3600
    8. return ttff_hours

GitHubMetricsCollector.get_step_logs(run):
    1. logs = []
    2. for job in run.jobs():
        for step in job.steps:
            if step.conclusion == 'failure':
                logs.append(f'{step.name}: {step.conclusion}')
    3. return logs
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | PyGithub wrapper | Wrap GitHub API for workflow data |
| L-2-2 | Timestamp extraction | Extract started_at, completed_at |
| L-2-3 | Log parsing | Download step logs for classification |

---

## A-4: Trial Manager [Complexity: 15, Budget: 3]

### API Signatures

```python
import sqlite3
import random
from typing import List, Dict, Optional
from enum import Enum


class Arm(Enum):
    """Experimental arm assignment."""
    CI_ONLY = "ci_only"
    CI_CONTRACTS = "ci_contracts"


class TrialManager:
    """Manage PR-level randomization and data persistence."""
    
    def __init__(self, db_path: str, seed: int = 42):
        """Initialize trial manager.
        
        Args:
            db_path: Path to SQLite database
            seed: Random seed for reproducibility
        """
        ...
    
    def register_repository(self, repo_id: str, stars: int) -> None:
        """Register repository in trial.
        
        Args:
            repo_id: Repository identifier (owner/repo)
            stars: GitHub stars count
        """
        ...
    
    def assign_pr_to_arm(self, repo_id: str, pr_number: int) -> Arm:
        """Assign PR to experimental arm.
        
        Args:
            repo_id: Repository identifier
            pr_number: PR number
        
        Returns:
            Assigned arm (CI_ONLY or CI_CONTRACTS)
        """
        ...
    
    def get_arm_assignment(self, repo_id: str, pr_number: int) -> Optional[Arm]:
        """Retrieve existing PR assignment.
        
        Args:
            repo_id: Repository identifier
            pr_number: PR number
        
        Returns:
            Assigned arm or None if not assigned
        """
        ...
    
    def record_workflow_result(
        self,
        pr_id: str,
        ttff: float,
        stage: str
    ) -> None:
        """Record workflow execution result.
        
        Args:
            pr_id: PR identifier (repo_id#pr_number)
            ttff: Time-to-first-failure in hours
            stage: Failure stage ("environment" or "training")
        """
        ...
    
    def get_trial_summary(self) -> Dict:
        """Generate trial summary statistics.
        
        Returns:
            Dict with arm counts, median TTFF, stage distribution
        """
        ...
```

### Pseudo-code

```
TrialManager.assign_pr_to_arm(repo_id, pr_number):
    1. existing = get_arm_assignment(repo_id, pr_number)
    2. if existing is not None:
        return existing
    
    # New assignment
    3. pr_id = f'{repo_id}#{pr_number}'
    4. arm = random.choice([Arm.CI_ONLY, Arm.CI_CONTRACTS])
    5. conn = sqlite3.connect(self.db_path)
    6. conn.execute('''
        INSERT INTO pr_assignments (pr_id, repo_id, pr_number, arm, assigned_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (pr_id, repo_id, pr_number, arm.value, datetime.now().isoformat()))
    7. conn.commit()
    8. return arm

TrialManager.get_trial_summary():
    1. conn = sqlite3.connect(self.db_path)
    2. results = conn.execute('''
        SELECT arm, COUNT(*), AVG(ttff_hours), stage
        FROM workflow_results
        JOIN pr_assignments ON workflow_results.pr_id = pr_assignments.pr_id
        GROUP BY arm, stage
    ''').fetchall()
    3. summary = {
        'ci_only': {'count': 0, 'median_ttff': 0, 'environment_count': 0, 'training_count': 0},
        'ci_contracts': {'count': 0, 'median_ttff': 0, 'environment_count': 0, 'training_count': 0}
    }
    4. for row in results:
        arm, count, avg_ttff, stage = row
        summary[arm]['count'] += count
        if stage == 'environment':
            summary[arm]['environment_count'] = count
        elif stage == 'training':
            summary[arm]['training_count'] = count
    5. return summary
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | SQLite schema | Implement database schema |
| L-4-2 | Randomization | PR-level 50/50 assignment |
| L-4-3 | Trial summary | Aggregate arm statistics |

---

## A-5: Stage Classifier [Complexity: 11, Budget: 2]

### API Signatures

```python
import re
from typing import List, Optional


class StageClassifier:
    """Classify failure stage from CI logs."""
    
    def __init__(self):
        """Initialize stage classifier."""
        ...
    
    def classify_from_logs(self, step_logs: List[str]) -> str:
        """Classify failure stage from step logs.
        
        Args:
            step_logs: List of log lines from workflow run
        
        Returns:
            Stage: "environment", "training", or "unknown"
        """
        ...
    
    def is_environment_failure(self, log: str) -> bool:
        """Check if log indicates environment-stage failure.
        
        Args:
            log: Log line
        
        Returns:
            True if environment-stage failure
        """
        ...
    
    def is_training_failure(self, log: str) -> bool:
        """Check if log indicates training-stage failure.
        
        Args:
            log: Log line
        
        Returns:
            True if training-stage failure
        """
        ...
```

### Pseudo-code

```
StageClassifier.classify_from_logs(step_logs):
    1. for log in step_logs:
        # Check for contract validation failure
        2. if 'Validate API Contracts' in log and 'failure' in log:
            return 'environment'
        
        # Check for setup failures
        3. if 'setup-python' in log or 'Install dependencies' in log:
            if 'failure' in log:
                return 'environment'
        
        # Check for training failures
        4. if 'Run training' in log or 'train.py' in log:
            if 'failure' in log:
                return 'training'
    
    5. return 'unknown'

StageClassifier.is_environment_failure(log):
    1. patterns = [
        'contract', 'validation', 'setup', 'dependencies',
        'pip install', 'import error', 'module not found'
    ]
    2. for pattern in patterns:
        if pattern.lower() in log.lower():
            return True
    3. return False
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Log pattern matching | Regex patterns for stage detection |
| L-5-2 | Classification logic | Determine environment vs training |

---

## A-6: Metrics Calculator [Complexity: 13, Budget: 2]

### API Signatures

```python
import numpy as np
from scipy import stats
from typing import List, Dict, Tuple


class MetricsCalculator:
    """Calculate experiment evaluation metrics."""
    
    def calculate_median_ttff(self, ttff_list: List[float]) -> float:
        """Calculate median TTFF.
        
        Args:
            ttff_list: List of TTFF values in hours
        
        Returns:
            Median TTFF
        """
        ...
    
    def calculate_ttff_reduction(
        self,
        ci_only: List[float],
        ci_contracts: List[float]
    ) -> float:
        """Calculate TTFF reduction.
        
        Args:
            ci_only: TTFF values for CI-Only arm
            ci_contracts: TTFF values for CI+Contracts arm
        
        Returns:
            TTFF reduction in hours (positive = improvement)
        """
        ...
    
    def mann_whitney_test(
        self,
        ci_only: List[float],
        ci_contracts: List[float]
    ) -> Tuple[float, float]:
        """Perform Mann-Whitney U test.
        
        Args:
            ci_only: TTFF values for CI-Only arm
            ci_contracts: TTFF values for CI+Contracts arm
        
        Returns:
            (u_statistic, p_value)
        """
        ...
    
    def calculate_marginal_detection(
        self,
        ci_only_count: int,
        ci_contracts_count: int
    ) -> float:
        """Calculate marginal detection improvement.
        
        Args:
            ci_only_count: Environment-stage detections in CI-Only
            ci_contracts_count: Environment-stage detections in CI+Contracts
        
        Returns:
            Marginal improvement percentage
        """
        ...
    
    def calculate_stage_distribution(
        self,
        results: List[Dict]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate stage-of-failure distribution.
        
        Args:
            results: List of dicts with 'arm' and 'stage' keys
        
        Returns:
            Dict[arm -> Dict[stage -> proportion]]
        """
        ...
```

### Pseudo-code

```
MetricsCalculator.calculate_ttff_reduction(ci_only, ci_contracts):
    1. median_ci_only = np.median(ci_only)
    2. median_ci_contracts = np.median(ci_contracts)
    3. reduction = median_ci_only - median_ci_contracts
    4. return reduction

MetricsCalculator.mann_whitney_test(ci_only, ci_contracts):
    1. u_stat, p_value = stats.mannwhitneyu(
        ci_only,
        ci_contracts,
        alternative='greater'
    )
    2. return (u_stat, p_value)

MetricsCalculator.calculate_marginal_detection(ci_only_count, ci_contracts_count):
    1. if ci_only_count == 0:
        return 0.0
    2. improvement = (ci_contracts_count - ci_only_count) / ci_only_count * 100
    3. return improvement
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Statistical tests | Implement Mann-Whitney U test |
| L-6-2 | Metric formulas | TTFF reduction, marginal detection |

---

## A-8: Experiment Orchestrator [Complexity: 14, Budget: 3]

### API Signatures

```python
import argparse
import json
from pathlib import Path
from typing import Dict


class ExperimentOrchestrator:
    """Coordinate full h-m4 experiment execution."""
    
    def __init__(self, config_path: str):
        """Initialize orchestrator.
        
        Args:
            config_path: Path to experiment configuration
        """
        ...
    
    def run_retrospective_analysis(self) -> Dict:
        """Execute retrospective analysis on Jiang et al. corpus.
        
        Returns:
            Dict with baseline TTFF, proposed TTFF, lifecycle shift
        """
        ...
    
    def run_prospective_trial(self) -> Dict:
        """Execute prospective PR-level trial.
        
        Returns:
            Dict with arm statistics, TTFF distributions, p-values
        """
        ...
    
    def evaluate_gate_criteria(self, results: Dict) -> bool:
        """Evaluate SHOULD_WORK gate criteria.
        
        Args:
            results: Combined results from retrospective + prospective
        
        Returns:
            True if gate criteria met
        """
        ...
    
    def generate_report(self, results: Dict) -> None:
        """Generate experiment report and visualizations.
        
        Args:
            results: Combined results
        """
        ...


def main() -> int:
    """Execute full h-m4 experiment.
    
    Returns:
        Exit code: 0 (success), 1 (failure)
    """
    ...
```

### Pseudo-code

```
ExperimentOrchestrator.evaluate_gate_criteria(results):
    1. prospective = results['prospective_trial']
    2. ttff_reduction = prospective['ttff_reduction']
    3. marginal_detection = prospective['marginal_detection_improvement']
    4. p_value = prospective['mann_whitney_p']
    
    # Primary gate criterion
    5. if ttff_reduction >= 5.0 and p_value < 0.05:
        gate_status = 'PASS'
    6. elif ttff_reduction >= 3.0:
        gate_status = 'PARTIAL'
    7. else:
        gate_status = 'FAIL'
    
    # Secondary gate criterion
    8. if marginal_detection >= 25.0:
        gate_status = gate_status  # No change if already PASS/PARTIAL
    9. elif marginal_detection < 15.0 and gate_status == 'PASS':
        gate_status = 'PARTIAL'
    
    10. results['gate_status'] = gate_status
    11. return gate_status in ['PASS', 'PARTIAL']

main():
    1. parser = argparse.ArgumentParser()
    2. parser.add_argument('--config', required=True)
    3. args = parser.parse_args()
    
    4. orchestrator = ExperimentOrchestrator(args.config)
    5. retrospective = orchestrator.run_retrospective_analysis()
    6. prospective = orchestrator.run_prospective_trial()
    
    7. results = {
        'retrospective_analysis': retrospective,
        'prospective_trial': prospective
    }
    
    8. gate_passed = orchestrator.evaluate_gate_criteria(results)
    9. orchestrator.generate_report(results)
    
    10. return 0 if gate_passed else 1
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Pipeline coordination | Coordinate retrospective + prospective |
| L-8-2 | Gate evaluation | Evaluate SHOULD_WORK criteria |
| L-8-3 | Report generation | Generate JSON report + visualizations |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-m3 base hypothesis. Signatures verified from actual implementation:

```python
# From: /workspace/TEST_scope/docs/youra_research/h-m3/code/composition_validator.py

class CompositionViolation(Exception):
    """Base exception for composition-level violations."""
    def __init__(self, message: str, violations: List[Dict[str, Any]]):
        """Initialize with structured violation data.
        
        Args:
            message: Human-readable error message
            violations: List of dicts with keys: param_name, expected, actual, violation_type
        """
        ...


class DeviceConsistencyViolation(CompositionViolation):
    """Raised when tensors are on inconsistent devices."""
    pass


class DtypeConsistencyViolation(CompositionViolation):
    """Raised when tensors have inconsistent dtypes."""
    pass


class LayoutConsistencyViolation(CompositionViolation):
    """Raised when tensors have incompatible layouts."""
    pass


def validate_composition(
    device_consistency: bool = True,
    dtype_spec: Optional[Dict[str, torch.dtype]] = None,
    layout_spec: Optional[Dict[str, torch.layout]] = None
) -> Callable:
    """Decorator for composition-level contract validation.
    
    Args:
        device_consistency: If True, validate all tensors on same device
        dtype_spec: Dict of param_name -> expected_dtype
        layout_spec: Dict of param_name -> expected_layout
    
    Returns:
        Decorator that wraps function with composition validation
    
    Raises:
        DeviceConsistencyViolation: If tensors on different devices
        DtypeConsistencyViolation: If dtypes don't match spec
        LayoutConsistencyViolation: If layouts incompatible
    
    Example:
        @validate_composition(
            device_consistency=True,
            dtype_spec={'query': torch.float32, 'key': torch.float32}
        )
        def attention(query, key, value):
            return (query @ key.T) @ value
    """
    ...


class CompositionValidator:
    """Core validator for composition-level contracts."""
    
    def validate_device_consistency(
        self,
        tensors: Dict[str, torch.Tensor]
    ) -> Tuple[bool, Optional[List[Dict]]]:
        """Validate all tensors on same device.
        
        Args:
            tensors: Dict of param_name -> tensor
        
        Returns:
            (is_valid, violations). violations is None if valid.
        """
        ...
    
    def validate_dtype_consistency(
        self,
        tensors: Dict[str, torch.Tensor],
        dtype_spec: Dict[str, torch.dtype]
    ) -> Tuple[bool, Optional[List[Dict]]]:
        """Validate tensors match expected dtypes.
        
        Args:
            tensors: Dict of param_name -> tensor
            dtype_spec: Dict of param_name -> expected_dtype
        
        Returns:
            (is_valid, violations). violations is None if valid.
        """
        ...
    
    def validate_layout_consistency(
        self,
        tensors: Dict[str, torch.Tensor]
    ) -> Tuple[bool, Optional[List[Dict]]]:
        """Validate tensors have compatible layouts.
        
        Args:
            tensors: Dict of param_name -> tensor
        
        Returns:
            (is_valid, violations). violations is None if valid.
        """
        ...
    
    def format_violation_message(
        self,
        violations: List[Dict[str, Any]],
        violation_type: str
    ) -> str:
        """Format structured violation data into actionable error message.
        
        Args:
            violations: List of violation dicts
            violation_type: Type of violation (device/dtype/layout)
        
        Returns:
            Formatted error message with suggestions
        """
        ...
```

**Verified from**: `/workspace/TEST_scope/docs/youra_research/h-m3/code/composition_validator.py` (actual implementation)

**Critical Note**: h-m3 validator methods return `Tuple[bool, Optional[List[Dict]]]` (not just error messages). Phase 4 coder must handle structured violations list.

---

## Data Structures

### SQLite Schema

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

### Contract Configuration Schema

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

### Experiment Results Schema

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

## Edge Cases & Error Handling

### GitHub API Rate Limiting

**Strategy**: Exponential backoff with caching
```python
def retry_with_backoff(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except github.RateLimitExceededException:
            wait_time = 60 * (2 ** i)
            time.sleep(wait_time)
    raise Exception('Rate limit exceeded after retries')
```

### Missing Timestamps

**Strategy**: Skip incomplete data
```python
if run.started_at is None or run.completed_at is None:
    log_warning(f'Missing timestamps for run {run.id}')
    return None  # Skip this PR
```

### CI Workflow Timeout

**Strategy**: Classify as "unknown" stage
```python
if run.conclusion == 'timed_out':
    stage = 'unknown'
    ttff = None  # Exclude from TTFF calculation
```

### Database Conflicts

**Strategy**: SQLite retry logic
```python
try:
    conn.execute(INSERT_QUERY)
except sqlite3.IntegrityError:
    # PR already assigned
    return get_existing_assignment()
```

---

## Summary

This logic design provides **copy-paste ready APIs** for h-m4 CI workflow lifecycle shift experiment. Key components:

1. **CI Integration Layer**: Wrap h-m3 validator for GitHub Actions with timing instrumentation
2. **GitHub API Client**: Collect workflow run data for TTFF measurement
3. **Trial Manager**: PR-level randomization with SQLite persistence
4. **Stage Classifier**: Log parsing for environment vs training detection
5. **Metrics Calculator**: Statistical tests (Mann-Whitney U) and gate evaluation
6. **Experiment Orchestrator**: Pipeline coordination and report generation

All modules designed for CI environment integration and statistical rigor.

**Total Budget Used**: 17/17 (100%)  
**Ready for Phase 4 Coding**: Yes
