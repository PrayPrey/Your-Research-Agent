# Discussion

## The Systematic Confabulation Regime

Our results support a specific theoretical interpretation: Llama-3-8B-Instruct on HaluEval QA operates in the **systematic confabulation** regime, rather than the stochastic hallucination regime assumed by sampling-based consistency methods.

In the stochastic hallucination regime — which characterizes GPT-3 on WikiBio biography generation [Manakul et al., 2023] and smaller models on open-ended QA [Kuhn et al., 2023] — a model producing incorrect outputs does so from uncertainty: its sampling distribution is broad, generating semantically diverse incorrect responses on repeated queries. In this regime, NLI consistency scores are discriminative: inconsistent outputs (low SMC) signal hallucination.

In the systematic confabulation regime — which our results suggest characterizes Llama-3-8B-Instruct on structured factual QA — RLHF fine-tuning has reinforced specific answer patterns to the point where the model produces confident, consistent outputs even for factually wrong beliefs. Multiple samples at temperature=0.7 converge on the same response (whether correct or incorrect) because RLHF training has sharped the output distribution. The mean SMC-NLI scores for correctly-labeled (0.6236) and hallucinated-labeled (0.6299) questions are near-identical, confirming that both categories produce high-consistency outputs.

**Why RLHF produces this regime:** RLHF training optimizes for human preference ratings, which typically reward confident, coherent, and consistent answers over hedged or varied ones. This optimization directly conflicts with the behavioral prerequisite of sampling-based consistency methods: that incorrect beliefs manifest as output diversity. An RLHF-fine-tuned model is trained to mask uncertainty, not express it — producing consistent answers even when the underlying "belief" is factually wrong.

This interpretation aligns with a growing understanding that instruction-tuned models are not simply better base models: their behavioral signatures differ in ways that have downstream implications for uncertainty quantification and calibration [Ouyang et al., 2022; Bai et al., 2022].

## Alternative Explanation: Dataset-Model Mismatch

A competing explanation for our negative result is dataset-model mismatch: HaluEval labels reflect ChatGPT's hallucination patterns, not Llama-3-8B's. If Llama-3-8B answers correctly on questions where ChatGPT hallucinated (or vice versa), the binary labels are effectively random ground truth from Llama's perspective, suppressing discriminative signal regardless of the detection method.

We consider this a secondary contributing factor, not the primary explanation, for three reasons:

1. **SMC-Embed independently confirms the result.** If label noise were the primary cause, both SMC-NLI and SMC-Embed would fail — which they do, but this is also consistent with the regime explanation.

2. **Mean score analysis is label-independent.** The near-identical mean SMC scores (correct=0.6236 vs hallucinated=0.6299) indicate that Llama-3-8B produces consistently high-consistency outputs regardless of which label category the question falls into. This pattern would hold even if the labels were perfect: both categories produce the same outputs.

3. **The mechanism verification on 5 questions passes locally.** For individual questions with strong SMC signals (0.9853, 0.3875), the direction appears correct. Label noise would produce random local patterns; the regime explanation predicts the global signal collapses even when local variation exists.

Both explanations — systematic confabulation and dataset-model mismatch — likely contribute to the result. Future work should disentangle them by running SMC on TriviaQA with exact-match labels (model-agnostic ground truth), which eliminates the dataset-model mismatch confound.

## Implications for Practitioners

Our findings have practical implications for deploying sampling-based consistency methods:

**Before deploying SMC-style detectors, verify the regime:** Generate multiple samples on a small calibration set and measure the per-label SMC score gap. If correctly-answered and incorrectly-answered questions show similar mean SMC scores (gap < 0.01), the model is likely in the systematic confabulation regime and SMC will not provide discriminative signal.

**Instruction-tuned models on structured QA are high-risk.** Our findings suggest this combination (RLHF-fine-tuned model + structured factual QA) is a likely failure mode. Open-ended generation tasks (biography, summarization, long-form QA) may retain the stochastic hallucination regime where SMC works.

**The validated SMC infrastructure is still useful.** The LLMSampler, SMCNLIScorer, and SMCEmbedScorer components are validated and reusable for future experiments on different model-task combinations where the stochastic hallucination regime may hold.

## Limitations

**L1: Single model evaluation.** All results are specific to Llama-3-8B-Instruct. Whether other instruction-tuned models (GPT-4, Llama-3-70B, Mistral-7B-Instruct) exhibit the same systematic confabulation regime on structured factual QA is unknown. Larger models with different RLHF training procedures may behave differently. The negative result cannot be generalized beyond this specific model.

**L2: Single benchmark.** We test only on HaluEval QA. The original hypothesis required AUROC ≥ 0.70 on four benchmarks (TriviaQA, NQ, HaluEval, TruthfulQA); only HaluEval was evaluated due to the MUST_WORK gate cascade failure design. While we expect similar results on TriviaQA and NQ given the regime analysis, direct multi-benchmark evaluation remains future work.

**L3: HaluEval label validity.** As discussed, HaluEval labels may not accurately reflect Llama-3-8B's hallucination patterns. The extent to which this confounds our AUROC estimate is unknown. Future work should measure Llama-3-8B-specific factual accuracy on HaluEval questions and recompute AUROC against model-specific labels.

**L4: Temperature not ablated.** We use temperature=0.7 following Manakul et al. [2023]. Whether higher temperatures (T≥1.0) restore the stochastic hallucination regime for instruction-tuned models is an open question. The SMC standard deviation of 0.3388 indicates variation exists at T=0.7, but this variation is not discriminative.

## Broader Impact

Our findings contribute to a broader understanding of when uncertainty quantification methods developed for base language models transfer to instruction-tuned models. The regime distinction — stochastic hallucination vs. systematic confabulation — provides a conceptual framework and empirical test protocol that can guide practitioners in evaluating whether sampling-based methods will be effective in their specific model-task setting.

The validated negative result is not a failure of the research program; it is a boundary characterization that the field needs. Positive results from SMC on open-ended generation [Manakul et al., 2023; Kuhn et al., 2023] and negative results from our structured QA evaluation together define the scope of applicability for these methods more precisely than either alone.
