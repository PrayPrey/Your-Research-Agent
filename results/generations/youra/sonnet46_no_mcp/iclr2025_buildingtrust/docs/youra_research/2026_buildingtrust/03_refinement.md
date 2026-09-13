# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-04-30T00:00:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: No Systematic Cross-Property Correlation Analysis Across Public Benchmarks
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Full pre-registered hypothesis with joint falsification criteria, N=30 power-analyzed design, 6-metric factor model with discriminant validity test, dose-response mechanistic probe, and observational training-regime clustering — all 6 convergence criteria met.

### Key Insights

1. **The psychometric framing is the core novelty**: Treating models as "subjects" and benchmarks as "test items" in a factor analysis recasts the question from "which model is most trustworthy?" to "is trustworthiness a coherent measurable construct?" — a fundamentally different and more valuable scientific question.

2. **ECE is not in public leaderboards**: The most critical practical insight from the discussion (Prof. Pax, Exchange 3) — ECE must be computed locally via lm-evaluation-harness from MMLU logits; public leaderboards only report accuracy. This constrains the study to open-weight models where logit extraction is possible.

3. **Any outcome is publishable**: Dr. Sage's reframing (Exchange 5) — confirming a distinct "epistemic reliability" axis reshapes evaluation practice; a capability-confound null result disciplines conceptual inflation in trustworthiness research. The study is informative regardless of outcome.

4. **HumanEval is the right discriminant control**: Prof. Rex's suggestion (Exchange 14) to use HumanEval pass@1 instead of latency as the negative control — coding performance is genuinely orthogonal to epistemic calibration, making it a stronger test of discriminant validity.

### Breakthrough Moments

- **Exchange 5**: Dr. Sage reframes from "prove unidimensionality" to "characterize cross-property structure" — both outcomes are scientifically informative
- **Exchange 7**: Dr. Ally synthesizes "epistemic reliability" as the causal construct linking ECE, TruthfulQA, and AdvGLUE through shared uncertainty representation fidelity
- **Exchange 9**: Prof. Pax resolves the threshold problem with LOO cross-validated optimization instead of arbitrary fixed threshold
- **Exchange 12**: Prof. Vera adds the joint pre-registration framework (three outcomes: unidimensional / multi-factor / unstable) with quantitative thresholds
- **Exchange 15**: Prof. Pax closes all three of Prof. Rex's final challenges (power analysis → N=30, factor model expansion → 5 indicators + HumanEval, training-regime language → observational only)

---

## Final Hypothesis

### Title
Epistemic Reliability as a Latent Dimension in LLM Trustworthiness: A Cross-Property Correlation Study

### Hypothesis ID
H-EpistemicReliability-v1

### Core Claim

Under a population of N≈30 instruction-tuned open-weight LLMs (7B–70B parameters, ≥3 model families, HuggingFace-accessible as of 2024-01), evaluated with lm-evaluation-harness under standardized conditions (greedy and T=0.7 decoding), if we compute a cross-property score matrix spanning ECE (from MMLU logits), TruthfulQA accuracy %, AdvGLUE accuracy drop, Brier score, and ANLI drop, then statistically significant, stable Spearman correlation structure will be detectable (|ρ| ≥ 0.40, BCa 95% CI excluding zero, Tucker's congruence ≥ 0.85 across decoding regimes), because these metrics reflect a shared latent "epistemic reliability" property — the degree to which a model's internal representations faithfully track uncertainty about its outputs — that partially determines graceful degradation under input perturbation.

### Null Hypothesis (H0)

There is no significant cross-property Spearman correlation structure in the (ECE, TruthfulQA %, AdvGLUE drop, Brier score, ANLI drop) space that survives capability control (MMLU partial correlation) and decoding invariance tests. Any observed correlations reflect MMLU-driven capability confound or evaluation pipeline artifacts, and LOO-AUC does not exceed 0.60.

### Mechanism

1. Models with well-calibrated confidence distributions (low ECE, low Brier) have representations that faithfully track prediction uncertainty
2. Calibration quality reduces hallucination susceptibility (TruthfulQA %) — both share the root of miscalibrated confidence
3. Models with faithful uncertainty representations exhibit more stable output distributions under input perturbation (lower AdvGLUE/ANLI drop) — tested via embedding perturbation dose-response across ε ∈ {0.005, 0.01, 0.02} × ‖e‖₂

---

## Predictions

### P1 (Primary): Cross-Property Correlation Structure
- **Statement**: Partial ρ(ECE, TruthfulQA% | MMLU) ≥ 0.40 AND partial ρ(ECE, AdvGLUE drop | MMLU) ≥ 0.40 with BCa 95% CIs excluding zero; factor analysis of 5-indicator set (ECE, Brier, TruthfulQA%, AdvGLUE drop, ANLI drop) extracts ≥1 stable factor (Tucker's congruence ≥ 0.85 across decoding regimes)
- **Test**: Partial Spearman correlation (pingouin), BCa bootstrap (10,000 resamples), FactorAnalyzer
- **Falsification**: Either partial ρ < 0.20 after MMLU control, OR Tucker's congruence < 0.85 across decoding regimes

### P2 (Secondary): Out-of-Sample Predictive Validity
- **Statement**: LOO-AUC ≥ 0.70 for predicting top-quartile AdvGLUE drop from (ECE + TruthfulQA% + Brier), exceeding MMLU-only baseline by ΔR² ≥ 0.10
- **Test**: Leave-one-model-out logistic regression with AUC-ROC (sklearn)
- **Falsification**: LOO-AUC < 0.60 or ΔR² CI includes zero

### P3 (Secondary): Mechanistic Mediation via Embedding Perturbation
- **Statement**: |ρ(ECE, embedding perturbation instability)| ≥ 0.40 with monotonic dose-response across ε levels (Jonckheere-Terpstra p < 0.05) and bootstrap mediation ≥ 30% of ECE→AdvGLUE indirect effect
- **Test**: Embedding perturbation experiment (20 draws per ε level), Spearman correlation, Jonckheere-Terpstra monotonicity test, pingouin mediation analysis
- **Falsification**: ρ < 0.25, non-monotonic dose-response, or mediation CI includes zero → downgrade to "empirically predictive but mechanistically unresolved"

---

## Novelty

**What's new**: First systematic quantitative cross-property correlation matrix across ECE, TruthfulQA, and adversarial robustness for a diverse open-weight model population with capability-independence test, factor stability analysis, and pre-registered falsification criteria.

**Key innovation**: Psychometric factor analysis applied to LLM trustworthiness — multi-layer stress test (structural stability + capability control + out-of-sample prediction + mechanistic probe + discriminant validity) that goes beyond pairwise correlations.

**Differentiation from prior work**:
- DecodingTrust (Wang et al. 2023): evaluates GPT models only, no partial correlations, no factor analysis, no predictive modeling
- TrustLLM (Sun et al. 2024): 16 LLMs × 6 dimensions, no capability-independence test, no out-of-sample prediction
- HELM (Liang et al. 2022): provides raw multi-metric scores but performs no cross-metric correlation analysis
- Zhao et al. 2023: demonstrates ECE-TruthfulQA link for specific models but not cross-family with adversarial robustness as third dimension

---

## Experimental Design

**Models**: N=30 instruction-tuned open-weight LLMs, 7B–70B, ≥3 families (LLaMA-2, Mistral, Falcon, Pythia, Qwen, Yi, OLMo, Gemma, MPT)

**Datasets**: MMLU (ECE/Brier from logits), TruthfulQA (hallucination rate), AdvGLUE (adversarial drop), ANLI (adversarial NLI drop), HumanEval (discriminant validity control)

**Evaluation tool**: lm-evaluation-harness v0.4.x with standardized prompt templates

**Decoding**: Greedy + temperature=0.7 (fixed seed, 3 runs averaged) for invariance test

**Analysis**: Partial Spearman correlations (pingouin), BCa bootstrap (10,000 resamples), FactorAnalyzer (Tucker's congruence), LOO logistic regression (sklearn), Jonckheere-Terpstra monotonicity test, pingouin mediation analysis, permutation MANOVA (family clustering)

**Compute**: ~150-180 GPU-hours on single A100 (≈1 week)

---

## Limitations

1. **Power constraint**: N=30 provides 80% power only for |ρ| ≥ 0.40 partial correlations; effects below this threshold are indeterminate, not null
2. **Observational scope**: Training regime clustering is observational — confounds from data curation, instruction format, and pretraining mixture prevent causal inference about RLHF
3. **Perturbation proxy**: Embedding perturbation instability approximates but does not replicate adversarial text perturbations; common-cause confounding with distributional shift sensitivity cannot be fully excluded
4. **Population scope**: Results bounded to instruction-tuned open-weight LLMs 7B–70B, HuggingFace-accessible 2024-01; not claimed to generalize to closed frontier models

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 15 exchanges |
| **Clarity Verified** | Yes |
| **Feasibility** | Confirmed — ~150-180 GPU-hours, single A100, standard Python stack |
| **Novelty** | STRONG (Dr. Nova verdict) |
| **Falsifiability** | STRONG (Prof. Vera verdict) |
| **Significance** | STRONG (Dr. Sage verdict) |
| **Remaining Objections** | Power constraint, observational clustering, perturbation proxy (all acknowledged as explicit limitations) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
