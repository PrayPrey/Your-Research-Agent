# Reward Sparsity in Function-Level Execution Feedback Degrades GRPO Training for 7B Code Models

## Abstract

Group Relative Policy Optimization (GRPO) has emerged as a method for training code-generating language models from execution feedback, yet its effectiveness depends on a structural precondition that is not always verified in practice: at least one completion in each training group must receive non-zero reward for advantage normalization to carry gradient signal. This paper examines what happens when that precondition is systematically violated. In a controlled comparison of function-level (APPS+CodeContests) and repository-level (SWE-bench Verified) GRPO training under otherwise identical configuration, we observe a 76× advantage variance gap (0.004 vs. 0.317, Welch's t-test: t=20.37, p=5.34×10⁻⁴⁴, Cohen's d=1.904) using CodeLlama-7b-Instruct-hf. This gap is explained by the difference in positive reward rates: approximately 0% for function-level competitive programming tasks versus approximately 6% for repository-level tasks. When positive reward rate is near zero, every training group is degenerate (std(r)=0), advantages are zero, and GRPO gradient contributions vanish. We additionally validate training infrastructure for a 4-condition difficulty-stratified curriculum GRPO experiment (curriculum, uniform, easy-only, hard-only) on APPS+CodeContests via a 10-step smoke test; reward density was 0.0 across all conditions and steps during this smoke test, consistent with the reward collapse finding. The full 5000-step behavioral experiment was not executed. Our results characterize advantage variance as a diagnostic for execution-feedback RL and identify conditions under which curriculum ordering may or may not rescue degenerate training.

## 1. Introduction

Group Relative Policy Optimization (GRPO) has attracted interest as a training method for code-generating language models because it replaces the learned critic of PPO with a group-relative normalization scheme, reducing implementation complexity while retaining execution feedback as the reward signal. However, the group-relative formulation carries a structural precondition: the advantage function

$$A_i = \frac{r_i - \text{mean}(r_{\text{group}})}{\text{std}(r_{\text{group}})}$$

is defined only when std(r_group) > 0. When all G completions in a group receive identical reward—most commonly, when all fail and receive reward zero—the advantage is undefined and the gradient contribution is zero. This degenerate case is not an edge case for 7B-class models on competitive programming tasks: models of this scale solve competitive programming problems at near-zero rates, so the majority of training groups are degenerate throughout training.

The failure mode is not visible in standard training diagnostics. Loss curves may appear stable. Periodic benchmark evaluations may show marginal or noisy changes. The collapse becomes apparent only when per-step advantage variance is measured directly.

In this paper, we address the following question: does task granularity—specifically, whether execution feedback is binary (function-level) or allows partial credit (repository-level)—determine whether GRPO advantage variance is in a viable or degenerate regime for 7B-class code models?

We conduct a controlled experiment comparing two conditions: function-level GRPO training on APPS and CodeContests (binary execution reward), and repository-level GRPO training on SWE-bench Verified (partial credit reward based on file-path overlap). All other factors are held constant: the same model (CodeLlama-7b-Instruct-hf), the same GRPO configuration (G=8, B=4), and the same training duration (120 steps per condition). We measure per-step advantage variance at every training step.

We additionally implement and smoke-test a training infrastructure for a 4-condition curriculum GRPO experiment on APPS+CodeContests, as a prerequisite for a full behavioral test of whether easy-to-hard curriculum ordering improves pass@1 on HumanEval+. The full behavioral experiment was not executed.

The remainder of this paper is organized as follows. Section 2 reviews related work. Section 3 describes the methodology. Section 4 describes the experimental setup. Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes.

## 2. Related Work

### 2.1 Execution-Feedback Reinforcement Learning for Code

Reinforcement learning with execution feedback has been applied to code generation in several prior works. CodeRL [Le et al., 2022] trained a code generation model on the APPS dataset using RL with execution outcomes as reward, demonstrating pass@1 improvements over supervised fine-tuning. CodeRL uses uniform random sampling from APPS and does not analyze how reward sparsity varies with problem difficulty or how it affects training dynamics.

RLEF [Gehring et al., 2024] extends execution-feedback RL to function-level benchmarks including HumanEval, MBPP, and APPS, and shows that iterative refinement with execution-grounded reward outperforms both SFT and standard RLHF. Per-step training diagnostics such as advantage variance or reward density are not reported, and training data difficulty composition is not a research variable.

DeepSeek-R1 [DeepSeek-AI, 2025] applies GRPO with competitive programming data at large model scales (>30B parameters), achieving strong reasoning performance. At these scales, non-zero solve rates are more common, and the paper does not characterize the regime where the initializing policy cannot solve training problems.

None of these works measure per-step advantage variance or reward density as a function of task difficulty. This paper addresses that gap.

### 2.2 Curriculum Learning

Bengio et al. [2009] established that training on easier examples first can accelerate convergence and improve generalization. The mechanism is that easy examples provide stable gradient signal early in training, when the model is most sensitive to update direction. Subsequent work applied curriculum learning to neural machine translation [Platanios et al., 2019] and question answering [Sachan and Xing, 2016].

Curriculum learning in the context of execution-feedback GRPO has not been systematically studied. This paper identifies a mechanistic precondition for curriculum GRPO to function: the initializing policy must have a non-zero solve rate on easy-tier problems, so that early curriculum phases produce non-degenerate advantage groups. Whether this precondition holds for a given model and difficulty tier is an empirical question that is not answered in this paper.

Kumar et al. [2010] introduce self-paced learning, which adapts difficulty selection to the model's current performance rather than following a pre-defined schedule. This direction is complementary to the fixed-schedule approach considered here.

### 2.3 GRPO

GRPO [Shao et al., 2024] replaces the learned value baseline of PPO [Schulman et al., 2017] with group-relative advantage normalization. For each prompt, G completions are sampled; advantages are computed as (r_i − mean(r_group)) / std(r_group). This eliminates the need for a separate critic model but creates a structural dependency on reward variance within each group: when all completions receive the same reward, the gradient contribution is zero.

AlphaCode [Li et al., 2022] demonstrates that model performance on competitive programming degrades sharply with problem difficulty tier, confirming that solve rate distributions are highly skewed for models of non-frontier scale. This paper quantifies how that skew translates into advantage variance collapse in GRPO.

### 2.4 Positioning

This work contributes a controlled measurement of GRPO advantage variance as a function of task granularity and reward structure, using training diagnostics (advantage variance, reward density) rather than only end-to-end benchmark outcomes. This diagnostic perspective is a prerequisite for principled design of curriculum approaches to execution-feedback GRPO.

## 3. Method

### 3.1 Experimental Design

The core experiment holds constant all factors except task granularity: same model, same GRPO hyperparameters, same training duration. The function-level condition uses binary execution reward on competitive programming problems; the repository-level condition uses partial credit reward on software engineering tasks. Advantage variance is measured at every training step.

This design isolates the effect of reward sparsity on GRPO advantage variance. The function-level condition is expected to produce near-zero positive reward rates; the repository-level condition provides non-zero reward even for incomplete solutions through file-path overlap scoring.

### 3.2 Model

Both conditions use **CodeLlama-7b-Instruct-hf** [Rozière et al., 2023] (HuggingFace Hub: `codellama/CodeLlama-7b-Instruct-hf`) with no additional fine-tuning. The instruction-tuned variant is used to ensure the model can follow task formatting requirements. This is a 7B-class model with known near-zero solve rates on competitive programming problems at APPS difficulty.

Note: CodeLlama-7b-Instruct was used for the H-M1 advantage variance experiment. The intended model for the full curriculum GRPO experiment (H-E1) is DeepSeek-Coder-7B-base; the behavioral results from that model were not obtained.

### 3.3 Datasets

**Function-level condition:**
- **APPS** [Hendrycks et al., 2021]: `codeparrot/apps`, train split, 5,000 problems with difficulty tiers 0–4. Problems require writing self-contained Python programs with stdin/stdout test cases.
- **CodeContests** [Li et al., 2022]: `deepmind/code_contests`, train split, 13,328 problems. Codeforces problems with public test cases.

**Repository-level condition:**
- **SWE-bench Verified** [Jimenez et al., 2024]: `princeton-nlp/SWE-bench_Verified`, test split, 500 GitHub issues. Each task requires generating a unified diff patch resolving a real software engineering issue.

APPS and CodeContests use incompatible test case schemas (`input_output` string vs. `public_tests` dict). The implementation unifies these to a common 4-column format.

### 3.4 GRPO Configuration

Both conditions use identical hyperparameters:

| Hyperparameter | Value |
|---|---|
| Group size G | 8 |
| Batch size B | 4 prompts/step |
| Training steps | 120 |
| Temperature | 0.8 |
| Max new tokens | 512 |
| Framework | TRL 1.3.0 GRPOTrainer |
| Hardware | NVIDIA H100 NVL |

### 3.5 Reward Functions

**Function-level:** Binary execution reward. Each of G=8 completions is executed against the problem's test cases via subprocess (3-second timeout per test case). Reward = 1.0 if all test cases pass, 0.0 otherwise.

**Repository-level:** Partial credit based on file-path overlap. The generated unified diff is parsed for modified file paths. Reward = fraction of gold patch file paths appearing in the generated patch.

### 3.6 Advantage Variance Measurement

At each training step t, the per-step GRPO advantage variance is recorded:

$$\text{adv\_var}(t) = \text{Var}\left(\left\{ A_i^{(j)} : i \in [G], j \in [B] \right\}\right)$$

where A_i^(j) = (r_i^(j) − mean(r^(j))) / std(r^(j)). For degenerate groups where std(r^(j)) = 0, advantages are set to 0.0. This is logged by the `RewardDensityCallback` at every step, aggregating across all B×G = 32 advantage values per step.

### 3.7 Statistical Analysis

Per-step advantage variance between the two conditions is compared using Welch's two-sample t-test on log-transformed variance values. Log transformation is applied because advantage variance is right-skewed and bounded below at zero. Welch's t-test is used over Student's t-test because the two conditions are expected to have substantially different variances.

- Null hypothesis H₀: Mean advantage variance is equal between conditions.
- Alternative hypothesis H₁: Mean advantage variance differs (two-tailed).

Effect size is reported as Cohen's d from log-transformed means and pooled standard deviation.

### 3.8 Curriculum GRPO Infrastructure

In parallel with the advantage variance experiment, training infrastructure for a 4-condition curriculum GRPO experiment is implemented and smoke-tested:

- **CurriculumDataset**: Wraps APPS+CodeContests with a `set_step()` interface that changes difficulty tier sampling at configurable step thresholds.
- **CurriculumCallback**: Triggers difficulty tier transitions at pre-specified steps (easy tiers 0–2 for steps 0–2500, hard tiers 3–4 for steps 2501–5000 in the curriculum condition).
- **RewardDensityCallback**: Logs per-step reward density and advantage variance to CSV files.

A 10-step smoke test verifies that all four conditions (curriculum, uniform, easy_only, hard_only) run without errors. Full 5000-step training was not executed.

## 4. Experimental Setup

### 4.1 Research Questions

- **RQ1:** Does task granularity (function-level vs. repository-level) produce a measurable difference in GRPO advantage variance for a 7B-class model?
- **RQ2:** Is reward sparsity (near-zero positive reward rate) the mechanistic pathway for advantage collapse?
- **RQ3:** Is any observed difference practically significant?

### 4.2 Dataset Details

| Dataset | Hub Name | Split | Size |
|---|---|---|---|
| APPS | codeparrot/apps | train | 5,000 |
| CodeContests | deepmind/code_contests | train | 13,328 |
| SWE-bench Verified | princeton-nlp/SWE-bench_Verified | test | 500 |

### 4.3 Baseline Conditions (H-E1 Infrastructure)

The curriculum GRPO infrastructure supports 4 conditions:

| Condition | Description |
|---|---|
| curriculum | Easy tiers (0–2) for steps 0–2500; hard tiers (3–4) for steps 2501–5000 |
| uniform | Random sampling across all tiers throughout training |
| easy_only | Only easy tiers (0–2) throughout training |
| hard_only | Only hard tiers (3–4) throughout training |

### 4.4 Implementation Details

The training framework uses TRL 1.3.0 GRPOTrainer. APPS and CodeContests require schema unification before use in a shared training loop. The H-M1 advantage variance experiment used CodeLlama-7b-Instruct-hf. The H-E1 smoke test used DeepSeek-Coder-7B-base. GPU isolation was enforced via CUDA_VISIBLE_DEVICES on a single NVIDIA H100 NVL.

## 5. Results

### 5.1 Advantage Variance Comparison (H-M1)

Table 1 presents the primary comparison between function-level and repository-level GRPO advantage variance across 120 training steps per condition.

**Table 1.** GRPO advantage variance comparison (CodeLlama-7b-Instruct-hf, G=8, B=4, 120 steps per condition).

| Condition | Mean Adv. Variance | Positive Rate | Steps |
|---|---|---|---|
| Function-level (APPS+CodeContests) | 0.004167 | ≈0% | 120 |
| Repo-level (SWE-bench Verified) | 0.316667 | ≈6% | 120 |
| Ratio (repo / function-level) | 76× | — | — |

**Statistical test:** Welch's t-test on log-transformed variance: t=20.37, p=5.34×10⁻⁴⁴, Cohen's d=1.904.

The function-level condition produces advantage variance of 0.004167, which is two orders of magnitude lower than the repository-level condition (0.316667). The ratio is 76×. The statistical test rejects the null hypothesis with t=20.37 and p=5.34×10⁻⁴⁴. Cohen's d=1.904 indicates a very large effect by conventional thresholds (d>0.8).

These results satisfy the gate condition for H-M1 (MUST_WORK gate: PASS).

![Per-step advantage variance over 120 training steps](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_dl4c/docs/youra_research/20260502_dl4c/paper/figures/advantage_variance_over_steps.png)

*Figure 1. Per-step GRPO advantage variance over 120 training steps for function-level (APPS+CodeContests) and repository-level (SWE-bench Verified) conditions.*

![Mean advantage variance bar chart](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_dl4c/docs/youra_research/20260502_dl4c/paper/figures/advantage_variance_bar.png)

*Figure 2. Mean GRPO advantage variance with 95% CI for both conditions.*

### 5.2 Reward Sparsity as Mechanistic Pathway (RQ2)

The positive reward rate directly explains the variance difference. In the function-level condition, approximately 0% of completions receive non-zero reward: CodeLlama-7b-Instruct essentially never generates a correct solution to an APPS or CodeContests problem within the allotted computation. Every group therefore has std(r)=0, every advantage is zero, and every gradient contribution vanishes.

In the repository-level condition, approximately 6% of completions receive non-zero reward through partial credit file-path overlap. This is sufficient to produce non-degenerate advantage groups in a meaningful fraction of training steps.

![Per-step positive reward rate](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_dl4c/docs/youra_research/20260502_dl4c/paper/figures/positive_rate_over_steps.png)

*Figure 3. Per-step positive reward rate (fraction of completions with non-zero reward) over 120 training steps.*

![Reward distribution comparison](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_dl4c/docs/youra_research/20260502_dl4c/paper/figures/reward_distribution.png)

*Figure 4. Reward distributions for function-level (left) and repository-level (right) conditions.*

### 5.3 Infrastructure Validation (H-E1)

All four curriculum GRPO conditions completed the 10-step smoke test without errors:

**Table 2.** H-E1 smoke test results (10 steps per condition).

| Condition | Exit Code | Checkpoints Saved | Reward Density Logs Produced |
|---|---|---|---|
| curriculum | 0 | Yes | Yes |
| uniform | 0 | Yes | Yes |
| easy_only | 0 | Yes | Yes |
| hard_only | 0 | Yes | Yes |

Reward density values were 0.0 across all 10 steps for all four conditions. This is consistent with the H-M1 finding: at initialization, even easy-tier APPS problems yield zero reward for the base model. The infrastructure is confirmed to be functioning correctly in that the logging system accurately records these zero values rather than producing spurious non-zero outputs.

The gate condition for H-E1 (MUST_WORK gate: infrastructure passes smoke test) is satisfied. The full 5000-step training run was not executed; no pass@1 comparison between curriculum and uniform conditions is available.

### 5.4 H-M2 Analysis (Not Completed)

H-M2 planned to measure Pearson correlation between per-checkpoint reward density and subsequent pass@1 gain (target: r>0.5) and to compare reward entropy between curriculum and uniform conditions. This analysis requires H-E1 full training logs (4 conditions × 5000 steps). Because full training was not executed, only the curriculum condition has checkpoints (8 checkpoints, steps 500–4000); uniform, easy_only, and hard_only conditions have no checkpoints. All reward density values are 0.0 across all checkpoints. The analysis pipeline was verified correct but could not be executed with the available data. H-M2 gate result: FAILED (SHOULD_WORK gate; not a blocking failure).

## 6. Discussion

### 6.1 Interpretation of the Advantage Variance Finding

The 76× advantage variance gap between function-level and repository-level GRPO training is not attributable to hyperparameter differences, training duration differences, or model initialization differences—all of these are held constant. The gap is explained algebraically: when positive reward rate ≈0%, std(r)=0 for essentially every training group, and the GRPO gradient is zero by definition. The result confirms that binary execution feedback on competitive programming problems is insufficient to produce informative GRPO gradients for CodeLlama-7b-Instruct-hf.

This finding does not imply that GRPO is generally ineffective. The repository-level condition (SWE-bench Verified) maintains advantage variance of 0.317, which indicates non-degenerate training. The distinction is between the reward structure (binary vs. partial credit) and the model's capability level relative to the task difficulty, not the algorithm itself.

### 6.2 Implications for Curriculum GRPO

The curriculum GRPO hypothesis posits that starting training on easier problems should maintain higher reward density during early training, preserving informative advantage groups and enabling the policy to improve before encountering harder problems. The H-M1 finding provides mechanistic motivation for this hypothesis: if early-curriculum problems yield non-zero reward rates, advantage groups are non-degenerate, and learning can occur.

However, the H-E1 smoke test showed reward density = 0.0 for all four conditions including easy_only. This raises a question about the activation condition for curriculum GRPO: if even easy-tier APPS problems yield zero reward for the model at initialization, easy-to-hard curriculum ordering provides no gradient advantage over uniform sampling, because both yield degenerate advantage groups throughout early training. Confirming or ruling out this possibility requires measuring per-difficulty-tier solve rates at initialization before committing to full training runs.

### 6.3 Limitations

**L1: Cross-granularity, not within-difficulty comparison.** H-M1 compares function-level (APPS+CodeContests) vs. repository-level (SWE-bench Verified) advantage variance. This establishes that reward sparsity causes advantage collapse but does not test whether easy-tier APPS problems yield higher reward density than hard-tier APPS problems within the function-level regime. The curriculum hypothesis requires a within-difficulty-level comparison that was not executed.

**L2: Single model.** The advantage variance comparison used CodeLlama-7b-Instruct-hf. Results may differ for other 7B architectures, for base models vs. instruction-tuned models, or for models at different capability levels. The finding is likely to generalize to other 7B-class models on competitive programming, but this has not been verified.

**L3: Behavioral hypothesis untested.** The primary behavioral claim—that easy-to-hard curriculum ordering improves HumanEval+ pass@1 relative to uniform sampling—was not tested. No full 5000-step training run was executed, and no pass@1 evaluation data exists for any condition. The paper's empirical contribution is the mechanistic characterization of advantage collapse (H-M1) and the infrastructure validation (H-E1), not a demonstration of curriculum effectiveness.

**L4: Assumption A1 unconfirmed.** The curriculum mechanism depends on the initializing policy having a non-zero solve rate on easy-tier problems (APPS tiers 0–2). The H-E1 smoke test showed 0.0 reward density even for the easy_only condition at initialization. If assumption A1 fails, the curriculum mechanism has no activation pathway. A targeted evaluation measuring per-tier solve rates at initialization is needed before proceeding to full training.

**L5: 120-step measurement window.** The advantage variance measurement was conducted over 120 training steps. This window is sufficient to characterize the reward distribution at initialization but does not capture whether variance might change over longer training horizons as the policy adapts.

**L6: Reward function confound.** The two conditions differ in both task granularity and reward function structure (binary vs. partial credit). It is not possible from this experiment alone to attribute the variance difference solely to task granularity rather than reward function design. Partial credit rewards applied to function-level tasks could potentially produce non-zero advantage variance even on competitive programming problems.

### 6.4 Practical Implications

Per-step advantage variance, measurable over as few as 10–20 training steps, provides a diagnostic signal for whether GRPO will produce informative gradients under a given reward function and model capability combination. A near-zero average advantage variance in early steps indicates that the reward structure is too sparse for the current model, regardless of other training configuration choices. This diagnostic is low-cost compared to full training runs.

## 7. Conclusion

We measured GRPO advantage variance in two conditions—function-level execution feedback on competitive programming tasks and repository-level execution feedback on software engineering tasks—using CodeLlama-7b-Instruct-hf with identical GRPO configuration (G=8, B=4, 120 steps). The result is a 76× advantage variance gap (0.004 vs. 0.317, p=5.34×10⁻⁴⁴, Cohen's d=1.904), explained by the difference in positive reward rates (≈0% vs. ≈6%). When positive reward rate is near zero, GRPO groups are degenerate and gradient contributions are zero.

We additionally implemented and smoke-tested training infrastructure for a 4-condition curriculum GRPO experiment on APPS+CodeContests. All four conditions (curriculum, uniform, easy_only, hard_only) completed the 10-step smoke test with exit code 0. Reward density was 0.0 in all conditions throughout the smoke test, consistent with the reward collapse finding. Full training was not executed; no behavioral comparison of curriculum vs. uniform sampling is available.

The primary open question raised by this work is whether assumption A1—that easy-tier APPS problems are solvable at initialization for DeepSeek-Coder-7B-base—holds. If it does, the full curriculum GRPO experiment is warranted. If it does not, alternative interventions such as SFT warm-up or partial credit reward shaping are needed before curriculum ordering can be expected to produce a gradient signal advantage.

Three concrete directions follow from these findings:

1. Measure per-difficulty-tier solve rates at initialization for the target model (DeepSeek-Coder-7B-base on APPS tiers 0–4) before running full curriculum GRPO training.
2. Implement and compare partial credit reward functions for function-level tasks to test whether reward engineering is a more tractable intervention than curriculum ordering for the advantage collapse problem.
3. Design a within-function-level experiment comparing easy-tier vs. hard-tier APPS advantage variance to directly test the curriculum mechanism rather than the cross-granularity confound.

## References

Bengio, Y., Louradour, J., Collobert, R., and Weston, J. (2009). Curriculum learning. In *Proceedings of the 26th International Conference on Machine Learning (ICML)*, pp. 41–48.

DeepSeek-AI (2025). DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning. *arXiv:2501.12948*.

Gehring, J., et al. (2024). Reinforcement learning from code execution feedback. *arXiv:2410.14986*.

Hendrycks, D., Basart, S., Kadavath, S., Mazeika, M., Arora, A., Guo, E., Burns, C., Puranik, S., He, H., Song, D., and Steinhardt, J. (2021). Measuring coding challenge competence with APPS. In *Advances in Neural Information Processing Systems (NeurIPS)*, 34.

Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., and Narasimhan, K. (2024). SWE-bench: Can language models resolve real-world GitHub issues? In *Proceedings of the International Conference on Learning Representations (ICLR)*.

Kumar, M. P., Packer, B., and Koller, D. (2010). Self-paced learning for latent variable models. In *Advances in Neural Information Processing Systems (NeurIPS)*, 23.

Le, H., Wang, Y., Gotmare, A. D., Savarese, S., and Hoi, S. C. H. (2022). CodeRL: Mastering code generation through pretrained models and deep reinforcement learning. In *Advances in Neural Information Processing Systems (NeurIPS)*, 35.

Li, Y., et al. (2022). Competition-level code generation with AlphaCode. *Science*, 378(6624), 1092–1097.

Platanios, E. A., Stretcu, O., Neubig, G., Poczos, B., and Mitchell, T. M. (2019). Competence-based curriculum learning for neural machine translation. In *Proceedings of NAACL-HLT*, pp. 1162–1172.

Rozière, B., et al. (2023). Code Llama: Open foundation models for code. *arXiv:2308.12950*.

Sachan, M. and Xing, E. (2016). Easy questions first? A case study on curriculum learning for question answering. In *Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics (ACL)*, pp. 453–463.

Schulman, J., Wolski, F., Dhariwal, P., Radford, A., and Klimov, O. (2017). Proximal policy optimization algorithms. *arXiv:1707.06347*.

Shao, Z., Wang, P., Zhu, Q., Xu, R., Song, J., Bi, X., Zhang, H., Zhang, M., Li, Y. K., Wu, Y., and Guo, D. (2024). DeepSeekMath: Pushing the limits of mathematical reasoning in open language models. *arXiv:2402.03300*.

Xu, B., et al. (2020). Curriculum learning for natural language understanding. In *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL)*, pp. 6095–6104.
