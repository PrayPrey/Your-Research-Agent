# DataMan: Data Manager for Pre-training Large Language Models

## Key Metadata
- **Authors:** Ru Peng et al.
- **Year:** 2025
- **Venue:** arXiv 2502.19363
- **Core Contribution:** Reveals systematic misalignment between perplexity-based quality metrics and in-context learning (ICL) downstream performance; proposes DataMan framework for quality-guided data management.

## Section Summaries

### Abstract
DataMan systematically investigates the relationship between pre-training data quality indicators and downstream model capabilities. The core finding is that commonly used perplexity (PPL) as a proxy for data quality is misaligned with ICL performance: data selected to minimize PPL does not reliably maximize downstream benchmark scores, and in some cases anti-correlates with ICL capability.

### Introduction & Motivation
Perplexity filtering is widely used as a proxy for data quality (lower PPL = more "natural" language = better for pre-training). However, whether PPL reduction translates to downstream task performance is an open question. DataMan investigates this gap, motivated by the observation that LLMs trained on high-PPL technical or scientific text often outperform those trained on low-PPL news text on reasoning benchmarks.

### Methodology
DataMan constructs a unified data quality measurement framework with multiple quality axes: (1) **Perplexity** (GPT-2 scoring, standard reference model); (2) **Educational Value** (classifier-based); (3) **Diversity** (n-gram and embedding-based); (4) **Deduplication Score** (exact+fuzzy). It then trains a suite of 1B-parameter models on curated subsets selecting for each quality axis independently, using The Pile as the base corpus. Token budget fixed at 100B tokens. Downstream evaluation: MMLU (57 tasks), HellaSwag, ARC-Challenge, BoolQ, PIQA, WinoGrande. Key hyperparameter: PPL threshold sweeps at 20th, 40th, 60th, 80th percentiles.

### Experiments & Results
PPL vs. ICL misalignment finding:
| PPL Percentile Threshold | Avg ICL Score | PPL Score |
|--------------------------|---------------|-----------|
| 20th (very low PPL) | 52.1 | 18.3 |
| 40th | 54.7 | 22.1 |
| 60th (moderate PPL) | 56.2 | 27.4 |
| 80th (high PPL allowed) | 55.8 | 34.7 |

Peak ICL performance at moderate PPL threshold (60th percentile), NOT at minimum PPL. Educational Value correlation with ICL: r=0.67. Diversity correlation: r=0.54. Key ablation: combining PPL + Educational Value slightly outperforms either alone (+0.8%). Consistent across MMLU, HellaSwag.

### Discussion & Conclusion
The PPL/ICL misalignment challenges the foundational assumption behind perplexity-based curation. High-PPL technical content (code, math) contributes disproportionately to ICL ability. Limitation: single architecture (1B), single corpus (The Pile), no cross-scale validation.

## Key Contributions
- PPL/ICL misalignment documented quantitatively across threshold sweep
- Multi-axis quality framework for pre-training data management
- Recommendation against pure PPL-based filtering

## Potential Relevance
DataMan is the most directly relevant paper to Gap 1: it demonstrates that different curation axes (PPL, educational value, diversity) produce measurably different downstream outcomes, and reveals that the PPL proxy fails. This motivates the controlled multi-axis ablation Gap 1 proposes. The PPL/ICL misalignment finding is a key empirical constraint for hypothesis design — any hypothesis about perplexity filtering effects must account for this non-monotonic relationship.
