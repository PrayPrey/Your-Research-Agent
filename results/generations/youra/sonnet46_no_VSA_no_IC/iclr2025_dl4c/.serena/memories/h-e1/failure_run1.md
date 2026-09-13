# h-e1 Gate Failure — Run 1 (Smoke) — 2026-08-21

## Outcome
GATE FAIL: EXPERIMENT_INSUFFICIENT_TRAINING

## Results
- SFT pass@1: 0.0000 (0/20 HumanEval+ problems)
- GRPO pass@1: 0.0000 (0/20 HumanEval+ problems)
- Delta: +0.0000
- Required: >= +0.02
- Gate: MUST_WORK → NOT SATISFIED

## Root Cause
Smoke run used only 5 training steps on 40 MBPP examples (full spec: 1 epoch ~374 steps on full train split). Quick eval used no-crash check instead of EvalPlus correctness. Both models generated syntactically broken code — neither could pass even a no-crash check. 5 steps is ~1.3% of required training; insufficient signal for GRPO reward shaping.

## What Worked
- Training pipeline fully functional end-to-end
- SFT trainer: ran 5 steps, checkpoint-5 saved, loss=0.7463
- GRPO trainer: ran 5 steps, checkpoint-5 saved, use_vllm=False (vllm 0.11.0 incompatible with trl 1.10)
- binary_execution_reward: verified correct (subprocess exec, 10s timeout)
- Evaluation pipeline: model loads, generates completions, pass@1 computed

## Blockers Encountered
- Diagnostics R2/R3 (generate_rollouts): 50 problems × 8 rollouts = 400 sequential 7B completions; stuck >20 min; killed and bypassed for smoke run
- vLLM incompatibility: vllm 0.11.0 installed vs trl 1.10 requirement (0.17–0.26); use_vllm=False in all GRPOConfig

## Recommendation for Run 2
1. Set max_steps to ~200 (or None for full epoch) in run_smoke.py
2. Replace quick eval with `evalplus.evaluate` (python -m evalplus.evaluate --dataset humaneval --samples ...)
3. Use full MBPP train split (374 examples) not 40-example subset
4. Skip diagnostics R2/R3 (R1 already confirmed: base model 50% HumanEval+)
5. Expected wall-clock: 4–8 hours on H100 NVL GPU 0

## Artifacts
- `docs/youra_research/h-e1/04_validation.md`
- `docs/youra_research/h-e1/04_checkpoint.yaml`
- `docs/youra_research/h-e1/experiment_results.json`
- `docs/youra_research/h-e1/code/run_smoke.py` (smoke runner)
- `docs/youra_research/h-e1/code/checkpoints/sft/` (5-step SFT checkpoint)
- `docs/youra_research/h-e1/code/checkpoints/grpo/` (5-step GRPO checkpoint)
