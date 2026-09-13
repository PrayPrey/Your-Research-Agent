# Conclusion

A hallucination detector calibrated on TriviaQA degrades by 3% on SQuAD—but by 22% on PopQA. This paper explains why: cluster membership, determined by uncertainty distribution similarity, predicts transfer success.

We presented the first systematic framework for predicting when hallucination detector calibration transfers across benchmarks. Our key contributions are:

1. **Benchmark taxonomy via uncertainty distributions.** QA benchmarks cluster into two empirically discoverable families with silhouette score 0.82, reflecting distinct error-generation processes (factual recall vs entity/claim verification).

2. **Quantified transfer boundaries.** Within-cluster transfer succeeds with 3.2% AUROC degradation; cross-cluster transfer fails with 22.3% degradation—a 7× gap that validates our conditional transfer hypothesis.

3. **Practical transfer criterion.** JS-divergence clustering provides an actionable criterion: check cluster membership before deployment, and recalibrate only when crossing cluster boundaries.

These findings transform hallucination detector deployment from trial-and-error to principled decision-making. Practitioners can predict transfer success a priori, reducing deployment cost while maintaining detection quality.

Future work will extend this framework to larger models (70B+), additional benchmark families (summarization, dialogue), and API-only models requiring alternative uncertainty methods. The benchmark taxonomy approach may generalize beyond hallucination detection to other transfer learning scenarios where distribution similarity predicts success.
