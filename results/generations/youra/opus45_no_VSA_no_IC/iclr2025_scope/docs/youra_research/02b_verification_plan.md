# Phase 2B Verification Plan

## Main Hypothesis

**ID**: H-LoRARankScaling-v1  
**Title**: Sub-Linear Scaling Law for Optimal LoRA Rank  
**Statement**: Under Pythia 1B-12B, optimal LoRA rank scales as r_opt ∝ N^α where α ∈ (0.3, 0.7), because task-relevant subspace dimensionality grows sub-linearly with model capacity.

## Sub-Hypotheses

| ID | Type | Gate | Status | Statement |
|----|------|------|--------|-----------|
| h-e1 | EXISTENCE | MUST_WORK | READY | Log-linear regression of r_opt vs N yields α ∈ (0.3, 0.7) with 95% CI excluding 0 and 1 |
| h-m1 | MECHANISM | SHOULD_WORK | READY | Attention entropy at r_opt correlates with model size (r > 0.6, p < 0.05) |
| h-m2 | MECHANISM | MUST_WORK | NOT_STARTED | Rank sensitivity >2x higher at 12B vs 1B (phase transition) |
| h-c1 | CONDITION | SHOULD_WORK | NOT_STARTED | Scaling law α consistent (within 0.15) across single-hop and multi-hop QA |

## Dependency Graph

```
H-E1 (Existence) ──┬──> H-M2 (Phase Transition)
                   │
                   └──> H-C1 (Task Complexity)

H-M1 (Attention Entropy) [Independent]
```

## Execution Order

1. **Wave 1** (parallel): h-e1, h-m1
2. **Wave 2** (after h-e1): h-m2, h-c1

## Risk Analysis

| Hypothesis | Risk | Mitigation |
|------------|------|------------|
| h-e1 | Medium - 4 points may yield wide CI | Use bootstrap for robust CI estimation |
| h-m1 | Low - measurement straightforward | Standard attention hook implementation |
| h-m2 | Medium - transition may be gradual | Report gradient magnitude, not binary |
| h-c1 | Low - confound manageable | 2-level factorial design |

## Experimental Setup

- **Models**: EleutherAI/pythia-{1b, 2.8b, 6.9b, 12b}
- **Datasets**: SQuAD-v2 (single-hop), HotpotQA (multi-hop), Natural Questions (held-out)
- **Ranks**: 4, 8, 16, 32, 64, 128
- **Training**: 3 epochs, lr=1e-4, LoRA α=2r, targets=Q,V

## Baselines (Phase 5)

1. Constant rank=16 (current practice)
2. Linear scaling r ∝ N
3. Full fine-tuning (upper bound)

## Archon Project

- **Project ID**: 9dd61e2d-6e54-4657-9b57-6c6632d5839b
- **Title**: Anonymous Pipeline: LoRA Rank Scaling Law

---
*Generated: 2026-08-24T14:32:00Z*
