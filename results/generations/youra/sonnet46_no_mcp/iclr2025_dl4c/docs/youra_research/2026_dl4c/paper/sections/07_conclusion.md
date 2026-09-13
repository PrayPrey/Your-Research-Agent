# 7. Conclusion

We began by observing that GRPO training on competitive programming problems collapsed: advantage variance of 0.004, effectively zero, across 120 consecutive gradient steps. We now understand why. Function-level execution feedback on competitive programming problems produces near-universal degenerate GRPO advantage groups for 7B-class models, because the positive reward rate is essentially zero — no completion in the group succeeds, std(r) = 0, and the gradient contribution vanishes. The policy learns nothing. This is not a failure of GRPO as an algorithm; it is a failure of the reward structure to satisfy GRPO's structural precondition: at least one completion in each group must receive non-zero reward.

## 7.1 Summary

In this work, we addressed the question of why execution-feedback GRPO fails silently on competitive programming problems by measuring the mechanistic quantity that determines gradient signal quality: GRPO advantage variance. Our contributions are:

1. **Advantage collapse characterization:** A controlled comparison of function-level (APPS+CodeContests) vs. repo-level (SWE-bench Verified) GRPO training reveals a 76× advantage variance gap (0.004 vs. 0.317, $p = 5.34 \times 10^{-44}$, Cohen's $d = 1.904$), confirming that binary execution reward on competitive programming is insufficient for effective GRPO with 7B-class models.

2. **Mechanistic pathway:** The collapse is explained by positive reward rate: function-level ≈0% vs. repo-level ≈6%. Even a small non-zero positive rate is sufficient to produce discriminative advantage groups; near-zero positive rate guarantees degenerate groups throughout training.

3. **Curriculum GRPO infrastructure:** A validated 4-condition training pipeline (curriculum, uniform, easy\_only, hard\_only) on APPS+CodeContests with TRL 1.3.0 GRPOTrainer, including CurriculumCallback for difficulty tier transitions and RewardDensityCallback for per-step advantage diagnostics.

## 7.2 Future Directions

This work opens three concrete research directions, each grounded in our experimental findings:

**From the reward collapse observation (H-E1, all conditions reward\_density=0.0):** Measure per-difficulty-tier solve rates at initialization for DeepSeek-Coder-7B-base on APPS tiers 0–4. If easy-tier problems yield non-zero solve rates, the curriculum mechanism has an activation pathway and the full 5000-step training run (4 conditions, EvalPlus evaluation) is warranted. If all tiers yield zero, the experiment requires either SFT warm-up before GRPO or partial credit reward shaping.

**From the reward structure finding (repo-level partial credit maintains viable variance):** Implement and compare partial credit rewards for function-level tasks — e.g., compilation success = 0.1, any test pass = 0.3, all tests pass = 1.0. This tests the competing explanation that reward engineering matters more than curriculum ordering for rescuing degenerate GRPO training.

**From the cross-granularity limitation (H-M1 measured function vs. repo, not easy vs. hard APPS tiers):** Design a within-function-level experiment comparing easy-tier (APPS 0–2) vs. hard-tier (APPS 3–4) advantage variance using the existing CodeLlama-7b-Instruct infrastructure. This directly tests whether the curriculum mechanism (not just granularity) produces the predicted reward density effect.

As execution-feedback RL continues to mature, understanding the conditions under which it works — and diagnosing when it silently fails — is as important as developing new algorithms. We hope this characterization of advantage collapse encourages practitioners to measure training diagnostics alongside benchmark performance, and researchers to develop reward structures that maintain informative gradients across the full range of task difficulty.
