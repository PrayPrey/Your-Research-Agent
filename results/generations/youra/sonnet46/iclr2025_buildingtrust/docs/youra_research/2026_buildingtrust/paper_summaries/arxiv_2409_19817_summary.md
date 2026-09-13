---
source_paper: "arxiv_2409_19817.md"
generated_at: "2026-03-14T22:48:33.880704"
model: "gpt-4o-mini"
summary_chars: 6638
---

# Calibrating Language Models with Adaptive Temperature Scaling

## Key Metadata
- **Authors:** Johnathan Xie et al.
- **Year:** 2023
- **Venue:** arXiv
- **Core Contribution:** Introduced Adaptive Temperature Scaling (ATS), a method for calibrating language models after fine-tuning with reinforcement learning from human feedback (RLHF).

## Section Summaries

### Abstract
The effectiveness of large language models (LLMs) is not only measured by their ability to generate accurate outputs but also by their calibration—how well their confidence scores reflect the probability of their outputs being correct. While unsupervised pre-training has been shown to yield LLMs with well-calibrated conditional probabilities, recent studies have shown that after fine-tuning with reinforcement learning from human feedback (RLHF), the calibration of these models degrades significantly. In this work, we introduce Adaptive Temperature Scaling (ATS), a post-hoc calibration method that predicts a temperature scaling parameter for each token prediction. The predicted temperature values adapt based on token-level features and are fit over a standard supervised fine-tuning (SFT) dataset. The adaptive nature of ATS addresses the varying degrees of calibration shift that can occur after RLHF fine-tuning. ATS improves calibration by over 10-50% across three downstream natural language evaluation benchmarks compared to prior calibration methods and does not impede performance improvements from RLHF.

### Introduction & Motivation
LLMs have become central to various AI applications, but their utility hinges on generating confidence scores that align with their accuracy. Calibration is crucial for real-world applications, as incorrect predictions can lead to significant consequences. Fine-tuning methods like RLHF boost LLM performance but often degrade calibration. This study addresses the calibration drop post-RLHF and aims to retain performance gains while ensuring reliable confidence scores through ATS, which individualizes temperature scaling for token predictions based on context-specific features.

### Methodology
ATS is designed to calibrate LLM outputs post-RLHF by predicting a token-specific temperature scaling parameter \( \tau \) using a calibration head. 

- **Architecture:** Given an input-output pair \((x, y)\) from a set of examples \(D = \{(x, y)\}\) with vocabulary \(V\), we first derive language model logits \(\hat{z} = \pi(x)\). The calibration head generates a temperature vector \(c_\theta(\hat{h}) = \tau\) where \(\hat{h}\) are input-dependent features derived from the last hidden state \(\hat{h} \in \mathbb{R}^{l_{x+y},h}\). The calibrated logits are computed as:
  \[
  \hat{q} = \hat{z} \circ e^{\tau}
  \]
- **Hyperparameters:** Key parameters include learning rate (not specified), batch size (varied), and \( \alpha \) in the loss function, set between 0 to 1.
- **Loss Function:** The proposed loss function adjusts targets based on the model's confidence:
  \[
  \ell(\hat{q}, y) = \begin{cases} 
  -(1 - \alpha) \log (\sigma_{SM}(\hat{q})_y) & \text{if } \hat{q} \text{ is correct} \\
  -\alpha \sum_{i=1}^{|V|} \log(\sigma_{SM}(\hat{q})_i) & \text{otherwise}
  \end{cases}
  \]
- **Input/Output:** Models utilize an SFT dataset and output calibrated logits for token predictions post-processing of language model logits.
- **Novel Components:** ATS optimizes temperature based on token-level features, diverging from traditional temperature scaling that uses a single value, enhancing adaptability.

### Experiments & Results
The evaluation involved two large language models with 7 billion parameters each, LLama-2-Chat and Qwen-Chat, utilizing a calibration dataset derived from Alpaca GPT-4. Performance was assessed on three tasks: MMLU, TriviaQA, and TruthfulQA.

- **Dataset Size:** Each benchmark was properly partitioned for training, validation, and testing.
- **Evaluation Metrics:** Metrics included Expected Calibration Error (ECE) and Brier Score (BS), measuring calibration accuracy in conjunction with standard accuracy metrics.
- **Baseline Methods:** ATS was compared against no calibration, basic temperature scaling, vector scaling, and scaling binning.
- **Main Results:**
  
  | Model                    | ECE (MMLU) | BS (MMLU) | ECE (TriviaQA) | BS (TriviaQA) | ECE (TruthfulQA) | BS (TruthfulQA) |
  | ------------------------ | ----------- | ---------- | --------------- | -------------- | ----------------- | ---------------- |
  | None                     | 0.298       | 0.313      | 0.221           | 0.239          | 0.507             | 0.480            |
  | Temperature Scaling      | 0.270       | 0.295      | 0.187           | 0.224          | 0.492             | 0.463            |
  | Vector Scaling           | 0.324       | 0.333      | 0.211           | 0.234          | 0.499             | 0.471            |
  | Scaling Binning          | 0.296       | 0.312      | 0.222           | 0.239          | 0.544             | 0.504            |
  | **ATS (Our Method)**     | **0.125**   | **0.227**  | **0.050**       | **0.190**      | **0.092**         | **0.267**        |

- **Statistical Findings:** ATS consistently demonstrated a 10-50% improvement in calibration metrics across all evaluated benchmarks relative to the nearest competitor.
- **Ablation Studies:** Evaluated components such as loss function choices (selective smoothing performed best), loss weighting (optimal at \(\alpha = 0.6\)), and head architecture (transformer head outperformed simpler architectures).

### Discussion & Conclusion
ATS markedly improves calibration in LLMs fine-tuned with RLHF while maintaining performance metrics. Despite demonstrated efficacy, limitations include unexplored interactions with various sentence-level confidence methods and the need for a broader exploration of adaptive techniques in calibration. Future research should aim to integrate these findings with more nuanced uncertainty modeling to enhance confidence expression in AI outputs.

## Key Contributions
- Introduced Adaptive Temperature Scaling for LLM calibration.
- Demonstrated significant improvements in model calibration post-RLHF.
- Developed an innovative method to integrate context-specific temperature scaling based on token-level features.

## Potential Relevance
ATS's method of tailoring calibration in LLMs could inform approaches to refining hypotheses about model outputs and confidence estimation in natural language tasks. Its high adaptability and focus on calibration merits consideration for future work in enhancing AI model reliability and performance.