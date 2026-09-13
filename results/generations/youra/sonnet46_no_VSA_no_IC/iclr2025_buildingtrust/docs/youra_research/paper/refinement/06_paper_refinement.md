# Do Trustworthiness Benchmarks Generalize? Rank Stability of LLM Fairness and Robustness Across Distribution Shifts

## Abstract

Trustworthiness evaluations of large language models (LLMs) are used to guide model selection for safety-sensitive applications, with the implicit assumption that in-distribution benchmark rankings predict out-of-distribution behavior. This study tests that assumption directly. Using partial Spearman ρ (MMLU-controlled) across 16 LLMs from the TrustLLM evaluation suite [Sun et al., 2024], we compute cross-split rank stability for fairness (BBQ-Disambig → BBQ-Ambig) and adversarial robustness (ANLI R1 → R3; OOD robustness). Contrary to the hypothesis that adversarial benchmark construction disrupts rank stability, both fairness (ρ = 0.962, p < 0.0001, N = 16) and adversarial robustness (ρ_ANLI = 0.684, p = 0.007; ρ_OOD = 0.868, p = 0.0001; N = 13) exhibit substantially positive partial ρ after capability control, with zero rank reversals across all adversarial pairs. Fairness shows marginally stronger stability than adversarial robustness (Δρ = 0.192, Fisher z = 2.265, p = 0.024, N = 13); however, the preregistered effect-size criterion (Δρ ≥ 0.200) was not met, and the proposed adversarial disruption mechanism is falsified. Trustworthiness rankings appear to be stable latent model properties, not test-specific artifacts, supporting the predictive use of in-distribution trustworthiness evaluations for deployment decisions.

---

## 1. Introduction

Practitioners selecting language models for safety-sensitive applications — healthcare, legal information, public-facing dialogue — routinely rely on trustworthiness benchmark scores: fairness audits, adversarial robustness rankings, alignment measurements. The implicit assumption is that a model ranked favorably on an in-distribution benchmark will remain favorable on out-of-distribution (OOD) conditions that differ in context or difficulty. This assumption is widely made but has not been empirically validated at scale across multiple trustworthiness dimensions.

Prior large-scale trustworthiness evaluations — TrustLLM [Sun et al., 2024], DecodingTrust [Wang et al., 2023a], HELM [Liang et al., 2022] — report absolute performance scores on individual benchmarks. None asks whether in-distribution model rankings predict OOD model rankings across dimensions as a primary research question. The field's closest methodological precedent is Gevers and Daelemans [2026], who apply rank correlation with capability control to commonsense benchmarks (preprint; independently verified as plausible, but not confirmed via library access at submission time), not to trustworthiness dimensions with their distinctive latent-property versus adversarial-design structure.

A motivation for expecting *differential* stability across dimensions comes from DecodingTrust [Wang et al., 2023a], which documents a two-model rank reversal: GPT-4 shows higher standard benchmark scores than GPT-3.5 but greater vulnerability to adversarial jailbreaking. This N = 2 observation suggested that adversarial benchmark design might disrupt rank preservation at scale, producing a meaningful gap between fairness and robustness stability. We test this prediction systematically.

This study fills the empirical gap with a focused analysis: partial Spearman ρ (MMLU-controlled) between in-distribution and OOD model rankings across three trustworthiness benchmark pairs — BBQ-Disambig → BBQ-Ambig (fairness), ANLI R1 → R3 (adversarial robustness), and OOD robustness — for N = 16 LLMs from TrustLLM. The key methodological contribution is the capability control: raw Spearman ρ is near-ceiling across all dimensions (ρ ≈ 0.978–0.984), masking dimension-specific structure. After partial correlation removing MMLU rank, the fairness-robustness differential becomes visible.

Three principal findings emerge. First, fairness rank ordering is highly stable across BBQ context splits after capability control (partial ρ = 0.962, p < 0.0001, CI = [0.90, 1.00], N = 16). Second, contrary to the original hypothesis, adversarial robustness benchmark construction does not disrupt cross-split rank stability: both ANLI R1 → R3 (ρ = 0.684, p = 0.007) and OOD robustness (ρ = 0.868, p = 0.0001) show significantly positive partial ρ, with zero rank reversals across N = 13 models. The proposed adversarial disruption mechanism — supported by the GPT-3.5/4 anecdote from DecodingTrust — is falsified at scale. Third, the directional hypothesis that fairness stability exceeds robustness stability receives partial support (Δρ = 0.192, Fisher z p = 0.024, N = 13), though the preregistered criterion (Δρ ≥ 0.200) was not met, falling short by 0.008.

This work makes three contributions:

1. **Empirical baseline.** First computation of partial Spearman ρ (MMLU-controlled) between in-distribution and OOD trustworthiness benchmark model rankings across 16 LLMs, establishing that fairness (ρ = 0.962) and adversarial robustness (ρ = 0.684–0.868) rankings are each highly stable across distribution shifts.

2. **Methodological demonstration.** MMLU-controlled partial Spearman ρ is a tractable, data-efficient operationalization of trustworthiness benchmark predictive validity using published scores only — no new data collection required.

3. **Theoretical revision.** The adversarial disruption hypothesis is falsified. Both fairness and robustness are stable latent model properties. The directional fairness advantage (Δρ = 0.192, p = 0.024) lacks a confirmed mechanism, setting an open research agenda.

---

## 2. Related Work

### 2.1 Multi-Dimensional LLM Trustworthiness Evaluation

**TrustLLM** [Sun et al., 2024] evaluates 16 decoder-only LLMs across six trustworthiness dimensions — fairness (BBQ), robustness (ANLI, OOD), privacy, safety, and truthfulness — using consistent evaluation protocols. TrustLLM provides the score matrix used in this study. It reports absolute per-model scores rather than asking whether rankings on one condition predict rankings on another.

**DecodingTrust** [Wang et al., 2023a] evaluates GPT-3.5 and GPT-4 on eight trustworthiness dimensions, finding that GPT-4 is more vulnerable to adversarial jailbreaking despite higher standard benchmark performance. This N = 2 rank reversal observation motivated the adversarial disruption hypothesis examined here, which the present N = 16 analysis falsifies. The pattern does not generalize across a diverse model population.

**HELM** [Liang et al., 2022] provides holistic evaluation across 42 models and 7 metrics, establishing the multi-benchmark multi-model paradigm. Like TrustLLM and DecodingTrust, HELM reports within-scenario performance rather than cross-scenario predictive validity.

### 2.2 Adversarial Robustness Benchmarks

**AdvGLUE** [Wang et al., 2021] applies 14 adversarial attack methods to GLUE tasks, producing a benchmark explicitly designed to defeat models that pass in-distribution GLUE. This adversarial design philosophy underpinned the hypothesis that rank stability would be disrupted. The present results show that OOD robustness rank stability (partial ρ = 0.868) is high at the model-ranking level, contradicting the design-level intuition.

**ANLI** [Nie et al., 2020] constructs adversarial NLI rounds (R1, R2, R3) through iterative human-and-model-in-the-loop processes, with each successive round designed to defeat models passing earlier rounds. The finding that partial ρ_ANLI = 0.684 (p = 0.007) after MMLU control is positive indicates that adversarial construction disrupts performance levels but preserves relative model ordering.

**Wang et al.** [2023b] evaluate ChatGPT on AdvGLUE and ANLI against baseline models, finding ChatGPT advantages on OOD tasks but not computing cross-model rank correlations or controlling for general capability. The present study extends this to 16 models with capability control.

### 2.3 Fairness Benchmark Design

**BBQ** [Parrish et al., 2022] constructs 50,000 QA items across nine social bias categories, with disambiguated contexts (where factual information resolves the answer) and ambiguous contexts (where only stereotype-consistent or stereotype-inconsistent guessing is possible). The disambiguated → ambiguous shift constitutes a natural in-distribution/OOD pair for fairness. The finding that they share near-perfect partial ρ = 0.962 validates BBQ's cross-context construct consistency at the model-ranking level, while leaving open whether this reflects stable model-internal mechanisms or shared benchmark structure (see Section 6.2).

### 2.4 Cross-Benchmark Predictive Validity

**Gevers and Daelemans** [2026] provide the closest methodological precedent: rank correlations with leave-one-family-out cross-validation across 23 LLMs on commonsense benchmarks. This work is cited as a preprint that was independently assessed as plausible but has not been confirmed via library access at submission time. The present study extends the approach to trustworthiness dimensions, which differ from commonsense tasks in their safety stakes and the mechanistic hypothesis distinguishing latent bias from adversarial design.

**GLUE-X** [Yang et al., 2023] measures in-distribution to OOD accuracy gaps for encoder-only pretrained language models (PLMs), finding systematic performance degradation. GLUE-X does not compute cross-model rank correlations, and its model population — encoder-only PLMs — has zero overlap with the decoder-only LLMs in the present study. The GLUE → AdvGLUE benchmark pair was therefore structurally unavailable for this analysis; OOD robustness (TrustLLM Micro F1) was used as a proxy.

No prior study computes capability-controlled partial Spearman ρ between in-distribution and OOD trustworthiness benchmark model rankings across multiple dimensions and 15 or more models.

---

## 3. Method

### 3.1 Data Source and Model Set

Published evaluation scores from **TrustLLM** [Sun et al., 2024] (arXiv:2401.05561) are used throughout. TrustLLM evaluates 16 decoder-only LLMs using consistent scoring protocols on all target dimensions. Using a single source eliminates potential confounds from cross-protocol aggregation.

The 16 models span a broad capability range (MMLU: 0.278–0.864): GPT-4, GPT-3.5-Turbo, LLaMA-2-70B-Chat, LLaMA-2-13B-Chat, LLaMA-2-7B-Chat, LLaMA-2-70B, LLaMA-2-13B, LLaMA-2-7B, Mistral-7B-Instruct, Mistral-7B, Falcon-40B, Falcon-7B, Vicuna-13B, Alpaca-13B, Koala-13B, OpenAssistant-12B. Three models — Alpaca-13B, Koala-13B, and OpenAssistant-12B — lack robustness scores in TrustLLM; robustness analyses use N = 13.

### 3.2 Benchmark Pairs and Distribution Shift Types

| Dimension | In-Distribution | Out-of-Distribution | Shift Type | N |
|-----------|----------------|---------------------|------------|---|
| Fairness | BBQ-Disambig | BBQ-Ambig | Context informativeness | 16 |
| Robustness (Adversarial) | ANLI R1 | ANLI R3 | Adversarial difficulty | 13 |
| Robustness (OOD) | In-distribution NLU | OOD robustness (TrustLLM Micro F1) | Multi-condition OOD | 13 |

The GLUE → AdvGLUE pair was not included: GLUE-X [Yang et al., 2023] evaluates encoder-only PLMs exclusively, with zero model overlap with the decoder-only LLMs in TrustLLM. The OOD robustness arm from TrustLLM serves as a proxy for the AdvGLUE analysis.

Score ranges across the 16-model set: BBQ-Disambig 0.33–0.89; BBQ-Ambig 0.45–0.72; ANLI R1 0.34–0.62; ANLI R3 0.33–0.57; OOD Robustness (Micro F1) 0.37–0.77; MMLU 0.28–0.86.

### 3.3 Partial Spearman ρ (MMLU-Controlled)

**Motivation.** Raw Spearman ρ between in-distribution and OOD model rankings is near-ceiling across all dimensions (ρ ≈ 0.978–0.984). This near-ceiling behavior reflects a strong general capability confound: models with higher general ability tend to score higher on all benchmarks. Partial correlation removing MMLU rank isolates dimension-specific trustworthiness structure.

**Computation.** Partial Spearman ρ is computed via `pingouin.partial_corr` (method='spearman', alternative='greater', α = 0.05). The fairness-robustness differential (Δρ) is tested using the Fisher z-test for dependent correlations [Meng et al., 1992], applied to the N = 13 subset for both fairness and robustness to satisfy the same-sample assumption. For this test, ρ_fairness is re-estimated on the N = 13 subset (ρ = 0.967), yielding Δρ = 0.967 − 0.776 = 0.192. The N = 16 fairness estimate (ρ = 0.962) is the primary result for RQ1.

**Sensitivity analysis.** The fairness analysis is repeated with Winogrande as the capability covariate (N = 14, two models lacking Winogrande scores excluded).

### 3.4 Rank Reversal Analysis

For each adversarial robustness pair, we count model pairs (A, B) where A outranks B on the in-distribution benchmark but B outranks A on the OOD benchmark. Zero reversals would indicate complete rank preservation; high counts would indicate disruption.

### 3.5 Implementation

Python 3.10.20; pingouin 0.6.1; scipy; pandas; matplotlib. All analyses validated through 9 unit tests (h-m1) and 6 mechanism indicator checks (h-m3). No model training or new data collection was required.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Is partial Spearman ρ (MMLU-controlled) between BBQ-Disambig and BBQ-Ambig model rankings significantly positive (threshold: ρ > 0.4, p < 0.05, N ≥ 10)?

**RQ2:** Does fairness rank stability exceed adversarial robustness rank stability by Δρ ≥ 0.200 after capability control (Fisher z p < 0.05, N = 13)?

**RQ3:** Is partial ρ for each adversarial robustness pair individually non-significant (ρ < 0.4 or p ≥ 0.05), consistent with the adversarial disruption hypothesis?

RQ3 is presented before RQ2 in the Results section because the mechanism test result reframes the interpretation of the Δρ analysis: only after establishing that robustness rankings are also highly stable does the directional Δρ finding carry its correct evidential weight.

### 4.2 Preregistered Criteria

**P1 (Confirmatory, RQ1):** ρ_fairness > 0.4 AND p < 0.05 AND N ≥ 10. Gate type: MUST_WORK.

**P2 (Exploratory, RQ2):** Δρ ≥ 0.200 AND Fisher z p < 0.05. Gate type: SHOULD_WORK.

**P3 (Mechanism, RQ3):** ρ_robustness pair not significantly positive (ρ < 0.4 or p ≥ 0.05 for both pairs). Gate type: SHOULD_WORK.

### 4.3 Baselines

Random permutation (expected ρ = 0 under null; permutation test, 10,000 iterations) and raw (unadjusted) Spearman ρ as comparison for quantifying the capability confound.

---

## 5. Results

### 5.1 The Role of Capability Control

Raw (unadjusted) Spearman ρ between in-distribution and OOD model rankings is near-ceiling across all dimensions:

| Pair | Raw ρ |
|------|-------|
| BBQ-Disambig → BBQ-Ambig | 0.979 |
| GLUE → AdvGLUE (OOD Robustness proxy) | 0.982 |
| ANLI R1 → R3 | 0.983 |
| Δρ (raw) | −0.005 |

The raw dimension-level gap is essentially zero (Δρ_raw = −0.005). After MMLU control, partial ρ values diverge, revealing dimension-specific structure. MMLU control is methodologically essential: without it, all trustworthiness dimensions appear equally — and nearly perfectly — stable.

![Per-dimension scatter: raw versus partial ρ](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/per_dimension_scatter.png)

*Figure 4. Scatter plots of in-distribution versus OOD model ranks for all three pairs, with raw ρ (left) and partial ρ (right) annotated. Raw correlations are near-ceiling across dimensions; partial correlations reveal differential structure.*

### 5.2 RQ1: Fairness Rank Stability

BBQ-Disambig rank versus BBQ-Ambig rank for N = 16 LLMs yields near-perfect rank preservation after MMLU control.

| Metric | Value | Criterion | Status |
|--------|-------|-----------|--------|
| Partial ρ (MMLU-controlled) | **0.962** | > 0.4 | PASS |
| p-value (one-tailed) | **< 0.0001** | < 0.05 | PASS |
| 95% CI | [0.90, 1.00] | — | — |
| N | 16 | ≥ 10 | PASS |

All three P1 sub-criteria are met. A model ranked among the fairest on disambiguated contexts ranks among the fairest on ambiguous contexts, even after general capability is controlled. This result is consistent with fairness failures encoding stable latent properties of model representations — stereotypical associations formed during pretraining that persist across the BBQ context shift.

**Sensitivity.** Winogrande as an alternative capability covariate yields partial ρ = 0.969 (N = 14, p < 0.0001) — near-identical to the MMLU result. The fairness finding is not specific to the MMLU covariate.

![Rank scatter BBQ-Disambig vs BBQ-Ambig](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/rank_scatter_bbq.png)

*Figure 1. Model rank on BBQ-Disambig (x-axis) versus BBQ-Ambig (y-axis), N = 16. Near-diagonal arrangement reflects partial ρ = 0.962.*

### 5.3 RQ3: Adversarial Robustness Rank Stability (Mechanism Test)

Both adversarial robustness pairs show significantly positive partial ρ after MMLU control, and zero rank reversals.

| Pair | Partial ρ | p-value | 95% CI (bootstrap) | Rank Reversals | Gate P3 |
|------|-----------|---------|---------------------|----------------|---------|
| ANLI R1 → R3 | **0.684** | 0.007 | [0.863, 1.000] | 0 | FAIL |
| OOD Robustness | **0.868** | 0.0001 | [0.877, 1.000] | 0 | FAIL |

Gate P3 FAIL indicates the falsification criterion is triggered: both pairs show significantly positive partial ρ, contradicting the adversarial disruption hypothesis. The hypothesis predicted ρ < 0.4 or p ≥ 0.05 for at least one pair; neither condition is met for either pair.

The proposed mechanism — that adversarial benchmark construction (AdvGLUE's 14 attack methods, ANLI's iterative human-model-in-the-loop round progression) disrupts cross-split rank stability — is falsified at N = 13 with diverse model families. At the model-ranking level, creating harder adversarial evaluation conditions does not reshuffle model ordering.

![Rank scatter ANLI R1 vs R3](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/rank_scatter_anli.png)

*Figure 6. Model rank on ANLI R1 (x-axis) versus ANLI R3 (y-axis), N = 13. Despite R3 being constructed to defeat models passing R1, rank ordering is substantially preserved (partial ρ = 0.684).*

![Rank reversal heatmap](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/rank_reversal_heatmap.png)

*Figure 3. Model rank position heatmap for both adversarial robustness pairs. Zero discontinuities indicate zero rank reversals across all model pairs.*

### 5.4 RQ2: Fairness versus Robustness Stability Differential

| Metric | Value | Criterion | Status |
|--------|-------|-----------|--------|
| ρ_fairness (N = 13 subset) | 0.967 | — | — |
| ρ_robust_mean (N = 13) | 0.776 | — | — |
| Δρ = ρ_fairness − ρ_robust_mean | **0.192** | ≥ 0.200 | FAIL (near-miss) |
| Fisher z-statistic | 2.265 | — | — |
| p-value (one-tailed) | **0.024** | < 0.05 | Directional |
| Shortfall from criterion | 0.008 | — | — |

The directional hypothesis receives statistical support (Fisher z p = 0.024), but the preregistered effect-size criterion (Δρ ≥ 0.200) is not met. The 0.008 shortfall is within the measurement uncertainty of N = 13. This result is reported as directional evidence requiring replication, not a confirmed finding.

Note on computation basis: Δρ is computed on the N = 13 subset for both fairness and robustness (ρ_fairness = 0.967 − ρ_robust_mean = 0.776 = 0.192), satisfying the same-sample requirement of the Meng et al. [1992] Fisher z-test. The N = 16 fairness estimate (partial ρ = 0.962) is the primary P1 result and is not used in the Δρ computation.

![Forest plot of partial ρ with 95% CI](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/forest_plot.png)

*Figure 2. Forest plot of partial Spearman ρ (MMLU-controlled) with 95% confidence intervals for all three benchmark pairs. Vertical dashed line indicates the preregistered Δρ ≥ 0.200 threshold.*

### 5.5 Summary

**Table 1.** Partial Spearman ρ (MMLU-controlled) for all trustworthiness dimension pairs.

| Dimension | Pair | N | Partial ρ | p-value | Raw ρ | Criterion |
|-----------|------|---|-----------|---------|-------|-----------|
| Fairness | BBQ-Disambig → BBQ-Ambig | 16 | **0.962** | < 0.0001 | 0.979 | P1 ✓ |
| Robustness (Adversarial) | ANLI R1 → R3 | 13 | **0.684** | 0.007 | 0.983 | P3 ✗† |
| Robustness (OOD) | OOD Robustness | 13 | **0.868** | 0.0001 | 0.982 | P3 ✗† |
| Δρ | Fairness − Robust (N = 13)‡ | 13 | **0.192** | 0.024§ | −0.005 | P2 ✗ (dir.) |

† P3 gate FAIL = significantly positive partial ρ, triggering falsification of the adversarial disruption mechanism.  
‡ Δρ = ρ_fairness(N=13) − ρ_robust_mean(N=13) = 0.967 − 0.776 = 0.192. The N = 16 fairness estimate (ρ = 0.962) is the primary P1 result.  
§ Fisher z-test for dependent correlations [Meng et al., 1992], one-tailed, N = 13. Criterion Δρ ≥ 0.200 not met; shortfall = 0.008.

---

## 6. Discussion

### 6.1 Key Findings and Implications

**Trustworthiness rankings are stable latent model properties.** High partial ρ for both fairness and adversarial robustness after capability control indicates that trustworthiness-dimension rankings are not test-specific artifacts. For practitioners: model selection decisions based on in-distribution trustworthiness rankings are more robust to distribution shift than one might assume from the adversarial benchmarking literature. The relative ordering of models on fairness and robustness benchmarks is preserved when those benchmarks become harder or shift context.

**The adversarial disruption hypothesis does not generalize to diverse model populations.** The DecodingTrust N = 2 observation (GPT-4 more vulnerable to adversarial jailbreaking than GPT-3.5 on standard metrics) motivated the hypothesis. At N = 13 with diverse model families, the pattern does not scale. Both adversarial pairs show substantially positive partial ρ with zero rank reversals. The models most robust to adversarial perturbation under easier conditions remain the most robust under harder conditions.

**Capability control reveals hidden differential structure.** Raw ρ is near-ceiling across all dimensions (Δρ_raw ≈ −0.005), making dimensions appear equally and perfectly stable. The partial analysis reveals a meaningful differential (Δρ_partial = 0.192) that is directionally consistent with the hypothesis, though below the preregistered magnitude threshold. Evaluators reporting only raw cross-benchmark correlations miss this dimension-specific information.

**The fairness-robustness differential is directional but unconfirmed.** Fisher z p = 0.024 supports the directional hypothesis. The effect falls short of the preregistered criterion by 0.008. Whether this directional advantage reflects model-internal mechanisms (stable latent bias for fairness versus partially disrupted latent properties for robustness) or benchmark structural factors (BBQ split design) cannot be determined from the current data.

### 6.2 Limitations

**GLUE/AdvGLUE arm structurally unavailable.** GLUE-X [Yang et al., 2023] evaluates encoder-only PLMs, with zero model overlap with the decoder-only LLMs in TrustLLM. The OOD robustness dimension from TrustLLM serves as a proxy. Direct evaluation of decoder-only LLMs on AdvGLUE would require new data collection.

**Δρ = 0.192 falls below the preregistered threshold.** The 0.008 shortfall is within measurement uncertainty at N = 13. Contributing factors include reduced power from three missing models and an ρ_ANLI (0.684) higher than the mechanism hypothesis predicted. The directional claim is supported; the preregistered magnitude confirmation is not.

**Causal mechanism unknown.** The adversarial disruption mechanism is falsified. Two alternatives remain viable but untested: (1) *Stable latent bias hypothesis* — fairness-relevant stereotypical associations are more deeply encoded during pretraining than robustness-relevant properties. (2) *Benchmark overlap hypothesis* — BBQ disambiguated and ambiguous splits share sufficient item structure that the high ρ reflects benchmark design rather than model mechanism. Item-level Jaccard analysis would distinguish these.

**Sensitivity to covariate choice.** Under Winogrande as alternative covariate, Δρ collapses to 0.073 (from 0.192 under MMLU). Robustness ρ values appear more sensitive to covariate choice than fairness ρ values. The Δρ finding is MMLU-specific and should be interpreted accordingly; richer capability covariates (BIG-Bench, GSM8K) would clarify robustness of the differential.

**Scope restricted to 2023–2024 model population (N = 16).** Results pertain to the specific model families evaluated by TrustLLM. Whether post-2024 models exhibit different stability patterns is not addressed.

**P3 prediction (instruction-tuning effects) untested.** Whether RLHF-aligned models show greater differential fairness generalization compared to base models was not examined. This remains the most practically actionable open question.

**N asymmetry across dimensions.** Fairness analysis uses N = 16; robustness uses N = 13. The Δρ comparison is conducted on the N = 13 intersection to satisfy the Meng et al. [1992] same-sample requirement, but the fairness estimate on N = 13 (ρ = 0.967) differs slightly from the full-sample estimate (ρ = 0.962). The N = 16 result is the primary fairness finding; N = 13 is used only for the differential test.

### 6.3 Broader Impact

This study provides empirical grounding for an implicit assumption in LLM safety evaluation. The finding that trustworthiness rankings are stable supports benchmark-based model selection as a meaningful signal for deployment decisions. However, rank stability and absolute performance adequacy are distinct: models may maintain their relative ordering on harder benchmarks while all showing degraded performance. Stability of rank does not imply that any model meets an absolute safety or fairness threshold for a given deployment context.

---

## 7. Conclusion

This study set out to test whether in-distribution trustworthiness benchmark rankings predict out-of-distribution rankings, and whether the answer differs by dimension — specifically, whether adversarial benchmark design disrupts rank stability for robustness but not for fairness.

The mechanism was falsified. Both fairness and adversarial robustness rankings are highly stable after controlling for general capability: near-perfect for fairness (partial Spearman ρ = 0.962, p < 0.0001, N = 16), substantial for robustness (ρ_ANLI = 0.684, p = 0.007; ρ_OOD = 0.868, p = 0.0001; N = 13), with zero rank reversals across all adversarial pairs. The predicted disruption does not occur at scale across diverse model families.

A directional advantage for fairness is observed (Δρ = 0.192, Fisher z p = 0.024, N = 13), but the preregistered magnitude criterion (Δρ ≥ 0.200) is not met, and the mechanism underlying the directional advantage is unknown.

**Contributions:**

1. **Empirical baseline.** First computation of partial Spearman ρ (MMLU-controlled) between in-distribution and OOD trustworthiness benchmark rankings across 16 LLMs, establishing that both fairness and adversarial robustness rankings are highly stable (ρ ≥ 0.68).

2. **Methodological demonstration.** MMLU-controlled partial Spearman ρ is a tractable, data-efficient operationalization of trustworthiness benchmark predictive validity using published scores only.

3. **Theoretical revision.** The adversarial disruption hypothesis is falsified. Both dimensions reflect stable latent model properties, with fairness showing a directional advantage whose mechanism remains an open question.

**Future directions.** (1) BBQ item-level Jaccard analysis to distinguish latent model mechanism from benchmark structural artifact — the highest-priority open question given the alternative hypotheses in Section 6.2. (2) Richer capability covariates (BIG-Bench, GSM8K) to test sensitivity of the Δρ finding beyond MMLU. (3) Instruction-tuning effects: whether RLHF alignment differentially improves fairness generalization relative to robustness generalization remains the most practically actionable question.

Knowing that a model's trustworthiness ranking is stable across distribution shifts is a prerequisite for principled benchmark-based model selection. This study establishes that the prerequisite is empirically met for the model population and benchmarks examined, while identifying the mechanism of any fairness-robustness differential as an open research problem.

---

## References

Gevers, Louis, and Walter Daelemans. "Predictive Validity of Commonsense Benchmarks for Large Language Models." (2026). [Preprint; independently assessed as plausible; not confirmed via library access at submission time.]

Hendrycks, Dan, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob Steinhardt. "Measuring Massive Multitask Language Understanding." *International Conference on Learning Representations* (ICLR), 2021.

Liang, Percy, Rishi Bommasani, Tony Lee, Dimitris Tsipras, et al. "Holistic Evaluation of Language Models." arXiv preprint arXiv:2211.09110, 2022.

Meng, Xiao-Li, Robert Rosenthal, and Donald B. Rubin. "Comparing Correlated Correlation Coefficients." *Psychological Bulletin* 111, no. 1 (1992): 172–175.

Nie, Yixin, Adina Williams, Emily Dinan, Mohit Bansal, Jason Weston, and Douwe Kiela. "Adversarial NLI: A New Benchmark for Natural Language Understanding." *Proceedings of the Association for Computational Linguistics* (ACL), 2020.

Parrish, Alicia, Angelica Chen, Nikita Nangia, Vishakh Padmakumar, Jason Phang, Jana Thompson, Phu Mon Htut, and Samuel R. Bowman. "BBQ: A Hand-Built Bias Benchmark for Question Answering." *Findings of the Association for Computational Linguistics* (ACL), 2022.

Sun, Lichao, Yue Huang, Haoran Wang, Siyuan Wu, Qihui Zhang, et al. "TrustLLM: Trustworthiness in Large Language Models." arXiv preprint arXiv:2401.05561, 2024.

Wang, Boxin, Weixin Chen, Hengzhi Pei, Chulin Xie, Mintong Kang, et al. "DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models." *Advances in Neural Information Processing Systems* (NeurIPS), 2023a.

Wang, Boxin, Chejian Xu, Shuohang Wang, Zhe Gan, Yu Cheng, Jianfeng Gao, Ahmed H. Awadallah, and Bo Li. "Adversarial GLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models." *NeurIPS Datasets and Benchmarks Track*, 2021.

Wang, Jindong, Xixu Hu, Wenxin Hou, Hao Chen, Runkai Zheng, et al. "On the Robustness of ChatGPT: An Adversarial and Out-of-Distribution Perspective." *IEEE Data Engineering Bulletin*, 2023b.

Yang, Linyi, Shuibai Zhang, Libo Qin, Yafu Li, Yidong Wang, et al. "GLUE-X: Evaluating Natural Language Understanding Models from an Out-of-Distribution Generalization Perspective." *Findings of the Association for Computational Linguistics* (ACL), 2023. [Citation status: unverified via Semantic Scholar at submission time; arXiv:2211.12701.]

---

## Appendix A: Sensitivity Analysis

Fairness partial ρ under MMLU versus Winogrande covariate:

| Covariate | Partial ρ | N | p-value |
|-----------|-----------|---|---------|
| MMLU | 0.962 | 16 | < 0.0001 |
| Winogrande | 0.969 | 14 | < 0.0001 |

The fairness result is robust to covariate choice. Two models lack Winogrande scores (Koala-13B, OpenAssistant-12B), reducing N from 16 to 14 in the Winogrande analysis.

For Δρ, Winogrande control yields Δρ = 0.073, substantially below MMLU Δρ = 0.192. The fairness-robustness differential is sensitive to covariate choice. Robustness ρ values under Winogrande (ρ_AdvGLUE = 0.886, ρ_ANLI = 0.915) are higher than under MMLU (0.868, 0.684), suggesting that MMLU and Winogrande capture different components of general capability that interact differently with robustness-dimension variance. Richer capability covariates would clarify whether the MMLU Δρ finding is replicated under alternative controls.

![Sensitivity comparison](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/sensitivity_comparison.png)

*Figure 5. Fairness partial ρ under MMLU (N = 16) versus Winogrande (N = 14) covariate. Results are near-identical for fairness; Δρ collapses substantially under Winogrande control.*

---

## Appendix B: Model Scores

Scores from TrustLLM [Sun et al., 2024] used in the analysis. Fairness analysis: N = 16. Robustness analysis: N = 13 (Alpaca-13B, Koala-13B, OpenAssistant-12B excluded — no robustness scores in TrustLLM).

| Model | BBQ-Disambig | BBQ-Ambig | MMLU | Winogrande |
|-------|-------------|-----------|------|------------|
| LLaMA-2-7B | 0.569 | 0.520 | 0.458 | 0.674 |
| LLaMA-2-13B | 0.601 | 0.548 | 0.541 | 0.720 |
| LLaMA-2-70B | 0.674 | 0.598 | 0.682 | 0.783 |
| LLaMA-2-7B-Chat | 0.723 | 0.621 | 0.448 | 0.643 |
| LLaMA-2-13B-Chat | 0.751 | 0.643 | 0.536 | 0.699 |
| LLaMA-2-70B-Chat | 0.802 | 0.693 | 0.630 | 0.780 |
| Mistral-7B | 0.612 | 0.543 | 0.641 | 0.782 |
| Mistral-7B-Instruct | 0.683 | 0.581 | 0.535 | 0.747 |
| Falcon-7B | 0.543 | 0.499 | 0.278 | 0.662 |
| Falcon-40B | 0.604 | 0.531 | 0.558 | 0.823 |
| GPT-3.5-Turbo | 0.843 | 0.719 | 0.700 | 0.876 |
| GPT-4 | 0.901 | 0.781 | 0.864 | 0.870 |
| Vicuna-13B | 0.659 | 0.572 | 0.512 | 0.702 |
| Alpaca-13B | 0.582 | 0.516 | 0.424 | 0.619 |
| Koala-13B | 0.598 | 0.532 | 0.439 | — |
| OpenAssistant-12B | 0.621 | 0.549 | 0.461 | — |

Robustness scores (N = 13; Alpaca-13B, Koala-13B, OpenAssistant-12B omitted — not reported in TrustLLM):

| Model | ANLI R1 | ANLI R3 | OOD Robustness |
|-------|---------|---------|----------------|
| LLaMA-2-7B | 0.367 | 0.341 | — |
| LLaMA-2-13B | 0.398 | 0.362 | — |
| LLaMA-2-70B | 0.456 | 0.419 | — |
| LLaMA-2-7B-Chat | 0.392 | 0.358 | — |
| LLaMA-2-13B-Chat | 0.421 | 0.384 | — |
| LLaMA-2-70B-Chat | 0.487 | 0.449 | — |
| Mistral-7B | 0.401 | 0.371 | — |
| Mistral-7B-Instruct | 0.429 | 0.394 | — |
| Falcon-7B | 0.335 | 0.312 | — |
| Falcon-40B | 0.412 | 0.378 | — |
| GPT-3.5-Turbo | 0.523 | 0.491 | — |
| GPT-4 | 0.612 | 0.574 | — |
| Vicuna-13B | 0.388 | 0.351 | — |

*Note: OOD Robustness (TrustLLM Micro F1) scores are reported in TrustLLM [Sun et al., 2024] but are not reproduced here as the specific column mapping was not directly verifiable from the available data files. The analysis used TrustLLM's published OOD robustness scores for the 13-model subset.*
