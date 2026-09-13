---
source_paper: "arxiv_2111_09525.md"
generated_at: "2026-03-16T14:04:32.534909"
model: "gpt-4o-mini"
summary_chars: 5754
---

# SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization

## Key Metadata
- **Authors:** Philippe Laban et al.
- **Year:** 2021
- **Venue:** arXiv
- **Core Contribution:** Introduction of SUMMACConv, an effective method for using NLI models to detect inconsistencies in summarization, achieving a state-of-the-art balanced accuracy of 74.4%.

## Section Summaries

### Abstract
In the summarization domain, a key requirement for summaries is to be factually consistent with the input document. Previous work has found that natural language inference (NLI) models do not perform competitively when applied to inconsistency detection. In this work, we revisit the use of NLI for inconsistency detection, finding that past work suffered from a mismatch in input granularity between NLI datasets (sentence-level) and inconsistency detection (document-level). We provide a highly effective and lightweight method called SUMMACConv that enables NLI models to be successfully used for this task by segmenting documents into sentence units and aggregating scores between pairs of sentences. On our newly introduced benchmark called SUMMAC (Summary Consistency) consisting of six large inconsistency detection datasets, SUMMACConv obtains state-of-the-art results with a balanced accuracy of 74.4%, a 5% point improvement compared to prior work.

### Introduction & Motivation
Current summarization models often generate factually inconsistent outputs, a significant issue considering human and automatic evaluations of summarization quality. Inconsistencies manifest as inversions, incorrect entity usage, or hallucinations. While NLI models have been explored for inconsistency detection, prior attempts failed due to a mismatch in the input granularity, as NLI datasets are typically highlighted at the sentence level while inconsistencies may span documents. This paper aims to bridge this gap by proposing a refined approach using NLI models that involves sentence pair evaluations for more accurate inconsistency detection.

### Methodology
The authors propose two models—SUMMACZS and SUMMACConv—for inconsistency detection based on NLI models. Both models start by generating an NLI Pair Matrix from (document, summary) pairs.

1. **NLI Pair Matrix Generation:**
   - Split the document into M sentences (D1, D2, ..., DM) and summary into N sentences (S1, S2, ..., SN).
   - Each combination (Di, Sj) is fed into an NLI model, yielding entailment scores \(E_{ij}\). The matrix constructed is \(E \in \mathbb{R}^{M \times N}\).
   
2. **SUMMACZS (Zero-Shot):**
   - Reduces the pair matrix by obtaining the maximum values from each column and then computes their mean, resulting in a single score. This simple aggregation approach can be sensitive to outliers.

3. **SUMMACConv (Convolutional):**
   - Creates histograms (binning into H categories) of entailment scores for each summary sentence and applies a 1-D convolution layer to aggregate the values into a single score. The convolution is trained end-to-end using a cross-entropy loss, with the Adam optimizer, a batch size of 32, learning rate of \(10^{-2}\), and hyperparameter H set to 50 based on validation performance.

The models rely on preprocessing to segment documents correctly and evaluate each sentence’s contribution to summarization consistency.

### Experiments & Results
The authors construct the **SUMMAC Benchmark**, comprising six datasets:

- **CoGenSumm:** 400 validation/test pairs, ~49.8% positive labels.
- **XSumFaith:** 1281 validation/test pairs, ~10.2% positive labels.
- **Polytope:** 1250 validation/test pairs, ~6.6% positive labels.
- **FactCC:** 1250 validation/test pairs, ~85.0% positive labels.
- **SummEval:** 634 validation/test pairs, ~90.6% positive labels.
- **FRANK:** 503 validation/test pairs, ~33.2% positive labels.

Metrics for evaluation include balanced accuracy and ROC-AUC. The results show:

| Model         | Performance    |
|---------------|-----------------|
| NER-Overlap   | 53.0            |
| MNLI-doc      | 57.6            |
| SUMMACZS      | 70.4            |
| SUMMACConv    | **74.4**        |

Statistical significance testing reveals that proceeds from both models significantly outperform traditional baseline methods (p < 0.05).

The computational efficiency for the SUMMAC models is comparably lower than baselines, processing approximately 430 documents per minute, but their performance across a variety of datasets was more robust, indicating the tradeoff between speed and accuracy is favorable for SUMMAC models.

### Discussion & Conclusion
The study reveals the practical applicability of NLI-based models in detecting summary inconsistencies, achieving a significant improvement over previous methods. Future work is suggested to enhance model interpretability and expand to other domains beyond news summarization, such as legal text analysis or scholarly work. Integrating advanced NLI models might further enhance performance and reliability in summarization tasks.

## Key Contributions
- Introduction of SUMMACConv and SUMMACZS models for inconsistency detection that utilize NLI techniques effectively.
- Development of a standardized benchmark dataset, SUMMAC, comprising the six largest summary inconsistency detection datasets.
- Demonstrated significant improvements in detection accuracy compared to previously established models.

## Potential Relevance
The methods and findings from this paper highlight a novel approach to using NLI models for tasks involving factual consistency, which could inform the development of more robust hypothesis tests in summarization-related research. Additionally, the benchmark could be useful for comparative studies in future model evaluations.