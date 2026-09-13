---
source_paper: "arxiv_2212_06254.md"
generated_at: "2026-03-19T21:48:38.897322"
model: "gpt-4o-mini"
summary_chars: 6373
---

# You Only Need a Good Embeddings Extractor to Fix Spurious Correlations

## Key Metadata
- **Authors:** Raghav Mehta et al.
- **Year:** 2022
- **Venue:** arXiv
- **Core Contribution:** Demonstrates that embeddings from large pre-trained vision models can effectively mitigate spurious correlations in data without using subgroup information.

## Section Summaries

### Abstract
Spurious correlations in training data often lead to robustness issues since models learn to use them as shortcuts. For example, when predicting whether an object is a cow, a model might learn to rely on its green background, so it would do poorly on a cow on a sandy background. A standard dataset for measuring state-of-the-art on methods mitigating this problem is Waterbirds. The best method (Group Distributionally Robust Optimization - GroupDRO) currently achieves 89% worst group accuracy and standard training from scratch on raw images only gets 72%. GroupDRO requires training a model in an end-to-end manner with subgroup labels. In this paper, we show that we can achieve up to 90% accuracy without using any subgroup information in the training set by simply using embeddings from a large pre-trained vision model extractor and training a linear classifier on top of it. With experiments on a wide range of pre-trained models and pre-training datasets, we show that the capacity of the pre-training model and the size of the pre-training dataset matters. Our experiments reveal that high capacity vision transformers perform better compared to high capacity convolutional neural networks, and larger pre-training datasets lead to better worst-group accuracy on the spurious correlation dataset.

### Introduction & Motivation
Spurious correlations in machine learning can lead to models relying on misleading features in data (e.g., background colors). The presence of these correlations hinders model performance on minority classes when tested on real-world data. Existing methods for addressing this problem often rely on subgroup labels, which can be unavailable or inaccurate. This paper proposes using frozen embeddings from large pre-trained networks and training linear classifiers on these embeddings as a robust alternative, with a focus on achieving high worst-group accuracy (WGA) in the Waterbirds dataset scenario, where misclassification is biased.

### Methodology
The proposed methodology employs embeddings from large pre-trained models (including convolutional networks like ResNets and RegNetYs, as well as Vision Transformers). The key steps involved are:

1. **Embedding Extraction**: Employ frozen models (ensuring they aren’t fine-tuned) to extract embeddings. Models trained on ImageNet and SWAG datasets are utilized to collect features.
  
2. **Classifier Training**: A linear classifier is trained on top of the extracted embeddings using Empirical Risk Minimization (ERM) with a cross-entropy loss:
   \[
   \mathcal{L} = -\frac{1}{N} \sum_{i=1}^N y_i \log(\hat{y}_i)
   \]
   where \( \hat{y}_i \) are the predicted probabilities for the true labels \( y_i \).

3. **Hyperparameters**: Grid search is performed over learning rates of 0.01, 0.001, and 0.0001, and weight decays of 0.0001, 0.00001, and 0.000001. The models are trained for 20 epochs using a batch size of 32.

4. **Data Preprocessing**: The Waterbirds dataset, containing 4,795 training images, is utilized. The dataset is split into four groups based on bird classifications and backgrounds, with a focus on achieving balanced performance across all subgroups.

5. **Model Evaluation**: Performance is measured using overall accuracy and worst-group accuracy to evaluate effectiveness against spurious correlations, with a particular focus on achieving WGA above existing benchmarks like GroupDRO.

### Experiments & Results
Experiments are conducted on the Waterbirds dataset, which consists of 4,795 images for training, 1,199 for validation, and 5,794 for testing. The dataset is split into four groups, including minority and majority representations. The evaluation metrics employed include overall accuracy and worst-group accuracy (WGA).

- **Model Comparisons**: The paper compares embedding extraction across different architectures (5 ResNets, 8 RegNetYs, and 4 ViTs) pre-trained on ImageNet and SWAG. It observes that higher capacity models perform better.
- **Results**: A maximum WGA of 90.13% was obtained using a ViT-H-14 pre-trained on SWAG, outperforming GroupDRO (89.2% WGA).
- **Timeliness**: The results achieved required no access to subgroup labels during training, which is a significant shift from existing methods.
  
| Model Type        | Pre-training Data | Worst Group Accuracy (%) | Overall Accuracy (%) |
|-------------------|-------------------|--------------------------|-----------------------|
| ViT-H-14          | SWAG + ImageNet   | 90.13                    | 92.00                 |
| ResNet-50         | ImageNet          | 88.50                    | 85.00                 |
| GroupDRO          | -                 | 89.20                    | -                     |

Additionally, various state-of-the-art methods including JTT, SSA, LfF, and EIIL were assessed, showing the proposed method's advantages in terms of efficiency and accuracy.

### Discussion & Conclusion
The findings indicate that high-capacity and well-pretrained models can effectively mitigate the issues related to spurious correlations. The absence of subgroup labels during training simplifies real-world applications. However, future work may focus on exploring more complex classifiers and additional regularization techniques to enhance performance further.

## Key Contributions
- Demonstrated a novel approach using frozen embeddings that eliminates the need for subgroup labels during training.
- Achieved a new state-of-the-art in worst-group accuracy on the Waterbirds dataset.
- Investigated the importance of model capacity and pre-training dataset size in improving classification robustness.

## Potential Relevance
The insights from this paper could inform hypotheses regarding the effectiveness of embedding strategies in handling spurious correlations in various datasets and domains. The techniques and findings might guide the development of more generalized approaches in supervised learning contexts where subgroup information is limited or unavailable.