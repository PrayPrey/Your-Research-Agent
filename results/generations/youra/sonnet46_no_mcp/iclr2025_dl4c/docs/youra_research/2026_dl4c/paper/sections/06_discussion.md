# 6. Discussion

## 6.1 Key Findings

Our experiments reveal two findings that together reframe the applicability of execution-feedback GRPO for code model training.

**Finding 1: Binary execution feedback on competitive programming problems is insufficient for GRPO with 7B-class models.** The 76× advantage variance gap (function-level: 0.004 vs. repo-level: 0.317) is not a hyperparameter sensitivity — it is a structural consequence of the GRPO formulation interacting with near-zero positive reward rates. Practitioners who apply GRPO to competitive programming datasets with 7B base models should expect this degenerate regime. This suggests that the impressive results from execution-feedback GRPO in the literature depend on either larger models (which have higher baseline solve rates) or simpler task distributions (where non-zero positive rates are more common).

**Finding 2: Reward structure determines viable training granularity, not task difficulty alone.** The repo-level condition (SWE-bench Verified) maintains viable advantage variance (0.317) despite being arguable more complex than competitive programming — because its partial reward structure (file-path overlap) provides non-zero signal even for imperfect completions. This suggests that reward engineering — specifically moving from binary to partial-credit reward — may be a more tractable intervention than difficulty curriculum for rescuing degenerate GRPO training. Both directions warrant exploration.

## 6.2 Implications for Curriculum GRPO

The H-M1 finding has a specific implication for the curriculum GRPO hypothesis. The curriculum mechanism requires a solvability gradient: easy-tier problems must yield higher positive reward rates than hard-tier problems for the initializing policy, so that early curriculum phases maintain non-degenerate advantage groups. The H-E1 smoke test showed reward density = 0.0 for all four conditions (including easy-only) at initialization. This raises an important caveat: if even easy-tier APPS problems yield zero reward for DeepSeek-Coder-7B-base, the curriculum effect has no activation pathway, and easy-to-hard ordering provides no advantage over uniform sampling.

This does not invalidate the curriculum hypothesis — it sharpens it. Measuring per-difficulty-tier solve rates at initialization (a quick 50-problem evaluation per tier) would determine whether assumption A1 (easy problems are solvable at initialization) holds. If it does, full 5000-step curriculum training is warranted. If it does not, the experiment requires either a warm-up phase (SFT on easy problems before GRPO) or a shift to partial credit rewards that provide gradient signal even for zero-execution-success completions.

## 6.3 Limitations

**L1 — H-M1 measured cross-granularity, not within-difficulty curriculum effects.** The experiment compares function-level (APPS+CodeContests) vs. repo-level (SWE-bench Verified) advantage variance. This establishes that reward sparsity causes advantage collapse, but it does not directly test whether easy-tier APPS problems yield higher reward density than hard-tier APPS problems within the function-level regime. The curriculum hypothesis requires a within-difficulty comparison (easy vs. hard APPS tiers), which was not executed. H-M1 provides mechanistic motivation for curriculum but cannot be cited as direct evidence that curriculum ordering affects reward density.

**L2 — Single model (CodeLlama-7b-Instruct-hf).** The advantage variance comparison used CodeLlama-7b-Instruct rather than DeepSeek-Coder-7B-base (the intended curriculum GRPO model), because CodeLlama had known capability characteristics for this experiment's design. Results may differ for base models vs. instruction-tuned models, or for different 7B architectures. The finding is likely to generalize to other 7B-class models on competitive programming, but this has not been directly verified.

**L3 — Primary behavioral hypothesis (curriculum improves pass@1) remains untested.** The H-E1 full training run (5000 steps, 4 conditions, EvalPlus evaluation) was not executed. No pass@1 comparison between curriculum and uniform conditions exists. The paper's primary contribution is mechanistic (characterizing advantage collapse) and infrastructural (validated training pipeline), not behavioral. Claims about curriculum improving HumanEval+ performance cannot be made from current data.

**L4 — Assumption A1 (easy APPS problems are solvable at initialization) is unconfirmed.** The H-E1 smoke test showed 0.0 reward density even for the easy-only condition. If APPS tier 0–2 problems are too hard for a 7B base model at initialization, the entire reward density mediation mechanism has no activation pathway regardless of curriculum ordering.

## 6.4 Broader Impact

This work has two broader impacts. Positively, characterizing the advantage collapse failure mode provides practitioners with a diagnostic tool (measure per-step advantage variance early in training) and actionable guidance (if variance ≈ 0, binary execution reward is insufficient — consider partial credit rewards or warm-up SFT before GRPO). Negatively, the curriculum infrastructure validated in this work could in principle be used to select training data in ways that introduce unintended curriculum biases; practitioners should verify that difficulty tier labels reflect the model's actual capability distribution rather than arbitrary metadata.
