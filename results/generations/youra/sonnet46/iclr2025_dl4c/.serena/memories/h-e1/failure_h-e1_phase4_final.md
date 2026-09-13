# Phase 4 Failure Record: h-e1 (Final)

## Metadata
- **hypothesis_id**: h-e1
- **type**: EXISTENCE
- **gate**: MUST_WORK
- **gate_result**: FAIL
- **phase**: Phase 4
- **experiment_completed_at**: 2026-03-15T12:13:33
- **routing**: Phase 0 (hypothesis redesign)
- **pipeline_project**: R_ratio vs R_binary GRPO mid-difficulty APPS

## Hypothesis Statement
Under Qwen2.5-Coder-7B-Instruct inference on APPS introductory/medium problems filtered to S_term in [0.4, 0.75], at least 20% of rollouts achieve k_pass >= 2 (partial tractability).

## Experiment Details
- Script: train_grpo.py (GRPO training, NOT prescreening)
- Model: Qwen/Qwen2.5-Coder-7B-Instruct
- Dataset: codeparrot/apps (5000 train problems, high stratum = 2361 problems, S_term>0.85)
- Seeds: 42, 1337, 2024 | Conditions: r_binary, r_ratio | Steps: 27/run

## Gate Results (ALL FAILED)
- Gate1 ZRF reduction ≥20%: FAIL (ZRF=1.0 both conditions, reduction=0.0%)
- Gate2 Gradient SNR ratio ≥1.5x: FAIL (SNR=0.0 both conditions, ratio=1.0)

## Root Causes
1. S_term threshold=0.85 too high → competition/interview problems → too hard for 7B model
2. max_completion_length=512 → all completions truncated → no valid code produced
3. Zero reward → zero GRPO advantage → no gradient → comparison meaningless
4. S_term was estimated via category labels (competition=0.95), not actual model performance

## Lessons Learned
1. Must run actual prescreening (k_pass counting) before GRPO training to verify tractability
2. For 7B models, target S_term ∈ [0.3, 0.55] (introductory problems), not 0.4-0.75
3. max_completion_length needs ≥1024 tokens for programming tasks
4. GRPO with 100% zero-reward is completely uninformative for reward signal comparison

## Cascade: h-m1, h-m2, h-m3, h-c1 all CASCADE_FAILED
