# Limitation Record: h-e2 (Run 1)

**Date:** 2026-08-20T08:30:00+00:00
**Hypothesis:** h-e2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Structural corpus mismatch between huashen218/bidirectional-alignment-reading-list and Baum 2025 (arXiv:2506.06286). Only N=1 overlapping paper found (Shen et al. 2024, arXiv:2406.09264). Spearman r cannot be computed with N < 2. The hypothesis (framing scores correlate with constituency dimension) is not falsified — it is untestable on these two corpora.

## Failed Checks

- spearman_r > 0.60 (N/A — insufficient overlap for correlation)
- sufficient_n >= 20 (N=1, need N >= 20)
- scores_nonempty (no overlapping paper pairs with both score types)

## Partial Results

| Metric | Value |
|--------|-------|
| N_overlap | 1 |
| overlap_pct | 1.3% |
| gate_overlap_pass | True |
| gate_correlation_pass | False |
| spearman_r | null |

## Experiment Summary

huashen218 corpus (64 papers, ML/NLP 2018–2024) and Baum 2025 bibliography (15 papers, philosophy-of-AI) share only 1 paper. Jaccard overlap = 1.3% (well below 30% threshold — overlap criterion passes). However, N=1 is insufficient for Spearman r. Root cause: Baum 2025 cites traditional philosophy journals and pre-2020 foundational AI papers; huashen218 focuses on contemporary ML/NLP bidirectional alignment methodology. These are structurally distinct literatures.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. Alternative constituency scoring source with better huashen218 coverage (e.g., a taxonomy paper that cites contemporary ML/NLP work)
2. The RICE framework beneficiary dimension as fallback scoring (as specified in the experiment brief)
3. Expanding Baum 2025 corpus by resolving bib-format IDs via Semantic Scholar API (may recover a few more overlapping papers, but structural gap makes N >= 20 geometrically improbable)

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this limitation informs brainstorming to avoid similar corpus mismatch issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-20T08:30:00+00:00*
*For cross-phase reference*
