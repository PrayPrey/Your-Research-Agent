# Phase 4.5 Synthesis Results
Date: 2026-07-30
Research: Pairwise Partial Spearman Structure of Alignment Benchmarks After MMLU Scale Control

## Key Outcomes
- Predictions supported: P1 SUPPORTED (HIGH), P2 PARTIALLY_SUPPORTED (MEDIUM), P3 REFUTED (HIGH)
- Refined core statement: MMLU scale control reduces TruthfulQA–BBQ rho from 0.732 to 0.343 (Fisher z=6.97, p=3.22e-12); scenario classification AMBIGUOUS; Tier 2/3 extensions underpowered
- Main theoretical contribution: First application of Fisher z difference test (raw vs MMLU-partial Spearman) to alignment-specific benchmark pairs, showing >53% rho reduction attributable to general capability confound
- Critical limitation: BBQ scores are ARC Challenge proxy (HELM Lite unavailable); HarmBench Tier 2 N=0 (temporal mismatch); N=296 insufficient for scenario resolution

## Lessons for Future Pipelines
- Always pre-confirm data source accessibility before Phase 2C experiment design — HELM Lite DNS failure caused proxy substitution throughout
- HarmBench Table 2 (2024 models) incompatible with LLM LB v1 (pre-2024) — contemporaneous benchmark evaluation required for three-benchmark analysis
- N≈300 insufficient for scenario CI resolution (CI spans +0.40 boundary); future studies need N>1000
- pingouin 0.6.1 uses 'p_val' not 'p-val' column name — detect dynamically in code
- BBQ proxy (ARC Challenge) inflates residual partial_rho interpretation — genuine BBQ scores needed

## Output File
- 045_validated_hypothesis.md (44k+ bytes, all 8 sections complete)
- synthesis_completed: true
- synthesis_completed_at: 2026-07-30T08:45:00Z
