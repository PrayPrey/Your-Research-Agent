# 2. Related Work

We organize related work around three themes, concluding each with the limitation our work addresses.

## 2.1 Perplexity-Based Quality Filtering

Perplexity computed by a reference language model (typically GPT-2 or a domain-matched model) is a widely used proxy for training data quality. ProX [Zhou et al., 2024] demonstrates that per-example programmatic text refinement, which includes a perplexity-informed quality signal, improves downstream benchmarks by approximately 2% across C4, DCLM, and FineWeb corpora. REWIRE [Nguyen et al., 2025] shows that transforming discarded low-quality documents (rather than simply filtering them) yields 1.0–2.5 percentage point improvements across 22 tasks at 1–7B scale.

Critically, DataMan [Peng et al., 2025] identifies a misalignment between perplexity-based quality and downstream in-context learning (ICL) performance: the token mixture that minimizes pre-training perplexity is not the same mixture that maximizes ICL scores. This PPL/ICL misalignment motivates careful threshold selection. However, DataMan evaluates this misalignment at a single model scale. Our work extends this line of inquiry by testing whether the optimal threshold in the PPL/ICL trade-off shifts with model scale — finding that it does, and dramatically so.

## 2.2 Deduplication Strategies

Near-duplicate removal is a standard component of pre-training data pipelines. SoftDedup [He et al., 2024] shows that n-gram commonness-based soft weighting of near-duplicates improves few-shot performance by 1.77% over hard deduplication on a fixed-scale model. FineWeb2 [Penedo et al., 2025] provides principled multi-language curation ablations including deduplication tuning, reporting improved benchmark performance across languages.

Both works evaluate deduplication effects at a single model scale. Our experiment includes two deduplication levels (MinHash Jaccard J=0.7 strict, J=0.9 loose) as a secondary axis in the factorial design. While our primary gate focused on the PPL × scale interaction, the experimental data exists for a post-hoc dedup × scale analysis — a direction we identify as immediate future work.

## 2.3 Scalable Curation Ablation Methodology

The computational expense of from-scratch pre-training ablations motivates work on efficient approximation. Na et al. [2024] propose training small proxy models and merging checkpoints to approximate ablation results, reporting Spearman r=0.81 correlation between proxy-model performance and full-scale benchmark outcomes. Chinchilla scaling laws [Hoffmann et al., 2022] provide theoretical grounding for relating compute-optimal training configurations across scales.

Our h-e1 proof-of-concept experiment (7M/16M proxy models, 200 training steps) produced p=1.0 and η²≈0 with all models at the MMLU floor — no statistical signal. This directly contradicts the applicability of Na et al.'s proxy-model approach for Scale × Curation interaction studies: below a minimum capacity threshold (empirically, below approximately 14M parameters with a 2.2× scale ratio), the interaction cannot manifest because neither model is large enough to exhibit the capacity-quality trade-off behavior. Curation ablations at sufficient model scale are necessary for studying scale-dependent effects.

## 2.4 Our Position

We contribute the first controlled factorial experiment that directly tests the Scale × Curation interaction in LLM pre-training. Unlike prior work, which either (a) evaluates curation at a single scale, (b) assumes scale-independence, or (c) uses proxy models too small to exhibit scale-dependent effects, we run a 24-run factorial experiment at 14M/31M parameter scales with real FineWeb data, real GPT-2 PPL scoring, and standard evaluation. The resulting τ*(14M)=20 vs. τ*(31M)=50 finding provides the first empirical evidence that optimal curation thresholds are model-scale-dependent.
