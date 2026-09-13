---
source_paper: "arxiv_1706_04599.md"
generated_at: "2026-03-18T02:44:10.690922"
model: "gpt-4o-mini"
summary_chars: 6143
---

# On Calibration of Modern Neural Networks

## Key Metadata
- **Authors:** Chuan Guo et al.
- **Year:** 2017
- **Venue:** Proceedings of the 34th International Conference on Machine Learning
- **Core Contribution:** This paper explores the miscalibration of modern neural networks, identifies the contributing factors, and introduces effective calibration techniques, particularly temperature scaling.

## Section Summaries

### Abstract
Conﬁdence calibration – the problem of predict-
ing probability estimates representative of the
true correctness likelihood – is important for
classiﬁcation models in many applications. We
discover that modern neural networks, unlike
those from a decade ago, are poorly calibrated.
Through extensive experiments, we observe that
depth, width, weight decay, and Batch Normal-
ization are important factors inﬂuencing calibra-
tion. We evaluate the performance of various
post-processing calibration methods on state-of-
the-art architectures with image and document
classiﬁcation datasets. Our analysis and exper-
iments not only offer insights into neural net-
work learning, but also provide a simple and
straightforward recipe for practical settings: on
most datasets, temperature scaling – a single-
parameter variant of Platt Scaling – is surpris-
ingly effective at calibrating predictions.

### Introduction & Motivation
The paper addresses the issue of confidence calibration in neural networks, which is critical for various applications, including autonomous vehicles and medical diagnostics. While neural networks have improved their classification accuracy, a surprising observation is that they are poorly calibrated compared to earlier models. The authors aim to identify factors causing this miscalibration and evaluate various calibration techniques that can effectively address the problem.

### Methodology
The study focuses on supervised multi-class classification with neural networks and operates under the definition that a well-calibrated model should have its predicted probabilities accurately reflect true correctness likelihoods. Calibration is quantitatively assessed using Expected Calibration Error (ECE) and Maximum Calibration Error (MCE), with the following definitions:

1. **Expected Calibration Error (ECE)**:
   \[
   ECE = \sum_{m=1}^{M} \frac{|B_m|}{n} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|
   \]

2. **Maximum Calibration Error (MCE)**:
   \[
   MCE = \max_{m=1,\ldots,M} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|
   \]

The study identifies four key hyperparameters impacting calibration: model depth and width, weight decay, and the use of Batch Normalization. Two proposed methods for calibration include:
1. **Temperature Scaling**: This simple post-processing technique utilizes a single parameter \(T\), affecting the logits before the softmax function:
   \[
   \hat{q}_i = \max_k \sigma_{SM} \left( \frac{z_i}{T} \right)
   \]
   where \(\sigma_{SM}\) is the softmax function.
   
2. **Platt Scaling**: A logistic regression model on the validation set used to calibrate output probabilities.

The training uses standard state-of-the-art architectures (ResNet, Wide ResNet, and DenseNet) across multiple datasets, with learning rates adaptable between \(0.1\) to \(0.001\), and optimization performed using Adam or SGD.

### Experiments & Results
The experiments are conducted on multiple datasets:
- **Image Classification**: CIFAR-10, CIFAR-100, ImageNet, Stanford Cars, SVHN, Birds
- **Document Classification**: 20 News, Reuters, SST

Each dataset is split into train/validation/test with specific sizes. Calibration is assessed using ECE and MCE metrics. The results show that most models experience miscalibration, up to 10%, and that temperature scaling consistently outperforms other calibration techniques across vision tasks. The effectiveness of temperature scaling is particularly notable, often achieving ECE below 1%, while other methods, including matrix scaling, exhibited larger errors due to a tendency to overfit.

The performance results summarized in the following table show ECE improvements across different calibration methods:
| Calibration Method | ECE (%) for CIFAR-10 | ECE (%) for CIFAR-100 |
|--------------------|----------------------|-----------------------|
| Uncalibrated       | 4.3                  | 12.67                 |
| Hist. Binning      | 1.74                 | 4.34                  |
| Isotonic           | 0.58                 | 1.85                  |
| BBQ (Bayesian)     | 0.67                 | 4.99                  |
| Temperature Scaling | **0.44**             | **0.96**              |

The study discusses that temperature scaling is not only computationally efficient but also simple to implement within existing architectures.

### Discussion & Conclusion
The key takeaway is that advanced neural network architectures can lead to greater miscalibration, and careful adjustment of calibration techniques, particularly temperature scaling, is crucial for improving model reliability. However, limitations arise as the paper acknowledges that temperature scaling may not enhance calibration for well-calibrated datasets. Future work is suggested to further explore causal relationships between architectural choices and calibration outcomes.

## Key Contributions
- Identification of deterioration in calibration qualities of modern neural networks despite performance improvements.
- Introduction of temperature scaling as a novel, effective calibration technique that is easy to implement.
- Comprehensive empirical analysis of calibration methods across diverse datasets and architectures.

## Potential Relevance
This paper provides insights into calibration that may inform future hypotheses related to design choices in neural networks. The emphasis on temperature scaling might inspire heuristic methods for model robustness and reliability, which is vital for applications requiring interpretability of predictions. Understanding how various parameters affect calibration can lead to the development of advanced training protocols that actively consider model confidences.