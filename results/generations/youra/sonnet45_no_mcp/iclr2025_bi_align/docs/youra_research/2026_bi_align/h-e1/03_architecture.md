# System Architecture
# Hypothesis: H-E1 - Base-Rate Validation Study

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-e1  
**Architecture Type:** Human Annotation Study with Statistical Analysis

---

## Codebase Analysis (Serena)

**Analysis Status:** Green-field implementation (no existing codebase)

**Context:** This is a novel human annotation validation study with no base hypothesis dependencies. The implementation will create a new annotation framework from scratch.

**Applied:** Standard annotation study architecture pattern (KB-001-AnnotationStudy)

---

## 1. System Overview

### 1.1 Architecture Pattern
**Pattern:** Annotation Study Pipeline  
**Components:** Data Sampling → Annotation Collection → Statistical Analysis → Visualization

### 1.2 Design Principles
- **Simplicity:** LIGHT tier (EXISTENCE hypothesis) - minimal infrastructure
- **Reproducibility:** Fixed seeds, logged decisions
- **Statistical Rigor:** Standard hypothesis testing frameworks

---

## 2. Module Structure

### Module 1: Data Sampling (`src/data/`)
**Purpose:** Stratified random sampling from HH-RLHF dataset  
**Files:**
- `src/data/sampler.py` - Stratified sampling logic
- `src/data/loader.py` - HuggingFace dataset loading

### Module 2: Annotation Interface (`src/annotation/`)
**Purpose:** Simple annotation collection system  
**Files:**
- `src/annotation/interface.py` - CLI or web-based annotation UI
- `src/annotation/storage.py` - Annotation data persistence

### Module 3: Statistical Analysis (`src/analysis/`)
**Purpose:** Inter-rater reliability and binomial testing  
**Files:**
- `src/analysis/agreement.py` - Cohen's κ calculation
- `src/analysis/hypothesis_test.py` - Binomial test implementation
- `src/analysis/metrics.py` - Base-rate and confidence intervals

### Module 4: Visualization (`src/visualization/`)
**Purpose:** Generate required figures  
**Files:**
- `src/visualization/plots.py` - All visualization logic

### Module 5: Experiment Runner (`src/`)
**Purpose:** Main experiment orchestration  
**Files:**
- `src/main.py` - Entry point
- `config.yaml` - Hardcoded configuration (LIGHT tier)

---

## 3. File Organization

```
h-e1/
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── sampler.py         # Stratified sampling
│   │   └── loader.py          # Dataset loading
│   ├── annotation/
│   │   ├── __init__.py
│   │   ├── interface.py       # Annotation UI
│   │   └── storage.py         # CSV persistence
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── agreement.py       # Cohen's κ
│   │   ├── hypothesis_test.py # Binomial test
│   │   └── metrics.py         # Base-rate calculation
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plots.py           # All figures
│   ├── main.py                # Experiment runner
│   └── config.yaml            # Configuration
├── data/
│   ├── hh_rlhf_samples.csv    # Sampled 500 responses
│   └── annotations.csv        # Annotation results
├── outputs/
│   ├── figures/               # Generated visualizations
│   ├── results.json           # Statistical test results
│   └── report.md              # Summary report
├── tests/
│   ├── test_sampler.py
│   ├── test_agreement.py
│   └── test_hypothesis_test.py
├── requirements.txt
└── README.md
```

---

## 4. Epic Tasks with Complexity Scores

### Epic E-1: Data Sampling Module
**ID:** E-1  
**Module:** data  
**Complexity Score:** 6/20  
**Breakdown:**
- Module Size: 2 files, ~150 LOC → 2/5
- Dependencies: HuggingFace datasets → 1/5
- Algorithm: Stratified sampling → 2/5
- Integration: Standalone module → 1/5

**Description:** Implement stratified random sampling to select 500 rejected responses from HH-RLHF harmless-base subset, balanced across response length quartiles.

**Acceptance Criteria:**
- Loads HH-RLHF dataset via HuggingFace API
- Computes length quartiles for rejected responses
- Stratified sampling with reproducible seed
- Outputs CSV with 500 samples

---

### Epic E-2: Annotation Interface
**ID:** E-2  
**Module:** annotation  
**Complexity Score:** 9/20  
**Breakdown:**
- Module Size: 2 files, ~200 LOC → 3/5
- Dependencies: CLI or simple web framework → 2/5
- Algorithm: Simple display + input collection → 1/5
- Integration: File I/O for annotations → 3/5

**Description:** Build simple annotation interface (CLI or spreadsheet-based) for 3 independent annotators to label samples as genuine violation vs. marginal preference.

**Acceptance Criteria:**
- Presents samples with violation criteria checklist
- Blinded to original HH-RLHF labels
- Supports 3 separate annotator sessions
- Saves annotations to CSV

---

### Epic E-3: Inter-Annotator Agreement Analysis
**ID:** E-3  
**Module:** analysis  
**Complexity Score:** 8/20  
**Breakdown:**
- Module Size: 1 file, ~100 LOC → 2/5
- Dependencies: statsmodels → 1/5
- Algorithm: Cohen's κ calculation → 3/5
- Integration: Reads annotation CSV → 2/5

**Description:** Calculate Cohen's κ to measure inter-annotator agreement across 3 raters, with pairwise comparisons and overall multi-rater κ.

**Acceptance Criteria:**
- Loads annotation CSV (500 × 3 matrix)
- Computes pairwise κ for all annotator pairs
- Reports overall κ with interpretation (Landis & Koch)
- Generates agreement heatmap

---

### Epic E-4: Majority Vote & Base-Rate Calculation
**ID:** E-4  
**Module:** analysis  
**Complexity Score:** 7/20  
**Breakdown:**
- Module Size: 1 file, ~80 LOC → 2/5
- Dependencies: numpy, pandas → 1/5
- Algorithm: Majority vote + proportion → 2/5
- Integration: Reads annotations, outputs final labels → 2/5

**Description:** Determine final labels using majority vote from 3 annotators, then calculate base-rate (proportion of genuine violations) with 95% confidence interval.

**Acceptance Criteria:**
- Majority vote with tie-breaking strategy
- Base-rate p calculation
- 95% CI using binomial proportion
- Outputs final labeled dataset

---

### Epic E-5: Binomial Hypothesis Test
**ID:** E-5  
**Module:** analysis  
**Complexity Score:** 6/20  
**Breakdown:**
- Module Size: 1 file, ~60 LOC → 1/5
- Dependencies: scipy.stats → 1/5
- Algorithm: Binomial test → 2/5
- Integration: Uses base-rate from E-4 → 2/5

**Description:** Perform one-tailed binomial test for H0: p < 0.40 vs H1: p ≥ 0.40 to validate MUST_WORK gate condition.

**Acceptance Criteria:**
- Uses scipy.stats.binomtest
- One-tailed test (alternative='greater')
- α = 0.05
- Reports p-value and PASS/FAIL decision

---

### Epic E-6: Visualization Generation
**ID:** E-6  
**Module:** visualization  
**Complexity Score:** 7/20  
**Breakdown:**
- Module Size: 1 file, ~150 LOC → 2/5
- Dependencies: matplotlib, seaborn → 1/5
- Algorithm: 4 distinct plot types → 3/5
- Integration: Reads results from E-3, E-4, E-5 → 1/5

**Description:** Generate 4 required figures: (1) base-rate vs threshold bar chart, (2) inter-annotator agreement heatmap, (3) violation type distribution, (4) length bias scatter plot.

**Acceptance Criteria:**
- Bar chart: base-rate p vs 0.40 threshold with p-value annotation
- Heatmap: pairwise agreement matrix
- Bar chart: violation criteria frequency
- Scatter: violation rate vs length quartile
- All figures saved to outputs/figures/

---

### Epic E-7: Experiment Runner & Configuration
**ID:** E-7  
**Module:** main  
**Complexity Score:** 5/20  
**Breakdown:**
- Module Size: 1 file, ~100 LOC → 2/5
- Dependencies: argparse (hardcoded config for LIGHT tier) → 1/5
- Algorithm: Sequential pipeline execution → 1/5
- Integration: Orchestrates all modules → 1/5

**Description:** Main experiment runner that orchestrates the full pipeline: sampling → annotation → analysis → visualization, with hardcoded configuration (LIGHT tier infrastructure).

**Acceptance Criteria:**
- Sequential execution of all Epic tasks
- Hardcoded config in YAML (no complex config system for LIGHT tier)
- Logs pipeline progress with print statements
- Generates final report.md with results summary

---

## 5. Task Budget Summary

**Hypothesis Type:** EXISTENCE  
**Tier:** LIGHT  
**Total Budget:** 15 tasks  
**Epic Tasks:** 7

**Complexity Distribution:**
- High (14-17): 0 tasks
- Medium (6-13): 7 tasks (all Epics)
- Low (4-8): 0 tasks

**Estimated Total:** 7 Epic tasks (within 4-8 range for LIGHT tier)

---

## 6. Data Flow

```
HH-RLHF Dataset (HuggingFace)
    ↓
Stratified Sampler (E-1) → samples.csv
    ↓
Annotation Interface (E-2) → annotations.csv
    ↓
    ├→ Inter-Annotator Agreement (E-3) → κ score, heatmap
    ├→ Majority Vote + Base-Rate (E-4) → p, final_labels.csv
    ├→ Binomial Test (E-5) → p-value, PASS/FAIL
    └→ Visualization (E-6) → figures/
    ↓
Experiment Runner (E-7) → report.md
```

---

## 7. Integration Points

### 7.1 External Dependencies
- **HuggingFace Datasets:** `load_dataset("Anthropic/hh-rlhf", "harmless-base")`
- **statsmodels:** Cohen's κ calculation
- **scipy.stats:** Binomial test

### 7.2 Internal Dependencies
- E-2 depends on E-1 (sampled data)
- E-3, E-4, E-5 depend on E-2 (annotation results)
- E-6 depends on E-3, E-4, E-5 (analysis results)
- E-7 orchestrates all modules

---

## 8. Testing Strategy

**Infrastructure Level:** Minimal (LIGHT tier)

### 8.1 Test Coverage
- **Data Sampling:** Test stratification balance, reproducibility
- **Agreement:** Test κ calculation with known examples
- **Hypothesis Test:** Test binomial_test with known outcomes
- **Visualization:** Smoke tests (plots generated without errors)

### 8.2 Test Files
- `tests/test_sampler.py` - Sampling logic validation
- `tests/test_agreement.py` - Cohen's κ calculation
- `tests/test_hypothesis_test.py` - Binomial test edge cases

**Note:** No integration tests or E2E tests for LIGHT tier (minimal infrastructure).

---

## 9. Configuration Management

**Infrastructure Level:** Minimal (LIGHT tier)

### 9.1 Configuration Approach
- **Hardcoded YAML:** `config.yaml` with fixed parameters
- **No Environment Variables:** All settings in config file
- **No Multi-Environment Support:** Single production configuration

### 9.2 Configuration Parameters
```yaml
experiment:
  name: "h-e1-base-rate-validation"
  seed: 42
  sample_size: 500
  n_annotators: 3

dataset:
  name: "Anthropic/hh-rlhf"
  subset: "harmless-base"
  split: "train"

hypothesis_test:
  null_hypothesis_threshold: 0.40
  alpha: 0.05
  alternative: "greater"

outputs:
  figures_dir: "outputs/figures"
  results_file: "outputs/results.json"
  report_file: "outputs/report.md"
```

---

## 10. Logging & Monitoring

**Infrastructure Level:** Minimal (LIGHT tier)

- **Logging:** Print statements only (no structured logging for LIGHT tier)
- **Monitoring:** No real-time monitoring (run locally, check outputs manually)
- **Progress Tracking:** Console output with step completion messages

---

## 11. Deployment

**Target Environment:** Local execution (no deployment infrastructure for LIGHT tier)

**Execution:**
```bash
python src/main.py
```

**Outputs:**
- `data/hh_rlhf_samples.csv` - Sampled 500 responses
- `data/annotations.csv` - Annotation results (manual input)
- `outputs/figures/` - Generated visualizations
- `outputs/results.json` - Statistical test results
- `outputs/report.md` - Summary report with PASS/FAIL decision

---

## 12. Architecture Validation

### 12.1 Complexity Check
✓ Total Epic tasks: 7 (within LIGHT tier range of 4-8)  
✓ All tasks have complexity scores  
✓ No task exceeds complexity 9/20 (appropriate for LIGHT tier)

### 12.2 Dependency Check
✓ No circular dependencies  
✓ Clear sequential execution path  
✓ All external dependencies documented

### 12.3 Infrastructure Check
✓ Minimal infrastructure (LIGHT tier)  
✓ Hardcoded configuration (no complex config system)  
✓ Print-based logging (no structured logging)  
✓ Manual test execution (no CI/CD for LIGHT tier)

---

**Document Status:** COMPLETE  
**Next Phase:** Logic Design (03_logic.md)  
**Applied Patterns:** KB-001-AnnotationStudy, LIGHT-tier minimal infrastructure
