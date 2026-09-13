# Phase 2B Verification Plan
## H-HybridRL-Refine-v1: Superadditive Gains from Hybrid RL Training + Test-Time Refinement

**Generated**: 2026-08-08T03:10:00Z
**Archon Project**: `07d63c5f-980d-4c54-a2bc-8bc4b1fb699a`

---

## Main Hypothesis

RL training with structurally diverse execution feedback induces a feedback-conditioned edit policy that, when combined with test-time refinement, produces **superadditive accuracy gains** measurable via positive interaction terms in factorial designs.

**Mechanism**: RL optimizes p(edit | code, feedback) under diverse feedback, forcing abstraction. This manifests as increased I(F;E) between feedback spans and edit spans. At inference, structural coupling compounds across refinement steps.

---

## Sub-Hypotheses

| ID | Type | Statement | Gate | Prerequisites |
|----|------|-----------|------|---------------|
| H-E1 | EXISTENCE | Training×Refinement interaction > 0 on logit(pass@1) | MUST_WORK | None |
| H-M1 | MECHANISM | I(F;E)_RL > I(F;E)_CE controlling for edit length | MUST_WORK | H-E1 |
| H-M2 | MECHANISM | DiD [(A-C)_RL - (A-C)_CE] > 0 for semantic sensitivity | SHOULD_WORK | H-E1 |
| H-C1 | CONDITION | High feedback diversity necessary for superadditivity | SHOULD_WORK | H-E1 |

---

## Dependency Graph (DAG)

```
H-E1 (Existence: Superadditivity)
  │
  ├──► H-M1 (Mechanism: I(F;E) coupling) [MUST_WORK]
  │
  ├──► H-M2 (Mechanism: Semantic sensitivity) [SHOULD_WORK]
  │
  └──► H-C1 (Condition: Diversity necessity) [SHOULD_WORK]
```

---

## Risk Analysis

| Hypothesis | Risk Level | Key Risk | Mitigation |
|------------|------------|----------|------------|
| H-E1 | HIGH | Interaction ≤ 0 invalidates entire hypothesis | Power analysis: 664+ problems × 3 seeds |
| H-M1 | MEDIUM | I(F;E) metric novel, calibration needed | Permutation baseline for significance |
| H-M2 | LOW | Standard DiD methodology | Template-based perturbations |
| H-C1 | MEDIUM | Diversity manipulation confounds | Control reward magnitude separately |

---

## Experimental Design Summary

**Model**: CodeT5+-base (220M parameters)
**Benchmarks**: HumanEval+ (164 problems), MBPP+ (500+ problems)
**Conditions**: 2×2 factorial (CE/RL × single-shot/refined)
**Refinement**: Self-Refine protocol, K=3 iterations
**Statistical**: GLMM with problem random effects, p<0.05, OR≥1.2

---

## Timeline

1. **H-E1** → Phase 2C → Phase 3 → Phase 4 (MUST validate first)
2. **H-M1** → Phase 2C → Phase 3 → Phase 4 (after H-E1 PASS)
3. **H-M2, H-C1** → Parallel after H-E1 (SHOULD_WORK, can fail without blocking)
4. **Phase 5** → Baseline comparison vs S*, CodeRL

---

## Archon Task Mapping

| Hypothesis | Archon Task ID |
|------------|----------------|
| H-E1 | `13b1edca-faff-4597-90de-3a1250291540` |
| H-M1 | `08bc4936-cb5a-4f50-98de-dcb83d35a2d3` |
| H-M2 | `640632b4-2607-4266-b610-e5e0e4410b8c` |
| H-C1 | `07985f94-98a7-489c-9ba2-ab9c2bb1ffd7` |
