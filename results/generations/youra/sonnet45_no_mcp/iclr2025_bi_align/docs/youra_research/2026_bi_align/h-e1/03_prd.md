# Product Requirements Document (PRD)
# Hypothesis: H-E1 - Base-Rate Validation Study

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE  
**Gate Type:** MUST_WORK

---

## 1. Executive Summary

### 1.1 Product Vision
Validate the base-rate of genuine safety policy violations in HH-RLHF dataset's rejected responses through blinded human annotation study.

### 1.2 Success Criteria
- **Primary Gate:** Base-rate p ≥ 0.40 with binomial test p-value < 0.05
- **Secondary:** Cohen's κ ≥ 0.75 (substantial inter-annotator agreement)

### 1.3 Core Hypothesis
Under the scope of HH-RLHF harmless-preference annotation, if we perform blinded human audit of rejected samples, then we will find ≥40% contain genuine safety policy violations (not marginal preferences), because annotators used explicit harmlessness criteria that distinguish violations from style differences.

---

## 2. Problem Statement

### 2.1 Research Question
What proportion of HH-RLHF rejected responses contain genuine safety policy violations versus marginal stylistic preferences?

### 2.2 Current Gap
Existing HH-RLHF dataset documentation does not quantify the base-rate of genuine safety violations in rejected responses.

### 2.3 Impact
This validation determines if the dataset provides sufficient signal for downstream geometric analysis hypotheses (H-M1 through H-M4).

---

## 3. Target Users & Stakeholders

### 3.1 Primary Users
- Research team conducting RLHF alignment failure analysis

### 3.2 Stakeholders
- Annotators (3 independent raters)
- Downstream hypothesis validation (H-M1, H-M2, H-M3, H-M4)

---

## 4. Data Specification

### 4.1 Primary Dataset

**Dataset:** HH-RLHF harmless subset  
**Source:** Hugging Face Datasets (Anthropic/hh-rlhf)  
**URL:** https://huggingface.co/datasets/Anthropic/hh-rlhf  
**Subset:** harmless-base (rejected responses only)  
**Sample Size:** 500 rejected responses (stratified random sampling)  
**Sampling Strategy:** Stratified by response length quartiles to avoid length bias

**Loading Method:**
```python
from datasets import load_dataset
dataset = load_dataset("Anthropic/hh-rlhf", "harmless-base")
rejected_samples = dataset['train']['rejected']
```

### 4.2 Violation Criteria (Annotation Guidelines)

1. Direct harm/violence encouragement
2. Toxic/offensive language
3. Privacy violations or personal information disclosure
4. Dangerous/illegal advice
5. Deception or misinformation
6. Other safety policy violations

### 4.3 Data Outputs

- Annotation results CSV (500 samples × 3 annotators)
- Inter-annotator agreement matrix
- Majority-vote final labels
- Statistical test results

---

## 5. Functional Requirements

### FR-1: Data Sampling
**Priority:** High  
**Description:** Implement stratified random sampling of 500 rejected responses from HH-RLHF harmless-base subset  
**Acceptance Criteria:**
- Sampling stratified by response length quartiles
- Reproducible seed for sampling
- Balanced distribution across length strata

### FR-2: Annotation Interface
**Priority:** High  
**Description:** Provide annotation interface for 3 independent annotators  
**Acceptance Criteria:**
- Blinded to original HH-RLHF labels
- Present violation criteria checklist
- Binary judgment: genuine violation vs. marginal preference
- Support for 3 independent annotators

### FR-3: Inter-Annotator Agreement Calculation
**Priority:** High  
**Description:** Compute Cohen's κ across 3 annotators  
**Acceptance Criteria:**
- Use statsmodels.stats.inter_rater.cohens_kappa
- Report pairwise κ for all annotator pairs
- Overall multi-rater κ

### FR-4: Majority Vote Labeling
**Priority:** High  
**Description:** Determine final labels using majority vote from 3 annotators  
**Acceptance Criteria:**
- Tie-breaking strategy defined
- Final label set generated

### FR-5: Base-Rate Calculation
**Priority:** High (MUST_WORK gate)  
**Description:** Calculate proportion of genuine violations in final labeled set  
**Acceptance Criteria:**
- Base-rate p = (genuine violations) / (total samples)
- 95% confidence interval reported

### FR-6: Binomial Test
**Priority:** High (MUST_WORK gate)  
**Description:** Statistical test for H0: p < 0.40 vs H1: p ≥ 0.40  
**Acceptance Criteria:**
- Use scipy.stats.binomtest
- One-tailed test with α = 0.05
- Report p-value and decision

### FR-7: Visualization Generation
**Priority:** Medium  
**Description:** Generate required figures for analysis  
**Acceptance Criteria:**
- Bar chart: base-rate vs threshold (0.40)
- Heatmap: inter-annotator agreement matrix
- Bar chart: violation type distribution
- Scatter: violation rate vs response length quartile

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed for sampling
- Version-controlled annotation guidelines
- Logged annotator training sessions

### NFR-2: Statistical Rigor
- Binomial test α = 0.05
- Cohen's κ interpretation per Landis & Koch (1977)

### NFR-3: Annotation Quality
- Annotator training: 1-hour session on HH-RLHF criteria
- Calibration: 50-sample pilot with κ ≥ 0.60 requirement
- Production: blinded annotation with no inter-annotator communication

---

## 7. Dependencies & Constraints

### 7.1 Python Packages
```
datasets>=2.14.0
transformers>=4.30.0
scipy>=1.11.0
statsmodels>=0.14.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### 7.2 External Repositories
- Anthropic/hh-rlhf (Hugging Face Datasets)

### 7.3 Compute Requirements
- No GPU required (human annotation study)
- Annotation interface: web browser or spreadsheet

### 7.4 Time Constraints
- Annotation time: ~2-3 hours per annotator for 500 samples
- Total study duration: ~1-2 weeks (including training and calibration)

---

## 8. Success Metrics

### 8.1 Primary Metrics (MUST_WORK Gate)
1. **Base-rate p:** Proportion of genuine violations
   - Target: p ≥ 0.40
   - Test: Binomial test p-value < 0.05

### 8.2 Secondary Metrics
2. **Inter-annotator Agreement (κ):** Cohen's κ across 3 annotators
   - Target: κ ≥ 0.75 (substantial agreement)
   - Interpretation: κ < 0.60 (poor), 0.60-0.75 (moderate), ≥ 0.75 (substantial)

### 8.3 Tertiary Analysis
- Agreement with original HH-RLHF labels
- Violation type distribution
- Length bias analysis

---

## 9. Out of Scope

- Machine learning model training (human annotation only)
- Automated violation detection
- Multi-language annotation (English only)
- Annotation of chosen responses (rejected only)

---

## 10. Risks & Mitigations

### Risk 1: Low Base-Rate (p < 0.40)
**Severity:** Critical (MUST_WORK gate failure)  
**Mitigation:** If gate fails, reassess hypothesis framing or pivot research direction per Phase 2B guidance

### Risk 2: Poor Inter-Annotator Agreement (κ < 0.60)
**Severity:** High  
**Mitigation:** Extended annotator training, refined violation criteria, or expert-only annotation subset

### Risk 3: Annotator Fatigue
**Severity:** Medium  
**Mitigation:** Break annotation into multiple sessions, quality checks on calibration subset

---

## 11. Timeline & Phasing

**Phase 4 (PoC Validation):**
- Data sampling implementation
- Annotation interface setup
- Annotator training and calibration
- Production annotation (500 samples)
- Statistical analysis and visualization

**Phase 4.5 (Synthesis):**
- Result interpretation
- Gate decision (PASS/FAIL)
- Documentation for dependent hypotheses

---

## 12. Appendix

### 12.1 Reference Papers
1. Bai et al. (2022). "Training a Helpful and Harmless Assistant with RLHF" - HH-RLHF annotation guidelines
2. Cohen, J. (1960). "A coefficient of agreement for nominal scales" - Cohen's κ
3. Landis & Koch (1977). "The measurement of observer agreement" - κ interpretation

### 12.2 Related Hypotheses
- **H-M1:** Annotation consistency validation (depends on H-E1 PASS)
- **H-M2:** Geometric structure in embedding space (depends on H-M1)
- **H-M3:** Distance-severity correlation (depends on H-M2)
- **H-M4:** Multi-encoder validation (depends on H-M3)

---

**Document Status:** COMPLETE  
**Next Phase:** Phase 3 - Architecture Design
