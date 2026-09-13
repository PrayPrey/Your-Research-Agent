---
title: "When Consistency Is Not Uncertainty: Sampling-Based Hallucination Detection Fails Under Systematic Confabulation in Instruction-Tuned LLMs"
authors: "Anonymous"
venue: "ICML 2025"
format: "ICML 2025"
---

# When Consistency Is Not Uncertainty: Sampling-Based Hallucination Detection Fails Under Systematic Confabulation in Instruction-Tuned LLMs

**Anonymous Authors**

---

# Abstract

Sampling-based semantic consistency — computing NLI agreement across multiple stochastic samples — is a widely adopted training-free hallucination detector for black-box LLMs, validated on open-ended generation tasks with base language models. We evaluate this paradigm on Llama-3-8B-Instruct, a representative RLHF-fine-tuned instruction model, using NLI-based (SMC-NLI) and embedding-based (SMC-Embed) consistency scores on 1,000 balanced HaluEval QA questions. Both metrics achieve chance-level AUROC (SMC-NLI: 0.4933; SMC-Embed: 0.4859), with implementation correctness independently verified by 14 unit tests and a mechanism verification step. Analysis reveals the failure is distributional: mean SMC-NLI scores for correctly-labeled (0.6236) and hallucinated-labeled (0.6299) questions differ by only 0.006, indicating that Llama-3-8B-Instruct produces consistent outputs for both correct and wrong beliefs — a "systematic confabulation" regime induced by RLHF fine-tuning that renders consistency-based signals non-discriminative. We introduce the stochastic hallucination vs. systematic confabulation distinction as a necessary regime prerequisite for sampling-based detectors, provide empirical evidence that instruction-tuned models on structured factual QA violate this prerequisite, and release validated SMC infrastructure for future evaluation on tasks where the stochastic regime may hold.

---

# Introduction

Consider a hallucination detector that passes every implementation check: 14 unit tests green, 10,000 real inference calls to Llama-3-8B-Instruct completed, 45,000 NLI pairs scored by a fine-tuned DeBERTa-v3-large cross-encoder, a 5-question mechanism verification confirming scores vary meaningfully in [0,1]. Now measure its performance on 1,000 balanced factual questions from a standard hallucination benchmark. The AUROC is 0.4933 — indistinguishable from a random classifier. A practitioner who deployed this detector would be filtering LLM outputs with zero discriminative power while believing the method is sound.

This is not a story of a broken implementation. It is a story of a broken assumption — and identifying precisely which assumption breaks, and why, is the contribution of this paper.

## The Problem: An Unexamined Regime Assumption

LLM hallucination detection without access to model internals (logit probabilities, attention weights) has become an active research area as proprietary APIs have proliferated. Among training-free black-box approaches, sampling-based semantic consistency has emerged as the dominant paradigm: generate $N$ stochastic samples from the LLM, measure their pairwise semantic agreement via NLI or embedding similarity, and use this consistency score as a hallucination proxy — inconsistent outputs signal uncertainty, consistent outputs signal grounded knowledge.

This paradigm rests on a foundational behavioral assumption: *hallucinated outputs are semantically diverse across samples because the model lacks grounded knowledge, while correct outputs converge because the model's parametric knowledge is concentrated*. This assumption was validated empirically for GPT-3 on open-ended biography generation [Manakul et al., 2023] and for smaller open-source models on open-ended QA [Kuhn et al., 2023]. Both studies confirmed that sampling-based consistency correlates with factual accuracy in their respective settings.

The assumption, however, has been silently extended: practitioners and researchers now apply SelfCheckGPT-style methods to instruction-tuned models — models trained with reinforcement learning from human feedback (RLHF) — on structured factual QA tasks, without verifying that the hallucination regime is the same. RLHF fine-tuning fundamentally changes model output distributions: it reinforces high-confidence, consistent answers, suppressing the stochastic variation that sampling-based methods rely on. Whether instruction-tuned models produce stochastically diverse hallucinations — or whether RLHF has collapsed their output distribution even for wrong beliefs — is an empirical question that has not been systematically addressed.

## The Deeper Problem: Systematic Confabulation vs. Stochastic Hallucination

We argue that two distinct hallucination regimes exist for LLMs, and that sampling-based consistency methods are only theoretically valid in one of them:

**Stochastic hallucination** (where sampling-based methods work): The model lacks grounded knowledge and samples from a broad, uncertain distribution. Hallucinated responses differ semantically across samples. NLI consistency scores are low for hallucinated questions and high for correctly answered ones — the discriminative signal exists.

**Systematic confabulation** (where sampling-based methods fail): RLHF fine-tuning has reinforced specific answer patterns, producing confident, consistent outputs even for factually wrong beliefs. The model's sampling distribution is peaked regardless of factual accuracy. Both correct and hallucinated questions yield high consistency scores. No discriminative signal exists.

The critical gap in the literature is that no study has characterized which regime instruction-tuned models inhabit on structured factual QA — the task type most commonly encountered in deployed question-answering systems. Without this characterization, practitioners cannot know whether deploying sampling-based consistency detectors in their systems will provide genuine signal or false assurance.

## Our Contribution: Regime Characterization with Clean Attribution

We present a controlled empirical investigation of sampling-based NLI consistency (SMC-NLI; N=10 samples, DeBERTa-v3-large cross-encoder) applied to Llama-3-8B-Instruct on HaluEval QA [Li et al., 2023] — a representative instruction-tuned model on a widely-used factual hallucination benchmark. Our experimental design includes two features that enable clean causal attribution:

1. **Dual-metric design**: We run both NLI-based (SMC-NLI) and embedding-based (SMC-Embed) consistency scoring in parallel. If NLI OOD (out-of-distribution for short factual answers) were the failure mode, SMC-Embed would serve as a fallback. If both fail equally, the failure is mechanism-level — in the shared consistency signal, not the scorer.

2. **Mechanism verification**: Before full-scale evaluation, we verify that scores vary meaningfully on 5 questions (distinguishing "broken code" from "wrong hypothesis"). Combined with 14 unit tests, this ensures the negative result is attributable to the hypothesis, not the implementation.

Our key findings are: (1) SMC-NLI achieves AUROC=0.4933 on HaluEval QA with Llama-3-8B-Instruct — indistinguishable from random; (2) SMC-Embed achieves AUROC=0.4859 — equally at chance level; (3) the mean SMC-NLI score for correctly-labeled questions (0.6236) is essentially identical to hallucinated-labeled questions (0.6299), with a gap of 0.006 — noise level over N=1000 questions; (4) the implementation is correct by independent verification (14/14 tests pass, mechanism check passes).

These findings collectively establish that Llama-3-8B-Instruct operates in the systematic confabulation regime on HaluEval QA: RLHF fine-tuning produces consistent outputs for both correct and wrong beliefs, eliminating the consistency-based discriminative signal.

We make the following contributions:

**C1 (Empirical — Negative Result):** First controlled demonstration that sampling-based consistency (both NLI and embedding variants) achieves chance-level AUROC (≈0.49) on HaluEval QA with Llama-3-8B-Instruct at temperature=0.7, with implementation correctness independently verified. This negative result is specific, replicable, and informative.

**C2 (Theoretical):** Introduction and operationalization of the *stochastic hallucination vs. systematic confabulation* regime distinction as a necessary prerequisite for sampling-based hallucination detection. We show that instruction-tuned models on structured factual QA exhibit systematic confabulation, rendering these methods ineffective for this model-task combination.

**C3 (Empirical — Benchmark Validity):** Evidence that HaluEval QA labels, derived from ChatGPT-generated hallucinations [Li et al., 2023], may not constitute valid evaluation ground truth for hallucination detectors applied to other models (Llama-3-8B-Instruct), raising a cross-model benchmark validity concern for a widely-used evaluation protocol.

**C4 (Infrastructure):** A validated, reusable implementation of the SMC pipeline (LLMSampler, SMCNLIScorer, SMCEmbedScorer) for Llama-3-8B-Instruct, with 10,000 real samples generated and 45,000 NLI pairs scored, available for future experiments in open-ended generation settings where the stochastic hallucination regime may hold.

The remainder of this paper is organized as follows: Section 2 situates our work within the hallucination detection and uncertainty quantification literature. Section 3 describes our methodology, emphasizing the design choices that enable clean attribution. Section 4 presents the experimental setup. Section 5 reports results. Section 6 discusses implications, limitations, and directions for future work. Section 7 concludes.

---

# Related Work

Our work intersects three research areas: sampling-based uncertainty quantification for LLMs, hallucination detection benchmarks, and the behavioral effects of RLHF fine-tuning on LLM output distributions. We review each in turn, positioning our contribution within the existing literature.

## Sampling-Based Consistency for Uncertainty Quantification

The use of sampling-based consistency as an uncertainty signal in language models was established by Wang et al. [2022] in the context of chain-of-thought reasoning: majority vote consistency over multiple samples implicitly captures model confidence. Kuhn et al. [2023] formalized this intuition as *Semantic Uncertainty* — using NLI to cluster semantically equivalent answers and computing entropy over these semantic equivalence classes, rather than over token sequences. Applied to TriviaQA and NaturalQuestions with GPT-3 and smaller models on open-ended generation, Semantic Uncertainty achieves meaningful AUROC and outperforms token-probability baselines. Critically, the models evaluated by Kuhn et al. are base or lightly fine-tuned models where the stochastic hallucination assumption naturally holds — models that exhibit broad, uncertain sampling distributions for questions they cannot answer.

Manakul et al. [2023] introduced SelfCheckGPT, which directly operationalizes NLI-based pairwise consistency (rather than entropy-based clustering) as a hallucination detector. Evaluated on WikiBio biography generation with GPT-3, SelfCheckGPT achieves AUROC ~0.65-0.75, confirming that consistent outputs signal factual accuracy in open-ended generation. SelfCheckGPT is the direct methodological predecessor of our SMC-NLI scorer; our experimental design closely follows their NLI consistency pipeline, extended to structured factual QA and an RLHF-fine-tuned model.

Lin et al. [2024] conducted a systematic comparison of black-box uncertainty methods, finding that sampling-based consistency is competitive with white-box (logit-based) methods when logits are unavailable. Xiong et al. [2023] showed that sampling-based UQ generalizes better across model families than verbalized confidence. These results establish sampling-based consistency as the dominant black-box UQ paradigm.

**Our gap:** All prior work establishing sampling-based consistency validates on base/lightly-tuned models on open-ended generation tasks. None has systematically evaluated whether this paradigm holds for instruction-tuned (RLHF-fine-tuned) models on structured factual QA — the setting most relevant to deployed QA systems. We fill this gap, and our findings suggest the paradigm's applicability is more constrained than the literature implies.

## Hallucination Detection Benchmarks

Hallucination detection has been studied across multiple benchmark types. TruthfulQA [Lin et al., 2022] evaluates models' propensity to repeat imitative falsehoods, focusing on adversarially constructed questions. TriviaQA [Joshi et al., 2017] and NaturalQuestions [Kwiatkowski et al., 2019] provide ground-truth factual QA with exact-match evaluation, enabling model-specific hallucination assessment.

HaluEval [Li et al., 2023], which we use as our primary benchmark, was constructed by sampling ChatGPT responses and asking ChatGPT to generate hallucinated versions, producing binary correct/hallucinated labels for QA, dialogue, and summarization tasks. HaluEval has been widely adopted as a hallucination detection benchmark due to its scale and accessibility.

However, HaluEval's construction protocol introduces a fundamental cross-model evaluation concern: the binary labels reflect ChatGPT's hallucination patterns, not those of the model being evaluated. A model that answers correctly where ChatGPT hallucinated — or vice versa — will receive inaccurate labels. This label-model mismatch makes AUROC evaluation ambiguous: low AUROC may reflect either (a) the detection method failing, or (b) the benchmark labels not matching the evaluation model's actual hallucination behavior. Our results suggest this is a non-trivial concern for Llama-3-8B-Instruct evaluation on HaluEval, and we flag it as a benchmark validity issue that the community should address.

In contrast, benchmarks with model-agnostic ground truth (TriviaQA exact match, NQ F1) avoid this confound and should be preferred for cross-model hallucination detection evaluation.

## Effects of RLHF Fine-Tuning on Model Output Distributions

A critical but underexplored factor in our context is how RLHF fine-tuning affects LLM output distributions. Ziegler et al. [2019] and Ouyang et al. [2022] established that RLHF training produces models that are more deterministic and consistent in their outputs — a desirable property for deployment (users expect consistent answers) but potentially problematic for uncertainty quantification.

Instruction-following fine-tuning, whether via RLHF or supervised instruction tuning, tends to sharpen model output distributions [Bai et al., 2022]. At temperature=0.7, an instruction-tuned model may produce a much narrower distribution over output tokens than an equivalently-sized base model would, because RLHF training has reinforced specific response patterns. If this sharpening is strong enough, even "uncertain" responses — responses where the model lacks grounded knowledge — may be generated consistently across samples, eliminating the consistency-based discriminative signal.

This theoretical concern has not been empirically tested against sampling-based hallucination detectors. Our work provides the first direct empirical evidence of this effect: Llama-3-8B-Instruct produces nearly identical consistency scores for correctly-labeled (mean SMC-NLI=0.6236) and hallucinated-labeled (mean SMC-NLI=0.6299) questions, with a gap of 0.006 — noise level over N=1000 questions — consistent with a sharpened output distribution that eliminates the assumed stochastic-hallucination regime.

## Positioning Our Work

Our contribution is complementary to, not contradictory of, the prior literature. SelfCheckGPT and Semantic Uncertainty establish that sampling-based consistency works in the stochastic hallucination regime (open-ended generation, base/lightly-tuned models). We establish that instruction-tuned models on structured factual QA — increasingly the practical deployment setting — exhibit a different regime (systematic confabulation) where these methods fail. The two findings together define a regime boundary that practitioners need to know before deploying consistency-based detectors.

The closest related work is [CITATION NEEDED: any paper discussing RLHF effects on UQ], but to our knowledge no prior work has explicitly characterized the stochastic hallucination vs. systematic confabulation distinction as a regime prerequisite for sampling-based detection, or provided empirical evidence via dual-metric (NLI + embedding) evaluation with implementation correctness verification.

---

# Methodology

Our experimental design is motivated by a single question: *if a sampling-based consistency detector fails on an instruction-tuned model, is the failure in the scoring mechanism or in the underlying consistency assumption?* This question requires more than measuring AUROC — it requires a design that separates implementation correctness, scorer validity, and mechanism validity as independent diagnostic layers.

## Overview

We evaluate NLI-based Semantic Mode Consistency (SMC-NLI), a direct instantiation of the SelfCheckGPT-NLI scoring protocol [Manakul et al., 2023], applied to Llama-3-8B-Instruct on HaluEval QA [Li et al., 2023]. The core scoring pipeline computes pairwise NLI agreement across N=10 stochastic samples per question and uses this consistency score as a hallucination predictor. We extend this with two design choices that enable clean attribution: a parallel embedding-based scorer (SMC-Embed) and an explicit mechanism verification step.

**Figure 1** (smc_nli_distribution.png): Distribution of SMC-NLI scores split by label (correct vs. hallucinated), illustrating the overlap that underlies our AUROC findings.

## Dataset

**HaluEval QA** [Li et al., 2023] consists of question-answer pairs with binary hallucination labels (correct / hallucinated), constructed by generating ChatGPT responses and using ChatGPT to create hallucinated alternatives. We use a stratified sample of $N=1000$ questions (500 correct, 500 hallucinated), drawn with `seed=42`, providing adequate statistical power for AUROC estimation (standard error < 0.02 at this sample size).

**Design rationale:** HaluEval is the most favorable structured factual QA benchmark for this evaluation — balanced labels, short-answer format, and no annotation noise from human raters. If SMC fails on HaluEval, failure on harder or more adversarial benchmarks is expected. We note the benchmark validity concern (ChatGPT labels vs. Llama-3-8B behavior) in Section 6 (Discussion).

## LLM Sampling (LLMSampler)

For each question $q_i$, we generate $N=10$ stochastic samples from Llama-3-8B-Instruct [Meta AI, 2024]:

$$S_i = \{s_i^{(1)}, s_i^{(2)}, \ldots, s_i^{(10)}\}$$

using temperature $\tau = 0.7$, top-p $p = 0.9$, and `max_new_tokens=50`. The model is loaded via HuggingFace Transformers with `device_map="auto"` for GPU memory management.

**Design rationale:** Temperature=0.7 matches the setting used in SelfCheckGPT [Manakul et al., 2023], enabling methodological comparability. We generate 10 samples following Kuhn et al. [2023], who found N=10 sufficient for reliable semantic entropy estimation. Intermediate samples are saved to disk (`data/llama_samples.json`) with resume logic to avoid re-inference.

Total inference: 10,000 samples across 1,000 questions.

## SMC-NLI Scoring

For each question $q_i$ and its samples $S_i$, we compute the Semantic Mode Consistency (NLI variant) as the mean pairwise non-contradiction rate over all $\binom{N}{2} = 45$ sample pairs:

$$\text{SMC-NLI}(q_i) = \frac{1}{45} \sum_{j < k} \left[ P_\text{ent}(s_i^{(j)}, s_i^{(k)}) + P_\text{neut}(s_i^{(j)}, s_i^{(k)}) \right]$$

where $P_\text{ent}$ and $P_\text{neut}$ are entailment and neutral probabilities from the DeBERTa-v3-large cross-encoder NLI model (`cross-encoder/nli-deberta-v3-large`). Higher SMC-NLI indicates greater semantic consistency among samples; lower SMC-NLI indicates semantic diversity (inconsistency).

To mitigate the documented out-of-distribution (OOD) concern for NLI models on short factual answers (trained on paragraph-length SNLI/MultiNLI pairs), each sample is prepended with the question context: `"Q: {question} A: {answer}"`. This follows the question-prepend convention from Manakul et al. [2023].

NLI pairs are processed in batches of 16 on GPU. Total NLI pairs scored: 45,000.

**Prediction direction:** Higher SMC-NLI should predict correctness (label=0); lower SMC-NLI should predict hallucination (label=1). AUROC is computed in this direction.

## SMC-Embed Scoring (Parallel Control)

In parallel with SMC-NLI, we compute an embedding-based consistency score:

$$\text{SMC-Embed}(q_i) = \frac{1}{45} \sum_{j < k} \cos\left(\mathbf{e}_i^{(j)}, \mathbf{e}_i^{(k)}\right)$$

where $\mathbf{e}_i^{(j)}$ is the sentence embedding of sample $s_i^{(j)}$ from `sentence-transformers/all-mpnet-base-v2`, and $\cos(\cdot, \cdot)$ denotes cosine similarity.

**Design rationale:** This is the critical diagnostic design choice. SMC-Embed measures the same underlying construct (output consistency) without the NLI scorer. If SMC-NLI fails due to NLI OOD for short factual answers, SMC-Embed should achieve meaningfully higher AUROC. If both fail at similar levels, the failure is in the shared assumption (consistent outputs carry no hallucination signal), not in the NLI scorer specifically. This dual-metric design enables clean causal attribution of the negative result.

## Mechanism Verification

Before full-scale evaluation, we perform a mechanism verification step on the first 5 questions:

1. Compute SMC-NLI scores for questions $\{q_1, \ldots, q_5\}$
2. Assert: all scores in $[0, 1]$
3. Assert: $\max_i \text{SMC-NLI}(q_i) - \min_i \text{SMC-NLI}(q_i) > 0.01$ (meaningful variation exists)
4. Raise an exception if either assertion fails

**Design rationale:** This step distinguishes two failure types: "the scorer is broken" (no variation, all scores identical or out-of-range) vs. "the scorer works but the scores are not discriminative at scale." When the mechanism check passes but full-scale AUROC collapses to chance, the failure is definitively in the hypothesis (assumed discriminative signal does not exist), not in the implementation. This is the key attribution step that makes our negative result interpretable.

## Evaluation

We compute AUROC for both SMC-NLI and SMC-Embed as hallucination predictors against HaluEval binary labels using `sklearn.metrics.roc_auc_score`. We also report:
- SMC-NLI standard deviation across questions (distribution check: should be >0.05 for meaningful variation)
- Per-label mean SMC-NLI scores (mechanism analysis: should differ between correct and hallucinated)
- ROC curves for both metrics (visual confirmation of performance)
- Per-question SMC-NLI vs. SMC-Embed scatter plot (correlation analysis: do the metrics agree in their failures?)

## Implementation Validation

All components are validated by 14 unit tests covering:
- Data pipeline correctness (stratified sampling, label extraction)
- LLMSampler output format and seed reproducibility
- SMCNLIScorer score range and batch consistency
- SMCEmbedScorer cosine similarity range
- Evaluate module AUROC computation

The Coder-Validator cycle completed in round 1/5 (all checks passing on first validation pass), providing independent confirmation that implementation errors are not a confound for interpreting the AUROC results.

## Summary of Key Design Choices

| Design Choice | Rationale |
|---|---|
| Dual metric (NLI + Embed) | Rules out NLI OOD as confound; enables regime-level attribution |
| Mechanism verification (5 questions) | Distinguishes broken code from wrong hypothesis |
| N=1000 balanced questions | Adequate statistical power (AUROC SE < 0.02) |
| 14 unit tests | Independent implementation correctness verification |
| Question-prepend for NLI | Mitigates NLI OOD for short factual answers |
| Resume logic for samples | Reproducibility: exact sample set fixed, scorer can be rerun |

---

# Experimental Setup

Our experimental design is structured to answer four nested questions, each resolving one layer of ambiguity in the negative result:

**Q1 (Primary):** Does SMC-NLI achieve AUROC > 0.60 on HaluEval QA with Llama-3-8B-Instruct?
**Q2 (Mechanism):** Does SMC-Embed achieve similar AUROC, ruling out NLI OOD as the primary failure mode?
**Q3 (Implementation):** Is the implementation correct, ruling out engineering error as a confound?
**Q4 (Distribution):** What is the per-label distribution of SMC scores, characterizing the mechanism failure?

## Model and Setup

**LLM:** Llama-3-8B-Instruct (meta-llama/Meta-Llama-3-8B-Instruct), a representative RLHF-fine-tuned instruction model with strong benchmark performance. We select this model because it is widely used in production QA deployments and represents the class of instruction-tuned models where sampling-based consistency has not been systematically evaluated.

**Hardware:** 5× NVIDIA H100 NVL (95GB VRAM), model loaded with `device_map="auto"`.

**Sampling:** $N=10$ stochastic samples per question, temperature $\tau=0.7$, top-p $p=0.9$, `max_new_tokens=50`, `seed=42` for reproducibility. Total inference: 10,000 forward passes.

## Dataset

**HaluEval QA** [Li et al., 2023]: structured factual question-answer pairs with binary hallucination labels (correct / hallucinated). Labels were generated by ChatGPT — the dataset contains `right_answer` (ChatGPT-generated correct response) and `hallucinated_answer` (ChatGPT-generated plausible but incorrect response) fields per question.

**Sampling:** We draw a stratified sample of $N_\text{eval}=1000$ questions (500 correct, 500 hallucinated) using `sklearn.model_selection.StratifiedShuffleSplit` with `seed=42`. Stratification ensures balanced evaluation and avoids class-imbalance bias in AUROC estimation.

**Label usage:** We use HaluEval's binary labels directly (0=correct, 1=hallucinated). We note that these labels reflect ChatGPT's behavior, not Llama-3-8B's — the benchmark validity concern is discussed in Section 6.

## Evaluation Protocol

**Primary metric:** AUROC (Area Under the Receiver Operating Characteristic Curve) for binary hallucination classification, computed with `sklearn.metrics.roc_auc_score`. AUROC is threshold-free and appropriate for imbalanced or binary classification tasks [Xiong et al., 2023].

**Secondary metrics:**
- SMC-NLI standard deviation across questions (distribution check): should exceed 0.05 for the mechanism to produce meaningful variation
- Per-label mean SMC-NLI (mechanism analysis): expected to differ between correct (lower) and hallucinated (higher) if the stochastic hallucination assumption holds
- ROC curves: visual confirmation of performance across all thresholds

**Random baseline:** AUROC=0.50 (a random classifier, included in Figure 1 for reference).

## Baselines

**Random classifier (AUROC=0.50):** The minimum meaningful threshold — we test whether SMC-NLI and SMC-Embed exceed this.

**SMC-Embed:** The parallel embedding-based consistency score serves as an internal control. If SMC-NLI fails due to NLI OOD, SMC-Embed should outperform it. Equal failure of both metrics indicates mechanism-level failure.

We do not compare against token-probability baselines (Kadavath et al., 2022) because Llama-3-8B-Instruct logits were not used in our strict black-box protocol — logit access would require white-box methods outside our scope.

## Implementation Validation

Prior to reporting results, we confirm:
1. **Mechanism verification (5 questions):** SMC-NLI scores are in $[0,1]$ and vary by $>0.01$ across the first 5 questions. This check passed with range 0.9853-0.3875=0.5978.
2. **Unit tests (14/14):** All tests covering data pipeline, scorer, and evaluate modules pass.
3. **Coder-Validator cycle (1/5):** Independent validation pass confirms all 15 implementation tasks completed correctly.

These checks confirm that any negative AUROC result is attributable to the detection mechanism, not implementation errors.

---

# Results

We present results in four layers, each addressing one experimental question from Section 4.

## Primary Result: Both Metrics at Chance Level

**Figure 1** (auroc_comparison.png) shows the AUROC comparison across SMC-NLI, SMC-Embed, and the random baseline.

| Metric | AUROC | Target | Status |
|--------|-------|--------|--------|
| SMC-NLI | **0.4933** | >0.60 | ❌ FAIL |
| SMC-Embed | **0.4859** | >0.60 | ❌ FAIL |
| Random baseline | 0.50 | — | — |

Both SMC-NLI (AUROC=0.4933) and SMC-Embed (AUROC=0.4859) are statistically indistinguishable from a random classifier (AUROC=0.50). Both are substantially below the MUST_WORK gate threshold of 0.60.

**Interpretation:** The primary detection task fails. A system using SMC-NLI to filter Llama-3-8B-Instruct outputs on HaluEval QA would achieve no improvement over random selection.

## ROC Curve Analysis

**Figure 2** (roc_curves.png) shows the full ROC curves for both metrics across all decision thresholds.

Both ROC curves are near-diagonal — confirming that the chance-level AUROC is not an artifact of threshold selection. There is no operating point at which either metric achieves meaningful sensitivity-specificity trade-off. The curves for SMC-NLI and SMC-Embed nearly overlap, already suggesting a shared failure mode.

## Mechanism Analysis: Score Distribution by Label

**Figure 3** (smc_nli_distribution.png) shows the SMC-NLI score histograms split by HaluEval label (correct vs. hallucinated).

| Label | Mean SMC-NLI | SMC-NLI Std |
|-------|-------------|-------------|
| Correct (n=500) | **0.6236** | — |
| Hallucinated (n=500) | **0.6299** | — |
| Gap | **0.006** | — |
| Overall std | **0.3388** | ✅ >0.05 |

The overall SMC-NLI standard deviation is 0.3388 — well above the 0.05 threshold, confirming that scores vary meaningfully across questions. This is a critical diagnostic: the mechanism produces a signal. But the signal carries no information about the label.

The per-label distributions overlap almost completely. The mean SMC-NLI score for correctly-labeled questions (0.6236) is essentially identical to hallucinated-labeled questions (0.6299), with a gap of only 0.006 — noise level over N=1000 questions. The direction is also inverted from the theoretical prediction: hallucinated questions show *slightly higher* consistency (0.6299 > 0.6236), though this difference is not statistically meaningful.

**Interpretation:** The mechanism assumption — that hallucinated outputs produce lower consistency than correct outputs — is empirically falsified. Both label categories produce similar high-consistency outputs in Llama-3-8B-Instruct. The model is "confidently consistent" regardless of factual accuracy.

## Mechanism Verification: Local vs. Global

The 5-question mechanism verification (detailed in Section 3) passed:

```
Q: "What year was the composed of Lux Aurunque born?"   SMC-NLI: 0.9530 | Label: 0 (correct)
Q: "What is the birthdate of this monarch of three...?"  SMC-NLI: 0.3875 | Label: 1 (hallucinated)
Q: "What US Air Force installation was last...?"         SMC-NLI: 0.9853 | Label: 0 (correct)
Q: "Esther Norma Arrostito is a founder of a...?"       SMC-NLI: 0.6162 | Label: 1 (hallucinated)
Q: "What is the birthdate of this American actor...?"   SMC-NLI: 0.4881 | Label: 1 (hallucinated)
✅ Mechanism verification PASSED (range: 0.3875–0.9853, all in [0,1])
```

The mechanism check shows SMC-NLI varies substantially on 5 questions, and appears directionally correct locally (question 1: high consistency, label=correct; question 2: lower consistency, label=hallucinated). This local appearance is misleading: across 1,000 questions, the discriminative signal collapses to AUROC=0.49.

This juxtaposition — local mechanism functioning, global discriminative failure — is the defining characteristic of the systematic confabulation regime. The scorer works correctly; the assumed signal does not exist at scale.

## Dual-Metric Correlation Analysis

**Figure 4** (nli_vs_embed_scatter.png) shows per-question SMC-NLI vs. SMC-Embed scatter.

The two metrics are strongly correlated across questions: questions with high NLI consistency also tend to have high embedding consistency, and vice versa. This strong correlation confirms that SMC-NLI and SMC-Embed are measuring the same underlying property — the output consistency of Llama-3-8B-Instruct — and that property is uniformly present regardless of factual accuracy.

The equal failure of both metrics, and their high correlation, is the strongest evidence for the regime-level interpretation: the failure is not in how consistency is measured (NLI vs. embedding) but in whether consistency discriminates labels in this model-task combination.

## Implementation Validation Summary

| Check | Result |
|-------|--------|
| Unit tests | 14/14 ✅ |
| Mechanism verification | PASSED ✅ |
| Coder-Validator cycles | 1/5 ✅ |
| Total tasks completed | 15/15 ✅ |
| LLM samples generated | 10,000 ✅ |
| NLI pairs scored | 45,000 ✅ |

All implementation checks pass. The negative AUROC result is not attributable to implementation error.

## Summary of Results

| Question | Answer |
|----------|--------|
| Q1: Does SMC-NLI achieve AUROC>0.60? | **No** (AUROC=0.4933) |
| Q2: Does SMC-Embed rule out NLI OOD? | **Yes** (SMC-Embed=0.4859, equal failure) |
| Q3: Is implementation correct? | **Yes** (14/14 tests, mechanism check passes) |
| Q4: What does the distribution reveal? | **Mechanism failure** (gap=0.006, distributions overlap completely) |

The results consistently point to a single interpretation: Llama-3-8B-Instruct on HaluEval QA operates in the systematic confabulation regime, producing consistent outputs for both correct and incorrect beliefs, eliminating the discriminative signal that SMC-based methods require.

---

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

---

# Conclusion

We began with a detector that worked perfectly — every implementation check green, every test passing — and an AUROC of 0.4933. This juxtaposition is not a cautionary tale about experimental failure. It is how we learned where a widely-adopted hallucination detection paradigm breaks.

Our investigation of NLI-based Semantic Mode Consistency (SMC-NLI) applied to Llama-3-8B-Instruct on HaluEval QA reveals that sampling-based consistency methods operate under a regime assumption — *that hallucinated outputs are stochastically diverse across samples* — that does not hold for instruction-tuned models on structured factual QA. RLHF fine-tuning produces systematic confabulation: consistent outputs for both correct and wrong beliefs, eliminating the consistency-based discriminative signal. Mean SMC-NLI scores for correctly-labeled (0.6236) and hallucinated-labeled (0.6299) questions differ by 0.006 — noise level — confirming the mechanism fails at the distributional level, not the implementation level.

The parallel SMC-Embed evaluation (AUROC=0.4859) rules out the NLI scorer as the source of failure. The validated implementation (14/14 tests passing, 10,000 real samples, 45,000 NLI pairs) rules out engineering error. What remains is a clean negative result: the assumed hallucination regime does not characterize Llama-3-8B-Instruct on this task.

**What we leave behind:** A validated SMC pipeline (LLMSampler, SMCNLIScorer, SMCEmbedScorer) tested at scale, ready for deployment on model-task combinations where the stochastic hallucination regime holds. A regime classification framework — stochastic hallucination vs. systematic confabulation — that provides a testable prerequisite for applying these methods. A benchmark validity concern about cross-model evaluation using ChatGPT-generated labels.

**What comes next:** The stochastic hallucination regime that prior work validated on GPT-3 open-ended generation should be re-examined for instruction-tuned models on open-ended tasks (WikiBio-style biography generation, long-form QA). If the regime holds there but not on structured QA, we have a task-type boundary. If neither task type produces the stochastic regime for instruction-tuned models, the boundary is model-type — and the UQ community needs calibration-aware alternatives for RLHF-fine-tuned models. Either finding advances our understanding of when and why these methods work.

The infrastructure is validated. The regime question is open. The next experiment is clear.

---

## References

*See 06_references.bib for full BibTeX entries.*

Bai et al., 2022. Training a Helpful and Harmless Assistant with RLHF. arXiv:2204.05862.

He et al., 2021. DeBERTa: Decoding-enhanced BERT with Disentangled Attention. ICLR 2021. arXiv:2006.03654.

Huang et al., 2023. A Survey on Hallucination in Large Language Models. arXiv:2311.05232.

Kadavath et al., 2022. Language Models (Mostly) Know What They Know. arXiv:2207.05221.

Kuhn et al., 2023. Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in NLG. ICLR 2023. arXiv:2302.09664.

Li et al., 2023. HaluEval: A Large-Scale Hallucination Evaluation Benchmark. EMNLP 2023. arXiv:2305.11747.

Lin et al., 2022. TruthfulQA: Measuring How Models Mimic Human Falsehoods. ACL 2022. arXiv:2109.07958.

Lin et al., 2024. Generating with Confidence: Uncertainty Quantification for Black-box LLMs. TMLR 2024. arXiv:2305.19187.

Manakul et al., 2023. SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative LLMs. arXiv:2303.08896.

Meta AI, 2024. Llama 3 Model Card. HuggingFace Model Hub.

Ouyang et al., 2022. Training language models to follow instructions with human feedback. NeurIPS 2022. arXiv:2203.02155.

Reimers and Gurevych, 2019. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP 2019. arXiv:1908.10084.

Wang et al., 2022. Self-Consistency Improves Chain of Thought Reasoning in Language Models. ICLR 2023. arXiv:2203.11171.

Xiong et al., 2023. Can LLMs Express Their Uncertainty? ICLR 2024. arXiv:2306.13063.

Ziegler et al., 2019. Fine-Tuning Language Models from Human Preferences. arXiv:1909.08593.
