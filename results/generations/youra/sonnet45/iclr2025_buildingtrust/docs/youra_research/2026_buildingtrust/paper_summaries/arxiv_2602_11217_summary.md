---
source_paper: "arxiv_2602_11217.md"
generated_at: "2026-03-17T00:22:29.490344"
model: "gpt-4o-mini"
summary_chars: 6361
---

# The Magic Correlations: Understanding Knowledge Transfer from Pretraining to Supervised Fine-Tuning

## Key Metadata
- **Authors:** Simin Fan et al.
- **Year:** 2026
- **Venue:** arXiv
- **Core Contribution:** This paper investigates knowledge transfer from pretraining to supervised fine-tuning, emphasizing the correlation between accuracy and confidence metrics across various model scales and capabilities.

## Section Summaries

### Abstract
Understanding how language model capabilities transfer from pretraining to supervised fine-tuning (SFT) is fundamental to efficient model development and data curation. In this work, we investigate four core questions: RQ1. To what extent do accuracy and confidence rankings established during pretraining persist after SFT? RQ2. Which benchmarks serve as robust cross-stage predictors and which are unreliable? RQ3. How do transfer dynamics shift with model scale? RQ4. How well does model confidence align with accuracy, as a measure of calibration quality? Does this alignment pattern transfer across training stages? We address these questions through a suite of correlation protocols applied to accuracy and confidence metrics across diverse data mixtures and model scales. Our experiments reveal that transfer reliability varies dramatically across capability categories, benchmarks, and scales—with accuracy and confidence exhibiting distinct, sometimes opposing, scaling dynamics. These findings shed light on the complex interplay between pretraining decisions and downstream outcomes, providing actionable guidance for benchmark selection, data curation, and efficient model development.

### Introduction & Motivation
The training of modern Large Language Models (LLMs) involves two distinct phases: pretraining on extensive text corpora and subsequent supervised fine-tuning (SFT) on curated datasets. The reliability of pretraining benchmarks as predictors of SFT performance is crucial for developing efficient models and conducting data curation. This paper examines whether performance metrics established during pretraining persist after SFT, how model scale affects transfer dynamics, and the calibration quality of model confidence against accuracy. By answering these questions, the authors aim to rectify existing gaps in empirical understanding of model training processes.

### Methodology
The study employs transformer models with two parameter sizes (240M and 1B) and investigates knowledge transfer across nine different data mixtures composed of web, code, and curated sources. The pretraining involves training on 12 billion tokens (for 240M models) and 52 billion tokens (for 1B models), followed by 5 epochs of SFT using cosine learning rate schedules. 

Key hyperparameters include:
- Learning Rate: Default to cosine annealing
- Batch Size: Not specified but generalized across the model scales.

The study evaluates performance on 20 benchmarks categorized into four domains: Commonsense Reasoning, Scientific Reasoning, Natural Language Inference (NLI), and Semantic Understanding, with performance measured through accuracy and model confidence.

Correlation metrics are established:
- Cross-Stage Accuracy Correlation: 
  \[
  r_{\text{acc}} = \text{corr}(a_{\text{PT}}, a_{\text{SFT}})
  \]
- Cross-Stage Confidence Correlation: 
  \[
  r_{\text{conf}} = \text{corr}(c_{\text{PT}}, c_{\text{SFT}})
  \]
where \(a_{\text{PT}}\) and \(c_{\text{PT}}\) are the metrics during pretraining, and \(a_{\text{SFT}}\), \(c_{\text{SFT}}\) after SFT. 

The study performs systematic experiments using correlation protocols to measure both performance persistence (cross-stage transfer) and calibration (alignment between accuracy and confidence across different stages and model sizes).

### Experiments & Results
The experiment examines various benchmarks within four capability categories with notable findings:
1. **Dataset Reliability and Transferability:**
   - Benchmarks such as Commonsense and Science exhibit high cross-stage correlations (average \(r_{\text{acc}} > 0.5\)), while benchmarks like NLI and Semantic show weaker performance persistence.
   
2. **Correlation Data:**
   - The correlation results indicate significant challenges in using certain benchmarks for early decision-making. High correlation is observed in the Commonsense metrics at smaller scales (240M: \(r_{\text{conf}} = 0.68\)), while anomalies appear in benchmarks like WinoGrande which show negative correlations (\(r_{\text{acc}} < 0.3\)).

3. **Scaling Dynamics:**
   - Observed inverse relationship: larger models yield higher accuracy correlations post-SFT (\(r_{\text{acc}} = 0.60\) for 1B vs. \(0.51\) for 240M) but lower confidence correlations (\(r_{\text{conf}} = 0.39\) for 1B vs. \(0.68\) for 240M).
   
4. **Calibration Quality:**
   - Significant sectorial variations in model confidence alignment vs accuracy. Domains like Science score high on alignment (mean \(r_{\text{align}} \approx 0.8\)) while Commonsense tasks show consistent miscalibration (\(r_{\text{align}} \approx -0.1\)).

The results suggest critical insights toward benchmark selection and the influence of model size on transfer mechanics and calibration practices.

### Discussion & Conclusion
The paper concludes that how pretraining decisions affect downstream model application is complex, highlighting critical trade-offs between accuracy and confidence metrics. The findings suggest that benchmark evaluations must consider specific capability domains and model sizes to ensure effective model training and application. Future research should explore broader domains and assess more models at varying scales for a comprehensive understanding of knowledge transfer dynamics.

## Key Contributions
- Comprehensive analysis of knowledge transfer from pretraining to fine-tuning.
- Systematic evaluation of benchmark reliability across various domains.
- Insights into scaling effects on accuracy and confidence dynamics and their implications for model calibration.

## Potential Relevance
The insights from this paper could inform the development of hypotheses around the impact of model architecture and data mixtures on knowledge transferability. Additionally, the findings emphasize the importance of careful benchmark selection, which could guide future experimental designs in LLM training and data curation.