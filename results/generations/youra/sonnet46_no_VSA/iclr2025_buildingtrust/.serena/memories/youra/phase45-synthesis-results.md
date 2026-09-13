# Phase 4.5 Synthesis Results
Date: 2026-08-02
Research: YouRA — Architecture-family adversarial robustness fingerprinting (Δ*-vectors)

## Key Outcomes
- Predictions supported: 0.5/3 (P1 partially, P2 refuted/degenerate, P3 inconclusive)
- Refined core statement: Architecture families show large-effect Δ*-clustering (η²=0.293, 83% categories) but underpowered for significance at N=9; LOMO at chance from N-degeneracy (3 models/family)
- Main theoretical contribution: First formal effect-size quantification of between-family adversarial vulnerability (η²=0.293) under scale-matched, multi-attack-category conditions with statistical controls
- Critical limitation: N=9 → ~40% power; LOMO degenerate at N=3/family; mechanism chain (h-m1–h-m4) blocked on h-e1 gate

## Lessons for Future Pipelines
- LOMO classification requires N≥5 models/family; N=3 is geometrically degenerate — do not interpret at-chance LOMO as evidence against family separability
- enc_dec models must be fine-tuned on ALL evaluated task types (MNLI for NLI evaluation) before including in multi-task benchmarks
- Power analysis first: η²=0.29 requires N=15 total (5/family) for 80% power at α=0.05
- All 7 h-e1 code modules validated and reusable for h-e1-v2 expansion
- Phase 4.5 output: docs/youra_research/045_validated_hypothesis.md (v2.0, complete)
