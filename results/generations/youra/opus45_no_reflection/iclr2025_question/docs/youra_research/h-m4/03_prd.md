# Product Requirements Document: H-M4

**Date:** 2026-08-18
**Hypothesis:** Probe outperforms output-level baselines by >= 5 AUROC points
**Type:** MECHANISM
**Prerequisite:** H-M3 (Linear probe AUROC=0.8851)

---

## Executive Summary

This experiment validates that hidden-state probing provides superior correctness prediction compared to output-level uncertainty baselines (token entropy, sequence probability). Success demonstrates the value of internal representations over surface-level signals.

---

## Problem Statement

Output-level uncertainty methods (token entropy, sequence NLL) are training-free but may lack discriminative power for correctness prediction. H-M3 established probe AUROC=0.8851. This experiment quantifies the improvement margin over standard baselines.

---

## Functional Requirements

### FR-1: Baseline Implementation - Token Entropy
- Compute per-token entropy: `H_t = -Σ(p_t(i) * log(p_t(i)))`
- Average over generated sequence
- No training required, computed during inference

### FR-2: Baseline Implementation - Sequence NLL
- Compute per-token log probability: `-log(p_t(y_t))`
- Average over sequence length
- Negate for confidence score (lower NLL = more confident)

### FR-3: Probe Loading
- Load H-M3 trained probe from checkpoint
- Load StandardScaler from H-M3
- Validate probe achieves AUROC ~0.885 on validation set

### FR-4: Evaluation Dataset
- TriviaQA validation split: 1,700 samples (matching H-M3)
- Reuse cached hidden states from H-M1/H-M3
- Binary correctness labels via exact-match

### FR-5: Comparative AUROC Computation
- Compute AUROC for each method: probe, token entropy, sequence NLL
- Calculate delta: probe_auroc - entropy_auroc
- Calculate delta: probe_auroc - nll_auroc

### FR-6: Visualization
- Bar chart: AUROC comparison with 0.05 threshold line
- ROC curves overlay for all three methods
- Confidence score distributions by correctness

---

## Non-Functional Requirements

### NFR-1: Runtime
- Single forward pass for entropy/NLL computation
- Probe inference <1ms per sample
- Total evaluation <30 minutes on single GPU

### NFR-2: Memory
- Reuse cached hidden states (no new extraction needed)
- Peak VRAM: model inference only (~16GB)

---

## Success Criteria

| Metric | Gate Threshold | Expected |
|--------|---------------|----------|
| Probe AUROC - Token Entropy AUROC | >= 0.05 | ~0.15-0.20 |
| Probe AUROC - Seq NLL AUROC | >= 0.05 | ~0.15-0.20 |
| Probe AUROC | >= 0.88 | 0.8851 (from H-M3) |

---

## Dependencies

- H-M3 trained probe checkpoint
- H-M1 cached hidden states
- TriviaQA validation dataset
- Llama-3-8B-Instruct model (for baseline inference)

---

## Out of Scope

- Multi-sample methods (semantic entropy) - single-pass only
- Training new probes - use H-M3 checkpoint
- New datasets - use same validation set as H-M3
