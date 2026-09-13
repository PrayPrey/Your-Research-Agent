# 1. Introduction

When we train a language model with execution feedback, does it learn to think
differently about code — restructuring control flow and data dependencies — or
does it simply become more confident about the same surface patterns? Despite
the widespread adoption of execution-feedback reinforcement learning (RL) for
code generation [Le et al., 2022; Shojaee et al., 2023; Lambert et al., 2024],
no measurement framework exists to distinguish these two fundamentally different
modes of policy change.

The common approach to comparing alignment methods — reporting pass@1 on
HumanEval+ or MBPP+ — answers only the outcome question: which method produces
more correct code? It cannot answer the structural question: which method induces
richer, more semantically meaningful policy movement per unit of deviation from
the base model? A model fine-tuned with GRPO-binary might achieve +3% pass@1
over DPO, but this number alone tells us nothing about whether the model has
learned to structure programs differently or has merely become more decisive
about existing surface patterns. These two scenarios have different implications
for generalization, robustness, and interpretability of code-generating models.

The deeper problem is that pass@1 conflates two distinct phenomena. **Structural
learning** occurs when a model reallocates probability mass toward control-flow
and data-flow AST transformations — the nodes that determine whether code is
functionally correct. **Confidence redistribution** occurs when a model becomes
more decisive about existing surface patterns without changing the underlying
structural distribution over code. The first represents genuine alignment
improvement; the second may inflate benchmarks without improving the model's
underlying understanding of program structure.

The gap in existing work is specific: no controlled, head-to-head comparison of
execution-RL and DPO exists under identical base model, training data, and
compute budget conditions, and no metric for structural policy movement quality
has been proposed or validated. The tools are available in isolation — ZSS tree
edit distance [Zhang & Shasha, 1989], FA-AST taxonomy [Wang et al., 2020], and
KL divergence from the base model — but they have not been composed into a
unified, reproducible framework for alignment analysis.

**Our key insight:** policy movement quality in code generation can be measured
as *semantic AST edit distance per unit KL divergence* — a quantity we call
**structural efficiency**. This metric restricts edit distance to control-flow
and data-flow AST nodes (via the FA-AST taxonomy), normalizes by KL divergence
at KL-matched checkpoints, and captures whether a method spends its "policy
change budget" on structurally meaningful program transformations. A high
structural-efficiency method changes more of what matters (functional code
structure) per unit of distance from the base model.

Building on this insight, we make the following contributions:

**1. The structural efficiency metric.** We formally define semantic-edit-per-KL
as a diagnostic for code generation alignment, grounded in established program
analysis tools (FA-AST taxonomy, ZSS tree edit distance) and information theory
(KL divergence). The metric is model-agnostic, language-agnostic for
AST-parseable languages, and reproducible from standard training checkpoints.

**2. An end-to-end measurement framework.** We implement and validate a complete
pipeline: FA-AST node classification, ZSS-based semantic AST edit distance,
KL-matched checkpoint selection, Semantic Edit Proportion (SEP), bootstrap
confidence intervals, and Mann-Whitney statistical testing. We demonstrate the
framework executes correctly end-to-end on DeepSeek-Coder-7B-instruct-v1.5
[Guo et al., 2024] trained with TRL GRPOTrainer and DPOTrainer [von Werra et al., 2020].

**3. A preliminary empirical analysis with a surprising finding.** Our proof-of-concept
demonstrates that GRPO exhibits substantially higher *raw* semantic AST edit
distance than DPO (+250% on synthetic data), yet the Semantic Edit Proportion —
the fraction of edits targeting semantic nodes — is nearly identical (≈0.237 for
both). This dissociation challenges the assumption that execution reward
selectively concentrates policy movement on functionally relevant code structures.
We discuss three competing interpretations and provide a corrected experimental
protocol for resolution.

**4. A documented methodological confound: checkpoint aliasing.** We identify
and characterize *checkpoint aliasing* — a failure mode in which insufficient
checkpoint diversity causes a nominally large analysis (27 pairs) to collapse to
an effective sample size of ≈2, silently corrupting statistical tests. This
confound affects any checkpoint-comparison study of RL fine-tuning and has not
been previously documented.

We organize the paper as follows. Section 2 surveys three lines of related work,
showing that none provides structural efficiency measurement under controlled
conditions. Section 3 defines the structural efficiency framework formally.
Section 4 describes our experimental setup. Section 5 presents results —
framework validation and the preliminary SEP finding. Section 6 interprets the
results and discusses limitations. Section 7 concludes with a vision for
corrected experimentation and broader application of the framework.
