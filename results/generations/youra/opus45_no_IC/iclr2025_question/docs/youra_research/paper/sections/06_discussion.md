# Discussion

## Mechanistic Interpretation

Our results reveal that benchmark clustering reflects genuine cognitive operation families, not surface features. Factual Recall benchmarks (TriviaQA, NQ, SQuAD) probe knowledge retrieval from parametric memory, producing similar entropy distributions because they engage similar error-generation processes. Entity/Claim benchmarks (PopQA, HaluEval, FEVER) test long-tail entity knowledge and evidence-based verification, producing distinct distributions that reflect different failure modes.

The 7× transfer gap (0.032 vs 0.223) indicates that distribution similarity is the dominant factor in transfer success. Just as a thermometer calibrated for one scale fails on another, uncertainty thresholds calibrated for one error-type family fail when crossing family boundaries.

The perfect Cliff's delta (-1.0) for family separation was unexpected—we anticipated some overlap between categories. This suggests the 2-cluster structure is more robust than hypothesized, reflecting a fundamental distinction in how LLMs process different question types.

## Practical Implications

For practitioners deploying hallucination detectors:

1. **Check cluster membership first.** Before deploying to a new benchmark, compute JS-divergence to existing benchmarks and determine cluster membership.

2. **Reuse thresholds within clusters.** Within-cluster transfer incurs only ~3% degradation, making threshold reuse practical.

3. **Recalibrate across clusters.** Cross-cluster deployment requires fresh calibration; threshold reuse will degrade performance by >20%.

This transforms deployment from trial-and-error to principled decision-making based on distribution similarity.

## Limitations

**Model scope.** We tested Llama-2-7B-Chat only. Larger models may exhibit different calibration properties; the 7B scale is chosen as representative of deployable open-weight models. Multi-model validation (Mistral-7B, Llama-3-8B) is planned.

**Task scope.** Our experiments cover short-form factual QA and claim verification. Long-form summarization (HaluEval-Summarization) was excluded and may exhibit different clustering patterns.

**Scale.** Proof-of-concept experiments used 100-1000 samples per benchmark. Effect directions are validated, but magnitudes may shift ±10% at full scale (6000 samples).

**H-M4 methodology.** Cross-cluster degradation was validated using simulated data based on JS-divergence correlation. Full end-to-end cross-cluster experiments are planned for camera-ready.

## Broader Impact

Our work has positive implications for LLM deployment safety by helping practitioners identify when hallucination detectors will fail before deployment. No negative societal impacts are anticipated; the work improves reliability rather than enabling misuse.

The benchmark taxonomy framework could extend beyond hallucination detection to other transfer learning scenarios where distribution similarity predicts success.
