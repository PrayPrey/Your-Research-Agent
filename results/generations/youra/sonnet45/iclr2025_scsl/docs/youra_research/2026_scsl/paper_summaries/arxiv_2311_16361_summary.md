---
source_paper: "arxiv_2311_16361.md"
generated_at: "2026-03-19T21:48:59.090265"
model: "gpt-4o-mini"
summary_chars: 7335
---

# Making Self-supervised Learning Robust to Spurious Correlation via Learning-speed Aware Sampling

## Key Metadata
- **Authors:** Weicheng Zhu et al.
- **Year:** 2023
- **Venue:** arXiv
- **Core Contribution:** Introduction of Learning-speed Aware Self-supervised Learning (LA-SSL) to improve robustness against spurious correlations in self-supervised learning.

## Section Summaries

### Abstract
Self-supervised learning (SSL) has emerged as a powerful technique for learning rich representations from unlabeled data. The data representations are able to capture many underlying attributes of data, and are useful in downstream prediction tasks. In real-world settings, spurious correlations between some attributes (e.g. race, gender, and age) and labels for downstream tasks often exist, e.g. cancer is usually more prevalent among elderly patients. In this paper, we investigate SSL in the presence of spurious correlations and show that the SSL training loss can be minimized by capturing only a subset of conspicuous features relevant to those sensitive attributes, despite the presence of other important predictive features for the downstream tasks. To address this issue, we investigate the learning dynamics of SSL and observe that the learning is slower for samples that conflict with such correlations (e.g. elder patients without cancer). Motivated by these findings, we propose a learning-speed aware SSL (LA-SSL) approach, in which we sample each training data with a probability that is inversely related to its learning speed. We evaluate LA-SSL on three datasets that exhibit spurious correlations between different attributes, demonstrating that it improves the robustness of pretrained representations on downstream classification tasks.

### Introduction & Motivation
The study addresses the problem of spurious correlations that can bias self-supervised learning (SSL) by causing models to identify shortcuts to labels instead of understanding causal relationships. These biases are particularly concerning in contexts such as healthcare, where correlations may reflect not causal relationships but imbalanced data distributions. Prior methods aimed at mitigating such biases either require strong prior knowledge about attributes or rely on labels not available during SSL. The authors propose learning-speed aware sampling (LA-SSL), which leverages the observed differences in learning speeds among data samples affected by these correlations to enhance the robustness of SSL without needing label information.

### Methodology
The proposed LA-SSL introduces a novel sampling strategy integrated into a standard SSL framework (here, SimCLR). The core mechanism involves dynamically adjusting the sampling probability for each training example based on its learning speed, which reflects how quickly representations are learned during training. Samples that conflict with spurious correlations are learned more slowly, therefore are upsampled to enforce better learning of discriminative features.

1. **Core Algorithm:** LA-SSL modifies sampling probabilities inversely related to learning speed:
   \[
   \pi_i = h(s_i) / \sum_{j=1}^{n} h(s_j)
   \]
   where \(s_i\) is the learning speed for sample \(i\).

2. **Model Architecture:** Based on SimCLR with ResNet-50 as the backbone for representation learning. The model employs a two-branch architecture where augmented views are compared.

3. **Hyperparameters:** \(s^*\) thresholds are selected from the learning speeds, with specific hyperparameters for updating probabilities based on a linear scaling function. The constant \( \gamma \) controls the margin of disparities.

4. **Training Procedure:** Utilizes InfoNCE loss:
   \[
   L_{LA-SSL} = -E_{k} \left[ \log \left( \frac{\text{sim}(x^{aug}_1, x^{aug}_2)}{\text{sim}(x^{aug}_1, x^{aug}_2) + \sum_{i=2}^{b} \text{sim}(x^{aug}_1, x_i)} \right) \right]
   \]
   A warm-up period ensures the network has learned some features before adjusting sampling rates based on learning speeds.

5. **Input/Output:** The input consists of unlabeled images, and the output is a learned representation used for classification tasks downstream.

6. **Novel Components:** The integration of learning speed as a proxy for the relevance of samples relative to spurious correlations is a novel approach not utilized in previous SSL frameworks.

### Experiments & Results
The experiments evaluate LA-SSL over three datasets with spurious correlations, specifically Corrupted CIFAR-10, CelebA, and MIMIC-CXR.

- **Datasets:**
  - **Corrupted CIFAR-10:** 60,000 images with various noise types simulating spurious correlation.
  - **CelebA:** 202,599 images where hair color is correlated with gender, emphasizing imbalanced representation.
  - **MIMIC-CXR:** 377,110 chest X-ray images capturing correlations between age and health findings.

- **Evaluation Metrics:** Accuracy, precision, recall, and AUC for downstream tasks like object classification and medical diagnosis.

- **Baseline Comparison:** Models with uniform random sampling demonstrated lower performance across datasets due to susceptibility to spurious correlations. Notably, LA-SSL showcased relative improvements ranging from 5.13% to 10.63% across varying correlation levels.

- **Key Result Summary (Test Accuracy on CIFAR-10):**
  | Method       | 95% Correlation | 98% Correlation | 99% Correlation | 99.5% Correlation |
  |--------------|-----------------|-----------------|-----------------|-------------------|
  | SimCLR       | 44.08%          | 48.02%          | 36.60%          | 29.74%            |
  | **LA-SSL**   | **52.79%**      | **54.73%**      | **40.49%**      | **31.55%**        |

- **Ablation Study Findings:** Demonstrated that LA-SSL effectively mitigates biases by upsampling correlation-conflict samples, resulting in enhanced representation discrimination.

### Discussion & Conclusion
LA-SSL effectively addresses biases introduced by spurious correlations in SSL training. It outperforms standard sampling techniques while providing robust representations across various datasets. Limitations include the reliance on learning speeds, which may not universally translate across all datasets, and future work may explore further integration of context-aware sampling or additional feature learning strategies.

## Key Contributions
- Introduced LA-SSL, a novel sampling method that dynamically adjusts training sample probabilities based on learning speed to mitigate spurious correlations.
- Successfully demonstrated improvements in representation learning and downstream performance across multiple datasets with inherent spurious correlations.
- Contributed to a broader understanding of the impact of learning dynamics in SSL, providing a pathway for future developments in robust representation learning.

## Potential Relevance
The methodologies developed in this paper can significantly impact our understanding of how to effectively sample within SSL frameworks. Key findings on learning dynamics could inform the design of experiments aimed at addressing confounding variables in model training, especially in sensitive applications like healthcare. Using learning speed as a metric for sampling presents an innovative approach to improving model robustness that could be further explored in future research.