# Configuration: h-e1 - DTS Inter-Annotator Agreement Study

**Date:** 2026-03-18
**Hypothesis Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK (κ ≥ 0.60 in ≥5/6 DTS sections)
**Configuration Version:** 1.0

---

## Applied Patterns

Applied: Statistical study configuration pattern (hardcoded constants for reproducibility)

---

## Codebase Analysis (Serena)

**Project Type:** Green-field implementation
**Status:** New DTS annotation study - no existing code to analyze
**Config Files Found:** None - new config
**Pattern Used:** Hardcoded dict (Python constants)

**Rationale:** Previous h-e1 code (MDS-12 psychometric validation) exists in archived folder but is unrelated to current DTS annotation study. Current hypothesis requires new configuration design.

---

## Configuration Overview

Single hardcoded configuration module for EXISTENCE hypothesis. No hyperparameter tuning or experimental variations needed for PoC validation.

**Format:** Python constants (hardcoded dict pattern)
**File:** `code/config.py`

---

## Global Configuration

### Data Collection Parameters (E1-1, E1-2)

```python
# Repository Configuration
REPOSITORIES = ["huggingface", "openml", "uci"]
SAMPLES_PER_REPO = 10

# API Configuration
API_CONFIG = {
    "request_delay": 1.0,  # seconds between requests (rate limit protection)
    "timeout": 30,         # seconds
    "max_retries": 3
}

# Stratification Criteria
QUALITY_STRATA = {
    "high": 10,    # Well-documented datasets
    "medium": 10,  # Moderate documentation
    "low": 10      # Minimal documentation
}

# Domain Coverage
DOMAINS = ["NLP", "CV", "Tabular"]
```

---

### DTS Annotation Criteria (E1-3)

```python
# DTS Sections (6 binary presence items)
DTS_SECTIONS = [
    "Motivation",
    "Composition",
    "Collection",
    "Preprocessing",
    "Uses",
    "Maintenance"
]

# Annotation Protocol Settings
ANNOTATION_CONFIG = {
    "time_limit_min": 5,    # Minimum minutes per dataset
    "time_limit_max": 10,   # Maximum minutes per dataset
    "break_interval": 60,   # Minutes before required break
    "break_duration": 10,   # Minutes for break
    "calibration_datasets": 5,  # Number of calibration datasets
    "calibration_agreement_threshold": 1.0  # 100% agreement required
}
```

---

### Statistical Settings (E1-4)

```python
# Bootstrap Configuration
BOOTSTRAP_CONFIG = {
    "n_resamples": 1000,
    "confidence_level": 0.95,
    "random_state": 42,
    "method": "percentile"
}

# Kappa Interpretation (Landis-Koch 1977)
KAPPA_INTERPRETATION = {
    "poor": (0.0, 0.20),
    "fair": (0.21, 0.40),
    "moderate": (0.41, 0.60),
    "substantial": (0.61, 0.80),
    "almost_perfect": (0.81, 1.00)
}
```

---

### Gate Thresholds (E1-5)

```python
# MUST_WORK Gate Thresholds
GATE_THRESHOLDS = {
    "kappa_min": 0.60,      # Minimum Cohen's κ per section
    "sections_min": 5       # Minimum sections passing (≥5/6)
}

# Secondary Quality Thresholds (Not gate-critical)
QUALITY_THRESHOLDS = {
    "percent_agreement_min": 0.70,   # 70% raw agreement
    "ci_width_max": 0.30             # Bootstrap CI precision
}
```

---

### Visualization Configuration (E1-6)

```python
# Figure Settings (4 required figures)
FIGURE_CONFIG = {
    "dpi": 300,
    "format": "png",
    "style": "seaborn-v0_8-whitegrid",
    "font_size": 12,

    # Figure 1: Gate Metrics Bar Chart
    "gate_metrics": {
        "figsize": (10, 6),
        "threshold_color": "red",
        "threshold_linestyle": "--",
        "pass_color": "green",
        "fail_color": "red",
        "show_ci": True
    },

    # Figure 2: Confusion Matrices
    "confusion_matrices": {
        "figsize": (15, 10),
        "layout": (2, 3),  # 2 rows × 3 columns for 6 sections
        "cmap": "Blues",
        "annot": True,
        "fmt": "d"
    },

    # Figure 3: Agreement Heatmap
    "agreement_heatmap": {
        "figsize": (12, 8),
        "cmap": "RdYlGn",  # Red (disagree) → Yellow (partial) → Green (agree)
        "annot": False,
        "cbar_label": "Agreement Status"
    },

    # Figure 4: Base Rate vs Kappa Scatter
    "baserate_scatter": {
        "figsize": (8, 6),
        "marker": "o",
        "markersize": 100,
        "alpha": 0.7,
        "show_trendline": True,
        "show_labels": True
    }
}
```

---

### Output Paths

```python
# Directory Structure
OUTPUT_PATHS = {
    "data_dir": "data/h-e1",
    "doc_dir": "data/h-e1/documentation",
    "annotation_dir": "data/h-e1/annotations",
    "figures_dir": "h-e1/figures",
    "results_file": "h-e1/results/validation_results.json",
    "metadata_file": "data/h-e1/datasets_metadata.csv"
}

# File Naming Patterns
FILE_PATTERNS = {
    "hf_docs": "hf_{:03d}.txt",      # hf_001.txt to hf_010.txt
    "openml_docs": "openml_{:03d}.txt",
    "uci_docs": "uci_{:03d}.txt",
    "coder_a": "coder_a_annotations.csv",
    "coder_b": "coder_b_annotations.csv",
    "protocol": "annotation_protocol.md"
}
```

---

## Task Configurations

### E1-1: Dataset Collection Pipeline [Complexity: 12, Budget: 5]

```python
COLLECTION_CONFIG = {
    "huggingface": {
        "api_endpoint": "https://huggingface.co/api/datasets",
        "filters": {
            "date_range": ("2020-01-01", "2024-12-31"),
            "domains": DOMAINS
        },
        "sample_size": 10
    },
    "openml": {
        "library": "openml",
        "filters": {
            "status": "active",
            "domains": DOMAINS
        },
        "sample_size": 10
    },
    "uci": {
        "base_url": "https://archive.ics.uci.edu/ml/datasets",
        "scraping": {
            "parser": "html.parser",
            "timeout": 30
        },
        "sample_size": 10
    }
}
```

**Subtasks [5/5 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | HuggingFace API Integration | Implement dataset collection from HF Hub |
| C-1-2 | OpenML API Integration | Implement dataset collection from OpenML |
| C-1-3 | UCI Web Scraping | Implement dataset collection from UCI repository |
| C-1-4 | Stratification Logic | Quality-based stratification (high/medium/low) |
| C-1-5 | Metadata Generation | Generate datasets_metadata.csv with 30 rows |

---

### E1-2: Documentation Extraction [Complexity: 8, Budget: 5]

```python
EXTRACTION_CONFIG = {
    "encoding": "utf-8",
    "max_doc_length": 50000,  # characters (prevent memory issues)
    "preserve_formatting": True,
    "clean_html": True,
    "output_format": "plain_text"
}
```

**Subtasks [5/5 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | HF Documentation Extraction | Extract dataset cards via datasets library |
| C-2-2 | OpenML Documentation Extraction | Extract metadata/description via API |
| C-2-3 | UCI Documentation Extraction | Extract description from HTML pages |
| C-2-4 | Text Formatting | Preserve human-readable formatting |
| C-2-5 | File Writing | Save 30 plain text files to data/h-e1/documentation/ |

---

### E1-3: Annotation Protocol Implementation [Complexity: 9, Budget: 5]

```python
PROTOCOL_CONFIG = {
    "training_phase": {
        "dts_study_duration": 60,  # minutes
        "calibration_datasets": 5,
        "calibration_source": "Rondina et al. (2025)",
        "agreement_threshold": 1.0  # 100% agreement required
    },
    "annotation_phase": {
        "blind_coding": True,
        "time_limit": (5, 10),  # (min, max) minutes per dataset
        "break_protocol": {
            "interval": 60,  # minutes
            "duration": 10   # minutes
        }
    },
    "csv_schema": {
        "columns": ["dataset_id"] + DTS_SECTIONS,
        "dtypes": {"dataset_id": str, **{s: int for s in DTS_SECTIONS}}
    }
}
```

**Subtasks [5/5 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Training Protocol | Generate annotation_protocol.md with DTS guidelines |
| C-3-2 | Calibration Set | Implement calibration validation (100% agreement check) |
| C-3-3 | Annotation Template | Generate CSV templates for both coders |
| C-3-4 | Binary Judgment Logic | Implement section presence detection logic |
| C-3-5 | Annotation Validation | Validate completeness (no missing values, correct format) |

---

### E1-4: Cohen's Kappa Calculator [Complexity: 11, Budget: 5]

```python
KAPPA_CONFIG = {
    "sklearn_method": "cohen_kappa_score",
    "scipy_bootstrap": "bootstrap",
    "bootstrap_params": BOOTSTRAP_CONFIG,
    "metrics": [
        "cohen_kappa",
        "percent_agreement",
        "positive_agreement",
        "negative_agreement",
        "ci_95_lower",
        "ci_95_upper",
        "interpretation"
    ]
}
```

**Subtasks [5/5 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Kappa Computation | Implement sklearn.metrics.cohen_kappa_score wrapper |
| C-4-2 | Bootstrap CI | Implement scipy.stats.bootstrap for 95% CI |
| C-4-3 | Agreement Metrics | Compute percent, positive, negative agreement |
| C-4-4 | Landis-Koch Interpretation | Map κ values to interpretation labels |
| C-4-5 | Section-Level Analysis | Analyze all 6 DTS sections independently |

---

### E1-5: Gate Validation Logic [Complexity: 7, Budget: 5]

```python
GATE_CONFIG = {
    "gate_type": "MUST_WORK",
    "thresholds": GATE_THRESHOLDS,
    "validation_logic": {
        "section_pass": "kappa >= 0.60",
        "gate_pass": "sum(section_pass) >= 5"
    },
    "output_format": {
        "pass_message": "✅ MUST_WORK gate PASSED",
        "fail_message": "❌ MUST_WORK gate FAILED - ABANDON hypothesis"
    }
}
```

**Subtasks [5/5 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Section Pass Check | Check if κ ≥ 0.60 for each section |
| C-5-2 | Gate Evaluation | Check if ≥5/6 sections pass |
| C-5-3 | Gate Report | Format PASS/FAIL message with section details |
| C-5-4 | Results JSON | Generate validation_results.json |
| C-5-5 | State Update | Update verification_state.yaml with gate result |

---

### E1-6: Visualization Suite [Complexity: 10, Budget: 5]

```python
VIZ_CONFIG = FIGURE_CONFIG  # Defined above
```

**Subtasks [5/5 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Gate Metrics Bar Chart | Bar chart with κ per section + threshold line |
| C-6-2 | Confusion Matrices | 6 subplots (2×3) with annotated confusion matrices |
| C-6-3 | Agreement Heatmap | 30×6 heatmap showing agreement patterns |
| C-6-4 | Base Rate Scatter | Scatter plot of section base rate vs κ |
| C-6-5 | Figure Saving | Save all 4 figures to h-e1/figures/ as PNG |

---

## Reproducibility Settings

```python
# Random Seeds
RANDOM_STATE = 42

# Numpy Random Generator
import numpy as np
RNG = np.random.default_rng(seed=RANDOM_STATE)

# Python Random Seed
import random
random.seed(RANDOM_STATE)
```

---

## Dependencies

```python
# requirements.txt
DEPENDENCIES = {
    "datasets": ">=2.10.0",           # HuggingFace Hub
    "openml": ">=0.14.0",             # OpenML API
    "beautifulsoup4": ">=4.11.0",     # UCI scraping
    "requests": ">=2.28.0",           # HTTP requests
    "scikit-learn": ">=1.2.0",        # Cohen's kappa
    "scipy": ">=1.10.0",              # Bootstrap CI
    "numpy": ">=1.24.0",              # Numerical operations
    "matplotlib": ">=3.7.0",          # Visualization
    "seaborn": ">=0.12.0",            # Advanced plots
    "pandas": ">=1.5.0"               # Data manipulation
}
```

---

## Configuration Summary

**Total Tasks:** 6 (E1-1 to E1-6)
**Total Subtasks:** 30 (5 per task)
**Complexity Budget:** 57 points used
**Configuration Pattern:** Hardcoded Python constants (single fixed configuration for EXISTENCE PoC)

**Key Design Decisions:**
- No hyperparameter variations (EXISTENCE hypothesis - single PoC configuration)
- Fixed random seeds for reproducibility
- Bootstrap resampling for CI precision (1000 iterations)
- Landis-Koch interpretation standard (established psychometric framework)
- 4 figures required for validation report (gate metrics, confusion matrices, heatmap, scatter)

---

**Configuration Completed:** 2026-03-18
**Next Phase:** Phase 4 - Implementation
