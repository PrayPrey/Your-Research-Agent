# Paper Summary: Semantic Uncertainty (Semantic Entropy)
**arXiv:** 2302.09664 | **Authors:** Kuhn, Gal, Farquhar | **Year:** 2023 | **Citations:** 881

## Key Contributions
- Semantic entropy (SE): clusters N sampled outputs by semantic equivalence (NLI), computes entropy over cluster-level probabilities
- First unsupervised, calibration-free hallucination detector for free-text LLM outputs
- Published in Nature 2024; gold standard for sequence-level UQ
- Outperforms predictive entropy (token sum) and lexical similarity on TriviaQA/NQ/BioASQ

## Methodology
- Sample N=10 outputs from model (nucleus sampling)
- Cluster by bidirectional NLI entailment (deberta-large-mnli)
- Aggregate token probabilities within each cluster (Rao-Blackwellised sum)
- Compute Shannon entropy over cluster-level probabilities
- No fine-tuning; works on any frozen generative LLM with sampling access

## Experiments & Results
- AUROC on TriviaQA: SE ~0.79 vs. predictive entropy (sum) ~0.72 vs. lexical similarity ~0.68
- Tested on Llama-1, OPT, GPT-3.5 — generalization across families confirmed at sequence level
- Key finding: semantic clustering is the differentiating factor, not aggregation per se
- Token-level aggregation within cluster = sum (Rao-Blackwellised); alternatives not ablated

## Potential Relevance to Gap 2
- Demonstrates that token SUM aggregation (within cluster) is the implicit baseline
- Does NOT compare max vs. mean vs. sum as standalone aggregation functions
- Provides AUROC as the evaluation metric — same metric usable in Gap 2 ablation
- jlko/semantic_uncertainty repo: clean evaluation pipeline for TriviaQA/NQ benchmarks
