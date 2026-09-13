---
source_paper: "arxiv_2511_06307.md"
generated_at: "2026-03-15T15:15:59.770674"
model: "gpt-4o-mini"
summary_chars: 6958
---

# DRIVE: Data Curation Best Practices for RLVR in Competitive Code Generation

## Key Metadata
- **Authors:** Speed Zhu et al.
- **Year:** 2025
- **Venue:** arXiv
- **Core Contribution:** A two-stage reinforcement learning framework that enhances competitive programming code generation through effective data curation and curriculum design.

## Section Summaries

### Abstract
Recent reasoning-first models (e.g., OpenAI o1, DeepSeek R1) have spurred a resurgence of interest in RLVR. Nevertheless, advances are dominated by mathematics (e.g., AIME), with competitive-programming code generation underexplored and data curation receiving less attention than RL algorithm design. We investigate how to construct RLVR datasets (i.e., RL prompts) and present practical training techniques that yield strong performance on competitive-programming code generation. Our pipeline begins with supervised fine-tuning (SFT) distilled from strong open-source models, augmented with general-purpose and reasoning-intensive data. RL then follows a two-stage process with executable, testcase-driven rewards: first, training on a large, uniformly distributed set of competitive-programming problems using Group Relative Policy Optimization (GRPO) with 8 rollouts per prompt and a relatively short response-generation window (e.g., 32k during SFT and 24k in this stage) to expand entropy and mitigate repetition and truncation; second, we perform Pre-GRPO: updating on a small, high-quality set of challenging problems with a large rollout budget (64 rollouts per prompt) under a hard-focus curriculum that continuously retains the most difficult instances throughout training. We implement our method on Qwen2.5-32B and evaluate on LeetCode and Codeforces weekly contests to avoid data leakage. The resulting model achieves state-of-the-art performance among models of similar scale and is comparable to leading systems such as DeepSeek v3.1 and Doubao-1.5-Thinking. We also examine scaling trends and observe strong RL scaling on an internal large-scale MoE model. Our study distills concise best practices for data curation, entropy expansion, and curriculum design in RLVR for competitive-programming code generation.

### Introduction & Motivation
The authors highlight a gap in applying reinforcement learning with verifiable rewards (RLVR) to competitive programming, an area requiring both algorithmic understanding and coding precision. Most prior research has emphasized algorithm design rather than data curation and training techniques, leading to suboptimal performance on competitive programming tasks. Competitive programming requires models to produce executable solutions that are both correct and optimized for efficiency, underscoring the need for innovative strategies in dataset construction and reinforcement learning methodology.

### Methodology
The proposed methodology consists of two main phases:

1. **Supervised Fine-Tuning (SFT):** 
   - We start with supervised fine-tuning on the Qwen2.5-32B model, utilizing a distillation process from strong open-source models. The training set is compiled from 1.27M competitive programming prompts, refined to 470K high-quality prompts through a five-round arena learning method. 
   - Problem difficulty is classified into easy, medium, and hard categories, with hard problems duplicated for emphasis. Unlike traditional methods, we avoid computationally intensive sampling techniques and instead focus on simpler duplication to enhance model learning.
   - The SFT is run for 3 epochs with a learning rate of \(1 \times 10^{-5}\) using a batch size of 512 across 256 GPUs.

2. **Two-Stage Reinforcement Learning:**
   - This phase is conducted in two stages. 
   - **Stage 1 (Entropy Expansion):** The model is trained on a mixed dataset of 9K problems with 8 rollouts per prompt and a sequence length of 24K tokens. This stage enhances output diversity and reduces repetitive generation, subsequently improving overall competitive programming capabilities.
   - **Stage 2 (Hard-Focus Curriculum):** The model is trained on a carefully selected dataset of challenging problems using Pre-GRPO, which filters and retains low-pass-rate cases to continue training with a hard-focus curriculum. We employ a rollout budget of 64 samples to ensure stability and depth in learning. The training spans three phases, progressively increasing problem difficulty with consistently high rollout counts.

### Experiments & Results
The experiments were structured as follows:

- **Datasets:** The study uses datasets from multiple sources, including 1.27M competitive programming prompts distilled to 470K high-quality samples for SFT, and 9K mixed competitive problems for the RL phase.
- **Evaluation Metrics:** Performance was assessed using pass rates (Pass@10) and average accuracy (Avg@1) on benchmarks like LeetCode and Codeforces. 
- **Baselines:** The proposed methods were compared against models such as DeepseekV3.1 and previous systems like Seed1.6-0715.
  
| Method                     | LeetCode Weekly OJ (Pass@10) | Codeforces OJ (Avg@1) |
|--------------------------- |------------------------------ |----------------------- |
| SFT (Qwen2.5-32B)         | 58.3%                        | 0.182                  |
| RL Stage 1                 | +16.1% (relative improvement) | +58.3%                |
| RL Stage 2                 | +13.0%                      | Up to +0.079           |

The results demonstrate that the model outperforms previous state-of-the-art techniques while only utilizing 32B parameters, achieving competitive or superior results against much larger models. Additionally, comprehensive ablation studies confirm that the proposed two-stage RL methodology significantly boosts performance on difficult tasks.

### Discussion & Conclusion
The findings highlight the crucial role of data curation and curriculum design in the success of RLVR in competitive coding applications. The two-stage framework effectively mitigates standard RL issues such as difficulty management and redundancy in code generation. Future work could delve into adaptive curriculum strategies and explore the integration of even more complex problem sets to further enhance model capability.

## Key Contributions
- A novel, two-stage RL framework for competitive programming enhancing model training efficiency through targeted data curation.
- Empirical evidence validating the necessity of large rollout budgets for challenging problem mastery.
- Detailed analysis revealing the importance of entropy expansion and hard-focus curriculum in reinforcing effective problem-solving capabilities.

## Potential Relevance
This work may inform the development of future hypotheses surrounding scaling methodologies in RLVR. Its emphasis on data curation, curriculum strategies, and empirical analysis of model performance may offer useful insights for enhancing performance in other challenging AI domains.