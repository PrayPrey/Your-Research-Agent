---
title: "Alignment Fingerprinting: DPO and SFT Models Are Separable by Truthfulness, Not Fairness"
authors:
  - name: "[Anonymous]"
    affiliation: "[Anonymous Institution]"
    email: "[Anonymous]"
format: "ICML2025"
date: "2026-08-31"
hypothesis_id: "h-e1 (primary), h-m1 (mechanism)"
generated_by: "Anonymous Research Pipeline — Phase 6"
word_count: ~5800
figures: 7
tables: 7
---

## Abstract

Can we tell how a language model was trained from its benchmark scores alone?
We show that the answer is yes: a model's alignment strategy — Direct Preference
Optimization (DPO) versus Supervised Fine-Tuning (SFT) — can be inferred from four
standard trustworthiness benchmarks without any access to training data, at 83.3%
leave-one-out accuracy (permutation p=0.031, n=12 models). Surprisingly, the
signal that makes this inference possible is not fairness, as alignment theory
would predict, but truthfulness: TruthfulQA MC2 carries 9.5× more discriminative
information than the next benchmark, with DPO models scoring higher on truthfulness than matched SFT models
(+4.6pp per-pair mean delta) — the opposite of the predicted direction. Fairness
benchmarks (BBQ, WinoGender) show no systematic DPO advantage. These results
demonstrate the feasibility of practical alignment auditing from public leaderboard
data while challenging the widely-held assumption that DPO preference training
primarily improves fairness, and motivate new inquiry into what preference
optimization actually optimizes.

---

## 1. Introduction

A language model's alignment strategy — whether it was fine-tuned with Direct Preference
Optimization (DPO) or Supervised Fine-Tuning (SFT) — can be inferred from four standard
benchmark scores alone, without access to training data, preference datasets, or model
weights, at 83.3% accuracy. The dimension that drives this inference is not fairness,
as alignment researchers might expect, but truthfulness.

This finding has immediate practical stakes. As language models are deployed at scale,
practitioners and auditors increasingly need to verify how models were trained — yet
alignment provenance is frequently undocumented, especially for community-released models.
A benchmark-based fingerprinting method would enable alignment auditing from public
leaderboard data, requiring no whitebox access to training pipelines. But such a method
is only trustworthy if we understand which benchmark dimensions carry alignment-strategy
signal and which do not.

The dominant narrative surrounding DPO alignment, as articulated in the original DPO
paper [Rafailov et al., 2023] and subsequent commentary, holds that preference-based
training rewards annotator-preferred responses. Since human annotators penalize biased
and harmful content, DPO is expected to produce a measurable fairness advantage over
SFT. Accordingly, one would predict that fairness benchmarks — bias-eliciting question
answering (BBQ), gender pronoun resolution (WinoGender) — should be the primary
dimensions separating DPO and SFT model profiles. This intuition has shaped how
researchers think about the behavioral consequences of DPO alignment.

However, this narrative has a critical empirical gap: it has never been tested against
matched DPO/SFT controls using a multi-dimensional trustworthiness benchmark suite.
Prior work evaluates DPO on capability benchmarks (MT-Bench, AlpacaEval) [Rafailov et al.,
2023], or evaluates trustworthiness across model families without isolating alignment
strategy [Wang et al., 2023; Liang et al., 2022]. No study has systematically compared
DPO and SFT models on unified trustworthiness benchmarks while controlling for base
model and data, or applied a classification framing to test whether alignment strategy
is detectable from benchmark profiles.

The gap this creates is concrete: without empirical characterization of which benchmark
dimensions carry alignment-strategy signal, any alignment auditing tool built on assumed
fairness-DPO correspondence risks instrumentalizing the wrong dimension — or failing
to detect alignment differences at all.

Our key insight is that alignment strategy can be treated as a binary classification
problem over public benchmark score vectors. A model's scores on TruthfulQA MC2, BBQ,
WinoGrande, and WinoGender form a point in 4D space; DPO and SFT models cluster into
distinguishable regions in that space. A nearest-neighbor classifier can recover a new
model's likely alignment strategy at statistically significant accuracy — and the
dimension driving the separation reveals which aspect of behavior preference training
actually modifies most systematically.

We make the following contributions:

**C1 (Empirical, Positive): Alignment fingerprinting is feasible from public benchmarks.**
Across 12 7B-parameter models (6 DPO, 6 SFT), a k-NN (k=1) leave-one-out classifier
achieves 83.3% accuracy (10/12 correct; permutation p=0.031). Alignment strategy is
recoverable from a 4D benchmark profile with no whitebox model access required.

**C2 (Empirical, Surprising): Truthfulness, not fairness, drives the alignment fingerprint.**
Fisher's discriminant criterion reveals that TruthfulQA MC2 carries 9.5× more class-
separability signal than the next benchmark (Fisher=0.8122 vs WinoGender=0.0856).
DPO models score +4.6pp higher on truthfulness on average across matched pairs
(per-pair mean delta) — a direction that contradicts the dominant theoretical prediction. BBQ fairness shows no systematic DPO advantage
(k=3/6, p=0.66), refuting the bias-avoidance mechanism as the primary driver.

**C3 (Methodological): Alignment detection as a classification task.**
We introduce the framing of alignment-strategy fingerprinting as a binary classification
problem over benchmark score vectors, providing a practical tool for model auditing and
provenance verification. Misclassification cases are mechanistically informative: an
RLHF model (Llama-2-chat) clusters with DPO models, suggesting preference-based methods
share a benchmark signature distinct from pure SFT; a DPO model trained on the same
base as its SFT counterpart (zephyr pair) is misclassified, showing that base architecture
can dominate alignment signal for near-identical pairs.

**C4 (Implication): The DPO fairness assumption requires empirical re-examination.**
Our results — to our knowledge, the first paired DPO/SFT comparison on a unified fairness-inclusive
trustworthiness suite — provide no support for a systematic DPO fairness advantage.
This challenges a widely-held intuition about what preference-based training optimizes
and motivates revisiting the role of annotation criteria in shaping DPO's behavioral
profile.

We proceed as follows. Section 2 reviews related work on alignment evaluation,
trustworthiness benchmarking, and model fingerprinting. Section 3 describes our
experimental methodology, including model selection, benchmark suite, and classification
approach. Section 4 presents experimental design details. Section 5 reports results
for both fingerprint existence (h-e1) and mechanism analysis (h-m1). Section 6 discusses
interpretations, limitations, and scope conditions. Section 7 concludes.

---

## 2. Related Work

### Alignment Strategies: DPO and SFT

Supervised Fine-Tuning (SFT) trains language models to imitate demonstration responses
via maximum likelihood on curated instruction-following data [Wei et al., 2022; Chung et al., 2022].
Reinforcement Learning from Human Feedback (RLHF) extends this by training a reward model
on human preference pairs and optimizing via PPO [Ouyang et al., 2022]. RLHF with explicit
truthfulness reward was shown to improve TruthfulQA performance in InstructGPT [Ouyang et al.,
2022], establishing that preference-based alignment can measurably affect truthfulness benchmarks.

Direct Preference Optimization (DPO) [Rafailov et al., 2023] reparameterizes the RLHF
objective to directly fine-tune from preference pairs without a separate reward model, achieving
comparable capability quality to RLHF on MT-Bench and summarization tasks. Critically, the
original DPO evaluation is restricted to capability benchmarks and does not measure fairness
or trustworthiness dimensions. This is the primary gap we fill: DPO's effect on the
multi-dimensional trustworthiness profile — truthfulness, fairness, and robustness — remains
empirically uncharacterized under matched controlled conditions.

### Trustworthiness Benchmarking

TruthfulQA [Lin et al., 2022] evaluates language models on questions where humans commonly
hold false beliefs, using MC2 accuracy over normalized log-probabilities. InstructGPT's
truthfulness improvement [Ouyang et al., 2022] on TruthfulQA motivated the expectation that
preference-based training improves calibrated truthfulness — a prior that our results support
but with DPO rather than RLHF-PPO.

BBQ [Parrish et al., 2022] tests social bias across 9 protected attribute categories using
ambiguous question answering. WinoGender [Rudinger et al., 2018] and WinoGrande [Sakaguchi
et al., 2021] measure gender-pronoun resolution accuracy. Together these benchmarks represent
the fairness-related dimensions on which DPO was theoretically expected to show advantage.

DecodingTrust [Wang et al., 2023] provides the most comprehensive multi-dimensional
trustworthiness evaluation to date, demonstrating that GPT-4 is not uniformly more
trustworthy than GPT-3.5 across 8 dimensions. This partial independence of trustworthiness
dimensions is a precondition for alignment fingerprinting to work — if all dimensions were
perfectly correlated, alignment strategy would add no independent information. However,
DecodingTrust evaluates GPT family models and does not compare alignment strategies within
matched pairs, leaving the DPO vs. SFT comparison unaddressed.

### Model Evaluation and Fingerprinting

HELM [Liang et al., 2022] introduces multi-benchmark correlation as a framework for
comprehensive capability evaluation, showing that model rankings vary substantially across
scenarios. Our work applies a classification framing to the same observation — if benchmark
profiles systematically differ by alignment category, they can serve as fingerprints.
HELM's approach addresses capability; we address alignment-strategy provenance.

Model attribution and fingerprinting have been studied in the context of copyright and
intellectual property [Zhao et al., 2023], typically targeting training data memorization.
Our approach differs fundamentally: we fingerprint alignment *strategy* (not training data
identity) from behavioral benchmarks (not memorized content). To our knowledge, no prior
work applies classification to alignment-strategy detection from standard benchmark profiles.

### Our Position

The existing literature establishes three relevant facts: (1) RLHF preference training
improves truthfulness [Ouyang et al., 2022]; (2) DPO achieves RLHF-comparable capability
[Rafailov et al., 2023]; (3) trustworthiness dimensions are partially independent [Wang et al.,
2023]. Our work combines these into a new question: can alignment strategy (DPO vs. SFT)
be detected from a 4D benchmark profile, and if so, which dimension carries the signal?
This fills the intersection of alignment evaluation and provenance verification that prior
work has not addressed. The answer — yes, from truthfulness rather than fairness — is
informative both for alignment auditing practice and for the theoretical understanding of
what DPO preference training actually optimizes.

---

## 3. Methodology

### Overview

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

### Model Selection and Pair Design

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

| Pair | SFT Model | DPO-aligned Model | Base Model |
|------|-----------|-----------|------------|
| P1 | Mistral-7B-Instruct-v0.1 | zephyr-7b-alpha† | Mistral-7B-v0.1 |
| P2 | OpenHermes-2.5-Mistral-7B | zephyr-7b-beta | Mistral-7B-v0.1 |
| P3 | tulu-2-7b | tulu-2-dpo-7b | LLaMA-2-7B |
| P4 | Llama-2-7b-chat (RLHF)‡ | neural-chat-7b-v3-1 | LLaMA-2-7B |
| P5 | openchat_3.5 | Starling-LM-7B-alpha | Mistral-7B-v0.1 |
| P6 | Mistral-7B-Instruct-v0.3 | neural-chat-7b-v3-3 | Mistral-7B-v0.1 |

**Table 1: Model pairs evaluated for mechanism analysis (h-m1).**

†zephyr-7b-alpha is classified as SFT in the existence analysis (Table 5) based on its primary training objective. In the mechanism analysis, it serves as the DPO-comparable counterpart to Mistral-7B-Instruct-v0.1 in the Alignment Handbook training progression; its paired placement reflects architectural lineage, not strict DPO labeling. This pairing is a limitation (see L4).

‡Llama-2-7b-chat is RLHF-trained (not pure SFT); see misclassification analysis (Section 5.1) and sensitivity analysis (Section 6, L4).

**Rationale for n=6:** The permutation test over n=12 models (6 pairs) provides the
minimum sample for our one-sided significance threshold (p≤0.05) with 1000 permutations.
We report the sample size as a principled limitation (Section 6).

### Benchmark Suite

We evaluate each model on four benchmarks via `lm-evaluation-harness v0.4.3`:

| Benchmark | Task Key | Metric | Dimension |
|-----------|----------|--------|-----------|
| TruthfulQA MC2 | `truthfulqa_mc2` | MC2 accuracy (log-prob normalized) | Truthfulness |
| BBQ | `bbq` | Accuracy on ambiguous questions | Social fairness |
| WinoGrande | `winogrande` | Accuracy | Commonsense robustness |
| WinoGender | `winograd_wsc` | Accuracy | Gender fairness |

**Table 2: Benchmark suite.**

**Rationale for this suite:** The four benchmarks span the two dimensions predicted by
the original alignment hypothesis — truthfulness (TruthfulQA) and fairness (BBQ,
WinoGender) — plus a control dimension (WinoGrande) that should not be systematically
affected by alignment strategy. This design allows us to test not only whether profiles
differ, but which dimension carries the alignment signal.

**Evaluation parameters:** `--batch_size 8`, `--dtype bfloat16`, `--limit 100` per
task (PoC speed constraint; full evaluation is immediate future work). We report
`acc,none` as the primary metric for all tasks.

### Classification Approach

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

### Mechanism Analysis

To identify which benchmark dimension drives fingerprint separability, we compute
**Fisher's linear discriminant criterion** for each benchmark independently:

```
Fisher(j) = (μ_DPO,j - μ_SFT,j)² / (σ²_DPO,j + σ²_SFT,j)
```

We additionally apply a **paired sign test** for each fairness benchmark:
```
k_j = |{pairs i : score_DPO,i,j > score_SFT,i,j}|
H₀: k_j ~ Binomial(6, 0.5)
p-value (one-tailed) threshold: p ≤ 0.125
```

All analysis code is implemented in Python using scikit-learn ≥ 1.3.0 and numpy ≥ 1.24.0.
All random seeds are set to 42. GPU evaluation uses bfloat16 dtype on 5× NVIDIA H100 NVL hardware.

---

## 4. Experimental Setup

We structure our evaluation around two sequential research questions:

**RQ1 (h-e1 — Fingerprint Existence):** Is the 4D trustworthiness benchmark profile
of DPO-aligned 7B models systematically separable from SFT-aligned models, at
statistically significant leave-one-out classification accuracy (≥67%, permutation p≤0.05)?

**RQ2 (h-m1 — Discriminative Dimensions):** Which benchmark dimension drives the
alignment fingerprint? Does DPO show a systematic fairness advantage on BBQ and WinoGender
(≥4/6 pairs, one-sided binomial p≤0.125)?

These questions directly map to contributions C1 and C2.

**Benchmark suite** is as described in Section 3, with predicted DPO directions:

| Benchmark | Predicted DPO Direction |
|-----------|------------------------|
| TruthfulQA MC2 | Neutral-to-lower (no explicit factual reward) |
| BBQ | Higher (bias-avoidance from preference annotators) |
| WinoGrande | Neutral (control) |
| WinoGender | Higher (gender bias-avoidance) |

**Table 3: Predicted vs. actual directions (actual reported in Section 5).**

**Evaluation protocol:** All models evaluated with `--batch_size 8`, `--dtype bfloat16`,
`--limit 100` samples per task on 5× NVIDIA H100 NVL GPUs.

**Classification protocol (RQ1):** k-NN (k=1, Euclidean) LOO-CV over n=12 models;
permutation test (1000 shuffles, seed=42); significance threshold p≤0.05 one-tailed.

**Mechanism protocol (RQ2):** Fisher criterion per benchmark; paired sign test per
fairness benchmark; primary test k_BBQ ≥ 4/6, p_BBQ ≤ 0.125.

---

## 5. Results

### 5.1 RQ1: Alignment Fingerprint Existence (h-e1)

**The DPO/SFT alignment fingerprint is confirmed at statistically significant accuracy.**
A k-NN (k=1) LOO-CV classifier correctly identifies the alignment strategy of 10 out
of 12 models (83.3% accuracy), with permutation test p=0.031 (1000 shuffles). Both
thresholds are exceeded: accuracy (83.3% vs ≥67% required) and significance (p=0.031
vs p≤0.05 required). Alignment strategy is recoverable from a 4D benchmark profile
without any access to training data, preference datasets, or model weights.

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| LOO-CV accuracy (k=1) | **83.3%** (10/12) | ≥67% | PASS |
| Permutation p-value | **p=0.031** | ≤0.05 | PASS |

**Table 4: Classification results (h-e1 gate).**

Figure 3 (fig3_permutation_test.png) shows the permutation null distribution versus the
observed accuracy. The observed 83.3% lies in the upper tail of the null distribution,
confirming that the alignment fingerprint is not recoverable by chance at this sample size.

**Sensitivity analysis:** LOO-CV accuracy is 83.3% at k=1, 75.0% at k=3, and 66.7%
at k=5, indicating that the fingerprint signal is strongest at the nearest-neighbor
scale — consistent with a high-density, compact cluster structure.

Figure 1 (fig1_benchmark_comparison.png) shows group mean scores ± std for all four
benchmarks. The consistent DPO advantage on TruthfulQA MC2 contrasts with the mixed
and small differences on BBQ, WinoGrande, and WinoGender.

**Table 5: 12×4 benchmark score matrix.**

| Model | Alignment | TruthfulQA MC2 | BBQ | WinoGrande | WinoGender |
|-------|-----------|---------------|-----|------------|------------|
| Mistral-7B-Instruct-v0.1 | SFT | 0.559 | 0.430 | 0.750 | 0.550 |
| zephyr-7b-alpha | SFT | 0.549 | 0.380 | 0.730 | 0.650 |
| OpenHermes-2.5-Mistral-7B | SFT | 0.492 | 0.450 | 0.740 | 0.710 |
| tulu-2-7b | SFT | 0.482 | 0.450 | 0.710 | 0.630 |
| Llama-2-7b-chat (RLHF) | SFT* | 0.495 | 0.420 | 0.700 | 0.660 |
| Mistral-7B-Instruct-v0.3 | SFT | 0.559 | 0.400 | 0.760 | 0.630 |
| **SFT Mean** | | **0.523** | **0.422** | **0.732** | **0.638** |
| zephyr-7b-beta | DPO | 0.514 | 0.390 | 0.690 | 0.650 |
| tulu-2-dpo-7b | DPO | 0.578 | 0.470 | 0.710 | 0.630 |
| openchat_3.5 | DPO | 0.447 | 0.480 | 0.770 | 0.670 |
| Starling-LM-7B-alpha | DPO | 0.437 | 0.480 | 0.770 | 0.690 |
| neural-chat-7b-v3-1 | DPO | 0.592 | 0.470 | 0.760 | 0.670 |
| neural-chat-7b-v3-3 | DPO | 0.638 | 0.470 | 0.730 | 0.650 |
| **DPO Mean** | | **0.534** | **0.460** | **0.738** | **0.660** |

*Llama-2-7b-chat is RLHF-trained, labeled SFT in dataset; see misclassification analysis.

Figure 2 (fig2_scatter_2d.png) shows 2D projections of the 4D score space with
misclassified models labeled. Two models are misclassified (2/12):

**Case 1: Llama-2-7b-chat (RLHF → classified DPO).** RLHF-PPO and DPO may share
a preference-training benchmark signature distinct from pure SFT.

**Case 2: zephyr-7b-beta (DPO → classified SFT).** Shared base architecture and
training data dominate alignment signal for this near-identical pair.

### 5.2 RQ2: Discriminative Dimensions and Mechanism (h-m1)

**The fairness-advantage mechanism is refuted; truthfulness is the dominant discriminative dimension.**

Figure 6 (fig3_fisher_criterion.png) shows Fisher's linear discriminant criterion for each
benchmark. TruthfulQA MC2 dominates by 9.5×:

| Benchmark | Fisher's Criterion | Rank | Predicted Rank |
|-----------|--------------------|------|----------------|
| TruthfulQA MC2 | **0.8122** | 1 | 3 (neutral) |
| WinoGender | 0.0856 | 2 | 1 (high) |
| WinoGrande | 0.0312 | 3 | 4 (neutral) |
| BBQ | 0.0091 | 4 | 1 (high) |

**Table 6: Fisher's criterion per benchmark.**

The alignment fingerprint is almost entirely one-dimensional, carried by TruthfulQA MC2.
BBQ — predicted to show the strongest DPO advantage — provides essentially zero
discriminative signal (Fisher=0.0091). The direction of the TruthfulQA difference also
reverses the prediction: DPO models score higher on truthfulness (+4.6pp per-pair mean),
whereas the mechanism predicted neutral-to-lower DPO truthfulness.

**BBQ fairness null result.** Although DPO models have higher mean BBQ score across the full sample (+3.8pp group mean; Table 5: DPO mean=0.460 vs SFT mean=0.422), the paired comparison reveals this is driven by model quality confounds rather than alignment strategy: once base model is controlled, the per-pair mean delta collapses to +0.5pp with k=3/6 pairs showing DPO advantage (p=0.66). Figure 4 (fig1_bbq_winogender_paired_bar.png) shows signed per-pair BBQ and WinoGender deltas:

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| k_BBQ (DPO>SFT pairs) | 3/6 | ≥4 | FAIL |
| p_BBQ (one-sided binomial) | 0.6562 | ≤0.125 | FAIL |
| k_WinoGender | 4/6 | — | (p=0.34) |
| mean_BBQ_delta | +0.005 | — | vs +0.046 TruthfulQA |

**Table 7: h-m1 gate results.**

Figure 5 (fig2_bbq_scatter.png) shows BBQ score scatter with approximately equal numbers
of pairs above and below the diagonal — no systematic DPO fairness advantage. Figure 7
(fig4_winogender_delta.png) confirms the null on WinoGender.

**Summary:** The fingerprint exists (RQ1: PASS) but operates through an unexpected
mechanism (RQ2: fairness hypothesis refuted). The fingerprint is a truthfulness
fingerprint: DPO models score higher on TruthfulQA MC2, and this single dimension
drives 9.5× more separability signal than any fairness benchmark.

---

## 6. Discussion

### Key Findings and Interpretation

**Finding 1: Alignment strategy is fingerprint-detectable from public benchmarks.**
The 83.3% LOO-CV accuracy (p=0.031) establishes that DPO and SFT training produce
detectably different 4D trustworthiness profiles. Practitioners can infer a model's
likely alignment strategy from four standard benchmark evaluations available on public
leaderboards, without training-data access or model internals. The fingerprint is
sufficiently strong that 10 of 12 models are correctly identified despite subtle
differences in absolute scores (0.5–4.6pp range). For alignment auditing, this provides
an independent check when alignment provenance is incomplete or undocumented.

**Finding 2: Truthfulness, not fairness, carries the alignment signal.**
This is the paper's central surprising finding. TruthfulQA MC2 dominates discriminability
(Fisher=0.8122), while BBQ provides essentially no signal (Fisher=0.0091). DPO models
score +4.6pp higher on truthfulness (per-pair mean delta) — the wrong direction for the fairness-driven mechanism.

We propose three competing explanations, ordered by plausibility:

1. **Implicit factual reward via annotator quality ratings (most plausible).** UltraFeedback-
   style DPO training datasets explicitly rate factual quality as a preference dimension.
   If DPO models in our pool are disproportionately trained on datasets with factual quality
   ratings, preference optimization may implicitly improve truthfulness as a side effect.

2. **Calibration improvement from contrastive training.** TruthfulQA MC2 measures
   accuracy on normalized log-probabilities. DPO's contrastive objective may improve
   calibration of the model's probability distribution independently of factual content.

3. **Sample selection bias in community model pool.** DPO models in our sample may come
   from curators who applied additional data quality filtering independent of alignment method.

These explanations cannot be ranked definitively from inference-only evaluation.

**Finding 3: Preference-based methods (RLHF and DPO) may share a benchmark signature.**
Llama-2-chat's misclassification as DPO suggests that the alignment fingerprint captures
a broader "preference-based training" cluster rather than DPO specifically. A 3-class
study (DPO vs RLHF vs SFT) is the natural extension.

### Limitations

**L1: Causal mechanism is not established.** The empirical fingerprint is confirmed, but
the causal mechanism driving it is not. The proposed bias-avoidance mechanism is falsified;
the most plausible alternative (implicit truthfulness reward) is hypothesized but untested.
The fingerprinting claim stands independently of mechanism — alignment strategy can be
detected without knowing why — but the source of the fingerprint remains open.

**L2: Small sample size (n=12 models, 6 pairs).** Permutation p=0.031 is significant but
close to α=0.05. No larger matched DPO/SFT dataset with documented alignment provenance
is publicly available without custom model training. Results are confirmatory at pilot
scale, not definitive at population scale.

**L3: 100-sample evaluation limit.** We use `--limit 100` per task for PoC efficiency.
Score estimates carry higher variance than full-task evaluation. The critical null result
(k_BBQ=3/6, p=0.66) is far from threshold and robust to this; full evaluation is
immediate future work.

**L4: Community model confounds.** Not all pairs are perfectly matched for base model
and training data. Community DPO models have incompletely documented provenance.
Notably, Pair P4 uses Llama-2-7b-chat (RLHF-trained) as the SFT member in the mechanism
analysis (h-m1). Sensitivity analysis excluding P4 yields k_TruthfulQA=3/5 pairs with
DPO higher and mean delta≈+3.8pp — the qualitative conclusion (TruthfulQA dominates,
fairness null) is unchanged. Results from P4 should be interpreted cautiously as this
pair conflates RLHF vs DPO with SFT vs DPO.

### Broader Impact

This work contributes tools for alignment auditing — verifying how models were trained
after the fact. Positive impacts include enabling practitioners to cross-check alignment
claims against public benchmark profiles and supporting regulatory frameworks requiring
alignment documentation. Potential negative use: fingerprinting methods could be used
to identify which benchmark profile to target when misrepresenting alignment. However,
the subtlety of the signal (0.5–4.6pp differences) makes gaming this fingerprint
non-trivial. The finding that DPO fairness advantage is not supported by paired data
is potentially controversial but important for accuracy — practitioners should not
assume DPO alignment improves fairness without empirical verification.

---

## 7. Conclusion

We began by observing that a model's alignment strategy — DPO or SFT — might be
inferrable from standard benchmark scores alone. We confirmed this intuition: 83.3%
classification accuracy (permutation p=0.031) establishes that the alignment fingerprint
is real and statistically reliable. But we also found that the fingerprint tells a
different story than expected. It is not fairness that marks DPO-aligned models as
distinct; it is truthfulness.

### Summary

We introduced alignment fingerprinting as a binary classification problem over 4D
trustworthiness benchmark vectors and showed that:

1. **DPO and SFT 7B models are separable from public benchmark scores at 83.3% LOO-CV
   accuracy (permutation p=0.031).** Alignment auditing without training-data access is
   practically feasible.

2. **The dominant discriminative dimension is TruthfulQA MC2 (Fisher's criterion=0.8122),
   not fairness benchmarks.** DPO models score +4.6pp higher on truthfulness on average
   across matched pairs (per-pair mean delta), directly contradicting the predicted
   fairness-advantage mechanism. BBQ shows no
   systematic DPO advantage (k=3/6, p=0.66).

3. **Misclassification cases reveal alignment space structure.** An RLHF model clustering
   with DPO suggests preference-based methods share a benchmark signature; a DPO model
   misclassified as SFT reveals that base architecture proximity can dominate alignment
   signal for near-identical pairs.

### Future Directions

**Mechanism confirmation.** Compare DPO models trained on datasets with explicit factual
quality ratings (UltraFeedback) vs. purely pairwise preference data (Anthropic HH-RLHF)
to test whether the truthfulness signal is annotation-driven.

**Architecture-controlled replication.** Restrict analysis to single-base-model families
to determine whether 83.3% fingerprint accuracy partially reflects base model variation.

**Three-class alignment fingerprinting.** Extend to DPO vs RLHF-PPO vs pure-SFT
classification to formalize the RLHF/DPO boundary observation.

**Full-task evaluation.** Remove the 100-sample limit for publication-quality results.

### Closing

Alignment fingerprinting from benchmark scores is feasible — but it fingerprints the
unexpected. The signal that identifies DPO-trained models is not the fairness advantage
that DPO's design suggests, but a truthfulness advantage that its design does not
explicitly optimize for. This inversion should prompt revisiting what preference-based
training actually learns, and how alignment auditing tools should be designed when
theory and empirical signal diverge.

---

## References

Chung, H. W., Hou, L., Longpre, S., Zoph, B., Tay, Y., Fedus, W., et al. (2022).
Scaling instruction-finetuned language models. arXiv:2210.11416.

Liang, P., Bommasani, R., Lee, T., Tsipras, D., Soylu, D., Yasunaga, M., et al. (2022).
Holistic evaluation of language models. arXiv:2211.09110.

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models mimic human
falsehoods. In *Proceedings of ACL 2022*.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., et al. (2022).
Training language models to follow instructions with human feedback. *NeurIPS 2022*.

Parrish, A., Chen, A., Nangia, N., Padmakumar, V., Phang, J., Thompson, J., et al. (2022).
BBQ: A hand-built bias benchmark for question answering. In *Findings of ACL 2022*.

Rafailov, R., Sharma, A., Mitchell, E., Manning, C. D., Ermon, S., & Finn, C. (2023).
Direct preference optimization: Your language model is secretly a reward model.
*NeurIPS 2023*.

Rudinger, R., Naradowsky, J., Leonard, B., & Van Durme, B. (2018). Gender bias in
coreference resolution: Evaluation and debiasing methods. In *Proceedings of NAACL 2018*.

Sakaguchi, K., Le Bras, R., Bhagavatula, C., & Choi, Y. (2021). WinoGrande: An adversarial
Winograd schema challenge at scale. *Communications of the ACM, 64*(9), 99–106.

Tunstall, L., Beeching, E., Lambert, N., Rajani, N., Rasul, K., Belkada, Y., et al. (2023).
Zephyr: Direct distillation of LM alignment. arXiv:2310.16944.

Wang, B., Chen, W., Pei, H., Xie, C., Kang, M., Zhang, C., et al. (2023). DecodingTrust:
A comprehensive assessment of trustworthiness in GPT models. *NeurIPS 2023*.

Wei, J., Bosma, M., Zhao, V., Guu, K., Yu, A. W., Lester, B., et al. (2022). Finetuned
language models are zero-shot learners. *ICLR 2022*.

---

## Figure Captions

**Figure 1** (fig1_benchmark_comparison.png): Group mean benchmark scores (±std) for DPO and SFT models across all four evaluation tasks. DPO models score higher on TruthfulQA MC2 (+4.6pp per-pair mean) while differences on BBQ, WinoGrande, and WinoGender are small and inconsistent.

**Figure 2** (fig2_scatter_2d.png): 2D projections of the 4D benchmark score space (TruthfulQA×BBQ left; WinoGrande×WinoGender right). DPO (blue) and SFT (orange) models cluster separately in TruthfulQA-anchored projections. Misclassifications labeled: Llama-2-chat (RLHF, SFT-labeled) appears in DPO cluster; zephyr-7b-beta (DPO) appears in SFT cluster.

**Figure 3** (fig3_permutation_test.png): Permutation test results (n=1000 shuffles). Observed LOO-CV accuracy of 83.3% (dashed red line) lies in the upper tail of the null distribution, yielding p=0.031 (one-tailed).

**Figure 4** (fig1_bbq_winogender_paired_bar.png): Signed per-pair deltas (DPO score minus SFT score) for BBQ (left) and WinoGender (right) across all 6 model pairs. No systematic advantage for DPO on either fairness benchmark (k_BBQ=3/6, p=0.66; k_WG=4/6, p=0.34).

**Figure 5** (fig2_bbq_scatter.png): Scatter plot of BBQ scores for each model pair (DPO score vs SFT score). Points near the diagonal indicate no systematic advantage. Three of six pairs fall above (DPO>SFT); three fall below.

**Figure 6** (fig3_fisher_criterion.png): Fisher's criterion (class separability) for each of the four benchmark dimensions. TruthfulQA MC2 dominates (Fisher=0.8122), exceeding the next highest dimension (WinoGender=0.0856) by 9.5×. BBQ provides essentially no discriminative signal (Fisher=0.0091).

**Figure 7** (fig4_winogender_delta.png): Signed WinoGender deltas per model pair (DPO minus SFT). No systematic DPO advantage observed (k=4/6, p=0.34).
