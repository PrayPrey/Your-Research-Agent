---
source_paper: "arxiv_2312_15058.md"
generated_at: "2026-03-15T02:46:12.046566"
model: "gpt-4o-mini"
summary_chars: 5709
---

# The State of Documentation Practices of Third-Party Machine Learning Models and Datasets

## Key Metadata
- **Authors:** Ernesto Lang Oreamuno et al.
- **Year:** 2023
- **Venue:** IEEE
- **Core Contribution:** This study evaluates the documentation practices of third-party machine learning models and datasets stored in Hugging Face, highlighting significant gaps in the completeness and quality of the documentation.

## Section Summaries

### Abstract
Model stores offer third-party ML models and datasets for easy project integration, minimizing coding efforts. One might hope to find detailed specifications of these models and datasets in the documentation, leveraging documentation standards such as model and dataset cards. In this study, we use statistical analysis and hybrid card sorting to assess the state of the practice of documenting model cards and dataset cards in one of the largest model stores in use today–Hugging Face (HF). Our findings show that only 21,902 models (39.62%) and 1,925 datasets (28.48%) have documentation. Furthermore, we observe inconsistency in ethics and transparency-related documentation for ML models and datasets.

### Introduction & Motivation
The significance of documentation for machine learning models and datasets cannot be overstated, as inadequate documentation hampers reusability and obscures ethical concerns, resulting in potential biases and compliance issues. Previous studies have indicated insufficient documentation in various contexts, but the literature lacks a comprehensive analysis specifically targeting model and dataset documentation in Hugging Face (HF). This paper aims to bridge this gap by qualitatively assessing 378 model cards and 321 dataset cards to evaluate compliance with existing documentation standards and investigate the completeness and quality of the provided information.

### Methodology
The study employed two main approaches to analyze model and dataset documentation in HF. First, model and dataset cards were scraped randomly from HF, filtering to keep only the non-empty entries. The final counts were 21,902 model cards from 55,280 models and 1,925 dataset cards from 6,758 datasets. 

A hybrid card sorting technique was then used for a random sample of 378 model cards, enabling categorization based on predetermined sections from the model card standard (e.g., Model Description, Training Data, Intended Use). Cohen's Kappa for inter-rater agreement during this phase reached 79%. 

For the dataset cards, a similar deductive coding process was applied to a random sample of 321 datasets, with agreement at 91% for inter-rater accuracy. 

The analysis sought to determine the presence of required sections, match between section titles and content, and completeness of information according to model and dataset card standards. Each section's compliance was quantitatively assessed, recording the percentage for content match, empty sections, and mismatched content.

### Experiments & Results
The analysis revealed that a substantial percentage of models (60.38%) lacked documentation, indicating significant gaps in the documentation practices of HF users. Among the sections, Model Details (93.7%), Training Data (57.7%), and Intended Use (52.4%) were the most consistently documented. However, critical areas such as Metrics (6.9%) and Ethical Considerations (0.3%) were alarmingly underreported.

For dataset cards, an even higher percentage (71.52%) were undocumented, with major sections such as Dataset Description (68%) and Dataset Structure (67%) showing more complete documentation compared to others like Dataset Creation (9%) and Considerations For Using The Data (e.g., 16%). Across the analyzed subsections, over half were empty in at least 57% of the cards, revealing severe deficiencies in both models and datasets documentation.

Main result summary:

| Category          | % Documented Models | % Documented Datasets | Observations               |
|-------------------|---------------------|-----------------------|----------------------------|
| Model Cards        | 39.62%              | N/A                   | High absence of Ethical & Metrics details|
| Dataset Cards      | N/A                 | 28.48%                | Major gaps in core sections  |
| Missing Ethical Considerations  | 0.3% | 57% empty in key subsections  | Ethical Information lacking   |

### Discussion & Conclusion
This research emphasizes the inadequate documentation practices observed within Hugging Face's model and dataset repositories, particularly concerning ethical considerations and performance metrics. The findings call for researchers and practitioners to advocate for improved documentation standards, as current practices do not sufficiently meet user needs or ethical liabilities. Future work should explore deeper reasons for these shortcomings and propose enhancements to documentation frameworks.

## Key Contributions
- A comprehensive quantitative analysis of model and dataset documentation practices within Hugging Face.
- Identification of significant gaps in the completeness and quality of documentation, particularly in ethical considerations.
- Recommendations for improved tools and practices to enhance documentation standards and compliance in machine learning resources.

## Potential Relevance
Understanding the gaps in documentation highlighted in this paper can inform future research hypotheses regarding the integration and reusability of third-party ML models and datasets. The findings regarding ethical documentation practices may serve as a basis for developing guidelines or standards in the ML community, potentially influencing both academic and industry practices.