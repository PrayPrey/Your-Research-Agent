# Trustworthy LLMs: A Survey and Guideline for Evaluating Large Language Models' Alignment

## Key Metadata
- **Authors:** Yang Liu et al.
- **Year:** 2023
- **Venue:** arXiv 2308.05374
- **Core Contribution:** 7-category taxonomy of LLM trustworthiness with per-dimension gap analysis across aligned and unaligned models.

## Section Summaries

### Abstract
We present a comprehensive survey of trustworthiness in large language models, organizing the landscape into 7 categories: truthfulness, calibration, robustness, fairness, bias, toxicity, and privacy. We review evaluation methods, datasets, and findings for each category, and identify gaps where current aligned models show unexpected vulnerabilities despite RLHF training.

### Introduction & Motivation
As LLMs are increasingly deployed in high-stakes contexts, understanding their trustworthiness properties becomes critical. The survey aims to unify fragmented literature across safety, fairness, robustness, and interpretability into a coherent taxonomy, and to highlight where alignment training helps vs. creates new problems.

### Methodology
Survey methodology: systematic review of papers from 2020-2023 covering LLM trustworthiness. 7 categories defined with distinct evaluation criteria: (1) Truthfulness: factual accuracy, hallucination rates; (2) Calibration: confidence-accuracy correspondence; (3) Robustness: performance under adversarial/distribution shift; (4) Fairness: demographic parity, stereotype reduction; (5) Bias: systematic skew toward groups; (6) Toxicity: harmful/offensive output generation; (7) Privacy: memorization and extraction risks. For each category, surveys: current benchmarks, state-of-the-art methods, RLHF/instruction-tuning effects, and remaining gaps.

### Experiments & Results
Key findings across the 7 dimensions: (1) Truthfulness improves with scale and RLHF, but GPT-4 still hallucinates ~20% on complex factual queries; (2) Calibration: larger models are better calibrated on in-distribution but OVERCONFIDENT on OOD; (3) Robustness: aligned models (GPT-4, Claude) show surprisingly high vulnerability to adversarial perturbations — safety alignment may create brittleness; (4) Fairness: RLHF reduces explicit bias but may amplify subtle stereotyping; (5) Critical gap: NO study computes cross-dimension correlations — are these 7 properties independent? The survey explicitly lists this as a future direction.

### Discussion & Conclusion
The survey identifies that "dimension-specific gaps in aligned models" — meaning RLHF improves some dimensions while degrading others — is a consistent pattern. The key unresolved question: are trustworthiness dimensions correlated or structurally independent? If correlated, optimizing one dimension could predict others; if independent, separate evaluation of all dimensions is necessary.

## Key Contributions
- 7-category unified taxonomy of LLM trustworthiness
- Identifies RLHF-induced dimension-specific vulnerability patterns
- Explicitly calls for cross-dimension correlation analysis as future work

## Potential Relevance
This survey directly motivates Gap 1 by explicitly identifying "cross-dimension correlation analysis" as future work in the field. Its 7-category taxonomy is similar but not identical to TrustLLM's 6-category framework, providing a framework comparison opportunity. The finding that "aligned models show unexpected vulnerabilities in specific dimensions" is a key motivation for the hypothesis that trustworthiness dimensions have distinct (possibly anti-correlated) behavior under RLHF optimization.
