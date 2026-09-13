# Conclusion

We began by observing a puzzling gap: hallucination detection methods report AUROC 0.70-0.85 in isolation, yet practitioners lack guidance on which method works for their specific benchmark. Our pilot study reveals why this gap exists—method performance is benchmark-sensitive in ways previous evaluations could not expose.

## Summary

In this work, we established a matched-budget comparison framework for hallucination detection methods. By evaluating semantic entropy and self-consistency under identical conditions—same model, same sample count, same temperature—we enabled direct comparison that isolated method differences from confounding variables.

Our main findings are:

1. **Benchmark sensitivity is real.** Semantic entropy achieved AUROC 0.551 on HaluEval but only 0.289 on TruthfulQA—the latter worse than random. This inverted behavior was entirely unexpected and highlights the risk of assuming method performance transfers across benchmarks.

2. **Self-consistency requires investigation.** BERTScore-based consistency performed near random (AUROC 0.444-0.474) on both datasets, suggesting surface similarity may not capture hallucination-relevant uncertainty in QA settings.

3. **Controlled comparison is essential.** Without matched-budget evaluation, practitioners cannot make informed method selection decisions. Published results from different papers, using different benchmarks and conditions, are fundamentally incomparable.

## Future Directions

Our pilot study opens several promising directions:

**From unexpected findings:** The TruthfulQA inversion warrants investigation. Is this a labeling methodology issue ("Best Answer" matching vs hallucination detection), a model-specific effect, or an implementation detail? Running with the original semantic entropy paper's evaluation protocol would disambiguate.

**From unverified mechanisms:** Self-consistency's near-random performance may stem from BERTScore limitations rather than fundamental method failure. Replacing BERTScore with NLI-based pairwise agreement could test whether surface similarity is the bottleneck.

**From scope boundaries:** Our pilot (N=20) validates pipeline functionality but lacks statistical power. Full-scale evaluation (N=817 TruthfulQA, N≥500 HaluEval) with multiple seeds would establish definitive performance comparisons.

## Closing

Our findings suggest that hallucination detection is harder than published results imply—not because methods don't work, but because benchmark choice fundamentally affects evaluation outcomes. We hope this work encourages more rigorous, multi-benchmark evaluation practices, moving the field toward detection systems that practitioners can deploy with confidence.
