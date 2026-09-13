# Related Work

Our work connects three research threads: alignment methods for language models, reinforcement learning for code generation, and error taxonomy analysis. We position our contribution at their intersection—an area that remains unexplored despite extensive work in each domain individually.

## Alignment Methods for Language Models

The landscape of alignment methods has expanded significantly since the introduction of reinforcement learning from human feedback (RLHF) [Ouyang et al., 2022]. Direct Preference Optimization (DPO) [Rafailov et al., 2023] emerged as a computationally efficient alternative that directly optimizes a preference objective without requiring a separate reward model. Recent work has compared these approaches, with Xu et al. [2024] demonstrating that PPO surpasses DPO in code competition settings, attributing the difference to "fundamental limitations" of the DPO objective.

However, existing comparisons focus exclusively on aggregate performance metrics (pass@k). Our work reveals a complementary dimension: alignment methods differ not just in *how often* models succeed, but in *how* they fail. This failure-mode analysis provides mechanistic insight into why methods perform differently.

## Reinforcement Learning for Code Generation

CodeRL [Le et al., 2022] established execution-based RL as a viable approach for code generation, using binary test pass/fail as the reward signal. Subsequent work refined this approach: StepCoder [Dou et al., 2024] introduced curriculum learning with compiler feedback, and RLEF [Liu et al., 2024] extended end-to-end execution feedback. PPOCoder [Shojaee et al., 2023] applied proximal policy optimization specifically to code tasks.

These approaches share a common reward structure: binary execution reward where all non-executing programs receive zero reward regardless of their semantic proximity to correctness. We theorize this creates a "zero-reward basin" in the loss landscape—a flat region over all execution failures that provides no gradient information to distinguish syntactically invalid code from semantically incorrect but executable code. Our experiments test whether this reward topology manifests in observable error distributions.

## DPO and Preference-Based Code Alignment

DPO-based code alignment has emerged through multiple pathways. CodeLlama-Instruct [Rozière et al., 2023] applies instruction tuning to the CodeLlama base model, incorporating preference data without explicit execution feedback during training. More recent approaches like CodeDPO [Chen et al., 2025] construct preference pairs using both correctness and efficiency criteria, while Focused-DPO [Wang et al., 2024] targets error-prone code regions.

A critical assumption in our hypothesis is that standard DPO training does not incorporate execution-based filtering of preference pairs. We validate this assumption by analyzing the training procedures of models in our study: CodeLlama-Instruct uses general instruction-following preferences, not execution-filtered code pairs. This distinction is essential—if DPO training already incorporated execution feedback, we would expect reduced divergence between methods.

## Error Taxonomy and Classification

Error analysis in code generation has developed rich taxonomies. The ICSE 2025 study by Wang et al. [2025] provides a three-tier classification (syntax, runtime, assertion) based on execution semantics. The LlmFix framework [Zhang et al., 2024] extends this to 19 distinct error causes, enabling fine-grained analysis of failure modes.

Critically, prior taxonomy work has categorized errors *without stratifying by training method*. The implicit assumption is that error distributions are primarily determined by task difficulty or model capacity, not alignment objectives. Our work challenges this assumption by demonstrating systematic alignment-induced variation in P(error_type | failure).

## Research Gap

Table 1 summarizes the positioning of our work relative to prior contributions:

| Prior Work | Contribution | Gap We Address |
|------------|--------------|----------------|
| Xu et al. [2024] | PPO vs DPO pass rate comparison | Aggregate metrics only; no error analysis |
| Wang et al. [2025] | Error taxonomy (ICSE 2025) | Not stratified by alignment method |
| Zhang et al. [2024] | 19-cause error classification (LlmFix) | Not stratified by alignment method |
| Le et al. [2022] | CodeRL execution-based RL | No DPO comparison; pass rate focus |

We provide the first study that combines alignment method comparison with conditional error distribution analysis, revealing that alignment objectives function as inductive biases over failure mode geometry.
