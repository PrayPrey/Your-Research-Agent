# 1. Introduction

Group Relative Policy Optimization (GRPO) promises to train code-generating language models directly from execution feedback — no human labels, no preference annotations, just a compiler and a test suite. Yet when we applied GRPO to competitive programming problems with a 7B code model, the training signal collapsed: across 120 consecutive gradient steps on function-level tasks, advantage variance measured a mere 0.004 — nearly indistinguishable from zero. Meanwhile, the same model trained on repository-level tasks under identical configuration produced advantage variance of 0.317, a **76× difference**. This gap is not a tuning artifact or a statistical quirk. It is a structural property of how GRPO's group-relative normalization interacts with sparse execution rewards.

Execution-feedback reinforcement learning is an appealing paradigm for code generation. Methods like CodeRL [Le et al., 2022], RLEF [Gehring et al., 2024], and DeepSeek-R1 [DeepSeek-AI, 2025] demonstrate that training against actual test execution produces stronger code models than supervised fine-tuning alone. GRPO [Shao et al., 2024], which replaces a learned value baseline with group-relative advantage normalization, has become a popular choice due to its simplicity and effectiveness at scale.

However, GRPO's advantage function carries a structural precondition. The group-relative advantage is computed as:

$$A_i = \frac{r_i - \text{mean}(r_{\text{group}})}{\text{std}(r_{\text{group}})}$$

When all $G$ completions in a group receive identical reward — most critically, when all fail and receive reward zero — $\text{std}(r_{\text{group}}) = 0$, the advantage is undefined, and the gradient contribution is zero. This degenerate case is not an edge case for 7B base models on competitive programming: it is the dominant training regime. At APPS+CodeContests difficulty, a 7B-class model generates near-zero correct completions, meaning degenerate groups dominate throughout training. The policy update never gets off the ground.

This failure mode is invisible in standard training diagnostics. Training loss curves may appear stable. Benchmark evaluations at fixed intervals may show marginal changes. Only by measuring advantage variance directly — the quantity that determines gradient signal quality in GRPO — does the collapse become visible.

**Key Insight.** Task granularity, not model size alone, determines whether GRPO advantage normalization produces informative gradients. Function-level execution feedback on competitive programming problems yields near-zero positive reward rates for 7B models, collapsing advantage variance to near-zero. Repository-level tasks, where even partial file-path overlap in a unified diff can yield non-zero reward, maintain sufficient positive rates (~6%) to produce discriminative advantage groups. The gap is 76×, with effect size Cohen's $d = 1.904$ — far beyond any conventional threshold for a large effect.

Our contributions are:

1. **Empirical characterization of advantage variance collapse**: We measure GRPO advantage variance across 120 training steps at two task granularities — function-level (APPS+CodeContests) and repository-level (SWE-bench Verified) — using a controlled experimental setup (same model, same $G=8$ configuration). We find a 76× variance ratio ($p = 5.34 \times 10^{-44}$, Cohen's $d = 1.904$), establishing that binary execution feedback on competitive programming problems is insufficient for effective GRPO training of 7B-class models.

2. **Training infrastructure for curriculum GRPO**: We implement and validate a complete GRPO training pipeline for difficulty-stratified curriculum on APPS+CodeContests, including a `CurriculumCallback` that transitions difficulty tiers at configurable training steps and a `RewardDensityCallback` that logs per-step advantage statistics. This infrastructure supports future empirical testing of the curriculum GRPO hypothesis.

3. **Mechanistic grounding for the curriculum hypothesis**: The H-M1 finding provides the mechanistic motivation for easy-to-hard curriculum ordering in GRPO training: if early training starts from problems where the initializing policy has non-zero solve rate, reward density is preserved, advantage groups remain informative, and the policy gradient carries signal throughout the curriculum. We characterize the conditions under which this mechanism can activate.

The rest of this paper is organized as follows. Section 2 reviews related work on execution-feedback RL and curriculum learning. Section 3 describes our experimental methodology. Section 4 presents the advantage variance comparison experiment. Section 5 reports results and analysis. Section 6 discusses implications and limitations. Section 7 concludes with future directions.
