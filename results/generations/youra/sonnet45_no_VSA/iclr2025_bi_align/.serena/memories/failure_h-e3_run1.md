# Phase 4 Failure Record: h-e3 (Run 1)

**Date:** 2026-07-10T04:34:00+00:00
**Hypothesis:** h-e3
**Run:** 1
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_FALSIFIED

## Performance Gap

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Accuracy | 50% (1/2) | 100% (3/3) | ❌ |
| WildChat Match | FAIL | PASS | ❌ |
| PersonaChat Match | PASS | PASS | ✅ |
| DailyDialog Match | NOT_TESTED | PASS | ⏸️ |

## Root Cause Analysis

1. **SAT measures inference-time throughput stability, not training-time OOM failures**
   - WildChat h-e1 timeout was caused by gradient memory accumulation during training
   - SAT profiling only measures forward pass throughput variance
   - Training has ~3× higher memory footprint than inference

2. **Truncation artifact masked long-tail distribution**
   - Experiment used max_length=1024 truncation
   - Removed long-tail samples that cause throughput variance
   - P95/Median = 1.00 for WildChat (unnatural, all samples truncated)

3. **Inference vs Training context mismatch**
   - h-e1 failure: Training OOM (backpropagation + optimizer state)
   - h-e3 measurement: Inference throughput (forward pass only)
   - These are ORTHOGONAL failure modes

4. **SAT alone is insufficient for training accessibility prediction**
   - Need combined MSI (Memory Stress Index) + SAT predictor
   - MSI > 0.7 predicts OOM (validated in H-M4)
   - SAT/CV predicts throughput instability
   - Must use context-specific thresholds (inference vs training)

## Lessons Learned

1. **SAT scope limitation discovered**
   - SAT is a throughput stability metric, not a memory predictor
   - Training failures require memory-aware prediction (MSI component)
   - Single-metric predictors miss orthogonal failure modes

2. **Truncation effects must be documented**
   - max_length truncation can mask dataset skew characteristics
   - Compare truncated vs non-truncated distributions before profiling
   - Document P95/Median artifacts in methodology section

3. **Ground truth validation is critical**
   - h-e1 "WildChat FAIL" ground truth assumed throughput variance
   - Actual failure was training OOM, not inference instability
   - Verify failure mode (OOM vs throughput vs convergence) before prediction

4. **Context-aware prediction rules**
   - Inference-time SAT ≠ Training-time accessibility
   - Need separate prediction models for different execution contexts
   - H-M4 combined predictor (MSI + SAT) handles both failure modes

## Feedback for Next Phase

### Suggested Modifications

- Replace WildChat with dataset exhibiting **inference-time throughput variance** (e.g., Reddit-1M from H-M4)
- Use H-M4 combined predictor: (MSI > 0.7) OR (P95/Median > 3.0)
- Add training-specific memory model (gradient buffers + optimizer state)
- Validate that inference predictions generalize to training outcomes

### What NOT To Do

- Do NOT use SAT-only threshold for training accessibility prediction
- Do NOT assume h-e1 timeouts are throughput-related without verification
- Do NOT truncate datasets before profiling without documenting artifacts
- Do NOT use single-metric predictors for multi-failure-mode scenarios

### What Showed Promise

- PersonaChat classification: CORRECT (SAT correctly identified stable dataset)
- SAT profiling protocol from H-M2: Validated and reproducible
- Structural metrics (P95/Median, MSI): Correlate with failure modes as expected
- Visualization pipeline: Effectively reveals classification errors

## Scientific Interpretation

This falsification reveals an important insight about SAT's scope:

**SAT measures throughput stability during inference**, capturing variance in per-batch processing time. It does NOT account for gradient memory accumulation during training. WildChat's h-e1 timeout was a **training OOM failure** (gradient buffers), not a **throughput instability failure** (variance).

**Key insight:** Training and inference have ORTHOGONAL failure modes requiring COMBINED prediction (MSI for OOM + SAT for instability).

## Recommended Routing

**Route to: Phase 2A (Hypothesis Refinement)**

### Revised Hypothesis (H-E3-v2)

> "SAT threshold correctly discriminates between stable (DailyDialog, PersonaChat) and unstable (Reddit-1M) datasets under inference profiling, but training-time failures (WildChat h-e1 timeout) require combined MSI+SAT prediction rules from H-M4."

### Key Changes

1. Replace WildChat (training failure) with Reddit-1M or another dataset with **inference-time throughput variance**
2. Use H-M4 combined predictor (MSI > 0.7 OR P95/Median > 3.0) instead of SAT-only rule
3. Validate that inference-time predictions generalize to training-time outcomes (or document the gap)

---
*For cross-phase reference*
*Written at: 2026-07-10T04:34:00+00:00*
