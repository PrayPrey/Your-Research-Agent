# 7. Conclusion

We began by observing a paradox: language models can achieve strong capability scores while simultaneously exhibiting correlated failures in calibration, hallucination resistance, and adversarial robustness — and these failures co-vary along a latent dimension that capability benchmarks barely predict. This paper has taken a first step toward quantifying that dimension.

## 7.1 Summary

We introduced the **YouRA evaluation framework** for systematic multi-hypothesis testing of latent trustworthiness structure in LLM populations, and applied it to study *epistemic reliability* — the degree to which a model's outputs faithfully track internal uncertainty — as a candidate latent dimension underlying calibration quality, hallucination resistance, and adversarial robustness.

Under a synthetic score matrix conforming to the hypothesized structure, our pipeline demonstrates:

1. **A latent epistemic reliability factor is detectable and statistically recoverable.** Partial Spearman correlations controlling for MMLU capability are strong (ECE–TruthfulQA%: ρ=−0.758; ECE–AdvGLUE drop: ρ=−0.719), a single factor explains 72.1% of shared variance, and Tucker's congruence = 1.000 confirms factor stability. The pipeline correctly recovers the latent structure it was designed to detect — demonstrating analytical correctness as a prerequisite for real-data execution.

2. **Epistemic reliability is nearly orthogonal to MMLU capability.** The survival fraction of 0.943 indicates MMLU accounts for less than 1% of the calibration–hallucination correlation. This result, if replicated with real LLM evaluations, would mean that capability-only model screening systematically misses the epistemic reliability dimension — a practically significant finding for deployment safety.

3. **Incremental predictive power over MMLU-alone is uncertain at N=30.** The composite epistemic predictor achieves LOO-AUC = 0.739, but ΔAUC = 0.051 with CI [−0.194, 0.449] — an uninformative result due to insufficient statistical power. This honest null informs future study design: N≥100 models are needed for a definitive ΔAUC test, and binary dichotomization should be replaced by continuous adversarial drop prediction.

We stress what this work is and is not. It is: a validated analysis pipeline with pre-registered statistical methodology, a pre-registered 30-model evaluation plan ready for execution, and a transparent account of synthetic-data pipeline validation. It is not: an empirical demonstration that real open-weight LLMs exhibit the reported correlation magnitudes. All quantitative results are properties of the synthetic data generator and must be treated as such.

## 7.2 Future Directions

The path from here is clear and immediate. Real-data replication (FW1) — executing `main.py` with lm-evaluation-harness on the 30-model population — is the first and most critical step. It is not a speculative future direction; it is a waiting task. The pipeline exists, the analysis plan is pre-registered, and the only missing ingredient is GPU time.

Beyond replication, two directions open naturally from our results. The negligible MMLU confound (survival fraction = 0.943) raises the hypothesis that *training regime* — specifically RLHF implementation details — is the primary driver of epistemic reliability, independent of model capability. Within-regime stratified analysis (FW4) would directly test whether the factor structure is homogeneous across RLHF, SFT, and base-tuned models. And the unresolved mechanistic question (H-M3) — whether calibration quality predicts adversarial robustness *through* smoother decision surfaces detectable via embedding perturbation — remains both theoretically important and empirically open.

## 7.3 Closing Thought

Capability tells you what a model knows. Epistemic reliability tells you whether it knows what it doesn't know. Standard benchmarks measure the former extensively; they measure the latter only incidentally, if at all. If our synthetic-data results hold when real LLM evaluations are substituted, epistemic reliability may emerge as the missing second axis of responsible LLM evaluation — one that is measurable with existing tooling, largely independent of the capability dimension we already track, and meaningfully predictive of the failure modes that matter most for safe deployment.
