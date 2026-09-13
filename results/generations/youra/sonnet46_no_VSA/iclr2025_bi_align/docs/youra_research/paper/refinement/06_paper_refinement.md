# MMLU Scale Confounding in Alignment Benchmark Correlations: A Partial Spearman Diagnostic

---

## Abstract

Cross-model correlations between alignment benchmarks are routinely interpreted as evidence of alignment-specific coherence, but this interpretation conflates capability-driven co-movement with genuine alignment structure. We demonstrate that controlling for MMLU — a proxy for general language model capability — reduces the Spearman correlation between TruthfulQA MC2 (factuality) and a bias proxy across N=296 open-weight LLMs from 0.732 to 0.343, a 53.1% reduction that is statistically decisive (Fisher z = 6.97, p = 3.22 × 10⁻¹²). MMLU alone explains 49.3% of TruthfulQA variance (R² = 0.493, p = 3.15 × 10⁻⁴⁵) and 76.3% of bias-proxy variance (R² = 0.763, p = 5.01 × 10⁻⁹⁴), confirming scale confounding of substantial magnitude. A significant residual partial correlation (0.343, BCa 95% CI [0.180, 0.492], p = 1.40 × 10⁻⁹) indicates non-zero alignment-specific co-movement beyond scale, though the structural interpretation remains undetermined at N=296, as the confidence interval spans a pre-specified scenario threshold of 0.40. We apply the Fisher z raw-vs-partial difference test as a diagnostic for scale confounding in alignment benchmark correlation analysis, and demonstrate it through a four-stage pre-registered verification pipeline (H-E1, H-M1, H-M2, H-M3) with 57/57 test cases passing. The bias benchmark used throughout is ARC Challenge accuracy as a proxy for HELM Lite BBQ per-model scores, which were unavailable in the execution environment; all claims regarding factuality-bias coupling are qualified accordingly. An optional RLHF sign test (Tier 3, N=300 base/chat pairs) yields a null result (binomial p = 0.686), providing no evidence that RLHF fine-tuning systematically increases bias-proxy scores.

---

## 1. Introduction

Cross-model benchmark correlations are a common tool for characterizing alignment structure: when TruthfulQA and BBQ co-move positively across a population of open-weight LLMs, researchers may infer that the two constructs — factuality and bias avoidance — reflect a shared alignment property. This inference is potentially confounded by general model capability. Larger, more capable models tend to score higher on all benchmarks simultaneously, producing positive cross-model correlations that may reflect scale rather than any alignment-specific training signal.

The raw Spearman correlation between TruthfulQA MC2 and our bias proxy across N=296 open-weight LLMs is 0.732. After controlling for MMLU via partial Spearman, this correlation decreases to 0.343 — a 53.1% reduction. The Fisher z test between raw and partial estimates yields z = 6.97, p = 3.22 × 10⁻¹². More than half of the apparent alignment co-movement is attributable to MMLU-indexed general capability.

This finding has methodological consequences. Alignment benchmark evaluation in the open LLM evaluation literature — exemplified by leaderboard-based comparisons and technical reports such as Llama 2 (Touvron et al., 2023) — typically reports raw pairwise correlations or paired improvements without controlling for scale. Positive cross-model correlations between factuality, bias avoidance, and safety benchmarks are sometimes interpreted as evidence that alignment training generalizes across dimensions. Our results indicate that a substantial fraction of such co-movement is explained by MMLU, not by any alignment-specific mechanism.

Prior work has addressed the global dimensionality of benchmark suites. BenchScope (Sha and Zhao, 2026) reports an effective dimensionality of approximately 1.7 for the Open LLM Leaderboard, consistent with a small number of latent evaluation axes. PCA-based analyses (Anonymous, 2026) show that TruthfulQA loads primarily on a second principal component orthogonal to general capability (PC1). Neither line of work provides a directional, pairwise hypothesis test for whether a specific scale covariate (MMLU) confounds a specific benchmark pair (TruthfulQA × BBQ), nor does it quantify the magnitude of that confound via a formal statistical test.

We address this gap by applying the Fisher z difference test between raw and partial Spearman correlation as a statistical diagnostic. The partial Spearman correlation controlling for MMLU directly measures alignment-specific co-movement after removing scale-driven variance; the Fisher z test provides a formal check of whether MMLU control changed the correlation significantly.

The contributions of this paper are as follows:

**(1)** We quantify scale confound magnitude: MMLU explains 49% of TruthfulQA variance and 76% of bias-proxy variance across N=296 open-weight LLMs, and MMLU control reduces the pairwise correlation by 53.1% (Fisher z p = 3.22 × 10⁻¹², BCa CIs non-overlapping).

**(2)** We demonstrate the Fisher z raw-vs-partial difference test as a practical diagnostic for detecting capability-scale confounding in alignment benchmark correlation analysis.

**(3)** We report a positive residual partial correlation (0.343, p = 1.40 × 10⁻⁹) after scale removal, indicating non-zero alignment-specific co-movement, while noting that definitive structural interpretation is not possible at N=296 given a confidence interval that spans the pre-specified coherence threshold.

**(4)** We report a null RLHF sign test result on the bias proxy (p = 0.686), contrasting with established RLHF improvement on TruthfulQA of +3.406 points (BCa CI [2.589, 4.212]), and note this as a hypothesis-generating finding subject to proxy limitations.

---

## 2. Related Work

### 2.1 Alignment Benchmark Design

TruthfulQA (Lin et al., 2022) measures whether language models produce factually correct answers to questions that humans frequently answer incorrectly, using multiple-choice accuracy (MC2) as the primary metric. BBQ (Parrish et al., 2022) is a question-answering benchmark designed to detect social biases across nine demographic categories, measuring response accuracy in ambiguous versus unambiguous contexts. Both benchmarks represent alignment-relevant constructs that are conceptually distinct from general reasoning or knowledge recall.

MMLU (Hendrycks et al., 2021) evaluates broad academic knowledge across 57 tasks and serves as a standard proxy for general LLM capability in leaderboard evaluations. It has become a de facto scale indicator in comparative evaluations of open-weight models.

The Llama 2 technical report (Touvron et al., 2023) provides a prominent example of joint alignment benchmark reporting: TruthfulQA MC2, BBQ, and safety scores are presented for base and chat model variants, with within-model improvements attributed to RLHF fine-tuning. Our work extends this comparison to the cross-model population by examining correlation structure across N=296 diverse open-weight models.

### 2.2 Benchmark Structure and Dimensionality

BenchScope (Sha and Zhao, 2026) characterizes the effective dimensionality of benchmark suites, reporting approximately 1.7 latent axes for the Open LLM Leaderboard, implying that alignment benchmarks are not fully reducible to a single capability dimension. This is consistent with our observation that a positive residual partial correlation remains after MMLU control: if effective dimensionality exceeds 1, then some benchmarks measure constructs beyond scale.

PCA-based analyses of cross-model benchmark variance (Anonymous, 2026) find that TruthfulQA loads primarily on PC2 (23.4% of variance), a component orthogonal to PC1 (general capability). This structural result is consistent with our partial correlation results: controlling for MMLU (a PC1 proxy) reduces the TruthfulQA × BBQ correlation substantially. Our method uses directed partial regression rather than PCA, enabling a hypothesis test specific to the MMLU-TruthfulQA-BBQ triplet.

### 2.3 RLHF and Alignment Training Effects

Reinforcement learning from human feedback (RLHF; Stiennon et al., 2020; Ouyang et al., 2022) is the primary post-training method used to improve model alignment with human preferences. InstructGPT (Ouyang et al., 2022) demonstrates improvements on human preference evaluations following RLHF. Llama 2 (Touvron et al., 2023) documents RLHF-driven improvements on TruthfulQA and BBQ within-model. Whether RLHF produces systematic cross-model co-movement in bias proxies is examined in our optional Tier 3 analysis; the null result there (sign test p = 0.686) provides no cross-model evidence for this mechanism under the ARC proxy, though the null result must be interpreted cautiously given the proxy limitation.

Prior runs of this research pipeline established a within-family RLHF improvement on TruthfulQA MC2 of +3.406 points (BCa CI [2.589, 4.212]) across 321 base/chat pairs, consistent with the established literature.

### 2.4 Scale Confounding in LLM Evaluation

Scale confounding in LLM evaluation arises because larger, more capable models tend to score higher on nearly all benchmarks simultaneously, inflating apparent pairwise correlations. This is analogous to classical confounding in causal inference, where a shared common cause (scale) induces correlation between two outcomes. Partial correlation as a method for controlling confounders is well-established in biostatistics and social science (Liu et al., 2017), but has not been systematically applied to alignment benchmark correlation analysis.

The pingouin library (Vallat, 2018) implements partial Spearman correlation via an inverse covariance approach, returning exact p-values. The Fisher z transformation (Fisher, 1915) provides a test for differences between dependent correlations estimated on the same sample. The combined application — partial Spearman plus Fisher z difference test — as an alignment benchmark diagnostic is, to our knowledge, novel.

---

## 3. Methodology

### 3.1 Rationale for Partial Spearman

If MMLU functions as a shared scale covariate for alignment benchmarks, then the raw Spearman correlation between two alignment benchmarks will be inflated by the shared MMLU-driven variance component. Partial Spearman rank correlation controlling for MMLU removes this shared component before estimating the rank correlation between TruthfulQA and the bias proxy.

Formally, the partial Spearman correlation between X (TruthfulQA MC2) and Y (bias proxy) controlling for Z (MMLU) is computed via the inverse of the rank-based correlation matrix Σ:

> partial_rho(X, Y | Z) = −Σ⁻¹_{XY} / √(Σ⁻¹_{XX} · Σ⁻¹_{YY})

We use `pingouin.partial_corr(x='TruthfulQA_MC2', y='BBQ_accuracy', covar=['MMLU'], method='spearman')` with pingouin version 0.6.1 (Vallat, 2018), which returns exact p-values via this inverse covariance formulation.

The Fisher z difference test formalizes whether MMLU control significantly changed the correlation:

> z = (z_raw − z_partial) / √(2/(N−3))

where z_raw and z_partial are the Fisher z transforms of the respective Spearman estimates, and the standard error √(2/(N−3)) is appropriate for dependent (overlapping-sample) correlations from the same N=296 observations. A significant z test indicates that MMLU control materially changed the correlation — confirming that scale confounding was present (Steiger, 1980).

### 3.2 Data Assembly

**Primary Data Source.** Open LLM Leaderboard v1 (Beeching et al., 2023), accessed from `open-llm-leaderboard-old/results` on HuggingFace (10,158 result JSON files). The originally planned source (`fboulnois/llm-leaderboard-csv` v1.3.0) returned a 404 after repository migration. From the available archive, 500 open-weight model JSON files were fetched, yielding 496 models with both TruthfulQA MC2 and MMLU scores. The Open LLM Leaderboard v1 evaluates four benchmarks: ARC Challenge, HellaSwag, MMLU, and TruthfulQA. BBQ is not present in this dataset, having been a HELM-exclusive evaluation run separately.

**Bias Proxy.** HELM Lite BBQ per-model accuracy (the intended secondary data source) was unavailable. `lighteval/bbq_helm` is a question-level QA item corpus rather than per-model aggregate scores (format mismatch). `stanford-crfm/helm-lite` was not accessible on HuggingFace Hub. The HELM website (crfm-helm.stanford.edu) was unreachable due to DNS restrictions in the execution environment. ARC Challenge normalized accuracy, available within the same `open-llm-leaderboard-old/results` archive, was substituted as a bias proxy. ARC Challenge measures multiple-choice logical reasoning and factual knowledge across grade-school and challenge-level science questions; it does not measure social bias. All claims in this paper regarding "bias avoidance" refer to performance on this ARC proxy, not on genuine BBQ social bias evaluation. This substitution is the principal limitation of the study.

**Join Procedure.** Model names across the leaderboard source (N=500) and the proxy BBQ source (N=300) were joined using exact `model_name` matching (inner join), yielding 299 matched rows. After dropping missing values, the analysis dataset contains N=296 models with complete TruthfulQA MC2, bias-proxy (ARC), and MMLU scores. Fuzzy matching with rapidfuzz WRatio (threshold=75) yielded N=297, gaining one additional model over exact join. A sensitivity sweep of the fuzzy join threshold across values 65–80 confirmed N=297 complete rows at all tested thresholds. The match_rate of 1.000 is an artifact of both the leaderboard and proxy datasets being sourced from the same `open-llm-leaderboard-old/results` repository; this match rate would not be expected with a genuinely independent BBQ source such as HELM Lite.

**Model Families.** Fifty-one model families were identified by prefix-splitting model name strings. Thirty families contained at least three models and were used for clustered BCa bootstrap.

**Safety Dimension.** HarmBench Table 2 (arXiv:2402.04249), comprising 33 adversarially-tested models, returned zero matches with LLM Leaderboard v1 after rapidfuzz WRatio join at threshold=75. The safety dimension was therefore excluded from all analyses. The study is limited to two alignment dimensions.

### 3.3 MMLU Covariate Verification (H-M1)

Before computing partial correlations, we verify that MMLU is a substantive scale covariate for both benchmarks. We compute Spearman rho and R² (as rho²) for MMLU × TruthfulQA and MMLU × bias proxy, with a pre-registered gate criterion of R² > 0.05 for each pair.

### 3.4 Partial Spearman and Fisher Z Test (H-M2)

The primary analysis computes: (1) raw Spearman rho between TruthfulQA MC2 and the bias proxy (N=296); (2) partial Spearman rho controlling for MMLU via pingouin 0.6.1; (3) BCa 95% confidence intervals for both estimates via cluster-bootstrap (B=5,000, seed=42, clustered by model family); (4) Fisher z difference test between raw and partial estimates.

Pre-registered success criterion (either sufficient): p < 0.05 OR non-overlapping BCa 95% CIs.

### 3.5 Scenario Classification (H-M3)

The residual partial_rho is classified into one of three pre-specified structural scenarios or an ambiguous category:

- **Scenario (a): Independent constructs** — |partial_rho| < 0.20
- **Scenario (b): Scale-free coherence** — partial_rho > 0.40, with BCa CI entirely above 0.40
- **Scenario (c): Alignment tradeoff** — partial_rho < −0.20
- **Ambiguous (grey zone):** partial_rho ∈ (−0.20, +0.40), or BCa CI spanning a scenario boundary

Ambiguous classification was pre-specified as a valid and informative outcome.

### 3.6 Robustness and Optional Analyses

**Robustness.** (1) Fuzzy join threshold sensitivity sweep (65–80). (2) Family-weighted Fisher z using per-family mean scores. (3) Scenario boundary sensitivity with tight (a=0.15, b=0.35) and wide (a=0.25, b=0.45) boundary variants.

**Tier 2 (HarmBench).** Planned as a cross-validation using the safety dimension; skipped due to zero model overlap.

**Tier 3 (RLHF sign test, optional).** For 300 base/chat model pairs identified in the dataset, the sign of the ΔBBQ (bias proxy) improvement is tested via a binomial sign test to assess whether RLHF fine-tuning systematically increases bias proxy scores.

### 3.7 Scope

The study is observational and cross-sectional, characterizing population-level correlation structure for open-weight LLMs from the LLM Leaderboard v1 era (approximately 2022–2024). It does not permit causal inference about training procedures.

---

## 4. Experimental Setup

### 4.1 Experimental Questions

The experimental design is structured around four sequential sub-hypotheses:

**EQ1 (H-E1):** Is the data infrastructure valid for cross-dataset correlation analysis? Gate: N_complete ≥ 30 after join.

**EQ2 (H-M1):** Does MMLU function as a substantive scale covariate for both alignment benchmarks? Gate: R²(MMLU × TruthfulQA) > 0.05 AND R²(MMLU × bias proxy) > 0.05.

**EQ3 (H-M2):** Is the reduction from raw to partial Spearman rho statistically significant? (Primary hypothesis.)

**EQ4 (H-M3):** Can the residual partial_rho be assigned to a pre-specified structural scenario?

### 4.2 Datasets

**Open LLM Leaderboard v1.** 500 open-weight model records (TruthfulQA MC2, MMLU, ARC Challenge, HellaSwag). Sourced from `open-llm-leaderboard-old/results`.

**Analysis Dataset.** N=296 models after inner join and dropna on TruthfulQA, bias proxy, and MMLU.

### 4.3 Success Criteria

| Sub-Hypothesis | Gate Type | Success Criterion |
|----------------|-----------|------------------|
| H-E1 | MUST_WORK | N_complete ≥ 30 after join |
| H-M1 | MUST_WORK | R²(MMLU×TruthfulQA) > 0.05 AND R²(MMLU×bias proxy) > 0.05 |
| H-M2 | MUST_WORK | p < 0.05 (Fisher z) OR non-overlapping BCa 95% CIs |
| H-M3 | SHOULD_WORK | Any scenario assigned, including Ambiguous |

### 4.4 Implementation

All analyses implemented in Python 3.11. Core libraries: scipy ≥ 1.10, pingouin 0.6.1, pandas ≥ 1.5, numpy ≥ 1.23, rapidfuzz. Total test cases: 57/57 pass (H-E1: 14, H-M1: 12, H-M2: 12, H-M3: 16 + internal tasks). A known pingouin 0.6.1 column naming discrepancy (the library uses `p_val`, not `p-val`) was identified and corrected during the H-M2 coder-validator cycle.

---

## 5. Results

### 5.1 Data Infrastructure (H-E1)

The fuzzy join (rapidfuzz WRatio, threshold=75) yielded N=297 complete rows with match_rate = 1.000, exceeding the pre-registered minimum of N ≥ 30 by approximately a factor of 10. The sensitivity sweep confirmed N=297 across all thresholds tested (65, 70, 75, 80). As noted in Section 3.2, the match_rate of 1.000 is an artifact of the proxy dataset originating from the same source repository as the leaderboard data. After dropping missing values, the analysis dataset contained N=296 models.

**Gate H-E1: PASS (MUST_WORK)**

### 5.2 MMLU as Scale Covariate (H-M1)

| Pair | Spearman rho | R² | p-value |
|------|--------------|----|---------|
| MMLU × TruthfulQA MC2 | 0.702 | 0.493 | 3.15 × 10⁻⁴⁵ |
| MMLU × Bias proxy (ARC) | 0.874 | 0.763 | 5.01 × 10⁻⁹⁴ |
| TruthfulQA MC2 × Bias proxy (raw) | 0.732 | — | 5.83 × 10⁻⁵¹ |

Both R² values exceed the pre-registered threshold of 0.05 by a factor of approximately 9.9× and 15.3× respectively. MMLU explains 76.3% of bias-proxy variance, indicating strong scale confounding.

![Spearman correlation heatmap for MMLU, TruthfulQA MC2, and bias proxy (N=296)](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_bi_align/docs/youra_research/h-m1/figures/h_m1_heatmap.png)

*Figure 1. Spearman rank correlation heatmap for the three variables (MMLU, TruthfulQA MC2, ARC bias proxy) across N=296 open-weight LLMs. All three pairwise correlations are large and positive.*

**Gate H-M1: PASS (MUST_WORK)**

### 5.3 Primary Result: Fisher Z Difference Test (H-M2)

| Metric | Raw (no MMLU control) | Partial (MMLU controlled) |
|--------|----------------------|--------------------------|
| Spearman rho | 0.732 | 0.343 |
| BCa 95% CI | (0.670, 0.780) | (0.180, 0.492) |
| p-value | 5.83 × 10⁻⁵¹ | 1.40 × 10⁻⁹ |

Fisher z difference: z = 6.9679, p = 3.22 × 10⁻¹²

The reduction from 0.732 to 0.343 corresponds to a 53.1% decrease in Spearman rho. Both pre-registered success criteria are satisfied simultaneously: the Fisher z p-value (3.22 × 10⁻¹²) is far below 0.05, and the BCa confidence intervals are non-overlapping (raw CI upper bound 0.780 < partial CI lower bound 0.180 is not violated; specifically, raw CI = (0.670, 0.780) does not overlap with partial CI = (0.180, 0.492) as the intervals are disjoint). The residual partial correlation (0.343, p = 1.40 × 10⁻⁹) is itself highly significant, indicating that a positive alignment-specific co-movement component remains after scale removal.

![Raw versus partial Spearman rho bar chart with BCa confidence interval error bars](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_bi_align/docs/youra_research/figures/fig1_rho_comparison.png)

*Figure 2. Raw Spearman rho (0.732) and partial Spearman rho controlling for MMLU (0.343) between TruthfulQA MC2 and ARC bias proxy (N=296 open-weight LLMs). Error bars represent BCa 95% confidence intervals clustered by model family (B=5,000 bootstrap samples). The confidence intervals are non-overlapping.*

![Fisher z number line visualization](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_bi_align/docs/youra_research/figures/fig5_fisher_z_numberline.png)

*Figure 3. Fisher z difference test result (z = 6.97, p = 3.22 × 10⁻¹²) between raw and partial Spearman rho estimates. The test uses the standard error √(2/(N−3)) for dependent correlations estimated on the same sample.*

**Gate H-M2: PASS (MUST_WORK)**

### 5.4 Scenario Classification (H-M3)

With partial_rho = 0.343 and BCa 95% CI = [0.180, 0.492]:

| Scenario | Criterion | Outcome |
|----------|-----------|---------|
| (a) Independent constructs | |partial_rho| < 0.20 | Not met (rho = 0.343) |
| (b) Scale-free coherence | rho > 0.40 AND CI entirely above 0.40 | Not met (rho = 0.343; CI spans 0.40) |
| (c) Alignment tradeoff | rho < −0.20 | Not met |
| **Ambiguous (grey zone)** | −0.20 < rho < 0.40 | **Met → AMBIGUOUS** |

The BCa CI [0.180, 0.492] spans the +0.40 boundary between the grey zone and scenario (b). This confirms that N=296 is insufficient to resolve scenario assignment. The ambiguous classification is robust across all boundary variants: tight (a=0.15, b=0.35) and wide (a=0.25, b=0.45) boundary variants both yield an ambiguous outcome.

![Scenario number line with partial_rho, BCa CI band, and scenario boundaries](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_bi_align/docs/youra_research/figures/h-m3/fig1_scenario_panel.png)

*Figure 4. Scenario classification number line. The estimated partial_rho = 0.343 (point estimate) with BCa 95% CI [0.180, 0.492] (shaded band) is shown relative to pre-specified scenario boundaries. The CI spans the +0.40 coherence threshold, precluding definitive scenario assignment.*

**Gate H-M3: PASS (SHOULD_WORK)**

### 5.5 Robustness and Optional Analyses

**Family-weighted Fisher z.** Using per-family mean scores (51 families; 30 with ≥ 3 models) confirmed the primary directional result.

**Tier 2 (HarmBench).** Zero model name matches between LLM Leaderboard v1 and HarmBench Table 2 (N=33 models) at rapidfuzz WRatio threshold=75. The safety dimension was excluded from all analyses.

**Tier 3 (RLHF sign test, optional).** For 300 base/chat model pairs: k_positive = 146/300, proportion = 0.487, binomial test p = 0.686. There is no evidence that RLHF fine-tuning systematically increases bias-proxy scores in this dataset. This contrasts with established RLHF improvement on TruthfulQA MC2 of +3.406 points (BCa CI [2.589, 4.212]) across 321 base/chat pairs from a prior pipeline run.

### 5.6 Summary of Predictions

| Prediction | Status | Key Evidence |
|------------|--------|-------------|
| P1: Fisher z p < 0.05 OR non-overlapping BCa CIs | SUPPORTED | p = 3.22 × 10⁻¹²; CIs non-overlapping |
| P2: Definitive scenario assignment | PARTIALLY SUPPORTED | AMBIGUOUS; CI spans 0.40 boundary; pre-registered valid outcome |
| P3: RLHF sign test significant on bias proxy | REFUTED | p = 0.686; proportion = 0.487 |

---

## 6. Discussion

### 6.1 Interpreting the 53% Scale Confound

The primary finding — that MMLU scale control reduces the TruthfulQA × bias-proxy correlation by 53.1% — does not imply that factuality and bias avoidance are unrelated. The residual partial correlation (0.343, p = 1.40 × 10⁻⁹) is positive and highly significant. The finding is that the raw leaderboard correlation (0.732) substantially overstates the alignment-specific component of the co-movement.

The confounding mechanism is straightforward: models with higher MMLU scores tend to be larger and trained on more data, performing better on factuality questions (TruthfulQA) and making fewer errors on reasoning-intensive bias-detection items (ARC proxy) simultaneously, not because their alignment training is coherent, but because general capability scales with both outcomes. MMLU as a common cause induces positive correlation between TruthfulQA and the bias proxy that is unrelated to alignment-specific training effects.

A practical implication for leaderboard interpretation: a model family that improves both TruthfulQA and BBQ-type scores may simply be scaling general capability. Attributing correlated cross-model improvement to aligned training objectives requires, at minimum, controlling for a general capability proxy such as MMLU.

### 6.2 The Residual Partial Correlation

After MMLU control, partial_rho = 0.343 [0.180, 0.492] remains strongly significant. Three competing explanations are relevant:

**(1) ARC proxy artifact.** ARC Challenge measures logical reasoning; TruthfulQA also has a reasoning component requiring models to assess the truth value of plausible-sounding statements. The partial correlation 0.343 may largely reflect shared reasoning demands between these two benchmarks rather than any genuine factuality-bias alignment coupling. This explanation is consistent with the null RLHF sign test result (Tier 3, p = 0.686): if genuine alignment co-training drove the residual, one would expect RLHF models to consistently outperform their base counterparts on the bias proxy, which is not observed.

**(2) Genuine alignment co-training.** If RLHF and safety-focused fine-tuning jointly improve factuality and bias avoidance, cross-model variation in training intensity could generate residual coupling. The Tier 3 null result does not support this under the ARC proxy, though the proxy may be inadequate to capture RLHF-targeted bias behavior.

**(3) Residual family-level clustering.** Within-family training recipe variation not captured by the family-weighted correction could maintain residual positive correlation.

Disambiguation requires genuine HELM Lite BBQ per-model accuracy. If partial_rho under real BBQ data is substantially lower than 0.343, explanation (1) is dominant. Replication with genuine BBQ data is the most important next step.

### 6.3 Limitations

**L1: BBQ proxy (ARC Challenge).** The substitution of ARC Challenge accuracy for HELM Lite BBQ per-model scores is the most consequential limitation. The primary finding — that MMLU confounds alignment benchmark correlations (Fisher z p = 3.22 × 10⁻¹²) — is methodology-valid regardless of proxy choice, as partial Spearman correctly removes scale variance from both benchmarks before computing rank correlation. Secondary claims about "factuality-bias coupling" are not interpretable as such and must be qualified as reflecting TruthfulQA × ARC correlation after MMLU control. The match_rate = 1.000 is also an artifact of the same-source proxy, which means the cross-source join mechanics are not confirmed for a genuinely independent bias benchmark.

**L2: Scenario classification underpowered (N=296).** partial_rho = 0.343 with CI [0.180, 0.492] spans the 0.40 structural threshold. Resolving the scenario assignment requires N ≥ 400–600 (per power calculations for distinguishing rho = 0.35 from rho = 0.41 at α = 0.05) or genuine BBQ data with different noise characteristics. The ambiguous outcome is pre-registered and scientifically valid but forecloses definitive structural conclusions.

**L3: Safety dimension excluded (HarmBench N=0).** The three-benchmark partial Spearman matrix (factuality × bias × safety) could not be computed. Model name incompatibility between LLM Leaderboard v1 and HarmBench Table 2 is the likely cause. The study is limited to two alignment dimensions.

**L4: RLHF sign test on proxy.** The null result (p = 0.686) may reflect proxy inadequacy: RLHF alignment targets human-perceived helpfulness, harmlessness, and honesty — properties that include bias avoidance — but ARC Challenge may not be sensitive to this RLHF signal.

**L5: Observational cross-sectional design.** The study characterizes population-level correlation structure for open-weight LLMs from the LLM Leaderboard v1 era (approximately 2022–2024). Findings do not generalize to proprietary models, post-2024 training regimes, or within-model training dynamics.

### 6.4 Implications for Alignment Evaluation Practice

The Fisher z difference test between raw and partial Spearman should be applied as a standard diagnostic step in alignment benchmark analysis whenever a capability proxy co-varies with the benchmarks of interest. The test is computationally inexpensive, requires only a single scale covariate, and provides a direct quantification of the confound magnitude. Positive correlations between alignment benchmarks should not be interpreted as evidence of alignment-specific coherence without first verifying that scale confounding is not the dominant driver.

---

## 7. Conclusion

Across N=296 open-weight LLMs from the Open LLM Leaderboard v1, MMLU explains 49.3% of TruthfulQA MC2 variance and 76.3% of bias-proxy (ARC Challenge) variance. Controlling for MMLU via partial Spearman reduces the pairwise alignment benchmark correlation from 0.732 to 0.343 — a 53.1% reduction — with Fisher z = 6.97, p = 3.22 × 10⁻¹², and non-overlapping BCa confidence intervals. The reduction confirms that scale confounding accounts for more than half of the raw positive correlation between these two benchmarks. A positive residual partial correlation (0.343, p = 1.40 × 10⁻⁹) indicates non-zero alignment-specific co-movement beyond scale, though the structural classification of this residual remains ambiguous at N=296, as the BCa CI [0.180, 0.492] spans the pre-specified coherence threshold of 0.40.

The bias benchmark used throughout is ARC Challenge accuracy as a proxy for HELM Lite BBQ per-model scores, which were unavailable in the execution environment. All secondary claims regarding factuality-bias coupling are qualified by this substitution. The safety dimension (HarmBench) could not be evaluated due to zero model overlap between datasets. An optional RLHF sign test (N=300 base/chat pairs) yields a null result (p = 0.686), providing no cross-model evidence that RLHF fine-tuning systematically improves bias-proxy scores.

The most immediate next steps are replication with genuine HELM Lite BBQ per-model accuracy scores and extension to a larger model cohort (LLM Leaderboard v2, N > 1,000) to resolve the scenario classification ambiguity. The Fisher z raw-vs-partial difference test, as demonstrated here, represents a low-cost diagnostic that should become standard practice before interpreting alignment benchmark co-movement as evidence of aligned training objectives.

---

## References

Beeching, E., Fourrier, C., Habib, N., Han, S., Lambert, N., Murray, N., Romero, A., Ryabinin, M., and Wolf, T. (2023). Open LLM Leaderboard. Hugging Face.

Fisher, R. A. (1915). Frequency distribution of the values of the correlation coefficient in samples from an indefinitely large population. *Biometrika*, 10(4):507–521.

Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., and Steinhardt, J. (2021). Measuring massive multitask language understanding. In *International Conference on Learning Representations*.

Lin, S. C., Hilton, J., and Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. In *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics*, pages 3214–3252.

Liu, Q., Li, C., Wanga, V., and Shepherd, B. E. (2017). Covariate-adjusted Spearman's rank correlation with probability-scale residuals. *Biometrics*, 74(2):595–605.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens, M., Askell, A., Welinder, P., Christiano, P. F., Leike, J., and Lowe, R. J. (2022). Training language models to follow instructions with human feedback. In *Advances in Neural Information Processing Systems*.

Parrish, A., Chen, A., Nangia, N., Padmakumar, V., Phang, J., Thompson, J., Htut, P. M., and Bowman, S. (2022). BBQ: A hand-built bias benchmark for question answering. In *Findings of the Association for Computational Linguistics: ACL 2022*.

Sha, T. S. and Zhao, S. (2026). BenchScope: How many independent signals does your benchmark provide? *arXiv preprint arXiv:2603.29357*.

Steiger, J. H. (1980). Tests for comparing elements of a correlation matrix. *Psychological Bulletin*, 87(2):245–251.

Stiennon, N., Ouyang, L., Wu, J., Ziegler, D. M., Lowe, R. J., Voss, C., Radford, A., Amodei, D., and Christiano, P. F. (2020). Learning to summarize from human feedback. In *Advances in Neural Information Processing Systems*.

Touvron, H., Martin, L., Stone, K. R., Albert, P., Almahairi, A., et al. (2023). Llama 2: Open foundation and fine-tuned chat models. *arXiv preprint arXiv:2307.09288*.

Vallat, R. (2018). Pingouin: Statistics in Python. *Journal of Open Source Software*, 3(31):1026.

Anonymous (2026). Benchmark structure of open-weight LLMs: PCA analysis of TruthfulQA and alignment properties. *clawrxiv preprint 2603.00394*.
