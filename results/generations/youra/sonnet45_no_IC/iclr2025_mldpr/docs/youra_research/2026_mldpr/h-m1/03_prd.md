# Product Requirements Document: H-M1 Artifact Quality Assessment

**Date:** 2026-07-12  
**Author:** Anonymous  
**Hypothesis:** h-m1 (MECHANISM)  
**Project:** ML Data Practices & Repository Benchmarking  

---

## Executive Summary

### Purpose
Develop an observational study system to measure documentation artifact quality in machine learning benchmarks. This PRD defines requirements for implementing a content analysis protocol that assesses whether documentation artifacts (GitHub repos, dataset cards, badges) provide detailed implementation specifications and usage guidelines.

### Hypothesis Statement
Under the scope of ML benchmarks with documentation artifacts (GitHub repos, dataset cards, badges), if artifacts are present, then they provide detailed implementation specifications and usage guidelines because standardized artifact formats (Croissant, FAIR) mandate specific metadata fields.

### Success Criteria
- **Primary:** Mean artifact quality score > 7.0/10 across sampled benchmarks
- **Validity:** Inter-rater reliability (Cohen's kappa) > 0.8
- **Completeness:** 20 benchmarks coded across 4 rubric dimensions
- **Gate:** MUST_WORK - If mean quality < 7.0, PIVOT to quality-weighted analysis

---

## Problem Statement

### Research Context
Building on H-E1 (EXISTENCE hypothesis, COMPLETED with PASS), which validated that ≥100 classification benchmarks exist with ≥5 reproduction attempts each, H-M1 tests the first mechanism step: whether documentation artifacts contain actionable implementation information.

### Current Gap
Existing research treats documentation artifacts as binary (present/absent) without measuring information richness. No standardized quality assessment exists for ML artifact documentation at scale.

### Proposed Solution
Implement a structured content analysis protocol using:
1. Papers with Code API for benchmark sampling
2. 4-dimension rubric (preprocessing, data splits, evaluation, hyperparameters)
3. Independent dual-rater coding
4. Statistical validation via Cohen's kappa

---

## Functional Requirements

### FR-1: Papers with Code API Integration
**Priority:** P0 (Critical)  
**Description:** Retrieve benchmark metadata via Papers with Code REST API  

**Acceptance Criteria:**
- Query classification benchmarks filtered by date (2019-2024)
- Extract artifact URLs (GitHub repo, dataset card, badge status)
- Apply stratified sampling: 10 CV + 10 NLP benchmarks
- Filter benchmarks with ≥2 artifacts present
- Handle API pagination (60 requests/minute rate limit)
- Export benchmark_sample.csv with 20 rows

**Dependencies:** None  
**Implementation Notes:**
```python
def fetch_pwc_benchmarks(task="classification", year_start=2019, year_end=2024):
    url = "https://paperswithcode.com/api/v1/benchmarks/"
    # Pagination handling, artifact filtering
    return pd.DataFrame(filtered_benchmarks)
```

### FR-2: Artifact Retrieval System
**Priority:** P0 (Critical)  
**Description:** Download and store artifact content for manual coding  

**Acceptance Criteria:**
- Retrieve GitHub README content via API
- Retrieve dataset card content (if available)
- Retrieve badge documentation metadata
- Store in structured folder: `artifact_content/{benchmark_id}/{artifact_type}.md`
- Handle missing/inaccessible artifacts gracefully

**Dependencies:** FR-1  
**Implementation Notes:** Use requests library for HTTP retrieval, store raw content

### FR-3: Artifact Quality Rubric Implementation
**Priority:** P0 (Critical)  
**Description:** Structured 4-dimension rubric for manual scoring  

**Rubric Dimensions:**
1. **Preprocessing:** Data preprocessing steps specification (0/5/10 scale)
2. **Data Splits:** Train/val/test split detail (0/5/10 scale)
3. **Evaluation Protocol:** Evaluation procedure completeness (0/5/10 scale)
4. **Hyperparameters:** Training hyperparameter specification (0/5/10 scale)

**Acceptance Criteria:**
- Rater scoring interface (manual, not automated)
- Score entry: 0 (no info), 5 (partial info), 10 (complete specification)
- Output: rater1_scores.csv, rater2_scores.csv with 20 rows × 4 dimensions
- Dimension-level aggregation to overall quality score (mean across 4 dimensions)

**Dependencies:** FR-2  
**Implementation Notes:**
```python
class ArtifactQualityRubric:
    RUBRIC_DIMENSIONS = {
        'preprocessing': {...},
        'data_splits': {...},
        'evaluation_protocol': {...},
        'hyperparameters': {...}
    }
    
    def score_artifact(self, artifact_content: dict) -> float:
        return mean([dimension_scores])
```

### FR-4: Inter-Rater Reliability Calculation
**Priority:** P0 (Critical)  
**Description:** Compute Cohen's kappa for measurement validity  

**Acceptance Criteria:**
- Load rater1_scores.csv and rater2_scores.csv
- Compute Cohen's kappa using sklearn.metrics.cohen_kappa_score
- Gate: kappa > 0.8 required for measurement validity
- If kappa < 0.8: Output discrepancy report for re-calibration
- Output: inter_rater_reliability.txt with kappa value and interpretation

**Dependencies:** FR-3  
**Implementation Notes:**
```python
from sklearn.metrics import cohen_kappa_score
kappa = cohen_kappa_score(rater1['quality_score'], rater2['quality_score'])
print(f"Reliability: {'PASS (>0.8)' if kappa > 0.8 else 'FAIL (<0.8)'}")
```

### FR-5: Quality Score Aggregation
**Priority:** P0 (Critical)  
**Description:** Compute mean artifact quality score across benchmarks  

**Acceptance Criteria:**
- Average scores across 2 raters for each benchmark
- Compute mean quality score across all 20 benchmarks
- Gate check: mean > 7.0 required for MUST_WORK gate pass
- If mean < 7.0: Output PIVOT recommendation for H-M2/H-M3
- Output: artifact_quality_scores.csv with final scores

**Dependencies:** FR-3, FR-4  
**Implementation Notes:**
```python
quality_scores = (rater1['quality_score'] + rater2['quality_score']) / 2
mean_quality = quality_scores.mean()
print(f"Gate Status: {'PASS (>7.0)' if mean_quality > 7.0 else 'PIVOT (<7.0)'}")
```

### FR-6: Visualization Generation
**Priority:** P1 (High)  
**Description:** Generate exploratory visualizations for artifact quality distribution  

**Required Figures:**
1. **Gate Metrics Comparison:** Target vs actual metrics bar chart (MANDATORY)
2. **Quality Distribution:** Histogram of quality scores across 20 benchmarks
3. **Dimension Breakdown:** Grouped bar chart for rubric dimensions
4. **Domain Comparison:** Box plots comparing CV vs NLP quality (exploratory)
5. **Inter-Rater Agreement:** Scatter plot of Rater 1 vs Rater 2 scores

**Acceptance Criteria:**
- All figures saved to `h-m1/figures/` directory
- Gate metrics figure shows: kappa threshold (0.8), quality threshold (7.0), actual values
- Figures use consistent color scheme and labeling
- PNG format with 300 DPI resolution

**Dependencies:** FR-5  

### FR-7: Experiment Execution Report
**Priority:** P1 (High)  
**Description:** Generate validation report with gate decision logic  

**Acceptance Criteria:**
- Report gate status: PASS or PIVOT based on mean quality score
- Include inter-rater reliability metrics
- Include dimension-level quality breakdown
- Include domain comparison results (CV vs NLP)
- Output: 04_validation.md with complete results

**Dependencies:** FR-5, FR-6  

---

## Non-Functional Requirements

### NFR-1: Data Collection Transparency
**Category:** Reproducibility  
**Description:** All data collection steps must be reproducible from documented protocol  

**Acceptance Criteria:**
- API query parameters logged
- Sampling seed documented for stratified random sampling
- Artifact retrieval timestamps recorded
- Rater training protocol documented

### NFR-2: Measurement Validity
**Category:** Quality Assurance  
**Description:** Ensure measurement reliability through statistical validation  

**Acceptance Criteria:**
- Cohen's kappa > 0.8 for inter-rater reliability
- If kappa < 0.8: Mandatory rubric refinement and re-coding
- Pilot test on 3 benchmarks before full coding
- Rater independence maintained (no communication during coding)

### NFR-3: Error Handling
**Category:** Robustness  
**Description:** Gracefully handle API failures and missing artifacts  

**Acceptance Criteria:**
- API timeout handling (retry with exponential backoff)
- Missing artifact handling (log and skip, don't fail entire process)
- Rate limit handling (60 req/min for Papers with Code API)
- Artifact retrieval errors logged to error_log.txt

### NFR-4: Execution Time
**Category:** Performance  
**Description:** Complete data collection within 1-2 weeks  

**Estimated Timeline:**
- Phase 1: Benchmark sampling (1-2 days)
- Phase 2: Artifact retrieval (2-3 days)
- Phase 3: Rater training (1 day)
- Phase 4: Independent coding (3-4 days)
- Phase 5: Reliability analysis (1 day)
- Phase 6: Quality score aggregation (1 day)

---

## Data Specifications

### Input Data
**Source:** Papers with Code API v1  
**Type:** Programmatic API (NOT synthetic)  
**Endpoints:**
- `/api/v1/benchmarks/` (primary)
- `/api/v1/papers/` (supplementary)

**Filters:**
- Task: Classification
- Publication year: 2019-2024
- Artifact count: ≥2 (GitHub, dataset card, or badge)
- Domain: Computer Vision OR NLP

**Sample Size:** 20 benchmarks (stratified: 10 CV + 10 NLP)

### Output Data
**Files Generated:**
1. `benchmark_sample.csv` (20 rows: benchmark metadata)
2. `artifact_content/*.md` (raw artifact content)
3. `rater1_scores.csv` (20 rows × 4 dimensions)
4. `rater2_scores.csv` (20 rows × 4 dimensions)
5. `artifact_quality_scores.csv` (20 rows: final aggregated scores)
6. `inter_rater_reliability.txt` (kappa value + interpretation)
7. `figures/*.png` (5 visualization files)
8. `04_validation.md` (final gate decision report)

---

## Evaluation Metrics

### Primary Metrics
1. **Mean Artifact Quality Score**
   - **Definition:** Average quality score across 20 benchmarks (0-10 scale)
   - **Success Criterion:** Mean > 7.0
   - **Calculation:** `quality_scores.mean()`
   - **Gate:** MUST_WORK - if < 7.0, PIVOT to quality-weighted analysis

2. **Inter-Rater Reliability (Cohen's Kappa)**
   - **Definition:** Agreement between 2 independent raters
   - **Success Criterion:** Kappa > 0.8
   - **Calculation:** `sklearn.metrics.cohen_kappa_score(rater1, rater2)`
   - **Interpretation:** < 0.40 poor, 0.40-0.59 fair, 0.60-0.79 good, ≥ 0.80 excellent

### Secondary Metrics
1. **Dimension-Level Quality Scores**
   - Mean scores for: Preprocessing, Data Splits, Evaluation, Hyperparameters
   - Purpose: Identify which artifact components are most/least informative

2. **Domain Comparison**
   - CV vs NLP artifact quality comparison (exploratory)
   - Statistical test: Mann-Whitney U test (non-parametric)

---

## Dependencies and Constraints

### External Dependencies
- **Papers with Code API:** Public REST API (no authentication required)
- **Python Libraries:** requests, pandas, scikit-learn, matplotlib
- **Rater Availability:** 2 independent human raters for manual coding

### Constraints
- **API Rate Limit:** 60 requests/minute (Papers with Code)
- **Sample Size:** Limited to 20 benchmarks due to manual coding time
- **Rater Time:** 3-4 days per rater for 20 benchmarks × 4 dimensions
- **Prerequisite:** H-E1 must be COMPLETED with PASS (verified)

### Risks
- **Low inter-rater reliability (kappa < 0.8):** Requires rubric refinement and re-coding
- **API unavailability:** Fallback to manual benchmark selection from Papers with Code website
- **Artifact access issues:** Some GitHub repos/dataset cards may be deleted or inaccessible
- **Low quality scores (mean < 7.0):** Triggers PIVOT to quality-weighted analysis in H-M2/H-M3

---

## Success Criteria Summary

### Must-Have (MUST_WORK Gate)
✅ **Data Collection:** 20 benchmarks sampled and artifacts retrieved successfully  
✅ **Measurement Validity:** Cohen's kappa > 0.8  
✅ **Primary Criterion:** Mean artifact quality > 7.0  

### Gate Decision Logic
```
IF kappa < 0.8:
    → Measurement unreliable, refine rubric and re-code
ELIF mean_quality < 7.0:
    → PIVOT: Artifacts lack information (H-M1 fails)
    → Update H-M2/H-M3 to use quality-weighted analysis
ELSE:
    → PASS: Artifacts contain actionable information, proceed to H-M2
```

### Nice-to-Have
- Domain-specific insights (CV vs NLP comparison)
- Dimension-level quality patterns
- Visualization suite for exploratory analysis

---

## Open Questions
1. **Rubric Calibration:** Final rubric scoring criteria may need adjustment after pilot test
2. **Sample Representativeness:** N=20 provides initial evidence but may need expansion for generalizability
3. **Artifact Evolution:** Quality may vary by publication year (2019 vs 2024 standards)

---

## Appendix: Reference Methodologies

### Inter-Rater Reliability
- **Source:** Scikit-learn documentation
- **Standard:** Cohen's kappa for categorical agreement
- **Threshold:** ≥ 0.80 for excellent reliability (Krippendorff 2018)

### Quantitative Content Analysis
- **Framework:** Krippendorff, K. (2018). Content Analysis: An Introduction to Its Methodology (4th ed.)
- **Best Practice:** 2+ independent raters, kappa > 0.80

### Artifact Quality Frameworks
- **FAIR Principles:** Findability, Accessibility, Interoperability, Reusability
- **Croissant-RAI:** Structured metadata format for ML datasets (Jain et al. 2024)

---

**Document Status:** Ready for Phase 3 Implementation Planning  
**Next Phase:** Architecture Design (Step 3)  
