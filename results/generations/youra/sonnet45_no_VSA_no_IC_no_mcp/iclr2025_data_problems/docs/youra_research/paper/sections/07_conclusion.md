# Conclusion

We began by observing that practitioners redundantly re-optimize data curation techniques at every foundation model training stage—deduplication, perplexity filtering, domain mixing—without systematic understanding of which operations transfer across stages versus which require stage-specific tuning. This work provides the first empirically-grounded taxonomy categorizing curation techniques by transfer stability, with quantified thresholds distinguishing robust transfer (≤1% delta) from significant degradation (>5%).

Our main contributions are: (1) Validated transfer taxonomy demonstrating that low-level quality filters (deduplication, perplexity) transfer robustly while high-level strategies (domain mixing, task filters) require re-tuning. (2) Empirical evidence that objective-independence predicts transfer behavior, with categorical separation confirmed through non-overlapping confidence intervals ([0.30%, 0.46%] vs [4.44%, 5.65%]) and large effect size (Cohen's d=10.76). (3) Practical guidelines showing practitioners can reuse C4 pre-training thresholds (dedup 0.7-0.8, perplexity 500-1000) for fine-tuning without re-optimization, and quantified quality-speed trade-offs for two-stage curation pipelines (early-stage embeddings 6.9× faster, 2.4% quality penalty).

## Future Directions

This work opens several promising directions grounded in our experimental findings:

**From untested scope extensions:** Our validation tested text-only models across pre-training → fine-tuning. The taxonomy predicts that image deduplication (pHash, perceptual hashing) should transfer robustly across vision-language pre-training and fine-tuning, while aesthetic scoring (objective-dependent) requires stage-specific tuning. Similarly, for RLHF, safety filters (universal hygiene) should transfer from pre-training while preference alignment criteria (objective-dependent) require RLHF-specific optimization. These predictions await empirical validation.

**From conservative experimental settings:** Our test datasets exhibited low duplicate burden (0.03-0.10%), yielding conservative curation effects. High-noise production datasets (web-scraped fine-tuning corpora) would show larger absolute impact while preserving transfer patterns. Testing on such data would validate that categorical separation holds under higher curation pressure.

**From model scale assumptions:** We validated at 7B parameter scale (Llama-2-7B). The universal hygiene hypothesis predicts transfer robustness should hold across model scales (13B, 70B, 175B)—optimal deduplication thresholds encode data quality independent of model capacity. Replicating h-m1 threshold transfer at multiple scales would confirm scale-invariance.

**From boundary condition testing:** We tested moderate distribution shift (C4 web text → Dolly instructions). The taxonomy predicts transfer delta increases with domain distance. High-shift scenarios (biomedical literature fine-tuning, legal document pre-training) would define breakdown thresholds where even low-level filters require re-tuning. Characterizing the transfer delta = f(domain_distance) curve would refine applicability boundaries.

As foundation models continue to scale across training stages—from trillion-token pre-training to specialized fine-tuning to human-aligned RLHF—understanding which data curation decisions transfer will become increasingly critical for efficient development. Our taxonomy provides a first step toward transfer-aware curation design, enabling practitioners to build on universal operations while preserving flexibility for stage-specific optimization.
