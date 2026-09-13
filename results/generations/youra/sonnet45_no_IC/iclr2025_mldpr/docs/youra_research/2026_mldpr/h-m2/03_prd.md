# Product Requirements Document (PRD)
# H-M2: Protocol Consistency via Artifact Quality

**Version:** 1.0
**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis ID:** h-m2
**Hypothesis Type:** MECHANISM
**Phase:** Phase 3 - Implementation Planning

---

## Executive Summary

### Purpose
Implement an observational study to test whether high-quality ML benchmark artifacts (documentation quality score >7.0) lead to higher protocol consistency rates (>70%) across independent research groups, demonstrating that detailed implementation specifications reduce interpretation ambiguity.

### Success Criteria
**Primary:** Protocol consistency rate >70% for high-quality artifacts
**Secondary:** Spearman correlation ρ >0.4 between artifact quality and protocol consistency (p<0.05)
**Gate Type:** SHOULD_WORK (failure triggers EXPLORE for artifact improvements)

### Scope
- 10 benchmarks stratified by artifact quality (from H-M1 quality scores)
- 5 citing papers per benchmark (50 total papers analyzed)
- 4 protocol dimensions: data splits, preprocessing, evaluation protocol, hyperparameters
- Inter-rater reliability validation (Cohen's kappa ≥0.8)

---

## Problem Statement

### Research Hypothesis
Under the scope of benchmarks with high-quality artifacts, if artifacts provide detailed implementation specifications, then independent research groups show lower interpretation variance in reproduction attempts because explicit protocols reduce researcher degrees of freedom.

### Motivation
H-M1 revealed highly variable artifact quality (mean 2.43/10) with reliable measurement (κ=1.000). This hypothesis tests the causal mechanism: does artifact quality actually predict protocol consistency across labs?

### Prerequisites
- **H-M1:** COMPLETED (PASS) - Artifact quality scores available for 20 benchmarks
- **Data Dependency:** H-M1 artifact_quality.csv provides stratification basis

---

## Functional Requirements

### FR-1: Benchmark Selection and Stratification
**Priority:** P0 (Critical)
**Description:** Select 10 benchmarks from H-M1 corpus stratified by artifact quality terciles
**Acceptance Criteria:**
- Load H-M1 artifact quality scores (20 benchmarks)
- Stratify into High (>7.0), Medium (4-7), Low (<4) quality strata
- Sample 10 benchmarks ensuring representation across strata
- Verify each benchmark has ≥5 citing papers available
**Input:** `../h-m1/data/artifact_quality.csv`
**Output:** `data/selected_benchmarks.csv`

### FR-2: Citing Paper Retrieval
**Priority:** P0 (Critical)
**Description:** Retrieve 5 citing papers per benchmark using Papers with Code + Semantic Scholar APIs
**Acceptance Criteria:**
- Query Papers with Code API for benchmark citations
- Fetch paper metadata (title, authors, year, venue)
- Download full papers via Semantic Scholar or arXiv
- Target: 50 total papers (5 per benchmark)
**API Endpoints:**
- Papers with Code: `https://paperswithcode.com/api/v1/papers/{id}/results`
- Semantic Scholar: `https://api.semanticscholar.org/v1/paper/{id}`
**Output:** `data/citing_papers/` (50 PDF files)

### FR-3: Protocol Extraction and Coding
**Priority:** P0 (Critical)
**Description:** Extract Methods sections and code protocols using 4-dimension rubric
**Acceptance Criteria:**
- Extract text from PDFs using PyMuPDF or pdfplumber
- Identify Methods sections via regex + heuristics
- Code 4 dimensions for each paper:
  1. **data_splits:** Identical (1) vs Divergent (0) relative to benchmark spec
  2. **preprocessing:** Normalization, augmentation, resizing
  3. **evaluation_protocol:** Metrics, validation strategy
  4. **hyperparameters:** Optimizer, LR, batch size, epochs
- Binary coding: Identical=1 if matches benchmark spec, Divergent=0 otherwise
**Input:** `data/citing_papers/*.pdf`
**Output:** `data/protocol_coding.csv` (50 rows x 4 dimensions)

### FR-4: Inter-Rater Reliability Validation
**Priority:** P0 (Critical)
**Description:** Validate coding reliability with 2 independent raters on 20% sample
**Acceptance Criteria:**
- Two independent coders code 10 papers (20% of corpus)
- Compute Cohen's kappa for each dimension
- Kappa threshold: κ ≥0.8 (same as H-M1)
- If κ <0.8: Refine rubric and re-code
**Input:** `data/protocol_coding.csv` (10 papers, rater1 and rater2 columns)
**Output:** `results/inter_rater_reliability.csv`
**Library:** `sklearn.metrics.cohen_kappa_score`

### FR-5: Protocol Consistency Computation
**Priority:** P0 (Critical)
**Description:** Compute consistency rate per benchmark and stratum
**Acceptance Criteria:**
- For each benchmark: % of papers with ≥3/4 dimensions identical
- Aggregate by quality stratum (High/Medium/Low)
- Primary metric: Mean consistency rate for High quality stratum
- Secondary metric: Spearman ρ between quality score and consistency rate
**Input:** `data/protocol_coding.csv`, `data/selected_benchmarks.csv`
**Output:** `results/consistency_by_stratum.csv`
**Library:** `scipy.stats.spearmanr`

### FR-6: Statistical Analysis
**Priority:** P0 (Critical)
**Description:** Test hypothesis with primary and secondary metrics
**Acceptance Criteria:**
- **Primary Test:** Is high-quality consistency rate >70%?
- **Secondary Test:** Is Spearman ρ >0.4 (p<0.05)?
- **Baseline Comparison:** One-sample t-test vs 50% random baseline
- Gate evaluation: PASS if primary OR secondary succeeds
**Input:** `results/consistency_by_stratum.csv`
**Output:** `results/hypothesis_test.json`

### FR-7: Visualization Generation
**Priority:** P1 (Important)
**Description:** Generate 4 required figures
**Acceptance Criteria:**
1. **gate_metrics.png:** Bar chart comparing Target vs Actual for primary (70%) and secondary (ρ=0.4) metrics
2. **consistency_by_quality.png:** Box plot of consistency rates by stratum (High/Medium/Low)
3. **quality_consistency_scatter.png:** Scatter plot with regression line (X=quality score, Y=consistency rate)
4. **dimension_heatmap.png:** Heatmap showing consistency per benchmark-dimension pair
**Output:** `figures/` directory with 4 PNG files
**Library:** `matplotlib`, `seaborn`

---

## Non-Functional Requirements

### NFR-1: Performance
- Data collection: Complete within 3-5 hours (API rate limits)
- Protocol coding: 2-3 minutes per paper (manual extraction)
- Statistical analysis: <1 minute runtime

### NFR-2: Reliability
- Inter-rater reliability: Cohen's κ ≥0.8 across all dimensions
- Missing data handling: Exclude papers with insufficient implementation detail
- Outlier detection: Flag benchmarks with <3 usable citing papers

### NFR-3: Reproducibility
- Random seed: Not applicable (observational study)
- API endpoints: Papers with Code + Semantic Scholar (public, rate-limited)
- Environment: Python 3.8+, standard scientific libraries (requests, scipy, sklearn, pandas)

### NFR-4: Data Quality
- Minimum papers per benchmark: 3 (flag if <3 after filtering)
- PDF parsing quality: Manual verification of Methods section extraction
- Protocol coding validation: 20% double-coding with κ ≥0.8

---

## Data Requirements

### Input Data

#### Primary Input: H-M1 Artifact Quality Scores
**Source:** `../h-m1/data/artifact_quality.csv`
**Format:** CSV with columns: `benchmark_id`, `quality_score`, `preprocessing`, `splits`, `evaluation`, `hyperparams`
**Volume:** 20 benchmarks
**Usage:** Stratification for benchmark selection

#### Secondary Input: Papers with Code API
**Endpoint:** `https://paperswithcode.com/api/v1/papers/{id}/results`
**Authentication:** Public API (rate-limited)
**Data:** Citing paper metadata (title, authors, venue, year)

#### Tertiary Input: Full Papers
**Source:** Semantic Scholar API or arXiv
**Format:** PDF files
**Volume:** 50 papers (5 per benchmark)
**Storage:** `data/citing_papers/`

### Output Data

#### Protocol Coding Dataset
**File:** `data/protocol_coding.csv`
**Schema:**
```csv
benchmark_id,paper_id,data_splits,preprocessing,evaluation_protocol,hyperparameters,rater
B001,P001,1,0,1,1,rater1
B001,P001,1,0,1,1,rater2
```
**Volume:** 50 rows (papers) x 4 dimensions + 10 rows (inter-rater sample)

#### Consistency Results
**File:** `results/consistency_by_stratum.csv`
**Schema:**
```csv
stratum,mean_consistency,std,n_benchmarks
High,0.75,0.12,3
Medium,0.60,0.15,4
Low,0.45,0.18,3
```

#### Hypothesis Test Results
**File:** `results/hypothesis_test.json`
**Schema:**
```json
{
  "primary_metric": {"value": 0.75, "threshold": 0.70, "pass": true},
  "secondary_metric": {"rho": 0.52, "p_value": 0.03, "threshold": 0.4, "pass": true},
  "gate_decision": "PASS"
}
```

---

## Dependencies

### External Services
- **Papers with Code API:** Public REST API for benchmark citations
- **Semantic Scholar API:** Public REST API for paper metadata and PDFs
- **arXiv API:** Fallback for paper downloads

### Python Libraries
```python
# Data collection
requests>=2.28.0

# PDF processing
PyMuPDF>=1.21.0  # or pdfplumber>=0.8.0

# Statistical analysis
scipy>=1.9.0
scikit-learn>=1.1.0
pandas>=1.4.0
numpy>=1.22.0

# Visualization
matplotlib>=3.5.0
seaborn>=0.12.0
```

### Data Dependencies
- **H-M1 Outputs:** Artifact quality scores (`artifact_quality.csv`)
- **Prerequisite Status:** H-M1 must have COMPLETED status with PASS gate

---

## Success Criteria

### Primary Success Criterion (Gate Metric)
**Metric:** Protocol Consistency Rate for High-Quality Artifacts
**Target:** >70%
**Measurement:**
```python
high_quality_benchmarks = benchmarks[quality_scores > 7.0]
consistency_rates = [compute_consistency(b) for b in high_quality_benchmarks]
primary_metric = np.mean([r > 0.80 for r in consistency_rates])
success = (primary_metric > 0.70)
```

### Secondary Success Criterion (Correlation)
**Metric:** Spearman Correlation between Quality Score and Consistency Rate
**Target:** ρ >0.4, p<0.05
**Measurement:**
```python
rho, p_value = spearmanr(quality_scores, consistency_rates)
secondary_success = (rho > 0.4) and (p_value < 0.05)
```

### PoC Success (Direction-Based)
**Requirement 1:** Code runs without error
**Requirement 2:** `consistency_high > consistency_low` (dose-response relationship)

### Gate Decision Logic
```python
if primary_success OR secondary_success:
    gate_decision = "PASS"
    next_action = "Proceed to H-M3"
else:
    gate_decision = "EXPLORE"
    next_action = "Identify missing artifact specifications"
```

---

## Risk Assessment

### Technical Risks
**R1: Insufficient Citing Papers**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** Pre-filter benchmarks by citation count (≥5 required)

**R2: PDF Parsing Failures**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** Manual verification of Methods section extraction; use both PyMuPDF and pdfplumber

**R3: API Rate Limiting**
- **Probability:** High
- **Impact:** Low
- **Mitigation:** Add delays between requests; cache API responses

### Data Quality Risks
**R4: Low Inter-Rater Reliability**
- **Probability:** Low (H-M1 achieved κ=1.000)
- **Impact:** High
- **Mitigation:** Use same rubric as H-M1; refine if κ<0.8

**R5: Ambiguous Protocol Specifications**
- **Probability:** High (many papers lack detail)
- **Impact:** Medium
- **Mitigation:** Binary coding (Identical=1 only if explicit match); exclude papers with insufficient detail

---

## Appendix: Reference Implementations

### A1: Papers with Code API
**Documentation:** https://paperswithcode.com/api/v1/docs/
**Example:**
```python
import requests

response = requests.get(
    f"https://paperswithcode.com/api/v1/papers/{paper_id}/results"
)
citing_papers = response.json()
```

### A2: Inter-Rater Reliability (Cohen's Kappa)
**Library:** `sklearn.metrics.cohen_kappa_score`
**Example:**
```python
from sklearn.metrics import cohen_kappa_score

rater1 = [1, 1, 0, 1, 0, 1, 1, 0, 1, 1]
rater2 = [1, 1, 0, 1, 1, 1, 1, 0, 1, 1]
kappa = cohen_kappa_score(rater1, rater2)
```

### A3: Spearman Correlation
**Library:** `scipy.stats.spearmanr`
**Example:**
```python
from scipy.stats import spearmanr

quality_scores = [2.5, 3.8, 5.2, 7.1, 8.3]
consistency_rates = [0.40, 0.50, 0.65, 0.75, 0.85]
rho, p_value = spearmanr(quality_scores, consistency_rates)
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-12 | Anonymous | Initial PRD from Phase 2C experiment brief |

---

**Status:** READY FOR ARCHITECTURE
**Next Phase:** Phase 3 Step 3 - Architecture Agent
