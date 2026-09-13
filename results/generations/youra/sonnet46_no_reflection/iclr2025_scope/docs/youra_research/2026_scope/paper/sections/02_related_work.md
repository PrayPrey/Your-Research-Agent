# 2. Related Work

## 2.1 KV Cache Compression

KV cache management has emerged as a critical efficiency bottleneck as sequence lengths grow. Eviction-based methods like H2O [Zhang et al., 2023] and StreamingLLM [Xiao et al., 2024] use heuristic attention scores to identify expendable tokens. Locret [Huang et al., 2024] advances this by training lightweight retaining heads (two linear layers per transformer layer) to predict eviction scores via a language modeling objective, achieving up to 20× KV compression with minimal perplexity loss. PruLong [Princeton, 2024] learns binary attention head masks via similar training dynamics. More recent systems-oriented work (TailorKV [Yao et al., 2025], MCaM [Chu et al., 2025], KV Pareto [Gokhale et al., 2025]) addresses memory hierarchy and quantization-eviction tradeoffs.

A critical shared limitation runs through this entire line of work: **all eviction policies are trained with language modeling loss**, making them optimized for preserving next-token-predictive token patterns. When these methods are applied to task-specific fine-tuned models, their eviction priorities may be misaligned with what the task-adapted representations actually need. No prior work has measured this misalignment, nor addressed it directly.

## 2.2 Parameter-Efficient Fine-Tuning (PEFT)

LoRA [Hu et al., 2022] injects low-rank matrices (A·B) into transformer weight projections, enabling effective task adaptation with fewer than 1% of the model's parameters. QLoRA [Dettmers et al., 2023] extends this to quantized base models. Comprehensive surveys [Mao et al., 2024; Yang et al., 2024] catalogue the many LoRA variants. In the context of KV compression, PEFT methods are universally applied as a prior stage — fine-tune first, compress later — without consideration of whether the compression aligns with the fine-tuning objective.

The key gap is that LoRA adapters alter the model's internal representations and attention patterns to serve the downstream task, yet the KV eviction policy is never informed of this change. Our work proposes that both should be trained together.

## 2.3 Joint PEFT + KV Compression

The closest prior work to ours is arXiv 2604.21335 [2025], which introduces sub-token routing that combines LoRA routing paths with KV value-group routing in a unified architecture. This establishes architectural feasibility — LoRA and KV routing can coexist in a single model. However, two critical differences separate it from JointLoRA-KV: (1) it uses **language modeling loss** throughout, making it a next-token-prediction variant rather than a task-classification approach, and (2) it evaluates on perplexity and RULER (a long-context recall benchmark), with no evaluation on GLUE or LongBench classification benchmarks.

The amazon-science/icr-kv-caching work [Molfese et al., EACL 2026] examines how SFT and RL fine-tuning affect KV compression robustness, finding moderate robustness with task-dependent variation. This is the most closely related applied work, but it does not propose joint training — it analyzes the interaction post-hoc.

NVIDIA's kvpress library [2024] implements forward-hook KV compression combinable with PEFT fine-tuned models but does not train the eviction components jointly with the adapter. The Efficient Compressing + Tuning survey [Kim et al., 2025] explicitly identifies the lack of unified compression+tuning frameworks as a key open problem.

**Our position:** JointLoRA-KV is the first method to jointly optimize LoRA adapter weights and KV eviction head weights via a task classification loss, and the first to measure the misalignment that motivates this approach on standard NLP benchmarks (GLUE, LongBench).

## 2.4 Differentiable Sparse Selection

The soft-to-hard training pattern we employ in JointLoRA-KV — sigmoid relaxation during training, hard discrete selection at inference — is established in the sparse learning literature. Locret itself uses soft scoring during training; PruLong employs a related mask-learning approach. Straight-through estimators (STE) [Bengio et al., 2013] provide the gradient bridge through hard discrete operations and have been widely used in quantization-aware training and binary neural networks. Our contribution is applying this pattern to the joint LoRA+KV eviction training problem with a task classification objective.
