# h-m1 Phase 4 Routing Decision

**Date:** 2026-08-20
**Hypothesis:** h-m1 — HCI venues (CHI/CSCW/IUI) score higher on SPECTER2 bidirectional alignment framing than ML venues (NeurIPS/ICML/ICLR/ACL/EMNLP)
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Key Findings

- SPECTER2 Mann-Whitney U p=1.000 (one-sided HCI>ML), rbc=-0.831 — direction REVERSED
- HCI median framing score=-0.1289, ML median=-0.0709 (ML > HCI, opposite of hypothesis)
- MiniLM baseline confirms same direction: rbc=-0.826
- Temporal stratification: pre-2022 rbc=-0.785, post-2022 rbc=-0.972 — consistent reversal
- Corpus: 210 papers (n_hci=70, n_ml=46) from S2 API

## Root Cause

h-e1 centroids trained on ML-centric alignment reading list (huashen218/bidirectional-alignment-reading-list). The "bidirectional" centroid captures ML alignment discourse semantics, not HCI human-values alignment. ML papers are closer to this centroid by construction.

## Phase 0 Suggestions

1. Reformulate with HCI-appropriate seed corpus
2. Train venue-specific centroids using venue labels rather than reading-list labels
3. Consider TF-IDF vocabulary-based mechanism instead of embedding-based
4. Flip framing: test ML > HCI on alignment (data supports this direction)
