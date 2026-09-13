# Phase 4 Failure Record: h-e1 (Run 4)

**Date:** 2026-03-15T12:22:00
**Hypothesis:** h-e1
**Run:** 4
**Final Status:** FAIL
**Failure Type:** DEGENERATE_EXPERIMENT_MISALIGNED_GATE
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Hypothesis Statement

Under Qwen2.5-Coder-7B-Instruct inference on APPS introductory/medium problems filtered to S_term in [0.4, 0.75], at least 20% of rollouts achieve k_pass >= 2 (partial tractability), as confirmed by pre-screening gate: bimodality_coefficient < 0.55, effective covariance rank > 3, and fraction(k_pass >= 2) >= 0.20.

## Gate Result

| Gate | Criterion | Actual | Required | Status |
|------|-----------|--------|----------|--------|
| Gate 1 | ZRF reduction (r_binary → r_ratio) | 0.0% | ≥ 20% | ❌ FAIL |
| Gate 2 | Gradient SNR ratio | 1.0x | ≥ 1.5x | ❌ FAIL |
| Overall | all_gates_passed | false | true | ❌ FAIL |

All key metrics: ZRF=1.0, Gradient SNR=0.0, Reward Mean=0.0, Reward Std=0.0 across all 6 runs.

## Root Cause Analysis

### Issue 1: S_term Threshold Too High (Primary)
- `s_term_labels.json` approximated S_term from problem category: competition→0.95, interview→0.75, intro→0.25
- With `s_term_high_threshold=0.85`, the "high" stratum = 2361 competition/interview problems (hardest problems)
- Qwen2.5-Coder-7B generates functionally incorrect code on nearly all of them → reward=0 everywhere

### Issue 2: max_completion_length=512 Too Short (Secondary)
- Competition-level problems require 100-400+ lines of Python → well over 512 tokens
- `completions/clipped_ratio=1.0` on most steps: all completions truncated

### Issue 3: Experiment-Hypothesis Mismatch
- H-E1 EXISTENCE was originally about **prescreening** (counting fraction(k_pass≥2) via direct inference)
- The Phase 4 experiment ran **GRPO training** with ZRF/SNR gates → measures different things
- The two approaches are fundamentally misaligned

### Consequence: Degenerate GRPO
- All GRPO advantages = r_i − mean(r) = 0 − 0 = 0
- All policy gradient signals = 0
- Comparison between r_binary and r_ratio is mathematically undefined

## Lessons Learned

1. S_term bins must be calibrated against actual model capability, not just problem category labels
2. max_completion_length must be set to ≥2048 for competition-level programming problems
3. EXISTENCE hypotheses should use direct inference (greedy/sample pass@k), NOT GRPO training
4. ZRF/SNR gates are only meaningful when reward variance > 0; verify with tiny smoke test first
5. S_term threshold=0.85 for a 7B model is too ambitious; consider 0.3-0.6 range for tractable problems

## Routing Decision

**ROUTED_TO_PHASE_0** — Fundamental misalignment between hypothesis design and experiment methodology requires hypothesis redesign from scratch.

## Recommendations for Phase 0

- Redesign h-e1 as a direct inference prescreening experiment (not GRPO)
- Use S_term bins [0.3, 0.6] for tractable subset
- Use pass@k (k=8) via temperature sampling as the measurement method
- Set max_new_tokens ≥ 2048 for programming problems
- Verify at least 5% reward rate in a 50-problem smoke test before full experiment

---
*For cross-phase reference*
*Written at: 2026-03-15T12:22:00*
