# Product Requirements Document (PRD)

**Date:** 2026-03-18
**Hypothesis:** h-e1 - Human Inter-Annotator Agreement Ceiling
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK (κ ≥ 0.60 in ≥5/6 DTS sections)

---

## Executive Summary

This PRD defines the implementation requirements for measuring human inter-annotator agreement (Cohen's κ) on DTS (Datasheets for Datasets) framework annotations. The study establishes a human performance ceiling necessary to interpret automated system success in downstream hypotheses.

**Deliverable:** Inter-annotator agreement study producing section-level Cohen's κ values for 6 DTS sections across 30 datasets.

---

## Problem Statement

**Context:** The ADAMS verification chain requires measurable human inter-annotator agreement to establish a performance ceiling for automated DTS annotation systems.

**Challenge:** Without empirical human agreement baselines, the 90% automation target in H-M lacks a valid reference point.

**Solution:** Conduct a controlled inter-annotator agreement study with two independent coders annotating 30 datasets using DTS binary presence criteria.

---

## Functional Requirements

### FR-1: Dataset Collection System

**Priority:** P0 (Critical)

**Description:** Programmatic collection of 30 datasets from three repositories with stratified sampling.

**Acceptance Criteria:**
- Collect 10 datasets from HuggingFace Hub API
- Collect 10 datasets from OpenML API
- Collect 10 datasets from UCI ML Repository (web scraping)
- Stratification: 10 high-quality, 10 medium-quality, 10 low-quality (preliminary DTS scoring)
- Repository balance: Exactly 10 per repository
- Domain coverage: Mix of NLP, CV, and tabular datasets
- Published date range: 2020-2024

**Data Outputs:**
```
data/h-e1/
├── datasets_metadata.csv (30 rows: dataset_id, repo, quality_stratum, domain)
└── documentation/
    ├── hf_001.txt to hf_010.txt
    ├── openml_001.txt to openml_010.txt
    └── uci_001.txt to uci_010.txt
```

**Dependencies:**
- HuggingFace `datasets` library
- OpenML Python API
- BeautifulSoup (for UCI scraping)
- Requests library

---

### FR-2: Documentation Extraction Pipeline

**Priority:** P0 (Critical)

**Description:** Extract full documentation text for each dataset and structure for annotation.

**Acceptance Criteria:**
- HuggingFace: Extract dataset card via `datasets` library
- OpenML: Extract metadata/description via API
- UCI: Extract description from HTML pages
- Store as plain text files (one per dataset)
- Preserve formatting for human readability

**Data Outputs:**
- 30 plain text files in `data/h-e1/documentation/`
- Each file contains complete documentation as presented to annotators

---

### FR-3: Annotation Protocol Implementation

**Priority:** P0 (Critical)

**Description:** Blind annotation protocol for two independent coders with DTS binary presence judgments.

**Acceptance Criteria:**
- **Training Phase:**
  - Both coders study Gebru et al. (2021) DTS framework
  - Calibration on 5 datasets from Rondina et al. (2025)
  - 100% agreement required on calibration set before proceeding
  - Pre-annotation quiz (5 questions) to verify understanding

- **Annotation Phase:**
  - Blind protocol: Coder A and B annotate independently
  - No communication between coders during annotation
  - Binary presence judgment for 6 DTS sections per dataset:
    - Motivation (M)
    - Composition (C)
    - Collection (Col)
    - Preprocessing (P)
    - Uses (U)
    - Maintenance (Maint)
  - Time limit: 5-10 minutes per dataset (avoid fatigue)
  - Break protocol: 10-minute break every hour

**Data Outputs:**
```
data/h-e1/annotations/
├── coder_a_annotations.csv (30 rows × 6 DTS sections)
├── coder_b_annotations.csv (30 rows × 6 DTS sections)
└── annotation_protocol.md (training + annotation instructions)
```

**CSV Schema:**
```
dataset_id,Motivation,Composition,Collection,Preprocessing,Uses,Maintenance
hf_001,1,1,0,1,1,0
...
```

---

### FR-4: Cohen's Kappa Calculation Engine

**Priority:** P0 (Critical)

**Description:** Compute Cohen's κ per DTS section with 95% confidence intervals.

**Acceptance Criteria:**
- Use `sklearn.metrics.cohen_kappa_score` for κ calculation
- Bootstrap confidence intervals (1000 iterations) via `scipy.stats.bootstrap`
- Compute for all 6 DTS sections independently
- Include Landis-Koch interpretation (Substantial ≥ 0.61)

**Metrics:**
- **Primary:** Cohen's κ per section
- **Secondary:**
  - Percent agreement (p_o)
  - Positive agreement (agreement on presence)
  - Negative agreement (agreement on absence)
  - 95% CI bounds (lower, upper)

**Output Format:**
```python
{
  "Motivation": {
    "kappa": 0.72,
    "ci_95": (0.65, 0.79),
    "interpretation": "Substantial",
    "passes_gate": true
  },
  ...
}
```

---

### FR-5: Gate Validation Logic

**Priority:** P0 (Critical)

**Description:** MUST_WORK gate check for hypothesis success/failure.

**Acceptance Criteria:**
- **Primary Gate:** κ ≥ 0.60 in ≥5/6 DTS sections
- **Pass:** Display "✅ MUST_WORK gate PASSED"
- **Fail:** Display "❌ MUST_WORK gate FAILED - ABANDON hypothesis"

**Gate Logic:**
```python
sections_passing = sum(1 for section in results.values()
                      if section["kappa"] >= 0.60)
gate_passed = sections_passing >= 5
```

---

### FR-6: Visualization Suite

**Priority:** P1 (Important)

**Description:** Generate 4 figures for validation report.

**Acceptance Criteria:**

**Figure 1: Gate Metrics Comparison (MANDATORY)**
- Bar chart: κ values per DTS section
- Horizontal line: Gate threshold (κ = 0.60, red dashed)
- Error bars: 95% confidence intervals
- Color coding: Green (≥0.60), Red (<0.60)

**Figure 2: Confusion Matrices per Section**
- 6 subplots (2×3 grid)
- 2×2 confusion matrix for each section
- Annotated cells with counts and percentages

**Figure 3: Agreement Heatmap**
- Rows: 30 datasets
- Columns: 6 DTS sections
- Colors: Green (both agree presence), Red (both agree absence), Yellow (disagreement)

**Figure 4: Base Rate vs. Kappa Scatter**
- X-axis: Section base rate
- Y-axis: Cohen's κ
- Points labeled with section names
- Trend line showing base rate effect

**Output Path:** `h-e1/figures/` (4 PNG files)

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**Requirement:** All random sampling must be seeded for reproducibility.

**Implementation:**
- Set random seed for dataset selection: `random.seed(42)`
- Set random seed for bootstrap CI: `np.random.default_rng(seed=42)`

### NFR-2: Data Quality

**Requirement:** Annotation data quality controls.

**Implementation:**
- Calibration phase with 100% agreement threshold
- Pre-annotation quiz to verify coder understanding
- Time limits to prevent annotation fatigue
- Break protocol every hour

### NFR-3: Computational Efficiency

**Requirement:** Minimal computational resources (CPU-only, no GPU).

**Rationale:** Human annotation study with statistical analysis only.

### NFR-4: Documentation

**Requirement:** All code must include docstrings and inline comments.

**Standards:**
- Function docstrings with parameter descriptions
- Inline comments for statistical calculations
- README.md with setup and execution instructions

---

## Data & Environment Specifications

### Data Preparation Tasks

| Task | Description | Output |
|------|-------------|--------|
| **D-1** | Install dependencies (HF datasets, OpenML, BeautifulSoup) | `requirements.txt` |
| **D-2** | Collect HuggingFace datasets (10) | `data/h-e1/documentation/hf_*.txt` |
| **D-3** | Collect OpenML datasets (10) | `data/h-e1/documentation/openml_*.txt` |
| **D-4** | Collect UCI datasets (10) | `data/h-e1/documentation/uci_*.txt` |
| **D-5** | Generate metadata CSV | `data/h-e1/datasets_metadata.csv` |
| **D-6** | Prepare annotation materials | `data/h-e1/annotations/annotation_protocol.md` |

### Environment Setup Tasks

| Task | Description | Output |
|------|-------------|--------|
| **E-1** | Create virtual environment | `venv/` |
| **E-2** | Install Python dependencies | Installed packages |
| **E-3** | Verify sklearn/scipy versions | Version check script |
| **E-4** | Create folder structure | `data/h-e1/`, `h-e1/figures/` |

### Required Dependencies

```txt
# requirements.txt
datasets>=2.10.0
openml>=0.14.0
beautifulsoup4>=4.11.0
requests>=2.28.0
scikit-learn>=1.2.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=1.5.0
```

---

## Success Criteria

### Primary Success Metrics

| Metric | Target | Gate Type |
|--------|--------|-----------|
| Cohen's κ in ≥5/6 sections | κ ≥ 0.60 | MUST_WORK |
| High-base-rate sections (Uses) | κ > 0.75 | Performance expectation |
| Sparse sections (Collection, Maintenance) | κ ≥ 0.55 | Performance expectation |

### Validation Outputs

1. **04_validation.md** report with:
   - Cohen's κ per section with 95% CI
   - Gate validation result (PASS/FAIL)
   - Landis-Koch interpretation
   - 4 figures saved to `h-e1/figures/`

2. **verification_state.yaml** update:
   - `validation.status = "COMPLETED"`
   - `validation.result = "PASS"` or `"FAIL"`
   - `gate.satisfied = true` or `false`

---

## Technical Constraints

### Assumptions

1. Both coders are available for ~5-6 hours each
2. Rondina et al. (2025) calibration datasets are accessible
3. Repository APIs remain stable during data collection
4. UCI datasets are publicly accessible (no authentication)

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limits (HF/OpenML) | Add delay between requests (1s) |
| UCI web scraping failures | Manual fallback for missing datasets |
| Low inter-annotator agreement | Pre-training with calibration set |
| Annotation fatigue | Time limits + break protocol |

---

## Implementation Scope

### In Scope

- Dataset collection (30 datasets, 3 repositories)
- Annotation protocol execution (2 coders, 6 sections)
- Cohen's κ calculation with CI
- Gate validation
- Visualization suite (4 figures)

### Out of Scope

- Multi-coder agreement (>2 coders)
- Section-level adjudication for disagreements
- Automated annotation system (deferred to H-M)
- Temporal stability analysis (deferred to H-M)

---

## Appendix: Reference Implementations

### Cohen's Kappa - sklearn

```python
from sklearn.metrics import cohen_kappa_score

coder_a = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]
coder_b = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1]

kappa = cohen_kappa_score(coder_a, coder_b)
# kappa = 0.667 (Substantial agreement)
```

### Bootstrap CI - scipy

```python
from scipy.stats import bootstrap
import numpy as np

def kappa_stat(*data):
    return cohen_kappa_score(data[0], data[1])

rng = np.random.default_rng(seed=42)
res = bootstrap((coder_a, coder_b), kappa_stat,
                n_resamples=1000, random_state=rng,
                method='percentile')
# CI: (res.confidence_interval.low, res.confidence_interval.high)
```

---

**PRD Version:** 1.0
**Last Updated:** 2026-03-18
**Next Phase:** Phase 3 - Architecture Design
