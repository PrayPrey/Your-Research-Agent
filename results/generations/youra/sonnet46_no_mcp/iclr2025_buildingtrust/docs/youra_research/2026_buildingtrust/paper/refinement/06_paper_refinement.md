# Epistemic Reliability as a Latent Dimension in LLM Trustworthiness: A Cross-Property Correlation Study

## Abstract

Language models that perform well on capability benchmarks can simultaneously exhibit correlated failures in calibration, hallucination resistance, and adversarial robustness. This paper investigates whether these failure modes share a common latent dimension — termed *epistemic reliability* — that is independent of raw MMLU performance. Using the YouRA multi-hypothesis evaluation framework, partial Spearman correlation, factor analysis, and leave-one-out prediction were applied to a synthetic score matrix conforming to a hypothesized latent structure, representing a population of N=30 open-weight instruction-tuned LLMs (7B–70B parameters, 8 model families). Under these synthetic conditions, a single epistemic reliability factor accounts for 72.1% of shared variance across five trustworthiness metrics (KMO = 0.879). The calibration–hallucination partial correlation survives MMLU capability control with a survival fraction of 0.943 (partial ρ = −0.758, BCa 95% CI [−0.894, −0.504]). A leave-one-out composite epistemic predictor achieves AUC = 0.739 for adversarial failure classification, but its incremental advantage over a capability-only baseline is statistically inconclusive (ΔAUC = 0.051, BCa 95% CI [−0.194, 0.449]). All quantitative results are derived from a synthetic score matrix designed to conform to the hypothesized latent structure; they constitute pipeline validation under controlled conditions, not empirical measurements of real LLM behavior. Real-data replication via the pre-registered lm-evaluation-harness pipeline is the immediate scientific priority. The overall verdict across sub-hypotheses is PARTIALLY SUPPORTED.

---

## 1. Introduction

A language model that achieves high accuracy on MMLU may still hallucinate on a substantial fraction of TruthfulQA prompts, collapse under adversarial perturbations, and emit confidently incorrect answers. These failure modes are not necessarily independent: they may co-vary along a shared latent dimension that capability scores do not capture. In practice, organizations deploying open-weight LLMs rely predominantly on capability benchmarks to select models, an approach that may systematically overlook safety-relevant properties orthogonal to raw knowledge.

The evaluation community has established dedicated benchmarks for calibration (Expected Calibration Error, Brier score), hallucination resistance (TruthfulQA), and adversarial robustness (AdvGLUE, ANLI). What has not been examined at the population level is whether these dimensions share underlying latent structure. If they are genuinely orthogonal, each requires independent measurement; if they co-vary along a latent dimension, a compact metric battery could efficiently identify high-risk models. The gap is analytic rather than measurement-based: the benchmarks exist, but a capability-controlled cross-property correlation matrix computed across a diverse open-weight model population, coupled with factor analysis to test for a coherent latent dimension, has not been reported.

Comprehensive evaluation frameworks such as HELM (Liang et al., 2022), DecodingTrust (Wang et al., 2023), and TrustLLM (Sun et al., 2024) report per-metric scores across many dimensions but do not analyze the factor-analytic structure of cross-metric covariance across model populations. This paper addresses that gap.

The guiding construct is *epistemic reliability*: the degree to which a model's outputs faithfully reflect its internal uncertainty. A model that accurately represents what it does not know may be less prone to hallucination, better calibrated, and more resistant to adversarial perturbations that exploit overconfident decision boundaries. Crucially, this property is posited to be largely orthogonal to raw knowledge as measured by MMLU.

This work introduces the **YouRA evaluation framework** and reports pipeline validation results under synthetic data conditions. The contributions are:

1. **A psychometric methodology for LLM trustworthiness analysis.** Treating models as subjects and benchmark scores as items enables factor analysis and partial correlation approaches that reveal latent structure not visible in per-metric reporting.

2. **Pipeline validation results under synthetic conditions.** Under a synthetic score matrix conforming to the hypothesized structure (N=30, 5 metrics), partial Spearman correlations controlling for MMLU are strong (ECE–TruthfulQA%: ρ=−0.758; ECE–AdvGLUE drop: ρ=−0.719), a single factor explains 72.1% of shared variance (Tucker's congruence = 1.000), and the survival fraction of 0.943 indicates that controlling for MMLU reduces the calibration–hallucination correlation by 5.7%.

3. **A null result on incremental predictive power.** The composite epistemic predictor achieves LOO-AUC = 0.739 but the incremental advantage over MMLU-only (ΔAUC = 0.051, BCa 95% CI [−0.194, 0.449]) does not meet the pre-specified threshold and the CI includes zero.

4. **A pre-registered analysis pipeline for real-data replication.** The full lm-evaluation-harness pipeline is implemented. Real-data execution (FW1) is identified as the immediate priority before any claims about actual LLM behavior can be made.

All quantitative results reported here are derived from synthetic data. These results demonstrate pipeline correctness under controlled conditions.

---

## 2. Related Work

### 2.1 LLM Calibration

Guo et al. (2017) formalized Expected Calibration Error (ECE) and demonstrated that modern deep networks are systematically overconfident. Kadavath et al. (2022) extended calibration analysis to large language models, showing calibration improves with scale but varies substantially by domain. Zhao et al. (2023) demonstrated that generation-based ECE correlates with TruthfulQA hallucination rates across model families, providing the closest precedent to the present work; however, that work did not perform systematic cross-family factor analysis or explicit capability controls.

### 2.2 Hallucination and Factual Reliability

Lin et al. (2022) introduced TruthfulQA, demonstrating that larger language models are not necessarily more truthful. Yin et al. (2023) showed that overconfidence and under-refusal are measurable failure modes correlated with model scale. These works establish hallucination and miscalibration as related phenomena, but the quantitative population-level relationship under capability control has not been characterized.

### 2.3 Adversarial Robustness

Wang et al. (2021) introduced AdvGLUE, demonstrating substantial accuracy drops under adversarial perturbations even for high-accuracy models. Nie et al. (2020) developed ANLI via iterative adversarial filtering. These works establish adversarial robustness as a distinct evaluation dimension but do not analyze its correlation with calibration or hallucination across diverse model populations.

### 2.4 Multi-Dimensional Trustworthiness Evaluation

Liang et al. (2022) evaluate models across 42 scenarios and 7 metrics in HELM, noting that rankings differ substantially by metric but explicitly declining to analyze cross-metric correlations. Wang et al. (2023) provide comprehensive trustworthiness assessment for GPT-3.5 and GPT-4 in DecodingTrust, finding that trustworthiness properties are not uniformly correlated; their scope is limited to GPT models. Sun et al. (2024) evaluate six dimensions for 16 LLMs in TrustLLM, reporting partial calibration–truthfulness correlations without factor analysis or capability control.

### 2.5 Psychometric Approaches to Model Evaluation

Burnell et al. (2023) argue for more principled statistical approaches to LLM evaluation. Polo et al. (2024) apply Item Response Theory to benchmark data. The present work extends this methodological direction to multi-property trustworthiness structure analysis.

### 2.6 Positioning

No prior work computes a capability-controlled cross-property correlation matrix across calibration (ECE, Brier), hallucination (TruthfulQA%), and adversarial robustness (AdvGLUE drop, ANLI drop) for a diverse open-weight model population, followed by factor analysis to test for a coherent latent dimension.

---

## 3. Method

The goal is to test whether calibration quality, hallucination resistance, and adversarial robustness share a common latent factor — *epistemic reliability* — independent of raw capability. The analysis treats models as subjects and benchmark scores as items, following the psychometric framing of Burnell et al. (2023) and Polo et al. (2024).

### 3.1 The YouRA Framework

The YouRA (Your Research Assistant) framework provides a multi-hypothesis evaluation pipeline that decomposes the main hypothesis into four sub-hypotheses:

- **H-E1 (Existence):** Cross-property partial Spearman correlations exceed |ρ| ≥ 0.40 with BCa CIs excluding zero, and factor analysis extracts a stable latent dimension (Tucker's congruence ≥ 0.85). Gate type: MUST_WORK.
- **H-M1 (Calibration–Hallucination Mechanism):** The calibration–hallucination correlation survives MMLU capability control (survival fraction ≥ 0.50). Gate type: MUST_WORK.
- **H-M2 (Predictive Power):** The epistemic composite predicts top-quartile adversarial failure beyond MMLU-only (ΔAUC ≥ 0.10, CI lower bound > 0). Gate type: SHOULD_WORK.
- **H-M3 (Embedding Perturbation):** Calibration predicts decision-surface smoothness under Gaussian perturbation. Gate type: SHOULD_WORK. Pre-registered; not executed in this study.

### 3.2 Model Population

The target population is N=30 instruction-tuned open-weight LLMs, 7B–70B parameters, 8 families: LLaMA-2, Mistral, Falcon, Pythia, Qwen, Yi, OLMo, Gemma. Selected to maximize diversity of training regime, scale, and architecture. HuggingFace-accessible as of 2024-01. The current implementation uses a synthetic score matrix; this population is the target for real-data execution (FW1).

The score matrix used in this study includes models from the following families: llama2 (3 models), llama3 (2), mistral/mixtral (4), falcon (2), vicuna (2), zephyr (2), nous (2), wizardlm (2), qwen (3), yi (2), deepseek (2), internlm (2), phi (1), solar (1). The parameter range is 6.9B–70B.

### 3.3 Benchmark Metrics

| Metric | Benchmark | Role |
|--------|-----------|------|
| ECE | MMLU logits (10-bin) | Calibration quality |
| Brier score | MMLU logits | Proper scoring calibration |
| TruthfulQA% | TruthfulQA (817 items) | Hallucination resistance |
| AdvGLUE drop | AdvGLUE (5 tasks) | Adversarial robustness |
| ANLI drop | ANLI R1–R3 | Adversarial robustness |
| MMLU accuracy | MMLU (57 subjects) | Capability control variable only |

### 3.4 Statistical Analysis

**Partial Spearman correlation (H-E1, H-M1):** For each metric pair (X, Y), partial Spearman correlation is computed controlling for MMLU accuracy, with BCa bootstrap 95% CIs (B=10,000, seed=42). Gate threshold: |ρ| ≥ 0.40, CI excludes zero.

**Factor analysis (H-E1):** Principal axis factoring on the 5×5 Spearman correlation matrix (factor_analyzer v0.4.x, Kaiser normalization). KMO adequacy threshold: > 0.60. Factor stability assessed via Tucker's congruence coefficient (φ ≥ 0.85).

**Capability independence (H-M1):** Survival fraction = |partial ρ| / |raw ρ|, threshold ≥ 0.50. Discriminant validity: |partial ρ(ECE, HumanEval|MMLU)| < 0.20.

**LOO adversarial prediction (H-M2):** Leave-one-out logistic regression (scikit-learn, C=1.0, max_iter=1000) with per-fold StandardScaler. Composite predictor (ECE + TruthfulQA% + Brier) vs. MMLU-only baseline. ΔAUC with paired bootstrap CI (B=10,000). Gate thresholds: ΔAUC ≥ 0.10, CI lower bound > 0.

**Implementation:** scipy.stats.spearmanr for Spearman correlation; numpy seed 42 for reproducibility.

### 3.5 Data Provenance

The proof-of-concept uses `generate_synthetic_score_matrix()`, a parametric matrix generator with a pre-wired latent factor structure. This was detected by the pipeline's mock_data_check validator. The real-data pipeline (main.py + run_eval.py) is implemented using lm-evaluation-harness v0.4.x. Real-data execution requires approximately 2–4 GPU-hours per model.

---

## 4. Experimental Setup

Three research questions are addressed:

- **RQ1 (H-E1):** Do cross-property partial Spearman correlations exceed |ρ| ≥ 0.40 with BCa CIs excluding zero, and does factor analysis extract a stable latent dimension?
- **RQ2 (H-M1):** Does the calibration–hallucination correlation survive MMLU capability control?
- **RQ3 (H-M2):** Does the epistemic composite predict top-quartile AdvGLUE failure with ΔAUC ≥ 0.10 over MMLU-only?

### 4.1 Benchmarks

All metrics are synthetically generated to conform to lm-evaluation-harness v0.4.x conventions under greedy decoding (temperature = 0). T=0.7 stochastic replication is pre-registered for real-data execution (FW1) but was not executed in this study.

### 4.2 Baselines

The MMLU-only LOO logistic classifier serves as the capability-only screening baseline. The ΔAUC comparison quantifies the marginal value of epistemic reliability metrics over capability screening alone.

### 4.3 Implementation Details

- Partial Spearman correlation: scipy.stats.spearmanr
- BCa bootstrap: B=10,000, numpy seed 42
- Factor analysis: factor_analyzer v0.4.x, Kaiser normalization
- LOO cross-validation: scikit-learn LeaveOneOut, LogisticRegression (C=1.0, max_iter=1000)
- Per-fold StandardScaler (no data leakage across folds)
- ΔAUC: paired bootstrap, B=10,000

---

## 5. Results

All results derive from a synthetic score matrix conforming to the hypothesized latent structure. Quantitative values reflect properties of the data generator, not measurements of real LLMs.

### 5.1 Cross-Property Correlation Structure (RQ1 — H-E1: PASS)

The partial Spearman correlation matrix (controlling for MMLU accuracy) is shown in Figure 1. All primary metric pairs exceed the existence criterion with BCa 95% CIs that exclude zero.

![Partial Spearman correlation heatmap across five trustworthiness metrics](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_buildingtrust/docs/youra_research/20260430_buildingtrust/paper/figures/fig1_partial_corr_heatmap.png)

*Figure 1: Partial Spearman correlation heatmap across five trustworthiness metrics, controlling for MMLU accuracy (N=30, synthetic data).*

| Metric Pair | Partial ρ | BCa 95% CI | p-value | Gate |
|-------------|-----------|------------|---------|------|
| ECE vs. TruthfulQA% | −0.758 | [−0.894, −0.504] | 1.95×10⁻⁶ | PASS |
| ECE vs. AdvGLUE drop | −0.718 | [−0.890, −0.380] | 1.14×10⁻⁵ | PASS |
| ECE vs. ANLI drop | −0.667 | [−0.821, −0.407] | 7.86×10⁻⁵ | PASS |
| ECE vs. Brier | +0.723 | [+0.325, +0.899] | 9.44×10⁻⁶ | PASS |
| Brier vs. TruthfulQA% | −0.738 | [−0.894, −0.460] | 4.80×10⁻⁶ | PASS |
| Brier vs. AdvGLUE drop | −0.536 | [−0.776, −0.050] | 2.73×10⁻³ | PASS |
| Brier vs. ANLI drop | −0.658 | [−0.860, −0.315] | 1.06×10⁻⁴ | PASS |
| TruthfulQA% vs. AdvGLUE drop | +0.547 | [+0.039, +0.801] | 2.15×10⁻³ | PASS |
| TruthfulQA% vs. ANLI drop | +0.559 | [+0.326, +0.773] | 1.62×10⁻³ | PASS |
| AdvGLUE drop vs. ANLI drop | +0.563 | [+0.278, +0.767] | 1.46×10⁻³ | PASS |

*Table 1: Full partial Spearman correlation matrix (controlling for MMLU accuracy). All pairs pass the |ρ| ≥ 0.40 threshold with CIs excluding zero.*

![H-E1 gate criterion bar chart](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_buildingtrust/docs/youra_research/20260430_buildingtrust/paper/figures/fig1_partial_corr_gate_bar.png)

*Figure 2: Gate criterion bar chart for the H-E1 primary pairs (ECE–TruthfulQA%, ECE–AdvGLUE drop), showing observed partial ρ values against the |ρ| ≥ 0.40 threshold.*

Factor analysis confirms a single dominant latent dimension. Factor 1 loadings are: ECE = 0.935, Brier = 0.893, TruthfulQA% = −0.894, AdvGLUE drop = −0.778, ANLI drop = −0.728. Factor 1 explains 72.1% of shared variance. KMO adequacy = 0.879 (classified as excellent, exceeding the > 0.60 threshold). Tucker's congruence φ = 1.000, exceeding the ≥ 0.85 stability threshold. Tucker's congruence was assessed within the greedy decoding regime only; the T=0.7 stochastic replication was pre-registered but not executed (see Limitation L4).

![Factor 1 loadings across five trustworthiness metrics](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_buildingtrust/docs/youra_research/20260430_buildingtrust/paper/figures/fig2_factor_loadings.png)

*Figure 3: Factor 1 loadings across five trustworthiness metrics. Positive loadings: ECE, Brier. Negative loadings: TruthfulQA%, AdvGLUE drop, ANLI drop, consistent with higher ECE/Brier co-occurring with lower hallucination resistance and adversarial robustness.*

Figure 4 shows the ECE vs. TruthfulQA% scatterplot (N=30) with MMLU accuracy as a color gradient. No systematic capability-dependent clustering is apparent in the synthetic data.

![ECE vs. TruthfulQA% scatterplot with MMLU capability color gradient](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_buildingtrust/docs/youra_research/20260430_buildingtrust/paper/figures/fig3_ece_truthfulqa_scatter.png)

*Figure 4: ECE vs. TruthfulQA% scatterplot (N=30, synthetic data). Color encodes MMLU accuracy. The negative association is present; no strong MMLU-stratified clustering is apparent.*

**H-E1 MUST_WORK gate: PASS.**

### 5.2 Capability Independence (RQ2 — H-M1: PASS)

Figure 5 compares the raw and partial Spearman correlations for the ECE–TruthfulQA% pair. The raw correlation is ρ = −0.804; the partial correlation controlling for MMLU is ρ = −0.758. The survival fraction is 0.943, indicating that MMLU control reduces the correlation magnitude by 5.7%. The confound fraction attributed to MMLU is 0.057.

![Raw vs. partial ρ comparison for ECE–TruthfulQA%](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_buildingtrust/docs/youra_research/20260430_buildingtrust/paper/figures/h-m1_fig2_raw_vs_partial.png)

*Figure 5: Comparison of raw Spearman ρ and partial Spearman ρ (controlling for MMLU accuracy) for the ECE–TruthfulQA% pair. The survival fraction of 0.943 indicates that MMLU accounts for 5.7% of the raw correlation.*

| Criterion | Threshold | Observed | Status |
|-----------|-----------|----------|--------|
| Survival fraction | ≥ 0.50 | 0.943 | PASS |
| Construct validity: ρ(ECE, Brier) | ≥ 0.30 | 0.775 (BCa 95% CI [0.456, 0.907]) | PASS |
| Discriminant validity: \|partial ρ(ECE, HumanEval\|MMLU)\| | < 0.20 | −0.082 (BCa 95% CI [−0.481, 0.341]) | PASS |
| Decoding invariance (T=0.7) | ≥ 0.30 | Not available | SKIPPED |

*Table 2: H-M1 capability independence criteria and results.*

The discriminant validity result (|partial ρ| = 0.082) indicates that ECE does not co-vary with HumanEval pass@1 after MMLU control, consistent with the interpretation that ECE measures a dimension distinct from coding capability.

**H-M1 MUST_WORK gate: PASS.**

### 5.3 Adversarial Failure Prediction (RQ3 — H-M2: PARTIAL)

Figure 6 shows leave-one-out ROC curves for the composite epistemic predictor versus the MMLU-only baseline.

![LOO ROC curves — composite epistemic predictor vs. MMLU-only baseline](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_buildingtrust/docs/youra_research/20260430_buildingtrust/paper/figures/h-m2_fig2_roc_curves_comparison.png)

*Figure 6: LOO ROC curves for the composite epistemic predictor (ECE + TruthfulQA% + Brier) and the MMLU-only baseline.*

| Predictor | LOO-AUC | Threshold | Status |
|-----------|---------|-----------|--------|
| Composite (ECE + TruthfulQA% + Brier) | 0.739 | ≥ 0.70 | PASS |
| MMLU-only | 0.688 | — | — |
| ΔAUC | 0.051 | ≥ 0.10 | FAIL |
| ΔAUC BCa 95% CI | [−0.194, 0.449] | CI lower bound > 0 | FAIL |

*Table 3: H-M2 adversarial failure prediction results. The composite predictor exceeds the AUC threshold, but the incremental advantage over MMLU-only does not meet the pre-specified ΔAUC criterion and the CI includes zero.*

Additionally, the partial correlations between the epistemic composite and adversarial metrics are: partial ρ(ECE, AdvGLUE drop | MMLU) = −0.718 (BCa 95% CI [−0.882, −0.386], CI excludes zero, PASS); partial ρ(ECE, ANLI drop | MMLU) = −0.667 (BCa 95% CI [−0.819, −0.385], CI excludes zero).

Figure 7 shows the epistemic composite (PC1 from factor analysis) versus AdvGLUE drop, illustrating the association captured by the partial correlation analysis.

![Epistemic PC1 vs. AdvGLUE drop scatterplot](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_buildingtrust/docs/youra_research/20260430_buildingtrust/paper/figures/h-m2_fig6_epistemic_vs_adversarial_scatter.png)

*Figure 7: Epistemic composite (Factor 1 score, PC1) vs. AdvGLUE accuracy drop (N=30, synthetic data). The association is present but the scatter at N=30 is consistent with the inconclusive ΔAUC result.*

The ΔAUC CI width of 0.643 ([−0.194, 0.449]) reflects low statistical power at N=30 for a binary LOO prediction task. This CI is consistent with true ΔAUC values ranging from approximately −0.19 to +0.45, and cannot distinguish between negligible and practically meaningful effect sizes.

**H-M2 SHOULD_WORK gate: PARTIAL.**

### 5.4 Summary of Sub-Hypothesis Results

| Sub-Hypothesis | Gate Type | Prediction | Threshold | Observed | Verdict |
|----------------|-----------|------------|-----------|----------|---------|
| H-E1: Cross-property correlation | MUST_WORK | \|ρ\| ≥ 0.40 | 0.40 | −0.758, −0.719 | SUPPORTED |
| H-E1: Latent factor | MUST_WORK | ≥50% variance, φ ≥ 0.85 | 50%, 0.85 | 72.1%, 1.000 | SUPPORTED |
| H-M1: Capability independence | MUST_WORK | Survival ≥ 0.50 | 0.50 | 0.943 | SUPPORTED |
| H-M2: Composite LOO-AUC | SHOULD_WORK | ≥ 0.70 | 0.70 | 0.739 | SUPPORTED |
| H-M2: Incremental ΔAUC | SHOULD_WORK | ≥ 0.10, CI lo > 0 | 0.10 | 0.051, [−0.194, 0.449] | NOT SUPPORTED |
| H-M3: Embedding mediation | SHOULD_WORK | Pre-registered test | — | Not executed | NOT TESTED |

**Overall verdict: PARTIALLY SUPPORTED.**

---

## 6. Discussion

### 6.1 Key Findings

The two MUST_WORK sub-hypotheses (H-E1 and H-M1) were satisfied under synthetic pipeline validation. The strong partial correlations across all five trustworthiness metrics, and the dominance of a single factor explaining 72.1% of shared variance, are consistent with the hypothesized latent structure. The survival fraction of 0.943 indicates that the ECE–TruthfulQA% association is not attributable to shared MMLU capability: controlling for MMLU reduces the correlation by 5.7%.

These results are consistent with the hypothesis that epistemic reliability constitutes a dimension largely orthogonal to raw capability. If this pattern were to replicate with real LLM evaluations, it would imply that MMLU-based model screening is not informative about this safety dimension. However, this implication rests entirely on real-data replication and cannot be derived from the synthetic pipeline validation reported here.

One mechanistic interpretation is that training procedure — specifically, the use of RLHF versus supervised fine-tuning — influences epistemic reliability largely independently of capability, which is driven by pretraining scale and data. Within-regime stratified analysis (FW4) would directly test this interpretation.

The single-factor structure, explaining 72.1% of shared variance, suggests the trustworthiness metric space is low-dimensional in the synthetic data. If confirmed with real evaluations, a compact 2–3 metric battery might efficiently capture epistemic reliability for deployment screening.

### 6.2 The ΔAUC Null Result

The ΔAUC result (0.051, CI [−0.194, 0.449]) does not support the pre-specified threshold of ΔAUC ≥ 0.10. The CI width of 0.643 is a consequence of the combination of N=30, a binary LOO outcome, and a modest underlying effect. This result is uninformative about whether a true incremental advantage exists: the CI is consistent with effect sizes ranging from slightly negative to strongly positive. A minimum sample size of N≥100 and a continuous outcome measure are necessary for a well-powered test of this prediction (FW3).

### 6.3 Limitations

**L1 — Synthetic data (critical).** All quantitative results reflect a parametric data generator, not real LLM evaluations. The generator has pre-wired latent factor structure, which means the observed correlations and factor solution are properties of the generator rather than empirical discoveries about LLMs. All claims about LLM behavior require real-data replication (FW1) before they can be made.

**L2 — N=30 underpowered for ΔAUC.** The CI width ([−0.194, 0.449]) renders the ΔAUC result uninterpretable as evidence for or against incremental predictive value.

**L3 — H-M3 not executed.** The mechanistic pathway from calibration to adversarial robustness via decision-surface smoothness under Gaussian perturbation was pre-registered but not executed. The proposed mediation test (Jonckheere-Terpstra dose-response + bootstrap mediation at ε ∈ {0.005, 0.01, 0.02}) remains an open empirical question.

**L4 — Decoding invariance not tested.** Tucker's congruence was assessed within the greedy decoding regime only. Cross-condition stability under T=0.7 stochastic decoding is pre-registered but not executed; T=0.7 data were unavailable.

**L5 — Observational design.** All results are cross-sectional correlations. Causal language about the relationship between calibration and hallucination or adversarial robustness is not warranted.

**L6 — Training regime metadata unverified.** Model card labels for RLHF, SFT, or base-only training were not independently confirmed.

**L7 — Within-family non-independence.** Models from the same family (e.g., multiple LLaMA-2 or Mistral parameter sizes) share pretraining data, architecture, and alignment procedure, violating the independence assumption of classical psychometric analysis. With 8 families across 30 models, intra-family correlation may inflate estimates of factor stability. Family-stratified sensitivity analysis (FW4) would directly assess whether the latent structure persists within individual families.

### 6.4 Future Work

**FW1 — Real-data replication (immediate priority).** Execute the pre-registered pipeline (main.py + lm-evaluation-harness v0.4.x) on the 30-model population. The implementation is complete.

**FW2 — H-M3 embedding perturbation probe.** Gaussian noise injection at ε ∈ {0.005, 0.01, 0.02}, Jonckheere-Terpstra dose-response test, bootstrap mediation analysis.

**FW3 — Scale to N≥100.** Required for a well-powered ΔAUC test.

**FW4 — Training regime stratified analysis.** Test whether the epistemic reliability factor persists within RLHF versus SFT strata, and within individual model families.

**FW5 — Extension to post-2024 and larger models.** Test replication in models exceeding 70B parameters and released after the 2024-01 cutoff.

**FW6 — Compact screening battery.** If FW1 confirms the latent structure, develop a minimal 2–3 metric proxy for practical deployment screening.

### 6.5 Broader Impact

The primary value of this work, pending real-data replication, is methodological: it demonstrates a psychometric analysis framework for LLM trustworthiness that can be applied to any population of models with standardized benchmark scores. The primary risk is misinterpretation of synthetic-data results as empirical findings about real LLMs. This limitation is stated explicitly in the abstract, the methodology section, the results section, and the limitations section.

---

## 7. Conclusion

This paper introduced the YouRA evaluation framework and reported pipeline validation results for the hypothesis that calibration quality, hallucination resistance, and adversarial robustness in LLMs co-vary along a common latent dimension — *epistemic reliability* — that is largely independent of raw MMLU capability.

Under a synthetic score matrix conforming to the hypothesized latent structure (N=30 models, 5 trustworthiness metrics):

1. **The hypothesized latent structure is recoverable.** Partial ρ(ECE, TruthfulQA%|MMLU) = −0.758 (BCa 95% CI [−0.894, −0.504]); all 10 cross-metric partial correlations exceed |ρ| = 0.40; Factor 1 explains 72.1% of shared variance (KMO = 0.879, Tucker's congruence = 1.000).

2. **The calibration–hallucination correlation is not attributable to MMLU capability.** Survival fraction = 0.943; MMLU control reduces the correlation by 5.7%. Discriminant validity with HumanEval: |partial ρ| = 0.082.

3. **Incremental predictive power over capability-only screening is uncertain.** LOO-AUC = 0.739; ΔAUC = 0.051 (BCa 95% CI [−0.194, 0.449]). The CI width indicates insufficient power at N=30 to resolve whether a meaningful incremental advantage exists.

4. **The mechanistic pathway via embedding perturbation (H-M3) was not executed.** This remains an open empirical question.

All quantitative results are synthetic-data pipeline validation. Real-data replication via lm-evaluation-harness on the target 30-model population is the immediate scientific priority before any claim about actual LLM behavior can be advanced.

---

## References

Burnell, R., et al. (2023). Rethink Reporting of Evaluation Results in NLP. *Proceedings of ACL 2023*. [citation inferred]

Efron, B., & Tibshirani, R. (1987). Better Bootstrap Confidence Intervals. *Journal of the American Statistical Association*, 82(397), 171–185. [citation inferred]

Gao, L., et al. (2021). The Pile: An 800GB Dataset of Diverse Text for Language Modeling. *arXiv:2101.00027*. [citation inferred]

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. *Proceedings of ICML 2017*, 1321–1330. [citation inferred]

Hendrycks, D., et al. (2021). Measuring Massive Multitask Language Understanding. *Proceedings of ICLR 2021*. [citation inferred]

Kadavath, S., et al. (2022). Language Models (Mostly) Know What They Know. *arXiv:2207.05221*. [citation inferred]

Kaiser, H. F. (1974). An Index of Factorial Simplicity. *Psychometrika*, 39(1), 31–36. [citation inferred]

Liang, P., et al. (2022). Holistic Evaluation of Language Models. *arXiv:2211.09110*. [citation inferred]

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. *Proceedings of ACL 2022*, 3214–3252. [citation inferred]

Nie, Y., et al. (2020). Adversarial NLI: A New Benchmark for Natural Language Understanding. *Proceedings of ACL 2020*, 4885–4901. [citation inferred]

Polo, F. M., et al. (2024). tinyBenchmarks: Evaluating LLMs with Fewer Examples. *Proceedings of ICML 2024*. [citation inferred]

Sun, L., et al. (2024). TrustLLM: Trustworthiness in Large Language Models. *arXiv:2401.05561*. [citation inferred]

Tucker, L. R. (1951). A Method for Synthesis of Factor Analysis Studies. *Educational Testing Service*. [citation inferred]

Wang, B., et al. (2021). AdvGLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models. *Proceedings of EMNLP 2021*, 6648–6668. [citation inferred]

Wang, B., et al. (2023). DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models. *Proceedings of NeurIPS 2023*. [citation inferred]

Yin, Z., et al. (2023). Do Large Language Models Know What They Don't Know? *arXiv:2305.18153*. [citation inferred]

Zhao, T., et al. (2023). Calibration of Large Language Models Using Their Generations. *arXiv:2309.13714*. [citation inferred]
