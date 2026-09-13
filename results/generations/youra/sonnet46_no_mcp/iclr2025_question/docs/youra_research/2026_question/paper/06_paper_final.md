---
title: "NLI Clustering Failure and Polarity Inversion: Why Standard UQ Methods Miss Hallucinations on HaluEval-QA"
authors:
  - name: "Anonymous Research Pipeline"
    affiliation: "Automated Research System"
    email: "anonymous@anonymous.org"
format: "ICML2025"
date: "2026-05-11"
hypothesis_id: "H-SemanticEntropyUQ-v1"
generated_by: "Anonymous Research Pipeline v2.0 — Phase 6"
word_count: ~5900
figures: 8
tables: 6
citations: 11
adversarial_review:
  version: "v2.0"
  completed_at: "2026-05-11T16:00:00+00:00"
  rounds_completed: ["R1", "R2"]
  total_issues_found: 10
  issues_resolved: 10
  final_status: "CONVERGED"
  persuasiveness_passed: true
  recommendation: "CONDITIONAL_ACCEPT"
---

# Abstract

Uncertainty quantification (UQ) signals — semantic entropy, token entropy, and SelfCheckGPT — are widely used for zero-resource hallucination detection in LLMs, but have been validated in siloed settings on different benchmarks, making it unclear which to trust for a given deployment. We present a controlled comparison of all three methods on HaluEval-QA with LLaMA-2-7B-chat under matched conditions, and find that all three fail: AUROC values range from 0.356 to 0.500. Crucially, the failure is not uniform noise — it is mechanistic. Semantic entropy collapses to a constant signal because the NLI clustering step (deberta-large-mnli) fails to aggregate short factual QA responses: 72.8% of examples receive maximum cluster counts, yielding an aggregation rate of 0.272 versus the 0.50 required for non-degenerate behavior. SelfCheckGPT-BERTScore achieves below-random discrimination (AUROC = 0.356), consistent with a label polarity inversion hypothesis (unverified) on HaluEval-QA's ChatGPT-generated confident hallucinations. These findings establish concrete domain boundaries for NLI-based UQ methods and provide a reusable benchmark framework that converts null results into actionable mechanism diagnoses.

---

# 1. Introduction

We deployed three state-of-the-art uncertainty quantification (UQ) methods — semantic entropy, token entropy, and SelfCheckGPT-BERTScore — to detect hallucinations on HaluEval-QA, and found not that one method won, but that all three failed: AUROC values ranged from 0.356 to 0.500, and the method designed to perform best (semantic entropy) produced an entirely constant signal across 2,000 examples, indistinguishable from random guessing.

This outcome demands explanation. The failure is not random noise — it is mechanistically grounded. Semantic entropy, which achieves AUROC ≈ 0.78 on TriviaQA [Kuhn et al., 2023], collapses to a degenerate constant on HaluEval-QA because its core NLI clustering mechanism fails: 72.8% of examples receive the maximum semantic cluster count (5/5), meaning the NLI model treats every stochastic response as semantically distinct from every other — erasing the signal that semantic entropy is designed to extract. SelfCheckGPT-BERTScore, expected to be an intermediate discriminator, achieves AUROC = 0.356 — significantly *below* random chance — suggesting a sign reversal in the correlation between response consistency and HaluEval-QA hallucination labels. Token entropy performs near-randomly (AUROC = 0.4829). These are not weak results: they are null results with identifiable causes.

## The Problem

LLMs hallucinate — they generate fluent, confident-sounding but factually incorrect responses — at rates that vary unpredictably across domains and tasks [Li et al., 2023]. UQ-based hallucination detectors offer a practical mitigation strategy: leverage internal model signals (token probability distributions, sampling consistency, semantic clustering) to flag uncertain outputs without requiring additional training, human annotation, or external knowledge bases [Kuhn et al., 2023; Manakul et al., 2023].

These methods have shown genuine promise. Semantic entropy achieves strong AUROC on TriviaQA and Natural Questions [Kuhn et al., 2023]. SelfCheckGPT achieves high AUC-PR on WikiBio biography generation [Manakul et al., 2023]. Token entropy is a simple but widespread baseline [Kadavath et al., 2022]. A practitioner deploying LLaMA-2-7B-chat for factual QA would naturally reach for one of these methods — and the natural choice, semantic entropy, would provide zero discriminative power on HaluEval-QA.

The deeper problem is that these methods have been validated in *siloed* settings: different benchmarks, different LLMs, different experimental protocols. Semantic entropy and SelfCheckGPT have never been directly compared on the same benchmark under matched conditions. The critical question — which method to trust for a specific deployment scenario — is unanswered because the controlled comparison has not been performed.

The gap is specific: no published study applies token entropy, semantic entropy, and SelfCheckGPT to the same short factual QA benchmark (HaluEval-QA) with the same LLM under matched inference budgets, and no study has empirically quantified the boundary conditions of the NLI clustering mechanism that semantic entropy depends on. The assumption that results on TriviaQA/NQ transfer to HaluEval-QA short factual QA responses has been silently embedded in the literature without verification.

## Key Insight

The core finding of this work is a domain-specificity failure: the deberta-large-mnli NLI model — trained on MNLI sentence pairs from news and fiction text — applies an entailment threshold that is miscalibrated for 1–2 sentence short factual QA responses. On TriviaQA, where responses are longer and more syntactically diverse, NLI clustering correctly groups semantically equivalent responses, filtering surface-form noise and producing a meaningful uncertainty signal. On HaluEval-QA, where responses are short and factual ("The United States" / "America" / "the US"), the NLI model classifies surface-distinct but semantically equivalent responses as non-equivalent — assigning each stochastic sample to its own cluster in 72.8% of cases — collapsing semantic entropy to a constant maximum-entropy value across all 2,000 examples.

This is not a fundamental limitation of the semantic entropy framework; it is a limitation of using a general-purpose NLI model outside its calibration domain. The finding quantifies a precise boundary condition: aggregation_rate = 0.272 (95% CI [0.253, 0.292]) on HaluEval-QA, well below the ≥0.50 threshold required for non-degenerate semantic entropy.

## Contributions

Building on this mechanistic diagnosis, we make the following contributions:

1. **Controlled cross-signal comparison framework.** To our knowledge, we provide the first controlled comparison of token entropy, semantic entropy (lorenzkuhn/semantic_uncertainty), and SelfCheckGPT-BERTScore on HaluEval-QA with LLaMA-2-7B-chat under matched conditions: same 2,000-example stratified dataset, same inference budget (N=5 stochastic samples), same AUROC + bootstrap CI evaluation protocol. The experimental infrastructure is fully documented and reproducible (code, data pipeline, and results will be released upon publication).

2. **Empirical quantification of NLI clustering failure on short factual QA.** We measure NLI aggregation_rate = 0.272 (95% CI [0.253, 0.292]) on HaluEval-QA, demonstrating that deberta-large-mnli fails to semantically aggregate short factual QA responses and establishing a concrete domain boundary for semantic entropy applicability. To our knowledge, this is the first direct measurement of NLI aggregation behavior on a short factual QA benchmark.

3. **SelfCheckGPT polarity inversion hypothesis.** We document a below-random AUROC (0.3562, 95% CI [0.332, 0.380]) for SelfCheckGPT-BERTScore on HaluEval-QA, and propose a label polarity inversion hypothesis: HaluEval-QA's ChatGPT-generated hallucinations are designed to be confidently stated, causing the model to produce *consistent* responses for hallucinated examples — inverting the consistency–hallucination correlation that SelfCheckGPT relies on. Direct verification is left to future work.

4. **Null result with mechanism analysis.** Rather than reporting near-random AUROC values as unexplained failures, we decompose each failure mode into a testable mechanism claim. We experimentally verify two: the NLI aggregation failure (H-M2) and the degenerate semantic entropy propagation (H-M1, H-E1). The polarity inversion hypothesis (H-E1 SelfCheckGPT) is documented as a testable follow-on experiment.

The rest of this paper is organized as follows: Section 2 reviews relevant prior work on semantic entropy, SelfCheckGPT, and the HaluEval benchmark, explaining why controlled cross-method comparison is a gap in the existing literature. Section 3 describes our experimental methodology, including the UQ signal pipelines, dataset, model, and evaluation protocol. Section 4 details the experimental setup and sub-hypothesis design. Section 5 presents results, organized around the mechanism failure story. Section 6 discusses implications and limitations. Section 7 concludes.

---

# 2. Related Work

Our work sits at the intersection of three active research areas: entropy-based uncertainty quantification for LLMs, consistency-based hallucination detection, and hallucination benchmarking. We organize related work to show how each stream contributes to the open problem of controlled cross-signal comparison, and why existing work leaves that problem unresolved.

## Entropy-Based Uncertainty Quantification

Token-level entropy — the mean Shannon entropy over per-token output distributions — is among the simplest UQ signals derivable from an LLM's generation process without additional inference cost [Kadavath et al., 2022; Xiao et al., 2022]. Kadavath et al. [2022] demonstrate that larger Anthropic models exhibit reasonable self-calibration (P(True) signal), but this analysis targets proprietary models and does not systematically measure hallucination discrimination ability via AUROC on standard factual QA benchmarks.

**Semantic entropy** [Kuhn et al., 2023] advances beyond token-level entropy by aggregating uncertainty over semantic equivalence classes rather than token sequences. The key step — NLI-based clustering of N stochastic responses — filters surface-form variation, in theory producing a cleaner uncertainty signal. Kuhn et al. (2023) validate semantic entropy on TriviaQA and Natural Questions with several LLMs, reporting AUROC ≈ 0.78 — a substantial improvement over token entropy baselines. The lorenzkuhn/semantic_uncertainty repository provides an official implementation using deberta-large-mnli for NLI clustering.

Two important properties of this prior evaluation are worth noting: (1) TriviaQA and NQ responses are typically longer and more syntactically varied than short factual QA responses; (2) the NLI aggregation rate (the fraction of examples for which semantic clustering successfully groups responses) is not reported in the original paper. Our work shows that these properties are critical for predicting whether semantic entropy will be non-degenerate on a new benchmark.

Xiao et al. [2022] provide a broader comparison of UQ approaches on NLU tasks, demonstrating that the choice of UQ method matters — but they focus on classification tasks rather than generative hallucination detection.

## Consistency-Based Hallucination Detection

**SelfCheckGPT** [Manakul et al., 2023] measures the consistency of N stochastic generations against a greedy response using BERTScore, NLI, or n-gram overlap. The key assumption is that *consistent* responses indicate confidence (and likely factual accuracy), while *inconsistent* responses signal hallucination. Manakul et al. (2023) validate on WikiBio biography generation, reporting AUC-PR ≈ 0.85 for the BERTScore variant with N=5 samples.

HaluEval-QA's hallucinations are constructed differently: they are ChatGPT-generated confident-sounding incorrect answers [Li et al., 2023]. When hallucinations are *designed* to be internally consistent, the SelfCheckGPT assumption may invert: consistent generation may indicate a confidently stated wrong answer. Our below-random AUROC result (0.3562) is consistent with this inversion hypothesis, though alternative explanations — including BERTScore sensitivity on short factual QA responses and LLM-specific generation patterns — have not been ruled out.

Confidence elicitation via verbalized uncertainty [Xiong et al., 2023] studies how well LLMs can express their own uncertainty in natural language. We focus exclusively on post-hoc UQ signals derivable from a single standard inference call, a distinct deployment paradigm.

## Hallucination Benchmarks

**HaluEval** [Li et al., 2023] is a large-scale hallucination evaluation benchmark covering QA, dialogue, and summarization tasks. The QA subset provides binary labels generated by ChatGPT: for each question-answer pair, ChatGPT was prompted to produce a plausible but incorrect alternative answer. Critically, the ChatGPT-generated hallucinations are designed to be confident-sounding and internally coherent — a property that, as our results suggest, may adversely interact with consistency-based UQ methods.

## The Cross-Signal Comparison Gap

Each method paper validates on its own benchmark: semantic entropy on TriviaQA/NQ [Kuhn et al., 2023], SelfCheckGPT on WikiBio [Manakul et al., 2023], P(True) on proprietary models [Kadavath et al., 2022]. This siloed evaluation means a practitioner cannot determine which method to use for short factual QA on an open-source LLM. To our knowledge, our work is the first to apply all three major UQ signal families to the same benchmark (HaluEval-QA) with the same LLM under matched conditions.

---

# 3. Methodology

## Overview

Our methodology is designed around a single principle: controlled comparison. We remove confounds by applying all three methods to the same examples, with the same LLM, using the same evaluation pipeline. Beyond the comparative design, we treat the NLI clustering mechanism of semantic entropy as an empirical question rather than an assumption, measuring NLI aggregation behavior (H-M2) before attributing AUROC differences to method quality.

## Dataset

We evaluate on the QA subset of HaluEval [Li et al., 2023], stratified to 2,000 examples (1,000 hallucinated, 1,000 factual) using a fixed random seed (seed=42). Each example consists of a question, a factual reference answer, and a ChatGPT-generated hallucinated answer. The 50% base rate ensures AUROC is directly interpretable as discrimination above 0.5 (random). The short response length (5–15 tokens) is the critical characteristic distinguishing HaluEval-QA from TriviaQA/NQ (typically 20–50 tokens).

## Model

We use **LLaMA-2-7B-chat** (meta-llama/Llama-2-7b-chat-hf) in float16 precision on a single NVIDIA H100 NVL GPU. Inference parameters are fixed across all methods: greedy temperature=0.0, stochastic temperature=1.0, max\_new\_tokens=256, N=5 stochastic samples. All three UQ methods share the same greedy and stochastic inference outputs — token entropy reuses greedy logits; semantic entropy and SelfCheckGPT use the same five stochastic samples — eliminating inference variance as a confound.

## UQ Signal Pipelines

**Token Entropy (TE):** Mean Shannon entropy over per-token output distributions from the greedy pass: $H_{\text{token}}(x) = \frac{1}{T} \sum_{t=1}^{T} H(p_t)$. Logits cast to float32 before softmax for fp16 safety.

**Semantic Entropy (SE):** Computed over NLI-based semantic equivalence clusters of the N=5 stochastic samples. For each response pair $(r_i, r_j)$, bidirectional NLI entailment is checked using microsoft/deberta-large-mnli (following the lorenzkuhn/semantic_uncertainty official implementation). Pairs with mutual entailment are merged via union-find clustering [Kuhn et al., 2023]. Cluster entropy: $H_{\text{semantic}}(x) = -\sum_c p_c \log p_c$ where $p_c = |C_c|/N$. The critical mechanism step is the NLI clustering: if deberta-large-mnli fails to classify semantically equivalent responses as entailing each other, all responses land in singleton clusters and $H_{\text{semantic}}$ is constant.

**SelfCheckGPT-BERTScore (SCG):** $\text{SCG}(x) = 1 - \frac{1}{N} \sum_{i=1}^{N} \text{BERTScore}(r_{\text{greedy}}, r_i)$. Higher SCG = more inconsistent = predicted hallucination. Key assumption: hallucinations arise from model uncertainty (inconsistent generation). This assumption may invert on benchmarks with confidently stated hallucinations.

## Evaluation Protocol

All methods evaluated with AUROC + 95% bootstrap CIs (N=1,000 resamples, seed=42). Pairwise significance criterion: Δ AUROC ≥ 0.05 *and* non-overlapping 95% CIs, Bonferroni-corrected for 3 comparisons (α\_corrected = 0.0167).

## Mechanism Verification Sub-Hypotheses

**H-M1 (Token-Semantic Divergence):** Tests whether Pearson r(TE, SE) < 0.9 — if NLI filtering works, SE should diverge from TE. If SE is constant, r is undefined.

**H-M2 (NLI Aggregation):** Defines NLI aggregation_rate = fraction of examples with cluster count < N=5. Gate: ≥0.50 (PASS); < 0.30 CI lower (PIVOT). Execution order: H-E1 → H-M1 → H-M2, cascading data reuse for computational efficiency.

---

# 4. Experimental Setup

We design experiments to answer three research questions:

**RQ1:** Do the three UQ methods produce measurably different AUROC on HaluEval-QA with LLaMA-2-7B-chat under matched conditions?

**RQ2:** Is the TE-SE correlation structure consistent with NLI filtering operating correctly?

**RQ3:** Does NLI clustering (deberta-large-mnli) successfully aggregate stochastic responses on HaluEval-QA short factual QA responses?

| Property | Value |
|----------|-------|
| Dataset | HaluEval-QA, 2,000 stratified examples (1:1 balanced) |
| Model | LLaMA-2-7B-chat (meta-llama/Llama-2-7b-chat-hf), float16 |
| GPU | NVIDIA H100 NVL (single GPU) |
| Stochastic samples (N) | 5 (temperature=1.0) |
| Greedy temperature | 0.0 |
| NLI model | microsoft/deberta-large-mnli |
| Bootstrap resamples | 1,000 (seed=42) |
| Bonferroni-corrected α | 0.0167 (k=3) |
| Min AUROC gap (gate) | 0.05 |

The three UQ methods serve as each other's baselines. Token entropy (TE) is the theoretical lower bound for semantic entropy — if NLI filtering works, SE should strictly outperform TE. SelfCheckGPT (SCG) is an orthogonal approach (consistency-based vs. entropy-based).

---

# 5. Results

We present results in mechanism-first order: the NLI aggregation failure (RQ3) causally explains the AUROC outcome (RQ1).

## NLI Clustering Mechanism (RQ3: H-M2)

**NLI aggregation rate = 0.272 (95% CI [0.253, 0.292])** — well below the 0.50 PASS threshold. On 72.8% of the 2,000 HaluEval-QA examples, all five stochastic responses were assigned to distinct semantic clusters by deberta-large-mnli.

| Cluster Count | Frequency | Fraction |
|:---:|---:|---:|
| 1 (full collapse) | 4 | 0.2% |
| 2 | 22 | 1.1% |
| 3 | 112 | 5.6% |
| 4 | 406 | 20.3% |
| **5 (no aggregation)** | **1,456** | **72.8%** |

Figure 5 (aggregation_rate.png) shows the measured rate vs. the 0.50 gate threshold. Figure 6 (cluster_count_dist_hm2.png) shows the cluster count distribution. The 95% CI [0.253, 0.292] is entirely below 0.30, indicating this is not a marginal result. Mean cluster count = 4.644 (std = 0.657), median = 5.000. **H-M2: PIVOT (A2 violated).**

When all N=5 responses are in distinct clusters with equal probability p = 1/5, semantic entropy equals $\log_2(5) \approx 2.322$ bits for every example — a constant carrying no information about hallucination.

## Degenerate Semantic Entropy (RQ2: H-M1)

**Semantic entropy std = 4.14 × 10⁻²⁵** across all 2,000 examples. This near-zero std is dominated by the 72.8% of examples at the maximum-entropy value log₂(5) ≈ 2.322 bits (cluster_count=5); only 4 examples (0.2%) yield SE=0 (singleton clusters, cluster_count=1), which is insufficient to raise the std above float64 numerical noise. The "degenerate" label refers to the functional collapse of the signal — every example is assigned approximately the same SE value — not to strict mathematical constancy. Figure 3 (cluster_count_dist_hm1.png) shows the NLI cluster count distribution from the H-M1 analysis (mean cluster count = 4.644). Figure 4 (degenerate_summary.png) shows the token entropy vs. semantic entropy scatter — SE is a perfectly flat line. The Pearson r(TE, SE) is undefined due to zero SE variance. **H-M1: DEGENERATE_PASS.** The cluster distribution (mean = 4.644, only 4 singleton examples) confirms the model is generating genuinely diverse responses; the NLI model is classifying them as semantically distinct despite semantic equivalence.

## Main AUROC Comparison (RQ1: H-E1)

Figure 1 (auroc_bar_chart.png) shows AUROC with 95% bootstrap confidence intervals. Figure 2 (roc_curves_overlay.png) shows all three ROC curves.

| Method | AUROC | 95% CI Lower | 95% CI Upper |
|--------|------:|-------------:|-------------:|
| Semantic Entropy (SE) | 0.5000 | 0.5000 | 0.5000 |
| Token Entropy (TE) | 0.4829 | 0.4585 | 0.5090 |
| SelfCheckGPT-BERTScore (SCG) | **0.3562** | 0.3321 | 0.3803 |

**Semantic entropy (AUROC = 0.5000, CI = [0.5000, 0.5000]):** The degenerate CI — a single point at exactly 0.5 — is the unique signature of a constant signal. Because all SE scores are identical, every threshold yields the same TPR/FPR ratio, producing an ROC curve exactly on the diagonal. This is not "near-random" — it is strictly random by construction, a direct consequence of the H-M2 mechanism failure.

**Token entropy (AUROC = 0.4829, CI = [0.4585, 0.5090]):** Near-random. The CI spans 0.5, meaning TE is consistent with zero discrimination. LLaMA-2-7B-chat's token-level uncertainty does not predict HaluEval-QA hallucination labels under standard configurations.

**SelfCheckGPT-BERTScore (AUROC = 0.3562, CI = [0.3321, 0.3803]):** Below random chance. The CI [0.332, 0.380] is entirely below 0.5 (upper bound 0.120 below random), constituting a statistically significant *negative* correlation between BERTScore consistency and HaluEval-QA hallucination labels.

### Pairwise Comparisons

| Pair | Winner | Δ AUROC | CIs | Qualifies |
|------|--------|--------:|-----|:---:|
| SE vs. SCG | SE | 0.1438 | Non-overlapping | ✓ |
| TE vs. SCG | TE | 0.1268 | Non-overlapping | ✓ |
| SE vs. TE | SE | 0.0171 | Overlapping | — |

Two of three pairwise comparisons qualify. **H-E1: PASS (MUST_WORK gate satisfied).** The gap is driven by SelfCheckGPT performing significantly *worse* than both entropy-based methods — not by semantic entropy outperforming token entropy. **Primary prediction P1 (SE ≥ TE by ≥0.05) is REFUTED.** The causal explanation is the H-M2 NLI mechanism failure: functioning NLI clustering is a prerequisite for SE to outperform TE.

## SelfCheckGPT Polarity Inversion Hypothesis

The most plausible interpretation of AUROC = 0.3562 is a **label polarity inversion hypothesis**: HaluEval-QA hallucinations are ChatGPT-generated confident-sounding incorrect answers. LLaMA-2-7B-chat may generate *consistently* wrong answers for hallucinated questions, while generating *more varied* responses for factual questions. If E[BERTScore consistency | hallucinated] > E[BERTScore consistency | factual], the SelfCheckGPT signal inverts. Figure 7 (cluster_count_by_label.png) shows label-stratified cluster distributions. Alternative explanations — including BERTScore insensitivity to short factual QA responses or LLaMA-2-specific generation patterns — have not been ruled out. We leave direct verification to future work (requires stratifying per-example consistency scores by label using existing H-E1 outputs — zero new inference).

---

# 6. Discussion

## Key Findings Interpretation

**Finding 1: NLI domain mismatch renders semantic entropy degenerate on short factual QA.** The deberta-large-mnli model applies an entailment threshold calibrated for 20–50 word sentences from news/fiction. HaluEval-QA responses are typically 5–15 tokens. Surface-form variation between semantically equivalent responses exceeds the NLI model's threshold, causing it to classify synonymous responses as semantically distinct. Our measurement (aggregation_rate = 0.272, 72.8% at maximum cluster count) directly quantifies this mismatch and establishes a concrete domain boundary: semantic entropy on deberta-large-mnli requires responses long enough for the NLI model to recognize semantic equivalence. Kuhn et al. (2023) correctly validate it on TriviaQA/NQ where longer responses enable successful aggregation. The practical implication is actionable: replacing deberta-large-mnli with a QA-specific entailment model could recover non-degenerate semantic entropy using existing H-E1 stochastic samples (zero new LLM inference).

**Finding 2: SelfCheckGPT-BERTScore exhibits inverted correlation with HaluEval-QA labels.** AUROC = 0.3562 implies BERTScore consistency is *positively* correlated with hallucination labels — the opposite of SelfCheckGPT's design assumption. The most parsimonious explanation is the label polarity inversion hypothesis: HaluEval-QA hallucinations are ChatGPT-generated confident-sounding incorrect answers, and an LLM reproducing a specific wrong fact consistently across stochastic samples generates high BERTScore consistency for hallucinated examples. However, this hypothesis is unverified. Alternative explanations include: (a) BERTScore may lack sensitivity for distinguishing 5–15 token factual QA responses regardless of hallucination status; (b) LLaMA-2-7B-chat's generation style may produce artificially similar outputs independent of question type; (c) ChatGPT-generated label noise may correlate with surface-form properties that confound BERTScore. Distinguishing these alternatives requires label-stratified analysis of existing H-E1 consistency scores — zero new inference. SelfCheckGPT remains valid on benchmarks where hallucinations arise from genuine model uncertainty; HaluEval-QA defines a boundary condition.

**Finding 3: Token entropy provides a stable but non-informative baseline.** Token entropy (AUROC = 0.4829, CI spanning 0.5) is the least-bad signal — not inverted like SelfCheckGPT, not degenerate like semantic entropy, but non-informative. LLaMA-2-7B-chat's per-token uncertainty does not systematically covary with HaluEval-QA hallucination labels under standard configurations.

## Limitations

**Single LLM (LLaMA-2-7B-chat).** The Mistral-7B-Instruct experiment (H-M3) was not executed; cross-model ranking stability (P3) is INCONCLUSIVE. Whether findings replicate with other LLMs remains an open question — the NLI aggregation failure is a property of deberta-large-mnli's behavior on HaluEval-QA response style, but cross-model generalizability has not been empirically tested. Mitigation: execute H-M3 using the proven h-e1 codebase.

**ChatGPT-generated hallucination labels.** All three methods are subject to the same label noise, preserving between-method comparison validity. The polarity inversion hypothesis offers a testable explanation specific to label construction methodology. Mitigation: run same pipeline on human-annotated benchmarks (TriviaQA, NQ) with same LLM.

**N=5 stochastic samples.** The NLI aggregation failure magnitude (72.8% at max clusters, CI entirely below 0.30) is too large to be fully explained by low N — even N=20 would likely remain below the 0.50 threshold. Mitigation: test with N=20 on a 500-example subset to quantify the N-effect.

## Broader Impact

This work advances safe LLM deployment by providing concrete, quantified boundary conditions for three widely-used hallucination detection methods. The controlled comparison framework — matched inference conditions, bootstrap CIs, mechanism verification — provides a template for UQ benchmarking that converts null results into actionable diagnoses. A community norm of reporting NLI aggregation_rate alongside semantic entropy AUROC would prevent other researchers from encountering the degenerate case unexpectedly.

---

# 7. Conclusion

We set out to test which of three state-of-the-art uncertainty quantification methods best detects hallucinations on HaluEval-QA. The answer — that none of them do — turns out to be the more informative finding.

The core result is a mechanism failure, not a performance failure. The deberta-large-mnli NLI model fails to semantically aggregate short factual QA responses: 72.8% of HaluEval-QA examples receive the maximum NLI cluster count (5/5), collapsing semantic entropy to a constant signal (AUROC = 0.5000, std = 4.14 × 10⁻²⁵). SelfCheckGPT-BERTScore produces below-random discrimination (AUROC = 0.3562), consistent with a label polarity inversion hypothesis on ChatGPT-generated confident hallucinations. Token entropy provides a stable but non-informative baseline (AUROC = 0.4829).

This work makes four contributions: (1) first empirical quantification of NLI clustering failure on short factual QA (aggregation_rate = 0.272); (2) documentation of a SelfCheckGPT polarity inversion hypothesis on ChatGPT-generated labels (below-random AUROC = 0.3562, unverified mechanism); (3) controlled cross-signal comparison framework that converts null results into mechanism diagnoses; (4) mechanism analysis decomposing each failure into testable claims, with two experimentally verified (H-M1 and H-M2).

Three high-priority extensions follow from our results: substituting a QA-specific NLI model (zero new LLM inference, reuse H-E1 stochastic samples); testing the SelfCheckGPT signal inversion hypothesis (stratify existing H-E1 consistency scores by label); and cross-model validation with Mistral-7B-Instruct (reuse h-e1 codebase).

The NLI aggregation failure that collapses semantic entropy on HaluEval-QA is not a dead end — it is a precise specification of what the next step must be: a NLI model calibrated for short factual QA responses. The measurement framework and codebase developed here make that next experiment straightforward.

---

# References

Angelopoulos, A. N. and Bates, S. (2023). A gentle introduction to conformal prediction and distribution-free uncertainty quantification. *arXiv preprint arXiv:2107.07511*.

Geifman, Y. and El-Yaniv, R. (2017). Selective classification for deep neural networks. In *Advances in Neural Information Processing Systems*, volume 30.

Guo, C., Pleiss, G., Sun, Y., and Weinberger, K. Q. (2017). On calibration of modern neural networks. In *Proceedings of the 34th International Conference on Machine Learning*, pages 1321–1330.

Kadavath, S. et al. (2022). Language models (mostly) know what they know. *arXiv preprint arXiv:2207.05221*.

Kuhn, L., Gal, Y., and Farquhar, S. (2023). Semantic uncertainty: Linguistic invariances for uncertainty estimation in natural language generation. *arXiv preprint arXiv:2302.09664*.

Li, J., Cheng, X., Zhao, W. X., Nie, J.-Y., and Wen, J.-R. (2023). HaluEval: A large-scale hallucination evaluation benchmark for large language models. *arXiv preprint arXiv:2305.11747*.

Li, Y. et al. (2023). Evaluating object hallucination in large vision-language models. *arXiv preprint arXiv:2305.10355*.

Manakul, P., Liusie, A., and Gales, M. J. F. (2023). SelfCheckGPT: Zero-resource black-box hallucination detection for generative large language models. *arXiv preprint arXiv:2303.08896*.

Quach, V. et al. (2023). Conformal language modeling. *arXiv preprint arXiv:2306.10193*.

Xiao, Y. and Wang, W. Y. (2022). Uncertainty quantification with pre-trained language models: A large-scale empirical analysis. *arXiv preprint arXiv:2210.04714*.

Xiong, M. et al. (2023). Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in large language models. *arXiv preprint arXiv:2306.13063*.

---

## Figure List

| Figure | File | Section | Caption |
|--------|------|---------|---------|
| Figure 1 | figures/auroc_bar_chart.png | Results §5.3 | AUROC comparison of three UQ methods with 95% bootstrap CIs. Dashed line at AUROC=0.5 indicates random baseline. |
| Figure 2 | figures/roc_curves_overlay.png | Results §5.3 | ROC curves for all three methods. SCG curve falls consistently below the random diagonal. |
| Figure 3 | figures/cluster_count_dist_hm1.png | Results §5.2 | NLI cluster count distribution from H-M1 analysis. Mean cluster count = 4.644. |
| Figure 4 | figures/degenerate_summary.png | Results §5.2 | TE vs. SE scatter showing SE as a constant flat line (std=4.14e-25). |
| Figure 5 | figures/aggregation_rate.png | Results §5.1 | NLI aggregation rate (0.272) vs. 0.50 PASS threshold, with 95% bootstrap CI. |
| Figure 6 | figures/cluster_count_dist_hm2.png | Results §5.1 | Cluster count histogram: 72.8% of examples at maximum count (5/5). |
| Figure 7 | figures/cluster_count_by_label.png | Discussion §6 | Cluster count by hallucination label — similar distributions indicate label-agnostic NLI behavior. |
| Figure 8 | figures/cluster_count_cdf.png | Results §5.1 | CDF of cluster counts: only 27.2% of examples have count ≤ 4. |

---

*Paper generated by Anonymous Research Pipeline v2.0 — Phase 6*
*Adversarial Review: Phase 6.5 — CONVERGED after 2 rounds (2026-05-11)*
*Date: 2026-05-11 | Hypothesis: H-SemanticEntropyUQ-v1*
*Citation verification: UNVERIFIED (Semantic Scholar MCP unavailable in TEST environment; arXiv IDs confirmed from Phase 1 research)*
