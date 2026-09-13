# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-08-21T07:30:00Z
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** GATE FAIL
**Failure Type:** EXPERIMENT_INSUFFICIENT_TRAINING

## Performance Gap

| Metric | Ours (GRPO) | Baseline (SFT) | Gap |
|--------|-------------|----------------|-----|
| pass@1 (HumanEval+) | 0.0000 | 0.0000 | 0.0000 |

## Root Cause Analysis

- Only 5 gradient steps on 40 MBPP examples (<2% of full epoch)
- Loose eval metric: no-crash check only, not correctness-based EvalPlus
- Insufficient training for either SFT or GRPO to converge
- Pipeline is functionally sound end-to-end; gate failure is measurement artifact

## Lessons Learned

1. Smoke run with 5 steps cannot distinguish trained vs untrained models at pass@1=0
2. Proper EvalPlus evaluation required (evalplus.evaluate, not crash-only check)
3. Need ≥100 steps (ideally full epoch ~374 steps) for meaningful GRPO signal
4. vLLM 0.11.0 incompatible with trl 1.10 — use use_vllm=False for this env
5. generation_batch_size=4 recommended to reduce OOM risk on H100 NVL

## Feedback for Next Phase

### Suggested Modifications
- Run full epoch (max_steps=None) or at least 200+ steps
- Use evalplus.evaluate for correctness-based pass@1
- Keep use_vllm=False (vllm 0.11.0 + trl 1.10 incompatible)

### What NOT To Do
- Do not use crash-only eval as pass@1 proxy
- Do not use <10 training steps as validity signal

### What Showed Promise
- Training pipeline runs end-to-end without errors
- Binary execution reward function verified working
- Base model achieves ~50% HumanEval+ (R1 diagnostic confirmed)

---
*Written at: 2026-08-21T07:30:00Z*
*For cross-phase reference*
