# Implementation Tasks: H-M4

**Hypothesis ID:** h-m4  
**Tier:** FULL (30 tasks max)  
**Generated:** 2026-07-11  
**Source Documents:** 03_prd.md, 03_architecture.md, 03_logic.md, 03_config.md

---

## Task Budget Summary

| Category | Count |
|----------|-------|
| Data Preparation | 1 |
| Environment Setup | 1 |
| Epic Tasks | 8 |
| Subtasks | 14 |
| Failsafe | 1 |
| **Total** | **25 / 30** ✓ |

---

## Data Preparation Tasks

### Task-001: Download Jiang et al. 348-Defect Corpus

**Epic:** Data Preparation  
**Priority:** 100  
**Complexity:** N/A  
**Source:** 03_prd.md § 4.1

**Description:**
Download Jiang et al. (2023) 348-defect corpus from supplementary materials.

**Actions:**
1. Download CSV from paper supplementary materials
2. Place in: `./data/jiang2023_defects.csv`
3. Verify CSV columns: defect_id, stage_of_failure, defect_type, description
4. Filter for contractable defects (device, dtype, layout API defects)
5. Expected: ~100-120 contractable defects from 348 total

**Test Requirements:** Data download tasks do not require tests.

---

## Environment Setup Tasks

### Task-002: Setup Development Environment

**Epic:** Environment Setup  
**Priority:** 99  
**Complexity:** N/A  
**Source:** 03_prd.md § 8.2

**Description:**
Install required packages and verify h-m3 prerequisite integration.

**Dependencies:**
- PyGithub >= 2.1.0 (GitHub API client)
- pandas >= 1.5.0 (data analysis)
- matplotlib >= 3.6.0 (visualization)
- scipy >= 1.9.0 (statistical tests)
- pyyaml >= 6.0 (config parsing)
- torch >= 1.12.0 (h-m3 dependency)

**External Prerequisites:**
- h-m3/code/composition_validator.py (validated in h-m3)
- Verify import: `from h_m3.composition_validator import validate_composition`

**Test Requirements:** Environment setup does not require tests.

---

## Epic Implementation Tasks

### Task-003: Epic-A-1 — CI Integration Layer

**Priority:** 98  
**Complexity:** 16 (HIGH)  
**Source:** 03_architecture.md § 8, 03_logic.md, 03_config.md

**Description:**
Implement CI integration layer for contract validation at environment-setup stage.

**Components:**
1. `ci_integration/contract_step.py` — GitHub Actions step wrapper for h-m3 validator
2. `ci_integration/timing_logger.py` — Timestamp instrumentation for TTFF measurement
3. `ci_integration/workflows/ci_only.yml` — Baseline workflow (no contracts)
4. `ci_integration/workflows/ci_contracts.yml` — Proposed workflow with contract step

**Key APIs:**
```python
class CIContractValidator:
    def __init__(self, config_path: str): ...
    def run_validation(self) -> int: ...
    def log_github_output(self, key: str, value: str) -> None: ...
    def format_error_for_ci(self, violation: CompositionViolation) -> str: ...

def main() -> int:
    """Entry point for GitHub Actions step."""
```

**Integration:**
- Reuse h-m3 `validate_composition()` for contract checks
- GitHub Actions output syntax: `::set-output name=key::value`
- Exit code: 0 if pass, 1 if violations detected

**Test Requirements:**
- `tests/test_ci_integration.py`
- Test contract validation wrapper
- Test GitHub Actions output formatting
- Test error annotation for CI logs

**Subtasks:** 4 (task-011 through task-014)

---

### Task-004: Epic-A-2 — GitHub API Client

**Priority:** 97  
**Complexity:** 14 (HIGH)  
**Source:** 03_architecture.md § 8, 03_logic.md

**Description:**
Implement PyGithub API wrapper for workflow run data collection.

**Key APIs:**
```python
class GitHubMetricsClient:
    def __init__(self, token: str): ...
    def get_workflow_run_timing(self, repo: str, run_id: int) -> Dict: ...
    def extract_failure_stage(self, run_id: int) -> str: ...
    def get_job_timestamps(self, job_id: int) -> Tuple[datetime, datetime]: ...
```

**Data Extraction:**
- Workflow run: `started_at`, `completed_at`
- Job-level: step timestamps, failure logs
- Parse logs to determine environment vs. training stage failure

**Test Requirements:**
- `tests/test_github_api.py`
- Mock PyGithub responses for testing
- Test timestamp extraction accuracy
- Test stage classification logic

**Subtasks:** 3 (task-019 through task-021)

---

### Task-005: Epic-A-3 — Corpus Analyzer

**Priority:** 96  
**Complexity:** 12 (MEDIUM)  
**Source:** 03_architecture.md § 8, 03_logic.md

**Description:**
Retrospective analysis on Jiang et al. 348-defect corpus.

**Key APIs:**
```python
class CorpusAnalyzer:
    def load_corpus(self, path: str) -> pd.DataFrame: ...
    def filter_contractable_defects(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def classify_counterfactual_stage(self, defect: Dict) -> str: ...
    def compute_lifecycle_shift(self) -> Dict: ...
```

**Analysis:**
1. Load corpus CSV
2. Filter for environment-stage contractable defects
3. For each defect, determine if h-m3 contracts would detect it
4. Calculate expected lifecycle shift (68% training → X% environment)

**Test Requirements:**
- `tests/test_corpus_analyzer.py`
- Test CSV loading and filtering
- Test counterfactual classification logic
- Test lifecycle shift calculation

---

### Task-006: Epic-A-4 — Trial Manager

**Priority:** 95  
**Complexity:** 15 (HIGH)  
**Source:** 03_architecture.md § 8, 03_logic.md

**Description:**
PR-level randomization, trial tracking, and arm assignment.

**Key APIs:**
```python
class TrialManager:
    def __init__(self, db_path: str): ...
    def assign_pr_to_arm(self, pr_id: int, repo: str) -> str: ...
    def record_trial_result(self, pr_id: int, metrics: Dict): ...
    def get_arm_distribution(self) -> Dict[str, int]: ...
```

**Randomization:**
- Hash-based assignment (deterministic from PR ID)
- 50/50 split CI-Only vs. CI+Contracts
- Stratification by repo maturity and reporter type

**Persistence:**
- SQLite database for trial metadata
- Schema: pr_id, repo, arm, started_at, completed_at, failure_stage

**Test Requirements:**
- `tests/test_trial_manager.py`
- Test randomization determinism
- Test arm balance (50/50 ± 5%)
- Test database persistence

**Subtasks:** 4 (task-015 through task-018)

---

### Task-007: Epic-A-5 — Stage Classifier

**Priority:** 94  
**Complexity:** 11 (MEDIUM)  
**Source:** 03_architecture.md § 8, 03_logic.md

**Description:**
Parse CI logs to classify failures as environment-stage vs. training-stage.

**Key APIs:**
```python
class StageClassifier:
    def classify_from_logs(self, logs: str) -> str: ...
    def parse_step_name(self, step_name: str) -> str: ...
```

**Classification Rules:**
- "Validate API Contracts" or "Install dependencies" step → environment-stage
- "Run tests" or "Run training" step → training-stage
- Unknown → label as "unknown"

**Test Requirements:**
- `tests/test_stage_classifier.py`
- Test environment-stage classification
- Test training-stage classification
- Test edge cases (unknown failures)

---

### Task-008: Epic-A-6 — Metrics Calculator

**Priority:** 93  
**Complexity:** 13 (MEDIUM)  
**Source:** 03_architecture.md § 8, 03_logic.md

**Description:**
Calculate primary and secondary metrics with statistical tests.

**Key APIs:**
```python
class MetricsCalculator:
    def compute_median_ttff(self, arm: str) -> float: ...
    def compute_ttff_reduction(self) -> float: ...
    def compute_stage_distribution(self, arm: str) -> Dict: ...
    def run_statistical_tests(self) -> Dict: ...
```

**Metrics:**
- **Primary:** Median TTFF reduction (Mann-Whitney U test)
- **Secondary:** Environment-stage proportion (Chi-square test)
- **Secondary:** Marginal detection improvement (%)

**Test Requirements:**
- `tests/test_metrics_calculator.py`
- Test median TTFF calculation
- Test statistical test execution (Mann-Whitney U)
- Test stage distribution computation

---

### Task-009: Epic-A-7 — Visualization

**Priority:** 92  
**Complexity:** 10 (MEDIUM)  
**Source:** 03_architecture.md § 8, 03_logic.md

**Description:**
Generate required and optional figures for validation report.

**Required Figures:**
1. **gate_metrics.png:** Median TTFF bar chart (CI-Only vs. CI+Contracts) with -5h threshold line
2. **stage_distribution.png:** Stacked bar chart (environment vs. training stage proportions)

**Optional Figures:**
3. **ttff_distribution.png:** Box plot showing TTFF distribution per arm

**Key APIs:**
```python
class Visualizer:
    def plot_gate_metrics(self, data: Dict, save_path: str): ...
    def plot_stage_distribution(self, data: Dict, save_path: str): ...
    def plot_ttff_distribution(self, data: Dict, save_path: str): ...
```

**Test Requirements:**
- `tests/test_visualizer.py`
- Test figure generation (file exists)
- Test chart elements (threshold line, labels)
- Test data accuracy in plots

---

### Task-010: Epic-A-8 — Experiment Orchestrator

**Priority:** 91  
**Complexity:** 14 (HIGH)  
**Source:** 03_architecture.md § 8, 03_logic.md

**Description:**
Main experiment orchestrator with retrospective + prospective pipeline.

**Key APIs:**
```python
class ExperimentOrchestrator:
    def run_retrospective_analysis(self): ...
    def run_prospective_trial(self, duration_weeks: int): ...
    def generate_validation_report(self): ...
```

**Pipeline:**
1. **Retrospective:** Jiang et al. corpus analysis → baseline lifecycle shift
2. **Prospective:** Live GitHub PR trial → measured lifecycle shift
3. **Evaluation:** Compare results, compute gate metrics, generate report

**Test Requirements:**
- `tests/test_experiment_orchestrator.py`
- Test pipeline execution order
- Test error handling (missing data)
- Test validation report generation

**Subtasks:** 3 (task-022 through task-024)

---

## Subtasks

### CI Integration Layer Subtasks (Epic-A-1)

**Task-011:** Implement contract_step.py CI wrapper  
**Priority:** 90  
**Description:** GitHub Actions step wrapper for h-m3 composition validator with fail-fast behavior.

**Task-012:** Implement timing_logger.py instrumentation  
**Priority:** 89  
**Description:** Timestamp logging for TTFF measurement (started_at, completed_at).

**Task-013:** Create ci_only.yml workflow template  
**Priority:** 88  
**Description:** Baseline GitHub Actions workflow (no contract validation step).

**Task-014:** Create ci_contracts.yml workflow template  
**Priority:** 87  
**Description:** Proposed workflow with contract validation at environment-setup stage.

---

### Trial Manager Subtasks (Epic-A-4)

**Task-015:** Implement PR randomization logic  
**Priority:** 86  
**Description:** Hash-based deterministic randomization for PR-to-arm assignment.

**Task-016:** Create SQLite database schema  
**Priority:** 85  
**Description:** Trial metadata schema (pr_id, repo, arm, timestamps, failure_stage).

**Task-017:** Implement arm assignment tracker  
**Priority:** 84  
**Description:** Track PR assignments and ensure 50/50 arm balance.

**Task-018:** Add trial metadata persistence  
**Priority:** 83  
**Description:** Save trial results to SQLite database for analysis.

---

### GitHub API Client Subtasks (Epic-A-2)

**Task-019:** Implement PyGithub API wrapper  
**Priority:** 82  
**Description:** Wrapper class for GitHub Actions API with rate limit handling.

**Task-020:** Add timestamp extraction methods  
**Priority:** 81  
**Description:** Extract started_at, completed_at from workflow runs and jobs.

**Task-021:** Add log parsing utilities  
**Priority:** 80  
**Description:** Parse failure logs to extract error messages and failure context.

---

### Experiment Orchestrator Subtasks (Epic-A-8)

**Task-022:** Implement run_experiment.py orchestrator  
**Priority:** 79  
**Description:** Main orchestration script for retrospective + prospective pipeline.

**Task-023:** Add retrospective analysis pipeline  
**Priority:** 78  
**Description:** Jiang et al. corpus analysis with counterfactual classification.

**Task-024:** Add prospective trial pipeline  
**Priority:** 77  
**Description:** Live GitHub PR trial with data collection and analysis.

---

## Failsafe Task

### Task-025: Pipeline Continuation Checkpoint

**Epic:** Pipeline Management  
**Priority:** 1  
**Complexity:** N/A  
**Source:** System

**Description:**
Failsafe task for pipeline continuation. Triggers `/full-pipeline-unattended` if reached.

**Test Requirements:** Failsafe task does not require tests.

---

## Implementation Notes

### Reuse from h-m3
All tasks should leverage h-m3 composition validator:
```python
from h_m3.composition_validator import (
    validate_composition,
    CompositionViolation,
    DeviceConsistencyViolation,
    DtypeConsistencyViolation,
    LayoutConsistencyViolation
)
```

### GitHub Actions Integration
Use native GitHub Actions syntax for CI integration:
- `::set-output name=key::value` for outputs
- `::error::message` for error annotations
- `::notice::message` for success notifications

### Statistical Tests
Use scipy.stats for hypothesis testing:
- Mann-Whitney U test for TTFF comparison
- Chi-square test for stage distribution
- Cohen's d for effect size

---

**Total Tasks:** 25 / 30 budget ✓  
**Ready for Phase 4 Implementation**
