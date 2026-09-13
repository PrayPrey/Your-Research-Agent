# 3. Methodology

## 3.1 Motivation: Offline Variance Profiling

Our approach is motivated by the GRPO gradient starvation identity: within-group reward standard deviation σ = √(k(G−k))/G equals zero when k=0 or k=G. For binary execution rewards, the expected variance for problem i with pass rate p_i is:

> Var_i = p_i · (1 − p_i)

This is maximized at p_i = 0.5 (equal probability of pass and fail) and equals zero for trivially easy (p_i ≈ 1) or trivially hard (p_i ≈ 0) problems. The key insight: if we can identify problems near p_i ≈ 0.5 *before* training begins, we can concentrate GRPO gradient steps on the productive fraction of data without paying the per-step cost of online difficulty estimation.

**Rationale for offline over online:** Online selection methods (VIGOR, Prompt Replay, LZE) require maintaining difficulty estimates throughout training and are tightly coupled to the training loop. For practitioners running short RLEF regimes (20–50 steps) with frequent hyperparameter sweeps, the ability to profile once and reuse the selection across runs has practical value. A frozen model's performance on a problem set should be a stable proxy over a short (20–50 step) training window — the model's capabilities do not change dramatically over such a short regime.

## 3.2 Offline Variance Profiling

**Protocol:**

1. Load the frozen base model (DeepSeek-Coder-7B-Instruct, weights frozen, no gradient computation).
2. For each problem i in the training pool (MBPP training split, 374 problems), generate k=4 independent completions using vLLM batch inference (temperature=1.0, top_p=0.95, max_new_tokens=128).
3. Execute each completion against the problem's test cases using subprocess execution (5-second timeout). Record binary outcome: 1 if all tests pass, 0 otherwise.
4. Compute pass rate p_i = (number of passing completions) / k.
5. Compute variance estimate: v_i = p_i · (1 − p_i).

**Implementation:** vLLM batch inference (gpu_memory_utilization=0.75) reduces profiling time from ~8 hours (sequential HF inference at k=8, max_new_tokens=512) to ~32 seconds for 374×4=1,496 completions on H100 NVL. This speed advantage is the primary practical benefit of offline profiling.

**Parameter note:** The design specified k=8 and max_new_tokens=512. Hardware constraints (sequential HF inference at those parameters requires ~8h) and vLLM-TRL incompatibility (vLLM 0.11.0 + TRL 1.10) required reduction to k=4, max_new_tokens=128 for the profiling phase while using max_completion_length=512 in training. This parameter mismatch is a central finding (Section 5.3) and is the most likely root cause of the cold-start failure observed in training.

## 3.3 Variance-Guided Selection

Given the per-problem variance estimates {v_i}, select the top-k problems by variance:

> S_variance = argsort(v_i, descending=True)[:k]

where k=50 in our experiments. This selects problems where the model's pass rate is closest to 0.5 — the zone of maximum gradient signal.

**Selection baseline:** For comparison, we use random-50 selection: k=50 problems drawn uniformly at random from the full training pool (seed=42 for reproducibility). Random selection is the natural null hypothesis — the current default for practitioners without profiling infrastructure.

**Boundary behavior:** With k=4 discrete pass rates (0, 0.25, 0.5, 0.75, 1.0) under max_new_tokens=128, all intermediate-success problems cluster at variance=0.1875 (p_i=0.25, 1 of 4 completions passing). When fewer than 50 problems have variance > 0, the top-50 selection necessarily includes some zero-variance problems at the boundary. We report this boundary_gap=0 explicitly.

## 3.4 GRPO Training Protocol

After selection, we train with TRL GRPOTrainer (version 1.9.2) using the following configuration:

| Parameter | Value |
|-----------|-------|
| Model | deepseek-ai/deepseek-coder-7b-instruct-v1.5 |
| num_generations (G) | 4 |
| per_device_train_batch_size | 1 |
| generation_batch_size | 4 |
| max_completion_length | 512 |
| learning_rate | 5×10⁻⁷ (h-m2); 1×10⁻⁶ (h-m3) |
| max_steps | 50 (h-m2); 200 (h-m3) |
| beta (KL penalty) | 0.0 |
| use_vllm | False |
| processing_class | AutoTokenizer |
| logging_steps | 1 |

**Reward function:** Binary execution reward via subprocess execution (5-second timeout). Returns 1.0 if all test cases pass, 0.0 otherwise. The same reward function used in profiling, but with different generation parameters (max_completion_length=512 vs max_new_tokens=128 in profiling).

## 3.5 Key Diagnostic Metric

TRL automatically logs `frac_reward_zero_std` — the fraction of training groups where all G=4 completions have identical reward (all-zero or all-one), producing σ=0 and zero gradient. We monitor this metric throughout training as the primary diagnostic for whether data selection is having any effect. A value of 1.0 indicates complete gradient starvation; any value < 1.0 indicates some learning signal.

## 3.6 Evaluation

The original design called for HumanEval+ pass@1 evaluation at 50-step checkpoints using EvalPlus correctness-based scoring (164 problems, k=8 generations per problem). This evaluation was planned for h-m4 but was not conducted because cold-start (Section 5.3) prevented any checkpoint from being generated: no gradient steps produced nonzero reward, no meaningful policy update occurred, and the model's weights remained at initialization. We report the cold-start finding as a prerequisite failure rather than an evaluation result.
