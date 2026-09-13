# Product Requirements Document: H-E1 Data Extraction Experiment

**Date:** 2026-04-14
**Author:** Anonymous
**Hypothesis:** H-E1 (EXISTENCE)
**Phase:** Phase 3 - Implementation Planning
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)

---

## Executive Summary

### Purpose
Validate the foundational assumption that published technical reports from major LLM labs contain category-level error rate data suitable for building an error taxonomy. This is an EXISTENCE hypothesis testing data availability, not model performance.

### Scope
Extract and structure category-level benchmark results from published technical reports for ≥3 model families (GPT, Claude, Llama) across ≥2 timepoints (baseline vs current) for TruthfulQA and MMLU benchmarks.

### Success Criteria
- **Primary:** ≥3 model families with category-level data for both timepoints
- **Secondary:** Data granularity ≥10 categories per benchmark
- **Tertiary:** Data completeness ≥90%

---

## Problem Statement

### Research Question
Can we extract structured category-level error rates from published LLM technical reports to support weak supervision learning?

### Gate Condition
**Type:** MUST_WORK
**Condition:** ≥3 model families with category-level data for both timepoints
**If Failed:** ABORT - entire approach infeasible without published data

### Context
This is the **foundation hypothesis** in a 5-hypothesis verification chain. Without published category-level data, the entire weak supervision approach for error taxonomy generation becomes infeasible.

---

## Functional Requirements

### FR-1: Technical Report Collection
**Priority:** P0 (Critical)
**Description:** Download and store technical reports from major LLM labs

**Acceptance Criteria:**
- Download GPT-4 technical report (OpenAI)
- Download Claude-3 technical report (Anthropic)
- Download Llama-3 technical report (Meta)
- Download baseline reports: GPT-3.5, Claude-2, Llama-2
- Store in structured format with metadata (publication date, source URL)

**Data Sources:**
- OpenAI: https://openai.com/research/gpt-4 (or arxiv.org/abs/2303.08774)
- Anthropic: https://www.anthropic.com/claude-3
- Meta: https://ai.meta.com/blog/meta-llama-3/

### FR-2: Category-Level Data Extraction (TruthfulQA)
**Priority:** P0 (Critical)
**Description:** Parse TruthfulQA category-level results from technical reports

**Acceptance Criteria:**
- Extract accuracy/error rate per category for each model
- Support both PDF and HTML report formats
- Handle ≥10 categories per report
- Store with columns: [model_family, timepoint, benchmark, category, error_rate]

**Expected Categories (TruthfulQA):**
- Health, Law, Finance, Politics, Science, Conspiracies, etc. (38 categories aggregated to 6-10)

### FR-3: Category-Level Data Extraction (MMLU)
**Priority:** P0 (Critical)
**Description:** Parse MMLU subject/domain-level results from technical reports

**Acceptance Criteria:**
- Extract accuracy per MMLU subject or domain
- Support 57 subjects or 4 domains (STEM, Humanities, Social Sciences, Other)
- Store in same structured format as FR-2

### FR-4: Data Validation
**Priority:** P0 (Critical)
**Description:** Verify extracted data meets quality and coverage requirements

**Acceptance Criteria:**
- Check ≥3 model families have data
- Check each family has both baseline AND current timepoint
- Check ≥10 categories per benchmark
- Check ≥90% completeness (no missing values)
- Flag and report any validation failures

### FR-5: Structured Output Generation
**Priority:** P0 (Critical)
**Description:** Generate structured dataset for downstream analysis

**Acceptance Criteria:**
- Output CSV/DataFrame with schema: [model_family, timepoint, benchmark, category, error_rate]
- Include metadata file with publication dates and source URLs
- Save to hypothesis folder with standardized naming

### FR-6: Evaluation Metrics Computation
**Priority:** P1 (Important)
**Description:** Calculate success metrics for gate condition evaluation

**Acceptance Criteria:**
- Compute Model Family Coverage metric
- Compute Category Granularity metric per benchmark
- Compute Data Completeness percentage
- Generate summary report with pass/fail status

### FR-7: Visualization Generation
**Priority:** P1 (Important)
**Description:** Create visualizations for data availability analysis

**Required Figures:**
1. **Gate Metrics Comparison** (Mandatory)
   - Bar chart: Model families × Timepoints with data
   - Target line at 2 timepoints
   
2. **Category Granularity Heatmap**
   - Model families × Benchmarks
   - Color intensity = number of categories
   
3. **Data Completeness Matrix**
   - Green/Yellow/Red cells for availability
   
4. **Temporal Coverage Timeline**
   - Publication dates with baseline vs current markers

**Output Location:** `h-e1/figures/`

---

## Non-Functional Requirements

### NFR-1: Execution Environment
- **Runtime:** <5 minutes for full extraction
- **GPU:** NOT REQUIRED (text processing only)
- **Dependencies:** Python 3.8+, pandas, PyPDF2, BeautifulSoup4, requests, matplotlib

### NFR-2: Reproducibility
- All extraction logic must be deterministic
- Manual downloads should be documented with exact URLs and access dates
- Extraction scripts must handle report format variations gracefully

### NFR-3: Extensibility
- Parser should support adding new model families
- Schema should accommodate additional benchmarks
- Easy to update for new report formats

### NFR-4: Error Handling
- Graceful degradation if a report is unavailable
- Clear error messages for parsing failures
- Validation failures should not crash the pipeline

---

## Data Specifications

### Input Data

**Dataset 1: TruthfulQA**
- **Source:** https://github.com/sylinrl/TruthfulQA
- **Type:** Standard benchmark dataset
- **Size:** 817 questions, 38 categories
- **Format:** CSV with question, category, answers
- **Loading:** `load_dataset("truthful_qa", "generation")`
- **Purpose:** Reference for category definitions

**Dataset 2: MMLU**
- **Source:** https://github.com/hendrycks/test
- **Type:** Standard benchmark dataset
- **Size:** 57 subjects, ~14,000 questions
- **Format:** CSV per subject (test/dev/val splits)
- **Loading:** `load_dataset("cais/mmlu", "all")`
- **Purpose:** Reference for subject/domain structure

**Dataset 3: Technical Reports**
- **Source:** Manual download from lab websites
- **Type:** PDF or HTML documents
- **Content:** Benchmark performance tables
- **Purpose:** Primary data source for extraction

### Output Data

**Output 1: Structured Dataset**
- **Filename:** `h-e1_extracted_data.csv`
- **Schema:**
  ```
  model_family: str (GPT, Claude, Llama)
  timepoint: str (baseline, current)
  benchmark: str (TruthfulQA, MMLU)
  category: str (category name)
  error_rate: float (0-100)
  ```
- **Expected Rows:** ~60-120 (3 families × 2 timepoints × 2 benchmarks × ~10 categories)

**Output 2: Metadata File**
- **Filename:** `h-e1_metadata.json`
- **Content:** Publication dates, source URLs, extraction timestamp

**Output 3: Validation Report**
- **Filename:** `h-e1_validation.json`
- **Content:** Coverage metrics, completeness checks, pass/fail status

**Output 4: Figures**
- **Location:** `h-e1/figures/`
- **Files:** `gate_metrics.png`, `granularity_heatmap.png`, `completeness_matrix.png`, `timeline.png`

---

## Dependencies and Constraints

### Technical Dependencies
- Python 3.8+ (standard library)
- pandas >= 1.3.0 (data manipulation)
- PyPDF2 >= 2.0.0 (PDF parsing)
- beautifulsoup4 >= 4.10.0 (HTML parsing)
- requests >= 2.26.0 (HTTP downloads)
- matplotlib >= 3.4.0 (visualization)
- datasets >= 2.0.0 (HuggingFace datasets - optional for reference)

### External Dependencies
- Internet access for downloading technical reports
- Manual intervention may be required if reports are paywalled or require login

### Constraints
- **No API calls:** This is a static data extraction task, not real-time model evaluation
- **No model training:** This is data availability verification only
- **Timepoint definition:** Baseline = 2022-2023 publications, Current = 2023-2024 publications
- **Category granularity:** Minimum 10 categories required per benchmark

---

## Success Metrics

### Primary Metrics

**1. Model Family Coverage**
- **Definition:** Number of model families with data for both timepoints
- **Target:** ≥3 families
- **Measurement:** Binary check per family (GPT, Claude, Llama)
- **Gate Condition:** MUST_WORK

**2. Category Granularity**
- **Definition:** Number of categories per benchmark in extracted data
- **Target:** ≥10 categories for TruthfulQA AND MMLU
- **Measurement:** Count unique category labels

**3. Data Completeness**
- **Definition:** Percentage of expected cells with non-null values
- **Target:** ≥90%
- **Measurement:** (filled_cells / total_cells) × 100

### Evaluation Code

```python
def evaluate_data_availability(extracted_df):
    """
    Evaluate if H-E1 success criteria are met
    
    Args:
        extracted_df: DataFrame with columns [model_family, timepoint, benchmark, category, error_rate]
    
    Returns:
        dict with metrics and pass/fail status
    """
    # Primary: Model family coverage
    families_with_data = extracted_df.groupby('model_family').apply(
        lambda x: ('baseline' in x['timepoint'].values) and ('current' in x['timepoint'].values)
    ).sum()
    
    # Secondary: Category granularity
    categories_per_benchmark = extracted_df.groupby('benchmark')['category'].nunique()
    
    # Tertiary: Data completeness
    completeness = (1 - extracted_df['error_rate'].isna().mean()) * 100
    
    # Gate condition evaluation
    gate_passed = (
        families_with_data >= 3 and
        categories_per_benchmark.get('TruthfulQA', 0) >= 10 and
        categories_per_benchmark.get('MMLU', 0) >= 10 and
        completeness >= 90
    )
    
    return {
        'families_with_data': families_with_data,  # Success: ≥3
        'categories_truthfulqa': categories_per_benchmark.get('TruthfulQA', 0),  # Success: ≥10
        'categories_mmlu': categories_per_benchmark.get('MMLU', 0),  # Success: ≥10
        'data_completeness_pct': completeness,  # Success: ≥90%
        'gate_passed': gate_passed
    }
```

---

## Implementation Phases

This is a **LIGHT-tier** implementation (EXISTENCE hypothesis):
- **Total Task Budget:** ≤15 tasks
- **Epic Range:** 4-8 epics
- **Infrastructure:** Minimal (no training pipeline, no model serving)

### Suggested Epic Breakdown (Architecture phase will finalize)

1. **Epic 1: Environment Setup** (1-2 tasks)
   - Install dependencies
   - Create folder structure

2. **Epic 2: Report Download** (1-2 tasks)
   - Implement download scripts
   - Store with metadata

3. **Epic 3: PDF/HTML Parsing** (2-3 tasks)
   - Implement table extraction
   - Handle format variations

4. **Epic 4: Data Extraction Logic** (2-3 tasks)
   - TruthfulQA category extraction
   - MMLU subject/domain extraction
   - Structured output generation

5. **Epic 5: Validation & Metrics** (2-3 tasks)
   - Implement validation checks
   - Compute success metrics
   - Generate validation report

6. **Epic 6: Visualization** (1-2 tasks)
   - Generate required figures
   - Save to figures folder

7. **Epic 7: Integration & Testing** (1-2 tasks)
   - End-to-end pipeline test
   - Generate final outputs

---

## Out of Scope

- **Model training/fine-tuning:** This is data extraction only
- **Real-time API calls:** Using static published reports
- **Benchmark re-evaluation:** Not re-running models on benchmarks
- **Category creation:** Using existing category definitions from datasets
- **Statistical significance testing:** PoC focuses on data availability, not statistical rigor
- **Multi-language support:** English technical reports only

---

## Risks and Mitigations

### Risk 1: Published error rate inaccuracy
- **Severity:** Medium
- **Mitigation:** Cross-validate sources, exclude outliers, document discrepancies

### Risk 2: Report format variations
- **Severity:** High
- **Mitigation:** Implement robust parsers with fallback to manual extraction, test on multiple report formats

### Risk 3: Missing category-level breakdowns
- **Severity:** Critical (Gate failure)
- **Mitigation:** If <3 families have data, check supplementary materials and appendices before declaring failure

### Risk 4: Insufficient granularity
- **Severity:** High
- **Mitigation:** If <10 categories, try extracting finer-grained subject-level data from appendices

---

## Acceptance Criteria Summary

✅ **Definition of Done:**
1. All 6 technical reports downloaded and stored
2. Category-level data extracted for ≥3 model families
3. Both timepoints (baseline + current) available per family
4. ≥10 categories per benchmark (TruthfulQA, MMLU)
5. Data completeness ≥90%
6. Structured CSV output generated
7. All 4 required figures created
8. Validation report shows GATE_PASSED = true
9. Code runs without errors in <5 minutes
10. All outputs saved to h-e1/ folder

---

## Appendix: Reference Implementations

### Known GitHub Repositories

**1. sylinrl/TruthfulQA** (⭐ 800+)
- Official dataset with category labels
- Use for category enumeration

**2. EleutherAI/lm-evaluation-harness** (⭐ 3000+)
- Standard evaluation framework
- Reference for how category-level metrics are computed

**3. hendrycks/test** (⭐ 1200+)
- Official MMLU dataset
- Use for subject/domain structure

### Data Loading Examples

```python
# Load TruthfulQA reference
from datasets import load_dataset
truthfulqa = load_dataset("truthful_qa", "generation")
categories = truthfulqa['validation']['category'].unique()

# Load MMLU reference
mmlu = load_dataset("cais/mmlu", "all")
subjects = mmlu.keys()  # 57 subjects

# Technical reports: Manual download
import requests
from bs4 import BeautifulSoup
import PyPDF2

# Example: Download GPT-4 technical report
# URL: https://arxiv.org/abs/2303.08774 (GPT-4 paper)
# Extract category-level tables from PDF
```

---

**Document Status:** ✅ Complete
**Next Phase:** Architecture Design (Step 3)
**Task Budget Allocated:** LIGHT tier (≤15 tasks)
