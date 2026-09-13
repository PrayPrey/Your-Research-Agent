---
source_paper: "arxiv_2401_09417.md"
generated_at: "2026-03-18T01:08:00.915215"
model: "gpt-4o-mini"
summary_chars: 6674
---

# Vision Mamba: Efficient Visual Representation Learning with Bidirectional State Space Model

## Key Metadata
- **Authors:** Lianghui Zhu et al.
- **Year:** 2024
- **Venue:** Proceedings of the 41st International Conference on Machine Learning
- **Core Contribution:** Introduction of Vision Mamba (Vim), a high-efficiency visual representation learning model using bidirectional state space models.

## Section Summaries

### Abstract
Recently the state space models (SSMs) with efficient hardware-aware designs, i.e., the Mamba deep learning model, have shown great potential for long sequence modeling. Meanwhile, building efficient and generic vision backbones purely upon SSMs is an appealing direction. How- ever, representing visual data is challenging for SSMs due to the position-sensitivity of visual data and the requirement of global context for visual understanding. In this paper, we show that the reliance on self-attention for visual representation learning is not necessary and propose a new generic vision backbone with bidirectional Mamba blocks (Vim), which marks the image sequences with position embeddings and compresses the visual representation with bidirectional state space models. On ImageNet classification, COCO object detection, and ADE20k semantic segmentation tasks, Vim achieves higher performance compared to well-established vision transformers like DeiT, while also demonstrating significantly improved computation & memory efficiency. For example, Vim is 2.8× faster than DeiT and saves 86.8% GPU memory when performing batch inference to extract features on images with a resolution of 1248×1248. The results demonstrate that Vim is capable of overcoming the computation & memory constraints on performing Transformer-style understanding for high-resolution images and it has great potential to be the next-generation backbone for vision foundation models. Code and models are released at https://github.com/hustvl/Vim

### Introduction & Motivation
Vision backbones traditionally rely on convolutional networks and Transformers; however, these approaches face limitations in high-resolution processing due to memory and computational costs. The authors propose Vision Mamba (Vim) that leverages bidirectional state space models for efficient visual representation learning without self-attention. This model allows for a more effective representation of visual data while retaining context. Vim seeks to bridge the efficiency-performance gap of current models, thereby enabling higher performance in vision tasks such as image classification and segmentation.

### Methodology
The core of the proposed model, Vim, integrates bidirectional selective state space modeling with positional embeddings for visual data. Vim processes images by first subdividing them into non-overlapping patches, transforming these into a sequence of tokens through linear projection, and then applying position embeddings to retain spatial awareness.

**Architecture Components:**
1. **Patch Extraction:** The image \( t \in \mathbb{R}^{H \times W \times C} \) is divided into \( J \) patches \( x_p \in \mathbb{R}^{J \times (P^2 \cdot C)} \).
2. **Token Sequence Initialization:** 
   \[
   T_0 = [t_{cls}; t_{1p}; t_{2p}; \ldots; t_{Jp}] + E_{pos}
   \]
   where \( W \in \mathbb{R}^{(P^2 \cdot C) \times D} \) is the linear projection matrix and \( E_{pos} \in \mathbb{R}^{(J+1) \times D} \) encompasses position embeddings.

3. **Vim Block Operations:** Each Vim block processes the token sequences \( T_{l-1} \) using operations defined in Algorithm 1, where tokens are normalized and projected into \( x \) and \( z \), followed by a concurrent forward and backward processing through SSM to generate \( T_l \). The parameters are updated via:
   \[
   y_{forward}, y_{backward} \leftarrow \text{SSM}(x_{forward}), \text{SSM}(x_{backward})
   \]
   followed by a gating mechanism and normalization to produce the output.

**Hyperparameters:**
- Number of Layers \( L \): 24 for both small and tiny variants.
- Hidden State Dimension \( D \): 192 for tiny, 384 for small.
- Expanded State Dimension \( E \): 384 for tiny, 768 for small.
- SSM Dimension \( N \): 16.
- Batch size: 1024.
- Optimizer: AdamW with a cosine scheduler starting at \( 1 \times 10^{-3} \).

### Experiments & Results
The experiments evaluate the model's performance on multiple datasets including ImageNet (1.28M training images), ADE20K for segmentation, and COCO for object detection. The main findings are summarized below:

1. **Image Classification (Table 1):** Vim demonstrated an accuracy of 80.3 on ImageNet, outpacing ResNet50 by 4.1 points and showing comparable performance to DeiT with significantly fewer parameters.
2. **Semantic Segmentation (Table 2):** On ADE20K, Vim achieved an mIoU of 44.9, outperforming DeiT with similar configurations (Vim-Ti: 39.2 mIoU).
3. **Object Detection (Table 3):** Vim-Ti surpassed DeiT-Ti by 1.3 in box AP and 1.1 in mask AP metrics, demonstrating its efficiency with high-resolution data.
4. **Efficiency:** Vim is 2.8× faster than DeiT and saves 86.8% GPU memory during batch inference on images sized 1248×1248. 

**Ablation Studies:** Conducted to assess the impact of key design choices including bidirectional SSM strategy and classification design, reinforcing the advantages of the bidirectional approach in performance across tasks.

### Discussion & Conclusion
Vim presents a promising alternative to conventional models in visual representation learning, effectively combining efficiency and accuracy without the reliance on self-attention based mechanisms. While it shows significant improvements in speed and memory usage, future work may explore its applicability in unsupervised tasks and multimodal applications, particularly in high-resolution image analyses.

## Key Contributions
- Introduction of Vision Mamba (Vim), a pure-SSM-based model optimizing visual representation learning without self-attention.
- Demonstration of superior performance and efficiency compared to existing models, particularly in high-resolution scenarios.
- Extensive benchmarking across standard datasets, affirming the potential of Vim as a next-generation backbone in vision tasks.

## Potential Relevance
The methodologies of Vim could inform future developments in lightweight, efficient visual models for high-resolution data processing, along with exploration into unsupervised and multimodal applications stemming from its sequence modeling capabilities. The findings demonstrate notable benchmarks which can aid in hypothesis formation regarding visual representation and processing efficiency in deep learning models.