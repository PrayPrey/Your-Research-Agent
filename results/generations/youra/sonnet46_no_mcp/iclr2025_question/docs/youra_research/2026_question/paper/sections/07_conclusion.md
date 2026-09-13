# Conclusion

We set out to test which of three state-of-the-art uncertainty quantification methods best detects hallucinations on HaluEval-QA. The answer — that none of them do — turns out to be the more informative finding.

## Summary

The core result is a mechanism failure, not a performance failure. The deberta-large-mnli NLI model that underlies semantic entropy fails to semantically aggregate short factual QA responses: 72.8% of HaluEval-QA examples receive the maximum NLI cluster count (5/5), collapsing semantic entropy to a constant signal (AUROC = 0.5000, std < 1e-6) that carries no information for hallucination discrimination. SelfCheckGPT-BERTScore produces below-random discrimination (AUROC = 0.3562), consistent with a label polarity inversion on HaluEval-QA's ChatGPT-generated confident hallucinations. Token entropy provides a stable but non-informative baseline (AUROC = 0.4829, CI spanning 0.5). Our controlled comparison framework — matched inference conditions, bootstrap CIs, explicit mechanism verification — ensures these are genuine null results with identifiable causes, not evaluation artifacts.

This work makes three contributions:

1. **First empirical quantification of NLI clustering failure on short factual QA.** We measure aggregation_rate = 0.272 (95% CI [0.253, 0.292]) on HaluEval-QA, establishing that deberta-large-mnli fails to aggregate 5–15 token responses into semantic clusters. This defines a concrete domain boundary for semantic entropy: the method requires an NLI model calibrated for the target response length and style.

2. **SelfCheckGPT polarity inversion on ChatGPT-generated hallucination labels.** AUROC = 0.3562, with CI entirely below random chance, suggests that BERTScore consistency positively correlates with HaluEval-QA hallucination labels — the opposite of SelfCheckGPT's design assumption. This finding is benchmark-specific (ChatGPT-generated confident hallucinations) and motivates a direct test: inverting the SelfCheckGPT signal should yield AUROC > 0.5.

3. **Controlled cross-signal comparison framework.** The experimental design (same 2,000-example stratified sample, same LLM, same bootstrap CI protocol, hypothesis-driven mechanism verification) provides a reproducible template for UQ benchmarking that converts null results into mechanistic diagnoses rather than unexplained failures.

## Future Directions

The NLI aggregation failure we identify is not a fundamental limitation of semantic entropy — it is a limitation of using a general-purpose NLI model outside its calibration domain. Three high-priority extensions follow directly from our results:

**Replace the NLI model.** Substituting deberta-large-mnli with a QA-specific entailment model (e.g., cross-encoder/nli-deberta-v3-base fine-tuned on QA entailment pairs) could recover non-degenerate semantic entropy on HaluEval-QA without any new LLM inference. The existing H-E1 stochastic samples provide all required inputs. This experiment directly tests whether the NLI domain mismatch hypothesis explains the aggregation failure.

**Test the polarity inversion hypothesis.** The SelfCheckGPT below-random result generates a testable prediction: per-example BERTScore consistency should be higher for hallucinated examples than factual ones on HaluEval-QA. Stratifying existing H-E1 consistency scores by hallucination label requires zero new computation. If confirmed, inverting the SelfCheckGPT signal (1 − consistency) would yield AUROC > 0.5, converting a below-random detector into a potentially useful one.

**Cross-model and cross-benchmark validation.** Executing H-M3 (Mistral-7B-Instruct) with the proven h-e1 codebase would test cross-model ranking stability. Running the same pipeline on TriviaQA with LLaMA-2-7B-chat would directly measure the HaluEval-QA vs. TriviaQA performance gap, isolating whether failure is driven by benchmark characteristics (ChatGPT-generated labels) or model-benchmark fit.

The NLI aggregation failure that collapses semantic entropy on HaluEval-QA is not a dead end — it is a precise specification of what the next step must be: a NLI model calibrated for short factual QA responses. The measurement framework and codebase developed here make that next experiment straightforward.
