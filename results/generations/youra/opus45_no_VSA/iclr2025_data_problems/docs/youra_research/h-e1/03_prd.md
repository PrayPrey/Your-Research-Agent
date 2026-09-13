# Product Requirements Document: H-E1

**Hypothesis:** Synthetic benchmark injection produces monotonic CCR scaling (R² ≥ 0.9) and validates detector precision (F1 > 0.8 at 0.1% injection)
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-08
**Gate:** MUST_WORK

---

## Executive Summary

Validate that Contamination Contribution Ratio (CCR) scales monotonically with synthetic benchmark injection rate, establishing foundational metrics for contamination detection research.

---

## Problem Statement

Need empirical validation that:
1. CCR metric responds predictably to known contamination levels
2. N-gram overlap detection achieves sufficient precision at low injection rates
3. TRAK attribution correctly identifies contaminated training samples

---

## Functional Requirements

### FR-1: Data Preparation
- **FR-1.1:** Load RedPajama-1B subset (1B tokens) as clean training corpus
- **FR-1.2:** Load MMLU test set (14,042 questions, 57 subjects)
- **FR-1.3:** Implement benchmark injection at rates [0.001, 0.01, 0.05, 0.1]
- **FR-1.4:** Verbalize MMLU as "Question: {q}\nAnswer: {a}" format

### FR-2: Model Training
- **FR-2.1:** Fine-tune Pythia-1B on each contaminated corpus
- **FR-2.2:** Use AdamW (lr=1e-4, weight_decay=0.01, betas=(0.9, 0.95))
- **FR-2.3:** Train 10,000 steps per injection level
- **FR-2.4:** Save checkpoints for attribution analysis

### FR-3: Contamination Detection
- **FR-3.1:** Implement 13-gram overlap detection
- **FR-3.2:** Integrate TRAK for data attribution
- **FR-3.3:** Compute CCR = contaminated_attribution / total_attribution

### FR-4: Evaluation
- **FR-4.1:** Measure MMLU accuracy per injection level
- **FR-4.2:** Compute detector F1 at each injection rate
- **FR-4.3:** Fit linear regression for CCR vs injection rate
- **FR-4.4:** Generate CCR scaling visualization

---

## Non-Functional Requirements

- **NFR-1:** Single GPU execution (RTX 3090 / A100 compatible)
- **NFR-2:** Reproducible with seed=42
- **NFR-3:** Total runtime < 24 hours

---

## Success Criteria

| Metric | Target | Priority |
|--------|--------|----------|
| CCR R² | ≥ 0.9 | P0 |
| Detector F1 @ 0.1% | > 0.8 | P0 |
| Monotonic CCR | Yes | P0 |

---

## Dependencies

- PyTorch, Transformers, Datasets (HuggingFace)
- TRAK library (`pip install traker[fast]`)
- sklearn for metrics

---

## Data Assets

| Asset | Source | Size |
|-------|--------|------|
| Pythia-1B | EleutherAI/pythia-1b | 2GB |
| RedPajama-1B | togethercomputer/RedPajama-Data-1T | ~4GB subset |
| MMLU | cais/mmlu | ~50MB |

---

*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
