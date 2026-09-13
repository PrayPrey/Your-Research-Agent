# Superseded Hypothesis Record

**Date:** 2026-03-17T15:44:01+00:00
**Hypothesis:** h-e1
**Superseded By:** Phase 2A (Hypothesis Revision Required)
**Status:** SUPERSEDED

## Supersede Reason

MUST_WORK gate failed: The hypothesis predicted ≥30% gradient conflict between three reward modalities (execution correctness, AI rubric quality, developer preference) in code generation RLHF, but the proof-of-concept implementation observed 0% conflict. All gradient pairs showed very high positive correlation (>0.95), contradicting the hypothesis expectation.

The mechanism was correctly implemented and verified, but the core phenomenon did not manifest. This indicates that either:
1. The simplified PoC setup (GPT2 model, simplified rewards) was insufficient to demonstrate the phenomenon
2. The reward function design did not create genuinely divergent objectives
3. The hypothesis assumptions about gradient conflict in this setting may be incorrect

**Routing Decision:** Phase 2A-Dialogue for complete hypothesis revision.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.0 |
| Recommendation | SUPERSEDE |
| Reasoning | Foundation hypothesis (EXISTENCE type) failed MUST_WORK gate with zero gradient conflict observed. All dependent hypotheses (h-m1, h-m2, h-m3) rely on gradient conflict existing. Complete hypothesis redesign required rather than incremental modification. |

## Experimental Evidence

**What Was Tested:**
- Model: GPT2 (124M parameters) as proxy for CodeLlama-7B
- Dataset: HumanEval + MBPP (100 prompts)
- Three reward modalities implemented
- 10 gradient conflict measurements completed
- Mechanism verification: PASSED

**What Failed:**
- Gradient conflict percentage: 0% (target: ≥30%)
- Bootstrap CI lower bound: 0% (target: >25%)
- All gradient pairs highly correlated (cosine similarity >0.95)

## Cascade Effects

The following hypotheses were blocked by this failure:

- h-m1 (MECHANISM: Pareto optimization gains from gradient conflict)
- h-m2 (MECHANISM: Representational separability from non-convex frontier)
- h-m3 (MECHANISM: Inference-time steering from representational geometry)

These will remain in NOT_STARTED status until new foundation hypothesis is validated.

## Key Insights for Revision

### What Didn't Work:
1. **Simplified reward functions** - All three rewards likely correlated with "syntactically valid code"
2. **Model mismatch** - GPT2 (general language) vs CodeLlama-7B (code-specialized)
3. **Simplified RLHF** - Missing full PPO training loop, KL penalty, advantage normalization
4. **Small sample size** - Only 10 measurements vs 100 planned

### Critical Questions for Phase 2A:
1. Can gradient conflict be demonstrated with accessible models and simplified rewards?
2. What specific reward function designs would create genuine objective conflicts?
3. Is full RLHF implementation (PPO + KL penalty) necessary to observe the phenomenon?
4. Should the hypothesis scope be narrowed to more demonstrable phenomena?

### What Showed Promise:
- Clean implementation architecture successfully completed
- Gradient measurement mechanism works correctly
- Three-modality reward system functional
- Proof-of-concept framework reusable for revised hypothesis

## Timeline

1. Original hypothesis: h-e1 (EXISTENCE - Gradient Conflict in Multi-Objective Code RLHF)
2. Phase 2C: Experiment design completed (2026-03-17T15:05:08)
3. Phase 3: Implementation planning completed (2026-03-17T15:27:00)
4. Phase 4: Implementation and validation completed (2026-03-17T15:44:01)
5. MUST_WORK gate result: FAIL (0% conflict observed)
6. Decision: SUPERSEDE (route to Phase 2A)
7. New direction: Hypothesis revision required - reassess fundamental assumptions about gradient conflict in code generation RLHF

## Recommendation for Phase 2A

The new hypothesis should address one of these directions:

**Option 1: Narrow Scope**
- Focus on demonstrable gradient behavior with accessible models
- Define reward functions that provably create conflict
- Reduce complexity to isolate core mechanism

**Option 2: Full-Scale Approach**
- Explicitly require CodeLlama-7B with HF authentication
- Implement complete RLHF training loop (PPO + KL)
- Use authentic reward functions (test execution, learned rubric, human preference)
- Accept higher implementation complexity

**Option 3: Alternative Phenomenon**
- Investigate different aspect of multi-objective code generation
- Focus on observable behavior rather than internal gradient dynamics
- Consider more empirically grounded hypothesis

---
*Superseded at: 2026-03-17T15:44:01+00:00*
*For cross-phase reference*