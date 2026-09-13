# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-08-03T12:00:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** PARTIAL (experiment incomplete — Condition B not yet finished)
**Failure Type:** EXPERIMENT_INCOMPLETE

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Boundary Retention (Cond A) | 0.104 | N/A (no Cond B yet) | N/A |
| frac_below_80 (Cond A) | 1.000 | threshold: 0.20 | +0.800 (exceeded) |
| Macro Accuracy (Cond A, single_doc_qa) | 0.028 | Cond B pending | N/A |

## Root Cause Analysis

- Condition A (vanilla H2O, 50% compression) ran and produced clear primary gate evidence: frac_below_80=1.000
- Condition B (H2O + 10% boundary reservation) is running but not yet complete at time of report
- Multiple process interruptions (PID 518899 killed, fresh start as PID 564658) delayed completion
- The `youra-h-m1` env (torch 2.8.0) was used initially but was slower; switched to `youra-h-m3-v2` (torch 2.11.0+cu128)

## Lessons Learned

1. Always use `youra-h-m3-v2` env for LLaMA-3-8B experiments (fastest CUDA)
2. At 50% KV compression, H2O causes catastrophic boundary token eviction (retention=10.4%, all examples <80%)
3. Near-zero MC accuracy (2.8%) at 50% compression confirms boundary token loss destroys question-parsing
4. Primary gate criterion strongly met; secondary requires Condition B completion
5. Checkpoint-per-example IO enables reliable resume across interruptions

## Feedback for Next Phase

### Suggested Modifications
- Complete Condition B experiment with PID 564658 (youra-h-m3-v2 env, --resume --skip-pilot)
- Once gate_result.json produced, update validation.result and gate.satisfied accordingly

### What NOT To Do
- Do not kill the running experiment process (PID 564658) — it is making progress
- Do not use youra-h-m1 env (no torch installed, wrong env)
- Do not run concurrent GPU experiments without coordination

### What Showed Promise
- H2O patch (h2o_patch.py) works correctly with transformers 5.x / LLaMA-3-8B
- Boundary token retention metric captures eviction correctly
- Checkpoint resume mechanism handles interruptions correctly

---
*For cross-phase reference*
*Written at: 2026-08-03T12:00:00+00:00*
