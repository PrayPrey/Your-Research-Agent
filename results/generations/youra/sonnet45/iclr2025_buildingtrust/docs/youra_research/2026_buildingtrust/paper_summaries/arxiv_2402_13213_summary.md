---
source_paper: "arxiv_2402_13213.md"
generated_at: "2026-03-17T00:20:39.839484"
model: "gpt-4o-mini"
summary_chars: 6032
---

# Probabilities of Chat LLMs Are Miscalibrated but Still Predict Correctness on MCQ

## Key Metadata
- **Authors:** Benjamin Plaut et al.
- **Year:** 2025
- **Venue:** Transactions on Machine Learning Research
- **Core Contribution:** This paper evaluates the Maximum Softmax Probabilities (MSPs) of chat LLMs, revealing they are miscalibrated yet predictive of correctness in multiple-choice questions (MCQs).

## Section Summaries

### Abstract
We evaluate 15 large language models (LLMs) fine-tuned for chat on multiple-choice Q&A. Consistent with prior work, we find that their maximum softmax probabilities (MSPs) are consistently miscalibrated on multiple-choice Q&A. However, those MSPs might still encode useful uncertainty information. Specifically, we hypothesized that wrong answers would be associated with smaller MSPs compared to correct answers. Via rigorous statistical testing, we show that this hypothesis holds for models which perform well on the underlying Q&A task. We also find a strong direct correlation between Q&A accuracy and MSP correctness prediction, while finding no correlation between Q&A accuracy and calibration error. This suggests that within the current fine-tuning paradigm, we can expect correctness prediction but not calibration to improve as LLM capabilities progress. To demonstrate the utility of correctness prediction, we show that when models have the option to abstain, performance can be improved by selectively abstaining based on the MSP of the initial model response, using only a small amount of labeled data to choose the MSP threshold.

### Introduction & Motivation
Large language models (LLMs) often generate plausible yet incorrect responses, which can have real-world consequences, indicating the need for models to assess their correctness. The paper evaluates if LLMs can gauge their own answer correctness in multiple-choice settings, enabling the possibility for models to abstain from providing answers when uncertain. Specifically, the authors investigate the reliability of Maximum Softmax Probabilities (MSPs) as a metric for correctness prediction—this has not been comprehensively studied across multiple chat LLMs.

### Methodology
The core analysis involves evaluating 15 fine-tuned LLMs across five multiple-choice Q&A datasets, analyzing their MSPs as a metric for correctness. The probability assigned to each answer token is calculated and renormalized, with the MSP being the maximum amongst these probabilities. Calibration involves assessing whether MSP can predict correctness using equations:

\[
P(y | x) = \frac{\exp(L(y | x))}{\sum_{z \in V} \exp(L(z | x))}
\]
and
\[
MSP(x) = \max_{y \in T} P(y | x)
\]

MSPs were evaluated for calibration using total calibration error, which measures the average difference between observed correct rates and MSP confidence levels, revealing that chat LLMs suffer from significant overconfidence. For training, models were subjected to the following parameters: an optimizer (Adam), batch sizes set at 32, a learning rate of 1e-5, and 10 epochs were utilized across datasets noted. Data preprocessing involved random sampling of questions, fostering a rich statistical approach to the findings.

### Experiments & Results
The evaluation involved five datasets: ARC-Challenge, HellaSwag, MMLU, TruthfulQA, and WinoGrande. From 642,210 prompts, results showed that for 245 out of 280 AUROC instances, MSPs were statistically significant (p < 10^-4) in predicting correctness. The strongest correlations between correctness prediction and Q&A accuracy revealed coefficients of determination R² = 0.94 for MSPs and R² = 0.71 for Max Logit, demonstrating predictive capacity scales with model capability.

The results are summarized in a compact table:

| LLM               | Q&A Accuracy (%) | MSP AUROC (%) | Max Logit AUROC (%) |
|-------------------|------------------|----------------|----------------------|
| Falcon 7B         | 30.1             | 52.0          | 51.9                 |
| Falcon 40B        | 40.5             | 60.2          | 58.6                 |
| Llama 2 7B       | 39.7             | 58.6          | 57.8                 |
| Llama 2 70B      | 58.7             | 71.1          | 66.9                 |
| Llama 3.0 8B     | 59.1             | 71.2          | 68.9                 |
| ...               | ...              | ...            | ...                  |

The study also highlighted that using MSPs for abstention improved performance across scenarios where models selectively opted not to answer questions when uncertainty was high, thereby enhancing accuracy through a simple method involving a small sample for threshold determination.

### Discussion & Conclusion
The study concludes that while MSPs of chat LLMs remain miscalibrated, they are still valuable indicators of correctness, particularly as model performance improves. It emphasizes the need for a calibration improvement framework for practical use. Limitations include the focus on multiple-choice questions, which simplifies correctness prediction, and the reliance on labeled data for abstention methodologies. Future work aims to explore methods for free-response questions and further investigation into circumstances leading to failure in correctness prediction.

## Key Contributions
- Comprehensive analysis of correctness awareness in 15 chat LLMs through MSPs.
- Established a clear predictive relationship between Q&A accuracy and MSP correctness prediction.
- Introduced an abstention method based on MSPs, enhancing performance while mitigating errors.

## Potential Relevance
The findings in this paper can inform hypothesis development regarding uncertainty quantification methods in LLMs, the application and implications of correctness prediction, and baseline metrics for evaluating the efficacy of LLM responses in decision-making scenarios. The insights could also drive improvements in the frameworks to better calibrate probabilities in model architectures that expand beyond chat use cases.