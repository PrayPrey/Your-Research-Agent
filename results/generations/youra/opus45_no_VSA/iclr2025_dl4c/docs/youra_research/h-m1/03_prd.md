# Product Requirements Document: H-M1

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis:** I(F;E)_RL > I(F;E)_CE controlling for edit length, p<0.05
**Type:** MECHANISM
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

This experiment validates the MECHANISM hypothesis that RL-trained code generation models develop tighter coupling between error feedback and generated edits compared to CE-trained models. We measure this via Mutual Information Neural Estimation (MINE) between feedback embeddings and edit embeddings, controlling for edit length to isolate the feedback utilization effect.

**Key Claim:** RL training on execution feedback forces the model to learn feedback-conditioned representations, resulting in measurably higher I(F;E) than CE training.

---

## Problem Statement

### Background
H-E1 established that Training×Refinement interaction exists (infrastructure validated). H-M1 investigates the mechanism: WHY does RL+Refinement outperform CE+Refinement?

### Hypothesis
RL training induces stronger feedback-code coupling because:
1. RL optimizes p(edit | code, feedback) under diverse feedback signals
2. This forces learning feedback-conditioned representations
3. CE training only minimizes next-token prediction loss, no explicit feedback coupling

### Success Criteria
- I(F;E)_RL > I(F;E)_CE after edit-length control
- p < 0.05 (permutation test, 10,000 permutations)

---

## Functional Requirements

### FR-1: Model Loading (from H-E1)

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1.1 | Load CE-trained CodeT5+-220M from h-e1/models/ce_model/ | H-E1 artifacts |
| FR-1.2 | Load RL-trained CodeT5+-220M from h-e1/models/rl_model/ | H-E1 artifacts |
| FR-1.3 | Load shared tokenizer from Salesforce/codet5p-220m | HuggingFace |

### FR-2: Refinement Trace Extraction

| ID | Requirement | Source |
|----|-------------|--------|
| FR-2.1 | Load HumanEval+ dataset (164 problems) | evalplus |
| FR-2.2 | Generate refinement traces with K=3 iterations per problem | Phase 2C spec |
| FR-2.3 | Extract (feedback, edit) pairs from each refinement step | Phase 2C spec |
| FR-2.4 | Compute edit as code diff between iterations | Phase 2C spec |
| FR-2.5 | Record edit_length for each pair | Phase 2C spec |
| FR-2.6 | Run with 3 seeds for variance estimation | Phase 2C spec |

**Sample Size:** 164 problems × 3 seeds × 3 rounds = 1,476 samples per condition

### FR-3: MINE Estimator Implementation

| ID | Requirement | Source |
|----|-------------|--------|
| FR-3.1 | Implement MINEEstimator class with 3-layer MLP | gtegner/mine-pytorch |
| FR-3.2 | Statistics network: (feedback_dim + code_dim) → 512 → 512 → 1 | Phase 2C spec |
| FR-3.3 | Use Donsker-Varadhan lower bound for MI estimation | MINE paper |
| FR-3.4 | Implement EMA bias correction (weight=0.01) | Phase 2C spec |

### FR-4: Text Embedding

| ID | Requirement | Source |
|----|-------------|--------|
| FR-4.1 | Embed feedback text using model encoder | Phase 2C spec |
| FR-4.2 | Embed edit text using model encoder | Phase 2C spec |
| FR-4.3 | Use mean pooling over encoder hidden states | Phase 2C spec |
| FR-4.4 | Embedding dimension: 256 (projected from model dim) | Phase 2C spec |

### FR-5: MINE Training

| ID | Requirement | Source |
|----|-------------|--------|
| FR-5.1 | Train MINE with Adam optimizer, lr=0.001 | Phase 2C spec |
| FR-5.2 | Batch size: 128 | Phase 2C spec |
| FR-5.3 | Training iterations: 5000 | Phase 2C spec |
| FR-5.4 | Train separate MINE estimators for CE and RL conditions | Phase 2C spec |

### FR-6: Edit Length Control

| ID | Requirement | Source |
|----|-------------|--------|
| FR-6.1 | Regress MI values on edit_length | Phase 2C spec |
| FR-6.2 | Compute residuals (MI - predicted) | Phase 2C spec |
| FR-6.3 | Compare residual MI between conditions | Phase 2C spec |

### FR-7: Statistical Testing

| ID | Requirement | Source |
|----|-------------|--------|
| FR-7.1 | Implement permutation test for significance | Phase 2C spec |
| FR-7.2 | Use 10,000 permutations | Phase 2C spec |
| FR-7.3 | Compute p-value as proportion of permuted diffs ≥ observed | Phase 2C spec |
| FR-7.4 | Compute Cohen's d effect size on residuals | Phase 2C spec |

### FR-8: Visualization

| ID | Requirement | Source |
|----|-------------|--------|
| FR-8.1 | MI comparison bar chart (CE vs RL, raw and controlled) | Phase 2C spec |
| FR-8.2 | Scatter plot: MI vs edit length, colored by condition | Phase 2C spec |
| FR-8.3 | Permutation distribution histogram with observed diff marked | Phase 2C spec |
| FR-8.4 | Save all figures to h-m1/figures/ | Phase 2C spec |

### FR-9: Results Persistence

| ID | Requirement | Source |
|----|-------------|--------|
| FR-9.1 | Save results to h-m1/results.json | Standard |
| FR-9.2 | Save tabular results to h-m1/results.csv | Standard |
| FR-9.3 | Include raw MI, controlled MI, p-value, effect size | Phase 2C spec |

---

## Non-Functional Requirements

### NFR-1: Performance
- Refinement trace extraction: < 2 hours (GPU)
- MINE training: < 30 minutes per condition
- Total runtime: < 4 hours

### NFR-2: Reproducibility
- Fixed random seeds (42, 43, 44)
- Deterministic CUDA operations where possible
- All hyperparameters in config file

### NFR-3: Dependencies
- PyTorch >= 2.0
- transformers >= 4.30
- evalplus
- scipy (for regression, permutation test)
- matplotlib (for visualization)

---

## Dependencies

### From H-E1 (Prerequisites)
- Trained CE model: h-e1/models/ce_model/
- Trained RL model: h-e1/models/rl_model/
- Shared tokenizer configuration

### External
- HumanEval+ dataset (evalplus)
- MINE reference implementation (gtegner/mine-pytorch)

---

## Success Metrics

| Metric | Threshold | Type |
|--------|-----------|------|
| I(F;E)_RL - I(F;E)_CE (controlled) | > 0 | Primary |
| p-value | < 0.05 | Primary |
| Cohen's d | Report | Secondary |
| MINE convergence | Loss decreasing | Sanity |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| MINE not converging | Use EMA bias correction, increase iterations |
| Insufficient samples | 1,476 per condition should be adequate |
| Edit length confound | Explicit regression control |
| H-E1 models not available | Verify paths in Step 1 |

---

## Out of Scope

- Retraining CE/RL models (use H-E1 artifacts)
- Alternative MI estimators (InfoNCE, etc.)
- Multi-dataset evaluation (HumanEval+ only)
- Model architecture changes

---

*Generated from Phase 2C experiment brief*
*Next: Architecture Design (Step 3)*
