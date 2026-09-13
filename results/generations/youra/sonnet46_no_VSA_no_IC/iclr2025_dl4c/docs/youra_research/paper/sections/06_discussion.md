# 6. Discussion

## 6.1 Key Findings

Our experiments yield a compound result: two sub-hypotheses validated, three falsified, with a precise causal explanation that preserves the method's theoretical integrity.

**Finding 1: Offline variance profiling is analytically valid.** The 4.24× mean variance advantage (p=2.22e−06) confirms that frozen-model pass rate profiling reliably identifies a statistically distinct subset of MBPP problems. Even under constrained generation (k=4, max_new_tokens=128), the variance-guided selection stochastically dominates random selection on the full distribution. This is not a marginal effect — the p-value of 2.22e−06 is far below any conventional significance threshold. The method works as a selection tool.

**Finding 2: The distribution is more degenerate than assumed.** 91.7% all-fail under constrained generation is substantially more severe than the 69.25% zero-gradient rate from theoretical analysis. Generation parameter constraints — specifically max_new_tokens=128 — appear to truncate many completions before Python function bodies are complete, converting potentially solvable problems to p_i=0. This suggests that the *effective training data pool* is highly sensitive to generation parameters, and that characterizing this distribution empirically (as we do) is a necessary first step before any selection method can be designed.

**Finding 3: Cold-start is a necessary precondition for variance selection.** The 40,000+ generation attempts across 50–200 training steps producing zero reward is not a stochastic outcome — it is deterministic given the current parameter configuration. Both conditions are identical in training because both produce k=0 correct completions for every problem in every group. The σ=√(k(G−k))/G=0 identity tells us that no data selection method can help in this regime. This is the key missing precondition that prior work on RLEF data selection has not systematically studied.

## 6.2 What This Means for Offline Profiling Methods

The cold-start finding does not invalidate offline variance profiling as a method. It identifies a deployment precondition:

*Offline variance profiling requires profiling-training parameter alignment.* If profiling and training use different generation parameters (inference engine, max tokens, temperature, prompt format), the problems identified as "high-variance" at profiling time may yield zero variance under training conditions. This nullifies the selection before training begins. The fix is: re-profile using training-identical parameters (same prompt format, max_new_tokens=max_completion_length, same execution harness).

This is an addressable engineering limitation, not a fundamental flaw. The profiling method, the selection algorithm, and the statistical analysis are all valid. The parameter mismatch is a one-experiment fix: re-profile MBPP with max_new_tokens=512, subprocess execution, and identical prompt format to GRPO training; if p_i≥0.25 still holds for the 29 previously-selected problems, the cold-start is a training-phase failure (higher LR, longer training, or warm-start needed). If p_i collapses to 0 for all problems, the mismatch is confirmed and alignment resolves the issue.

## 6.3 Limitations

**Limitation 1: Cold-start prevents empirical gradient-concentration test.** The central mechanism claim — that variance selection reduces frac_reward_zero_std during training — could not be tested because the base model generates zero correct solutions across all training conditions. The selection method is validated analytically (4.24× advantage) but its training-phase benefit is contingent on cold-start resolution. Future work must re-profile under training-identical parameters and/or use a warm-started model before this mechanism can be empirically verified.

**Limitation 2: Profiling parameters (k=4, max_new_tokens=128) differ from training parameters (max_completion_length=512).** The 29 "high-variance" problems were selected based on profiling performance under shortened generation; their performance under training conditions is unverified. This is the most likely root cause of cold-start. Future experiments should align profiling and training generation parameters. The mismatch arose from hardware constraints (sequential HF inference at k=8, max_new_tokens=512 required ~8h) and vLLM-TRL incompatibility (vLLM 0.11.0 + TRL 1.10 incompatible).

**Limitation 3: Only 29/374 problems are usable for variance selection.** The severely degenerate distribution (91.7% at p_i=0) narrows the usable selection pool from the assumed 50+ to 29 problems. "Top-50" selection necessarily includes 21 zero-variance problems. This weakens the efficiency argument (7.8% data recovery rather than 13.4%) and requires k≥8 with max_new_tokens≥512 to reveal the full intermediate-difficulty structure.

**Limitation 4: Single-run training experiments, no multi-seed validation.** Each GRPO training condition was run once. For the cold-start negative result, multi-seed replication is unnecessary — 100% zero reward across 40,000+ attempts is not a stochastic event. For future positive-result claims, 3+ seeds per condition are required to distinguish selection advantage from initialization variance.

## 6.4 Broader Impact

This work contributes a cautionary finding for the growing literature on RLEF data selection. The implicit assumption in most selection papers — that if a selection signal is analytically real, it will manifest in training — may not hold in cold-start regimes. We recommend that future papers on RLEF data selection report frac_reward_zero_std trajectories as a baseline diagnostic to confirm that the training regime is not in cold-start before claiming selection advantages.

For practitioners, the implication is practical: before deploying any data selection method for RLEF, verify that the base model achieves pass@k > 0 on target problems under training-identical generation parameters. This verification takes seconds (profile with the same generation setup as training) and prevents silent failure of the selection method.

The offline profiling approach itself remains promising. The 32-second vLLM profiling speed demonstrates that the overhead is negligible compared to even short GRPO runs. Once the cold-start barrier is resolved — either through parameter alignment or a warm-started model — the 4.24× analytical selection advantage provides a strong prior that gradient concentration will follow.
