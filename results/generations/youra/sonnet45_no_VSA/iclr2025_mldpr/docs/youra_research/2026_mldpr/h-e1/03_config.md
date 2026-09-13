# Configuration: H-E1 - Documentation Gap Validation Study

**Date:** 2026-07-12  
**Hypothesis:** H-E1 (EXISTENCE - FOUNDATION)  
**Type:** Observational Study Configuration  
**Author:** Configuration Agent  
**Status:** DRAFT v1.0  

---

## Codebase Analysis (Serena)

**Project Type:** Green-field  
**Status:** New implementation from scratch - first temporal documentation measurement study  
**Config Files Found:** None - new config design  
**Pattern Used:** Hardcoded dict (Python constants)  

---

## Applied Patterns

**Applied:** Data Pipeline Configuration Pattern (ETL observational studies)

---

## E-2: Manual Coding Infrastructure [Complexity: 9, Budget: 1]

### Configuration (Hardcoded Dict)

```python
# DCS Rubric Configuration
DCS_CODING_CONFIG = {
    'threshold': 2.4,
    'components': ['data_context', 'preprocessing', 'licensing'],
    'dual_code_percentage': 0.20,
    'template_output': './notebooks/manual_coding_template.xlsx',
    'coding_results_file': './data/dcs_coding_results.csv',
    'dual_coded_file': './data/dcs_dual_coded_sample.csv'
}

# DCS Rubric Scoring
DCS_RUBRIC = {
    'data_context': {
        'score_0': 'No mention of data sources or collection methodology',
        'score_0.5': 'Partial mention (sources OR methodology)',
        'score_1.0': 'Clear description of both sources AND methodology'
    },
    'preprocessing': {
        'score_0': 'No documentation of cleaning, augmentation, or splits',
        'score_0.5': 'Partial documentation (1-2 aspects)',
        'score_1.0': 'Comprehensive (cleaning + augmentation + splits)'
    },
    'licensing': {
        'score_0': 'No license file or statement',
        'score_0.5': 'License mentioned in README but no LICENSE file',
        'score_1.0': 'Clear LICENSE file or SPDX identifier'
    }
}

# Template Generation
TEMPLATE_CONFIG = {
    'header_instructions': True,
    'example_rows': 3,
    'auto_calculate_total': True,
    'columns': ['repo_id', 'dcs_data_context', 'dcs_preprocessing', 'dcs_licensing', 'dcs_3_total', 'compliant', 'notes']
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | DCS Template Generator | Create Excel template with rubric instructions and validation formulas |

---

## E-3: Statistical Analysis Engine [Complexity: 12, Budget: 1]

### Configuration (Hardcoded Dict)

```python
# Statistical Testing Configuration
STATISTICAL_CONFIG = {
    'alpha': 0.05,
    'ci_method': 'wilson',
    'ci_level': 0.95,
    'h0_threshold': 0.70,
    'h1_prediction': 0.40,
    'gate_threshold': 0.60,
    'irr_threshold': 0.70,
    'random_seed': 42
}

# Hypothesis Testing
HYPOTHESIS_TEST_CONFIG = {
    'null_hypothesis': 'π ≥ 0.70',
    'alternative_hypothesis': 'π < 0.70',
    'test_type': 'binomial_proportion',
    'one_sided': True
}

# Component Analysis
COMPONENT_TEST_CONFIG = {
    'test_type': 'chi_square_goodness_of_fit',
    'expected_distribution': 'uniform',
    'alpha': 0.05,
    'component_threshold': 0.5
}

# Inter-Rater Reliability
IRR_CONFIG = {
    'metric': 'cohen_kappa',
    'min_kappa': 0.70,
    'dual_code_sample_size': 20,
    'random_seed': 42
}

# Gate Criteria
GATE_CRITERIA = {
    'primary': {
        'metric': 'ci_upper_bound',
        'threshold': 0.60,
        'direction': 'less_than',
        'required': True
    },
    'secondary': {
        'metric': 'chi_square_p_value',
        'threshold': 0.05,
        'direction': 'less_than',
        'required': True
    },
    'quality': {
        'metric': 'kappa',
        'threshold': 0.70,
        'direction': 'greater_equal',
        'required': True
    }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Statistical Engine Core | Implement binomial CI, chi-square, Cohen's kappa, and gate validation |

---

## E-5: Pipeline Orchestration [Complexity: 11, Budget: 2]

### Configuration (Hardcoded Dict)

```python
# Pipeline Phase Control
PIPELINE_CONFIG = {
    'phases': ['sampling', 't0_detection', 'cloning', 'manual_coding', 'analysis'],
    'checkpoint_dir': './data/checkpoints',
    'resume_from_checkpoint': True,
    'validate_each_phase': True
}

# Sampling Phase
SAMPLING_CONFIG = {
    'start_date': '2022-01-01',
    'end_date': '2024-12-31',
    'min_stars': 10,
    'sample_size': 120,
    'n_per_year': 40,
    'random_seed': 42,
    'output_file': './data/sampled_repositories.csv'
}

# T0 Detection Phase
T0_DETECTION_CONFIG = {
    'tier1_preference': True,
    'tier2_fallback': True,
    'tier3_last_resort': True,
    'dataset_commit_patterns': ['add dataset', 'upload data', 'initial commit', 'first commit'],
    'min_success_rate': 0.95,
    'output_file': './data/t0_detection_results.csv'
}

# Cloning Phase
CLONING_CONFIG = {
    'base_dir': './data/repos',
    't0_offset_days': 90,
    'verify_readme': True,
    'min_success_rate': 0.98,
    'retry_attempts': 3,
    'retry_delay_seconds': 5
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': './logs/pipeline.log',
    'console': True,
    'file_mode': 'a'
}

# Error Handling
ERROR_CONFIG = {
    'max_retries': 3,
    'backoff_factor': 2,
    'timeout_seconds': 60,
    'continue_on_api_error': True,
    'save_failed_items': True
}

# API Configuration
API_CONFIG = {
    'github_token_env': 'GITHUB_TOKEN',
    'hf_token_env': 'HF_TOKEN',
    'rate_limit_buffer': 100,
    'request_timeout': 30
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Pipeline Orchestrator | Coordinate 5 phases with checkpoint/resume capability |
| C-5-2 | Error Handler & Logger | Implement retry logic, API error handling, and progress logging |

---

## E-6: Quality Validation [Complexity: 9, Budget: 2]

### Configuration (Hardcoded Dict)

```python
# Validation Gates
VALIDATION_CONFIG = {
    't0_detection_success_rate': 0.95,
    'cloning_success_rate': 0.98,
    'manual_coding_completion': 1.00,
    'irr_kappa_threshold': 0.70,
    'ci_upper_bound_threshold': 0.60,
    'chi_square_p_threshold': 0.05
}

# Test Configuration
TEST_CONFIG = {
    'test_framework': 'pytest',
    'coverage_threshold': 0.80,
    'mock_data_seed': 42,
    'integration_test_sample_size': 10
}

# Mock Data Generation
MOCK_DATA_CONFIG = {
    'n_repos': 10,
    'compliant_rate': 0.40,
    'component_scores': {
        'data_context': [0.0, 0.5, 1.0],
        'preprocessing': [0.0, 0.5, 1.0],
        'licensing': [0.0, 0.5, 1.0]
    },
    'random_seed': 42
}

# Gate Validation
GATE_VALIDATION_CONFIG = {
    'pass_scenario': {
        'ci_upper': 0.55,
        'chi_square_p': 0.02,
        'kappa': 0.75,
        'expected_result': 'PASS'
    },
    'fail_scenario': {
        'ci_upper': 0.65,
        'chi_square_p': 0.12,
        'kappa': 0.65,
        'expected_result': 'FAIL'
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Unit Test Suite | Test sampling, T0 detection, and statistical modules |
| C-6-2 | Gate Validation Logic | Verify gate criteria with synthetic pass/fail scenarios |

---

## Visualization Configuration [E-4: Not Allocated Subtasks]

```python
# Visualization Settings
VISUALIZATION_CONFIG = {
    'output_dir': './docs/youra_research/h-e1/figures',
    'dpi': 300,
    'format': 'png',
    'style': 'seaborn-v0_8-whitegrid',
    'figsize_bar': (8, 6),
    'figsize_stacked': (10, 6),
    'figsize_pie': (7, 7),
    'figsize_hist': (9, 6),
    'font_size': 11,
    'title_size': 13,
    'save_params': {
        'bbox_inches': 'tight',
        'pad_inches': 0.1
    }
}

# Required Figures
REQUIRED_FIGURES = {
    'compliance_rate': {
        'filename': 'compliance_rate.png',
        'type': 'bar',
        'title': 'Compliance Rate vs H0/H1 Thresholds',
        'x_categories': ['H0: 70%', 'H1: 40%', 'Observed'],
        'reference_lines': [0.60, 0.70],
        'show_ci': True
    },
    'component_breakdown': {
        'filename': 'component_breakdown.png',
        'type': 'stacked_bar',
        'title': 'DCS Component Score Distribution',
        'x_labels': ['Data Context', 'Preprocessing', 'Licensing'],
        'stack_labels': ['Score: 0', 'Score: 0.5', 'Score: 1.0'],
        'colors': ['#d62728', '#ff7f0e', '#2ca02c']
    },
    't0_detection_breakdown': {
        'filename': 't0_detection_breakdown.png',
        'type': 'pie',
        'title': 'T0 Detection Method Distribution',
        'labels': ['Tier 1: Release Tags', 'Tier 2: Dataset Commits', 'Tier 3: Repo Creation']
    },
    'dcs_distribution': {
        'filename': 'dcs_distribution.png',
        'type': 'histogram',
        'title': 'DCS_3 Score Distribution',
        'bins': 6,
        'threshold_line': 2.4,
        'x_label': 'DCS_3 Total Score',
        'y_label': 'Frequency'
    }
}
```

---

## Data Collection Configuration [E-1: Not Allocated Subtasks]

```python
# HuggingFace API
HUGGINGFACE_CONFIG = {
    'api_endpoint': 'HfApi().list_datasets()',
    'filter_type': 'dataset',
    'date_field': 'created_at',
    'likes_field': 'likes',
    'rate_limit_delay': 0.5
}

# GitHub API
GITHUB_CONFIG = {
    'api_endpoint': 'Github().get_repo()',
    'rate_limit': 5000,
    'rate_limit_buffer': 100,
    'backoff_strategy': 'exponential',
    'backoff_base': 2,
    'max_retries': 5
}

# File Extraction
FILE_EXTRACTION_CONFIG = {
    'required_files': ['README.md', 'LICENSE'],
    'optional_files': ['DATASET_CARD.md', '.huggingface.yaml'],
    'markdown_extensions': ['.md', '.markdown'],
    'search_depth': 1
}
```

---

## Experiment Metadata

```python
# Study Metadata
EXPERIMENT_CONFIG = {
    'hypothesis_id': 'h-e1',
    'study_type': 'observational',
    'start_date': '2026-07-12',
    'output_dir': './docs/youra_research/h-e1',
    'results_file': './data/final_results.json',
    'validation_report': '04_validation.md',
    'timestamp_format': '%Y-%m-%d %H:%M:%S',
    'random_seed': 42
}

# Report Structure
REPORT_SECTIONS = [
    'executive_summary',
    'sampling_results',
    't0_detection_summary',
    'cloning_summary',
    'manual_coding_summary',
    'statistical_results',
    'gate_evaluation',
    'visualizations',
    'conclusions'
]

# Phase Outputs
PHASE_OUTPUTS = {
    'phase1_sampling': './data/sampled_repositories.csv',
    'phase2_t0_detection': './data/t0_detection_results.csv',
    'phase3_cloning': './data/repos/',
    'phase4_manual_coding': './data/dcs_coding_results.csv',
    'phase4_dual_coding': './data/dcs_dual_coded_sample.csv',
    'phase5_analysis': './data/final_results.json',
    'phase5_figures': './docs/youra_research/h-e1/figures/'
}
```

---

## Configuration Consolidation

For implementation convenience, all configurations can be loaded from a single file:

```python
# src/config.py
"""
Complete configuration for H-E1 observational study.
All configuration constants consolidated in one module.
"""

# Import all config dicts defined above
# Phase 4 Coder: Copy-paste the configuration blocks as needed

# Usage example:
# from config import STATISTICAL_CONFIG, GATE_CRITERIA
# alpha = STATISTICAL_CONFIG['alpha']
# ci_method = STATISTICAL_CONFIG['ci_method']
```

---

## Self-Validation

### Brevity Checks
- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: Data Pipeline Configuration Pattern")
- [x] Rationale only for non-standard values (all values are standard for observational studies)
- [x] Subtask count within budget (6 total: E-2=1, E-3=1, E-5=2, E-6=2)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included

### Serena MCP Validation
- [x] Green-field project → Serena skip is acceptable
- [x] "Codebase Analysis (Serena)" section included with status

### Content Completeness
- [x] Configurations for all allocated tasks (E-2, E-3, E-5, E-6)
- [x] Default values for all parameters
- [x] Statistical test thresholds
- [x] Pipeline orchestration settings
- [x] Quality validation gates
- [x] Subtask breakdown matches budget

---

**Document Version:** 1.0  
**Next Phase:** Phase 4 - Implementation (Coder Agent)  
**Config Subtasks:** 6/6 allocated  
**Format:** Hardcoded Python dictionaries (copy-paste ready)
