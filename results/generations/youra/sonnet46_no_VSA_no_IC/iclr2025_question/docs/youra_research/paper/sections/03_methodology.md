# Methodology

## Overview

Our methodology operationalizes a three-step causal mechanism linking hallucination type to optimal aggregation function. Rather than treating aggregation as a hyperparameter to tune empirically, we derive a testable prediction from the mechanism's structure and design four nested experiments that verify the mechanism at increasing levels of specificity. The experimental design follows directly from the mechanism: if the theory is correct, distribution-level evidence should precede rank-level evidence, which should precede threshold-level evidence — and all three layers should point in the same direction.

## Mechanism Hypothesis

The hallucination detection problem for zero-cost single-pass methods reduces to a signal extraction problem: the token log-probability sequence contains information about hallucination, and the aggregation function determines how that information is read out.

**Step 1: Hallucination type determines token probability distribution shape.**

We define two hallucination types based on the mechanism of incorrect generation:

- *Recall-failure hallucination* (operationalized by TriviaQA, NQ): The model fails to retrieve a specific fact. During greedy generation, it assigns high probability to the contextual frame ("The capital of France is") but low probability to the incorrect fact-token it substitutes. The resulting per-token log-probability sequence is *peaked*: the distribution has high variance, with a sharp minimum at the fact-token.

- *Imitative-falsehood hallucination* (operationalized by TruthfulQA): The model generates an answer that is factually wrong but that it "believes" — it learned a confident wrong pattern from training data. The model generates each token with high probability because the entire sequence has high prior probability under its training distribution. The resulting per-token log-probability sequence is *flat*: low variance, uniformly high probability throughout.

We measure distribution peakedness as a composite score: `peakedness(x) = kurtosis(x) + max(x)/mean(x)`, where `x` is the vector of absolute token log-probability values for a generated response. Higher peakedness indicates a more concentrated (peaked) distribution.

**Step 2: Distribution shape determines aggregation function sensitivity.**

Given the peaked/flat distinction:

- *Min log-probability* captures the single most uncertain token. For peaked distributions, the minimum is informative because uncertainty is concentrated there. For flat distributions, the minimum is less reliable because it may reflect only the mildest local perturbation in an otherwise uniform sequence.

- *Mean log-probability* integrates uncertainty across all tokens. For flat distributions, the aggregate signal over all tokens is more stable than any individual token. For peaked distributions, the mean dilutes the concentrated signal with high-probability background tokens.

- *Raw sum log-probability* (unnormalized): equal to the model's autoregressive log P(sequence). Unlike mean (which normalizes by sequence length), raw sum accumulates both per-token confidence and sequence length. For factual recall benchmarks, correct answers tend to be longer and token-by-token confident; hallucinated answers may be shorter or carry throughout higher uncertainty. Raw sum thus captures a joint length-confidence signal.

**Step 3: Aggregation-distribution alignment produces statistically significant AUROC differentials.**

If Step 1 and Step 2 hold jointly, we predict:
- P1: AUROC(min) > AUROC(mean) on TriviaQA (factual recall) by ≥ 0.02, bootstrap 95% CI excluding zero, both LLaMA-2-7B and Mistral-7B-v0.1.
- P2: AUROC(mean) > AUROC(min) on TruthfulQA (imitative falsehood) by ≥ 0.02, bootstrap 95% CI excluding zero, both models.

## Models

We use two frozen open-weight LLMs at the 7B parameter scale:

- **LLaMA-2-7B** (`meta-llama/Llama-2-7b-hf`): autoregressive transformer; Llama architecture; trained on 2T tokens.
- **Mistral-7B-v0.1** (`mistralai/Mistral-7B-v0.1`): sliding-window attention; trained on 7.3T tokens; distinct tokenization.

The choice of two architecturally distinct model families at the same parameter scale is deliberate: consistent directional effects across both families provide stronger evidence that the mechanism is not model-specific. Both models are frozen (weights unchanged) throughout all experiments; we use fp16 precision with flash_attention_2 where available, and `device_map=auto` for placement.

## Datasets and Labels

**TriviaQA** (factual recall): We use the Farquhar 2023 evaluation splits from the `jlko/semantic_uncertainty` repository [Farquhar et al., 2023]. Binary correctness labels are derived by exact-match against reference answers (n ≈ 488–500 per model). This split is the standard in the uncertainty estimation literature and enables direct comparison to published baselines.

**TruthfulQA** (imitative falsehood): We use the HuggingFace generation subset (n = 810–817). Binary correctness labels are assigned by ROUGE-L ≥ 0.3 against best reference answers, matching the Fadeeva et al. [2024] protocol.

**NQ (Natural Questions)**: Included in the experiment design as a second factual-recall benchmark. NQ inference ran during h-e1 but the score cache was not persisted (data availability gap, not mechanism failure). NQ results are pending.

## Inference Protocol

For each (model, question) pair, we perform a single greedy forward pass with `do_sample=False`, `max_new_tokens=30`, and `batch_size=1`. The batch size of 1 is mandatory for numerical correctness of per-token log-probability extraction under the flash_attention_2 kernel: batching introduces padding that modifies attention patterns and corrupts per-token scores in subtle ways. Token log-probabilities for generated tokens only (not prompt tokens) are extracted from `model.generate()` output scores.

We do not use the lm-polygraph library [Fadeeva et al., 2024] due to version incompatibility with the hardware environment; instead, we implement the aggregation functions directly:

```python
def aggregate(logprobs: list[float], method: str) -> float:
    """method in {'min', 'mean', 'sum'}. Returns scalar score (not negated)."""
    arr = np.array(logprobs)
    if method == 'min':   return float(np.min(arr))
    if method == 'mean':  return float(np.mean(arr))
    if method == 'sum':   return float(np.sum(arr))
```

All three implementations are validated against unit tests (22/22 passing). Scores are negated before AUROC computation (more negative log-prob → higher uncertainty → predicted hallucinated).

## Evaluation Protocol

**AUROC** (Area Under the ROC Curve): Primary metric. Threshold-independent, commonly reported in the uncertainty estimation literature. Scores are passed as uncertainty predictors; binary correctness labels as targets.

**Spearman ρ** (rank-order correlation): Secondary metric used for mechanism verification (h-m2). Threshold-agnostic: confirms whether aggregation function scores rank hallucinated responses above correct responses, independent of threshold choice. ρ > 0 means higher uncertainty score (more negative log-prob) correlates with incorrectness (hallucination predicted).

**Bootstrap 95% CI for pairwise AUROC/ρ differences**: We use percentile bootstrap with n=1000 resamples and seed=42. The CI for AUROC(A)−AUROC(B) excludes zero if and only if the difference is statistically significant at the 5% level. We report the raw differential and the CI bounds for all pairwise comparisons.

## Hypothesis Design

The verification proceeds in four nested hypotheses:

- **h-e1** (Existence): Gate experiment — do the three aggregation methods produce statistically different AUROC values on any (model, dataset) pair? Confirmed if any pairwise AUROC differential ≥ 0.02 with CI_lower > 0. This is the prerequisite gate: if aggregation function does not matter at all, the directional claims are moot.

- **h-m1** (Distributional mechanism, Step 1): Do recall-failure hallucinations produce significantly higher token distribution peakedness than correct responses on TriviaQA? Confirmed if peakedness(hallucinated) > peakedness(correct) with t-test p < 0.05 on at least one model.

- **h-m2** (Rank-correlation mechanism, Step 2): Does rank-order correlation confirm the directional prediction at the signal level? Confirmed if ρ(min) > ρ(mean) on TriviaQA AND ρ(mean) > ρ(min) on TruthfulQA for both models, with bootstrap 95% CIs excluding zero.

- **h-m3** (AUROC threshold, Step 3): Do AUROC threshold differentials confirm P1 and P2 with ≥ 0.02 margin and bootstrap CI excluding zero? This is the primary claim hypothesis; h-m1 and h-m2 provide mechanistic grounding for its interpretation.

This layered design is intentional: it means a confirmed P1/P2 finding in h-m3 is not an isolated empirical result but the terminal confirmation of a causal chain supported at three independent measurement levels.
