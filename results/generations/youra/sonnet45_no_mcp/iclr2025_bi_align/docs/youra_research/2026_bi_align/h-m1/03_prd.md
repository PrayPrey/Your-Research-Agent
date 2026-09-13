# Product Requirements Document: h-m1 Annotation Consistency Study

**Hypothesis ID:** h-m1  
**Hypothesis Type:** MECHANISM (Step 1)  
**Date:** 2026-04-19  
**Author:** anonymous@anonymous.org

---

## 1. Executive Summary

This PRD specifies the implementation requirements for h-m1, which validates the annotation consistency mechanism in the HH-RLHF dataset. The experiment tests whether explicit criteria training improves inter-annotator agreement to substantial levels (Cohen's κ ≥ 0.70) and alignment with original labels (≥75% agreement).

**Success Criteria:**
- Primary: Average pairwise Cohen's κ ≥ 0.70
- Secondary: Mean agreement with HH-RLHF original labels ≥ 75%

**Gate Type:** SHOULD_WORK

---

## 2. Problem Statement

### 2.1 Background

h-e1 established that 45.6% of HH-RLHF rejected responses contain genuine safety violations. However, inter-rater agreement was only fair (κ=0.498), suggesting high annotator variability. h-m1 tests whether explicit criteria training can reduce this variability.

### 2.2 Research Question

Does training annotators with explicit HH-RLHF harmlessness criteria improve annotation consistency compared to untrained annotation?

### 2.3 Hypothesis Statement

Under controlled annotation conditions, if human annotators evaluate response pairs using HH-RLHF harmlessness criteria, then inter-annotator agreement will be substantial (κ ≥ 0.70) and align with original HH-RLHF labels (≥75% agreement), because explicit criteria reduce subjective variation in violation detection.

---

## 3. Functional Requirements

### FR-1: Annotator Recruitment and Training

**Description:** Recruit and train 3 annotators with explicit HH-RLHF criteria.

**Acceptance Criteria:**
- 3 annotators recruited with NLP/safety background
- Training protocol implemented (30min guidelines + 30min calibration)
- Calibration check: Each annotator achieves κ ≥ 0.60 on 50 practice samples
- Annotation guidelines document created from HH-RLHF paper

**Priority:** Critical  
**Dependencies:** None

### FR-2: Data Sampling and Preparation

**Description:** Create stratified sample of 300 response pairs from HH-RLHF harmless subset.

**Acceptance Criteria:**
- 300 pairs sampled (100 per violation type from h-e1 taxonomy)
- Stratified sampling by violation type (harmful_content, misinformation, instruction_violation)
- Seed=42 for reproducibility
- Presentation order randomized per annotator
- Original labels stored but hidden from annotators

**Priority:** Critical  
**Dependencies:** h-e1 completion (violation taxonomy)

### FR-3: Annotation Interface

**Description:** Implement annotation collection interface (web-based or CSV-based).

**Acceptance Criteria:**
- Binary choice interface (chosen=0, rejected=1)
- Randomized sample presentation per annotator
- Independent annotation (no cross-annotator visibility)
- Progress tracking per annotator
- Uncertain case flagging option

**Priority:** High  
**Dependencies:** FR-2

### FR-4: Agreement Calculation

**Description:** Compute inter-annotator agreement metrics.

**Acceptance Criteria:**
- Pairwise Cohen's κ for all annotator pairs (3 pairs total)
- Average pairwise κ calculation
- Agreement rate with original HH-RLHF labels per annotator
- Mean agreement rate across all annotators

**Priority:** Critical  
**Dependencies:** FR-3

### FR-5: Statistical Testing

**Description:** Test hypothesis support with statistical significance.

**Acceptance Criteria:**
- One-sample t-test: H0: κ < 0.60 vs H1: κ ≥ 0.70
- α = 0.05 significance level
- Effect size calculation
- Confidence intervals for κ and agreement rates

**Priority:** High  
**Dependencies:** FR-4

### FR-6: Visualization

**Description:** Generate required visualizations for results.

**Acceptance Criteria:**
- Gate metrics comparison (target vs actual bar chart)
- Inter-annotator agreement matrix (3×3 heatmap)
- Agreement distribution per annotator (bar chart with 75% threshold)
- Confusion matrices per annotator vs original labels

**Priority:** Medium  
**Dependencies:** FR-4

---

## 4. Data Specification

### 4.1 Primary Dataset

**Dataset:** HH-RLHF harmless subset  
**Source:** Anthropic via HuggingFace Hub  
**Identifier:** "Anthropic/hh-rlhf", subset "harmless-base"  
**License:** MIT  
**Size:** ~160K pairs (full), 300 pairs (experiment sample)

**Loading:**
```python
from datasets import load_dataset
dataset = load_dataset("Anthropic/hh-rlhf", "harmless-base")
```

**Auto-download:** Yes (via HuggingFace datasets library)

### 4.2 Sampling Strategy

- Stratified random sampling by violation type (3 types from h-e1)
- 100 pairs per type = 300 total
- Seed: 42
- Remove duplicates
- Shuffle presentation order per annotator

### 4.3 Calibration Sample

- 50 pairs for annotator training
- Separate from 300-pair test set
- Gold standard labels for feedback

---

## 5. Model Specification

### 5.1 Baseline: Original HH-RLHF Annotations

**Type:** Human annotation ground truth  
**Purpose:** Comparison standard for alignment measurement  
**Access:** Original labels included in dataset

### 5.2 Proposed: Trained Annotator Protocol

**Type:** Human annotation with explicit criteria training  
**Components:**
- HH-RLHF annotation guidelines document
- 30min guideline presentation
- 50-sample calibration with feedback
- Independent annotation phase (300 samples)

**Mechanism:** Explicit criteria reduce subjective variation in violation detection

---

## 6. Evaluation Metrics

### 6.1 Primary Metric

**Cohen's Kappa (Average Pairwise)**

- Definition: Average of 3 pairwise κ values between annotators
- Target: κ ≥ 0.70 (substantial agreement)
- Interpretation: κ < 0.40 (poor), 0.40-0.60 (moderate), 0.60-0.80 (substantial), >0.80 (almost perfect)
- Implementation: `sklearn.metrics.cohen_kappa_score`

### 6.2 Secondary Metric

**Agreement with HH-RLHF Labels**

- Definition: Mean proportion of matches with original labels across 3 annotators
- Target: ≥ 75% agreement
- Calculation: `(matches / 300)` per annotator, then averaged

### 6.3 Baseline Comparison

- h-e1 untrained baseline: κ = 0.498 (fair)
- Expected improvement: +0.15 to +0.25
- Target improvement: κ ≥ 0.70 (substantial)

---

## 7. Dependencies and Infrastructure

### 7.1 Python Packages

```
datasets>=2.0.0
scikit-learn>=1.0.0
numpy>=1.20.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
pyyaml>=5.4.0
scipy>=1.7.0
```

### 7.2 External Resources

- HuggingFace datasets library (auto-download)
- HH-RLHF paper (Bai et al. 2022) for annotation guidelines

### 7.3 Infrastructure

- Standard CPU compute (no GPU required)
- Web server for annotation interface (optional, can use CSV)
- ~1GB storage for dataset cache

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility

- All random operations use seed=42
- Annotation order randomization tracked per annotator
- Complete audit trail of all annotations

### NFR-2: Data Quality

- Calibration gate: κ ≥ 0.60 required to proceed to main annotation
- Progress tracking prevents incomplete annotations
- Uncertain case flagging for quality review

### NFR-3: Execution Time

- Annotator training: 1 hour per annotator
- Main annotation: 2-3 hours per annotator
- Total experiment duration: 1-2 days (parallel annotation)

### NFR-4: Ethical Considerations

- Annotators informed of content nature (safety violations)
- Break options during annotation
- Content warnings provided

---

## 9. Success Criteria and Gate Conditions

### 9.1 SHOULD_WORK Gate

**Primary Condition:** Cohen's κ ≥ 0.70  
**Secondary Condition:** Agreement with HH-RLHF ≥ 75%  
**Both must pass for gate success**

### 9.2 Failure Actions

**If κ < 0.60 (below moderate):**
- Action: EXPLORE refined annotation criteria
- Alternative: Expert-only annotation subset
- Fallback: Increase training duration or sample size

**If 0.60 ≤ κ < 0.70 (moderate but not substantial):**
- Action: PARTIAL result - some improvement documented
- Consideration: Sufficient for downstream use with caveats

### 9.3 Mechanism Validation

**Success indicators:**
- Calibration phase: All annotators achieve κ ≥ 0.60
- Main phase: Average κ ≥ 0.70
- Improvement over h-e1: Δκ > +0.15

---

## 10. Risks and Mitigations

### Risk 1: Annotator Fatigue

**Impact:** Degraded annotation quality over time  
**Mitigation:** Progress tracking, break reminders, session limits

### Risk 2: Training Ineffectiveness

**Impact:** κ remains below 0.60 after calibration  
**Mitigation:** Extended training, clearer examples, expert consultation

### Risk 3: Guidelines Misalignment

**Impact:** High inter-annotator agreement but low alignment with original  
**Mitigation:** Calibration samples drawn from same distribution as test set

---

## 11. Phase 2C Completeness Check

### Datasets
✓ HH-RLHF harmless subset specified  
✓ Sampling strategy defined (stratified, 300 samples)  
✓ Calibration set specified (50 samples)

### Models
✓ Baseline: Original HH-RLHF annotations  
✓ Proposed: Trained annotator protocol with explicit criteria

### Evaluation Metrics
✓ Primary: Cohen's κ (pairwise average)  
✓ Secondary: Agreement with original labels  
✓ Statistical test: One-sample t-test specified

### Ablation Variants
N/A - This is an annotation consistency study, not a model ablation

---

## 12. Implementation Priority

**Phase 4 Implementation Order:**
1. Data preparation (sampling, stratification)
2. Environment setup (packages, annotation interface)
3. Annotator training protocol implementation
4. Annotation collection
5. Metric calculation and statistical testing
6. Visualization generation

**Critical Path:** Training → Calibration → Annotation → Analysis

---

## Appendix: h-e1 Context

**Previous Result:** κ = 0.498 (fair agreement) without training  
**Baseline Rate:** 45.6% genuine violations  
**Sample Size:** 500 (h-e1) → 300 (h-m1, focused consistency study)  
**Lesson:** Training and explicit criteria needed for substantial agreement
