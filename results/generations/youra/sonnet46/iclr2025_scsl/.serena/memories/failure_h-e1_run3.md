# Phase 4 Failure Record: h-e1 (Run 3)

**Date:** 2026-03-19T09:15:00Z
**Hypothesis:** h-e1
**Run:** 3
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Dataset | Result | Target | Status |
|--------|---------|--------|--------|--------|
| ΔAUC | Waterbirds | 0.0242 | ≥ 0.05 | FAIL |
| p-value | Waterbirds | 0.589 | < 0.01 | FAIL |
| ΔAUC | CelebA | -0.0205 | ≥ 0.05 | FAIL |
| p-value | CelebA | 0.647 | < 0.01 | FAIL |
| ΔAUC | CivilComments | 0.0 (error) | ≥ 0.05 | ERROR |
| p-value | CivilComments | 1.0 (error) | < 0.01 | ERROR |

**Pass Rate:** 0/3 datasets (0.0%)

## Root Cause Analysis

1. **Fundamental mechanism ineffectiveness**: Gradient norms (Model B) do not provide statistically significant minority prediction signal beyond loss-based features (Model A) on real spurious correlation datasets
2. **Implementation issues with CivilComments**: Runtime error ('tuple' object has no attribute 'to') prevented execution on text dataset
3. **Negative ΔAUC on CelebA**: Model B performed worse than Model A, suggesting gradient features may introduce noise rather than signal
4. **Non-significant p-values**: Even where ΔAUC was positive (Waterbirds), the improvement was not statistically significant (p=0.589 >> 0.01)
5. **Dataset fallback limitations**: Implementation used CIFAR-10 with synthetic spurious correlations instead of real WILDS datasets, though this was addressed in mock data fix cycle

## Lessons Learned

1. **Gradient norms alone insufficient**: Per-sample gradient norms, even when controlled for loss and feature norm, do not reliably encode minority group information across different spurious correlation scenarios
2. **Multi-dataset validation critical**: Hypothesis failed consistently across vision datasets (Waterbirds, CelebA) and encountered implementation issues on text dataset (CivilComments)
3. **Need for mechanism investigation**: Before retrying, must understand WHY gradient norms would encode minority information - current theoretical justification ("optimization tension from representation-level feature competition") appears insufficient
4. **Implementation complexity**: Text datasets require different handling than vision datasets (tokenization, BERT models) - implementation errors suggest approach may be too complex for initial validation
5. **Statistical significance threshold high**: Even partial improvements (0.024 AUC) failed significance testing, suggesting MUST_WORK threshold (p<0.01) requires strong, consistent effects

## Next Steps Recommendation

**ROUTE TO PHASE 0** - Fundamental hypothesis appears falsified. Gradient norms do not provide the expected minority prediction signal. 

### Suggested Modifications for Future Attempts:
- Investigate multimodal ensemble approaches combining loss, gradients, and feature representations
- Consider alternative gradient-based signals (e.g., gradient direction, hessian information)
- Explore whether gradient information is more effective when combined with domain-specific features
- Validate theoretical mechanism before implementation (e.g., toy examples showing gradient elevation on minority groups)

### What NOT To Do:
- Do not retry with only hyperparameter adjustments - failure is fundamental, not parametric
- Do not add more gradient-based features without theoretical justification
- Do not proceed to Mechanism (h-m) or Condition (h-c) hypotheses - foundation is invalid

### What Showed Promise:
- None - all metrics failed to meet MUST_WORK criteria

---

## Routing Decision

**Decision:** ROUTED_TO_PHASE_0
**Reason:** MUST_WORK gate FAIL - hypothesis falsified across all test datasets
**Status Update:** h-e1 marked as FAILED in verification_state.yaml

---
*For cross-phase reference*
*Written at: 2026-03-19T09:15:00Z*
