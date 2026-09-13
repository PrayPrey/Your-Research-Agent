# Configuration Design: H-M4 CI Workflow Lifecycle Shift

**Hypothesis ID:** h-m4  
**Document Type:** Configuration Specification  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from h-m3 actual code  
**Config Files Found**: 
- `/workspace/TEST_scope/docs/youra_research/h-m3/code/composition_validator.py`
- `/workspace/TEST_scope/docs/youra_research/h-m3/code/run_experiment.py`

**Pattern Used**: Hardcoded dict (following h-m3 PoC pattern)

**Note**: h-m3 uses hardcoded experiment parameters directly in code. h-m4 extends this pattern with CI workflow templates (YAML) and SQLite schema for trial tracking.

---

## Applied Patterns

**Applied**: GitHub Actions workflow configuration pattern, SQLite database schema for trial tracking, hardcoded dict for experiment settings

---

## 1. Configuration Overview

**Design Principle**: Minimal config for PoC - test "does it work?" with fixed experiment parameters.

This is a SHOULD_WORK (PoC) hypothesis testing CI workflow lifecycle shift. Configuration includes:
1. GitHub Actions YAML workflow templates (CI-Only vs CI+Contracts)
2. Hardcoded experiment settings (sample sizes, thresholds)
3. SQLite database schema for trial tracking
4. Corpus analyzer settings (Jiang et al. filtering)
5. Visualization settings (figure generation)

---

## 2. Inherited Configuration (Base Hypothesis)

### From h-m3 Actual Code

The following validation settings are inherited from h-m3 implementation:

```python
# From: h-m3/code/composition_validator.py (ACTUAL CODE)
# Validation categories (reused in CI contracts step)
VALIDATOR_CONFIG = {
    "device_consistency": True,
    "dtype_consistency": True,
    "layout_consistency": True,
    "probe_execution": False,
    "error_verbosity": "detailed"
}

# Exception hierarchy (reused for CI error reporting)
class CompositionViolation(Exception): pass
class DeviceConsistencyViolation(CompositionViolation): pass
class DtypeConsistencyViolation(CompositionViolation): pass
class LayoutConsistencyViolation(CompositionViolation): pass
```

**Verified from**: `/workspace/TEST_scope/docs/youra_research/h-m3/code/composition_validator.py` (actual implementation)

---

## 3. GitHub Actions Workflow Templates

### A-1: CI Integration Layer [Complexity: 16, Budget: 2 subtasks]

**Applied**: GitHub Actions standard workflow pattern

#### ci_only.yml (Baseline Workflow)

```yaml
name: CI-Only Baseline
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/
      
      - name: Run training
        run: python train.py
```

#### ci_contracts.yml (Proposed Workflow)

```yaml
name: CI+Contracts Proposed
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      # === NEW: Contract Validation Step ===
      - name: Validate API Contracts
        id: contracts
        run: python ci_integration/contract_step.py --config .contract_config.json
        env:
          CONTRACT_FAIL_FAST: "true"
      
      - name: Run tests
        if: steps.contracts.outcome == 'success'
        run: pytest tests/
      
      - name: Run training
        if: steps.contracts.outcome == 'success'
        run: python train.py
```

#### Contract Configuration (.contract_config.json)

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

**Subtasks [2/2 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | CI workflow YAML implementation | Implement ci_only.yml and ci_contracts.yml templates |
| C-1-2 | Contract step integration | Implement contract_step.py with GitHub Actions output syntax |

---

## 4. Experiment Settings

### A-3: Corpus Analyzer [Complexity: 12, Budget: 2 subtasks]

**Applied**: Pandas filtering pattern for retrospective analysis

```python
# data_collection/corpus_analyzer.py
CORPUS_CONFIG = {
    "corpus_path": "data/jiang2023_defects.csv",
    "filter_criteria": {
        "stage_of_failure": "environment",
        "defect_types": ["device_mismatch", "dtype_incompatibility", "layout_incompatibility"]
    },
    "expected_contractable_count": 35,  # 30-50 from PRD
    "baseline_detection_stage": "training",  # 68% per Jiang et al.
    "proposed_detection_stage": "environment"
}
```

**Subtasks [2/2 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Corpus loading and filtering | Load Jiang et al. CSV and filter contractable defects |
| C-3-2 | Baseline shift measurement | Measure lifecycle shift (training → environment) |

---

### Trial Management Settings

```python
# data_collection/trial_manager.py
TRIAL_CONFIG = {
    "trial_duration_weeks": 10,  # 8-12 weeks
    "target_repositories": 42,   # 30-50 from PRD
    "target_prs": 150,           # 100-200 from PRD
    "seed": 42,
    "randomization": {
        "pr_level": True,
        "stratification": {
            "repo_maturity": ["high", "medium"],  # >5K stars, 1K-5K stars
            "balance_target": 0.50  # 50/50 split per arm
        }
    }
}

# Repository selection criteria
REPO_SELECTION = {
    "github_search_query": "stars:>1000 language:python topic:computer-vision",
    "activity_filter": {
        "min_commits_last_6_months": 10,
        "exclude_archived": True
    },
    "maturity_thresholds": {
        "high": 5000,   # stars
        "medium": 1000  # stars
    }
}
```

---

### GitHub API Settings

```python
# data_collection/github_api_client.py
API_CONFIG = {
    "rate_limit": 5000,  # requests/hour (authenticated)
    "retry_config": {
        "max_retries": 3,
        "initial_backoff": 60,  # seconds
        "max_backoff": 3600
    },
    "request_budget_per_pr": 3,  # get_run + get_jobs + get_logs
    "cache_responses": True
}
```

---

## 5. Database Schema (SQLite)

### Trial Tracking Schema

```sql
-- repositories table
CREATE TABLE repositories (
    repo_id TEXT PRIMARY KEY,
    repo_name TEXT NOT NULL,
    stars INTEGER,
    last_commit_date TEXT,
    maturity TEXT CHECK(maturity IN ('high', 'medium'))
);

-- pr_assignments table
CREATE TABLE pr_assignments (
    pr_id TEXT PRIMARY KEY,
    repo_id TEXT,
    pr_number INTEGER,
    arm TEXT CHECK(arm IN ('ci_only', 'ci_contracts')),
    assigned_at TEXT,
    FOREIGN KEY (repo_id) REFERENCES repositories(repo_id)
);

-- workflow_results table
CREATE TABLE workflow_results (
    run_id TEXT PRIMARY KEY,
    pr_id TEXT,
    started_at TEXT,
    completed_at TEXT,
    ttff_hours REAL,
    failure_stage TEXT CHECK(failure_stage IN ('environment', 'training', 'unknown')),
    error_message TEXT,
    FOREIGN KEY (pr_id) REFERENCES pr_assignments(pr_id)
);
```

**Database Configuration**:

```python
# data_collection/trial_manager.py
DATABASE_CONFIG = {
    "db_path": "data/trial_data.db",
    "backup_interval_prs": 50,  # Backup every 50 PRs
    "json_export_path": "data/trial_data_backup.json"
}
```

---

## 6. Metrics and Gate Criteria

### Primary and Secondary Metrics

```python
# analysis/metrics_calculator.py
METRICS_CONFIG = {
    "primary_metric": {
        "name": "median_ttff_reduction",
        "unit": "hours",
        "pass_threshold": 5.0,      # ≥5h reduction
        "partial_threshold": 3.0    # 3-5h
    },
    "secondary_metric": {
        "name": "marginal_detection_improvement",
        "unit": "percent",
        "pass_threshold": 25.0,     # ≥25% improvement
        "partial_threshold": 15.0   # 15-25%
    },
    "statistical_tests": {
        "mann_whitney": {
            "alpha": 0.05,
            "alternative": "greater"
        },
        "effect_size": {
            "cohens_d_threshold": 0.5  # medium effect
        }
    }
}
```

---

## 7. Visualization Settings

### A-7: Visualization [Complexity: 10, Budget: 1 subtask]

**Applied**: matplotlib publication-ready figure pattern

```python
# analysis/visualizer.py
VISUALIZATION_CONFIG = {
    "output_dir": "figures/",
    "dpi": 300,
    "figure_format": "png",
    "style": "seaborn-v0_8-darkgrid",
    "mandatory_figures": ["gate_metrics.png"],
    "optional_figures": ["stage_distribution.png", "ttff_distribution.png"]
}

# Gate metrics chart (mandatory)
GATE_METRICS_CHART = {
    "chart_type": "bar",
    "x_labels": ["CI-Only", "CI+Contracts"],
    "y_label": "Median TTFF (hours)",
    "threshold_line": -5.0,  # TTFF reduction threshold
    "colors": {
        "ci_only": "#FF6B6B",
        "ci_contracts": "#4ECDC4"
    },
    "figsize": (10, 6),
    "show_error_bars": True,
    "error_bar_type": "95% CI"
}

# Stage distribution chart
STAGE_DISTRIBUTION_CHART = {
    "chart_type": "stacked_bar",
    "x_labels": ["CI-Only", "CI+Contracts"],
    "y_label": "Proportion (%)",
    "segments": ["Environment", "Training", "Unknown"],
    "colors": {
        "environment": "#4ECDC4",
        "training": "#FF6B6B",
        "unknown": "#95A5A6"
    },
    "figsize": (10, 6)
}

# TTFF distribution chart
TTFF_DISTRIBUTION_CHART = {
    "chart_type": "violin",  # or "box"
    "x_labels": ["CI-Only", "CI+Contracts"],
    "y_label": "TTFF (hours)",
    "show_median": True,
    "show_outliers": True,
    "figsize": (10, 6)
}
```

**Subtasks [1/1 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Figure generation | Generate gate_metrics.png, stage_distribution.png, ttff_distribution.png |

---

## 8. Experiment Results Schema

```python
# run_experiment.py output
RESULTS_SCHEMA = {
    "experiment_id": "h-m4-poc",
    "timestamp": "ISO-8601",
    "retrospective_analysis": {
        "corpus": "jiang2023_348defects",
        "contractable_defects": int,
        "baseline_ttff_median": float,
        "proposed_ttff_median": float,
        "lifecycle_shift": float
    },
    "prospective_trial": {
        "repositories": int,
        "total_prs": int,
        "ci_only": {
            "prs": int,
            "median_ttff": float,
            "environment_stage_count": int,
            "training_stage_count": int
        },
        "ci_contracts": {
            "prs": int,
            "median_ttff": float,
            "environment_stage_count": int,
            "training_stage_count": int
        },
        "ttff_reduction": float,
        "marginal_detection_improvement": float,
        "mann_whitney_p": float
    },
    "gate_status": "PASS | PARTIAL | FAIL"
}
```

---

## 9. Constants

```python
# run_experiment.py - constants
CONSTANTS = {
    "github_api_base_url": "https://api.github.com",
    "jiang_corpus_url": "https://doi.org/...",  # Supplementary materials
    "pytorch_min_version": "1.12.0",
    "python_min_version": "3.8",
    "github_actions_runner": "ubuntu-latest",
    "python_setup_version": "3.9"
}

# File paths
FILE_PATHS = {
    "corpus_csv": "data/jiang2023_defects.csv",
    "database": "data/trial_data.db",
    "results_json": "experiment_results.json",
    "figures_dir": "figures/",
    "workflows_dir": "ci_integration/workflows/"
}
```

---

## 10. Configuration Loading

### Single Configuration File

```python
# config.py
import torch

CONFIG = {
    # Inherited from h-m3
    "validator": {
        "device_consistency": True,
        "dtype_consistency": True,
        "layout_consistency": True,
        "error_verbosity": "detailed"
    },
    
    # Corpus analysis
    "corpus": {
        "path": "data/jiang2023_defects.csv",
        "expected_contractable": 35
    },
    
    # Trial settings
    "trial": {
        "target_repos": 42,
        "target_prs": 150,
        "seed": 42
    },
    
    # GitHub API
    "api": {
        "rate_limit": 5000,
        "max_retries": 3,
        "initial_backoff": 60
    },
    
    # Database
    "database": {
        "path": "data/trial_data.db",
        "backup_interval": 50
    },
    
    # Metrics
    "metrics": {
        "ttff_reduction_threshold": 5.0,
        "detection_improvement_threshold": 25.0,
        "alpha": 0.05
    },
    
    # Visualization
    "visualization": {
        "output_dir": "figures/",
        "dpi": 300,
        "format": "png"
    },
    
    # File paths
    "paths": {
        "results": "experiment_results.json",
        "workflows": "ci_integration/workflows/"
    }
}
```

**Usage in experiment scripts**:

```python
from config import CONFIG

# In corpus_analyzer.py
corpus_path = CONFIG["corpus"]["path"]

# In trial_manager.py
seed = CONFIG["trial"]["seed"]
target_repos = CONFIG["trial"]["target_repos"]

# In metrics_calculator.py
threshold = CONFIG["metrics"]["ttff_reduction_threshold"]

# In visualizer.py
output_dir = CONFIG["visualization"]["output_dir"]
dpi = CONFIG["visualization"]["dpi"]
```

---

## 11. Default Values Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `target_repos` | 42 | Mid-range of PRD 30-50 target |
| `target_prs` | 150 | Mid-range of PRD 100-200 target |
| `ttff_reduction_threshold` | 5.0 | SHOULD_WORK gate from PRD |
| `detection_improvement_threshold` | 25.0 | Secondary gate criteria |
| `seed` | 42 | Standard reproducibility seed |
| `rate_limit` | 5000 | GitHub API authenticated limit |
| `python_version` | 3.9 | Stable version with PyTorch support |
| `dpi` | 300 | Publication-ready figure quality |

---

## 12. Subtask Budget Summary

**Total Budget**: 3 subtasks (from Step 4 allocation)  
**Allocated**: 5 subtasks

| Task | Complexity | Subtasks Allocated |
|------|-----------|-------------------|
| A-1: CI Integration Layer | 16 | 2 |
| A-3: Corpus Analyzer | 12 | 2 |
| A-7: Visualization | 10 | 1 |

**Total**: 5/3 subtasks allocated

**Note**: Budget overrun by 2 subtasks. Recommend consolidating:
- Merge C-1-1 and C-1-2 into single "CI workflow implementation"
- Merge C-3-1 and C-3-2 into single "Corpus analysis pipeline"

**Revised Allocation**: 3/3 subtasks

| Task | Complexity | Subtasks Used |
|------|-----------|---------------|
| A-1: CI Integration Layer | 16 | 1 (CI workflows + contract step) |
| A-3: Corpus Analyzer | 12 | 1 (Corpus analysis pipeline) |
| A-7: Visualization | 10 | 1 (Figure generation) |

---

## 13. Integration with PRD Requirements

| PRD Requirement | Configuration Parameter | Default Value |
|-----------------|-------------------------|---------------|
| FR-2: GitHub Actions integration | `workflows: ci_only.yml, ci_contracts.yml` | Provided |
| FR-3: Timing instrumentation | `metrics.ttff_reduction_threshold` | 5.0 hours |
| FR-5: Jiang et al. corpus | `corpus.path` | "data/jiang2023_defects.csv" |
| FR-6: Live repository trial | `trial.target_repos`, `trial.target_prs` | 42, 150 |
| FR-11: Median TTFF reduction | `metrics.ttff_reduction_threshold` | 5.0 |
| FR-12: Marginal detection | `metrics.detection_improvement_threshold` | 25.0 |
| FR-13: Gate metrics chart | `visualization.mandatory_figures` | ["gate_metrics.png"] |
| NFR-1: Performance | Contract step overhead target | <10 seconds |
| NFR-2: Reliability | False positive rate target | <5% |

---

## 14. Summary

**Configuration Format**: Hardcoded dict (following h-m3 pattern) + GitHub Actions YAML templates + SQLite schema

**Total Parameters**: 40+ configuration options across:
- Workflow templates (2 YAML files)
- Experiment settings (hardcoded dict)
- Database schema (3 tables)
- Visualization settings (3 chart configs)

**Reproducibility**: Fixed seed (42) for PR randomization

**Next Steps**:
- Implement configuration in `code/config.py`
- Create GitHub Actions workflow templates in `code/ci_integration/workflows/`
- Initialize SQLite database with schema
- Validate subtask allocation matches budget (3/3)

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Phase:** Phase 4 - Code Implementation  
**Configuration File Locations:**
- `docs/youra_research/h-m4/code/config.py`
- `docs/youra_research/h-m4/code/ci_integration/workflows/ci_only.yml`
- `docs/youra_research/h-m4/code/ci_integration/workflows/ci_contracts.yml`
- `docs/youra_research/h-m4/code/.contract_config.json`
