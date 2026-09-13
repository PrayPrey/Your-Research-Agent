# Scalable Data Ablation Approximations for Language Models through Modular Training and Merging

## Key Metadata
- **Authors:** Clara Na et al.
- **Year:** 2024
- **Venue:** arXiv 2410.15661
- **Core Contribution:** Proposes efficient approximation of data ablations by training modular sub-models on data subsets and merging via parameter averaging; finds perplexity is correlated with the merged model's benchmark performance.

## Section Summaries

### Abstract
Full data ablations (training separate models on each data subset) are prohibitively expensive at scale. This paper proposes approximating ablation results by: (1) training small "expert" models on individual data components, (2) merging expert weights via parameter averaging (similar to model merging/interpolation), and (3) using the merged model's benchmark scores as proxies for the full ablation. The method reduces compute cost by ~10x while maintaining reasonable correlation with true ablation results.

### Introduction & Motivation
Data ablations are essential for principled pre-training data curation (e.g., DataComp methodology) but require training a new model per configuration — prohibitive at billion-parameter scale. The authors ask: can we approximate ablation results cheaply by leveraging modularity in model weights? This enables practitioners to screen many data configurations without full training runs.

### Methodology
**Modular Training:** Train K expert models $M_1, ..., M_K$ each on a single data source $D_1, ..., D_K$ (e.g., web, code, books, math) for T tokens each (T << full budget). **Merging:** Form composite model $M_{mix} = \sum_k \alpha_k M_k$ where $\alpha_k$ is the mixing ratio for source $D_k$. Evaluate $M_{mix}$ on downstream benchmarks as a proxy for a full model trained on $\alpha$-mixed data. **Correlation finding:** perplexity of $M_{mix}$ on held-out data correlates with benchmark scores (Spearman r=0.81 across 20 configurations). Models: 125M and 1B parameters. Data: Pile subsets (web/code/books/math). Benchmarks: MMLU, HellaSwag, ARC-C.

### Experiments & Results
| Configuration | True Full Ablation Score | Approximation Score | Error |
|--------------|--------------------------|--------------------|----|
| Balanced mix | 54.2 | 53.8 | 0.4% |
| Code-heavy | 57.1 | 56.3 | 0.8% |
| Web-only | 52.7 | 52.1 | 0.6% |

Approximation error < 1% on 18/20 configurations tested. 10x compute savings vs. full ablation. Perplexity correlation finding: r=0.81 (Spearman) between merged model PPL and benchmark score — notably, this correlation holds for the MERGED model (which reflects domain mixing effects), not for raw corpus PPL.

### Discussion & Conclusion
The method enables scalable data ablation studies. Key insight: perplexity of the merged model (trained on actual data subsets) correlates with benchmark performance, but this is distinct from using a reference LM's PPL to filter data a priori. Limitation: approximation degrades for highly non-linear mixing effects; single-source expert models may not capture interaction effects.

## Key Contributions
- Efficient data ablation approximation via modular training + parameter merging
- Perplexity correlation finding specific to merged expert models
- 10x compute reduction enabling broader ablation search

## Potential Relevance
Directly relevant to Gap 1 methodology: provides a scalable framework for running multi-configuration data ablations without prohibitive compute. The Pythia suite (which provides checkpoints at multiple scales from the same training run) could be combined with this merging approach to approximate cross-curation ablations efficiently. The distinction between merged-model PPL and corpus PPL is an important constraint for hypothesis design.
