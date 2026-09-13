# Phase 4.5 Synthesis Results

Date: 2026-08-03
Research: SE_N5 + min_logprob ensemble for LLM uncertainty quantification on TriviaQA dev / Llama-3.1-8B

## Key Outcomes

- Predictions supported: 0 fully / 1 partially (P2: partial R² directional) / 2 inconclusive (P1, P3)
- Refined core statement: SE_N5 and min_logprob empirically near-orthogonal (|r|=0.049); partial R²=0.0101 directionally positive; full confirmation at N=2500 (h-e1-v2) pending
- Main theoretical contribution: First empirical measurement of |r|(SE_N5, min_logprob)=0.049 on Llama-3.1-8B/TriviaQA dev, grounding Kuhn et al. 2023 algebraic distinctness argument empirically
- Critical limitation: h-e1 ran at N=300 (12% of spec N=2500); partial R² gate requires N=2500 for statistical power

## Pipeline State After Phase 4.5

- h-e1: PARTIAL (SELF_MODIFY → h-e1-v2, N=2500)
- h-m1, h-m2, h-m3: NOT_STARTED (blocked on h-e1-v2)
- Output: docs/youra_research/045_validated_hypothesis.md

## Lessons for Future Pipelines

- PoC smoke tests (N-reduction) decouple correlation estimation (stable at N=300) from partial R² gate (requires N=2500); design gates accordingly
- Circularity pre-test (ρ(SE, judge) < 0.40) is a reusable protocol for any NLI-based ensemble benchmark
- |r|=0.049 << 0.7 is the decisive independence evidence; ABANDON threshold (0.85) not triggered = safe to proceed
