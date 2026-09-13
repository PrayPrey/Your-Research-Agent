# Phase 4.5 Synthesis — H-EntropySWA-v1 (Interim)

**Date:** 2026-08-22
**Research:** Zero-Shot Entropy-Guided Selective SWA Conversion in Llama-2-7B
**Pipeline:** TEST_scope (sonnet46, no_VSA_no_IC ablation)
**Status:** INTERIM — h-e1 validated; h-e2/h-m1/h-m2/h-c1 not yet executed

## Key Outcomes

- Predictions supported: 0/3 (P1, P2, P3 all INCONCLUSIVE — experiments not run)
- h-e1 PASS: Gini mean=0.6829 (std=0.0117), top-10% share=0.7172 (std=0.0196), 100% of 200 examples
- Refined core statement: Entropy criterion (head-mean pooling) confirmed as stable selector; accuracy-preservation claims pending h-e2/h-m1/h-m2
- Main theoretical contribution (confirmed): Head-mean entropy identifies strong attention concentration in Llama-2-7B (Gini=0.6829); head-mean >> head-max (Gini 0.681 vs 0.466)
- Critical limitation: Phase 4.5 invoked before hypothesis loop completed; all primary accuracy claims untested

## Critical Implementation Lessons

1. **Head-mean pooling is essential**: Head-max pooling drops Gini from 0.681 to 0.466 (32% reduction). Always use head-mean for layer-level entropy characterization in Llama-2-7B.
2. **h-e1 metric deviation**: Gate used Gini/top-10% instead of planned Spearman ρ — both valid; ρ confirmed via h-e2 continuation context reference but not in key_findings. Future runs should ensure key_findings explicitly report ρ values.
3. **QA F1 ablation (attn_k20/k40)**: Added to h-e1 beyond plan — provides directional P2 support (entropy 0.43pp vs random 0.67pp, p=0.4507) but underpowered and uses top-k truncation not SWA masking. Not citable as P2 evidence.
4. **SCOPE_CHANGE deviation**: Constructive — enriched evidence set while passing gate. Pattern: h-e1 implementer measured more than planned.

## Lessons for Future Pipelines

- Phase 4.5 should only be invoked after ALL sub-hypotheses complete (sub_hypotheses_complete=true). This was an early invocation producing an interim synthesis.
- Experiment state key_findings should explicitly include ALL gate criteria metrics (not just supplementary metrics); if Spearman ρ is the gate criterion, include ρ values in key_findings.
- Preliminary cross-hypothesis probing within h-eX scope (like the P2 QA F1 ablation in h-e1) is valuable but must be clearly labeled as preliminary/proxy — not cited as main hypothesis evidence.
- h-e2 is the next critical gate: if Δperplexity ≤ 2.0, hypothesis P1 is confirmed and full Phase 4.5 re-synthesis is warranted.

## Output

- `docs/youra_research/045_validated_hypothesis.md` — Interim synthesis (8 sections complete)
- All accuracy-preservation sections (Sections 2, 3.4, 8.3-8.5 P1/P2/P3 entries) marked PENDING
- Next: Execute h-e2 → h-m1 → h-m2 → h-c1 → re-invoke Phase 4.5
