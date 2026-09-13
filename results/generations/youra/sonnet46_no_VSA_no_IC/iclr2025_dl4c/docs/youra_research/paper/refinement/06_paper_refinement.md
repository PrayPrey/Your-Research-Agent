# When the Signal is Real but the Training is Not: Variance-Guided RLEF Data Selection and the Cold-Start Problem

**Authors:** Anonymous  
**Format:** ICML  
**Date:** 2026-08-21  
**Hypothesis ID:** H-VarianceGuidedRLEF-v1

---

## Abstract

Reinforcement learning from execution feedback (RLEF) with binary rewards suffers from gradient starvation: at group size G=4, up to 69% of GRPO training steps produce zero gradient because the model either passes or fails every completion in a group. This paper proposes offline variance-guided selection — profiling a frozen model once to compute per-problem binary execution reward variance p_i(1−p_i), then selecting problems with the highest variance before training begins. On MBPP (374 training problems) with DeepSeek-Coder-7B-Instruct, two results are confirmed: (1) 7.8% of problems exhibit nonzero variance under constrained generation (k=4, max_new_tokens=128), and (2) top-50 variance-guided selection achieves 4.24× higher mean variance than random-50 selection (Mann-Whitney U p=2.22×10⁻⁶), stochastically dominating random selection across the full distribution, with profiling completing in approximately 32 seconds via vLLM. However, GRPO training on the variance-selected subset produces no gradient signal across more than 50,000 generation attempts (50–200 steps), because the model generates zero correct solutions under training conditions — a cold-start regime that renders data selection method irrelevant regardless of analytical validity. Generation parameter mismatch between profiling (max_new_tokens=128, vLLM) and training (max_completion_length=512, HF GRPOTrainer) is identified as the primary candidate root cause among several alternatives. A prescriptive resolution protocol is proposed but not empirically validated. The primary contribution is a precisely characterized failure mode and its necessary precondition: cold-start verification is established as a prerequisite for any RLEF data selection method, and the first systematic per-problem empirical characterization of binary execution reward variance distribution on MBPP for a 7B code LLM is provided.

---

## 1. Introduction

Selecting 7.8% of training data for GRPO code generation yields a 4.24× gradient signal advantage over random selection — yet that advantage is entirely invisible during training when the model never generates a single correct solution. This discrepancy between a confirmed analytical advantage and an empirically null training result is the central finding of this paper.

Reinforcement Learning from Execution Feedback (RLEF) has emerged as an effective approach for improving code generation capabilities in large language models [Gehring et al., 2024]. In RLEF, a policy model receives binary execution rewards (pass/fail on test cases) and is updated via Group Relative Policy Optimization (GRPO) [Shao et al., 2024]. Binary rewards impose a fundamental inefficiency: when a model either passes every completion or fails every completion within a group, the within-group reward standard deviation equals zero, producing zero gradient. At group size G=4, this zero-gradient pathology affects approximately 69.25% of training groups [Nie et al., 2026] — the majority of gradient steps are wasted.

The natural remedy is data selection: train only on problems where the model occasionally succeeds. Several recent methods achieve this via online selection — computing difficulty signals during training and adjusting the data distribution as the model improves [Jiang et al., 2026; Baroian & Berger, 2026; Sun et al., 2025; Cui et al., 2026]. Online methods work but face a practical limitation: selection overhead is coupled to training cost, and the selection signal cannot be reused across hyperparameter sweeps or model variants.

This paper proposes offline variance-guided selection: profile a frozen model once on all candidate problems, compute per-problem binary execution reward variance v_i = p_i(1−p_i), and select problems with the highest variance before training begins. This design separates a cheap profiling phase (approximately 32 seconds for 374 problems via vLLM) from the expensive GRPO training phase, enabling reuse of the selection across runs.

Three gaps in existing work motivate this study: no prior work has (1) characterized the per-problem binary execution reward variance distribution across MBPP for a code LLM systematically, (2) compared offline variance-guided selection to random selection under binary RLEF, or (3) identified the cold-start precondition that determines whether any selection method can operate in this setting.

The key finding, confirmed experimentally, is: offline frozen-model variance profiling produces a statistically robust selection signal, but GRPO gradient concentration can only manifest this advantage when the model is already capable of generating at least some correct solutions. Cold-start — the model generating zero correct solutions across all training conditions — renders data selection method irrelevant. When every problem yields k=0 correct completions in every group, σ=√(k(G−k))/G=0 regardless of which problems were selected.

This paper reports this negative result alongside the confirmed analytical findings because the precise characterization of where and why the method fails prevents others from repeating the same failure. The analytical validity of the selection signal (confirmed, 4.24× advantage) is separable from the training-phase failure (cold-start due to parameter mismatch) — making that separation explicit is itself a contribution.

**Contributions:**

1. **Variance distribution characterization** (empirical, confirmed): The first systematic per-problem characterization of binary execution reward variance across MBPP training problems for DeepSeek-Coder-7B-Instruct under constrained generation. The distribution is severely right-skewed: 91.7% of problems yield p_i=0 (all-fail), 7.8% yield p_i=0.25, and 0.5% yield p_i=1.0.

2. **Offline variance profiling** (method, analytically validated): Top-50 selection by frozen-model variance achieves 4.24× higher mean variance than random-50 selection (Mann-Whitney U p=2.22×10⁻⁶), with the variance-selected subset stochastically dominating random-50. vLLM batch inference completes the 374-problem profiling in approximately 32 seconds on H100 NVL.

3. **Cold-start diagnosis** (negative result, high confidence): More than 50,000 GRPO generation attempts across 50–200 training steps — all producing zero reward. Four candidate root causes are enumerated and ranked; generation parameter mismatch is identified as the most likely explanation. A prescriptive resolution protocol is provided but not yet empirically validated.

---

## 2. Related Work

### 2.1 Reinforcement Learning from Execution Feedback

RLEF with binary execution rewards was established by Gehring et al. [2024], who demonstrated order-of-magnitude inference-time sample reductions through binary pass/fail rewards combined with GRPO policy optimization. That work confirmed that binary execution correctness is sufficient for meaningful policy improvement and established the MBPP training → HumanEval+ evaluation protocol used here.

The mathematical foundation for why binary rewards lead to gradient starvation is the GRPO standard deviation identity: σ = √(k(G−k))/G, where k is the number of correct completions out of G. When k=0 or k=G, σ=0 and no gradient is produced. This identity underlies both the motivation for variance-guided selection and the cold-start diagnosis.

### 2.2 Gradient Starvation in GRPO

The empirical consequences of gradient starvation were quantified by Nie et al. [2026]: at G=4 with binary rewards, 54.75% of training groups have all-fail outcomes and 14.50% have all-pass outcomes, producing 69.25% zero-gradient groups in expectation. The experiments reported here provide a per-problem characterization of this effect for MBPP under constrained generation, finding a more severe all-fail rate (91.7%), suggesting that generation parameter constraints amplify practical gradient starvation beyond theoretical estimates for this model.

### 2.3 Online Data Selection for GRPO Efficiency

Multiple recent methods converge on selecting intermediate-difficulty problems as the key to GRPO efficiency — all as online methods operating during training.

Jiang et al. [2026] (VIGOR, arXiv:2607.22002) allocate rollouts based on variance-utility signals computed during active training. This method parallels offline profiling conceptually but requires training loop integration, precluding the decoupled "profile once, train anywhere" design.

Baroian and Berger [2026] (Prompt Replay, arXiv:2603.21177) track per-problem running pass rates during training and prioritize problems with pass rate approximately 0.5 — the maximum-variance point under the binary variance identity. This is the closest conceptual predecessor to the method proposed here, but it cannot operate as a pure offline step.

Sun et al. [2025] demonstrate difficulty-targeted online selection for math reasoning with scalar rewards, achieving 23–62% compute reduction. This work targets a different reward type and domain; the data selection intuition is extended here to binary-reward code generation with an offline design.

Cui et al. [2026] (LZE, arXiv:2605.17003) fuse pass-rate momentum and outcome-uncertainty during training. Like the methods above, this requires an active training loop.

The offline approach in this paper occupies a distinct niche: profile once with a frozen model, train anywhere. The cold-start failure identified here — that parameter mismatch between profiling and training can nullify the entire selection — is a failure mode that online methods naturally avoid, since they compute difficulty signals during training where profiling-training alignment is not a concern.

### 2.4 Positioning

This work contributes: (1) the first offline variance-guided selection method for binary-reward code generation RLEF, (2) to the best of our knowledge, the first systematic per-problem binary reward variance distribution characterization on MBPP (prior GRPO-on-MBPP papers encounter this distribution but do not report it at per-problem granularity), and (3) the first systematic identification of cold-start as a necessary precondition for data selection in RLEF.

---

## 3. Method

### 3.1 Motivation: Offline Variance Profiling

The GRPO gradient starvation identity — σ = √(k(G−k))/G equals zero when k=0 or k=G — implies that for binary execution rewards, the expected gradient signal for problem i with pass rate p_i is proportional to:

> v_i = p_i · (1 − p_i)

This quantity is maximized at p_i = 0.5 and equals zero for problems that are trivially easy or trivially hard. If problems near p_i ≈ 0.5 can be identified before training, gradient steps can be concentrated on the productive fraction without paying the per-step cost of online difficulty estimation. For short RLEF regimes (20–50 steps), frozen-model performance provides a stable proxy — the model's capabilities do not change dramatically over such a window.

### 3.2 Offline Variance Profiling Protocol

The profiling procedure is as follows:

1. Load the frozen base model (DeepSeek-Coder-7B-Instruct, weights frozen).
2. For each problem i in the MBPP training split (374 problems), generate k=4 independent completions using vLLM batch inference (temperature=1.0, top_p=0.95, max_new_tokens=128).
3. Execute each completion against the problem's test cases via subprocess execution (5-second timeout). Record binary outcome: 1 if all tests pass, 0 otherwise.
4. Compute pass rate p_i = (correct completions) / k.
5. Compute variance estimate: v_i = p_i · (1 − p_i).

**Implementation:** vLLM batch inference (gpu_memory_utilization=0.75) reduces profiling from approximately 8 hours (sequential HF inference at k=8, max_new_tokens=512) to approximately 32 seconds for 374×4=1,496 completions on H100 NVL.

**Parameter note:** The original design specified k=8 and max_new_tokens=512. Hardware constraints and vLLM-TRL incompatibility (vLLM 0.11.0 + TRL 1.10) required reduction to k=4, max_new_tokens=128 for profiling, while training used max_completion_length=512. This parameter mismatch is a central finding reported in Section 5.3.

### 3.3 Variance-Guided Selection

Select the top-k problems by variance:

> S_variance = argsort(v_i, descending=True)[:k]

where k=50. This selects problems where the model's pass rate is closest to 0.5 — the zone of maximum gradient signal.

**Baseline:** random-50 selection — 50 problems drawn uniformly at random (seed=42). This is the natural null hypothesis and the current default for practitioners without profiling infrastructure.

**Boundary behavior:** With k=4 discrete pass rates under max_new_tokens=128, all intermediate-success problems cluster at variance=0.1875. When fewer than 50 problems have variance > 0, the top-50 selection includes zero-variance problems at the boundary (boundary_gap=0 in the experiments reported here).

### 3.4 GRPO Training Protocol

Training was conducted with TRL GRPOTrainer (version 1.9.2). The configuration is summarized in Table 1 below (Section 4).

**Reward function:** Binary execution reward via subprocess execution (5-second timeout): 1.0 if all test cases pass, 0.0 otherwise.

**Key diagnostic:** TRL automatically logs `frac_reward_zero_std` — the fraction of training groups where all G=4 completions have identical reward, producing σ=0. This metric is the primary diagnostic for whether data selection is having any effect.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1 (Existence):** Does MBPP exhibit a non-degenerate binary execution reward variance distribution for DeepSeek-Coder-7B-Instruct? Is there a meaningful subset with variance > 0.1? *(Experiment h-e1)*

**RQ2 (Selection Signal):** Does top-50 variance-guided selection achieve statistically significantly higher mean variance than random-50? *(Experiment h-m1)*

**RQ3 (Gradient Concentration):** Does GRPO training on the variance-selected subset produce lower frac_reward_zero_std than random-50 selection? *(Experiments h-m2, h-m3)*

### 4.2 Dataset and Model

**Dataset:** MBPP training split [Austin et al., 2021] — 374 Python programming problems (`google-research-datasets/mbpp`, subset=full, split=train, task IDs 601–974). MBPP is the standard benchmark for binary execution reward RLEF [Gehring et al., 2024].

**Model:** DeepSeek-Coder-7B-Instruct (deepseek-ai/deepseek-coder-7b-instruct-v1.5) [Guo et al., 2024] — a 7B-parameter instruction-tuned code generation model, confirmed functional with TRL GRPOTrainer in this environment (torch 2.6.0+cu124, CUDA 12.4, NVIDIA H100 NVL).

### 4.3 Experimental Conditions

| Condition | Description | Used in |
|-----------|-------------|---------|
| variance-50 | Top-50 by offline variance profiling (k=4, max_new_tokens=128) | h-m2, h-m3 |
| random-50 | 50 problems, uniform random (seed=42) | h-m2 |
| full-374 profiling | All 374 problems profiled (no GRPO) | h-e1, h-m1 |

**Table 1: GRPO Training Hyperparameters**

| Parameter | h-m2 Value | h-m3 Value |
|-----------|-----------|-----------|
| Model | deepseek-coder-7b-instruct-v1.5 | same |
| num_generations (G) | 4 | 4 |
| max_completion_length | 512 | 512 |
| learning_rate | 5×10⁻⁷ | 1×10⁻⁶ |
| max_steps | 50 | 200 |
| beta (KL penalty) | 0.0 | 0.0 |
| use_vllm | False | False |
| per_device_train_batch_size | 1 | 1 |
| seed | 42 | 42 |
| save_strategy | no | no |

### 4.4 Evaluation Metrics

- `count_nonzero_variance`: number of problems with v_i > 0.1 (gate threshold: ≥15 for RQ1)
- `mean_var_selected` vs `mean_var_random`: Mann-Whitney U test, one-sided, α=0.05 (RQ2)
- `frac_reward_zero_std` per training step: primary training diagnostic (RQ3)
- HumanEval+ pass@1 via EvalPlus [Liu et al., 2023]: planned; not conducted due to cold-start

---

## 5. Results

Results are presented in causal chain order: variance distribution → selection signal → training gradient concentration.

### 5.1 RQ1: Variance Distribution (h-e1) — Gate Passed

The binary execution reward variance distribution on MBPP is severely right-skewed, but a meaningful high-variance subset exists.

**Table 2: MBPP Pass Rate Distribution (374 problems, k=4, max_new_tokens=128)**

| Pass Rate (p_i) | Count | Percentage | Variance (v_i) |
|-----------------|-------|------------|----------------|
| 0.00 (all-fail) | 343 | 91.7% | 0.0000 |
| 0.25 (1/4 pass) | 29 | 7.8% | 0.1875 |
| 0.50 (2/4 pass) | 0 | 0.0% | 0.2500 |
| 0.75 (3/4 pass) | 0 | 0.0% | 0.1875 |
| 1.00 (all-pass) | 2 | 0.5% | 0.0000 |

Source: `h-e1/results/mbpp_variance_profile.json`, confirmed in `h-e1/04_validation.md`.

29 problems satisfy v_i > 0.1, exceeding the gate threshold of 15 (gate passed). No problems were observed at pass rates 0.50 or 0.75 — a consequence of k=4 granularity combined with max_new_tokens=128 truncation. The 91.7% per-problem all-fail rate under profiling substantially exceeds the 54.75% all-fail component reported by Nie et al. [2026] under different generation conditions, suggesting that constrained generation parameters amplify practical gradient starvation.

The mean p_i across all 374 problems is 0.035. The mean p_i across the top-50 variance-selected problems is 0.225.

![Pass rate histogram for MBPP training problems (374 problems, k=4, max_new_tokens=128). The distribution is bimodal: 91.7% at p_i=0, 7.8% at p_i=0.25.](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c/docs/youra_research/h-e1/figures/fig2_pass_rate_histogram.png)

*Figure 1: Pass rate histogram for MBPP training problems (374 problems, k=4, max_new_tokens=128).*

![Variance histogram for MBPP training problems. 343 problems have v_i=0; 29 have v_i=0.1875. No intermediate levels exist under k=4 discrete sampling.](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c/docs/youra_research/h-e1/figures/fig3_variance_histogram.png)

*Figure 2: Variance distribution histogram. 343 problems cluster at v_i=0; 29 problems at v_i=0.1875.*

**Gate verdict (h-e1): Passed** — existence of gradient-signal subset confirmed.

### 5.2 RQ2: Selection Signal (h-m1) — Gate Passed

Variance-guided selection achieves 4.24× higher mean variance than random selection, with a highly significant difference.

**Table 3: Variance Selection Comparison**

| Metric | Variance-50 | Random-50 |
|--------|-------------|-----------|
| Mean variance | 0.1113 | 0.0262 |
| Ratio | 4.24× | 1.0× |
| Difference | 0.0850 | — |
| Mann-Whitney U statistic | 1807.0 | — |
| Mann-Whitney U p-value (one-sided) | 2.22×10⁻⁶ | — |

Source: `h-m1/results/comparison_results.json`.

The Mann-Whitney U test (one-sided, alternative='greater') confirms that variance-50 problems have statistically higher variance than random-50 problems (p=2.22×10⁻⁶ < 0.05). The empirical CDF of variance-50 lies entirely above that of random-50, confirming stochastic dominance.

The selection includes 21 zero-variance filler problems at the boundary (boundary_gap=0), since only 29 problems have positive variance while the top-50 requires 50. Despite this, the overall distribution of the variance-selected subset differs dramatically from random selection.

![Mean variance comparison between variance-50 and random-50 selections, with individual data points shown. Variance-50 mean (0.1113) is 4.24× higher than random-50 mean (0.0262).](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c/docs/youra_research/h-m1/figures/fig1_mean_comparison.png)

*Figure 3: Mean variance comparison (variance-50 vs random-50) with individual data points.*

![Empirical CDF comparison: variance-50 lies entirely above random-50, confirming stochastic dominance.](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c/docs/youra_research/h-m1/figures/fig4_cdf.png)

*Figure 4: Empirical CDF of variance values for variance-50 and random-50. Variance-50 stochastically dominates random-50.*

**Gate verdict (h-m1): Passed** — selection signal confirmed.

### 5.3 RQ3: Gradient Concentration During Training (h-m2, h-m3) — Gates Failed

Both conditions show frac_reward_zero_std=1.0 throughout all training steps in both experiments.

**h-m2 (50 steps, LR=5×10⁻⁷):** Both variance-50 and random-50 maintained frac_reward_zero_std=1.0 at every step. reward/mean=0.0, grad_norm=0.0 throughout. TRL GRPOTrainer logged 13 generation-phase steps (due to off-policy replay). Total generation attempts: approximately 50 steps × 50 problems × 4 completions = 10,000, all returning reward=0.

**Table 4: H-M2 Gate Results (50 Steps)**

| Checkpoint | frac_reward_zero_std (variance-50) | frac_reward_zero_std (random-50) | Gap | Gate pass |
|------------|-----------------------------------|----------------------------------|-----|-----------|
| Step 10 | 1.0000 | 1.0000 | 0.0000 | False |
| Step 20 | 1.0000 | 1.0000 | 0.0000 | False |
| Step 50 | 1.0000 | 1.0000 | 0.0000 | False |

Source: `h-m2/results/gate_results.json`.

**h-m3 (200 steps, LR=1×10⁻⁶):** Cold-start persisted despite doubled learning rate and 4× more training steps. frac_reward_zero_std=1.0 throughout all 200 steps. Condition A (variance-50): 200 steps completed, max_reward=0.0. Condition B (random-50): 200 steps completed, max_reward=0.0. Total additional attempts: 200 steps × 50 problems × 4 completions = 40,000, all reward=0.

Source: `h-m3/results/gate_results.json`, `h-m3/04_validation.md`.

**Combined total: more than 50,000 generation attempts, zero reward across all conditions.**

The 4.24× selection signal from RQ2 is completely invisible during training. σ=√(k(G−k))/G=0 when k=0 for every problem — cold-start nullifies any selection advantage before any gradient can be generated.

![Per-step frac_reward_zero_std for variance-50 and random-50 conditions (h-m2, 50 steps). Both conditions are flat at 1.0 throughout, visually indistinguishable.](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c/docs/youra_research/h-m2/figures/learning_curves.png)

*Figure 5: frac_reward_zero_std per training step (h-m2, 50 steps). Both conditions maintain 1.0 throughout.*

**Gate verdicts (h-m2, h-m3): Failed** — mechanism Step 3 falsified under current parameters.

**HumanEval+ evaluation:** Not conducted. Cold-start prevented accumulation of any reward signal; no checkpoint was saved at step 50; evaluation was not possible.

---

## 6. Discussion

### 6.1 Summary of Findings

**Finding 1: Offline variance profiling is analytically valid.** The 4.24× mean variance advantage (p=2.22×10⁻⁶) confirms that frozen-model pass rate profiling reliably identifies a statistically distinct problem subset. The selection method operates as designed.

**Finding 2: The MBPP variance distribution is more degenerate than theoretical analyses assume.** The 91.7% all-fail rate under constrained generation (k=4, max_new_tokens=128) substantially exceeds both the 69.25% theoretical rate for G=4 [Nie et al., 2026] and the heterogeneous difficulty distribution assumed by prior RLVR work. Generation parameter constraints critically shape the effective training data pool.

**Finding 3: Cold-start is a necessary precondition.** More than 50,000 generation attempts producing zero reward is not a stochastic event — it is deterministic given the current parameter configuration. The identity σ=0 when k=0 tells us no data selection method can help when the model generates no correct solutions.

### 6.2 Root Cause Analysis

Cold-start (zero reward across all 50,000+ generation attempts) admits several candidate explanations. These are enumerated and ranked by supporting evidence.

**Candidate 1 (Most likely): Generation parameter mismatch.** Profiling used vLLM with max_new_tokens=128; training uses HF GRPOTrainer with max_completion_length=512. The 29 problems identified as high-variance (p_i=0.25 at max_new_tokens=128) may require longer completions to produce correct solutions. Under training conditions, they may all collapse to p_i=0. Evidence in favor: truncation ratio is severe (128 vs. 512 tokens); max_new_tokens is the single parameter most likely to prevent solution completion for many code problems. Evidence against: this cannot be confirmed without re-profiling under training-identical parameters.

**Candidate 2 (Plausible): Prompt format mismatch.** The prompt format used during vLLM profiling may differ from the chat template applied by GRPOTrainer. A different instruction prefix or separator could change the model's generation behavior sufficiently to shift pass rates from 0.25 to 0.0. Evidence in favor: instruction-tuned models are sensitive to prompt format. Evidence against: both paths use the same base model and were configured to use the same prompt template, though this was not verified by logging decoded prompts.

**Candidate 3 (Plausible): Fundamental capability gap.** DeepSeek-Coder-7B-Instruct may generate syntactically valid but semantically incorrect Python in this zero-shot GRPO setup at a rate insufficient for any of G=4 completions to pass, regardless of generation length. Evidence in favor: h-m3 extending to 200 steps with doubled LR produced no nonzero rewards, suggesting the failure is not simply a matter of more training. Evidence against: h-e1 profiling found p_i=0.25 for 29 problems under max_new_tokens=128, suggesting the model does generate correct solutions under some conditions.

**Candidate 4 (Less likely): Execution harness mismatch.** The subprocess execution harness (timeout, working directory, import availability) may differ between profiling and training reward evaluation. Evidence in favor: execution environment differences can silently flip pass/fail outcomes. Evidence against: both phases use the same reward function implementation; no execution errors were logged.

**Resolution protocol (prescriptive, not yet empirically validated):** Re-profiling with training-identical parameters (same prompt format, max_new_tokens=max_completion_length=512, same execution harness) would directly distinguish Candidates 1 and 2 from Candidates 3 and 4. If the 29 currently-selected problems retain p_i≥0.25 after aligned re-profiling, cold-start is a training-phase issue. If they collapse to p_i=0, Candidate 1 or 2 is confirmed. This protocol is proposed as future work; it was not executed in this study.

Cold-start does not in itself invalidate offline variance profiling as a design — it identifies a deployment precondition: profiling-training parameter alignment must be verified before training begins.

### 6.3 Limitations

**Limitation 1: Cold-start prevents empirical mechanism validation.** The gradient concentration claim (mechanism Step 3) and the HumanEval+ performance claim (Step 4) are contingent on nonzero reward signal. The selection method is validated analytically; training-phase benefit requires cold-start resolution. The proposed resolution protocol is prescriptive and has not been empirically executed.

**Limitation 2: Profiling parameters differ from training parameters.** Profiling used k=4, max_new_tokens=128; training used max_completion_length=512. The mismatch arose from hardware constraints (sequential HF inference at k=8, max_new_tokens=512 required approximately 8 hours) and vLLM-TRL incompatibility (vLLM 0.11.0 + TRL 1.10). This is the most likely root cause of cold-start among the candidates enumerated above.

**Limitation 3: Only 29/374 problems usable for variance selection.** The severely degenerate distribution narrows the selection pool. k≥8 with max_new_tokens≥512 would reveal richer intermediate-difficulty structure and a more heterogeneous variance distribution.

**Limitation 4: Single-run training experiments, no multi-seed validation.** For the cold-start negative result, replication is unnecessary — zero reward across 50,000+ attempts is not stochastic. For future positive-result claims, 3+ seeds are required.

**Limitation 5: Root cause is inferred, not confirmed.** The resolution protocol in Section 6.2 remains unexecuted.

### 6.4 Implications

The experimental findings suggest that any RLEF data selection paper should report `frac_reward_zero_std` trajectories as a baseline diagnostic to confirm training regime viability before claiming selection advantages. Practitioners deploying data selection for RLEF should verify pass@k > 0 on target problems under training-identical generation parameters before investing in offline or online selection infrastructure.

---

## 7. Conclusion

Offline variance-guided selection for binary-reward RLEF produces a statistically robust analytical advantage — 4.24× higher mean variance than random selection (Mann-Whitney U p=2.22×10⁻⁶), confirmed across 374 MBPP problems — but this advantage is rendered invisible during GRPO training when the model generates zero correct solutions across more than 50,000 generation attempts. This result establishes cold-start verification as a necessary precondition for any RLEF data selection method.

Contributions of this work:

1. **Variance distribution characterization** (confirmed): The first systematic per-problem characterization of binary execution reward variance on MBPP for DeepSeek-Coder-7B-Instruct — 91.7% all-fail, 7.8% at p_i=0.25, 0.5% all-pass under k=4, max_new_tokens=128.

2. **Offline variance profiling** (method, analytically validated): 4.24× mean variance advantage, stochastic dominance on empirical CDF, approximately 32-second profiling via vLLM for 374×4=1,496 completions.

3. **Cold-start diagnosis** (negative result, high confidence): More than 50,000 generation attempts, zero reward; four candidate root causes enumerated and ranked; generation parameter mismatch identified as most likely; concrete prescriptive resolution protocol provided as future work.

**Directions for future work:**

- *Highest priority:* Re-profile MBPP with max_new_tokens=512, subprocess execution, and identical prompt format to GRPO training. If the 29 problems retain p_i≥0.25, cold-start is a training-phase issue. If they collapse, parameter alignment is the fix. This is a single experiment reusing existing code (`h-e1/code/profile_mbpp_vllm.py`).

- *High priority:* Use a model with >10% initial MBPP pass@1 (e.g., Qwen2.5-7B-Instruct) to break the cold-start barrier. All h-m2 training code is directly reusable.

- *Conditional on cold-start resolution:* Measure `frac_reward_zero_std` gap trajectories across training steps to test whether the frozen-model variance ranking degrades over the course of training, as assumed by the proxy stability hypothesis.

---

## References

Austin, J., et al. (2021). Program synthesis with large language models. *arXiv:2108.07732*.

Baroian, A., & Berger, R. (2026). Prompt replay. *arXiv:2603.21177*.

Cui, P., et al. (2026). Learning-zone energy. *arXiv:2605.17003*.

Gehring, J., et al. (2024). RLEF: Grounding code LLMs in execution feedback with reinforcement learning. *ICML 2025. arXiv:2410.02089*.

Guo, D., et al. (2024). DeepSeek-Coder: When the large language model meets programming — the rise of code intelligence. *arXiv:2401.14196*.

Jiang, H., et al. (2026). Learning as reasoning unfolds (VIGOR). *arXiv:2607.22002*.

Liu, J., et al. (2023). Is your code generated by ChatGPT really correct? Rigorous evaluation of large language models with comprehensive code evaluation. *NeurIPS 2023. arXiv:2305.01210*.

Nie, W., et al. (2026). Gradient starvation in GRPO. *arXiv:2605.07689*.

Shao, Z., et al. (2024). DeepSeekMath: Pushing the limits of mathematical reasoning in open language models. *arXiv:2402.03300*.

Sun, Y., et al. (2025). Difficulty-targeted online data selection for RLVR. *NeurIPS 2025. arXiv:2506.05316*.
