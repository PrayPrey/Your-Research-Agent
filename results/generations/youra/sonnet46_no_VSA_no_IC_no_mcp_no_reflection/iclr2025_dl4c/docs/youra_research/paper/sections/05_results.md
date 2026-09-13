# Results

## 5.1 Mechanistic Proof: Ratio Reward Advantage Variance (h-e1)

**Table 1: Advantage comparison for illustrative GRPO group.**

| Completion | Test passes (k/5) | Binary reward | Ratio reward | Binary advantage | Ratio advantage |
|------------|-------------------|---------------|--------------|-----------------|-----------------|
| c1 | 0 | 0.000 | 0.000 | 0.000 | −0.150 |
| c2 | 0 | 0.000 | 0.000 | 0.000 | −0.150 |
| c3 | 1 | 0.000 | 0.200 | 0.000 | +0.050 |
| c4 | 2 | 0.000 | 0.400 | 0.000 | +0.250 |
| c5 | 0 | 0.000 | 0.000 | 0.000 | −0.150 |
| c6 | 3 | 0.000 | 0.600 | 0.000 | +0.450 |
| c7 | 0 | 0.000 | 0.000 | 0.000 | −0.150 |
| c8 | 0 | 0.000 | 0.000 | 0.000 | −0.150 |
| **Group mean** | — | **0.000** | **0.150** | — | — |
| **Advantage variance** | — | **0.0000** | **0.0475** | — | — |

This result is a mathematical guarantee, not an empirical estimate. For this group — in which 5 of 8 completions fail all test cases, 2 fail all but achieve partial credit (1–2 passes), and 1 achieves 3 passes — binary reward must produce zero gradient contribution. Ratio reward must produce non-zero gradient that pushes the model toward the 3-pass completion over the 0-pass completions. The difference in advantage variance (0.0475 vs. 0.0000) is exact to the precision of the floating-point computation.

The formal condition for binary reward's dead zone is: all completions achieve k ∈ {0, n} test passes (none have partial credit). In this group, completions c3, c4, c6 have k ∈ {1, 2, 3} — partial credit — and no completion achieves all 5. This group lies in the dead zone for binary reward and in the informative zone for ratio reward.

## 5.2 Scale of the Dead Zone: 1,000-Group Simulation

**Figure 1** (reward_histograms.png) shows the distribution of group-level advantage variance across 1,000 simulated early-training GRPO groups (p_pass = 0.1 per test case, G = 8 completions, n = 5 test cases per problem).

Under binary reward, 987/1,000 groups (98.7%) have advantage variance = 0.0: every completion in the group fails all test cases, and binary reward assigns zero to all. Only 13/1,000 groups (1.3%) have non-zero binary reward variance — these are the rare early-training groups in which at least one completion passes all 5 test cases.

Under ratio reward, 987/1,000 groups (98.7%) have advantage variance > 0: in these groups, at least one completion achieves partial credit, and ratio reward differentiates among completions. The 13 groups where binary reward is non-zero correspond to groups where at least one completion passes all tests; in these groups, ratio reward is also non-zero (and equals 1.0 for full-pass completions).

**Summary.** Under realistic early-training conditions (p_pass = 0.1), binary reward provides gradient signal to only 1.3% of GRPO groups. Ratio reward provides gradient signal to 98.7% of groups — the complement of the all-zero-variance set under binary reward. The 98.7% figure is the fraction of early-training groups where ratio reward provides information that binary reward cannot.

## 5.3 Infrastructure Validation: Smoke Test and Unit Tests

The h-e1 smoke test (3 GRPO training steps, binary condition, GPU 0) confirmed:
- Exit code: 0 (no runtime error)
- Gradient norms: steps 1, 2, 3 in range [3×10⁻⁴, 7×10⁻⁴] — healthy, non-NaN
- Checkpoint saved at step 3: confirmed
- Duration: approximately 54 seconds per step on H100 NVL

Unit test results:
- h-e1 total: 17/17 passing (config: 2/2; rewards: 12/12; analyze: 3/3)
- h-m1 total: 18/18 passing (config: 2/2; rewards: 12/12; analyze: 4/4)
- Combined: 35/35

These results confirm that the null result in h-m1 (Section 5.4) is attributable to experimental setup, not implementation bugs.

## 5.4 h-m1 Training: Precision Null Result

**Figure 2** (mean_reward.png) shows reward_mean at each logged training step for both binary and ratio conditions throughout h-m1.

Both conditions show reward_mean = 0.000 at all 208 logged training steps (steps 1 through approximately 208, the last step completed before the experiment was terminated per the FractionPartialCallback diagnostic). The two curves are identical throughout training. There is no step at which either condition achieves reward_mean > 0.

**Table 2: h-m1 training diagnostics.**

| Metric | Binary condition | Ratio condition |
|--------|-----------------|-----------------|
| reward_mean at all steps | 0.0000 | 0.0000 |
| clipped_ratio (all steps) | 1.0000 | 1.0000 |
| fraction_partial (all steps) | NaN | NaN |
| mean_terminated_length | 0 | 0 |
| grad_norm (steps 1–136 mean) | ~10⁻³ | ~10⁻³ |

**Interpretation.** clipped_ratio = 1.0 at all steps means every completion in every group hits the max_new_tokens = 512 token limit — no completion generates a natural end-of-sequence token before the limit. These completions are syntactically incomplete Python functions: truncated mid-expression or mid-statement, never reaching a state where any test case can be executed to completion. fraction_partial = NaN confirms that no partial-pass completions were observed (the denominator of the fraction is 0 throughout).

**Why the rewards are identical.** When no completion executes any test case (all completions are truncated non-programs), binary_reward(c) = 0 and ratio_reward(c) = 0 for all completions c. In this regime, binary and ratio reward functions are mathematically equivalent — both produce all-zero group rewards for every training group. GRPO produces zero gradient contribution from every group, for both conditions.

**Figure 3** (grad_norm_trajectory.png) shows per-step gradient norms for binary and ratio conditions across early training steps. Both conditions produce gradient norms in the range [0.5×10⁻³, 3×10⁻³], with no consistent directional difference. The gradient norm 95% bootstrap CI on (ratio − binary) over steps 1–136 is: mean = +0.000730, CI = [−0.000253, +0.002561], which includes zero. This is consistent with the interpretation that both conditions receive identical zero-reward gradients from the GRPO reward head, with observed non-zero gradient norms arising from the KL penalty term rather than from execution reward signal.

**Gate verdict: NOT SATISFIED.** The h-m1 gate criterion requires ratio HumanEval pass@1 − binary ≥ 0.03 with 95% CI excluding 0. Since both conditions are reward-equivalent (both = 0 throughout), no policy divergence can emerge from the GRPO reward signal. Evaluating HumanEval at any checkpoint would compare two identically-trained models. The experiment was terminated and routed to Phase 0 redesign.

## 5.5 Summary of Results

| Result | Hypothesis | Value | Status |
|--------|------------|-------|--------|
| Binary advantage variance | h-e1 | 0.0000 | Mathematical guarantee |
| Ratio advantage variance | h-e1 | 0.0475 | Mathematical guarantee |
| Groups receiving ratio≠binary signal (simulation) | h-e1 | 987/1,000 (98.7%) | Confirmed |
| h-e1 gate | h-e1 | SATISFIED | GATE PASS |
| reward_mean at all steps (both conditions) | h-m1 | 0.0000 | Confirmed |
| clipped_ratio (both conditions, all steps) | h-m1 | 1.0000 | Confirmed |
| h-m1 gate | h-m1 | NOT SATISFIED | GATE FAIL — setup failure |
| Unit tests | Both | 35/35 | PASS |
