---
source_paper: "arxiv_2510_03313.md"
generated_at: "2026-03-17T07:42:45.989237"
model: "gpt-4o-mini"
summary_chars: 6594
---

# Scaling Laws Revisited: Modeling the Role of Data Quality

## Key Metadata
- **Authors:** Anirudh Subramanyam et al.
- **Year:** 2023
- **Venue:** arXiv
- **Core Contribution:** Introduced a quality-aware scaling law that integrates data quality into the performance prediction of language models.

## Section Summaries

### Abstract
Scaling laws for language model training traditionally characterize how performance scales with model size and dataset volume. Prior work has explored architecture variants and data treatments such as dataset filtering and noise injection in language model pretraining; however, these studies have not formalized data quality within a principled scaling law. We introduce a dimensionless data-quality parameter Q, and propose a quality-aware scaling law extending the Chinchilla framework to predict loss as a joint function of model size, data volume, and data quality. The law is motivated by an effective-sample-size and information-theoretic view of noisy or redundant corpora, and it admits two practical estimators for Q: (i) a corruption rate proxy and (ii) a deficiency measure. Through synthetic experiments in neural machine translation and autoregressive modeling—where we systematically control data quality via multiple levels of noise injection variation—we show that loss scales predictably with data quality and that higher-quality data can substantially reduce model size and hence compute requirements. Our results demonstrate a sublinear decay of effective data with quality and robustness to moderate data corruption; out-of-sample evaluations further validate the predictive form of the law. Unlike prior empirical analyses, our work establishes an explicit, generalizable law for data quality, offering concrete guidance for balancing data curation effort and model scale in large-scale pretraining.

### Introduction & Motivation
This work aims to address the lack of a formalized quantitative framework for data quality in scaling laws, which typically consider only dataset size and model size. Quality of data is crucial in specialized domains where data is often limited and heterogeneous. Previous studies identified various dimensions of data quality but did not integrate them into a unified scaling law. This paper seeks to formalize the impact of data quality via a dimensionless parameter Q with values ranging from 0 (completely corrupt) to 1 (perfectly clean data), linking performance to both quality and quantity of data used.

### Methodology
The authors propose a quality-aware scaling law, expressed as:

\[
L(N, D, Q) = \frac{A}{N^\alpha} + \frac{B}{D^\beta Q^\gamma} + E
\]

where \( L \) denotes loss, \( N \) the number of training parameters, \( D \) the number of training tokens, and \( Q \) is the data quality parameter. Estimates for \( Q \) are obtained through two methods: 
1. **Data Corruption Rate (CR):** Defined as \( Q(\omega) = 1 - CR \), allowing for easy calculation of dataset quality based on the fraction of corrupted tokens.
2. **Data Deficiency (\( \Delta \)):** Computes \( Q \) as \( Q(\omega) = e^{-\Delta(\omega)} \), allowing for more complex measures of quality degradation.

The experiments utilize neural machine translation (NMT) and causal language modeling (CLM) tasks, employing datasets like Paracrawl v8 for NMT and subsets of C4 for CLM. The training uses AdamW optimizer with varying learning rates and dataset sizes to explore the effects of data quality across different volumes. Synthetic noise is added systematically to assess how varying levels of data corruption impact performance.

Key hyperparameters and configurations:
- **For NMT:** 8L GPT Neo model with 1024 hidden size, maximum learning rate of \(5 \times 10^{-4}\), and cosine decay scheduling.
- **For CLM:** 8L Llama 3 model with hidden size of 512 and context length of 2048, maximum learning rate of \(1 \times 10^{-3}\) with a similar scheduling.

### Experiments & Results
The experiments assess both tasks under controlled conditions across multiple data sizes (500K, 1M, and 2M sentence pairs for NMT; 100M, 1B, and 10B tokens for CLM) and varying levels of synthetic noise (0% to 50% corruption). The evaluation metrics include pretraining loss on held-out data.

Key findings:
- **Data Quality Impact:** Higher-quality data resulted in lower loss, demonstrating that good data can compensate for smaller models.
- **Sublinearity in Quality's Effect:** The value of \(\hat{\gamma}\) was estimated as 0.173 for NMT and 0.401 for CLM, indicating sublinear decay of effective size with respect to quality. This suggests robustness to moderate levels of corruption.
- **Scaling Generalization:** Results showed consistent performance on unseen data, with the fitted quality-aware scaling law accurately predicting performance metrics.

Results summary (main parameters observed across tasks):
| Task   | Method       | B         | β       | γ       | E       |
|--------|--------------|-----------|---------|---------|---------|
| NMT    | Least Squares| 166.57    | 0.2629  | 0.1851  | 0.1469  |
| CLM    | Huber        | 1428.23   | 0.3951  | 0.3887  | 3.4399  |

The scalability and robustness were highlighted through iso-loss contours indicating the balance between dataset volume and quality metrics.

### Discussion & Conclusion
The study establishes a clear relationship between data quality and model performance, allowing practitioners to strategically balance data curation efforts against model complexity. Limitations acknowledge variability when extending this framework to other domains beyond the tested language tasks, suggesting further exploration into diverse applications. Future work may enhance the precision of estimators for Q or explore quality metrics in additional real-world datasets to refine the scaling relationships presented.

## Key Contributions
- Introduction of a dimensionless data quality parameter \( Q \) to enhance scaling laws' applicability.
- Development of a quality-aware scaling law expressing loss as a function of model size, data volume, and data quality.
- Empirical validation of the new law through well-controlled experiments across various data corruption levels.

## Potential Relevance
The integration of data quality into scaling laws could inform future experimental designs in language models, especially for specialized domains seeking to optimize performance with limited high-quality data. The methodologies and findings may guide discussions around hypotheses concerning the efficiency of model training relative to data curation efforts.