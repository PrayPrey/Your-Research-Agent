# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-08-31T12:05:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Ours (best) | Baseline (FlatMLP) | Gap |
|--------|-------------|-------------------|-----|
| Spearman(gap) best (NFT) | 0.5752 | 0.5330 | +0.0422 |
| Spearman(test_acc) best (NFT) | 0.4801 | 0.2790 | +0.2011 |
| Δ = gap − test_acc best (NFT) | -0.1589 | N/A | FAIL |

## Gate Condition

**Required:** Δ > 0.02 for ≥2 of {DWSNet, NFT, GNN}
**Achieved:** Δ < 0 for all 3 encoders (n_pass = 0)

| Encoder | Spearman(gap) | Spearman(test_acc) | Δ | Pass? |
|---------|--------------|-------------------|---|-------|
| DWSNet | 0.4881 | 0.4553 | -0.2212 | FAIL |
| NFT | 0.5752 | 0.4801 | -0.1589 | FAIL |
| GNN | 0.3747 | 0.3480 | -0.2272 | FAIL |
| FlatMLP | 0.5330 | 0.2790 | — | baseline |

## Root Cause Analysis

- Equivariant encoders predict test_acc substantially better than gap across all architectures
- Gap prediction appears harder than test_acc for all encoder types, not just equivariant ones
- FlatMLP Spearman(test_acc)=0.279 anomalously low vs. literature (expected ~0.85), suggesting this zoo's test_acc weight-space structure differs from Unterthiner 2020
- The hypothesis that permutation-equivariance gives *differential* advantage for gap (vs. test_acc) is not supported — equivariant encoders are better at test_acc too
- P3 (partial Spearman of gap controlling for test_acc) = 0.7305 (p=1.6e-167) is strong, indicating gap contains information beyond test_acc, but this doesn't translate to Δ > 0

## Lessons Learned

1. The differential advantage Δ metric conflates encoder quality with target difficulty — gap is harder to predict than test_acc for ALL encoders
2. FlatMLP test_acc baseline anomaly (0.279) warrants investigation — possible zoo-specific artifact
3. NFT remains best encoder for gap prediction (0.5752), supporting h-m1 findings
4. P3 result (partial Spearman) is a strong positive signal — gap contains unique information not captured by test_acc
5. Future hypotheses should target gap-specific signal identification rather than differential advantage

## Routing Decision

**Outcome:** ROUTED_TO_PHASE_0
**Reason:** MUST_WORK gate FAIL — the differential advantage mechanism is not confirmed; fundamental redesign required

## Note on Serena MCP

This record was written as a local fallback file because mcp__serena__write_memory was unavailable
(Serena MCP not configured in this project). Content mirrors what would be written to Serena Memory.

---
*Failure recorded at: 2026-08-31T12:05:00+00:00*
*For cross-phase reference*
