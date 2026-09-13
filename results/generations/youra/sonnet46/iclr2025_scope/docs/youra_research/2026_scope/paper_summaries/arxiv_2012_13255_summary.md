---
source_paper: "arxiv_2012_13255.md"
generated_at: "2026-05-08T05:57:24.382730"
model: "gpt-4o-mini"
summary_chars: 6736
---

# Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning

## Key Metadata
- **Authors:** Armen Aghajanyan et al.
- **Year:** 2020
- **Venue:** arXiv
- **Core Contribution:** The paper introduces intrinsic dimensionality as a crucial factor in understanding why fine-tuning large language models is effective even with limited data.

## Section Summaries

### Abstract
Although pretrained language models can be fine-tuned to produce state-of-the-art results for a very wide range of language understanding tasks, the dynamics of this process are not well understood, especially in the low data regime. Why can we use relatively vanilla gradient descent algorithms (e.g., without strong regularization) to tune a model with hundreds of millions of parameters on datasets with only hundreds or thousands of labeled examples? In this paper, we argue that analyzing fine-tuning through the lens of intrinsic dimension provides us with empirical and theoretical intuitions to explain this remarkable phenomenon. We empirically show that common pre-trained models have a very low intrinsic dimension; in other words, there exists a low dimension reparameterization that is as effective for fine-tuning as the full parameter space. For example, by optimizing only 200 trainable parameters randomly projected back into the full space, we can tune a RoBERTa model to achieve 90% of the full parameter performance levels on MRPC. Furthermore, we empirically show that pre-training implicitly minimizes intrinsic dimension and, perhaps surprisingly, larger models tend to have lower intrinsic dimension after a fixed number of pre-training updates, at least in part explaining their extreme effectiveness. Lastly, we connect intrinsic dimensionality with low dimensional task representations and compression based generalization bounds to provide intrinsic-dimension-based generalization bounds that are independent of the full parameter count.

### Introduction & Motivation
Pre-trained language models serve as the primary initialization for numerous NLP tasks, yet the fine-tuning process on small datasets remains poorly understood. The authors propose analyzing this process through intrinsic dimensionality, which reflects the minimal number of parameters needed to effectively solve specific optimization problems. The insight is that a low intrinsic dimension implies that only a small subset of parameters are essential for fine-tuning, allowing for effective learning on datasets with limited examples.

### Methodology
The core methodology revolves around measuring the intrinsic dimensionality of NLP tasks through a re-parameterization approach. The authors adopt the framework specified by Li et al. (2018), which quantifies the intrinsic dimension necessary to solve an optimization problem. Specifically, they employ a subspace method defined as:

\[
\theta_D = \theta_{D0} + P(\theta_d)
\]

where \(P\) is a projection from a lower-dimensional space (\(d\)) back to the original parameter space (\(D\)). The specific projection utilized in the paper is based on the Fastfood transform, allowing the mapping to be computed efficiently.

For the experiments, the quality of fine-tuning is evaluated through the ability to reach a satisfactory solution (90% of the full parameter performance) with different dimensions of \(d\). Two approaches are employed: the Structure-Aware Intrinsic Dimension (SAID), which incorporates layer-wise scaling, and the Direct Intrinsic Dimension (DID), which does not consider structural properties.

Key hyperparameters include:
- Learning rates tuned during experiments.
- Fixed number of updates (200k for pre-training).

Data processed includes various sentence prediction tasks, specifically MRPC and QQP from the GLUE Benchmark. By reinitializing the parameters of the sentence classification head randomly, the dimensionality (\(d\)) ranges from 10 to 10,000 to find the optimal performance for each model architecture tested.

### Experiments & Results
A series of experiments were conducted using datasets including MRPC (3,700 training samples) and QQP (363,000 training samples) to analyze the intrinsic dimensionality of different NLP tasks. The authors found that a minimal set of parameters could achieve high performance, with the following results summarized in a table:

| Model            | MRPC (SAID) | MRPC (DID) | QQP (SAID) | QQP (DID) |
|------------------|-------------|------------|------------|-----------|
| BERT-Base        | 1608        | 8030       | 1861       | 9295      |
| BERT-Large       | 1037        | 1200       | 2493       | 1389      |
| RoBERTa-Base     | 896         | 896        | 1000       | 1389      |
| RoBERTa-Large    | 207         | 774        | 322        | 774       |

The results showed that RoBERTa models consistently required fewer parameters to achieve comparable performance to BERT, emphasizing the impact of architecture on intrinsic dimensionality. Additionally, a trend emerged that indicated lower intrinsic dimensions correlate with larger model sizes and enhanced effectiveness during fine-tuning.

An ablation study confirmed that incorporating layer-wise considerations (SAID) significantly outperformed the layer-unaware approach (DID). The authors reported that larger models not only minimized intrinsic dimension but also resulted in better generalization performance across multiple datasets.

### Discussion & Conclusion
Overall, the findings support the premise that understanding intrinsic dimensionality can elucidate the success of large language models under fine-tuning. Pre-training appears to simplify subsequent learning tasks by optimizing the intrinsic dimension of representations. The authors suggest that further theoretical exploration is needed to explicitly connect SGD optimization with intrinsic dimension strategies.

## Key Contributions
- Establishes the intrinsic dimensionality as a key concept for understanding effective fine-tuning of NLP tasks.
- Empirically illustrates that a low intrinsic dimension allows large language models to perform well with limited labeled data.
- Provides a new framework for generalization bounds independent of parameter count, focusing instead on intrinsic dimensionality.

## Potential Relevance
This paper's exploration of intrinsic dimensionality could inform the formulation of new hypotheses around fine-tuning, serving as a foundation for understanding model efficiency, and potentially guiding future research on model architecture and training dynamics. Its findings on the relationships between dimensionality, model size, and task generalization may be useful for optimizing deep learning strategies in language processing.