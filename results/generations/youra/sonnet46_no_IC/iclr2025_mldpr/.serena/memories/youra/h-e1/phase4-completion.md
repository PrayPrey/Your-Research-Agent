# H-E1 Phase 4 Completion Record

**Completed:** 2026-08-04T16:00:00Z
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Hypothesis
H-E1 (EXISTENCE): Partial Spearman ρ(submission_count, r_i | architecture_era_code) > 0.3, p < 0.01
Dataset: pwc-archive/evaluation-tables (HuggingFace)

## Experiment Results
- Partial Spearman ρ = -0.1392 (required > 0.3): FAIL
- p-value = 0.1763 (required < 0.01): FAIL
- 95% CI: [-0.33, 0.06]
- n = 97 qualifying benchmarks
- Logistic fit convergence: 100% (97/97)
- Direction: NEGATIVE (opposite to hypothesis)

## Key Insight
High-submission benchmarks saturate MORE SLOWLY, not faster. Benchmark popularity
is sustained by lack of saturation — researchers submit because benchmark is unsolved.

## Infrastructure (reusable)
- src/h_e1/data_pipeline.py — PwC HF loader, 9681 rows, cached at results/pwc_flat_cache.csv
- src/h_e1/filter.py — accuracy filter, MIN_RECORDS=15, MIN_YEAR_SPAN=5
- src/h_e1/features.py — logistic saturation fit (scipy TRF), architecture era assignment
- src/h_e1/analysis.py — pingouin partial_corr (columns: r, CI95, p_val), naive OLS
- src/h_e1/visualization.py — 5 figures
- src/h_e1/experiment.py — orchestration

## Output Files
- docs/youra_research/h-e1/04_validation.md
- docs/youra_research/h-e1/04_checkpoint.yaml
- docs/youra_research/h-e1/reflection_report.md
- docs/youra_research/h-e1/results/correlation_results.json
- docs/youra_research/h-e1/results/benchmark_features.csv
- docs/youra_research/h-e1/results/pwc_flat_cache.csv
- docs/youra_research/h-e1/figures/ (5 figures)
