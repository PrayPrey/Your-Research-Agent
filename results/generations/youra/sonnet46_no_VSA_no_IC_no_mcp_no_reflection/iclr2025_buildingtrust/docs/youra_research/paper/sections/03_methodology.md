# Methodology

## Overview

Our approach treats alignment-strategy detection as a binary classification problem over
public benchmark score vectors. This framing follows directly from our central question:
if DPO and SFT training produce systematically different behavioral profiles, those
profiles should be detectable as distinct clusters in benchmark score space, recoverable
by a classifier without access to model internals or training data.

We operationalize this as a three-stage pipeline: (1) curate matched DPO/SFT model
pairs and evaluate them on a 4-benchmark trustworthiness suite; (2) build a 4D score
matrix and apply k-NN leave-one-out cross-validation; (3) use Fisher's linear discriminant
criterion per benchmark to identify which dimension drives separability. Two sub-hypotheses
structure the inquiry: h-e1 tests fingerprint *existence* (is classification accuracy
statistically significant?), and h-m1 tests the *mechanism* (which benchmark dimension
and which direction?).

## Model Selection and Pair Design

**Rationale for matched pairs:** We require that DPO and SFT models within each pair
share the same base model to the extent possible, isolating alignment strategy as the
primary variable. Unmatched comparisons confound alignment with architecture and data
quality differences.

**Primary pair (alignment-handbook):** `HuggingFaceH4/zephyr-7b-dpo-full` and
`HuggingFaceH4/zephyr-7b-sft-full` share the same base model (Mistral-7B-v0.1) and
training data corpus, providing the cleanest controlled comparison. This pair is from
the Alignment Handbook [Tunstall et al., 2023], which documents matching procedures
explicitly.

**Community pairs (n=5):** To reach the minimum n=6 pairs required for permutation
significance, we include publicly available 7B DPO and SFT models with documented
alignment provenance:

| DPO Model | SFT Counterpart | Base Model |
|-----------|-----------------|------------|
| HuggingFaceH4/zephyr-7b-dpo-full | HuggingFaceH4/zephyr-7b-sft-full | Mistral-7B-v0.1 |
| Intel/neural-chat-7b-v3-1 | Intel/neural-chat-7b-v3 | Mistral-7B-v0.1 |
| openchat/openchat-3.5 | Open-Orca/Mistral-7B-OpenOrca | Mistral-7B-v0.1 |
| berkeley-nest/Starling-LM-7B-alpha | openchat/openchat-3.5 | Mistral-7B-v0.1 |
| teknium/OpenHermes-2.5-Mistral-7B | mistralai/Mistral-7B-Instruct-v0.1 | Mistral-7B-v0.1 |
| meta-llama/Llama-2-chat-hf (RLHF) | meta-llama/Llama-2-7b-hf + SFT | Llama-2-7B |

**Rationale for n=6:** The permutation test over n=12 models (6 pairs) provides the
minimum sample for our one-sided significance threshold (p≤0.05) with 1000 permutations.
We report the sample size as a principled limitation (Section 6).

## Benchmark Suite

We evaluate each model on four benchmarks via `lm-evaluation-harness v0.4.3`:

| Benchmark | Task Key | Metric | Dimension |
|-----------|----------|--------|-----------|
| TruthfulQA MC2 | `truthfulqa_mc2` | MC2 accuracy (log-prob normalized) | Truthfulness |
| BBQ | `bbq` | Accuracy on ambiguous questions | Social fairness |
| WinoGrande | `winogrande` | Accuracy | Commonsense robustness |
| WinoGender | `winograd_wsc` | Accuracy | Gender fairness |

**Rationale for this suite:** The four benchmarks span the two dimensions predicted by
the original alignment hypothesis — truthfulness (TruthfulQA) and fairness (BBQ,
WinoGender) — plus a control dimension (WinoGrande) that should not be systematically
affected by alignment strategy. This design allows us to test not only whether profiles
differ, but which dimension carries the alignment signal.

**Evaluation parameters:** `--batch_size 8`, `--dtype bfloat16`, `--limit 100` per
task (PoC speed constraint; full evaluation is immediate future work). We report
`acc,none` as the primary metric for all tasks.

## Classification Approach

**Score matrix construction:** For each of the 12 models, we extract the 4-dimensional
score vector `(TruthfulQA MC2, BBQ, WinoGrande, WinoGender)`, yielding a design matrix
`X ∈ R^{12×4}` with labels `y ∈ {0=SFT, 1=DPO}^{12}`.

**k-NN leave-one-out cross-validation:**

```
Classifier: KNeighborsClassifier(n_neighbors=1, metric='euclidean')
CV: LeaveOneOut() over n=12 samples
LOO-CV accuracy = (number of correct leave-one-out predictions) / 12
```

**Rationale for k=1:** With n=12 samples and balanced classes, k=1 minimizes inductive
bias and maximizes sensitivity to cluster structure. We report k=3,5 sensitivity as
a robustness check.

**Rationale for Euclidean distance in 4D:** The four benchmark scores are on [0,1] scales
with similar variance, making Euclidean distance appropriate without normalization. We
verify this via Fisher's criterion analysis.

**Permutation significance test:**

```
H₀: LOO-CV accuracy ≤ chance level (50%)
Test: Permute alignment labels y → y_perm (1000 shuffles, seed=42)
      Re-run LOO-CV for each permutation → perm_scores[1000]
p-value = P(perm_score ≥ observed_accuracy) under H₀
Significance threshold: p ≤ 0.05 (one-tailed)
```

The permutation test provides a model-free non-parametric significance assessment
appropriate for small n, controlling false positive rate without distributional
assumptions.

## Mechanism Analysis (h-m1)

To identify which benchmark dimension drives fingerprint separability, we compute
**Fisher's linear discriminant criterion** for each benchmark independently:

```
Fisher(j) = (μ_DPO,j - μ_SFT,j)² / (σ²_DPO,j + σ²_SFT,j)
```

Higher Fisher criterion indicates greater between-class separation relative to
within-class variance. We rank benchmarks by Fisher criterion and test whether the
ranking matches the predicted ordering (BBQ highest, TruthfulQA neutral-to-lower).

We additionally apply a **paired sign test** for each fairness benchmark:
```
k_j = |{pairs i : score_DPO,i,j > score_SFT,i,j}|
H₀: k_j ~ Binomial(6, 0.5)
p-value (one-tailed) threshold: p ≤ 0.125  [binomial(6, 0.5) ≥ 5]
```

## Implementation

All analysis code is implemented in Python using `scikit-learn ≥ 1.3.0` and `numpy ≥
1.24.0`. The pipeline is modular:

- `curate_pairs.py`: Validates model pair definitions, writes `model_pairs.json`
- `run_evaluations.sh`: Bash loop over model pairs invoking `lm_eval` CLI per model
- `build_score_matrix.py`: Parses `lm-eval` result JSONs into `X, y` arrays
- `classify.py`: k-NN LOO-CV + permutation test + sensitivity analysis
- `visualize.py`: Generates all figures (benchmark comparison, 2D scatter, permutation histogram, Fisher criterion, paired delta bars)
- `report.py`: PASS/FAIL determination and `summary.json` output

All random seeds are set to 42 for reproducibility. GPU evaluation uses `bfloat16`
dtype on H100 hardware.
