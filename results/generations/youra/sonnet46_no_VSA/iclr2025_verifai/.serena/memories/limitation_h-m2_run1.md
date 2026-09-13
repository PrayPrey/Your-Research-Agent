# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-03T15:31:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate not satisfied: Spearman ρ = 0.136 < threshold 0.30. Weak but statistically significant positive correlation (p = 0.005 exact permutation). Tier group differences significant (Kruskal-Wallis H = 11.22, p = 0.011), but non-monotonic tier means (T1=0.339, T2=0.523, T3=0.436, T4=0.473) indicate contract richness tiers do not cleanly predict oracle-isolation gap magnitude.

## Failed Checks

- Spearman ρ ≥ 0.30 (achieved 0.136)
- Monotonic tier gradient (non-monotonic: T3 < T2)

## Partial Results

| Metric | Value |
|--------|-------|
| Spearman ρ | 0.136 |
| p-value (exact permutation) | 0.005 |
| 95% CI lower | 0.034 |
| 95% CI upper | 0.235 |
| Kruskal-Wallis H | 11.22 |
| Kruskal-Wallis p | 0.011 |
| n_tasks | 364 |
| HumanEval+ ρ | 0.164 (p=0.038) |
| MBPP+ ρ | 0.096 (p=0.067) |

## Experiment Summary

ContractEval tasks stratified by postcondition complexity (AST-based, 4 tiers) show a weak but significant positive correlation between contract richness and oracle-isolation gap. The FLAT_GRADIENT flag triggered (ρ < 0.15). Publishable as a negative/nuanced result: correlation exists but is weaker than hypothesized, and tier means are non-monotonic. The universal-property mechanism from h-m1 (gap=0.40) is confirmed; h-m2's contribution is that AST complexity is a weak proxy for this gap.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Alternative complexity metrics beyond AST node count (e.g., semantic richness, number of distinct postcondition predicates)
2. Finer-grained tier boundaries or continuous complexity measure instead of discrete tiers
3. Whether task difficulty (not just contract complexity) mediates the gap

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL), this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-03T15:31:00+00:00*
*For cross-phase reference*
