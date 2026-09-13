# Superseded Hypothesis Record

**Date:** 2026-08-29T15:45:00+00:00
**Hypothesis:** h-m1
**Superseded By:** Phase2A-redesign
**Status:** ROUTED_TO_PHASE_2A

## Supersede Reason

Semantic clustering mechanism functions correctly but does not achieve required AUROC on MC-format task. MC format limits semantic content available for NLI clustering - short option labels (A/B/C/D) provide insufficient semantic variation for meaningful clustering. Hypothesis needs redesign for free-form generation tasks where semantic entropy can properly discriminate.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.56 |
| Recommendation | ROUTE_TO_PHASE_2A |
| Reasoning | Mechanism verified (clustering active, entropy varies), but MC format fundamentally incompatible with semantic entropy approach. Requires task redesign, not parameter tuning. |

## Experiment Results

| Metric | Value |
|--------|-------|
| Semantic Entropy AUROC | 0.5645 |
| Gate Threshold | 0.70 |
| Avg Clusters | 4.92 |
| Entropy Std | 0.0752 |
| Mechanism Verified | Yes |

## Root Cause Analysis

1. MC format provides only option labels (A/B/C/D) for generation
2. Short text gives NLI model insufficient semantic content
3. Clustering defaults to near-random groupings
4. Entropy calculation loses discriminative power

## Lessons Learned

1. Semantic entropy requires free-form generation for meaningful clustering
2. MC-format tasks should use token-level methods (max_prob, choice_entropy)
3. Gate verification showed mechanism works - task format is the issue
4. Future experiments should match UQ method to task format

## Timeline

1. Original hypothesis: h-m1 (Semantic entropy AUROC >= 0.70 on TruthfulQA mc1)
2. Implementation completed: All 9 tasks done
3. Experiment executed: AUROC=0.5645 < 0.70 threshold
4. Gate evaluation: FAILED
5. Reflection outcome: ROUTED_TO_PHASE_2A
6. Decision: Redesign for free-form generation tasks

---
*Superseded at: 2026-08-29T15:45:00+00:00*
*For cross-phase reference*
