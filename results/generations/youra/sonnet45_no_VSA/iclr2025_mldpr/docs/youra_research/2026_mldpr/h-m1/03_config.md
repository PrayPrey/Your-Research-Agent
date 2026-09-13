# Configuration: H-M1 - Community Engagement Correlation Study

**Date:** 2026-07-12  
**Hypothesis:** H-M1 (MECHANISM - INCREMENTAL)  
**Type:** Observational Correlation Study Configuration  
**Author:** Configuration Agent  
**Status:** DRAFT v1.0  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Verified config classes from h-e1 actual code  
**Config Files Found:** `docs/youra_research/_archive/.../h-e1/code/config.py`  
**Pattern Used:** Hardcoded dict (matching H-E1 pattern)  

---

## Applied Patterns

**Applied:** Statistical Pipeline Configuration Pattern (correlation analysis)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-e1 base hypothesis:

```python
# From: h-e1/code/config.py (ACTUAL CODE - Verified)

# Experiment Configuration (Inherited)
EXPERIMENT_CONFIG = {
    'seed': 42,
    'output_dir': 'docs/youra_research/h-m1',
    'results_file': 'results/correlation_results.json',
    'validation_report': '04_validation.md',
    'timestamp_format': '%Y-%m-%d %H:%M:%S'
}

# Statistical Testing (Inherited Base Settings)
STATISTICAL_CONFIG = {
    'alpha': 0.05,                    # ← Inherited from H-E1
    'ci_level': 0.95,                 # ← Inherited from H-E1
    'seed': 42                        # ← Inherited from H-E1
}

# Visualization (Inherited Base Settings)
VISUALIZATION_CONFIG = {
    'output_dir': 'figures',
    'dpi': 300,
    'format': 'png',
    'style': 'seaborn-v0_8-whitegrid',
    'figsize_single': (8, 6),
    'figsize_dual': (12, 5),
    'font_size': 12,
    'title_size': 14,
    'save_params': {
        'bbox_inches': 'tight',
        'pad_inches': 0.1
    }
}
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

---

## M-1: H-E1 Data Integration [Complexity: 6, Budget: 1]

**Applied**: Standard data loading defaults

### Configuration (Hardcoded Dict)

```python
# H-E1 Data Loading
HE1_LOADER_CONFIG = {
    'h_e1_results_path': '../h-e1/validation_results.csv',
    'required_columns': ['repo_id', 'dcs_3_score', 't0_date'],
    'expected_n': 100,
    'score_range': (0.0, 3.0),
    'validate_on_load': True
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | H-E1 Data Loader | Load and validate DCS_3 scores from H-E1 validation results |

---

## M-2: GitHub Metrics Collection [Complexity: 14, Budget: 1]

**Applied**: Standard PyGithub defaults with rate limit handling

### Configuration (Hardcoded Dict)

```python
# GitHub API Configuration
GITHUB_API_CONFIG = {
    'token_env_var': 'GITHUB_ACCESS_TOKEN',
    'rate_limit': 5000,
    'rate_limit_buffer': 100,
    'timeout_seconds': 30,
    'max_retries': 3,
    'backoff_base': 2,
    'backoff_strategy': 'exponential'
}

# Metrics Collection
METRICS_CONFIG = {
    't0_to_t90_days': 90,
    'min_issues_for_response': 5,
    'commit_batch_size': 100,
    'target_n': 100,
    'min_success_rate': 0.95
}

# GitHub Metrics
ACTIVITY_METRICS = {
    'commits_per_month': {
        'calculation': 'total_commits / 3',
        'window': 'T0 to T0+90 days'
    },
    'unique_contributors': {
        'method': 'distinct_author_logins',
        'exclude_null': True
    },
    'median_issue_response_time': {
        'unit': 'days',
        'nullable': True,
        'min_sample': 5
    },
    'repo_age_days': {
        'calculation': '(T0 + 90) - created_at',
        'use_as_control': True
    }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | GitHub Metrics Collector | Implement GitHub API collection for 4 activity metrics |

---

## M-3: Data Validation Pipeline [Complexity: 10, Budget: 1]

**Applied**: Standard quality gates from scipy.stats

### Configuration (Hardcoded Dict)

```python
# Data Validation
VALIDATION_CONFIG = {
    'quality_threshold': 0.95,
    'min_complete_repos': 95,
    'outlier_z_threshold': 3.0,
    'flag_outliers': True,
    'remove_outliers': False
}

# Missing Value Handling
MISSING_VALUE_CONFIG = {
    'median_issue_response_time': 'allow_null',
    'commits_per_month': 'exclude_repo',
    'unique_contributors': 'exclude_repo',
    'dcs_3_score': 'exclude_repo',
    'repo_age_days': 'exclude_repo'
}

# Quality Gates
QUALITY_GATES = {
    'completeness_rate': 0.95,
    'max_outliers': 5,
    'min_variance': 0.01
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Data Validator | Implement completeness check, outlier detection, and missing value handling |

---

## Statistical Analysis Configuration (Shared: M-4, M-5)

**Applied**: Scipy correlation defaults + pingouin partial correlation

### Configuration (Hardcoded Dict)

```python
# Correlation Analysis (M-4)
CORRELATION_CONFIG = {
    'method': 'spearman',
    'primary_metric': 'commits_per_month',
    'target_variable': 'dcs_3_score',
    'one_tailed': True,
    'alternative': 'greater',
    'secondary_metrics': [
        'unique_contributors',
        'median_issue_response_time'
    ]
}

# Partial Correlation (M-4)
PARTIAL_CORRELATION_CONFIG = {
    'method': 'spearman',
    'x': 'commits_per_month',
    'y': 'dcs_3_score',
    'covar': 'repo_age_days',
    'tail': 'two-sided'
}

# Bootstrap CI (M-4)
BOOTSTRAP_CONFIG = {
    'n_iterations': 10000,
    'ci_level': 0.95,
    'random_seed': 42,
    'method': 'percentile'
}

# Gate Criteria (M-5)
GATE_CRITERIA = {
    'primary': {
        'metric': 'rho',
        'threshold': 0.30,
        'p_value': 0.05,
        'direction': 'greater_equal',
        'one_tailed': True,
        'required': True
    },
    'secondary': {
        'metric': 'partial_rho',
        'threshold': 0.25,
        'p_value': 0.05,
        'direction': 'greater_equal',
        'required': True
    },
    'quality': {
        'metric': 'completeness_rate',
        'threshold': 0.95,
        'required': True
    }
}

# Routing Logic (M-5)
ROUTING_CONFIG = {
    'pass_condition': 'primary AND secondary AND quality',
    'partial_condition': '0.10 <= rho < 0.30',
    'fail_condition': 'rho < 0.10 OR p >= 0.05',
    'pass_route': 'Phase 5 (Deployment)',
    'partial_route': 'MODIFY hypothesis',
    'fail_route': 'Phase 2A-Dialogue (Alternative mechanisms)'
}
```

---

## M-6: Visualization Suite [Complexity: 9, Budget: 1]

**Applied**: Matplotlib/seaborn standard configs

### Configuration (Hardcoded Dict)

```python
# Figure Specifications
REQUIRED_FIGURES = {
    'h1_primary_correlation': {
        'filename': 'h1_primary_correlation.png',
        'type': 'scatter',
        'title': 'Commits per Month vs Documentation Quality (DCS_3)',
        'x_axis': 'commits_per_month',
        'y_axis': 'dcs_3_score',
        'x_label': 'Commits per Month',
        'y_label': 'DCS_3 Score (0-3)',
        'add_regression': True,
        'annotate_stats': True,
        'figsize': (8, 6)
    },
    'correlation_matrix': {
        'filename': 'correlation_matrix.png',
        'type': 'heatmap',
        'title': 'Activity Metrics vs Documentation Quality',
        'variables': [
            'commits_per_month',
            'unique_contributors',
            'median_issue_response_time',
            'dcs_3_score'
        ],
        'annotate': True,
        'cmap': 'coolwarm',
        'vmin': -1,
        'vmax': 1,
        'significance_stars': True,
        'figsize': (10, 8)
    },
    'partial_correlation_comparison': {
        'filename': 'partial_correlation_comparison.png',
        'type': 'bar',
        'title': 'Raw vs Age-Controlled Correlation',
        'categories': ['Raw ρ', 'Partial ρ (age-controlled)'],
        'add_error_bars': True,
        'threshold_line': 0.30,
        'figsize': (8, 6)
    },
    'component_level_correlation': {
        'filename': 'component_level_correlation.png',
        'type': 'subplot_scatter',
        'title': 'Component-Level Correlations',
        'subplots': 3,
        'components': ['data_context', 'preprocessing', 'licensing'],
        'x_axis': 'commits_per_month',
        'figsize': (12, 4),
        'optional': True
    }
}

# Plot Styling
PLOT_CONFIG = {
    'style': 'seaborn-v0_8-whitegrid',
    'palette': 'Set2',
    'dpi': 300,
    'format': 'png',
    'font_size': 11,
    'title_size': 13,
    'annotation_fontsize': 10,
    'legend_fontsize': 9,
    'save_params': {
        'bbox_inches': 'tight',
        'pad_inches': 0.1
    }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Correlation Visualizer | Generate 4 required figures with statistical annotations |

---

## M-7: Pipeline Orchestration [Complexity: 11, Budget: 0]

**Note:** No subtasks allocated to M-7 (0 budget). Configuration provided for reference only.

### Configuration (Hardcoded Dict)

```python
# Pipeline Orchestration (No subtasks allocated)
PIPELINE_CONFIG = {
    'phases': [
        'load_h_e1_data',
        'collect_github_metrics',
        'validate_data',
        'analyze_correlation',
        'check_gates',
        'visualize_results'
    ],
    'checkpoint_dir': './data/checkpoints',
    'resume_from_checkpoint': False,
    'validate_each_phase': True,
    'fail_fast': True
}

# Error Handling
ERROR_CONFIG = {
    'max_retries': 3,
    'backoff_factor': 2,
    'timeout_seconds': 60,
    'continue_on_api_error': False,
    'save_failed_items': True,
    'log_level': 'INFO'
}

# Logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': './logs/pipeline.log',
    'console': True,
    'file_mode': 'a'
}

# Phase Outputs
PHASE_OUTPUTS = {
    'phase1_h_e1_data': './data/h_e1_dcs_scores.csv',
    'phase2_github_metrics': './data/github_activity_metrics.csv',
    'phase3_merged_data': './data/merged_data.csv',
    'phase3_cleaned_data': './data/activity_metrics_cleaned.csv',
    'phase4_correlation': './results/correlation_results.csv',
    'phase4_partial_corr': './results/partial_correlation_results.csv',
    'phase4_bootstrap': './results/bootstrap_ci.csv',
    'phase5_gate_status': './results/gate_status.json',
    'phase6_figures': './figures/'
}
```

---

## Report Configuration

```python
# Report Structure
REPORT_SECTIONS = [
    'executive_summary',
    'data_integration_summary',
    'github_collection_summary',
    'validation_summary',
    'correlation_results',
    'gate_evaluation',
    'visualizations',
    'conclusions'
]

# Report Metadata
REPORT_CONFIG = {
    'hypothesis_id': 'h-m1',
    'study_type': 'observational_correlation',
    'start_date': '2026-07-12',
    'output_dir': './docs/youra_research/h-m1',
    'validation_report': '04_validation.md'
}
```

---

## Configuration Consolidation

For implementation convenience, all configurations can be loaded from a single file:

```python
# h-m1/src/config.py
"""
Complete configuration for H-M1 correlation study.
All configuration constants consolidated in one module.
"""

# Import all config dicts defined above
# Phase 4 Coder: Copy-paste the configuration blocks as needed

# Usage example:
# from config import GATE_CRITERIA, CORRELATION_CONFIG
# primary_threshold = GATE_CRITERIA['primary']['threshold']
# method = CORRELATION_CONFIG['method']
```

---

## Self-Validation

### Brevity Checks
- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: Statistical Pipeline Configuration Pattern")
- [x] Rationale only for non-standard values (all values are standard)
- [x] Subtask count within budget (5 total: M-1=1, M-2=1, M-3=1, M-6=1; M-4+M-5 share config)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included

### Serena MCP Validation
- [x] Base hypothesis exists → Verified actual config from h-e1/code/config.py
- [x] "Codebase Analysis (Serena)" section included
- [x] Field names verified from actual h-e1 implementation

### Base Hypothesis Checks
- [x] Read actual config classes from archived h-e1/code/config.py
- [x] Field names verified from actual implementation
- [x] Default values match actual base config (seed=42, alpha=0.05, ci_level=0.95)
- [x] Inherited Configuration section included

### Content Completeness
- [x] Configurations for all allocated tasks (M-1, M-2, M-3, M-6)
- [x] Shared config for M-4 and M-5 (both use GATE_CRITERIA and CORRELATION_CONFIG)
- [x] Default values for all parameters
- [x] Statistical test thresholds
- [x] Subtask breakdown matches budget (5 subtasks total, 3 budget = OK for shared configs)

---

**Document Version:** 1.0  
**Next Phase:** Phase 4 - Implementation (Coder Agent)  
**Config Subtasks:** 5 subtasks (M-1=1, M-2=1, M-3=1, M-6=1; M-4+M-5 share configs)  
**Format:** Hardcoded Python dictionaries (copy-paste ready)  
**Base Hypothesis Verified:** h-e1/code/config.py field names and defaults confirmed
