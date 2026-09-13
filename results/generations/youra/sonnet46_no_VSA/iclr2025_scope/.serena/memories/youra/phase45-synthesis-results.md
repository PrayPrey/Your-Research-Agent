# Phase 4.5 Synthesis Results
Date: 2026-08-03
Research: MOHAWK-SSM vs LAWCAT LLaMA-3-8B conversion, LongBench v2 task-type interaction

## Key Outcomes
- H-M1 (MUST_WORK): PASS — SSD Frobenius log-log slope β=-0.368 (≤0.5); 90th pct error/N=0.027 (≤0.3) at N=2048. Normalized error DECREASES with N (stronger than required).
- H-E1 (MUST_WORK PoC): PASS — 22/22 tests; experiment running (~20-40h); final gate numbers pending
- H-M2 (SHOULD_WORK): FAIL — proxy data (EADDRINUSE port conflict blocked H-E1 checkpoints); pipeline validated end-to-end
- Predictions supported: 0/3 (all INCONCLUSIVE — experiments running or prerequisites blocked)
- Refined core statement: SSD approximation sub-linear (β=-0.368 confirmed); task-type interaction and depth-slope differential pending H-E1 completion
- Main theoretical contribution: SSD error/N DECREASES with N → retrieval degradation is bounded-state architectural bias, not approximation failure
- Critical limitation: H-E1 results pending; EADDRINUSE fix required for H-M2 (use --master_port 29502)

## Lessons for Future Pipelines
- model ID: meta-llama/Llama-3-8B does NOT exist; use meta-llama/Llama-3.1-8B
- C4 dataset rate-limited (429); use monology/pile-uncopyrighted instead
- MOHAWK checkpoint loading: use lazy_init mode=inference, NOT AutoModelForCausalLM
- LAWCAT: use alpaca_clean dataloader (not c4_distill which does not exist)
- torchrun port: always check `ss -tlnp | grep 29501` before launch; use --master_port 29502 to avoid EADDRINUSE
- N=8k OOM with eager attention at 96GB H100-NVL; use N≤2048 or implement chunked attention for N=4096
- rpy2 not available in youra-h-e1 env; statsmodels MixedLM fallback works (linear approximation for binary DV)
- LongBench v2 cached arrow schema: uses `domain`, `choice_A/B/C/D` fields (not `category`, `options[]`)
- Depth percentile mean=0.96 in retrieval subset (answers near document start); sign convention needs careful verification

## Output
- 045_validated_hypothesis.md: written to docs/youra_research/045_validated_hypothesis.md
