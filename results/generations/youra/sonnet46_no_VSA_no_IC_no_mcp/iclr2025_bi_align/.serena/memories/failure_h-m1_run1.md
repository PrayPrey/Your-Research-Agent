# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-25T21:30:02+00:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** synthetic_data_inversion
**Gate Type:** MUST_WORK
**Routing:** ROUTED_TO_PHASE_0

## Performance Gap

| Metric | Ours (RLHF) | Baseline (SFT) | Gap |
|--------|-------------|----------------|-----|
| Intra-group mean cosine sim | 0.9854 | 1.0000 | -0.0146 |
| Mann-Whitney p-value | 1.0000 | — | p >> 0.05 |
| Cohesion ratio (RLHF/SFT) | 0.9854 | — | < 1.0 (inverted) |

## Root Cause Analysis

- AlpacaEval 2.0 HuggingFace API was unavailable (deprecated `trust_remote_code` protocol)
- Triggered `_load_from_leaderboard_fallback()` synthetic data generator in h_e1/data_loader.py
- SFT synthetic templates (3 types, less variation) produce nearly identical embeddings (cosine sim ≈ 1.0)
- RLHF synthetic templates (7 types, more variation) produce more diverse embeddings (cosine sim ≈ 0.985)
- Result: SFT appears MORE cohesive than RLHF — the opposite of the hypothesis prediction
- This is a data artifact, not evidence against the hypothesis mechanism

## Lessons Learned

1. Real AlpacaEval 2.0 data must be acquired via alternative path (direct GitHub download from tatsu-lab/alpaca_eval releases, or alpaca_eval Python package) before H-M1 can be validly tested
2. The analysis pipeline (compute_intra_group_cohesion, compute_centroid_stability, run_mann_whitney, gate_check) is mechanistically correct — all 14 pytest tests pass
3. Synthetic fallback generators must use equal template diversity across alignment groups to avoid cohesion inversion
4. Centroid stability metric is robust (>0.999) regardless of data source — reliable for real data runs
5. H-M2 and H-M3 share the same data dependency — acquire real data before proceeding with either

## Feedback for Next Phase (Phase 0 / Redesign)

### Suggested Modifications
- Acquire real AlpacaEval 2.0 output data via: `pip install alpaca_eval` then `alpaca_eval --help`
- Alternative: Direct download from https://github.com/tatsu-lab/alpaca_eval releases
- The R5 fallback (explicit style features: mean_length r=0.963, hedge_freq r=0.534) may serve as alternative mechanism evidence

### What NOT To Do
- Do not use the leaderboard fallback synthetic generator for cohesion studies
- Do not proceed with H-M2/H-M3 until real embedding data is available

### What Showed Promise
- Code implementation is complete and validated (14/14 tests pass)
- Pipeline runs in <2 seconds on precomputed embeddings
- Centroid stability analysis is robust
- All 5 figures generated successfully
- The RLHF convergence hypothesis is plausible — only the data source was wrong

---
*Failure record written at: 2026-08-25T21:30:02+00:00*
*For cross-phase reference — read by Phase 0 brainstorming*
