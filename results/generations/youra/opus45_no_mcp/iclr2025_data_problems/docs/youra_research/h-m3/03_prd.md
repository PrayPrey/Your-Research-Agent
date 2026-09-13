# Product Requirements Document: H-M3

**Hypothesis:** Representation Invariance Manifests as Uniform Confidence
**Date:** 2026-08-19
**Phase:** 3 - Implementation Planning
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Executive Summary

This PRD specifies implementation requirements for H-M3, which tests whether representation invariance (validated in H-M2) manifests as uniform confidence scores across paraphrases. The experiment uses inference-only analysis on H-M2 trained checkpoints, computing correlation between representation variance and confidence variance across MMLU items.

**Success Criteria:** Pearson r < -0.4 (negative correlation)

---

## Problem Statement

H-M2 established that paraphrase-augmented training creates representation invariance (MPS diff 0.065, d=0.52). H-M3 tests the next causal link: does this invariance translate to uniform confidence scores? This is critical for validating the SSI contamination detection mechanism.

---

## Functional Requirements

### FR-1: Representation Extraction Pipeline

**Description:** Extract hidden states from model forward passes for original items and paraphrases
**Source:** H-M2 validated implementation
**Priority:** P0

- Extract last-layer hidden states at final token position
- Support batch processing for efficiency
- Handle variable-length paraphrase sets (K=5 per item)

### FR-2: Confidence Score Extraction

**Description:** Extract probability of correct answer for each item/paraphrase
**Source:** Phase 2C experiment brief
**Priority:** P0

- Compute softmax probabilities from logits
- Extract P(correct_answer) for MMLU multiple-choice format
- Support A/B/C/D answer token extraction

### FR-3: Variance Computation Module

**Description:** Compute representation variance and confidence variance per item
**Source:** Phase 2C specification
**Priority:** P0

- Representation variance: 1 - mean pairwise cosine similarity
- Confidence variance: np.var(confidence_scores)
- Output: (rep_variance, conf_variance) per item

### FR-4: Correlation Analysis

**Description:** Compute and test correlation between variances
**Source:** Phase 2C evaluation specification
**Priority:** P0

- Primary: Pearson correlation
- Secondary: Spearman correlation
- Group comparison: high-MPS vs low-MPS items
- Statistical significance (p-value)

### FR-5: H-M2 Checkpoint Loading

**Description:** Load trained models from H-M2 validation
**Source:** H-M2 outputs
**Priority:** P0

- Load verbatim-trained checkpoint
- Load paraphrase-trained checkpoint
- Support LoRA adapter loading via PEFT

### FR-6: MMLU Dataset Loading

**Description:** Load full MMLU test set with paraphrases
**Source:** Phase 2C dataset specification
**Priority:** P0

- Load 14,042 MMLU test items
- Load K=5 paraphrases per item (from H-M2)
- Preserve answer labels

### FR-7: Figure Generation

**Description:** Generate required visualizations
**Source:** Phase 2C visualization requirements
**Priority:** P1

- Gate metrics bar chart (target r vs actual r)
- Scatter plot: rep_variance vs conf_variance
- Box plot: confidence variance by MPS group
- Histogram: correlation distribution across seeds

---

## Non-Functional Requirements

### NFR-1: Statistical Validity
- Full test set (14,042 items), NOT trivially small samples
- Multiple seeds (42, 123, 456)
- Report confidence intervals

### NFR-2: Reproducibility
- Deterministic operations (fixed seeds)
- Version-pinned dependencies
- Checkpoint verification

### NFR-3: Performance
- Batch processing for hidden state extraction
- fp16 inference
- Target: ~2 hours per model variant on H100

---

## Success Criteria

### Primary Gate Condition
- Pearson r < -0.4 between representation_variance and confidence_variance

### Secondary Metrics
- High-MPS items have lower confidence variance than low-MPS items
- Spearman correlation negative
- Effect size (Cohen's d) > 0.3 between groups

---

## Data Requirements

### Input Data
| Data | Source | Format |
|------|--------|--------|
| MMLU test set | cais/mmlu (HuggingFace) | 14,042 items |
| Paraphrases | H-M2 generated | K=5 per item |
| H-M2 checkpoints | h-m2/checkpoints/ | LoRA adapters |

### Output Data
| Data | Path | Format |
|------|------|--------|
| Correlation results | h-m3/results.json | JSON |
| Figures | h-m3/figures/ | PNG |
| Validation report | h-m3/04_validation.md | Markdown |

---

## Dependencies

### Prerequisite Hypotheses
- H-M2: PASS (MPS diff 0.065, d=0.52)
  - Provides: Trained checkpoints, paraphrase data

### Software Dependencies
- transformers >= 4.35.0
- peft >= 0.6.0
- torch >= 2.0
- scipy >= 1.10
- numpy
- matplotlib

---

## Ablation Variants

### A1: Single vs Multi-seed Analysis
Test correlation stability across 3 seeds

### A2: Per-subject Correlation
Analyze correlation per MMLU subject (57 subjects)

### A3: MPS Threshold Sensitivity
Test different MPS thresholds for high/low grouping

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| H-M2 checkpoints unavailable | High | Verify checkpoint paths before execution |
| Correlation weak but negative | Medium | Report effect size alongside r value |
| Computational timeout | Low | Use batched inference, fp16 |

---

*Generated for Phase 3 Implementation Planning*
*Hypothesis: H-M3 - Representation Invariance → Confidence Uniformity*
