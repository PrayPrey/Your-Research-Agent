---
source_paper: "arxiv_2310_04564.md"
generated_at: "2026-05-08T05:59:30.929105"
model: "gpt-4o-mini"
summary_chars: 6435
---

# ReLU Strikes Back: Exploiting Activation Sparsity in Large Language Models

## Key Metadata
- **Authors:** Iman Mirzadeh et al.
- **Year:** 2023
- **Venue:** arXiv
- **Core Contribution:** This paper re-evaluates the use of ReLU activation in Large Language Models (LLMs), demonstrating significant computation savings during inference without sacrificing performance, through the novel "relufication" process.

## Section Summaries

### Abstract
Large Language Models (LLMs) with billions of parameters have drastically transformed AI applications. However, their demanding computation during inference has raised significant challenges for deployment on resource-constrained devices. Despite recent trends favoring alternative activation functions such as GELU or SiLU, known for increased computation, this study strongly advocates for reinstating ReLU activation in LLMs. We demonstrate that using the ReLU activation function has a negligible impact on convergence and performance while significantly reducing computation and weight transfer. This reduction is particularly valuable during the memory-bound inference step, where efficiency is paramount. Exploring sparsity patterns in ReLU-based LLMs, we unveil the reutilization of activated neurons for generating new tokens, and leveraging these insights, we propose practical strategies to substantially reduce LLM inference computation up to three times, using ReLU activations with minimal performance trade-offs.

### Introduction & Motivation
Large Language Models (LLMs) present significant computational and memory challenges, hindering their deployment in resource-constrained environments. Recent methods have focused on improving inference efficiency, yet activation sparsity remains underutilized. ReLU activation is known for inducing sparsity but has been overshadowed by alternatives like GELU or SiLU, which, despite slightly better convergence, incur higher computational costs. This paper aims to demonstrate that ReLU can be effectively employed in LLMs to capitalize on activation sparsity, thereby reducing inference costs while maintaining performance.

### Methodology
The authors utilize the OPT model, replacing alternative activation functions with ReLU, to evaluate the impacts on performance and computational efficiency. Key aspects of the proposed methodology include:

- **Core Algorithm:** The primary algorithm focuses on the "relufication" process, where non-ReLU activations in pretrained models are systematically replaced with ReLU. This is conducted in two stages: 1) replacing non-ReLU activations in the Feed Forward Network (FFN), 2) adding ReLU layers after normalization layers. 

- **Model Architecture:** The models evaluated include OPT (with ReLU by default), Llama (using SiLU), and Falcon (using GELU). Each model's architecture supports sparsity in activations, confirmed through analysis showing over 90% sparsity in all layers of the OPT model.

- **Hyperparameters:** Fine-tuning is performed at a fixed learning rate of 1.5e-5 for Llama, Falcon, and OPT, with the AdamW optimizer and ZeRO stage 1 to shard optimizer states across GPUs.

- **Training Procedure:** Models are trained from scratch on the RefinedWeb dataset, encompassing around 100 billion tokens. Evaluations are conducted using various tasks from the Language Model Evaluation Harness to measure performance using metrics such as accuracy.

- **Data Preprocessing:** The analysis included tracking activation patterns and sparsity across layers during both training and evaluation.

Novel components include insights on activation sparsity in existing models, suggesting that the introduction of additional activation layers can further harness computational efficiency through architectural changes without necessitating retraining from scratch.

### Experiments & Results
The experiments are centered around assessing the impact of ReLU through a series of systematic evaluations. 

- **Datasets:** The RefinedWeb dataset for pretraining (100B tokens) and WikiText for validation purposes.

- **Evaluation Metrics:** Metrics include zero-shot accuracy across tasks such as ARC-Easy, HellaSwag, and LAMBADA, while inference efficiency is measured in FLOPS (Floating Point Operations Per Second).

- **Baseline Methods:** Models with SiLU and GELU are compared against the new ReLU models. Results show that models trained with ReLU achieve comparable performance at lower computational costs. 

Main results indicate significant reductions in FLOPS, where transitioning to ReLU yields efficiencies such as a decrease from 6.6G to 4.5G FLOPS, marking a cumulative efficacy gain of approximately 32%. An extensive table outlines the zero-shot accuracy and FLOPS usage across all evaluated models, revealing minimal performance loss post-relufication.

- **Ablation Study Findings:** Each stage of relufication significantly contributes to the overall computational benefits while preserving near-original performance levels. 

- **Computational Cost:** Notably fewer GPU hours are required for inference, with stark contrasts noted between the number of FLOPS across models before and after the relufication process.

### Discussion & Conclusion
The analysis provides strong evidence that ReLU activation not only sustains performance but significantly enhances inference efficiency through computed sparsity. The innovative relufication approach facilitates practical adaptation of existing models, enhancing usability on constrained computational resources. Future directions include further exploration of activation functions which obviate losses in performance while maximizing efficiency.

## Key Contributions
- Demonstrated ReLU's superiority in achieving activation sparsity, yielding significant computation savings.
- Developed a staged relufication process allowing adaptation of pretrained models without retraining from scratch.
- Introduced aggregated sparsity and its implications on improving inference speed, particularly in speculative decoding.

## Potential Relevance
This paper's exploration of ReLU's computational advantages and the relufication process may inform new hypotheses regarding architecture adaptations in LLMs. The findings on computational efficiency with minimal performance trade-off could drive further investigations into activation function optimization and architectural refinement in large-scale language models.