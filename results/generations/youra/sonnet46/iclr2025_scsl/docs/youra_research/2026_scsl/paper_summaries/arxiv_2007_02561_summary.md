---
source_paper: "arxiv_2007_02561.md"
generated_at: "2026-03-16T20:40:39.925909"
model: "gpt-4o-mini"
summary_chars: 6101
---

# Learning from Failure (LfF)

## Key Metadata
- **Authors:** Junhyun Nam et al.
- **Year:** 2020
- **Venue:** NeurIPS 2020
- **Core Contribution:** Introduction of a failure-based debiasing scheme that effectively trains a debiased classifier from a biased one without requiring explicit supervision or labels for the bias.

## Section Summaries

### Abstract
Neural networks often learn to make predictions that overly rely on spurious correlations existing in the dataset, which causes the model to be biased. While previous work tackles this issue by using explicit labeling on the spuriously correlated attributes or presuming a particular bias type, we instead utilize a cheaper, yet generic form of human knowledge, which can be widely applicable to various types of bias. We first observe that neural networks learn to rely on the spurious correlation only when it is “easier” to learn than the desired knowledge, and such reliance is most prominent during the early phase of training. Based on these observations, we propose a failure-based debiasing scheme by training a pair of neural networks simultaneously. Our main idea is twofold; (a) we intentionally train the first network to be biased by repeatedly amplifying its “prejudice,” and (b) we debias the training of the second network by focusing on samples that go against the prejudice of the biased network in (a). Extensive experiments demonstrate that our method significantly improves the training of networks against various types of biases in both synthetic and real-world datasets. Surprisingly, our framework even occasionally outperforms debiasing methods that require explicit supervision of spuriously correlated attributes.

### Introduction & Motivation
Deep neural networks excel in performance on curated datasets but often fail when trained on biased datasets. These biases lead networks to adopt unintended decision rules, such as relying on spurious correlations instead of meaningful features. Traditional methods typically necessitate exhaustive human labeling to identify bias attributes or are tailored to specific forms of bias, making them costly to implement. This paper introduces "Learning from Failure" (LfF), a technique that leverages intrinsic properties of neural networks, allowing them to debias effectively without needing explicit supervision on biases.

### Methodology
The LfF method employs two neural networks: a biased network $f_B$ and a debiased network $f_D$. The training procedure unfolds as follows:

1. **Training the Biased Network ($f_B$):** This network is trained to make predictions influenced largely by spurious correlations. It uses the Generalized Cross Entropy (GCE) loss defined as:

   \[
   GCE(p(x; \theta), y) = \frac{1 - p_y(x;\theta)^q}{q}
   \]

   where $q \in (0, 1]$ controls the emphasis on easier, bias-aligned samples. As the GCE loss amplifies the bias presence, the network learns to heavily weigh biased attributes during training.

2. **Training the Debiased Network ($f_D$):** The second neural network is trained concurrently with $f_B$ but focuses on bias-confliting samples. The weighted Cross Entropy loss is represented as follows:

   \[
   W(x) = \frac{CE(f_B(x), y)}{CE(f_B(x), y) + CE(f_D(x), y)}
   \]

   The model's loss is adjusted based on how difficult it finds each sample, using the loss dynamics from both networks to guide training. Samples that contribute more to the bias are assigned lower priority in $f_D$'s training, while those that are more challenging for $f_B$ receive higher priority.

The datasets used include Colored MNIST, Corrupted CIFAR-10, and a new realistic dataset, Biased Action Recognition (BAR), which contributes to training on a variety of bias types.

### Experiments & Results
The proposed LfF scheme was evaluated on multiple datasets:

- **Datasets:** Colored MNIST (60,000 samples), Corrupted CIFAR-10 (60,000 samples), and BAR (construction from images depicting six action-place pairs).
- **Evaluation Metrics:** Model performance was assessed on both unbiased and bias-confliting samples.
- **Baselines:** Compared against methods like HEX, REPAIR, and Group DRO, which require explicit labels for debiasing.

Results (samples in the tables condensed):

| Dataset               | Acc (LfF) | Acc (Vanilla) |
|----------------------|-----------|---------------|
| Colored MNIST        | 85.39%    | 50.34%        |
| Corrupted CIFAR-101  | 41.37%    | 22.72%        |
| CelebA (Gender Bias) | 84.24%    | 62.00%        |

The framework consistently outperformed baselines even when 99.5% of training samples were bias-aligned. Ablation studies demonstrated that the GCE significantly amplified bias in $f_B$, which played a crucial role in the debiased training process. Computational cost involved approximately 35 GPU hours for the training and evaluation phases.

### Discussion & Conclusion
The LfF methodology demonstrates a novel approach to debiasing classifiers without the need for explicit bias supervision, thus broadening its applicability. By exploiting training dynamics and emphasizing challenging samples, LfF enhances model accuracy and generalizes well in diverse scenarios. Future work could explore extensions into other domains and real-time applications while acknowledging the challenges in interpreting outcomes on underexplored biases.

## Key Contributions
- Introduction of LfF, a novel debiasing method requiring no explicit supervision.
- Demonstrated significant effectiveness in various datasets, achieving state-of-the-art results.
- Developed and utilized a new realistic dataset (BAR) for evaluating debiasing methods.

## Potential Relevance
The findings from this paper can inform future hypotheses about debiasing techniques in machine learning. The LfF approach can inspire further research into unsupervised learning methods for addressing bias and highlight the importance of understanding model training dynamics in the presence of various biases. The established baselines could also serve as a reference point for comparative studies on new debiasing approaches.