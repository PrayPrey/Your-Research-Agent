# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-23T09:41:16Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** FUNDAMENTAL_HYPOTHESIS_FAILURE
**Gate Type:** MUST_WORK
**Routing Decision:** Phase 0

## Hypothesis Statement

Layer-wise gradient cosine similarity between execution-based RL and preference-based DPO shows structured divergence: lower layers (1-8) exhibit higher similarity (>0.4) while upper layers (17-24) exhibit lower similarity (<0.2).

## Experiment Results

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Lower Layers (1-8) Cosine | > 0.4 | -0.084 ± 0.102 | FAIL |
| Upper Layers (17-24) Cosine | < 0.2 | -0.059 ± 0.046 | PASS |
| Mid Layers (9-16) Cosine | N/A | -0.070 ± 0.070 | N/A |

## Key Findings

1. **Anti-correlation across all layers:** RL and DPO gradients show negative cosine similarity across all 48 transformer layers
2. **No structured divergence:** The expected pattern of high similarity in lower layers and low similarity in upper layers was not observed
3. **Statistical significance:** 48/48 layers showed statistically significant differences (p < 0.05) compared to null baseline
4. **Gradient directions are orthogonal/opposite:** Instead of aligned gradients in lower layers, the methods optimize in opposite directions

## Root Cause Analysis

- The fundamental assumption that RL and DPO would share similar gradient directions in lower layers was incorrect
- Execution-based rewards (test pass/fail) and preference-based rewards (human rankings) create fundamentally different optimization pressures from the start
- The hypothesis assumed gradual divergence that increases with layer depth, but actual behavior shows uniform anti-correlation

## Lessons Learned

1. **RL vs DPO gradient alignment assumptions need revision:** The assumption that different alignment objectives would share base representations in lower layers is not supported by CodeT5-770M evidence
2. **Anti-correlation is the actual pattern:** Methods optimize in opposite directions rather than diverging from a shared foundation
3. **Layer-wise analysis valuable but hypothesis direction wrong:** The gradient cosine similarity metric is valid, but the expected pattern was incorrect
4. **Consider alternative framings:** Instead of "structured divergence," investigate why gradients are anti-correlated and what this reveals about alignment mechanisms

## Feedback for Phase 0 (Research Direction Pivot)

### Questions to Explore
- Why are RL and DPO gradients anti-correlated? What does this reveal about code generation alignment?
- Are there specific layer patterns in the anti-correlation that could inform hybrid approaches?
- Does the anti-correlation suggest the methods are complementary (could be combined)?

### What NOT To Do
- Do not assume gradient similarity patterns from NLP transfer to code generation
- Do not assume layer-wise divergence without first establishing baseline correlation

### What Showed Promise
- The gradient capture and analysis infrastructure works correctly
- Statistical significance testing revealed clear patterns
- Encoder-decoder heatmap visualization provides useful insights

## Pipeline Status

- **Episode:** TERMINATED
- **Termination Trigger:** MUST_WORK gate FAIL
- **Dependent Hypotheses (BLOCKED):** h-m1, h-m2, h-m3, h-m4
- **Next Phase:** Phase 0 (Research Direction Pivot)

---
*For cross-phase reference*
*Written at: 2026-03-23T09:41:16Z*
*Phase 4 MUST_WORK gate failure - fundamental hypothesis failure*
