---
source_paper: "arxiv_2409_05816.md"
generated_at: "2026-03-17T07:41:43.540547"
model: "gpt-4o-mini"
summary_chars: 6438
---

# Improving Pretraining Data Using Perplexity Correlations

## Key Metadata
- **Authors:** Tristan Thrush et al.
- **Year:** 2025
- **Venue:** ICLR
- **Core Contribution:** A framework for selecting high-quality pretraining data for LLMs using correlations between log-likelihood and downstream task performance without expensive retraining.

## Section Summaries

### Abstract
Quality pretraining data is often seen as the key to high-performance language models. However, progress in understanding pretraining data has been slow due to the costly pretraining runs required for data selection experiments. We present a framework that avoids these costs and selects high-quality pretraining data without any LLM training of our own. Our work is based on a simple observation: LLM losses on many pretraining texts are correlated with downstream benchmark performance, and selecting high-correlation documents is an effective pretraining data selection method. We build a new statistical framework for data selection centered around estimates of perplexity-benchmark correlations and perform data selection using a sample of 90 LLMs taken from the Open LLM Leaderboard on texts from tens of thousands of web domains. In controlled pretraining experiments at the 160M parameter scale on 8 benchmarks, our approach outperforms DSIR on every benchmark while matching the best data selector found in DataComp-LM, a hand-engineered bigram classifier.

### Introduction & Motivation
Dataset curation has become essential for optimizing large language models (LLMs). As pretraining datasets have increased from 200B tokens in 2020 to 240T today, the need to identify a subset that maximizes LLM performance is paramount. Existing data-driven selection methods often require expensive retraining of models, limiting their practicality. This paper proposes a novel approach that leverages existing high-performance LLMs for data selection, thereby circumventing the need for costly training while addressing the gap in high-performance data selection techniques.

### Methodology
The proposed methodology for selecting training data involves analyzing perplexity correlations across multiple LLMs. Key steps include:

1. **Data Collection**: Collecting log-likelihoods (perplexity) from 90 LLMs ranking on the Hugging Face Open LLM Leaderboard, leading to a dataset spanning over 9,000 web domains.

2. **Perplexity Correlation Estimation**: The core insight is that lower perplexity (i.e., higher log likelihood) documents correlate with better downstream task performance. A correlation coefficient $\gamma_j$ is calculated for each domain $j$ using:

   \[
   \gamma_j = \sum_{1 \leq k, l \leq n; k \neq l} \text{sign}(y_k - y_l)(\text{rank}_j(x_{k,j}) - \text{rank}_j(x_{l,j}))
   \]

   where $x_{k,j}$ is the log-likelihood of document $j$ under model $k$.

3. **Data Selection Process**: Project positive $\gamma_j$ values into a valid probability distribution while ensuring that selection avoids duplications to curb performance degradation. This is achieved through a linear programming approach that constructs a normalized sampling distribution:

   - **Token Selection**: Domains are sampled from highest to lowest $\gamma_j$ until the desired total token count is reached.

4. **Algorithm Implementation**: The procedure is implemented with no additional hyperparameters, utilizing a fastText classifier for document-level selection. The algorithm ensures efficiency in handling large datasets while maintaining compliance with preservation of non-redundancy in training data.

### Experiments & Results
1. **Dataset and Training**: The study employed the "sample-100B" subset of the RedPajama V2 dataset for initialization. Controlled experiments were conducted with a 160M parameter model, training on various selected subsets of domains totaling 3.2 billion tokens.

2. **Evaluation Metrics**: The model performance was gauged across eight benchmarks, utilizing metrics such as accuracy and perplexity for LAMBADA tasks, while also confirming its effectiveness with additional aggregates across diverse benchmarks.

3. **Comparative Analysis**: The results were benchmarked against both baseline methods (including DSIR and handcrafted fastText classifiers) and showed significant improvements, with our method achieving the lowest average ranking (1.375) compared to others like DSIR (4.500) and various fastText configurations.

   | Method                                        | Avg. Rank |
   |-----------------------------------------------|-----------|
   | Perplexity Correlations                       | 1.375     |
   | Handcrafted fastText + manual language filter | 1.750     |
   | DSIR                                          | 4.500     |

4. **Ablation Studies**: Conducted to examine contributions of each algorithm component, demonstrating that the perplexity-correlation method outperformed alternative ranking strategies across benchmarks, even when factoring in manual filtering efforts.

5. **Statistical Findings**: The model predictions about downstream performances showed high correlations, with specific attention to the efficiency gains when scaling up to 1.4B parameters.

### Discussion & Conclusion
This work demonstrates the capability of selecting optimal pretraining data through existing LLMs without retraining, allowing for more effective LLM training. The findings validate that simpler correlation techniques can outperform more complex, tuned methods, suggesting future improvements in LLM pretraining may focus on enhancing statistical frameworks rather than extensive retraining.

## Key Contributions
- Proposed a novel data selection framework that uses perplexity correlations to replace traditional costly retraining methods.
- Demonstrated the practical success of the algorithm through controlled pretraining experiments across multiple benchmarks.
- Provided theoretical underpinnings for using rank correlation coefficients as predictive tools for data quality in LLM training.

## Potential Relevance
The methodologies and findings of this paper are relevant for hypotheses concerning efficient data selection strategies without expensive model training, especially in improving downstream performance in LLM applications. The demonstrated effectiveness of perplexity-correlation could inspire similar approaches or modifications in data filtration processes in ongoing research.