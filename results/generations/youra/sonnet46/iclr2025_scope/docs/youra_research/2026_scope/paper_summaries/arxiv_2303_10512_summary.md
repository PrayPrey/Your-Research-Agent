---
source_paper: "arxiv_2303_10512.md"
generated_at: "2026-05-08T05:58:49.603979"
model: "gpt-4o-mini"
summary_chars: 7213
---

# AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning

## Key Metadata
- **Authors:** Qingru Zhang et al.
- **Year:** 2023
- **Venue:** ICLR 2023
- **Core Contribution:** Introduction of AdaLoRA, a method for adaptive parameter budget allocation during fine-tuning of large pre-trained models, enhancing performance especially in low-budget settings.

## Section Summaries

### Abstract
Fine-tuning large pre-trained language models on downstream tasks has become an important paradigm in NLP. However, common practice fine-tunes all of the parameters in a pre-trained model, which becomes prohibitive when a large number of downstream tasks are present. Therefore, many fine-tuning methods are proposed to learn incremental updates of pre-trained weights in a parameter efficient way, e.g., low-rank increments. These methods often evenly distribute the budget of incremental updates across all pre-trained weight matrices, and overlook the varying importance of different weight parameters. As a consequence, the fine-tuning performance is suboptimal. To bridge this gap, we propose AdaLoRA, which adaptively allocates the parameter budget among weight matrices according to their importance score. In particular, AdaLoRA parameterizes the incremental updates in the form of singular value decomposition. Such a novel approach allows us to effectively prune the singular values of unimportant updates, which is essentially to reduce their parameter budget but circumvent intensive exact SVD computations. We conduct extensive experiments with several pre-trained models on natural language processing, question answering, and natural language generation to validate the effectiveness of AdaLoRA. Results demonstrate that AdaLoRA manifests notable improvement over baselines, especially in the low budget settings. Our code is publicly available at https://github.com/QingruZhang/AdaLoRA.

### Introduction & Motivation
With the growing use of pre-trained language models (PLMs) in natural language processing tasks, the challenge of fine-tuning these models efficiently has become apparent. Common practices, such as full fine-tuning of all parameters, lead to excessive memory demands, especially when handling multiple tasks simultaneously. Existing methods like adapter tuning and LoRA seek to minimize fine-tuning parameters or add modular components, but they often do not consider the varying importance of different weights across tasks. This paper introduces AdaLoRA to address these issues by adaptively allocating parameter budgets based on the significance of the weights involved, ensuring improved model performance under tighter resource constraints.

### Methodology
**Core Algorithm:** AdaLoRA adapts the rank of incremental matrices during the fine-tuning of PLMs. The method initializes the updates for weight matrices \(\Delta\) as:

\[
W = W^{(0)} + \Delta = W^{(0)} + P \Lambda Q,
\]

where \( \Lambda \) is a diagonal matrix containing singular values, and \( P \) and \( Q \) are orthogonal matrices representing the singular vectors. This parameterization allows for effective pruning of the singular values of \(\Delta\), which is crucial for controlling the tuning budget.

**Model Architecture:** AdaLoRA is implemented on transformer-based architectures, applying SVD-based adaptation to the query, key, value, and feed-forward weight matrices across each transformer layer.

**Key Hyperparameters:** 
- Learning rate: \(1 \times 10^{-4}\)
- Batch size: 16
- Maximum epochs: 15
- Regularization parameter \( \gamma \): evaluated, typical values found to yield good performance.
- Initial and target budget defined through heuristic tuning to ensure efficient dimensional allocation.

**Training Procedure:**
- Optimizer: AdamW.
- Loss Function: Cross-entropy for classification tasks.
- The global budget scheduler starts with an initial budget slightly above the final target and reduces it over training iterations.
  
**Importance Scoring:** A novel importance metric computes the importance of singular values, integrating sensitivity-based assessments to account for the contribution of each weight in the context of task performance. The singular value updates are pruned based on calculated importance scores during training, ensuring that more relevant weights receive a larger share of the parameter budget.

### Experiments & Results
**Datasets:** 
- **Natural Language Understanding**: GLUE (General Language Understanding Evaluation) benchmark.
- **Question Answering**: SQuAD v1.1 and v2.0 datasets.
- **Natural Language Generation**: XSum and CNN/DailyMail datasets.

**Evaluation Metrics:**
- GLUE tasks: Accuracy, Matthews correlation coefficient (MCC), F1 score.
- SQuAD: Exact Match (EM) and F1.
- NLG tasks: ROUGE-1, ROUGE-2, and ROUGE-L.

**Baseline Comparisons:** 
- Full fine-tuning (FT)
- Bitfit (only biases)
- Adapter tuning (both types: Houlsby and Pfeiffer)
- LoRA (low-rank adaptation)

**Results:** 
| Method      | MNLI Acc | SQuAD v2.0 F1 | Params |
|-------------|----------|----------------|--------|
| Full FT     | 91.68    | 88.4           | 184M   |
| BitFit      | 89.22    | 87.25          | 0.1M   |
| HAdapter    | 90.95    | 88.3           | 1.22M  |
| PAdapter    | 90.3     | 88.0           | 1.18M  |
| LoRA        | 90.62    | 88.0           | 0.32M  |
| **AdaLoRA** | **90.76**| **89.2**       | **0.3M**|

Notably, AdaLoRA demonstrates superior performance relative to ROI-type baselines, especially under lower budget constraints (i.e., with 0.08% training parameters, AdaLoRA outperformed higher-budget baselines).

**Ablation Studies:** Indicated that maintaining orthogonality through regularization, as well as the budget scheduler, presented significant advantages. Comparisons showed that selective pruning based on the triplet importance metric allowed for stable and consistent performance improvement across tasks.

### Discussion & Conclusion
AdaLoRA establishes a new benchmark for parameter-efficient fine-tuning, highlighting its adaptive method of budget allocation for fine-tuning tasks on PLMs. Performance gains are especially pronounced in resource-constrained scenarios. However, potential limitations include the increased complexity of implementing the new importance scoring mechanism. Future work could explore further optimizations in the budget allocation strategy and the extension of the AdaLoRA framework to other architectures beyond transformers.

## Key Contributions
- Introduction of AdaLoRA for adaptive budget allocation in fine-tuning large models.
- Demonstration of improved performance particularly in low-resource settings over existing fine-tuning methods.
- Development of a novel importance metric that effectively guides parameter allocation during training.

## Potential Relevance
The methodologies in AdaLoRA regarding adaptive budget allocation and importance scoring could be pivotal in developing more resource-efficient models for various NLP tasks. The findings emphasize the need for dynamic rather than uniform approaches to parameter tuning in multi-tasking scenarios, which can be particularly relevant for optimizing performance across diverse applications.