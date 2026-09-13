---
source_paper: "arxiv_2502_11028.md"
generated_at: "2026-03-14T22:48:52.332598"
model: "gpt-4o-mini"
summary_chars: 6364
---

# Mind the Confidence Gap: Overconfidence, Calibration, and Distractor Effects in LLMs

## Key Metadata
- **Authors:** Prateek Chhikara et al.
- **Year:** 2025
- **Venue:** Transactions on Machine Learning Research
- **Core Contribution:** This paper presents a large-scale empirical study demonstrating how structured distractors can significantly mitigate overconfidence and improve the calibration of large language models (LLMs).

## Section Summaries

### Abstract
Large Language Models (LLMs) show remarkable proficiency in natural language tasks, yet their frequent overconfidence—misalignment between predicted confidence and true correctness—poses significant risks in critical decision-making applications. We present a comprehensive analysis on calibration in LLMs across nine LLMs and three factual Question-Answering (QA) datasets, systematically comparing standard free-generation settings against structured distractor-augmented prompts. Our evaluation reveals that explicitly incorporating distractors can substantially mitigate miscalibration, achieving relative accuracy improvements up to 460% and ECE reductions up to 90%. Despite general trends, we uncover nuanced findings: large RLHF-tuned models display inherent calibration strengths but can paradoxically suffer increased miscalibration on easier queries, whereas smaller models benefit disproportionately from distractor prompts but remain significantly miscalibrated. Through detailed analyses across question types, we identify persistent calibration failures, particularly in person-based queries. We conclude with concrete recommendations—targeted fine-tuning, structured prompting, and strategic model choice—to ensure reliable, trustworthy LLM deployments. Code is publicly available at: https://github.com/prateekchhikara/llms-calibration

### Introduction & Motivation
LLMs significantly advance natural language understanding and achieve state-of-the-art results across diverse tasks. However, as these models increasingly influence critical decisions in sensitive fields like healthcare and finance, their reliability in confidence estimation is crucial. Miscalibration—disparities between model confidence and actual correctness—can lead to dangerous errors. This paper addresses performance under distractor-augmented prompting, assessing whether presenting models with incorrect options mitigates overconfidence and improves overall calibration.

### Methodology
The study compares nine state-of-the-art LLMs under two conditions: standard free-generation prompting and distractor-augmented prompting. Each model is subjected to three datasets: SimpleQA (4,326 queries), FaVIQ (2,922 labeled supports), and TriviaQA (1,000 validation queries). 

In the distractor-augmented setting, for each query \( q_i \), three distractors \( d_{i,j} \) are generated contextually. To compare performance, they define \( S = \{(q_i, a_i)\}_n^1 \) for the evaluations, with generated answers and associated elicited confidence: 
- **Free-generation**: \( y^N_i, c^N_i = \text{LLM}(\pi_N \ || \ q_i) \)
- **Distractor-augmented**: \( y^D_i, c^D_i = \text{LLM}(\pi_D \ || \ q_i \ || \ C_i) \)

The distractors are generated using GPT-4o-mini with prompts ensuring they are incorrect yet plausible. Elicited confidence is measured on a 0-100 scale, allowing consistent comparisons across models. Performance is quantified using Expected Calibration Error (ECE), defined as \( ECE = \sum_{b=1}^B \frac{|p_b - o_b|}{N_b} \), where \( p_b \) is the predicted frequency and \( o_b \) is the observed frequency.

Key hyperparameters include learning rate adjustments based on performance, along with a training regimen featuring supervised fine-tuning (SFT) and reinforcement learning from human feedback (RLHF).

### Experiments & Results
The performance across datasets was rigorous, with metrics computed for accuracy (N_correct), NOT_ATTEMPTED (N_na), and ECE (N_ECE) against distractor settings (D_correct, D_na, D_ECE). The results are summarized in the table below:

| Dataset / LLMs         | N_correct | N_na | N_ECE | D_correct | D_na | D_ECE | D_helped | D_harmed |
|------------------------|-----------|------|-------|-----------|------|-------|----------|----------|
| SimpleQA               |           |      |       |           |      |       |          |          |
| GPT-4o-mini            | 0.750     | 6.80%| 0.450 | 47.43%    | 0.320| 0.165 | 1644 (93.78%) | 109 (6.22%) |
| LLaMA-3.1-8b-instant   | 18.78%    | 0.799| 0.769 | 44.64%    | 0.12%| 0.367 | 1644 (93.78%) | 109 (6.22%) |
| ...                    |           |      |       |           |      |       |          |          |

Key findings reveal significant calibration improvements due to distractors—e.g., up to 460% relative accuracy gain in smaller models on SimpleQA while ECE reductions reached 90%. Smaller models showed substantial gains while larger models displayed increased miscalibration in simpler conditions. The study includes detailed ablation analyses demonstrating how different model architectures respond distinctively to distractor prompts.

### Discussion & Conclusion
The results underscore the need for multifaceted calibration strategies for LLMs. While introducing structured distractors significantly enhances calibration, larger models, particularly RLHF-tuned ones, can paradoxically misalign on simpler tasks. Continuous exploration of tailored calibration methods and the role of distractors is advocated to mitigate persistent overconfidence and achieve trustworthy AI applications.

## Key Contributions
- Systematic evaluation of calibration in LLMs using distractor-augmented prompting strategies.
- Quantification of accuracy improvements up to 460% and ECE reductions up to 90% across model families.
- Identification of nuanced calibration issues, specifically in person-based QA settings, providing insights for future LLM deployments.

## Potential Relevance
This paper's findings on calibration strategies could inform future research on LLM confidence metrics. Insights into the effects of distractor prompts and model architecture variations could direct hypothesis testing, facilitating improved model designs and applications in reality-sensitive environments. The extensive benchmarking establishes a baseline for comparison relevant to ongoing calibration research.