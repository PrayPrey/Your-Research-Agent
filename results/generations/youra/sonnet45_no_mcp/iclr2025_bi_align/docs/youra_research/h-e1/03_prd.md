# Product Requirements Document (PRD)
# Hypothesis h-e1: Base-Rate Validation Study

**Date:** 2026-04-19  
**Author:** Anonymous
**Hypothesis:** h-e1 (EXISTENCE)  
**Phase:** Phase 3 - Implementation Planning  
**Budget Tier:** LIGHT (≤15 tasks)

---

## Executive Summary

### Project Overview
Validate the foundational assumption that HH-RLHF rejected responses contain genuine safety policy violations rather than marginal preference differences. This human annotation study will audit 500 rejected samples from the HH-RLHF harmless subset using blinded 3-annotator review to determine if the base-rate of genuine violations meets the ≥40% threshold required for downstream geometric analysis.

### Problem Statement
The entire geometric manifold hypothesis depends on rejected responses encoding genuine alignment failures. If the base-rate of genuine violations is below 40%, label noise dominates and no meaningful geometric structure can emerge. This MUST_WORK gate experiment validates whether the HH-RLHF dataset has sufficient signal for the research program.

### Success Criteria (MUST_WORK Gate)
- **Primary:** Base-rate p ≥ 0.40 genuine violations (binomial test p-value < 0.05)
- **Secondary:** Inter-annotator agreement κ ≥ 0.75 (substantial agreement)
- **Failure Action:** STOP entire workflow → reassess hypothesis or pivot framing

---

## Functional Requirements

### FR-1: Dataset Acquisition and Sampling
**Priority:** P0 (Critical)  
**Description:** Download HH-RLHF harmless subset and perform stratified random sampling of 500 rejected responses.

**Acceptance Criteria:**
- Load `Anthropic/hh-rlhf` dataset from Hugging Face
- Extract harmless-base subset (rejected responses only)
- Stratify by response length quartiles to avoid length bias
- Generate 500-sample dataset for annotation
- Save sample IDs and metadata for reproducibility

**Dependencies:** None

---

### FR-2: Annotation Protocol Implementation
**Priority:** P0 (Critical)  
**Description:** Implement blinded annotation interface for 3 independent annotators with explicit violation criteria.

**Acceptance Criteria:**
- Web-based or spreadsheet annotation interface
- Blinded presentation (no original HH-RLHF labels shown)
- Explicit violation criteria display:
  1. Direct harm/violence encouragement
  2. Toxic/offensive language
  3. Privacy violations or personal information disclosure
  4. Dangerous/illegal advice
  5. Deception or misinformation
  6. Other safety policy violations
- Binary judgment per sample: "genuine violation" vs "marginal preference"
- Independent annotation (no inter-annotator communication during production phase)
- CSV export of annotations (annotator_id, sample_id, judgment)

**Dependencies:** FR-1

---

### FR-3: Inter-Annotator Agreement Calculation
**Priority:** P0 (Critical)  
**Description:** Compute Cohen's κ across 3 annotators to validate annotation reliability.

**Acceptance Criteria:**
- Load annotation results from all 3 annotators
- Compute pairwise Cohen's κ for all annotator pairs
- Calculate aggregate κ across all 3 annotators
- Require κ ≥ 0.60 on calibration set before production
- Report κ with 95% confidence intervals
- Use statsmodels.stats.inter_rater.cohens_kappa

**Dependencies:** FR-2

---

### FR-4: Base-Rate Computation and Statistical Test
**Priority:** P0 (Critical)  
**Description:** Calculate proportion of genuine violations and test H0: p < 0.40 vs H1: p ≥ 0.40.

**Acceptance Criteria:**
- Apply majority vote across 3 annotators for final labels
- Calculate base-rate: p = (# genuine violations) / 500
- Execute one-tailed binomial test (scipy.stats.binomtest)
  - Null hypothesis: p < 0.40
  - Alternative: p ≥ 0.40
  - Significance level: α = 0.05
- Report: base-rate p, test statistic, p-value, 95% CI
- PASS gate if p ≥ 0.40 AND p-value < 0.05

**Dependencies:** FR-2, FR-3

---

### FR-5: Violation Type Distribution Analysis
**Priority:** P1 (Important)  
**Description:** Analyze which violation criteria are most common among genuine violations.

**Acceptance Criteria:**
- Extract violation type annotations from annotators
- Compute frequency distribution across 6 criteria categories
- Generate bar chart showing violation type frequencies
- Report top-3 most common violation types with percentages

**Dependencies:** FR-2, FR-4

---

### FR-6: Length Bias Analysis
**Priority:** P1 (Important)  
**Description:** Verify stratified sampling eliminated length bias in violation detection.

**Acceptance Criteria:**
- Group samples by length quartiles
- Calculate violation rate per quartile
- Test for significant differences across quartiles (chi-square test)
- Generate scatter plot: violation rate vs response length quartile
- Report: "No significant length bias" if p > 0.05

**Dependencies:** FR-1, FR-4

---

### FR-7: Agreement with Original HH-RLHF Labels
**Priority:** P2 (Nice to have)  
**Description:** Compare majority-vote annotations with original HH-RLHF rejected labels.

**Acceptance Criteria:**
- Load original HH-RLHF labels for sampled responses
- Compute agreement proportion with majority-vote labels
- Generate confusion matrix visualization
- Report agreement percentage and Cohen's κ with HH-RLHF

**Dependencies:** FR-1, FR-4

---

## Non-Functional Requirements

### NFR-1: Annotation Time Efficiency
**Target:** ≤3 hours per annotator for 500 samples (≤22 seconds per sample)

### NFR-2: Data Reproducibility
- Save random seed for stratified sampling
- Export sample IDs, metadata, and all annotations to CSV
- Document annotation protocol in README

### NFR-3: Statistical Validity
- Use standard statistical libraries (scipy, statsmodels)
- Report all test assumptions and violations
- Include 95% confidence intervals for all estimates

### NFR-4: Minimal Infrastructure (LIGHT Tier)
- Hardcoded or argparse configuration (no YAML needed)
- Print statements + CSV logging (no WandB)
- Smoke test coverage only (basic sanity checks)

---

## Data Requirements

### Input Data
- **Source:** Hugging Face Datasets API
- **Dataset:** Anthropic/hh-rlhf (harmless-base subset)
- **Split:** train (rejected responses only)
- **Sample Size:** 500 responses (stratified by length quartiles)
- **Format:** Pandas DataFrame with columns: sample_id, response_text, length_quartile

### Output Data
- **Annotations:** CSV with columns: annotator_id, sample_id, judgment (0/1), violation_type
- **Results:** JSON with keys: base_rate, kappa, p_value, confidence_interval, gate_status
- **Figures:** PNG files saved to h-e1/figures/

---

## Evaluation Metrics

### Primary Metrics (Gate Condition)
1. **Base-rate (p):** Proportion of genuine violations
   - **Target:** p ≥ 0.40
   - **Test:** Binomial test (α = 0.05, one-tailed)
   
2. **Inter-annotator Agreement (κ):** Cohen's κ across 3 annotators
   - **Target:** κ ≥ 0.75 (substantial agreement)
   - **Interpretation:** κ < 0.60 (poor), 0.60-0.75 (moderate), ≥0.75 (substantial)

### Secondary Metrics
3. **Agreement with HH-RLHF:** Proportion matching original labels
4. **Violation Type Distribution:** Frequency of each violation category
5. **Length Bias:** Chi-square test across quartiles

---

## Technical Architecture

### Components
1. **Data Loader:** Download and sample HH-RLHF dataset
2. **Annotation Interface:** Web form or Google Sheets template
3. **Statistical Analysis:** Python scripts using scipy + statsmodels
4. **Visualization:** Matplotlib/seaborn for figures

### Technology Stack (LIGHT Tier)
- **Language:** Python 3.8+
- **Libraries:** 
  - datasets (Hugging Face)
  - pandas, numpy
  - scipy.stats (binomtest)
  - statsmodels.stats.inter_rater (cohens_kappa)
  - matplotlib, seaborn
- **Configuration:** argparse or hardcoded parameters
- **Logging:** print() + CSV export

---

## Dependencies and Prerequisites

### External Dependencies
- HH-RLHF dataset availability on Hugging Face
- 3 human annotators with ~3 hours availability each
- Python environment with scientific computing stack

### Internal Dependencies
- Phase 2C experiment brief (02c_experiment_brief.md) ✓
- No prerequisite hypotheses (foundation hypothesis)

---

## Implementation Constraints

### Budget Constraints (LIGHT Tier)
- **Maximum Tasks:** 15 implementation tasks
- **Epic Range:** 4-8 epics
- **Infrastructure Level:** Minimal (hardcoded config, print logging, smoke tests)

### Time Constraints
- Annotator training: 1 hour
- Calibration phase: 50 samples with discussion
- Production annotation: ~2-3 hours per annotator
- Statistical analysis: 1-2 hours coding + execution

### Quality Constraints
- Must achieve κ ≥ 0.60 on calibration before production
- Must sample all 4 length quartiles evenly
- Must use standard statistical libraries (no custom implementations)

---

## Risks and Mitigations

### Risk 1: Low Inter-Annotator Agreement (κ < 0.60)
**Impact:** Cannot trust annotation results  
**Likelihood:** Medium  
**Mitigation:**
- 1-hour training session on HH-RLHF criteria
- 50-sample calibration with discussion
- Require κ ≥ 0.60 before production

### Risk 2: Base-Rate Below Threshold (p < 0.40)
**Impact:** MUST_WORK gate fails → STOP entire workflow  
**Likelihood:** Medium  
**Mitigation:**
- None (this is the hypothesis being tested)
- Failure action: Reassess hypothesis or pivot framing

### Risk 3: Annotator Fatigue Affecting Quality
**Impact:** Declining annotation quality over time  
**Likelihood:** Low  
**Mitigation:**
- Limit to 3 hours per annotator (≤22 sec/sample is reasonable)
- Randomize sample order to distribute difficulty
- Allow breaks every 100 samples

---

## Success Metrics Summary

**MUST_WORK Gate PASS Condition:**
✅ Base-rate p ≥ 0.40 AND binomial test p-value < 0.05

**Secondary Quality Checks:**
✅ Inter-annotator agreement κ ≥ 0.75  
✅ No significant length bias (chi-square p > 0.05)  
✅ All 500 samples annotated by 3 independent annotators

**Implementation Compliance (LIGHT Tier):**
✅ Total tasks ≤ 15  
✅ Minimal infrastructure (no YAML, no WandB)  
✅ Smoke test coverage only

---

## Appendix: Phase 2C Traceability

**Source:** h-e1/02c_experiment_brief.md

| Phase 2C Item | PRD Reference |
|---------------|---------------|
| Dataset: HH-RLHF harmless subset | FR-1 |
| Sample Size: 500 rejected responses | FR-1 |
| Sampling Strategy: Stratified by length quartiles | FR-1 |
| Annotation Protocol: Blinded 3-annotator review | FR-2 |
| Primary Metric: Base-rate p with binomial test | FR-4 |
| Secondary Metric: Cohen's κ | FR-3 |
| Gate Condition: p ≥ 0.40, p-value < 0.05 | FR-4 |
| Visualization: Bar chart (gate metrics) | FR-4, FR-5 |
| Additional Figures: IAA matrix, violation types, length bias | FR-3, FR-5, FR-6 |

---

*Generated by Phase 3 Implementation Planning (Step 2)*  
*Next: Architecture Design (Step 3)*
