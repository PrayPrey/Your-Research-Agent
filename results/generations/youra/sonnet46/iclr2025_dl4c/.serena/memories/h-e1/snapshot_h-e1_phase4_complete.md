# Hypothesis Completion Snapshot: h-e1

**Date**: 2026-03-15T12:22:00
**Hypothesis**: h-e1
**Type**: EXISTENCE
**Statement**: Under Qwen2.5-Coder-7B-Instruct inference on APPS introductory/medium problems filtered to S_term in [0.4, 0.75], at least 20% of rollouts achieve k_pass >= 2 (partial tractability).
**Final Status**: FAILED
**Gate Type**: MUST_WORK
**Gate Result**: FAIL
**Reflection Outcome**: ROUTED_TO_PHASE_0

## Results Summary
- Experiment: train_grpo.py, 6 seeds x 27 steps (grpo_early_stop)
- ZRF: 1.0 (all runs, all seeds) — zero reward throughout
- Gradient SNR: 0.0 (all runs) — no gradient signal
- Gate1 (ZRF reduction ≥20%): FAIL (0.0%)
- Gate2 (SNR ratio ≥1.5x): FAIL (1.0x)

## Outputs Generated
- 04_validation.md: ✓
- experiment_results.json: ✓
- figures/: 4 figures (ZRF curves, SNR curves, gate summary, per-seed heatmap)
- reflection_report.md: ✓
- code/: 15 tasks complete, all modules implemented

## Key Lessons
1. S_term threshold=0.85 (competition problems) → too hard for 7B model
2. max_completion_length=512 → all completions truncated → zero valid code
3. Must run prescreening before GRPO to verify tractability
4. Target introductory problems (S_term [0.3, 0.55]) for 7B model partial tractability

---
*Phase 4 complete for h-e1. Routing to Phase 0.*
