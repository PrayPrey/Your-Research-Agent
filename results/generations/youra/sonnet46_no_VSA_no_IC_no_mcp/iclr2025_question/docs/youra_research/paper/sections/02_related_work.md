# Related Work

Our work synthesizes and extends four lines of research: token-level entropy methods, semantic-level sampling methods, verbalized confidence calibration, and comparative uncertainty evaluation. Each line is missing at least one of the dimensions our study closes: 7B-scale coverage, all four methods simultaneously, mechanism measurement, or cross-benchmark testing.

## Token-Level Entropy for Uncertainty Estimation

The entropy of a model's output token distribution — Shannon entropy over the softmax probability vector — is the simplest and most computationally efficient uncertainty proxy [Guo et al., 2017]. Applied to language models, it requires a single forward pass and no additional samples [Huang et al., 2023]. Huang et al. compare single-pass entropy against sampling-based methods on TriviaQA and NaturalQuestions, finding that sampling-based methods consistently outperform single-pass entropy, but do not include semantic entropy in their comparison and do not measure the mechanism driving the gap. Our H-M1 experiment provides the mechanistic explanation: TE aggregates surface-form variation within semantically equivalent answer clusters, adding noise that does not reflect semantic uncertainty.

## Semantic-Level Uncertainty: Semantic Entropy and SelfCheckGPT

Kuhn et al. [2023] introduce semantic entropy, which groups semantically equivalent outputs via NLI entailment clustering before computing entropy over the cluster distribution. This clustering removes paraphrase noise at the feature level. Evaluated at 65B scale on TriviaQA and NaturalQuestions, SE substantially outperforms TE. Our work extends Kuhn et al. in three dimensions: (1) we confirm the SE > TE ordering at 7B scale, where prior work did not evaluate; (2) we measure the paraphrase-noise mechanism directly (H-M1); and (3) we test cross-benchmark generalization (H-C1), identifying a task-structure scope condition that Kuhn et al.'s TriviaQA/NQ-only evaluation could not detect.

Manakul et al. [2023] introduce SelfCheckGPT, which scores hallucinations via cross-sample consistency — measuring how much the model's stochastic outputs agree with each other — using BERTScore, NLI, or n-gram overlap as the consistency measure. SelfCheckGPT is evaluated on long-form generation (WikiBio) rather than short factual QA. Our H-M3 experiment demonstrates that BERTScore-based SCG fails on 1-3 word TriviaQA answers (AUROC = 0.378 vs. SE AUROC = 0.714), with the gap attributable to BERTScore's lexical-overlap measure failing to capture entailment-level equivalence on short spans. This extends Manakul et al. by characterizing the short-QA failure mode of the BERTScore SCG variant.

## Verbalized Confidence and Calibration at Scale

Kadavath et al. [2022] demonstrate that sufficiently large language models can self-report calibrated probability estimates, with calibration improving with scale. Lin et al. [2022] train models to attach verbal confidence to factual claims. Xiong et al. [2023] provide the most comprehensive evaluation of confidence elicitation strategies, finding that verbalized confidence is poorly calibrated at 7B scale and improves substantially at 70B. Our H-M4 independently confirms Xiong et al.'s 7B finding: VC produces a near-degenerate score distribution (5 distinct values; ~60% at 95% confidence; ECE = 0.430 against ~47% empirical accuracy), providing an independent replication with a different elicitation prompt and characterizing the degeneracy more precisely than prior work.

## Comparative Uncertainty Evaluation

Huang et al. [2023] compare single-pass entropy, MC dropout, and self-consistency methods on factual QA benchmarks but exclude SE and VC, limiting comparability with the semantic-entropy literature. Xiong et al. [2023] evaluate VC comprehensively but do not include SE or SCG as baselines. Neither study measures the mechanism driving method differences or tests cross-benchmark generalization.

Our study is the first to include all four methods (SE, TE, SCG, VC) at 7B scale under identical experimental conditions, measure the mechanistic driver of the primary performance gap, and test cross-benchmark generalization. The cross-benchmark reversal we find (SE > TE on TriviaQA, TE > SE on TruthfulQA) exposes a task-structure condition that single-benchmark comparative evaluations cannot detect, and provides an empirical basis for principled method selection that prior survey papers [Guo et al., 2023; Ji et al., 2023] recommend but do not operationalize.

## Positioning Summary

| Prior Work | Methods | Scale | Mechanism | Cross-Benchmark | Gap We Fill |
|------------|---------|-------|-----------|-----------------|-------------|
| Kuhn et al. [2023] | SE, TE | 65B | No | TriviaQA/NQ only | 7B scale; mechanism; cross-task |
| Manakul et al. [2023] | SCG | 7B-175B | No | WikiBio only | SE comparison; short QA |
| Xiong et al. [2023] | VC | 7B-70B | No | MMLU, TriviaQA | SE, SCG comparison |
| Huang et al. [2023] | TE, SCG | 7B-70B | No | TriviaQA, NQ | SE; mechanism |
| **This work** | SE, TE, SCG, VC | 7B | Yes | TriviaQA + TruthfulQA | Closes all gaps |
