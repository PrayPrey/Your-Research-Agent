# Conclusion

We began by observing that quality filtering—the foundation of modern LLM data curation—might not be contamination-neutral. Our work confirms this concern and quantifies its scope: perplexity-based filtering systematically amplifies benchmark contamination, and the resulting contaminated examples are causally necessary for benchmark performance.

## Summary

This work establishes the first systematic connection between data curation strategies, benchmark contamination, and attribution methods. Our key contributions are:

**Contamination Contribution Ratio (CCR):** We introduced a metric that combines n-gram contamination detection with TRAK attribution to quantify benchmark-specific influence from contaminated training examples. Synthetic injection experiments validated CCR as calibrated (R² = 0.9998).

**Curation-Contamination Amplification:** Perplexity filtering increases CCR by 0.1594 relative to random sampling (p < 0.0001), demonstrating that quality filtering concentrates benchmark-overlapping content rather than excluding it.

**Causal Necessity:** High-CCR examples are not merely correlated with benchmark performance—removing them causes 1.97× greater accuracy degradation than random removal. This proves contaminated examples provide irreplaceable benchmark-specific signal.

**Influence Fragility Ratio (IFR):** Contaminated examples exhibit 4.1× higher IFR than non-contaminated examples, revealing they are structurally necessary and cannot be substituted by other training content.

## Future Directions

This work opens several promising research directions grounded in our experimental findings:

**Sub-document Attribution:** The weaker-than-expected IFR-redundancy correlation (ρ = -0.11 vs. hypothesized ρ < -0.5) suggests contamination operates at span rather than document level. Future work should compute span-level TRAK scores and measure redundancy on benchmark-overlapping spans specifically.

**Document-Length Confounds:** Our experiments did not stratify by document length. Future work should verify that CCR differences persist within length strata, ruling out length as a confound for the perplexity-contamination correlation.

**Clean Benchmark Verification:** Our Amplification Index computation assumes MMLU-Redux has <0.01% overlap with training corpora. Explicit MinHash and embedding-based audit would strengthen AI as a reliable metric.

**Scaling Experiments:** Results validated at 1B scale; TRAK with LoGra speedups enables extension to 7B–70B models where contamination dynamics may differ.

**Contamination-Aware Curation:** Armed with CCR measurement, future work can develop filtering algorithms that explicitly balance quality selection with contamination attenuation—achieving the benefits of perplexity filtering while preserving evaluation integrity.

## Closing

Quality filtering, long assumed to uniformly improve training data, introduces systematic bias that inflates benchmark scores through contamination amplification. Our metrics—CCR, AI, and IFR—provide tools to measure this effect, enabling contamination-aware evaluation and curation. As the field increasingly relies on benchmark performance to guide model development, understanding what benchmarks actually measure becomes essential. We hope this work contributes to more trustworthy evaluation of language model capabilities.
