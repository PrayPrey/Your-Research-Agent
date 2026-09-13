# 7. Conclusion

We began by noting that practitioners training model cascades at multiple scales routinely apply the same data curation recipe — the same perplexity threshold, the same deduplication aggressiveness — regardless of model capacity. Our work shows this assumption has an empirical cost. Filtering the same FineWeb corpus at τ=20 (retaining only the 3.5% lowest-perplexity documents) maximizes HellaSwag performance for a 14M-parameter model and simultaneously yields the *worst* configuration for a 31M-parameter model, which peaks at τ=50 (retaining 41.5% of documents). Data curation is not one-size-fits-all.

## 7.1 Summary

In this work, we addressed the implicit scale-independence assumption in LLM pre-training curation by running the first controlled factorial experiment that directly tests the Scale × Curation interaction. Our main contributions are:

1. **Scale-dependent optimal PPL threshold confirmed at PoC scale.** In a 24-run factorial experiment (3 PPL thresholds × 2 dedup levels × 2 model scales × 2 seeds), we find τ*(14M)=20 and τ*(31M)=50 using real FineWeb data with real GPT-2 perplexity scoring and lm-evaluation-harness HellaSwag evaluation. The direction is consistent across all conditions and seeds.

2. **Proxy model feasibility boundary established.** Our h-e1 proof-of-concept (7M/16M proxy models) produced p=1.0, η²≈0 — zero signal. This demonstrates that scale-dependent curation effects require a minimum model capacity: approximately 14M parameters with a 2.2× scale ratio appears necessary at 200–500 training steps. Scalable ablation methods using smaller proxy models [Na et al., 2024] cannot be applied to scale-dependent interaction studies without verifying this threshold.

3. **MMLU floor documented for sub-100M pre-training ablations.** MMLU 4-shot accuracy equals the random baseline for all sub-100M models at short training runs. HellaSwag 0-shot is the appropriate metric for this regime.

## 7.2 Future Directions

Our results motivate three categories of immediate extensions:

**Testing alternative explanations.** The most important untested alternative is a training duration confound: perhaps the τ* ordering reverses at convergence, with both models eventually preferring looser filtering. An extended training run (100M → 500M → 1B → 5B token budget sweep) on the h-e1-v2 protocol would test this. If τ* ordering is stable across token budgets, training duration is not the confound.

**Verifying scale generalization (Assumption A5).** The highest-risk assumption is that the 14M/31M interaction generalizes to the originally targeted 70M/160M scale. The full-scale pipeline (23/23 pytest tests passing) requires only compute to run — approximately 5 H100-days for 72 training runs at the original 50B token budget. Confirmation at 70M/160M would substantially strengthen the existence claim.

**Post-hoc dedup × scale analysis.** The existing results.csv contains 24-row data with dedup_j column (J=0.7 or 0.9). A simple group-by analysis can extract the dedup × scale interaction direction from existing data in approximately one hour — no new experiments required. This would address the P3 claim (dedup aggressiveness has opposite effects by scale) that remains inconclusive.

## 7.3 Closing Thought

As model training cascades become standard practice — releasing families of models at 7B, 13B, 70B parameters trained with the same recipe — the implicit assumption that curation is scale-independent becomes increasingly costly. Our results suggest that the optimal curation threshold may shift substantially even across a 2.2× scale difference. Optimal data curation, like optimal architecture, may need to be conditioned on model scale.
