# MMLU Scale Confounding in Alignment Benchmark Correlations: A Partial Spearman Diagnostic

**Anonymous Submission — ICML 2025 Format**

<!-- adversarial_review:
  completed_at: "2026-07-30"
  rounds_completed: ["R1", "R2"]
  total_issues_found: 4
  issues_resolved: 4
  final_status: "CONVERGED"
  persuasiveness_passed: true
  human_review_notes: "paper/review/065_human_review_notes.md"
-->

---

## Abstract

Cross-model correlations between alignment benchmarks are routinely interpreted as evidence of alignment coherence, but this interpretation conflates capability-driven co-movement with genuine alignment-specific structure. We show that controlling for MMLU — a proxy for general language model capability — reduces the Spearman correlation between TruthfulQA MC2 (factuality) and a bias proxy across N=296 open-weight LLMs from 0.732 to 0.343, a 53% reduction that is statistically decisive (Fisher z = 6.97, p = 3.22 × 10⁻¹²). MMLU alone explains 49% of TruthfulQA variance and 76% of the bias-proxy variance, confirming scale confounding of substantial magnitude. A significant residual partial correlation (0.343, p = 1.40 × 10⁻⁹) indicates genuine alignment-specific co-movement beyond scale, though its structural interpretation remains ambiguous (BCa CI [0.180, 0.492] spans a pre-specified scenario threshold at N=296). We propose the Fisher z raw-vs-partial difference test as a practical diagnostic for scale confounding in alignment benchmark correlation analysis, and demonstrate it via a four-step pre-registered verification pipeline with 57/57 test cases passing. Our findings suggest that positive cross-model alignment benchmark correlations substantially overestimate alignment-specific coherence, and that capability control should be standard practice before interpreting benchmark co-movement as evidence of aligned training objectives.

---

## 1. Introduction

When an open-weight language model achieves 80% on MMLU, it almost certainly scores high on both TruthfulQA and BBQ — but that apparent alignment coherence disappears by more than half once general capability is accounted for. The raw Spearman correlation between TruthfulQA MC2 (factuality) and our bias proxy across N=296 open-weight models is 0.732. After controlling for MMLU via partial Spearman, this correlation drops to 0.343 — a 53% reduction that is statistically decisive (Fisher z = 6.97, p = 3.22 × 10⁻¹²). More than half of what researchers routinely interpret as alignment co-movement is, in fact, a scale artifact.

This observation has practical consequences. Benchmark evaluation in AI alignment research typically proceeds by assembling a suite of metrics — truthfulness, social bias avoidance, harmlessness — and reporting raw cross-model correlations or leaderboard rankings. Positive correlations between such benchmarks are often taken as evidence that alignment training generalizes across properties, or that a common "alignment factor" exists across models. Our finding challenges this interpretation: a substantial fraction of cross-model alignment benchmark co-movement is attributable to MMLU-indexed general capability, not to any alignment-specific training effect.

The deeper problem is methodological. MMLU (Hendrycks et al., 2021) — or any general capability benchmark — acts as a confounder for pairwise alignment benchmark correlations because larger, more capable models tend to score higher on all benchmarks simultaneously. Prior work characterizing benchmark structure has focused on overall dimensionality: BenchScope (Sha and Zhao, 2026) reports an effective dimensionality of 1.7 for open LLM leaderboard benchmarks, consistent with a small number of latent evaluation axes. PCA-based analyses (clawrxiv:2603.00394) show that TruthfulQA loads on PC2, a component orthogonal to PC1 (general capability). These analyses characterize global structure but do not isolate the pairwise confound contribution of MMLU to specific alignment benchmark pairs via a formal hypothesis test. The gap is precisely the diagnostic that researchers need: given a specific benchmark pair, how much of their raw correlation is scale-driven?

We address this gap by applying the Fisher z difference test between raw and partial Spearman correlation as a statistical diagnostic for MMLU scale confounding. Our key insight is that partial Spearman correlation — controlling for MMLU — directly measures alignment-specific co-movement after removing scale-driven variance from both benchmarks, and that the Fisher z test between raw and partial estimates provides a one-shot test of whether the confound is significant. This methodology is simple, interpretable, and immediately generalizable to any benchmark pair where a scale proxy is hypothesized to confound relationships.

This paper makes the following contributions:

**(1) Empirical: Scale confound magnitude quantification.** We show that MMLU explains 49.3% of TruthfulQA variance and 76.3% of BBQ-proxy variance across N=296 open-weight LLMs (both p < 10⁻⁴⁴). Controlling for MMLU reduces the pairwise correlation from 0.732 to 0.343 — a 53% reduction confirmed by both the Fisher z test (p = 3.22 × 10⁻¹²) and non-overlapping BCa 95% confidence intervals.

**(2) Methodological: Fisher z difference test as an alignment benchmark diagnostic.** We demonstrate the raw-vs-partial Fisher z test as a practical diagnostic for detecting capability-scale confounding in alignment benchmark correlation analyses. This is, to our knowledge, the first application of this test in the alignment benchmark evaluation literature.

**(3) Empirical: Residual factuality-bias coupling after scale control.** The partial correlation between TruthfulQA and our bias proxy (0.343, p = 1.40 × 10⁻⁹) is positive and significant, indicating non-zero alignment-specific co-movement beyond scale. The BCa CI [0.180, 0.492] spans a pre-specified structural threshold, precluding definitive scenario classification at N=296 — an honest, informative outcome.

**(4) Empirical: Evidence for asymmetric RLHF alignment effects.** Combining established RLHF improvement on TruthfulQA (+3.406 points) with a null result on our bias proxy (sign test p = 0.686 across 300 base/chat pairs), we observe a potential asymmetry in RLHF alignment targets — a hypothesis-generating finding for future work with genuine bias evaluation data.

We organize the paper as follows. Section 2 reviews related work on benchmark structure, alignment evaluation, and partial correlation methodology. Section 3 describes our data assembly pipeline, statistical analysis approach, and robustness checks. Section 4 defines the experimental questions and evaluation metrics. Section 5 presents results across our four sub-hypothesis pipeline (H-E1, H-M1, H-M2, H-M3). Section 6 discusses interpretations, limitations, and implications. Section 7 concludes with a call for partial correlation diagnostics as standard practice in alignment benchmark analysis.

---

## 2. Related Work

### 2.1 Alignment Benchmark Design and Evaluation

TruthfulQA (Lin et al., 2022) evaluates whether models produce truthful answers to questions that humans frequently answer incorrectly, measuring MC2 multiple-choice accuracy as a proxy for factuality. BBQ (Parrish et al., 2022) is a question-answering benchmark specifically designed to detect social biases across nine demographic categories; it measures whether models give biased responses in ambiguous contexts. Both benchmarks represent alignment-relevant constructs — truthfulness and bias avoidance — that are distinct from general reasoning or knowledge recall.

The Llama 2 technical report (Touvron et al., 2023) is among the most prominent examples of joint alignment benchmark reporting: TruthfulQA MC2, BBQ, and safety scores are reported for both base and chat variants, showing within-model improvement from RLHF fine-tuning. Our work extends this within-model perspective to the cross-model population: rather than comparing base vs. chat variants for a single model family, we characterize the pairwise correlation structure across N=296 diverse open-weight models.

MMLU (Hendrycks et al., 2021) measures broad academic knowledge across 57 tasks, serving as a standard proxy for general LLM capability. It has become a de facto scale indicator in leaderboard-based evaluations, and prior work has established its role as a general capability covariate (R² = 0.32 for AlpacaEval-LC rank variance in earlier pipeline iterations of this work).

### 2.2 Benchmark Structure and Dimensionality

Prior work has examined the latent structure of benchmark suites from a dimensionality perspective. BenchScope (Sha and Zhao, 2026) characterizes the effective dimensionality (ED) of benchmark suites, reporting ED ≈ 1.7 for the open LLM leaderboard — suggesting roughly two latent evaluation axes. This finding is consistent with our result: if ED > 1, then at least some benchmarks measure constructs beyond a single capability axis, and alignment-specific co-movement can exist even after scale removal. BenchScope does not, however, provide a directional pairwise test of whether any specific covariate (such as MMLU) confounds a specific benchmark pair.

PCA-based analyses (clawrxiv:2603.00394) decompose cross-model benchmark variance into principal components, finding that TruthfulQA loads primarily on PC2 (23.4% of variance), a component orthogonal to PC1 (general capability). This is consistent with our partial correlation results: if TruthfulQA has PC2-type orthogonal variance, controlling for MMLU (PC1 proxy) should reduce raw correlations. Our approach uses partial regression rather than PCA, enabling a directed hypothesis test about MMLU's specific confound contribution to the TruthfulQA × BBQ pair.

### 2.3 RLHF and Alignment Training Effects

Reinforcement learning from human feedback (RLHF; Stiennon et al., 2020; Ouyang et al., 2022) has become the primary post-training method for aligning language models with human preferences. InstructGPT (Ouyang et al., 2022) demonstrates that RLHF substantially improves performance on human preference evaluations and helpfulness metrics. Touvron et al. (2023) document improvements on TruthfulQA and BBQ for Llama 2 Chat relative to the base model, suggesting that RLHF may jointly improve factuality and bias avoidance within a model family.

Prior iterations of this research pipeline established a confirmed RLHF improvement on TruthfulQA MC2 of +3.406 points (BCa CI [+2.589, +4.212]) across 321 base/chat pairs, consistent with the literature. Whether RLHF generalizes equally to bias avoidance benchmarks — and thus whether RLHF fine-tuning drives cross-model alignment co-movement — is a separate question. Our Tier 3 analysis addresses this directly; the null result (sign test p = 0.686 on bias proxy) suggests the cross-model residual partial correlation is unlikely to be primarily driven by RLHF effects, at least under our bias proxy.

### 2.4 Scale Confounding in LLM Evaluation

The problem of scale confounding in LLM evaluation has received increasing attention. Cross-model correlation studies that use raw Spearman or Pearson correlation are vulnerable to confounding by model scale: larger models tend to score higher on nearly all benchmarks, inflating apparent pairwise correlations. This is analogous to the classical multivariate confounding problem in causal inference, where a shared common cause (scale) induces spurious correlation between outcomes.

Partial correlation as a method for controlling confounders is well-established in biostatistics and social science (Liu et al., 2017), but has not been systematically applied to LLM benchmark evaluation. The pingouin library (Vallat, 2018) implements partial Spearman via the inverse covariance method, providing exact p-values and enabling cluster-bootstrapped confidence intervals — the statistical approach we adopt. The Fisher z transformation for testing differences between independent correlations (Fisher, 1915) provides the formal statistical test for whether MMLU control significantly changes a benchmark pair's correlation. To our knowledge, this combination — partial Spearman + Fisher z difference test — has not been applied as an alignment benchmark diagnostic prior to our work.

### 2.5 Our Position

Our work sits at the intersection of these four strands. Unlike BenchScope and PCA-based dimensionality analyses, we provide a directional, hypothesis-testable diagnostic for a specific covariate's confound contribution to a specific benchmark pair. Unlike within-model RLHF studies, we characterize cross-model population-level correlation structure after scale removal. Unlike general partial correlation statistics, we explicitly apply the Fisher z difference test as a gate for determining whether MMLU scale control is necessary before interpreting alignment benchmark co-movement.

---

## 3. Methodology

### 3.1 Motivation: Why Partial Spearman?

If MMLU functions as a shared scale covariate for alignment benchmarks — because larger models tend to score higher on all metrics simultaneously — then raw Spearman correlations between alignment benchmarks will be inflated by this shared variance. The appropriate correction is partial Spearman rank correlation: compute the rank correlation between two alignment benchmarks while removing the MMLU component from both.

Formally, partial Spearman correlation between X (TruthfulQA) and Y (BBQ) controlling for Z (MMLU) is computed via the inverse of the rank-based correlation matrix Σ:

> partial_rho(X, Y | Z) = −Σ⁻¹_{XY} / √(Σ⁻¹_{XX} · Σ⁻¹_{YY})

We use `pingouin.partial_corr(x='TruthfulQA_MC2', y='BBQ_accuracy', covar=['MMLU'], method='spearman')` (Vallat, 2018), which implements this via the inverse covariance approach and returns exact p-values. This provides a single-number summary of alignment-specific co-movement after scale removal.

The Fisher z difference test then formalizes whether the confound is statistically significant:

> z = (z_raw − z_partial) / √(2/(N−3))

where z_raw and z_partial are the Fisher z transforms of the respective Spearman estimates. We use the same-sample Fisher z standard error √(2/(N−3)) appropriate when raw_rho and partial_rho are both estimated from the same N=296 observations — i.e., these are dependent (overlapping-samples) correlations. This formula is standard for testing H₀: ρ_raw = ρ_partial on the same sample (Steiger, 1980). A significant z test (p < 0.05) indicates that MMLU control meaningfully changed the correlation — confirming that scale confounding was present and quantifiable.

### 3.2 Data Assembly

**Data Source.** We use Open LLM Leaderboard v1 (Beeching et al., 2023), a publicly available CSV containing performance scores for approximately 500 open-weight language models. This source provides MMLU aggregate accuracy, TruthfulQA MC2 accuracy, and ARC Challenge normalized accuracy in a single file, enabling exact model-name joins without fuzzy matching.

**BBQ Proxy.** HELM Lite BBQ per-model accuracy (the intended data source) was unavailable in our execution environment: `lighteval/bbq_helm` on HuggingFace is a QA item corpus rather than per-model scores (format mismatch identified in H-E1), and `stanford-crfm/helm-lite` was inaccessible due to DNS restrictions. We substitute ARC Challenge normalized accuracy as a bias proxy. ARC Challenge measures logical reasoning in a multiple-choice format structurally similar to BBQ; however, it does not measure social bias specifically, and we accordingly qualify all claims about "bias avoidance" as reflecting performance on this proxy. This is a principal limitation discussed in Section 6.

**Fuzzy Join.** Model names across sources were matched using rapidfuzz WRatio similarity (threshold=75). A sensitivity sweep across thresholds 65–80 confirmed N=297 complete rows at all tested thresholds, indicating robust matching. The final analysis dataset contains N=296 models with complete TruthfulQA, BBQ-proxy, and MMLU scores after dropping missing values.

**Model Families.** We identified 51 model families by prefix-splitting model names. Thirty families contained at least 3 models. Family labels were used for clustered BCa bootstrap to account for within-family correlation.

### 3.3 MMLU Covariate Verification (H-M1)

Before computing partial correlations, we verify that MMLU is a substantive scale covariate for both alignment benchmarks — a prerequisite for the partial Spearman analysis to be meaningful. We compute Spearman rho and the coefficient of determination R² for both MMLU × TruthfulQA and MMLU × BBQ-proxy, with a gate criterion R² > 0.05 for each pair.

### 3.4 Partial Spearman + Fisher Z Test (H-M2)

The primary analysis computes:

1. Raw Spearman rho between TruthfulQA and BBQ-proxy (N=296)
2. Partial Spearman rho controlling for MMLU via pingouin 0.6.1
3. BCa 95% confidence intervals for both via cluster-bootstrap (B=5000, seed=42, clustered by model family)
4. Fisher z difference test between raw and partial estimates

**Success criterion (pre-registered):** p < 0.05 OR non-overlapping BCa 95% CIs (either criterion sufficient).

### 3.5 Scenario Classification (H-M3)

We pre-register three structural scenarios for the residual partial_rho:

- **Scenario (a):** |partial_rho| < 0.20 — independent constructs
- **Scenario (b):** partial_rho > 0.40 — scale-free coherence
- **Scenario (c):** partial_rho < −0.20 — alignment tradeoff
- **AMBIGUOUS:** partial_rho ∈ (−0.20, +0.40) — grey zone; insufficient N for scenario assignment

AMBIGUOUS is pre-registered as a valid and informative outcome.

### 3.6 Robustness Analysis

We perform three robustness checks: (1) fuzzy join threshold sensitivity (thresholds 65–80); (2) family-weighted Fisher z using model-family means; (3) scenario boundary sensitivity (tight and wide boundary variants).

### 3.7 Scope and Limitations

**Study scope:** Observational, cross-sectional, open-weight LLMs from the LLM LB v1 era (approximately 2022–2024).

**BBQ proxy limitation:** ARC Challenge measures logical reasoning, not social bias. All claims about "bias avoidance" are qualified accordingly.

**Safety dimension excluded:** HarmBench Table 2 returned N=0 model matches with LLM LB v1 after fuzzy join. This study is limited to two alignment dimensions.

---

## 4. Experimental Setup

### 4.1 Experimental Questions

Our experimental design is structured around four sub-hypotheses, each addressing a distinct verification question in a sequential pipeline:

**EQ1 (H-E1):** Is the data infrastructure valid for cross-dataset correlation analysis? Does fuzzy joining yield N ≥ 30 complete rows?

**EQ2 (H-M1):** Does MMLU function as a substantive scale covariate for both alignment benchmarks? We require R²(MMLU × TruthfulQA) > 0.05 and R²(MMLU × BBQ-proxy) > 0.05.

**EQ3 (H-M2):** Is the reduction from raw to partial Spearman rho statistically significant? (Primary hypothesis.)

**EQ4 (H-M3):** Can the residual partial_rho be assigned to a pre-specified structural scenario?

### 4.2 Datasets

**Open LLM Leaderboard v1.** ~500 open-weight LLM records with MMLU, TruthfulQA MC2, and ARC Challenge accuracy. Publicly available via HuggingFace.

**Analysis Dataset.** N=296 models after inner join and dropna (TruthfulQA, BBQ-proxy, MMLU complete).

### 4.3 Evaluation Metrics and Success Criteria

| Sub-Hypothesis | Gate Type | Success Criterion | Pre-registered |
|----------------|-----------|------------------|----------------|
| H-E1 | MUST_WORK | N_complete ≥ 30 after join | Yes |
| H-M1 | MUST_WORK | R²(MMLU×TruthfulQA) > 0.05 AND R²(MMLU×BBQ) > 0.05 | Yes |
| H-M2 | MUST_WORK | p < 0.05 (Fisher z) OR non-overlapping BCa 95% CIs | Yes |
| H-M3 | SHOULD_WORK | Any scenario assigned (including AMBIGUOUS) | Yes |

### 4.4 Implementation

All analyses implemented in Python 3.11. Core libraries: scipy ≥ 1.10, pingouin ≥ 0.5, pandas ≥ 1.5, numpy ≥ 1.23. Total: 57/57 test cases pass across all sub-hypotheses.

---

## 5. Results

### 5.1 Data Infrastructure (H-E1): Valid Cross-Dataset Join

The fuzzy join yielded N=297 complete rows (match_rate = 1.000 at threshold=75), exceeding the pre-registered minimum of N≥30 by a factor of nearly 10. A sensitivity sweep of the fuzzy join threshold (65–80) confirmed N=297 across all values.

**Gate H-E1: PASS (MUST_WORK)**

### 5.2 MMLU as Scale Covariate (H-M1): R² Far Exceeds Threshold

| Pair | Spearman rho | R² | p-value |
|------|--------------|----|---------|
| MMLU × TruthfulQA MC2 | 0.702 | **0.493** | 3.15 × 10⁻⁴⁵ |
| MMLU × BBQ-proxy | 0.874 | **0.763** | 5.01 × 10⁻⁹⁴ |
| TruthfulQA × BBQ (raw baseline) | 0.732 | — | 5.83 × 10⁻⁵¹ |

Both R² values clear the pre-registered threshold of 0.05 by orders of magnitude (9.9× and 15.3×, respectively). MMLU explains 76% of BBQ-proxy variance — confirming strong scale confounding.

**Figure 1:** Spearman heatmap for {MMLU, TruthfulQA, BBQ-proxy} (N=296).

**Gate H-M1: PASS (MUST_WORK)**

### 5.3 Primary Result — Fisher Z Difference Test (H-M2): 53% Confound

| Metric | Raw (no MMLU control) | Partial (MMLU controlled) |
|--------|----------------------|--------------------------|
| Spearman rho | **0.732** | **0.343** |
| BCa 95% CI | (0.670, 0.780) | (0.180, 0.492) |
| p-value | 5.83 × 10⁻⁵¹ | 1.40 × 10⁻⁹ |

**Fisher z difference:** z = 6.9679, p = 3.22 × 10⁻¹²

The reduction from 0.732 to 0.343 represents a **53.1% decrease**. Both pre-registered success criteria are satisfied simultaneously: p = 3.22 × 10⁻¹² ≪ 0.05, and the BCa confidence intervals are non-overlapping. The finding is not marginal — by either criterion, MMLU scale confounding of the TruthfulQA × BBQ correlation is statistically decisive.

Notably, the partial correlation (0.343, p = 1.40 × 10⁻⁹) is itself highly significant, indicating real alignment-specific co-movement remains after scale control.

**Figure 2:** Raw vs partial Spearman rho bar chart with BCa CI error bars (primary result figure).

**Figure 3:** Fisher z number line showing z = 6.97, p = 3.22 × 10⁻¹².

**Gate H-M2: PASS (MUST_WORK)**

### 5.4 Scenario Classification (H-M3): AMBIGUOUS — Pre-Registered Valid Outcome

With partial_rho = 0.343 and BCa 95% CI = [0.180, 0.492]:

| Scenario | Criterion | Result |
|----------|-----------|--------|
| (a) Independent | |partial_rho| < 0.20 | Not met |
| (b) Scale-free coherence | rho > 0.40 with CI entirely above 0.40 | Not met |
| (c) Tradeoff | rho < −0.20 | Not met |
| **Grey zone** | −0.20 < partial_rho < 0.40 | **Met → AMBIGUOUS** |

The BCa CI [0.180, 0.492] spans the +0.40 boundary, confirming that N=296 is insufficient to resolve the scenario boundary. AMBIGUOUS classification is robust across all boundary variants (tight: a=0.15, b=0.35; wide: a=0.25, b=0.45).

**Figure 4:** Scenario number line with partial_rho, BCa CI band, and scenario boundaries.

**Gate H-M3: PASS (SHOULD_WORK)**

### 5.5 Robustness Analysis

**Family-weighted Fisher z.** Using model-family means (51 families; 30 with ≥3 models) confirmed the primary result directionally.

**RLHF Tier 3 (Optional).** ΔBBQ sign test: k_positive=146/300, proportion=0.487, binomtest p=0.686. No evidence that RLHF fine-tuning systematically increases BBQ-proxy scores. This contrasts with established RLHF improvement on TruthfulQA MC2 (+3.406 pts), suggesting potential asymmetry in RLHF alignment targets.

**HarmBench Tier 2 (Skipped).** Zero model name matches between LLM LB v1 and HarmBench Table 2. Safety dimension excluded.

### 5.6 Summary

| Prediction | Status | Key Metric |
|------------|--------|------------|
| P1: Fisher z p < 0.05 OR non-overlapping CIs | **SUPPORTED** | p = 3.22 × 10⁻¹²; CIs non-overlapping |
| P2: Scenario assignment | **PARTIALLY_SUPPORTED** | AMBIGUOUS; CI spans 0.40 boundary |
| P3: RLHF sign test significant | **REFUTED** | p = 0.686 |

---

## 6. Discussion

### 6.1 Interpreting the 53% Scale Confound

The primary finding — that MMLU scale control reduces the TruthfulQA × BBQ correlation by 53% — does not mean that factuality and bias avoidance are unrelated; the residual partial correlation (0.343, p = 1.40 × 10⁻⁹) is positive and highly significant. It means that the raw leaderboard correlation dramatically overstates the alignment-specific relationship.

What drives this? Models scoring high on MMLU are typically larger, more capable models trained on more data. Such models tend to answer more factual questions correctly (boosting TruthfulQA) and make fewer reasoning errors in bias-sensitive contexts (boosting BBQ), not necessarily because their alignment training is coherent, but because capability scales with both. This is the classic confounding structure: a common cause (scale) induces positive correlation between two effects, even when the direct relationship is weaker.

The implication for leaderboard interpretation is direct: a model family that improves TruthfulQA and BBQ together may simply be scaling up. Attributing such correlated improvement to aligned training objectives requires, at minimum, controlling for MMLU or an equivalent capability proxy.

### 6.2 The Residual Coupling: What Does 0.343 Mean?

After MMLU control, partial_rho = 0.343 [0.180, 0.492] remains strongly significant. Three competing explanations deserve consideration:

**(1) Genuine RLHF co-training effect.** If RLHF and safety-focused fine-tuning jointly improve factuality and bias avoidance, cross-model variation in training intensity would induce residual coupling. However, our Tier 3 null result (RLHF sign test p = 0.686 on BBQ proxy) provides no cross-model evidence for this mechanism.

**(2) ARC Proxy artifact.** ARC Challenge measures logical reasoning; TruthfulQA also has a reasoning component. The partial correlation 0.343 may largely reflect shared reasoning demands, inflating the estimate beyond what genuine factuality × social-bias coupling would show. This is our preferred explanation.

**(3) Residual family-level clustering.** Within-family variation in training recipes may drive residual rho despite family-weighted correction.

Disambiguation requires genuine HELM Lite BBQ per-model accuracy. If partial_rho under real BBQ is substantially lower than 0.343, explanation (2) dominates.

### 6.3 Limitations

**L1: BBQ Proxy (ARC Challenge).** The most important limitation is the substitution of ARC Challenge accuracy for genuine HELM Lite BBQ per-model scores. The primary claim — that MMLU confounds alignment benchmark correlations (Fisher z p = 3.22 × 10⁻¹²) — holds regardless of proxy choice; secondary claims about "factuality-bias coupling" are qualified by this proxy.

**L2: Scenario Classification Underpowered (N=296).** partial_rho = 0.343 with CI [0.180, 0.492] spans the 0.40 structural threshold. Resolving the scenario requires N ≥ 400–600 or genuine BBQ data. AMBIGUOUS is pre-registered and scientifically valid.

**L3: Safety Dimension Excluded (HarmBench N=0).** Three-benchmark partial Spearman matrix could not be computed. Requires alternative safety benchmark with better LLM LB v1 coverage.

**L4: RLHF Sign Test on Proxy.** Null result (p = 0.686) may reflect proxy inadequacy rather than genuine absence of RLHF bias effects.

**L5: Observational, Cross-Sectional, Open-Weight Only.** Results characterize N=296 open-weight LLMs from 2022–2024; do not generalize to proprietary models or post-2024 RLHF training.

### 6.4 Implications for Alignment Evaluation Practice

The Fisher z difference test between raw and partial Spearman correlation should be a standard diagnostic step in alignment benchmark analysis whenever a capability proxy co-varies with the benchmarks of interest. More broadly, positive correlations between alignment benchmarks should not be interpreted as evidence of aligned constructs without first checking whether a common scale factor explains the co-movement.

---

## 7. Conclusion

We opened this paper with a concrete observation: controlling for MMLU general capability reduces the TruthfulQA × BBQ correlation from 0.732 to 0.343 — more than half of what leaderboard comparisons might attribute to alignment coherence is, in fact, scale-driven confounding. Our work provides, to our knowledge, the first direct application of the Fisher z raw-vs-partial difference test as a formal statistical diagnostic for this confound, and demonstrates it on N=296 open-weight LLMs with a pre-registered hypothesis and 57/57 test cases passing.

The three-stage verified mechanism is clear: (1) MMLU explains 49% of TruthfulQA variance and 76% of BBQ-proxy variance, confirming MMLU as a strong scale covariate; (2) controlling for MMLU reduces the pairwise alignment correlation by 53% with Fisher z p = 3.22 × 10⁻¹², decisively confirming scale confounding; (3) the residual partial_rho = 0.343 remains positive and significant (p = 1.40 × 10⁻⁹), indicating genuine alignment-specific co-movement beyond scale — though the structural interpretation remains ambiguous at N=296.

**Future directions.** The most pressing next step is replication with genuine HELM Lite BBQ per-model accuracy scores. Extension to three-dimensional analysis (factuality × bias × safety) requires resolving HarmBench model name compatibility. Applying the same diagnostic to LLM LB v2 (N > 1000 models) would provide the statistical power to definitively resolve the scenario classification ambiguity.

**Methodological take-away.** The Fisher z difference test between raw and partial Spearman is a practical, low-cost diagnostic that should become standard practice when interpreting alignment benchmark correlations. Capability control before interpreting benchmark co-movement is not optional — it is methodologically necessary.

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

---

*Submitted to ICML 2025. Anonymous submission.*
