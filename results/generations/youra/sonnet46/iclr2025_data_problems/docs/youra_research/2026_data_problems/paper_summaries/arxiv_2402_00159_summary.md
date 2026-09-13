---
source_paper: "arxiv_2402_00159.md"
generated_at: "2026-03-14T16:47:41.029224"
model: "gpt-4o-mini"
summary_chars: 5852
---

# Dolma : an Open Corpus of Three Trillion Tokens for Language Model Pretraining Research

## Key Metadata
- **Authors:** Luca Soldaini et al.
- **Year:** 2024
- **Venue:** ArXiv
- **Core Contribution:** Release of Dolma, a diverse three-trillion-token corpus for language model pretraining.

## Section Summaries

### Abstract
Information about pretraining corpora used to train the current best-performing language models is seldom discussed: commercial models rarely detail their data, and even open models are often released without accompanying training data or recipes to reproduce them. As a result, it is challenging to conduct and advance scientific research on language modeling, such as understanding how training data impacts model capabilities and limitations. To facilitate scientific research on language model pretraining, we curate and release Dolma, a three-trillion-token English corpus, built from a diverse mixture of web content, scientific papers, code, public-domain books, social media, and encyclopedic materials. We extensively document Dolma, including its design principles, details about its construction, and a summary of its contents. We present analyses and experimental results on intermediate states of Dolma to share what we have learned about important data curation practices. Finally, we open-source our data curation toolkit to enable reproduction of our work as well as support further research in large-scale data curation.

### Introduction & Motivation
As language models grow central to various NLP tasks, transparency regarding their training data is crucial. Current practices are often opaque, limiting research opportunities and hindering understanding of how data influences model capabilities. This paper introduces Dolma, which collects three trillion tokens from diverse sources, aiming to improve scientific inquiry by providing a well-documented, openly accessible corpus. The motivation includes facilitating better-informed decisions for model developers and users, catalyzing research on the effects of corpus composition on model behavior, and enhancing reproducibility in NLP research.

### Methodology
Dolma is constructed with a diverse set of data, including sources such as Common Crawl, GitHub, Reddit, Semantic Scholar, Wikipedia, and Project Gutenberg, resulting in a corpus of approximately 200 TB of raw text distilled into 11 TB of curated data (3 trillion tokens). The construction is achieved through the **Dolma Toolkit**, which includes:

1. **Filtering pipeline** that applies methods like language detection, low-quality content detection, toxicity screening, and removal of personally identifiable information (PII).
2. **Mixing operations** that consolidate and deduplicate the dataset using probabilistic data structures like Bloom filters to ensure efficient access and reduced redundancy.

Key hyperparameters used in baseline models include a **learning rate of 1e-5**, **batch sizes of 64**, and training up to **150 billion tokens** following the scaling laws suggested by Hoffmann et al. (2022). The main loss function used for model training is standard cross-entropy loss, where the model's predictions \(\hat{y}\) aim to minimize:
\[
L(y, \hat{y}) = -\sum_{i=1}^{C} y_i \log(\hat{y}_i)
\]
where \(C\) is the number of classes in the dataset.

The inputs are formatted as plain text documents, with a preprocessing pipeline to ensure the removal of non-English content and other undesirable artifacts.

### Experiments & Results
Dolma's token diversity is measured across several datasets through evaluations on performance metrics, such as **perplexity**, **accuracy**, and other metrics tied to comprehension and reasoning tasks tested against established baselines (including models trained on C4 and Pile).

A detailed ablation study was carried out using a 1.2 billion parameter model from the OLMo family, revealing quantifiable impacts of filtering interventions on model performances across various tasks. Notably, while evaluating on 8 different tasks including HellaSwag and ARC, OLMo-1B, the model trained on Dolma, demonstrated an **average accuracy** of \(61\%\). 

The experiments were conducted across multiple splits, with training on approximately \(2\) trillion tokens and verification against the following dataset splits: 

- **Train/Val/Test**: 90%/5%/5% for multiple datasets like HellaSwag and ARC-Common.
  
The results (Table 2, comparison metrics) indicated that OLMo-1B performed competitively against other baseline models like TinyLlama and StableLM2, resulting in perceptible reductions in perplexity when trained on diverse token distributions.

### Discussion & Conclusion
The analyses highlight that transparency and rigor in curation practice can significantly impact the performance of language models. However, limitations persist, including the corpus being primarily English-only and challenges in capturing the representational breadth of language usage across diverse contexts. The authors advocate for continued research efforts to expand beyond English and refine curation processes. Dolma and the accompanying toolkit are positioned as resources for future improvements in data stewardship and model training.

## Key Contributions
- Release of the Dolma Corpus, featuring three trillion tokens from diverse data sources.
- Development and open-sourcing of the Dolma Toolkit for data curation.
- Extensive analysis of the data curation pipeline leading to recommendations for future practices.

## Potential Relevance
Dolma provides an extensive framework for understanding data impacts on language model performance, presenting a significant opportunity for hypothesis development in the NLP research domain, particularly regarding data composition and its broader implications on model behavior and societal integration.