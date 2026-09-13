# H-E2 Phase 4 Completion

**Completed:** 2026-08-02T10:45:00+00:00
**Status:** VALIDATED (PARTIAL gate — satisfied)

## Results

- n_valid: 496 of 500 TriviaQA prompts
- Model used: meta-llama/Llama-3.1-8B (Llama-3.3-70B-Instruct inaccessible, 403)
- VIF: mean_token_entropy=16.09, mean_logprob=15.50, content_token_variance=3.91, min_logprob=3.14
- gate_passed=True (< 3 features exceed VIF 5.0), all_pass=False
- MUST_WORK gate: SATISFIED

## Fallback ensemble (pre-registered)

Use `[min_logprob, content_token_variance]` in H-M1/H-M2/H-C1 (not all 4 features).

mean_token_entropy and mean_logprob are collinear in greedy decoding (entropy ≈ −log_prob). Expected per HALT paper.

## Fixes applied during Phase 4

- h_e1_code_dir: was 3 levels up (../../../), fixed to 2 (../../)
- sys.path: use append() not insert(0) — prevents h-e1 config.py shadowing h-e2
- datasets: upgraded 3.6.0→5.0.1 (3.6.0 removed `List` feature type, breaks TriviaQA cache)
- Llama-3.3-70B-Instruct: 403 gated → used Llama-3.1-8B

## Key files

- code/: config.py, vif_analysis.py, run_h_e2.py
- results/: features_500.csv, vif_results.csv, gate_result.json
- figures/: vif_bar.png, correlation_heatmap.png, scatter_matrix.png
- experiment_results.json, 04_validation.md
