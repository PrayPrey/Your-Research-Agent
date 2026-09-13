---
source_paper: "arxiv_2408_14690.md"
generated_at: "2026-05-08T06:00:08.468098"
model: "gpt-4o-mini"
summary_chars: 5951
---

# Training-Free Activation Sparsity in Large Language Models

## Key Metadata
- **Authors:** James Liu et al.
- **Year:** 2025
- **Venue:** ICLR
- **Core Contribution:** TEAL, a training-free approach to achieve activation sparsity in large language models, achieving 40-50% sparsity with minimal performance degradation across several models.

## Section Summaries

### Abstract
Activation sparsity can enable practical inference speedups in large language models (LLMs) by reducing the compute and memory-movement required for matrix multiplications during the forward pass. However, existing methods face limitations that inhibit widespread adoption. Some approaches are tailored towards older models with ReLU-based sparsity, while others require extensive continued pre-training on up to hundreds of billions of tokens. This paper describes TEAL (Training-Free Activation Sparsity in LLMs), a simple training-free method that applies magnitude-based activation sparsity to hidden states throughout the entire model. TEAL achieves 40-50% model-wide sparsity with minimal performance degradation across Llama-2, Llama-3, and Mistral families, with sizes varying from 7B to 70B. We improve existing sparse kernels and demonstrate wall-clock decoding speed-ups of up to 1.53× and 1.8× at 40% and 50% model-wide sparsity. TEAL is compatible with weight quantization, enabling further efficiency gains.

### Introduction & Motivation
Large language models (LLMs) have shown that scaling both parameters and training data yields significant capabilities for various tasks. However, their high parameter counts result in memory-bound inference challenges, primarily hindering the transfer of weights between off-chip and on-chip memory. While methods such as weight quantization and sparsification have emerged to address this, limitations exist for modern LLM architectures—they struggle with activation sparsity due to non-ReLU activations and require costly pre-training to regain sparsity. TEAL introduces a magnitude-based pruning approach that achieves input-dependent sparsity efficiently across various LLM architectures without necessitating extensive retraining.

### Methodology
TEAL employs magnitude-based activation sparsity across the entire model with a focus on enhancing practical inference speeds. The core algorithm involves applying a sparsification function \( s_{tp} \) to hidden activations, defined as:
\[
s_{tp}(x_i) = 
\begin{cases} 
0 & \text{if } |x_i| \leq t_p \\
x_i & \text{otherwise}
\end{cases}
\]
where \( t_p \) is determined empirically based on the distribution of activations. The method characterizes each layer's sparsity level, with a total configuration denoted as \( p = (p_1, ..., p_N) \) for \( N \) matrices in the model. The forward pass is then computed using the sparsified activations:
\[
\hat{Y} = s_{tp_i}(x) W_i^\top
\]
where each matrix \( W_i \) undergoes layer-level sparsification throughout the Transformer blocks.

Hyperparameters include:
- Learning rate: Not applicable (training-free).
- Batch size: Not explicitly specified.
- Evaluation epochs: Depends on specific tasks evaluated.

TEAL utilizes a block-wise greedy optimization method, incrementing sparsity in matrices based on their memory footprint and minimizing the L2 activation error. The forward pass complexity reaches \( O(M n^2 \alpha) \), which in practice results in about 9800 forward passes, amounting to less than one GPU-hour on an A100 for Llama-3-8B.

To achieve speed-ups, a specialized sparse GEMV kernel is developed, utilizing memory formats to maximize coalescing and reduce computation overhead. 

### Experiments & Results
TEAL is evaluated on the Mistral, Llama-2, and Llama-3 families across various tasks, including language modeling on WikiText and six aggregative downstream tasks using EleutherAI LM Harness. The models and datasets used span sizes from 7B to 70B parameters, with results summarized in compact tables. 

Baseline methods include CATS (Lee et al., 2024a) for contrast. The results indicate:
- Perplexity metrics reveal minor degradation at 25% sparsity and modest degradation at 40-50% sparsity across models (Table 1).
- Overall accuracy results (Table 2) show TEAL outperforming CATS at 25% and 40% sparsity, with particular emphasis on the lower error rates attributed to TEAL’s approach of input sparsity versus CATS' output sparsity.
- Single-batch inference speed results highlight decoding speed-ups with TEAL, achieving up to 1.53x and 1.8x at 40% and 50% sparsity (Table 3).
- Variations with quantization indicate compatibility, enabling further efficiency improvements, confirmed through perplexity evaluations across different bit-width encodings.

### Discussion & Conclusion
TEAL offers a significant advancement in achieving activation sparsity for LLM inference with minimal performance trade-offs, realizing up to 50% model-wide sparsity effectively. Although the technique excels in low-batch settings, challenges persist in scaling up to larger batch sizes, indicating a potential area for further research. TEAL's enhancements in kernel efficiency and compatibility with quantization demonstrate promising avenues for improving inference in resource-constrained settings.

## Key Contributions
- Introduction of TEAL, a training-free method to achieve 40-50% activation sparsity in LLMs.
- Implementation of a specialized kernel for enhanced efficiency during inference.
- Compatibility with weight quantization techniques for increased performance.

## Potential Relevance
This paper's methodology on achieving activation sparsity without extensive retraining can inform hypothesis development regarding the optimization of LLM inference, particularly in scenarios where resource efficiency is crucial. Results and techniques pertinent to compatibility with quantization also open pathways for future experiments on model efficiency trades in large-scale applications.