# Superseded Hypothesis Record

**Date:** 2026-08-02T15:20:00+00:00
**Hypothesis:** h-m2
**Superseded By:** h-m2-v2
**Status:** SUPERSEDED

## Supersede Reason

OLS length residualization failed the MUST_WORK gate (PARTIAL result). Condition 4 (res UQ × res EM — full residualization) produces a negative ΔAUROC of −0.0409, causing 3/4 rank flips against the ≥0.02 threshold. The hypothesis claimed OLS is "sufficient" to remove length confounding, but the mechanism behavior is fundamentally violated: joint residualization of both UQ features and correctness labels removes predictive signal when OLS R²≈0 (R²=−0.001), meaning length explains essentially nothing about EM correctness.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.3 |
| Recommendation | SUPERSEDE |
| Reasoning | Behavior incompatible: OLS full residualization (Condition 4) hurts ensemble performance. Recovery requires fundamental redesign of debiasing strategy — not a parameter tweak... |

## Key Findings to Carry Forward

- **Condition 2 (res UQ × raw EM) works**: AUROC=0.739, positive ΔAUROC — UQ-only debiasing is sufficient and beneficial
- **Condition 4 is harmful**: Residualizing correctness labels with near-zero R² creates ill-conditioned binary classification
- **Length-EM correlation is negligible** (R²=−0.001): Length debiasing of correctness labels is unnecessary
- **Sample size artifact**: Min decile AUROC=0.408 at D6 (N=21 samples); with full 2500-sample dataset this may resolve
- **Alternative debiasing**: Spearman-based reranking, isotonic regression, or length-stratified AUROC (Uncertainty-LINE, Vashurin et al. 2025) are candidates

## Recommended Direction for h-m2-v2

Reformulate hypothesis to: "UQ-only OLS residualization (Condition 2: res UQ × raw EM) is sufficient to remove length confounding from SE/SelfCheckNLI features, without residualizing correctness labels."

## Timeline

1. Original hypothesis: h-m2 (OLS sufficient for joint residualization)
2. PARTIAL result: 3/4 rank flips, min decile AUROC=0.408
3. LLM assessment: compatibility_score=0.3, behavior_compatible=False
4. Decision: SUPERSEDE → Phase 2A redesign
5. New direction: h-m2-v2 (UQ-only debiasing)

---
*Superseded at: 2026-08-02T15:20:00+00:00*
