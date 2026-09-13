# Hypothesis Completion Snapshot: h-m4

**Date:** 2026-03-18T17:10:00+00:00
**Hypothesis:** h-m4
**Statement:** Under M=15-bin ECE computation per difficulty tier using P(True) confidence, if DELTA_ECE = ECE(hard) - ECE(easy) is measured with 1000-sample bootstrap 95% CIs and compared to tier-specific null baseline, then DELTA_ECE >= 0.03 (CI excluding zero) in >=2/3 model families AND persists after global temperature scaling (T fitted on 20% holdout).
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)

## Results
- Gate Type: MUST_WORK
- Gate Result: FAIL
- Models passing P1: 1/3 (deepseek_6.7b only)
- llama3_8b: DELTA_ECE=0.0034, CI=[-0.0074, 0.0133] — near-zero, CI includes zero
- codellama_7b: DELTA_ECE=-0.2490, CI=[-0.2589, -0.2391] — inverted direction
- deepseek_6.7b: DELTA_ECE=0.2979, CI=[0.2849, 0.3115] — strong PASS

## Reflection
- Reflection outcome: ROUTED_TO_PHASE_0
- Reason: MUST_WORK FAIL — effect is architecture-dependent, not universal
- CodeLlama inversion is fundamental (not fixable by tuning)
- Route: Phase 0 for new hypothesis generation

## Lessons for Phase 0
1. Never assume calibration phenomena are universal across LLM families
2. Degenerate tier assignments (CodeLlama n_easy=0 on HumanEval) invalidate ECE
3. DeepSeek-Coder confirms the mechanism is real for capable code models
4. Consider model-conditional hypotheses (condition on model capability)
5. P(True) confidence infrastructure is validated and reusable (h-m3)

---
*Per-hypothesis snapshot for Phase 2A reference*
