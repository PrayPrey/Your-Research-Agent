---
source_paper: "arxiv_2406_09997.md"
generated_at: "2026-05-20T23:17:11.748310"
model: "gpt-4o-mini"
summary_chars: 6214
---

# Towards Scalable and Versatile Weight Space Learning (SANE)

## Key Metadata
- **Authors:** Konstantin Schürholt et al.
- **Year:** 2024
- **Venue:** Proceedings of the 41st International Conference on Machine Learning
- **Core Contribution:** Introduction of SANE, a method for learning task-agnostic neural network weight representations that scales effectively for larger models and varied architectures.

## Section Summaries

### Abstract
Learning representations of well-trained neural network models holds the promise to provide an understanding of the inner workings of those models. However, previous work has either faced limitations when processing larger networks or was task-specific to either discriminative or generative tasks. This paper introduces the SANE approach to weight-space learning. SANE overcomes previous limitations by learning task-agnostic representations of neural networks that are scalable to larger models of varying architectures and that show capabilities beyond a single task. Our method extends the idea of hyper-representations towards sequential processing of subsets of neural network weights, thus allowing one to embed larger neural networks as a set of tokens into the learned representation space. SANE reveals global model information from layer-wise embeddings, and it can sequentially generate unseen neural network models, which was unattainable with previous hyper-representation learning methods. Extensive empirical evaluation demonstrates that SANE matches or exceeds state-of-the-art performance on several weight representation learning benchmarks, particularly in initialization for new tasks and larger ResNet architectures.

### Introduction & Motivation
Exploring the "weight space" of neural networks offers insights into how these models operate. Traditional approaches have struggled with scalability for larger architectures and have focused exclusively on specific tasks, limiting their applicability. This paper presents SANE, which establishes a framework for task-agnostic weight representation learning capable of processing larger networks efficiently. By leveraging sequential processing of weight subsets, SANE allows for the generation of embeddings that encapsulate global model characteristics, thereby improving performance across discriminative and generative tasks.

### Methodology
SANE (Sequential Autoencoder for Neural Embeddings) introduces an architecture that learns from the weight space of neural networks through a two-part autoencoder that has a transformer backbone. The core algorithm works as follows:

1. The weights \( W \) of the neural network are flattened into a vector, which is then tokenized into smaller, manageable sequences based on layer-wise components.
2. The encoder \( g_\theta \) maps these sequences to lower-dimensional embeddings \( z \):
   \[
   z = g_\theta(T)
   \]
3. The decoder \( h_\psi \) reconstructs the weights from the embeddings:
   \[
   \hat{W} = h_\psi(z)
   \]
4. SANE utilizes a composite training loss, which combines reconstruction and contrastive losses:
   \[
   L = (1 - \gamma)L_{\text{rec}} + \gamma L_c
   \]
   where \( L_{\text{rec}} = \| W - \hat{W} \|^2_2 \) and the contrastive loss \( L_c \) is based on the normalized temperature-scaled cross-entropy loss.

Key hyperparameters include a window size \( ws \), global token size \( dt \), and training duration of 50 epochs. Models are pretrained on various datasets (with different architectures) and subsequently evaluated on tasks such as model initialization using learned representations. SANE can encode extremely large models like ResNet-101 by processing their weights in smaller, manageable subsets, thus enabling scalability.

### Experiments & Results
SANE's efficacy was assessed using diverse datasets, including MNIST, SVHN, CIFAR-10, and Tiny-ImageNet. Performance on discriminative tasks was measured using the accuracy \( Acc \), generalization gap \( Ggap \), and training epoch \( Ep \) for linear probing. The results demonstrated:

| Dataset       | Method                | Acc   | Ep     | Ggap   |
|---------------|-----------------------|-------|--------|--------|
| MNIST         | SANE                  | 0.978 | 0.402  | 0.246  |
| SVHN          | SANE                  | 0.991 | 0.930  | 0.479  |
| CIFAR-10      | SANE                  | 0.991 | 0.771  | 0.324  |
| CIFAR-100     | SANE                  | 0.992 | 0.879  | 0.500  |
| Tiny-ImageNet | SANE                  | 0.931 | 0.902  | 0.654  |

Additionally, SANE outperformed state-of-the-art methods notably in generative tasks by 25% in accuracy for new task initialization and 31% for finetuning. An ablation study revealed that processing weights in subsets significantly improved model performance over prior methods limited to entire vector encoding.

### Discussion & Conclusion
SANE provides a compelling advancement in weight representation learning, demonstrating that task-agnostic embeddings can be effectively generated for diverse models of varying architectures. Nevertheless, limitations include dependence on prompt examples for sampling, which may restrict its application in highly heterogeneous environments. Future work may explore broader architectures beyond computer vision tasks and develop sampling strategies that further reduce reliance on high-quality prompt examples.

## Key Contributions
- Introduction of SANE, enabling efficient and scalable weight representation learning for neural networks.
- Development of sequential processing methods that allow for encoding large models through manageable subsets.
- Demonstration of superior performance against existing methods, notably in model initialization and transfer tasks.

## Potential Relevance
As the paper outlines improvements in both discriminative and generative representation learning with SANE, these methods may offer useful insights for developing robust initialization strategies and sampling techniques in our research hypothesis discussions. The findings on performance scaling and the ability to transfer learning across architectures are particularly relevant for future exploration in model generalization and interpretability.