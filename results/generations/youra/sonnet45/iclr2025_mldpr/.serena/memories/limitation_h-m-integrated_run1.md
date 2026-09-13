# Limitation Record: h-m-integrated (Run 1)

**Date:** 2026-03-18T08:37:00Z
**Hypothesis:** h-m-integrated
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Semantic embeddings demonstrate supervised lifecycle detection capability (97-100% linear probe accuracy) but fail at unsupervised clustering recovery (NMI=0.02, 96% below 0.6 threshold). The hypothesis that distributional signatures enable unsupervised clustering to recover lifecycle structure is rejected due to severe class imbalance (8.3% RAI) preventing natural cluster formation.

## Failed Checks

- NMI threshold: 0.0229 < 0.6 (96% below target)
- Baseline gap: 0.0129 < 0.15 (91% below target)
- Normalized NMI: 0.0229 < 0.6 (control experiments show signal persists but remains weak)

## Partial Results

| Metric | Value |
|--------|-------|
| Semantic NMI | 0.0229 |
| Linear Probe Accuracy (HF) | 0.9733 |
| Linear Probe Accuracy (UCI) | 1.0000 |
| Probe Variance | 0.0002 |
| Baseline Gap | 0.0129 |
| UCI Repository NMI | 0.3914 |

## Experiment Summary

**Successful Aspects:**
- Embeddings capture lifecycle signals (proven by 97-100% supervised probe accuracy)
- Signal persists across length normalization and modality filtering controls
- Low probe variance (0.0002) indicates consistent embedding quality
- UCI repository shows moderate unsupervised recovery (NMI=0.39)

**Failed Aspects:**
- K-means clustering fails to recover lifecycle structure (NMI=0.02)
- Severe class imbalance (8.3% RAI vs 91.7% General) prevents natural clustering
- Lexical baseline achieves 0.0 NMI (zero keyword matches), suggesting lifecycle is schema-based not content-based
- Repository heterogeneity: 15x NMI variation (UCI 0.39 vs HF 0.03)

**Root Cause:**
The core issue is the supervised-unsupervised gap: embeddings contain separable signals (proven by probes) but the RAI class is too sparse (8.3%) and distributed to form natural clusters. K-means assumes balanced clusters and produced 230/70 split instead of true 275/25 distribution.

**Recommended Actions:**
1. Re-sample dataset with balanced RAI/General ratio (50/50)
2. Replace K-means with density-based clustering (HDBSCAN) for imbalanced data
3. Test domain-specific embeddings (SciBERT)
4. Pivot to supervised lifecycle detection (leverages proven probe success)
5. Reframe as few-shot learning problem given RAI scarcity

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed
2. Whether the limitation is fundamental or circumstantial
3. Alternative approaches that might avoid this limitation

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-03-18T08:37:00Z*
*For cross-phase reference*