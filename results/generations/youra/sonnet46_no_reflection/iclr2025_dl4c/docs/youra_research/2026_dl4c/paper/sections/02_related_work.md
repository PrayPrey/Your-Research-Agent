# 2. Related Work

We survey three lines of work that collectively motivate but do not provide
structural efficiency measurement for code generation alignment.

## 2.1 Execution-Feedback Reinforcement Learning for Code Generation

A growing body of work demonstrates that execution feedback improves code
generation beyond supervised fine-tuning. CodeRL [Le et al., 2022] introduces
actor-critic training with unit test feedback, establishing that execution
outcome signals can guide policy improvement. PPOCoder [Shojaee et al., 2023]
extends PPO-based RL to code synthesis, showing gains on HumanEval and MBPP.
TÜLU 3 [Lambert et al., 2024] demonstrates that GRPO with binary pass/fail
rewards on code problems yields competitive pass@1 improvements in a
multi-task alignment setting. CodeRL+ [Jiang et al., 2025] shows that
variable-level execution trajectory rewards outperform binary pass/fail by
+4.6% pass@1, suggesting reward granularity affects outcome.

**The limitation of this line:** all comparisons are made on pass@1 outcomes.
None of these works measures *how* the policy moves structurally relative to
the base model. It is unknown whether the observed improvements reflect
genuinely richer structural learning or more decisive surface-level pattern
matching. Our framework provides the diagnostic to answer this question.

## 2.2 DPO and Preference-Based Alignment

Direct Preference Optimization [Rafailov et al., 2023] provides an alternative
post-training objective that avoids online rollouts by framing RLHF as a
supervised learning problem over preference pairs. DPO has been applied to
code generation [Guo et al., 2024; Luo et al., 2023], typically using
execution-oracle labeling (passing vs. failing solutions as preferred/rejected).
GRPO [Shao et al., 2024] reformulates PPO's policy gradient without a critic
network, using group-relative rewards, and has become the dominant execution-RL
method for code alignment following DeepSeek-R1 [DeepSeek-AI, 2025].

**The limitation of this line:** DPO and GRPO are compared on benchmark outcomes,
not on structural properties of the policy change they induce. KL divergence
appears in both frameworks as a constraint (DPO's implicit KL regularization;
GRPO's KL penalty term $\beta$), but is used only as a training-time constraint,
never as a diagnostic normalizer for structural movement analysis. We repurpose
KL divergence from a training constraint into a measurement tool.

## 2.3 AST-Based Code Analysis and Similarity Metrics

The program analysis community has developed rich tools for AST-level code
comparison. The FA-AST taxonomy [Wang et al., 2020] classifies Python AST nodes
into control-flow (If, For, While, Try, With), data-flow (Assign, Call, Return,
FunctionDef), and surface categories, providing a principled semantic
classification of structural program elements. The ZSS algorithm [Zhang & Shasha,
1989] computes minimum-cost tree edit distance and has been validated as
correlating with established code similarity metrics [Ding et al., 2024,
arXiv:2404.08817]. Code clone detection [Svajlenko et al., 2014] and program
repair [Hua et al., 2018] literatures use AST edit distances extensively.

**The limitation of this line:** AST analysis in program analysis is applied to
pairs of programs, not to the *policy movement* of a trained model relative to
its base. The composition of FA-AST classification, ZSS edit distance,
and KL-matched checkpoint comparison — which enables structural efficiency
measurement — has not been proposed or validated.

## 2.4 Policy Analysis and Interpretability in RL Fine-Tuning

Recent work on understanding RL fine-tuning [Schulman et al., 2017; Zheng et al.,
2023] focuses on training stability, reward hacking, and KL divergence management.
[CITATION NEEDED: work on structural analysis of RL policy changes in NLP/code].
Mechanistic interpretability work [Anthropic, 2023; Elhage et al., 2022] analyzes
model internals (attention heads, circuits) but does not specifically measure
the structural quality of code-level policy movement as a function of alignment
method.

**Our position:** We bring program analysis tools (FA-AST, ZSS) into the alignment
evaluation setting, providing a structural lens on policy movement that complements
both activation-level interpretability and benchmark-based evaluation. The result
is a framework that any team can apply to their checkpoint archive to diagnose
whether their alignment method produces structurally rich policy change.
