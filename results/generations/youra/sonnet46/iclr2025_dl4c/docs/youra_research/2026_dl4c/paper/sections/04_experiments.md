# 5. Experiments

## 5.1 Research Questions

Our experimental design is organized around four concrete research questions that map directly to the claims in the Introduction.

**RQ1 (Existence):** Does prescreening APPS introductory problems with a Qwen2.5-Coder-7B model under SFT initialization yield ≥50 qualifying problems satisfying S_term ∈ [0.3, 0.55]? This question tests the basic feasibility of the prescreening-gated approach: if the tractability window is empty, no subsequent reward comparison is meaningful.

**RQ2 (Variance Gate):** In groups that pass the prescreening filter, does R_ratio produce statistically higher reward variance than R_binary? Formally, does E[Var(r_ratio)] / E[Var(r_binary)] ≥ 1.5× for problems with q ∈ [0.3, 0.55] and group size G=8? This question operationalizes our core Binomial-variance argument (Section 3.2).

**RQ3 (Advantage Diversity):** Does R_ratio produce more distinct advantage levels per group under GRPO than R_binary? Our prediction (h-m1) is that R_ratio yields ≥5 distinct advantage values per group in the prescreened subset, compared to the near-binary ±1 distribution under R_binary. Greater advantage diversity is the mechanism by which higher gradient SNR is achieved.

**RQ4 (ZRF Escape):** Does R_ratio produce earlier escape from the Zero Reward Fraction plateau than R_binary? Our prediction (h-m4) is that ZRF_ratio(t*) < 0.8 × ZRF_binary(t*) for t* in the first 25% of training, with log-rank p < 0.05 on ZRF survival curves.

## 5.2 Dataset

We use the **APPS benchmark** (Automated Programming Progress Standard) introduced by Hendrycks et al. [2021], a collection of programming problems scraped from competitive programming platforms. We restrict attention to the **introductory difficulty tier** (difficulty = 0) to target problems appropriate for a 7B model after SFT initialization.

Within introductory problems, we apply a **T≥3 filter** (minimum 3 test cases per problem) to ensure that the fractional pass rate S_term = (number of test cases passed) / T is a meaningful signal with sufficient resolution. Problems with T < 3 would produce an excessively coarse S_term grid (e.g., only {0, 0.5, 1.0} for T=2), potentially placing problems outside the [0.3, 0.55] window that actually belong in it. After filtering, **1,923 introductory problems** are available in the APPS dataset. We process a random sample of **300 problems** (seed=42) for prescreening, which is sufficient to estimate the prevalence of qualifying problems if the base rate is ≥5%.

The prescreening design is motivated by the observation that the tractability window S_term ∈ [0.3, 0.55] represents problems that are neither trivially solvable (which would produce degenerate reward distributions under both R_ratio and R_binary) nor completely intractable (which would produce all-zero rewards, preventing any learning signal). This window is where the differential expressiveness of R_ratio versus R_binary is largest.

## 5.3 Baselines

**R_binary (primary baseline):** The standard GRPO reward used in prior code generation work assigns +1 if all test cases pass and 0 otherwise. This is the universal baseline in RL-for-code research (DeepSeek-R1 [Guo et al., 2025], Afterburner [Liao et al., 2025]) and represents the current default. All comparisons in RQ2–RQ4 are measured relative to R_binary.

**Afterburner SFT initialization [ArXiv 2505.23387]:** We treat the Afterburner pipeline as a reference implementation for the SFT prerequisite. Afterburner demonstrates that GRPO on code generation requires an SFT-initialized model to produce nonzero rewards at training outset. We use this finding both as motivation for our SFT prerequisite and as a consistency check: our h-e1 results should replicate the Afterburner finding that base models are incompatible with GRPO-for-code.

## 5.4 Implementation Details

**Model:** Qwen2.5-Coder-7B-Instruct [Hui et al., 2024] serves as the base model for prescreening. The -Instruct variant is used because it produces structured code outputs. An SFT checkpoint trained on APPS introductory solutions is the required prerequisite for Stage 2 (GRPO training); this checkpoint was absent at the time of the h-e1 evaluation.

**Training framework:** We use HuggingFace TRL's GRPOTrainer with the reward function replaced by R_ratio or R_binary as appropriate. No modifications to the GRPO update rule are required; the reward signal is the only difference between conditions.

**Hardware:** All experiments run on a single **NVIDIA H100 NVL GPU** (80GB HBM3). Prescreening of 300 problems with k=8 rollouts each completed in approximately 42 minutes.

**Sampling parameters:**
- Rollouts per problem: k = 8
- Sampling temperature: T = 0.8
- Maximum new tokens: 1,024
- Random seed: 42 (prescreening); seeds {42, 43, 44} planned for GRPO training runs (Stage 2)

**Execution sandbox:** Solutions are executed in an isolated subprocess environment with a 5-second timeout per test case. The sandbox correctly handles import errors, runtime exceptions, and timeout failures — all of which contribute to partial credit under R_ratio.

**Code implementation:** The prescreening pipeline consists of six modules:
- `prescreening.py` (371 lines): main prescreening loop and filter logic
- `evaluate.py`: per-problem evaluation harness
- `reward_fn.py`: R_ratio and R_binary implementations
- `data_loader.py`: APPS dataset loading with difficulty and T≥3 filters
- `execution_sandbox.py`: isolated subprocess execution
- `visualization.py`: gate metric and advantage distribution plots

## 5.5 Evaluation Metrics

We evaluate the prescreening stage (h-e1) using three gate metrics with pre-registered thresholds:

**fraction_k_pass_ge1:** Fraction of processed problems where at least one of k=8 rollouts passes all test cases. Threshold: ≥ 0.10. This measures whether the model has any non-trivial solve rate on the problem set.

**pct_groups_above_1.5x:** Among qualifying prescreened groups (S_term ∈ [0.3, 0.55]), the fraction where Var(r_ratio) / Var(r_binary) ≥ 1.5. Threshold: ≥ 0.80. This directly tests RQ2 on the prescreened subset.

**n_prescreened:** Number of problems with S_term ∈ [0.3, 0.55] in the processed sample. Threshold: ≥ 50. This tests RQ1.

For Stage 2 GRPO training experiments (h-m1 through h-m4, projected pending SFT), we will additionally track:

**Distinct advantage levels per group:** Number of unique advantage values A_i = r_i − mean(r) across k=8 rollouts, averaged over prescreened groups. Predicted: ≥5 under R_ratio vs ~2 under R_binary (h-m1).

**Gradient SNR:** ‖E[A_i · ∇θ log π(o_i)]‖ / std(A_i · ∇θ log π(o_i)), computed per optimization step. Predicted: R_ratio SNR ≥ 1.5× R_binary SNR in first 25% of training (h-m3).

**Zero Reward Fraction (ZRF):** Fraction of rollouts receiving zero reward per training step. ZRF survival curves will be compared via log-rank test (h-m4).

## 5.6 Experimental Pipeline

The full evaluation proceeds in two sequential stages:

**Stage 1 — Prescreening (h-e1, completed):** Run k=8 rollouts per problem on 300 APPS introductory problems. Compute S_term = (tests passed) / T for each problem. Apply the filter S_term ∈ [0.3, 0.55] to identify qualifying training groups. Evaluate gate metrics against pre-registered thresholds.

**Stage 2 — GRPO Training (h-m1 through h-m4, projected pending SFT):** Using the qualifying prescreened groups as the training corpus, run two parallel GRPO training runs — one with R_ratio and one with R_binary — for 1,000 gradient steps. Log ZRF curves, advantage distributions, and gradient SNR at 50-step intervals. Compare via log-rank test (ZRF) and paired t-test (SNR).

Stage 2 is contingent on Stage 1 producing ≥50 qualifying problems (the n_prescreened gate). The h-e1 evaluation revealed that the current base model does not satisfy this prerequisite; see Section 6 for results and Section 7 for discussion of the path forward.
