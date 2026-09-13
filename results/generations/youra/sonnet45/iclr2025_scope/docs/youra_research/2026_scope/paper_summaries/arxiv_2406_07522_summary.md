---
source_paper: "arxiv_2406_07522.md"
generated_at: "2026-03-18T01:09:06.946313"
model: "gpt-4o-mini"
summary_chars: 6297
---

# Samba: Simple Hybrid State Space Models for Efficient Unlimited Context Language Modeling

## Key Metadata
- **Authors:** Liliang Ren et al.
- **Year:** 2025
- **Venue:** ICLR 2025
- **Core Contribution:** Introduction of the SAMBA architecture, a hybrid model that efficiently combines State Space Models and Sliding Window Attention for improved language modeling over arbitrary context lengths.

## Section Summaries

### Abstract
Efficiently modeling sequences with infinite context length has long been a challenging problem. Previous approaches have either suffered from quadratic computational complexity or limited extrapolation ability in length generalization. In this work, we present SAMBA, a simple hybrid architecture that layer-wise combines Mamba, a selective State Space Model (SSM), with Sliding Window Attention (SWA). SAMBA selectively compresses a given sequence into recurrent hidden states while still maintaining the ability to precisely recall recent memories with the attention mechanism. We scale SAMBA up to 3.8B parameters with 3.2T training tokens and demonstrate that it significantly outperforms state-of-the-art models across a variety of benchmarks. Pretrained on sequences of 4K length, SAMBA shows improved perplexity in context lengths of up to 1M in zero-shot. When finetuned on 4K-length sequences, SAMBA efficiently extrapolates to a 256K context length with perfect memory recall on the Passkey Retrieval task and exhibits superior retrieval extrapolation on the challenging Phonebook task compared to full-attention models. As a linear-time sequence model, SAMBA achieves a 3.73× higher throughput compared to Transformers with grouped-query attention for user prompts of 128K length, and a 3.64× speedup when generating 64K tokens with unlimited streaming. Our code for training on open source data is publicly available at https://github.com/microsoft/Samba.

### Introduction & Motivation
Current attention-based models, while effective for capturing long-term dependencies in large language tasks, struggle with quadratic complexity and poor extrapolation for long sequences. State Space Models (SSMs) offer linear complexity but are less effective for memory recall in longer contexts. Previous attempts to hybridize SSMs with attention have not shown significant performance improvements compared to Transformers. This paper introduces SAMBA, a hybrid architecture that combines SSMs with attention mechanisms, aiming to maintain linear complexity while enhancing the memory recall capabilities, making it suitable for unlimited context language modeling.

### Methodology
SAMBA employs a hybrid architecture that integrates Mamba (a selective SSM) with Sliding Window Attention (SWA) and Multi-Layer Perceptrons (MLPs). The architecture consists of configurations that interleave different layers:

1. **Mamba Layer:** Expands input sequence representations \( X \in \mathbb{R}^{n \times d_m} \) using a learnable projection matrix \( W_{in} \) into a higher dimension \( H \), then applies a Short Convolution (SC) operator to smooth the input.

   \[
   U = SC(H) = SiLU(DepthwiseConv(H, W_{conv}))
   \]
   
   A selective gating mechanism is introduced using a low-rank projection and the Softplus activation function:
   
   \[
   \Delta = Softplus(U W_r W_q + b)
   \]

   where the output of the selective state space model is computed through:
   
   \[
   Z_t = exp(-\Delta_t \odot exp(A)) \odot Z_{t-1} + \Delta_t \odot (B_t \otimes U_t)
   \]
   
   \[
   Y_t = Z_t C_t + D \odot U_t
   \]

2. **SWA Layer:** Implements local attention with a fixed window size of 2048, ensuring linear complexity by enabling efficient access to a context window. Utilizing Rotatory Positional Embeddings (RoPE), SWA enhances signal retrieval capabilities from the model’s memory.

3. **MLP Layer:** Employs SwiGLU activation functions for nonlinear transformations linked to the hybrid architecture. 

Key hyperparameters include model sizes of 421M, 1.3B, 1.7B, and 3.8B, a learning rate of \( 5e^{-5} \), and a batch size of 1024. SAMBA implements a multi-phase pretraining strategy across 3.2 trillion tokens.

### Experiments & Results
SAMBA was evaluated across various datasets, including ARC, MMLU, and GSM8K, focusing on both short and long-context scenarios. The models demonstrated:

- A comparative performance table (Table 1) showcases that the 3.8B SAMBA model outperforms the Phi-3-mini, achieving 71.9 on MMLU and 87.6 on GSM8K.
- An ablation study revealed that SAMBA consistently surpasses both pure attention-based and SSM-based models, confirming the utility of its hybrid design for tasks demanding long-term memory and comprehension.
- SAMBA achieved a perplexity reduction in very long context scenarios (up to 1M) and exhibited lower computational costs, with 3.73× higher throughput compared to traditional transformers.

### Discussion & Conclusion
The results indicate that SAMBA effectively combines the strengths of both attention-based mechanisms and recurrent structures, achieving notable efficiency in processing long sequences while maintaining high accuracy in language understanding tasks. Limitations include the need for further exploration of its zero-shot performance and its transferability of learning across different long-context tasks. Future work will investigate optimizing memory recall and processing strategies even further.

## Key Contributions
- Introduced a novel hybrid architecture (SAMBA) that achieves linear complexity while integrating SSMs with attention mechanisms.
- Demonstrated improved performance in contexts of arbitrary length over state-of-the-art models, along with a processing efficiency advantage.
- Provided insights into architectural design through extensive ablation studies and performance evaluations across various language modeling tasks.

## Potential Relevance
The SAMBA architecture's hybridization approach may provide promising methods for addressing length generalization in language models, making it a potential framework for developing more efficient models that can handle extensive inputs in real-world applications. Its findings related to throughput and complexity metrics may inform future hypothesizing in building scalable and performant language models.