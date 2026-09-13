---
source_paper: "arxiv_2204_02937.md"
generated_at: "2026-03-16T20:42:09.724130"
model: "gpt-4o-mini"
summary_chars: 5822
---

# Last Layer Re-Training (DFR)

## Key Metadata
- **Authors:** Polina Kirichenko et al.
- **Year:** 2023
- **Venue:** ICLR
- **Core Contribution:** Introduced Deep Feature Reweighting (DFR) as a method to enhance neural network robustness to spurious correlations by retraining only the last layer, achieving state-of-the-art performance with lower computational costs.

## Section Summaries

### Abstract
Neural network classifiers can largely rely on simple spurious features, such as backgrounds, to make predictions. However, even in these cases, we show that they still often learn core features associated with the desired attributes of the data, contrary to recent findings. Inspired by this insight, we demonstrate that simple last layer retraining can match or outperform state-of-the-art approaches on spurious correlation benchmarks, but with profoundly lower complexity and computational expenses. Moreover, we show that last layer retraining on large ImageNet-trained models can also significantly reduce reliance on background and texture information, improving robustness to covariate shift, after only minutes of training on a single GPU.

### Introduction & Motivation
Spurious correlations in deep learning datasets can mislead classifiers by causing reliance on irrelevant features, leading to performance drops when these correlations do not hold in test data. This paper addresses the need for understanding which features are learned by models in such contexts and proposes an effective solution for improving neural network robustness using a simple last layer retraining method. The aim is to enhance accuracy on minority groups in datasets, where spurious correlations often cause prediction errors.

### Methodology
The proposed method, Deep Feature Reweighting (DFR), involves a two-stage training process. 

1. **Initial Training:**
   - A base neural network model is trained using standard Empirical Risk Minimization (ERM) on the entire training dataset \( D \).
   - \( D \) contains multiple groups, each defined by a label and a spurious attribute.

2. **Last Layer Retraining:**
   - After initial training, the last classification layer of the network is replaced and retrained using a small reweighting dataset \( \hat{D} \), where the distribution of groups is balanced, allowing focus on core attributes relevant to the prediction task.
   - The model's output logits \( z_i \) are defined as \( z_i = W^T h(x) \), where \( h(x) \) is the learned feature representation.

This approach is computationally efficient and straightforward, relying on a single hyperparameter for regularization. DFR can be trained on a variety of architectures, including convolutional networks and transformers, enabling it to maintain high performance while being inexpensive in terms of computation time (a few minutes on a single GPU).

### Experiments & Results
The efficacy of DFR was evaluated across several datasets with spurious correlations, including Waterbirds, CelebA, MultiNLI, and CivilComments. 

- **Datasets:**
  - **Waterbirds:** Contains 4 groups with significant class imbalance, emphasizing background correlation.
  - **CelebA:** Focused on hair color predictions, where gender acts as a spurious feature.
  - **MultiNLI:** A text classification task affected by negation words.
  - **CivilComments:** Classifying comments based on nuanced attributes.
  
- **Baselines:** DFR was compared against methods including:
  - **Empirical Risk Minimization (ERM)**
  - **Group DRO**, which uses group information for training.
  - **Just Train Twice (JTT)**, and others.

The results demonstrated that DFR consistently outperformed or matched state-of-the-art methods in worst-group and mean accuracy, effectively balancing performance across underrepresented groups while reducing reliance on spurious features. An ablation study confirmed that retraining the last layer significantly enhances worst-group performance without retraining the entire model.

| Method        | Waterbirds Worst (%) | CelebA Worst (%) | MultiNLI Worst (%) | CivilComments Worst (%) |
|---------------|----------------------|------------------|---------------------|-------------------------|
| JTT           | 86.7                 | 81.1             | 72.6                | 69.3                    |
| Group DRO     | 91.4                 | 88.9             | 77.7                | 69.9                    |
| DFR           | 92.9                 | 88.3             | 78.6                | 70.1                    |

### Discussion & Conclusion
The findings indicate that standard neural networks retain the capacity to learn core features despite relying on spurious correlations for predictions. Last layer retraining through DFR effectively reallocates the model's reliance toward relevant features, greatly enhancing the worst-group accuracy and overall robustness. The approach offers a practical, low-computation alternative to existing methods that require extensive retraining or complex data handling.

## Key Contributions
- Introduction of Deep Feature Reweighting (DFR) as a method to enhance robustness against spurious correlations.
- Demonstrated that retraining only the last layer can maintain or exceed state-of-the-art performance while being computationally efficient.
- Analysis of learned feature representations in the context of spurious correlations, challenging previous assumptions.

## Potential Relevance
The methodologies and findings presented in this paper can inform future research hypotheses regarding robust feature learning in deep neural networks. The straightforward implementation of DFR provides a compelling framework for developing and testing interventions aimed at improving model accuracy in the face of spurious correlations, especially in imbalanced datasets.