# Introduction

When a reward model assigns a score, we assume it evaluates the response's content---its accuracy, helpfulness, and reasoning quality. Yet our experiments reveal a striking pattern: RLHF-trained reward models systematically assign higher scores to responses that enumerate options, even when content, length, and quality are precisely matched. Across three of four architecturally distinct reward models, enumerated responses receive significantly higher scores than synthesized alternatives (pooled Cohen's *d* = 0.70), suggesting that RLHF training encodes implicit preferences for formatting features independent of actual response quality.

This finding has significant implications for language model alignment. Reward models serve as the optimization target in RLHF, guiding language models toward behaviors that humans prefer [Ouyang et al., 2022]. If these models encode structural biases alongside content preferences, RLHF optimization may inadvertently steer language models toward superficial formatting patterns rather than substantive improvements in helpfulness or accuracy. Consider a medical advice system: it might receive higher reward scores for listing treatment options in numbered format over providing a well-reasoned single recommendation, regardless of which presentation is clinically appropriate for the patient's situation.

## The Problem: Unexplored Structural Dimensions

Prior work has made substantial progress in understanding reward model behavior along *content* dimensions. RewardBench [Lambert et al., 2024] evaluates reward models on helpfulness, safety, and reasoning accuracy. MRMBench probes multi-dimensional preferences including instruction following and harmlessness. These benchmarks assume that reward model scores primarily reflect content quality---the accuracy, completeness, and appropriateness of responses.

However, this focus on content leaves a critical dimension unexplored: *structural* preferences. When human raters compare responses during preference data collection, they may unconsciously prefer certain formatting patterns---numbered lists, bullet points, explicit step-by-step organization---that are easier to scan and evaluate. If reward models faithfully encode these implicit formatting preferences, they learn to associate structure with quality independent of what that structure contains.

This gap matters because existing evaluation methods cannot detect it. RewardBench tests whether reward models correctly identify better responses, not whether they exhibit systematic biases toward particular formats. HumanAgencyBench [Sturgeon et al., 2025] evaluates how well language models support user autonomy, but examines LLM outputs rather than the reward models that train them. No systematic behavioral probing exists for structural (non-content) preferences in reward models.

## Our Insight: Enumeration as a Beacon Feature

We hypothesize that enumeration markers---numbered lists, bullet points, explicit options---function as "beacon features" during RLHF training. These patterns are visually distinctive, occur at predictable positions in responses, and provide clear, stable signals during gradient-based learning. Human raters may unconsciously prefer enumerated responses because they are easier to scan and evaluate, and reward models faithfully encode this preference as an independent structural signal.

Critically, we observe that this effect depends on model architecture. In decoder-only transformers with causal attention, enumeration markers create cumulative structural signals as the model processes the sequence. In encoder-only models with bidirectional attention, the same markers are processed as local patterns without sequential accumulation. This architectural difference predicts that decoder-based reward models should exhibit enumeration preference while encoder-based models may not.

## Contributions

Building on this insight, we make the following contributions:

1. **First Systematic Structural Probe for Reward Models.** We introduce a methodology for behavioral probing of structural (non-content) preferences in RLHF-trained reward models. Using controlled stimulus pairs that match content, length, correctness, and completeness while varying only structural format, we isolate the effect of enumeration on reward model scores.

2. **Multi-Architecture Analysis.** We evaluate four architecturally distinct reward models spanning different training objectives (Bradley-Terry, scalar regression, mixture-of-experts) and base architectures (Llama-3, Llama, Mistral, DeBERTa). We find significant enumeration preference in three decoder-based models (*d* = 0.38--1.45) and no significant effect in the encoder-only model (*d* = 0.08, *p* = 0.35).

3. **Architecture-Conditional Effect.** We identify a surprising architectural boundary: the enumeration preference is robust in decoder-only models but absent in encoder-only PairRM. This finding suggests that structural encoding depends on how models process sequential information, opening new questions about the relationship between attention mechanisms and learned preferences.

Our results demonstrate that reward model evaluation must extend beyond content dimensions. Understanding which structural features reward models encode---and why---is essential for building alignment systems that optimize for genuine quality rather than superficial formatting patterns.

The remainder of this paper is organized as follows. Section 2 discusses related work on reward model evaluation and structural preferences. Section 3 presents our methodology for controlled structural probing. Section 4 describes our experimental setup. Section 5 presents results demonstrating the enumeration preference and its architectural dependency. Section 6 discusses implications and limitations, and Section 7 concludes.
