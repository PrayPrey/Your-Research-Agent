# 4. Experimental Setup

## 4.1 Research Questions

Our experiments are designed to test the causal chain underlying offline variance-guided selection: does a gradient-signal substrate exist? → does variance selection identify it? → does training exploit it?

**RQ1 (Existence):** Does the MBPP training split exhibit a non-degenerate binary execution reward variance distribution for DeepSeek-Coder-7B-Instruct? Is there a meaningful subset of problems with intermediate pass rates (variance > 0.1)? *(Hypothesis h-e1)*

**RQ2 (Selection Signal):** Does top-50 variance-guided selection achieve statistically significantly higher mean variance than random-50 selection? Does the selected distribution stochastically dominate random selection? *(Hypothesis h-m1)*

**RQ3 (Gradient Concentration):** Does GRPO training on the variance-selected subset produce lower frac_reward_zero_std than random-50 selection, confirming that the selection signal translates to actual gradient concentration during training? *(Hypotheses h-m2, h-m3)*

RQ3 is the critical link in the causal chain: if selection does not reduce gradient starvation during training, the selection signal — however robust analytically — provides no training benefit.

## 4.2 Dataset

We use the **MBPP (Mostly Basic Python Problems)** training split [Austin et al., 2021]: 374 Python programming problems, sourced from `google-research-datasets/mbpp` (HuggingFace Datasets), subset=full, split=train.

**Why MBPP:** MBPP is the standard benchmark for binary execution reward RLEF in code generation [Gehring et al., 2024]. It spans a range of problem difficulties (from simple string manipulation to more complex algorithmic tasks) and provides test-case-based execution verification. The 374-problem training split provides a large enough pool for meaningful subset selection.

**Why not HumanEval+ directly for training:** HumanEval+ is used for evaluation (measuring transfer generalization), not training. MBPP training → HumanEval+ evaluation is the standard RLEF protocol [Gehring et al., 2024; Skopin & Kotelnikov, 2025].

## 4.3 Model

We use **DeepSeek-Coder-7B-Instruct** (deepseek-ai/deepseek-coder-7b-instruct-v1.5, HuggingFace), a 7B-parameter instruction-tuned code generation model.

**Why DeepSeek-Coder-7B:** (1) Confirmed functional with TRL GRPOTrainer in our environment (use_vllm=False, generation_batch_size=4, H100 NVL). (2) 7B scale balances capability (non-trivial MBPP performance, so intermediate-difficulty problems exist) with tractable training time on a single GPU. (3) Widely used in code RLEF research.

## 4.4 Baselines and Conditions

| Condition | Description | Hypotheses |
|-----------|-------------|------------|
| **variance-50** | Top-50 MBPP problems by offline variance profiling (frozen model, k=4, max_new_tokens=128) | h-m2, h-m3 |
| **random-50** | 50 MBPP problems drawn uniformly at random (seed=42) | h-m2, h-m3 |
| **profiling baseline** | All 374 MBPP problems profiled (no GRPO training) | h-e1, h-m1 |

**Why random-50:** Random selection is the natural null hypothesis — the default for practitioners without profiling infrastructure. Equal size (N=50) controls for the number of gradient steps per epoch. Fixed seed ensures reproducibility.

## 4.5 Evaluation Metrics

**Primary (profiling phase):**
- `count_nonzero_variance`: Number of problems with v_i = p_i(1−p_i) > 0.1 (gate threshold: ≥15 problems for h-e1)
- `mean_var_selected` vs `mean_var_random`: Mean variance of top-50 vs random-50 selections (Mann-Whitney U test, one-sided, α=0.05)

**Primary (training phase):**
- `frac_reward_zero_std`: Fraction of training groups with σ_reward = 0 (TRL built-in metric, logged every step). Target: mean frac_reward_zero_std(variance-50) < mean frac_reward_zero_std(random-50) at steps 10, 20, 50.

**Planned but not conducted:**
- HumanEval+ pass@1 at 50-step checkpoint via EvalPlus correctness-based evaluation. Contingent on nonzero reward signal during training.

## 4.6 Implementation Details

**Profiling environment:**
- Inference: vLLM 0.8.x (batch inference, gpu_memory_utilization=0.75)
- Hardware: H100 NVL (80GB HBM3)
- Execution: subprocess with 5-second timeout per test case

**Training environment:**
- Framework: TRL 1.9.2 GRPOTrainer
- Hardware: H100 NVL (single GPU)
- Key API: `processing_class=AutoTokenizer` (not deprecated `tokenizer=`), `save_strategy="no"` (checkpoint not saved given cold-start)
- Dataset loading: MBPP subset="full" (NOT "sanitized" — the sanitized subset excludes problems the full h-m2 training requires)

**h-m2 configuration:** 50 training steps, learning_rate=5×10⁻⁷, both variance-50 and random-50 conditions.

**h-m3 configuration:** 200 training steps, learning_rate=1×10⁻⁶ (doubled), variance-50 condition only — an attempt to break cold-start with extended training and higher learning rate.

## 4.7 Statistical Significance

For the selection signal comparison (RQ2), we report Mann-Whitney U one-sided test (H_a: variance-50 > random-50 in mean variance), with p < 0.05 as the significance threshold. Mann-Whitney U is appropriate because the variance distributions are non-normal (discrete, with mass at 0.0 and 0.1875 only).

For the training gradient analysis (RQ3), we report frac_reward_zero_std at every logged step (logging_steps=1). Given the cold-start result (both conditions at exactly 1.0 throughout), statistical testing is not required — the finding is deterministic.
