---
source_paper: "arxiv_2410_04209.md"
generated_at: "2026-05-20T23:18:23.673606"
model: "gpt-4o-mini"
summary_chars: 7387
---

# Equivariant NFNs for Transformers

## Key Metadata
- **Authors:** Viet-Hoang Tran et al.
- **Year:** 2025
- **Venue:** ICLR
- **Core Contribution:** The paper presents a systematic study on neural functional networks (NFNs) for transformer architectures, introducing Transformer-NFN, an equivariant approach, and releasing the Small Transformer Zoo dataset.

## Section Summaries

### Abstract
This paper systematically explores neural functional networks (NFN) for transformer architectures. NFN are specialized neural networks that treat the weights, gradients, or sparsity patterns of a deep neural network (DNN) as input data and have proven valuable for tasks like learnable optimizers, implicit data representations, and weight editing. While NFN have been extensively developed for MLP and CNN, no prior work has addressed their design for transformers, despite their importance in modern deep learning. This paper aims to address this gap by systematically studying NFN for transformers. We first determine the maximal symmetric group of the weights in a multi-head attention module and a necessary and sufficient condition under which two sets of hyperparameters of the module define the same function. We then define the weight space of transformer architectures and its associated group action, leading to design principles for NFN in transformers. Based on these, we introduce Transformer-NFN, an NFN equivariant under this group action. Additionally, we release a dataset of over 125,000 Transformers model checkpoints trained on two datasets with two tasks, providing a benchmark for evaluating Transformer-NFN and encouraging further research on transformer training and performance. The code is publicly available at https://github.com/MathematicalAI-NUS/Transformer-NFN.

### Introduction & Motivation
Neural functional networks (NFNs) utilize the structure of deep neural networks (DNNs) by treating their weights and gradients as input. Despite NFNs being effectively developed for various architectures, there is a notable gap in their adaptation for transformer networks, which dominate modern applications in NLP and beyond. The authors highlight that developing NFNs for transformers is essential for improving model understanding, generalization prediction, and optimizing training processes.

### Methodology
The core technique introduced in this paper is **Transformer-NFN**, an NFN specifically designed for transformer architectures. The major steps of the methodology include:

1. **Establishing Maximal Symmetric Group**: The authors define the maximal symmetric group of weights in a multi-head attention (MHA) module. They derive necessary and sufficient conditions under which two settings of hyperparameters define the same MHA function.

   The MHA is formalized as:
   \[
   \text{MultiHead}(X; W^{(O)}, \{W^{(Q,i)}, W^{(K,i)}, W^{(V,i)}\}_{i=1}^{h}) = W^{(O)} \cdot \text{concat}(\text{Head}(X; W^{(Q,i)}, W^{(K,i)}, W^{(V,i)})_{i=1}^{h})
   \]

2. **Defining Weight Space**: The authors construct a weight space \( U \) for a standard transformer block, including the layers for MHA and feedforward networks. The weights of the transformer block can be described as:
   \[
   U = \left( \prod_{i=1}^{h} (W^{(Q,i)}, W^{(K,i)}, W^{(V,i)}, W^{(O,i)}) \right) \times (W^{(A)}, W^{(B)}) \times (b^{(A)}, b^{(B)})
   \]

3. **Group Action**: A group \( G_U \) that describes the symmetries of the weight space is introduced, incorporating permutations and transformations related to the MHA:
   \[
   G_U = S_h \times GL_{D_k}(R)^h \times GL_{D_v}(R)^h \times PD \times PD_{A}
   \]

4. **Designing Transformer-NFN**: Utilizes equivariant polynomial layers that maintain performance and generalization by leveraging the described group \( G_U \). The polynomial mapping \( I: U \to R^{D'} \) is constructed to take this equivariance and express polynomial relationships among weights.

   The polynomial expression is given by:
   \[
   I(U) = \sum_{s=1}^{h} \Phi(QK,s) \cdot [W_{QK,s}] + \sum_{s=1}^{h} \Phi(VO,s) \cdot [W_{VO,s}] + \ldots
   \]

5. **Dataset Creation**: The authors introduce the **Small Transformer Zoo**, comprising over 125,000 checkpoints derived from transformers trained on MNIST (digit image classification) and AGNews (text classification).

Key hyperparameters for training include a learning rate of 1e-4, batch sizes of 32 or 64, and multiple training epochs adapted to task specifics.

### Experiments & Results
1. **Datasets**: The MNIST-Transformers dataset includes 62,756 models trained for digit recognition, while AGNews-Transformers consists of 63,796 models focusing on text classification. Both datasets facilitate extensive evaluation of Transformer-NFN.

2. **Evaluation Metrics**: The experiments primarily use **Kendall’s τ** for assessing model performance. This metric ranges from -1 (no correlation) to 1 (perfect correlation), indicating how closely predicted accuracies align with ground truth values.

3. **Baseline Methods**: Various standard models were evaluated against Transformer-NFN, including MLPs, STATNN, XGBoost, LightGBM, and Random Forest.

4. **Main Results**: Transformer-NFN significantly outperformed baseline models across various accuracy thresholds and datasets, achieving scores up to:
   - **MNIST Dataset**: Up to 0.905 Kendall’s τ
   - **AGNews Dataset**: Up to 0.910 Kendall’s τ

   | Dataset                | Model            | Kendall’s τ      |
   |-----------------------|------------------|------------------|
   | MNIST-Transformers    | Transformer-NFN  | 0.905 ± 0.002    |
   | AGNews-Transformers    | Transformer-NFN  | 0.910 ± 0.001    |

5. **Ablation Study**: The authors demonstrated that the structure of the NFN crucially impacts performance; notably, the transformer block alone yields a high correlation (0.902) to model generalization for MNIST.

6. **Cost and Efficiency**: The overall computational expense includes GPU hours for training and extensive usage assessments within both dataset settings, though specific numbers were not disclosed in the paper.

### Discussion & Conclusion
The authors established that Transformer-NFN effectively utilizes weight structures for improved model predictions, revealing that weights from transformer architectures contain substantial information that may predict performance efficiently. They acknowledge some limitations regarding potential unexplored symmetries and the compact settings needed for optimal results. Future research directions include expanding NFNs with richer equivariance properties and exploring their applications in other architectures beyond transformers.

## Key Contributions
- Introduced Transformer-NFN, an equivariant NFN for transformers leveraging maximal symmetric groups.
- Released the Small Transformer Zoo dataset, aiding extensive evaluation of transformer architectures.
- Established a theoretical framework linking weight symmetries and equivariance, enhancing transformer model interpretability and performance prediction.

## Potential Relevance
The methodology and findings from this paper could significantly enrich the development of novel methods for hypothesizing performance indicators in transformer models. The insights on equivariance and the released dataset might facilitate further exploration of weight dynamics and optimizations in model training processes.