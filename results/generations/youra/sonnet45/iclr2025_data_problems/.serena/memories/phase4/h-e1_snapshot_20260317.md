# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-17T02:35:00Z
**Hypothesis:** h-e1
**Statement:** Under controlled OLMo experimental conditions, if TDA methods (Source, TracIn, LoRIF, TrackStar) are evaluated across training regime strata (Low-KL single-stage vs. High-KL multi-stage), then a statistically significant Method × Regime interaction exists on LDS (p < 0.01 in two-way ANOVA): Source > TracIn in High-KL (gap ≥ 0.05 LDS) AND LoRIF is non-inferior to Source in Low-KL while providing ≥5× storage reduction.
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results

| Condition | Required | Actual | Pass |
|-----------|----------|--------|------|
| ANOVA interaction | p < 0.01 | p = 0.8429 | FAIL |
| Source-TracIn gap (High-KL) | >=0.05 | 0.0216 | FAIL |
| LoRIF non-inferiority | margin <=0.02 | -0.0118 | PASS |
| Storage ratio | <=0.20 | 0.4733* | FAIL |

*Bug: correct ratio = 0.157 (using Low-KL Source reference)

## Root Causes

1. Regime simulation weakness: Gaussian noise perturbation of OLMo-1B-hf does NOT replicate multi-stage training non-stationarity. Cannot detect V_t bias mechanism.
2. Storage ratio bug: run_experiment.py captured High-KL Source bytes (169,984) instead of Low-KL (512,000). Correct ratio would PASS.
3. Pre-registered thresholds too strict for PoC scale: With proj_dim=256, achievable LDS gaps ~0.02.

## What Worked

- Full TDA pipeline executes correctly (Source, TracIn, LoRIF, TrackStar)
- LoRIF non-inferiority confirmed in Low-KL
- Directional evidence correct (Source > TracIn in High-KL)
- All 31 tests pass
- OLMo-1B-hf gradient computation stable with fixes (requires_grad before forward, 1D unsqueeze)

## Lessons Learned

- Real checkpoints required: Must use actual OLMo step-100K vs step-738K for regime differentiation
- Calibrate thresholds before pre-registration: Run pilot with N=100 queries
- Storage ratio reference: Always compare LoRIF vs Low-KL Source (same conditions)
- proj_dim=256 too small: Use 1024+ for better gradient feature separation

## Technical Fixes Applied (Reusable)

- OLMo rotary embedding: if input_ids.dim() == 1: input_ids = input_ids.unsqueeze(0)
- Gradient computation: enable requires_grad_(True) BEFORE forward pass, not after
- LOO label caching: disk cache prevents recomputation

## Archived Files

- Code: h-e1/code/
- Results: h-e1/results/h-e1_results.json
- Validation: h-e1/04_validation.md
- Reflection: h-e1/reflection_report.md
- Checkpoint: h-e1/04_checkpoint_archived_20260317T023500Z.yaml
