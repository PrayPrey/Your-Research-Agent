# Product Requirements Document: H-M4

**Hypothesis:** SSI Captures Invariance as Contamination Signal
**Date:** 2026-08-19
**Author:** PrayPrey
**Phase:** 3 - Implementation Planning
**Type:** MECHANISM

---

## Executive Summary

This PRD specifies requirements for validating that the Semantic Saturation Index (SSI = 1/variance) transforms confidence variance patterns into an effective contamination detection metric. Building on H-M3's validated correlation between representation invariance and confidence uniformity (r=-0.517), H-M4 demonstrates SSI achieves AUC > 0.7 for contamination classification and Pearson r > 0.6 between contamination percentage and mean SSI.

---

## Problem Statement

Contaminated models exhibit uniform confidence across paraphrases (validated in H-M3). The SSI metric must transform this variance signal into a usable contamination classifier. Success validates the complete SSI detection pipeline.

---

## Functional Requirements

### FR-1: SSI Computation Module

**Description:** Compute SSI = 1/(variance + epsilon) for item-level confidence scores across K paraphrases.

**Acceptance Criteria:**
- Input: confidence matrix shape (N_items, K_paraphrases)
- Output: SSI values shape (N_items,)
- Numerical stability with epsilon=1e-8
- Batch processing support for 14,042 items

### FR-2: Confidence Extraction Pipeline

**Description:** Extract confidence scores from model checkpoints on paraphrased MMLU items.

**Acceptance Criteria:**
- Load checkpoints from H-M1 (5 contamination levels: 0%, 5%, 10%, 20%, 50%)
- Process K=20 paraphrases per item (from H-E1)
- Extract softmax confidence for correct answer option
- Store in confidence matrix format

### FR-3: AUC Classification Evaluation

**Description:** Evaluate SSI as binary classifier (clean vs contaminated).

**Acceptance Criteria:**
- Compute ROC AUC using sklearn.metrics.roc_auc_score
- Primary threshold: AUC > 0.7
- Generate ROC curve visualization

### FR-4: Correlation Analysis

**Description:** Compute Pearson correlation between contamination level and mean SSI.

**Acceptance Criteria:**
- Aggregate mean SSI per contamination level (5 data points)
- Compute Pearson r with scipy.stats.pearsonr
- Secondary threshold: r > 0.6
- Generate correlation scatter plot

### FR-5: Effect Size Computation

**Description:** Compute Cohen's d between clean (0%) and contaminated (50%) SSI distributions.

**Acceptance Criteria:**
- Effect size d > 0.5 threshold
- Report statistical significance (p-value)

### FR-6: Visualization Suite

**Description:** Generate all required experimental figures.

**Required Figures:**
1. SSI distribution violin/box plot by contamination level
2. ROC curve with AUC annotation
3. Correlation scatter (mean SSI vs contamination %)
4. Gate metrics comparison bar chart

---

## Non-Functional Requirements

### NFR-1: Performance

- Process 14,042 items × 20 paraphrases × 5 models efficiently
- Total forward passes: 1,404,200 (reuse cached if available)

### NFR-2: Reproducibility

- Fixed random seeds: [42, 123, 456]
- Deterministic numpy/torch operations

### NFR-3: Memory

- Support batch inference on single A100 GPU
- Batch size configurable based on available memory

---

## Data Requirements

### Dataset

| Attribute | Value |
|-----------|-------|
| Name | MMLU |
| Size | 14,042 items |
| Split | Full test set |
| Paraphrases | K=20 per item (from H-E1) |

### Models (Reuse from H-M1)

| Contamination Level | Checkpoint |
|---------------------|------------|
| 0% (clean) | mistral-7b-mmlu-0pct |
| 5% | mistral-7b-mmlu-5pct |
| 10% | mistral-7b-mmlu-10pct |
| 20% | mistral-7b-mmlu-20pct |
| 50% | mistral-7b-mmlu-50pct |

---

## Success Criteria

### Primary (Gate Pass)
- AUC > 0.7 for SSI-based contamination classification

### Secondary
- Pearson r > 0.6 between contamination % and mean SSI
- Effect size (Cohen's d) > 0.5

### Gate Logic
- **PASS:** Both primary and secondary met
- **PARTIAL:** Primary met, secondary not met
- **FAIL:** Primary not met → EXPLORE alternative metric

---

## Dependencies

### Prerequisites (Validated)
- H-M3: PASS (r=-0.517, d=0.58)
- H-M2: PASS (MPS difference 0.065)
- H-M1: PASS (Effect size 31.1%)
- H-E1: PASS (Asymmetry ratio 5.07x)

### Reused Artifacts
- Paraphrase sets from H-E1
- Model checkpoints from H-M1
- Confidence extraction code from H-M3

---

## Out of Scope

- New model training (inference only)
- New paraphrase generation
- Alternative metric formulations (only if gate fails)
