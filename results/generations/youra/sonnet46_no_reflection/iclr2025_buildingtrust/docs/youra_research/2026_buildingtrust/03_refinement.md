# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-12T00:00:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap1
- **Gap Title**: No Systematic Cross-Benchmark Predictive Correlation Study for LLM Failure Modes
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16

**Convergence Reason**: All 6 convergence criteria met — SPECIFIC (RI construct defined), MECHANISM (domain-general instability via OVI), PREDICTIONS (P1-P4 pre-registered with exact thresholds), NOVELTY (orthogonal axis beyond capability), FEASIBILITY (existing benchmarks only), OBJECTIONS (contamination, power, lineage, interaction all addressed)

### Key Insights
- The TruthfulQA inverse scaling finding (larger models less truthful) is a critical confound requiring capability-PC1 control before any cross-dimension correlation claim
- Residualizing AdvGLUE_drop against capability-PC1 + mean_confidence is the key methodological move transforming a raw correlation study into a construct discovery attempt (Residual Instability, RI)
- LOFO-CV (leave-one-family-out cross-validation) is the appropriate transportability validation with small model sets
- OVI on GSM8K arithmetic is the most novel prediction — cross-domain instability signal rules out task-specific linguistic confounds
- Contamination stratification by benchmark release year turns a threat into a replication strength demonstration

### Breakthrough Moments
- **Exchange 8**: Prof. Pax identified geometric mechanism requires model internals → redirected to behavioral proxies (OVI, self-consistency variance)
- **Exchange 11**: Dr. Sage proposed residual instability score (RI) residualized against PC1 + mean_confidence as the construct independence test
- **Exchange 12**: Dr. Ally synthesized two-stage design and contamination stratification as practical path through all objections
- **Exchange 15**: Prof. Vera formalized conjunctive falsification criteria with pre-committed withdrawal thresholds
- **Exchange 16**: Dr. Nova proposed cross-domain OVI prediction as the paradigm-shift headline finding

---

## Final Hypothesis

### Title
Residual Instability as an Orthogonal Trust-Failure Predictor in LLMs

### Hypothesis ID
H-ResidualInstability-v1

### Core Claim
Under a diverse set of ≥30 LLMs spanning ≥3 families, ≥2 scales, and ≥2 training regimes, if adversarial robustness fragility (AdvGLUE accuracy drop) is residualized against a composite capability index (PC1 of MMLU/GSM8K/BBH/HellaSwag/WinoGrande) and mean model confidence to produce a Residual Instability score (RI), then RI will significantly predict calibration error (ECE), hallucination rate (HaluEval), and out-of-sample safety failure (HarmBench) — because adversarial fragility reflects a domain-general structural property of the model's decision surface that is orthogonal to capability and causes coupled failure across trust dimensions.

### Mechanism
RI reflects sharp or anisotropic decision boundaries in model representation space. Models with high adversarial fragility overcommit with high confidence to brittle predictions (→ ECE), fail under distribution shift by fabricating plausible outputs (→ hallucination rate), and misclassify safety-relevant inputs under style perturbations (→ HarmBench failure). Domain-generality is confirmed if RI also predicts output variance (OVI) on GSM8K arithmetic reasoning under controlled temperature sampling (T=0.7, 20 samples), ruling out task-specific linguistic confounds.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (Primary) | RI significantly predicts ECE after controlling for capability-PC1 and mean confidence | Partial ρ ≥ 0.4, Holm p < 0.05 | Partial ρ < 0.2 or sign reversal in >1 family |
| **P2** | RI significantly predicts HaluEval hallucination rate | Partial ρ ≥ 0.4; within-family ρ ≥ 0.2 in ≥2 families | Partial ρ < 0.2 or within-family ρ < 0.2 in all families |
| **P3** | RI adds out-of-sample predictive power for HarmBench via LOFO-CV | ΔR² ≥ 0.1 in ≥2/3 LOFO folds; permutation p < 0.05 | ΔR² < 0.1 in ≥2 folds, or negative ΔR² in any fold |
| **P4** | RI predicts GSM8K OVI (domain-general instability probe) | ρ(RI, OVI) ≥ 0.4, Holm p < 0.05 (open-source subset) | ρ < 0.2 or non-significant |

---

## Novelty

**Key Innovation**: Residual Instability (RI) — a capability-controlled operationalization of adversarial fragility that predicts hallucination, calibration error, and safety failure out-of-sample via LOFO-CV; validated cross-domain via GSM8K OVI mechanistic probe.

**Differentiators**:
- DecodingTrust: evaluates 8 trust dimensions independently — no inter-dimension predictive correlations, no capability residualization, no forward prediction
- TrustLLM: benchmarks 16 LLMs across 8 dimensions — reports scores independently, no RI construct, no LOFO-CV
- ctlllll/understanding_llm_benchmarks: Spearman correlations for general capability — targets capability not trust/failure-mode prediction, no RI concept
- Know Thy Judge: single dimension (safety judges), no cross-dimension correlation, no capability control

---

## Experimental Design

### Model Set
≥30 LLMs spanning:
- **Families**: LLaMA-series, Mistral-series, GPT-series (or equivalent, ≥3 families)
- **Scales**: ≤13B and ≥30B parameter tiers
- **Training regimes**: Pretrained-only and RLHF/instruction-tuned (2-cell stratification)

### Datasets & Tools
| Benchmark | Purpose | Source |
|-----------|---------|--------|
| AdvGLUE | Adversarial robustness (IV) | AI-secure/adversarial-glue |
| MMLU, GSM8K, BBH, HellaSwag, WinoGrande | Capability-PC1 computation | lm-evaluation-harness |
| ECE on QA tasks | Calibration error (DV-primary) | p-lambda/verified_calibration |
| HaluEval | Hallucination rate (DV) | RUCAIBox/HaluEval |
| HarmBench | Safety failure (held-out DV for LOFO-CV) | centerforaisafety/HarmBench |
| GSM8K (T=0.7, 20 samples) | OVI mechanistic probe (open-source) | lm-evaluation-harness |

### Statistical Protocol
1. **Stage 1**: Descriptive Spearman correlation matrix across all trust dimensions (raw)
2. **Stage 2**: Compute RI = OLS residual of AdvGLUE_drop ~ PC1 + mean_confidence
3. Partial Spearman correlations ρ(RI, ECE|PC1,conf) and ρ(RI, HaluEval|PC1,conf) with Holm correction
4. Split-sample Fisher z-test for interaction (high vs. low PC1 halves)
5. LOFO-CV: train [RI+PC1]→HarmBench on 2 families, test on 3rd (3 rotations)
6. Within-family partial correlations reported separately
7. OVI computation and correlation with RI (open-source models)
8. Sensitivity: contamination strata, jackknife, VIF < 5, bootstrap CIs (10,000 resamples)

---

## Limitations

- **Power**: Within-cell power is exploratory (~0.61 per cell with n≈10); subgroup analyses pre-registered as exploratory
- **Closed models**: OVI mechanistic probe limited to open-source models (temperature sampling requires model access); GPT-series excluded
- **Contamination**: Cannot be fully eliminated for older benchmarks (TruthfulQA 2021, AdvGLUE 2021); treated as sensitivity analysis
- **Causal direction**: Cannot be established from cross-sectional cross-model data; all claims are associative/predictive
- **Scale**: 30-model set is small by ML standards; single-outlier sensitivity reported via Cook's distance

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Converged at Exchange 16 — all 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Within-cell power exploratory; OVI limited to open-source; contamination as sensitivity analysis |

### Pre-committed Falsification
If any two of P1–P3 fail, the "orthogonal instability axis" construct claim is withdrawn. The study is still publishable as a descriptive robustness–trust correlation analysis. Pre-registration on OSF recommended before data collection.

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Participants: Dr. Nova (🔭), Prof. Vera (🔬), Dr. Sage (🎯), Prof. Pax (⚙️), Dr. Ally (🛡️), Prof. Rex (🔍)*
