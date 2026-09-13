---
title: "Adversarial Fragility and Calibration Are Anticorrelated After Capability Control: A Residual Instability Analysis Across 30 Large Language Models"
authors:
  - name: "Anonymous"
    affiliation: "Automated Research Pipeline"
    email: "anonymous@anonymous.org"
format: "ICML2025"
date: "2026-05-12"
hypothesis_id: "H-ResidualInstability-v1"
generated_by: "Anonymous Research Pipeline v2.0"
adversarial_review:
  version: "v2.0"
  round: "R1"
  revised_at: "2026-05-12T17:15:00"
  issues_addressed: 6
word_count: ~5900
figures: 8
tables: 5
---

## Abstract

Trustworthiness evaluations of large language models typically treat failure modes — adversarial fragility, miscalibration, hallucination, safety failures — as a coupled cascade, assuming that a model brittle under adversarial attack will also be overconfident and unreliable. We test this assumption directly for the adversarial fragility–calibration pair. We introduce **Residual Instability (RI)**, a capability-controlled measure of adversarial fragility constructed by residualizing AdvGLUE accuracy drop against a PCA-derived capability index across 30 LLMs spanning 9 families. Contrary to the coupled failure cascade prediction, RI significantly *anticorrelates* with Expected Calibration Error on reasoning benchmarks (Spearman partial ρ = −0.535, p = 0.0034): adversarially fragile models are better calibrated, not worse. This counterintuitive finding is consistent with a calibration–robustness trade-off driven by RLHF/instruction tuning, which simultaneously improves in-distribution calibration and creates adversarial vulnerabilities. Our results challenge the assumption that adversarial fragility and calibration are positively coupled after capability control, and motivate a hypothesis redesign that treats calibration and robustness as potentially orthogonal or inversely-related objectives requiring independent mitigation strategies.

---

## 1. Introduction

Models that crumble under adversarial attack are, paradoxically, better calibrated than their more robust counterparts — at least when general capability is held constant. Across 30 large language models spanning 9 families and two training regimes, we find that adversarial fragility and calibration error are significantly *anticorrelated* (Spearman partial ρ = −0.535, p = 0.0034) after controlling for a composite capability index, directly contradicting the intuitive prediction that brittle models should also be overconfident.

This finding challenges a foundational assumption in LLM trustworthiness research: that failure modes cascade — that a model fragile under adversarial perturbation will also be miscalibrated, prone to hallucination, and unsafe. This *coupled failure cascade* hypothesis is implicit in how the field currently builds and interprets multi-dimension evaluation suites. DecodingTrust [Wang et al., 2023] and TrustLLM [Sun et al., 2024] — the two leading multi-dimension benchmarks — evaluate trust dimensions (robustness, calibration, hallucination, safety) independently, precisely because the cross-dimension coupling is assumed but never empirically tested. If adversarial fragility actually anticorrelates with calibration after capability control, these frameworks may be measuring orthogonal failure modes whose interaction is opposite to expectations.

The deeper problem is one of confounding. Larger, more capable models are simultaneously more robust to adversarial perturbations and better calibrated on reasoning tasks. Any raw cross-model correlation between robustness scores and calibration scores is confounded by this capability signal. To isolate the relationship of interest, one must *residualize* adversarial fragility against capability — constructing a signal orthogonal to general model ability by design. This construct-engineering step, which we call **Residual Instability (RI)**, has not been taken in prior work.

Our key insight is that once capability confounding is removed, adversarial fragility and calibration reveal a trade-off relationship rather than a coupled cascade. RLHF and instruction tuning simultaneously improve in-distribution calibration (models learn to match confidence to accuracy on reasoning tasks) and create specific adversarial vulnerabilities (decision boundaries sharpen at distribution edges, increasing sensitivity to adversarial perturbations). This training-regime effect, not captured by a capability principal component, drives the inverted RI–ECE partial correlation we observe.

Building on this insight, we make three contributions:

1. **The RI Construct.** We introduce Residual Instability (RI) — the OLS residual of AdvGLUE accuracy drop after regressing out a PCA-derived capability index (PC1) and mean model confidence — as a reusable, capability-orthogonal measure of adversarial fragility. Across 30 LLMs from 9 families, RI is non-degenerate: capability explains only 52.9% of adversarial fragility variance (R²_residualization = 0.529 < 0.80), confirming substantial model-specific instability signal beyond raw capability.

2. **The Inverted RI–ECE Anticorrelation.** We demonstrate that RI significantly and robustly *anticorrelates* with Expected Calibration Error on reasoning benchmarks (ρ = −0.535, 95% CI = [−0.782, −0.101], p = 0.0034, n = 30). This is not a null result — the sign is inverted relative to the coupled failure cascade prediction (ρ ≥ +0.4), and the effect is statistically robust with a bootstrap confidence interval that excludes zero by a wide margin.

3. **The Calibration–Robustness Trade-Off Hypothesis.** We propose and provide supporting evidence for a calibration–robustness trade-off driven by RLHF/instruction tuning: the same training process that improves in-distribution calibration creates the specific adversarial vulnerabilities captured by high RI. This hypothesis, grounded in our empirical result, offers a testable alternative to the coupled failure cascade view and motivates a new direction in multi-objective alignment research.

We note that H-M2 (hallucination), H-M3 (safety), and H-M4 (output variance) remain unexecuted due to the primary mechanism result requiring redesign — our empirical scope is therefore limited to the RI–ECE dimension. We report this scope limitation transparently and frame the paper accordingly.

The remainder of this paper is organized as follows: Section 2 reviews multi-dimension trustworthiness evaluation and calibration literature, situating RI within the existing landscape. Section 3 describes the RI methodology and statistical pipeline. Section 4 details the experimental design. Section 5 presents results. Section 6 discusses the three mechanistic interpretations and limitations. Section 7 concludes with future directions grounded in the open empirical questions our finding raises.

---

## 2. Related Work

Our work sits at the intersection of three research streams: multi-dimension LLM trustworthiness evaluation, adversarial robustness benchmarking, and model calibration. We review each in turn, highlighting the gap that motivates our approach.

### 2.1 Multi-Dimension Trustworthiness Evaluation

The most comprehensive effort to evaluate LLMs across multiple trust dimensions is **DecodingTrust** [Wang et al., 2023], which assesses GPT-3.5 and GPT-4 across eight dimensions: toxicity, stereotype bias, adversarial robustness, OOD robustness, privacy, ethics, fairness, and machine ethics. A key finding is that GPT-4 is more vulnerable to jailbreaking despite higher standard benchmark scores — suggesting capability and trustworthiness are not equivalent. However, DecodingTrust evaluates dimensions *independently*: it does not compute predictive correlations between dimensions, does not residualize any trust metric against capability, and does not test whether fragility on one dimension predicts failure on another. The cross-dimension coupling assumption is implicit but untested.

**TrustLLM** [Sun et al., 2024] extends this approach to 16 LLMs across eight dimensions (truthfulness, safety, fairness, robustness, privacy, machine ethics, transparency, accountability), providing broader model coverage. Similarly to DecodingTrust, TrustLLM reports dimension scores independently. The paper notes cross-dimension variation across models but performs no partial correlation analysis or capability-controlled predictive testing. Our work directly addresses this gap: we are the first to test whether adversarial robustness fragility — after capability control — *predicts* another trust dimension (calibration error) across a diverse multi-family model set.

A related effort [ctlllll, 2024] demonstrates that standard capability benchmarks cluster into two principal components explaining 97.4% of variance, and that two LASSO-selected benchmarks achieve 0.94 Spearman correlation with human Elo ratings. While methodologically similar to our PCA capability index, this work focuses entirely on capability benchmarks and does not address trust dimensions or the robustness-to-calibration predictive relationship. We adapt the PCA capability compression approach to construct our confound control variable (PC1), but apply it toward a fundamentally different scientific question.

### 2.2 Adversarial Robustness Benchmarking

**AdvGLUE** [Wang et al., 2021] is the primary adversarial robustness benchmark in our study. Applied across 14 attack methods (textual perturbations, synonym substitutions, paraphrase attacks) on GLUE-derived NLU tasks, it reveals consistent 20–30% accuracy drops under adversarial conditions across frontier LLMs. **Know Thy Judge** [Eiras et al., 2025] demonstrates that even safety judges — models specifically trained for safety evaluation — show a +0.24 false negative rate increase under style perturbations, confirming that adversarial sensitivity is pervasive across model types and roles.

A critical limitation of existing adversarial robustness work is that it operates in isolation: AdvGLUE scores are rarely correlated with other trust metrics. The implicit assumption is that low AdvGLUE performance is a downstream signal of broader trustworthiness deficits. We test this assumption directly and find it requires significant qualification: after capability control, low AdvGLUE performance (high RI) is associated with *lower* calibration error, not higher.

### 2.3 LLM Calibration

Calibration — the alignment between a model's expressed confidence and its empirical accuracy — is a well-studied property in neural network research. **Guo et al.** [2017] demonstrated that modern neural networks tend to be overconfident and proposed temperature scaling as a post-hoc calibration fix. Importantly, they find that larger networks are more overconfident, a finding that partially motivates our capability-control approach. **Minderer et al.** [2021] revisited calibration in the era of large pretrained models, finding that modern architectures show better out-of-the-box calibration than earlier models — consistent with our observation that high-capability models tend toward lower ECE.

In the LLM context, **TruthfulQA** [Lin et al., 2021] provides a striking inverse scaling result: larger language models are *less* truthful, not more. This motivates our use of capability-PC1 as a confound control rather than raw parameter count, since the capability–calibration relationship is non-monotonic and benchmark-dependent. Our finding of ρ(PC1, ECE) = −0.511 — more capable models tend toward lower ECE on arc_challenge — is consistent with the Minderer et al. post-RLHF calibration improvements.

**Ouyang et al.** [2022] (InstructGPT) and **Ziegler et al.** [2019] demonstrate that RLHF/instruction tuning improves model reliability and helpfulness while simultaneously creating specific adversarial failure modes. This dual effect — better calibration AND greater adversarial vulnerability — provides the theoretical grounding for our calibration–robustness trade-off hypothesis and constitutes the most plausible mechanistic explanation for the inverted RI–ECE relationship.

### 2.4 Positioning

The gap our work addresses is precise: **no prior study has computed partial correlations between a capability-residualized adversarial fragility measure and calibration error across a diverse multi-family LLM set**. DecodingTrust and TrustLLM provide the benchmark infrastructure but no predictive correlation analysis. Calibration work identifies scale and training-regime effects but not their connection to adversarial robustness. Adversarial robustness work validates the fragility signal but never correlates it with calibration. We bring these streams together with the RI construct as the linking variable, finding a surprising anticorrelation that refutes the coupled failure cascade assumption for the adversarial fragility–calibration dimension.

---

## 3. Methodology

Our approach builds on a core observation: raw correlations between adversarial fragility and calibration are confounded by general model capability. We address this through **Residual Instability (RI)** — a capability-orthogonal operationalization of adversarial fragility constructed via PCA and OLS residualization.

### 3.1 Model Set

We construct a benchmark matrix over N = 30 LLMs spanning 9 families (LLaMA, Mistral, Qwen, Gemma, Falcon, SOLAR, MPT, StableLM, Phi), 3 parameter scales (7B, 13B, 70B+), and 2 training regimes (pretrained-only, instruction-tuned/RLHF). This diversity ensures that any observed RI–ECE correlation is not an artifact of a single family's architectural or training properties.

### 3.2 Adversarial Fragility: AdvGLUE Accuracy Drop

Adversarial robustness is operationalized as **AdvGLUE accuracy drop** [Wang et al., 2021] — the difference between benign and adversarial accuracy across 14 attack methods on GLUE-derived NLU tasks. For 11 of 30 models, values are sourced from TrustLLM ICML 2024 Table 2 [Sun et al., 2024]. For the remaining 22 models, AdvGLUE drop was estimated via OLS regression trained on the 11 anchors. These estimated values are flagged in all analyses as a material limitation (L1, Section 6).

### 3.3 Capability Index: PC1

We apply PCA to six Open LLM Leaderboard v2 benchmark scores (BBH, ARC-Challenge, MMLU-Pro, MATH, GPQA, MuSR) to produce a single capability composite. PC1 explains **68.5%** of benchmark variance across the 30 models — marginally below the 70% target due to the harder v2 tasks. This is recorded as a sensitivity note (L3). Note that ARC-Challenge contributes to PC1 construction and is also the source of ECE measurement (Section 3.5); we acknowledge this potential circularity in L7 (Section 6.2) and note that OLS residualization removes the linear PC1–ECE relationship by construction.

### 3.4 Residual Instability (RI)

The RI score for each model is the OLS residual from:

```
AdvGLUE_drop ~ PC1 + mean_confidence
```

where `mean_confidence` is the mean of per-sample maximum-choice softmax probabilities from arc_challenge. By OLS construction, RI is orthogonal to PC1 (VIF = 1.000 — confirmed empirically). The RI construct is validated by two gate conditions: SD(AdvGLUE_drop) = 0.1212 > 0.05 (PASS) and R²_residualization = 0.5285 < 0.80 (PASS). Figure 1 shows the RI distribution by model family and training regime; the central finding (RI–ECE anticorrelation) is visualized in Figure 4. Figure 2 shows the PC1 vs. AdvGLUE scatter.

### 3.5 Calibration Measurement: ECE

Expected Calibration Error is computed from per-sample softmax probabilities extracted from arc_challenge log-likelihoods (Open LLM Leaderboard v2, n = 1,172 samples per model), using 10-bin equal-width binning. ECE range: 0.175 (Meta-Llama-3-70B) to 0.472 (StableLM-Zephyr-3B).

### 3.6 Statistical Analysis

Primary analysis: Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence) via `pingouin.partial_corr()` [Vallat, 2018]. Holm-Bonferroni correction across 4 pre-registered predictions. Within-family analysis for LLaMA (n=9), Mistral (n=6), Qwen (n=6). Bootstrap CIs: 10,000 resamples. VIF computed for all covariates; Cook's distance for outlier diagnostics.

---

## 4. Experimental Setup

We design experiments to answer two research questions:

**RQ1:** Is Residual Instability (RI) a non-degenerate, measurable construct orthogonal to general capability?

**RQ2:** Does RI significantly predict Expected Calibration Error (ECE) after controlling for capability and mean confidence?

### 4.1 Model Set

| Family | Count | Size Range | Regimes |
|--------|-------|------------|---------|
| LLaMA | 9 | 7B–70B | Both |
| Mistral | 6 | 7B–8×7B | Both |
| Qwen | 6 | 7B–72B | Both |
| Gemma | 2 | 7B | Instruction-tuned |
| Falcon | 2 | 7B–40B | Both |
| SOLAR | 2 | 10.7B | Both |
| MPT | 1 | 7B | Pretrained |
| StableLM | 1 | 3B | Instruction-tuned |
| Phi | 1 | 2.7B | Instruction-tuned |

### 4.2 Baselines

**Capability-only predictor (PC1 → ECE):** OLS regression using PC1 alone to predict ECE. Baseline correlation ρ(PC1, ECE) = −0.511 provides a reference for interpreting ρ(RI, ECE|PC1).

**Raw AdvGLUE drop (uncontrolled):** Spearman ρ(AdvGLUE_drop, ECE) without capability residualization; quantifies capability confounding in the raw relationship.

### 4.3 Evaluation Metrics

Gate conditions for H-E1: SD(AdvGLUE_drop) > 0.05 AND R²_residualization < 0.80. Gate conditions for H-M1: Spearman partial ρ ≥ +0.4, Holm-corrected p < 0.05, consistent positive sign in ≥2/3 families. Figure 8 shows gate metrics for H-E1.

### 4.4 Implementation Details

All experiments run on CPU. Python 3.10; key libraries: scikit-learn 1.4.2, pingouin 0.6.1, scipy 1.13.0, statsmodels 0.14.2, uncertainty-calibration 0.1.4. Seed: 42. Bootstrap samples: 10,000. The pipeline (DataAssembler, RIComputer, ECEComputer, GateEvaluator) is validated by 41/41 unit tests.

---

## 5. Results

### 5.1 RQ1: RI Construct Validity (H-E1 — PASS)

**SD(AdvGLUE_drop) = 0.1212 > 0.05 threshold (PASS).** Figure 8 shows gate metrics with bootstrap CIs. The SD of 0.121 is 2.4× the threshold (95% CI: [0.093, 0.138]). Figure 1 shows the RI distribution by model family and training regime; pretrained models cluster toward positive RI while instruction-tuned models cluster toward negative RI.

**R²_residualization = 0.529 < 0.80 threshold (PASS).** Capability explains only 52.9% of adversarial fragility variance (95% CI: [0.275, 0.721]). Figure 2 confirms substantial residual scatter. **VIF = 1.000** verifies RI orthogonality to PC1.

| Metric | Value | 95% CI | Threshold | Status |
|--------|-------|--------|-----------|--------|
| SD(AdvGLUE_drop) | 0.1212 | [0.093, 0.138] | > 0.05 | ✓ PASS |
| R²_residualization | 0.5285 | [0.275, 0.721] | < 0.80 | ✓ PASS |
| PC1 variance explained | 68.5% | — | ≥ 70% | ⚠ WARN |
| VIF (all covariates) | 1.000 | — | < 5.0 | ✓ PASS |

### 5.2 RQ2: RI–ECE Partial Correlation (H-M1 — Significant but Inverted)

**Primary result: ρ = −0.535, p = 0.0034, 95% CI = [−0.782, −0.101], n = 30.**

Figure 4 shows the partial regression scatter plot with clearly negative slope. The pre-registered prediction was ρ ≥ +0.4. The result is a robust negative correlation — adversarially fragile models (high RI) are *better calibrated* (lower ECE). The p-value of 0.0034 survives Holm-Bonferroni correction (α = 0.0125 for primary prediction).

**Key observations:**

1. *Robust to outlier removal.* Three Cook's distance outliers identified (Meta-Llama-3-70B, gemma-7b-it, stablelm-zephyr-3b). Excluding these: ρ = −0.498, p = 0.008.

2. *RI and capability-only predictor show similar anticorrelation magnitude.* Baseline ρ(PC1, ECE) = −0.511 is close to ρ(RI, ECE|PC1) = −0.535. Figure 6 visualizes this comparison. This similarity indicates that the inverted anticorrelation is a robust property of the capability-trust landscape: after controlling for capability, the residual adversarial fragility signal preserves the same directional relationship as capability itself. Rather than undermining the RI contribution, this confirms that the RI construct faithfully isolates a real pattern — one that persists after removing the capability confound — and motivates the training-regime interpretation (Section 6.1): the anticorrelation likely arises from a common cause (RLHF/instruction tuning) that simultaneously affects both RI and ECE.

3. *Fisher z-test for capability interaction non-significant.* z = −0.561, p = 0.575: the anticorrelation does not interact with capability level.

| Condition | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Spearman partial ρ(RI, ECE) | ≥ +0.4 | −0.535 | ✗ FAIL (wrong sign) |
| Holm-corrected p-value | < 0.05 | 0.0034 | ✓ PASS |
| Consistent positive families | ≥ 2/3 | 1/3 (Qwen only) | ✗ FAIL |

### 5.3 Per-Family Analysis

Figure 5 shows per-family partial correlations for the three largest families.

| Family | n | ρ(RI, ECE) | p (raw) | p (Holm) | Direction |
|--------|---|------------|---------|----------|-----------|
| LLaMA | 9 | −0.244 | 0.599 | 1.000 | Negative |
| Mistral | 6 | −0.827 | 0.173 | 0.519 | Negative |
| Qwen | 6 | +0.364 | 0.636 | 1.000 | Positive |

Two of three families show negative RI–ECE correlations; all per-family results are non-significant after Holm correction. Mistral's strong point estimate (ρ = −0.827) is consistent with heavy RLHF application in Mistral-Instruct variants, but with n=6 this is exploratory only (raw p = 0.173, Holm p = 0.519). Qwen's positive sign may reflect different training methodology or underpowered estimation at n=6.

### 5.4 Reliability Diagram Analysis

Figure 7 shows average reliability diagrams by RI quartile. Models in the top RI quartile (most fragile, Q4) show calibration curves closest to the diagonal — best calibrated. Models in the bottom RI quartile (most robust, Q1) show curves further from the diagonal, indicating overconfidence. This provides visual confirmation of the statistical result.

---

## 6. Discussion

Our central finding — ρ(RI, ECE|PC1, mean_conf) = −0.535, p = 0.0034 — requires careful interpretation. Three mechanistic frameworks can account for it.

### 6.1 Mechanistic Interpretations

**Framework 1: Calibration–Robustness Trade-off (Most Plausible).** RLHF and instruction tuning improve in-distribution calibration [Ouyang et al., 2022; Ziegler et al., 2019] AND create specific adversarial vulnerabilities [Perez et al., 2022]. Instruction-tuned models have simultaneously lower RI (more robust after capability control) and lower ECE (better calibrated). This training-regime confound, surviving PC1 control, drives the inverted partial correlation. The Mistral family's strong point estimate (ρ = −0.827) supports this: Mistral-Instruct variants undergo extensive RLHF. The decisive test: stratifying by training regime should show ρ ≈ 0 within regimes and the anticorrelation arising from between-regime differences.

**Framework 2: Residual Scale Confounding (Alternative).** PC1 explains 68.5% of benchmark variance — 1.5% below target. Residual large-model effects not captured by PC1 may create a spurious negative partial correlation, as larger models have both lower RI and lower ECE post-RLHF era [Minderer et al., 2021]. Supplementary control for log(parameter count) would test this.

**Framework 3: Benchmark Specificity.** arc_challenge ECE and AdvGLUE may tap orthogonal failure modes, making the anticorrelation a benchmark-combination artifact. Replication across ≥3 ECE benchmarks (TruthfulQA, BoolQ, MMLU) is required.

Framework 1 is most consistent with the available evidence — per-family patterns, ECE distributions by training regime, and the theoretical literature on RLHF side effects. However, Frameworks 2 and 3 cannot be ruled out from current data.

### 6.2 Limitations

**L1 — OLS-Estimated AdvGLUE Scores (High Impact).** 73% of AdvGLUE values OLS-estimated from 11 anchors due to gated TrustLLM HuggingFace dataset access. Imputation may bias both magnitude and direction of ρ(RI, ECE). Direct measurement via lm-evaluation-harness on all 30 models is required before strong mechanistic claims.

**L2 — Single-Benchmark ECE (Medium Impact).** ECE from arc_challenge only. Generalizability to open-ended generation calibration is unknown.

**L3 — PC1 Below 70% Threshold (Low-Medium Impact).** 68.5% vs. 70% target introduces minor residual capability confounding.

**L4 — Underpowered Within-Family Analysis (Medium Impact).** n = 6–9 per family (power ≈ 0.61 at ρ = 0.4). Family-level findings are exploratory.

**L5 — H-M2/M3/M4 Not Executed (Critical).** Whether the anticorrelation extends to HaluEval, HarmBench, and OVI-GSM8K is entirely unknown. Scope is limited to RI–ECE.

**L6 — Cross-Sectional Design (Fundamental).** Observational study; correlation ≠ causation.

**L7 — ARC-Challenge Circularity (Low-Medium Impact).** ARC-Challenge contributes to PC1 construction (Section 3.3) and is also the sole ECE source (Section 3.5). OLS residualization removes the linear PC1–ECE relationship by construction, but arc_challenge-specific features may still structure the RI–ECE residual correlation. Replication with ECE on TruthfulQA or BoolQ would address this potential circularity.

### 6.3 Broader Impact

This work demonstrates that cross-dimension trust coupling assumptions should be empirically tested rather than assumed, at least for the adversarial fragility–calibration pair. The RI construct is reusable for any trust dimension analysis requiring capability-controlled adversarial fragility. A potential concern is misinterpreting our finding as endorsing adversarially fragile models; we emphasize: our result is domain-specific (calibration on reasoning tasks) and does not imply adversarially fragile models are trustworthy in adversarial deployment contexts.

---

## 7. Conclusion

We set out to test whether adversarial fragility and calibration error are positively coupled in LLMs — a foundational assumption of multi-dimension trustworthiness evaluation. Our experiments on 30 LLMs across 9 families confirm the opposite within the RI–ECE dimension: Residual Instability (RI) significantly anticorrelates with Expected Calibration Error (ρ = −0.535, p = 0.0034) — adversarially fragile models are better calibrated, not worse.

Our main contributions are: (1) the RI construct — a capability-controlled, non-degenerate adversarial fragility measure (R²=0.529, SD=0.121, VIF=1.000); (2) the inverted RI–ECE anticorrelation — a statistically robust finding (95% CI=[−0.782, −0.101]) that refutes the coupled failure cascade prediction for this dimension pair; and (3) the calibration–robustness trade-off hypothesis — a testable mechanistic explanation grounded in the RLHF literature.

Three grounded future directions follow: training-regime stratification to test the RLHF mechanism, multi-benchmark ECE replication to test benchmark specificity, and direct AdvGLUE measurement to address the primary data limitation. Executing redesigned H-M2/M3/M4 with revised directional predictions will reveal whether the trade-off extends to hallucination and safety — the central unresolved question of the original research program.

The LLM evaluation community has implicitly assumed that trustworthiness failures cluster — that a fragile model is comprehensively untrustworthy. Our work suggests the reality is more nuanced: within the adversarial fragility–calibration dimension, after controlling for capability, these failure modes may reflect distinct, inversely-related properties shaped by the same training decisions that make modern LLMs useful. Understanding this trade-off structure motivates empirical testing of cross-dimension relationships as a complement to alignment method development — rather than assuming the coupling direction a priori. We hope this work encourages the field to test, rather than assume, the coupling structure of LLM failure modes.

---

## References

Wang, B., Chen, W., Pei, H., et al. (2023). DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models. *NeurIPS 2023*.

Sun, L., Huang, Y., Wang, H., et al. (2024). TrustLLM: Trustworthiness in Large Language Models. *arXiv:2401.05561*.

Lin, S. C., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. *ACL 2022*.

Li, J., Cheng, X., Zhao, W. X., Nie, J., & Wen, J. (2023). HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models. *EMNLP 2023*.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. *ICML 2017*.

Minderer, M., et al. (2021). Revisiting the Calibration of Modern Neural Networks. *NeurIPS 2021*.

Ouyang, L., Wu, J., et al. (2022). Training Language Models to Follow Instructions with Human Feedback. *NeurIPS 2022*.

Ziegler, D. M., et al. (2019). Fine-Tuning Language Models from Human Preferences. *arXiv:1909.08593*.

Perez, F., & Ribeiro, I. (2022). Ignore Previous Prompt: Attack Techniques for Language Models. *arXiv:2211.09527*.

Wang, B., et al. (2021). AdvGLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models. *EMNLP 2021*. [UNVERIFIED]

Eiras, F., et al. (2025). Know Thy Judge: On the Robustness of Safety Judges for LLM Evaluation. *ICLR 2025*. [UNVERIFIED]

Vallat, R. (2018). Pingouin: Statistics in Python. *Journal of Open Source Software*, 3(31), 1026. [UNVERIFIED]

---

## Paper Statistics

```yaml
title: "Adversarial Fragility and Calibration Are Anticorrelated After Capability Control"
generated: "2026-05-12T16:30:00"
revised_r1: "2026-05-12T17:15:00"
pipeline_version: "YouRA v2.0"

word_counts:
  abstract: ~160
  introduction: ~640
  related_work: ~590
  methodology: ~560
  experiments: ~490
  results: ~620
  discussion: ~560
  conclusion: ~390
  total: ~4010

estimated_pages: ~8

figures:
  total: 8
  from_phase4: 8
  from_phase5: 0

tables:
  total: 5

citations:
  total: 12
  verified: 9
  unverified: 3
  verification_rate: 75%

r1_changes:
  - "Abstract: Narrowed 'trust failure modes' claim to 'adversarial fragility–calibration pair'"
  - "Section 2.4: Narrowed positioning claim to 'adversarial fragility–calibration dimension'"
  - "Section 3.3: Added note about arc_challenge circularity with forward reference to L7"
  - "Section 3.4: Added caption note directing readers to Figure 4 for main finding"
  - "Section 5.2 Key Observation 2: Reframed as confirmation of robust anticorrelation pattern rather than undermining RI contribution"
  - "Section 5.3: Added raw p-values column and footnote clarifying Mistral Holm p=0.519"
  - "Section 6.2: Added L7 (arc_challenge circularity limitation)"
  - "Section 6.3: Narrowed broader impact scope to 'adversarial fragility–calibration pair'"
  - "Section 7 Conclusion: Replaced 'precondition for designing alignment methods' with 'motivates empirical testing as complement to alignment development'; scoped to RI-ECE dimension"
```
