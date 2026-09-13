# Phase 4.5 Synthesis Results
Date: 2026-08-02
Research: Architecture-family adversarial vulnerability fingerprinting (Δ*-vectors)

## Key Outcomes
- Predictions supported: P1 PARTIALLY (η² met, p not), P2 REFUTED (LOMO at chance, N-degeneracy), P3 INCONCLUSIVE (h-m1–h-m4 not run)
- Refined core statement: η²=0.293 between-family Δ* effect (large, consistent across 83% categories); not significant at N=9 (40% power); LOMO=0.333 from N-degeneracy, not genuine null
- Main theoretical contribution: First formal η² measurement of architecture-family adversarial fingerprint; power analysis establishing N≥15 requirement
- Critical limitation: N=9 (3/family) insufficient for 80% power; LOMO geometrically degenerate at N=3/family

## Output File
docs/youra_research/045_validated_hypothesis.md (all 8 sections filled)

## Lessons for Future Pipelines
- LOMO with N<5/family is geometrically degenerate — do not interpret as evidence against hypothesis
- enc_dec models require multi-task fine-tuning (MNLI + SST-2) before NLI evaluation; SST-2-only causes degenerate ANLI-R3 results
- CheckList package must be pre-installed before experiment run
- Power analysis is essential before declaring MUST_WORK gate failure: distinguish underpowering from genuine null
- All 7 h-e1 code modules validated and reusable for h-e1-v2 and h-m* hypotheses
