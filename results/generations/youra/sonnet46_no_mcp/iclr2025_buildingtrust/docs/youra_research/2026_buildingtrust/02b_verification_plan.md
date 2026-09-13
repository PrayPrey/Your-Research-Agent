# Verification Plan: Epistemic Reliability as a Latent Dimension in LLM Trustworthiness

**Date:** 2026-04-30
**Hypothesis ID:** H-EpistemicReliability-v1
**Confidence:** 0.72
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under a population of N≈30 instruction-tuned open-weight LLMs (7B–70B parameters, ≥3 model
families, HuggingFace-accessible as of 2024-01), if we compute a cross-property score matrix
spanning ECE (from MMLU logits), TruthfulQA accuracy %, AdvGLUE accuracy drop, Brier score, and
ANLI drop using lm-evaluation-harness under standardized conditions, then statistically
significant, stable Spearman correlation structure will be detectable (|ρ| ≥ 0.40, BCa 95% CI
excluding zero, Tucker's congruence ≥ 0.85 across greedy and T=0.7 decoding regimes), because
these metrics reflect a shared latent "epistemic reliability" property — the degree to which a
model's internal representations faithfully track uncertainty about its outputs — that partially
determines graceful degradation under input perturbation.

### 1.2 Alternative Hypothesis (H0)

There is no significant cross-property Spearman correlation structure in the (ECE, TruthfulQA %,
AdvGLUE drop, Brier score, ANLI drop) space that survives capability control (MMLU partial
correlation) and decoding invariance tests; any observed correlations reflect MMLU-driven
capability confound or evaluation pipeline artifacts, and LOO-AUC for adversarial failure
prediction does not exceed 0.60.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Multi-benchmark evaluation suite (MMLU + TruthfulQA + AdvGLUE + ANLI + HumanEval) (standard) | MMLU provides logits for ECE/Brier; TruthfulQA provides hallucination rate; AdvGLUE+ANLI provide adversarial robustness; HumanEval provides discriminant validity negative control — all directly address the cross-property correlation matrix gap |
| **Model** | N=30 open-weight instruction-tuned LLMs (7B–70B) | Open-weight models allow logit extraction for ECE/Brier computation; diverse families (LLaMA-2, Mistral, Falcon, Pythia, Qwen, Yi, OLMo, Gemma) ensure cross-family generalizability within the stated population scope |

**Dataset Details:**
- Source: lm-evaluation-harness tasks; datasets available via HuggingFace datasets library
- Path: Accessed via EleutherAI/lm-evaluation-harness v0.4.x task definitions

**Model Details:**
- Type: Causal decoder-only transformer, instruction-tuned
- Source: HuggingFace model hub; models accessible as of 2024-01

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| MMLU accuracy as trustworthiness proxy | State-of-practice default; no published LOO-AUC for adversarial failure prediction | Open LLM Leaderboard |
| DecodingTrust multi-dimensional evaluation | Qualitative trustworthiness rankings for GPT-3.5/4 only | Custom GPT evaluation |
| TrustLLM 6-dimension evaluation | Aggregate scores for 16 LLMs across 6 dimensions | TrustLLM benchmark suite |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | lm-evaluation-harness produces consistent, reproducible scores (test-retest reliability ≥ 0.8) | Standard community tool; deterministic for greedy; fixed seeds for stochastic | Measurement noise attenuates correlations → Type II error inflation |
| A2 | ECE from MMLU multi-choice logits is a valid proxy for overall model calibration quality | Standard practice since Guo et al. 2017; Kadavath et al. 2022 validate on LLMs | ECE becomes task-specific, not general → weakens cross-property correlation interpretation |
| A3 | Open-weight HuggingFace models (7B–70B) represent a meaningful diverse slice of instruction-tuned LLMs as of 2024-01 | Major families (LLaMA-2, Mistral, Falcon, Pythia, Qwen, Yi, OLMo, Gemma) cover diverse architectures and training regimes | Results may not generalize beyond sampled families; bounded external validity |
| A4 | Gaussian noise in embedding space (ε = 0.005–0.02 × ‖e‖₂) captures sensitivity correlating with adversarial text perturbations | Embedding-space perturbations are standard proxy for input sensitivity; AdvGLUE uses text-level perturbations propagating through embedding layer | Embedding perturbation instability decorrelated from adversarial text perturbations → mechanistic mediation test invalid (but predictive claim LOO-AUC remains unaffected) |
| A5 | Training regime metadata (RLHF-tuned vs. SFT-only) is accurately documented in HuggingFace model cards | Major model families publish training details; model cards reliable for well-known models | Family-level clustering uses incorrect regime labels → potentially masks or inflates training-regime association |

### 1.6 Research Gap & Novelty

**Gap:** No systematic cross-property Pearson/Spearman correlation matrix has been computed
across ECE, TruthfulQA, and AdvGLUE simultaneously for a diverse open-weight model population.
HELM provides multi-metric scores but performs no cross-metric correlation analysis.

**Novelty:** First systematic quantitative cross-property correlation matrix across ECE,
TruthfulQA, and adversarial robustness for a diverse open-weight model population; first
empirical test of "epistemic reliability" as a latent construct independent of capability.
Psychometric framing of LLM trustworthiness — treating models as "subjects" and benchmark
scores as "test items" — is a genuinely novel analytical lens. Multi-layer stress test (factor
stability + capability control + out-of-sample prediction + mechanistic probe + discriminant
validity) goes beyond pairwise correlations.

**Scope Reduction:** 33% of claims are BUILD_ON (established); verification focuses on
PROVE_NEW claims only: (1) the cross-property correlation structure itself and (2) the
mechanistic probe (ECE-perturbation instability link).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Cross-Property Epistemic Reliability Structure Exists

**Type:** EXISTENCE
**Statement:** Under a population of N≈30 instruction-tuned open-weight LLMs (7B–70B, ≥3 families), if we compute partial Spearman correlations across (ECE, Brier score, TruthfulQA %, AdvGLUE drop, ANLI drop) controlling for MMLU accuracy, then |ρ| ≥ 0.40 with BCa 95% CIs excluding zero for at least the ECE-TruthfulQA% and ECE-AdvGLUE drop pairs, and factor analysis extracts ≥1 stable factor (Tucker's congruence ≥ 0.85 across greedy vs. T=0.7), because these five metrics share a common latent root in epistemic reliability — the fidelity of a model's internal uncertainty representations.

**Rationale:** This is the foundational existence claim. Without a stable, capability-independent correlation structure, downstream mechanism and prediction claims are meaningless. The 33% scope reduction means ECE computation validity and TruthfulQA benchmark validity are BUILD_ON facts — we focus solely on proving the cross-property structure is real and not a capability artifact.

**Variables:**
- Independent: Model identity (N=30 open-weight LLMs, categorical) + Decoding regime (greedy vs. T=0.7)
- Dependent: Partial Spearman ρ matrix (ECE, Brier, TruthfulQA%, AdvGLUE drop, ANLI drop | MMLU); Tucker's factor congruence
- Controlled: MMLU accuracy (partial correlation); log-parameter count; evaluation pipeline version

**Verification Protocol:**
1. Run lm-evaluation-harness v0.4.x on all N=30 models for MMLU, TruthfulQA, AdvGLUE, ANLI, HumanEval under greedy decoding.
2. Extract MMLU logits; compute ECE (10 equal-width bins) and Brier score via netcal library.
3. Repeat all evaluations under T=0.7 decoding (fixed seed, 3-run average) for invariance test.
4. Assemble N×6 score matrix; compute partial Spearman ρ(ECE, TruthfulQA% | MMLU) and ρ(ECE, AdvGLUE drop | MMLU) with BCa bootstrap (10,000 resamples) using pingouin.
5. Run factor analysis (FactorAnalyzer) on 5-indicator set; compute Tucker's congruence between greedy and T=0.7 factor solutions.

**Success Criteria (PoC: Direction-based):**
- Primary: partial ρ(ECE, TruthfulQA% | MMLU) ≥ 0.40 AND partial ρ(ECE, AdvGLUE drop | MMLU) ≥ 0.40, BCa 95% CI excluding zero
- Secondary: ≥1 factor explaining ≥50% variance; Tucker's congruence ≥ 0.85 across decoding regimes; HumanEval loads < 0.40 on epistemic reliability factor

**Failure Response:**
- IF fails: PIVOT — correlations below 0.20 after MMLU control → H0 supported (capability confound); document as null result; do not proceed to H-M hypotheses (MUST_WORK gate)

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1 (phase2b_readiness.sh1_existence) + Predictions P1 + Sections 1.1, 1.3, 1.6

---

#### H-M1: Calibration Faithfully Tracks Prediction Uncertainty

**Type:** MECHANISM
**Statement:** Under the N=30 LLM population, if a model has lower ECE and Brier score (better calibration), then its internal confidence distributions more faithfully track prediction uncertainty — evidenced by ECE-Brier internal consistency (ρ ≥ 0.30) and by the capability-independent ECE-TruthfulQA% partial correlation (ρ ≥ 0.40) — because overconfidence and hallucination share a common root in miscalibrated confidence, a mechanistic link that cannot be explained by MMLU capability alone.

**Rationale:** This is the first causal mechanism step: calibration quality (measured by ECE and Brier) is a valid proxy for internal uncertainty fidelity, not just task performance. Validated by Kadavath et al. 2022 and Zhao et al. 2023. If ECE and Brier do not correlate (ρ < 0.30), the calibration construct is internally inconsistent and the entire mechanism chain collapses.

**Variables:**
- Independent: Model identity; calibration score (ECE, Brier)
- Dependent: ECE-Brier internal consistency (Spearman ρ); partial ρ(ECE, TruthfulQA% | MMLU)
- Controlled: MMLU accuracy; evaluation pipeline

**Verification Protocol:**
1. Compute Spearman ρ(ECE, Brier) across N=30 models; verify internal consistency (ρ ≥ 0.30).
2. Compute partial ρ(ECE, TruthfulQA% | MMLU) with BCa 95% CI using pingouin partial_corr.
3. Verify MMLU-control removes less than half the correlation (compare raw ρ vs. partial ρ to assess confounding magnitude).
4. Check decoding invariance: partial ρ should remain ≥ 0.30 under T=0.7 to confirm pipeline artifact control.
5. Confirm HumanEval (discriminant control) does NOT drive ECE variance (partial ρ(ECE, HumanEval | MMLU) < 0.20).

**Success Criteria (PoC: Direction-based):**
- Primary: partial ρ(ECE, TruthfulQA% | MMLU) ≥ 0.40 with BCa 95% CI excluding zero
- Secondary: ρ(ECE, Brier) ≥ 0.30 (construct internal consistency)

**Failure Response:**
- IF fails (partial ρ < 0.20): STOP — calibration-hallucination link is capability-confounded; document as MUST_WORK failure; route to reflection/Phase 0
- IF partial (0.20 ≤ ρ < 0.40): EXPLORE — smaller-than-expected effect; document limitation; proceed with reduced confidence

**Dependencies:** H-E1 (existence of correlation structure must be established first)

**Source:** Phase 2A Causal Step 1 + Section 1.3 + Prediction P1 + Key Assumption A2

---

#### H-M2: Hallucination and Adversarial Robustness Share Epistemic Root

**Type:** MECHANISM
**Statement:** Under the N=30 LLM population, if a model has faithful uncertainty representations (lower ECE, lower hallucination rate on TruthfulQA), then it also exhibits lower adversarial accuracy drop (AdvGLUE, ANLI), evidenced by partial ρ(ECE, AdvGLUE drop | MMLU) ≥ 0.40, and the LOO cross-validated composite predictor (ECE + TruthfulQA% + Brier) achieves AUC ≥ 0.70 for predicting top-quartile AdvGLUE failure, exceeding MMLU-only baseline by ΔR² ≥ 0.10, because well-calibrated models have smoother decision surfaces that resist both factual confabulation and adversarial perturbation.

**Rationale:** This hypothesis tests whether the epistemic reliability construct has predictive validity beyond existence — that knowing a model's calibration and hallucination scores gives you real out-of-sample signal about adversarial robustness. The LOO-AUC ≥ 0.70 threshold targets a level where the composite score would be practically useful as a cheap safety proxy.

**Variables:**
- Independent: ECE, TruthfulQA%, Brier composite; MMLU-only baseline
- Dependent: partial ρ(ECE, AdvGLUE drop | MMLU); LOO-AUC for top-quartile AdvGLUE prediction; ΔR²
- Controlled: MMLU accuracy; log-parameter count; evaluation pipeline

**Verification Protocol:**
1. Compute partial ρ(ECE, AdvGLUE drop | MMLU) and partial ρ(ECE, ANLI drop | MMLU) with BCa CIs.
2. Define top-quartile AdvGLUE drop binary label (top 25% of N=30 models = highest 7–8 models).
3. Run LOO logistic regression with composite predictor (ECE + TruthfulQA% + Brier) and MMLU-only baseline; compute AUC-ROC for both using sklearn.
4. Compute ΔR² between composite and MMLU-only; bootstrap 95% CI for ΔR² to confirm it excludes zero.
5. Record LOO-threshold selected via cross-validation (not fixed) to avoid arbitrary threshold concern.

**Success Criteria (PoC: Direction-based):**
- Primary: LOO-AUC ≥ 0.70 AND ΔR² ≥ 0.10 with bootstrap 95% CI excluding zero
- Secondary: partial ρ(ECE, AdvGLUE drop | MMLU) ≥ 0.40

**Failure Response:**
- IF fails (LOO-AUC < 0.60 or ΔR² CI includes zero): EXPLORE — composite score has no predictive advantage over capability alone; downgrade predictive claim; document limitation; H-E1 may still hold
- IF partial (0.60 ≤ AUC < 0.70): document as SHOULD_WORK limitation; proceed to H-M3

**Dependencies:** H-M1 (calibration-hallucination link must be established)

**Source:** Phase 2A Causal Step 2 + Prediction P2 + Section 1.3

---

#### H-M3: Mechanistic Pathway via Embedding Perturbation Instability

**Type:** MECHANISM
**Statement:** Under the N=30 LLM population, if a model has better calibration (lower ECE), then it exhibits lower embedding perturbation instability (fewer answer flips under Gaussian noise at ε ∈ {0.005, 0.01, 0.02}), evidenced by |ρ(ECE, instability)| ≥ 0.40, a monotonic dose-response curve across ε levels (Jonckheere-Terpstra p < 0.05), and bootstrap mediation showing perturbation instability accounts for ≥30% of the ECE→AdvGLUE drop indirect effect (BCa 95% CI excluding zero), because well-calibrated models have smoother decision surfaces that do not catastrophically flip under small input changes.

**Rationale:** This is the mechanistic probe — the strongest (and most challenging) part of the hypothesis. It distinguishes whether the ECE-AdvGLUE correlation reflects a true causal pathway through decision-surface smoothness (mechanistic) vs. a common upstream cause (confounding). The dose-response design (3 ε levels) provides empirical falsifiability that a single-point correlation cannot.

**Variables:**
- Independent: ECE; perturbation magnitude ε ∈ {0.005, 0.01, 0.02}
- Dependent: Embedding perturbation instability (answer-flip probability per ε); Spearman ρ(ECE, instability); mediation proportion ECE→instability→AdvGLUE drop
- Controlled: MMLU accuracy; model parameter count; evaluation pipeline

**Verification Protocol:**
1. For each model, apply 20 Gaussian draws at each ε level to MMLU test subset (200 examples); record answer-flip probability per draw, average across draws.
2. Compute Spearman ρ(ECE, instability) across N=30 models; bootstrap 95% CI.
3. Test dose-response monotonicity across ε ∈ {0.005, 0.01, 0.02} using Jonckheere-Terpstra test (scipy implementation).
4. Run bootstrap mediation analysis (pingouin.mediation_analysis or equivalent): ECE → instability → AdvGLUE drop; extract indirect effect proportion with BCa 95% CI (10,000 bootstraps).
5. Acknowledge limitation: mediation cannot fully resolve common-cause confounding with distributional shift sensitivity (per Prof. Rex's acknowledged critique).

**Success Criteria (PoC: Direction-based):**
- Primary: |ρ(ECE, instability)| ≥ 0.40 AND Jonckheere-Terpstra p < 0.05 for dose-response monotonicity
- Secondary: Bootstrap mediation ≥ 30% with BCa 95% CI excluding zero

**Failure Response:**
- IF fails (ρ < 0.25 or non-monotonic): EXPLORE — mechanistic pathway not supported; downgrade mechanism claim to "empirically predictive but mechanistically unresolved"; H-E1 and H-M2 may still hold
- IF partial (mediation CI includes zero but ρ holds): document as SHOULD_WORK limitation; mediation is suggestive but unconfirmed

**Dependencies:** H-M2 (shared epistemic root must be established first)

**Source:** Phase 2A Causal Step 3 + Prediction P3 + Section 1.3

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Partial ρ(ECE, TruthfulQA% \| MMLU) ≥ 0.40 AND partial ρ(ECE, AdvGLUE \| MMLU) ≥ 0.40; Tucker's ≥ 0.85 | STOP all downstream hypotheses; route to Phase 0 |
| H-M1 | MUST_WORK | partial ρ(ECE, TruthfulQA% \| MMLU) ≥ 0.40; ρ(ECE, Brier) ≥ 0.30 | STOP H-M2, H-M3; document calibration-hallucination link as capability-confounded |
| H-M2 | SHOULD_WORK | LOO-AUC ≥ 0.70 AND ΔR² ≥ 0.10 with CI excluding zero | Document predictive claim failure; continue to H-M3 with reduced confidence |
| H-M3 | SHOULD_WORK | \|ρ(ECE, instability)\| ≥ 0.40 AND Jonckheere-Terpstra p < 0.05 | Downgrade to "empirically predictive but mechanistically unresolved"; proceed to Phase 5 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Gate 1 decision | — | End of Week 2 |
| Phase 2: Core Mechanisms | H-M1 | 2 weeks (Weeks 3–4) |
| Phase 2: Core Mechanisms | H-M2 | 1 week (Week 5) |
| Phase 2: Core Mechanisms | H-M3 | 1 week (Week 6) |
| Gate 2 decision | — | End of Week 6 |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Measurement noise attenuates true correlations | A1 (pipeline reproducibility) | H-E1, H-M1, H-M2, H-M3 | High |
| R2: ECE is task-specific, not general calibration proxy | A2 (ECE validity) | H-E1, H-M1 | High |
| R3: Model family selection creates selection bias | A3 (population diversity) | H-E1, H-M2 (external validity) | Medium |
| R4: Embedding perturbation decorrelated from adversarial text | A4 (perturbation proxy validity) | H-M3 (mechanistic probe only) | Medium |
| R5: Training regime metadata inaccurate | A5 (model card reliability) | Family clustering (supplementary) | Low |

### 4.2 Mitigation Strategies

**R1: Measurement Noise (A1 violation)**
- **Prevention:** Use lm-evaluation-harness deterministic greedy mode for primary results; fixed seeds for stochastic runs; verify reproducibility on 3-model sample before full N=30 run.
- **Detection:** Test-retest reliability check on 3 held-out models; if ICC < 0.8, investigate pipeline configuration.
- **Response:** PIVOT — if reliability < 0.8, switch to averaging 3 greedy runs; report reliability as limitation.
- **Early Warnings:** Large variance in per-model score across repeated runs; anomalously high/low scores for known models.

**R2: ECE Task-Specificity (A2 violation)**
- **Prevention:** Use MMLU (57 subjects, multi-choice) as the broadest available multi-task ECE proxy; supplement with Brier score as second calibration indicator.
- **Detection:** If ρ(ECE, Brier) < 0.30, the calibration construct is internally inconsistent → H-M1 falsified.
- **Response:** EXPLORE — treat ECE and Brier as separate predictors rather than unified calibration index; check if Brier alone gives stronger signal.
- **Early Warnings:** ρ(ECE, Brier) < 0.20 in preliminary data.

**R3: Selection Bias (A3 violation)**
- **Prevention:** Sample ≥3 distinct model families (LLaMA-2, Mistral, Falcon, Pythia minimum); include both RLHF-tuned and SFT-only models; aim for N=30 with family diversity.
- **Detection:** If all top-quartile AdvGLUE failures are from a single family, external validity is bounded.
- **Response:** SCOPE — explicitly bound claims to "among the model families sampled"; flag as limitation in paper.
- **Early Warnings:** N < 20 available models meeting criteria; >50% of N from single family.

**R4: Embedding Perturbation Proxy Invalidity (A4 violation)**
- **Prevention:** Note this only affects H-M3 mechanistic probe; H-E1 and H-M2 (LOO-AUC) are unaffected even if A4 is violated.
- **Detection:** If ρ(ECE, instability) < 0.25, embedding perturbation is not capturing adversarial sensitivity.
- **Response:** EXPLORE — downgrade H-M3 to "mechanistic pathway unresolved"; maintain H-E1 and H-M2 claims; report dose-response result as supplementary.
- **Early Warnings:** Non-monotonic flip probability across ε levels at preliminary check.

**R5: Training Regime Metadata (A5 violation)**
- **Prevention:** Cross-check model card information for the 5 most ambiguous models; use paper-reported training details as ground truth.
- **Detection:** If clustering analysis is incoherent (RLHF models cluster with SFT models), metadata may be wrong.
- **Response:** SCOPE — drop regime clustering claim; report aggregate results only without RLHF/SFT breakdown.
- **Early Warnings:** Model cards with contradictory or absent training regime information.

### 4.3 Baseline Failure Pattern → Risk Mapping

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| DecodingTrust: only 2 closed models, no partial correlation | R3 (selection bias generalizability) | Extend to N=30 diverse open-weight families |
| TrustLLM: no capability control, no factor analysis | R2 (ECE conflated with capability) | Partial Spearman ρ controlling for MMLU |
| HELM: no cross-metric correlation analysis | R1 (measurement noise masking structure) | Test-retest reliability check; BCa bootstrap CIs |

### 4.4 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation Strategy |
|----|------|--------|----------|----------|---------------------|
| R1 | Pipeline measurement noise attenuates correlations | A1 | High | All | Test-retest reliability; deterministic greedy mode |
| R2 | ECE task-specific rather than general calibration | A2 | High | H-E1, H-M1 | Supplement with Brier; check ρ(ECE, Brier) ≥ 0.30 |
| R3 | Selection bias limits external validity | A3 | Medium | H-E1, H-M2 | ≥3 families; N=30; explicit scope statement |
| R4 | Embedding perturbation decorrelated from text adversarial | A4 | Medium | H-M3 only | Downgrade to "mechanistically unresolved" if fails |
| R5 | Training regime metadata inaccurate | A5 | Low | Clustering only | Cross-check model cards; drop if incoherent |

Critical Risks: 0 | High: 2 | Medium: 2 | Low: 1

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1: Existence — Cross-property correlation structure (no dependencies)
         │
         ▼ GATE 1 (MUST_WORK)
[Level 1 - Mechanism Step 1]
    H-M1: Calibration faithfully tracks prediction uncertainty ← H-E1
         │
         ▼ GATE 1.5 (MUST_WORK)
[Level 2 - Mechanism Step 2]
    H-M2: Hallucination & robustness share epistemic root ← H-M1
         │
         ▼ (SHOULD_WORK — failure does not block)
[Level 3 - Mechanism Step 3]
    H-M3: Mechanistic pathway via embedding perturbation instability ← H-M2
         │
         ▼ GATE 2 (SHOULD_WORK)
[Phase 5 — Baseline Comparison — DETERMINES_SUCCESS]

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Depth:   4 levels, 2 MUST_WORK gates, 2 SHOULD_WORK gates
═══════════════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2       │ W3-4       │ W5         │ W6
─────────────────┼────────────┼────────────┼────────────┼────────────
PHASE 1: Foundation (H-E1)
  H-E1           │ ████████   │            │            │
  [Gate 1]       │          ◆ │            │            │
─────────────────┼────────────┼────────────┼────────────┼────────────
PHASE 2: Mechanisms
  H-M1           │            │ ████████   │            │
  H-M2           │            │            │ ████████   │
  H-M3           │            │            │            │ ████████
  [Gate 2]       │            │            │            │         ◆
─────────────────┼────────────┼────────────┼────────────┼────────────
═══════════════════════════════════════════════════════════════════════
Legend: ████ = Active work  │  ◆ = Gate decision point
Total Duration: 6 weeks
Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) = 6 weeks
═══════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3)

Slack Available: 0 weeks (all sequential)
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses:  4
- Existence:       1 (H-E1)
- Mechanism:       3 (H-M1, H-M2, H-M3)
- Condition:       0 (not required)

Verification Phases: 2
1. Foundation (H-E1): 2 weeks
2. Mechanisms (H-M1 through H-M3): 4 weeks

Total Duration:    6 weeks
Critical Path:     6 weeks
Compute:           ~150–180 GPU-hours on single A100 (per Phase 2A feasibility)

Python Stack:
- scipy (Spearman ρ, Jonckheere-Terpstra)
- pingouin (partial_corr, mediation_analysis, BCa bootstrap)
- FactorAnalyzer (factor analysis, Tucker's congruence)
- sklearn (LOO logistic regression, AUC-ROC)
- netcal (ECE, Brier computation from logits)
- lm-evaluation-harness v0.4.x (all benchmark evaluations)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Weeks 1–2
Step 2: Evaluate Gate 1 → If MUST_WORK PASS, proceed; if FAIL, route to Phase 0
Step 3: Execute H-M1 (Calibration-Hallucination Mechanism) — Weeks 3–4
Step 4: Evaluate Gate 1.5 → If MUST_WORK PASS, proceed; if FAIL, stop H-M2/H-M3
Step 5: Execute H-M2 (Shared Epistemic Root + Predictive Validity) — Week 5
Step 6: Execute H-M3 (Mechanistic Probe via Embedding Perturbation) — Week 6
Step 7: Evaluate Gate 2 → Document SHOULD_WORK outcomes; proceed to Phase 5 (or skip per config)
Final:  Verification complete → Phase 2C experiment design for each hypothesis
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Instruction-tuned open-weight LLMs (7B–70B) exhibit a latent
"epistemic reliability" dimension — reflected jointly by ECE, Brier score,
TruthfulQA %, AdvGLUE drop, and ANLI drop — that is statistically distinct from
raw capability (MMLU), structurally stable across evaluation protocols, and
predictive of adversarial failure out-of-sample.

Supporting Evidence:
1. Zhao et al. 2023 demonstrate ECE-TruthfulQA correlation in existing models
   (prior empirical grounding).
2. Kadavath et al. 2022 show P(True) probing captures genuine self-knowledge
   (calibration reflects real uncertainty tracking, not just task performance).
3. Theoretical smoothness arguments: better calibrated models have smoother
   decision surfaces (Guo et al. 2017 temperature scaling); ε-perturbation
   test provides empirical dose-response test of this claim.

Strengths:
- Study design is informative under ANY outcome (unidimensional / multi-factor /
  null) — no result is uninterpretable.
- Pre-registered joint success criteria prevent post-hoc narrative construction.
- Psychometric framing (models as subjects, benchmarks as items) is a novel
  analytical lens not previously applied to LLM trustworthiness.
- Practical deployment implication: LOO-AUC ≥ 0.70 enables cheap safety proxy
  for organizations without red-team budget.

Expected Outcomes:
- P1 (PRIMARY): Partial Spearman ρ(ECE, TruthfulQA% | MMLU) ≥ 0.40 and
  ρ(ECE, AdvGLUE drop | MMLU) ≥ 0.40; Tucker's congruence ≥ 0.85
- P2: LOO-AUC ≥ 0.70 for composite predictor; ΔR² ≥ 0.10 over MMLU baseline
- P3: |ρ(ECE, instability)| ≥ 0.40; monotonic dose-response (J-T p < 0.05);
  mediation ≥ 30%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): There is no significant cross-property Spearman
correlation structure in the (ECE, TruthfulQA %, AdvGLUE drop, Brier score,
ANLI drop) space that survives capability control (MMLU partial correlation) and
decoding invariance tests; any observed correlations reflect MMLU-driven
capability confound or evaluation pipeline artifacts, and LOO-AUC does not
exceed 0.60.

Counter-Arguments:
1. Baselines insufficient → generalizability questionable: DecodingTrust and
   TrustLLM show partial orthogonality QUALITATIVELY — the quantitative partial
   correlation may collapse once MMLU is controlled.
2. Assumption violations (A1, A2): Pipeline noise and ECE task-specificity could
   attenuate true correlations below detection threshold at N=30.
3. Scope limitations: Open-weight 7B–70B models from 2024-01 may share
   pre-training data and architectural similarities (LLaMA-2 derivatives), making
   the "diverse population" claim questionable despite family diversity.

Potential Failure Points:
- R1 (High): Pipeline noise → correlations wash out; Type II error at N=30.
- R2 (High): ECE-MMLU confound → partial correlations collapse after capability
  control.
- R4 (Medium): Embedding perturbation proxy invalid for H-M3 mechanistic claim.

Conditions Under Which H0 Would Be Supported:
- If partial ρ(ECE, TruthfulQA% | MMLU) collapses below 0.20 after MMLU control.
- If factor structure is unstable (Tucker's congruence < 0.85) across decoding.
- If LOO-AUC < 0.60 — composite scores provide no advantage over random.
- If ρ(ECE, instability) < 0.25 AND dose-response is non-monotonic.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:
The hypothesis H-EpistemicReliability-v1 presents a testable, well-grounded
claim that calibration quality (ECE/Brier) is a latent anchor linking
hallucination resistance and adversarial robustness independently of raw
capability. However, the null hypothesis raises valid concerns: N=30 is at the
lower power bound, ECE task-specificity is a genuine risk, and capability
confound (MMLU) may explain observed correlations once properly controlled.

Resolution Path:
The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Partial correlation controlling for MMLU is
   the primary tool for ruling out capability confound — this is the key design
   decision that distinguishes this work from DecodingTrust/TrustLLM.
2. Sequential mechanism testing (H-M1 → H-M3): Tests the causal chain
   step-by-step; each step has explicit falsification criteria.
3. Gate conditions: MUST_WORK gates on H-E1 and H-M1 allow early detection of
   H0 support without wasting resources on H-M2/H-M3.
4. Discriminant validity control (HumanEval negative control): Prevents
   conflating epistemic reliability with general reasoning capability.

Conditions for Thesis Support:
- Both MUST_WORK gates pass (H-E1, H-M1).
- P1 confirmed: partial ρ ≥ 0.40 for both ECE-TruthfulQA% and ECE-AdvGLUE pairs.
- Factor structure stable (Tucker's ≥ 0.85).

Conditions for Antithesis Support:
- H-E1 fails (partial correlations collapse after MMLU control).
- H-M1 fails (ECE-Brier inconsistency or ECE-TruthfulQA% < 0.20 partial ρ).
- Tucker's congruence < 0.85 (pipeline artifact, not real construct).

Nuanced Outcome Possibilities:
1. Full Support: All 4 hypotheses pass → Epistemic reliability confirmed as
   distinct latent dimension with mechanistic grounding. Paper: "first systematic
   psychometric characterization of LLM trustworthiness structure."
2. Partial Support: H-E1 + H-M1 pass; H-M3 fails → "empirically predictive but
   mechanistically unresolved." Paper: practical screening tool without causal
   mechanism claim.
3. No Support: H-E1 fails → H0 supported; capability confound disciplines
   conceptual inflation. Paper: "epistemic reliability is not a distinct construct;
   MMLU captures trustworthiness structure."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Cross-property correlation is real and capability-independent | Correlations are MMLU-confounded artifacts | H-E1: partial ρ with BCa bootstrap |
| Mechanism Step 1 | Calibration faithfully tracks uncertainty (ECE-TruthfulQA link) | ECE is task-specific; link is capability epiphenomenon | H-M1: internal consistency + partial ρ |
| Mechanism Step 2 | Epistemic root enables adversarial failure prediction (LOO-AUC) | Composite scores add no value over MMLU alone | H-M2: LOO cross-validation vs. MMLU baseline |
| Mechanism Step 3 | Embedding perturbation mediates calibration→robustness pathway | Perturbation proxy invalid; common-cause confound | H-M3: dose-response + mediation analysis |
| Discriminant Validity | HumanEval loads < 0.40 on epistemic reliability factor | Coding performance is in the factor → construct conflated with reasoning | Built into H-E1 factor analysis as negative control |
| Scope | Results generalize to 7B–70B open-weight models (2024-01) | LLaMA-2 derivatives dominate; false diversity | A3 mitigation: explicit family diversity requirement |

**Overall Robustness Score:** Medium-High (design is strong; N=30 power constraint is the primary vulnerability)

**Confidence in Verification Plan:** 0.72 (matches Phase 2A confidence — N=30 power bound acknowledged)

---

## 7. Executive Summary

**Main Hypothesis:** H-EpistemicReliability-v1 — instruction-tuned open-weight LLMs exhibit a
latent "epistemic reliability" dimension (ECE + Brier + TruthfulQA% + AdvGLUE drop + ANLI drop)
statistically distinct from capability (MMLU) and predictive of adversarial failure.

**Verification Structure:**
- Mode: Incremental (33% scope reduction from BUILD_ON facts)
- Sub-Hypotheses: 4 total (H-E1: 1, H-M: 3, H-C: 0)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 MUST_WORK (H-E1, H-M1) + 2 SHOULD_WORK (H-M2, H-M3)

**Risk Assessment:** Medium
- Primary concerns: (R1) pipeline measurement noise at N=30; (R2) ECE task-specificity

**Immediate Action:** Begin Phase 1 with H-E1 — set up lm-evaluation-harness, run N=30 models under greedy decoding, compute partial Spearman correlation matrix.

---

## 8. Conclusions

### 8.1 Key Achievements
- 4 hypotheses across 2 phases designed from Phase 2A causal chain (3 steps + existence)
- H0 addressed: capability confound explicitly modeled and tested via partial Spearman ρ
- Scope reduction: 33% BUILD_ON facts excluded from re-verification
- All outcomes pre-registered: unidimensional / multi-factor / unstable / capability-confound null

### 8.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Partial Spearman correlation matrix across 5 indicators, MMLU-controlled, with factor analysis and decoding invariance test
- Gate 1: MUST PASS — failure triggers Phase 0 routing

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Calibration internal consistency + ECE-TruthfulQA% partial ρ (Weeks 3–4)
- H-M2: LOO-AUC for adversarial failure prediction; ΔR² over MMLU baseline (Week 5)
- H-M3: Embedding perturbation dose-response + bootstrap mediation (Week 6)
- Gate 2: H-M1 MUST pass; H-M2/H-M3 SHOULD pass

### 8.3 Critical Decision Points

1. **Gate 1 (H-E1 Foundation):** Partial ρ ≥ 0.40, Tucker's ≥ 0.85
   - FAIL → STOP all downstream; route to Phase 0 (capability confound null)
   - PASS → Proceed to Phase 2 with mechanism chain

2. **Gate 1.5 (H-M1 Mechanism Step 1):** Partial ρ(ECE, TruthfulQA% | MMLU) ≥ 0.40
   - CRITICAL FAIL → Stop H-M2/H-M3; document as MUST_WORK failure
   - PARTIAL → Document limitation; may proceed to H-M2 at reduced confidence

3. **Gate 2 (H-M2, H-M3 — SHOULD_WORK):**
   - Failures narrow scope claim or downgrade mechanism claim
   - Do not block Phase 5 (baseline comparison)

### 8.4 Open Questions
- Which model families cluster most distinctly in the (ECE, TruthfulQA, AdvGLUE) space?
- Will the factor solution be unidimensional or multi-factor (5-indicator expansion)?
- Does the dose-response curve hold monotonically, or is perturbation magnitude calibration needed?
- Will HumanEval load on the epistemic reliability factor (discriminant validity risk)?

### 8.5 Recommendations

1. **Immediate Actions:**
   - Set up lm-evaluation-harness v0.4.x environment; verify GPU access (single A100 or equivalent)
   - Run 3-model pilot (LLaMA-2-7B-chat, Pythia-6.9B-deduped, Mistral-7B-Instruct) for pipeline reproducibility check
   - Reserve 6 weeks on compute schedule for critical path

2. **Resource Allocation:**
   - Allocate ~150–180 GPU-hours; budget for potential re-runs if A1 violated
   - Python environment: scipy, pingouin, FactorAnalyzer, sklearn, netcal, lm-evaluation-harness

3. **Failure Management:**
   - Document ALL failures in hypothesis loop; maintain gate evaluation log
   - Execute PIVOT strategies per risk plan before routing to Phase 0
   - Pre-register three-outcome framework before running experiments

---

## Appendices

### A. Phase 2A Reference
- **Source:** `03_refinement.yaml` (ID: H-EpistemicReliability-v1)
- **Generated:** 2026-04-30T00:00:00Z | workflow: phase2a-dialogue v10.0.0
- **Discussion:** 15 exchanges, 6 agents, 12 paper citations; converged with 6/6 criteria met

### B. MCP Tool Usage Summary
- **Total MCP calls:** 2 (simulated inline — Archon/ClearThought/Exa unavailable in no-MCP build)
- **Tools:** scientificmethod (2× simulated: H-E1 existence, H-M integrated mechanism chain)
- **Note:** Archon pipeline project ID: null (no-MCP build; verification_state.yaml populated with null)

### C. Key Papers
- Guo et al. 2017 (ECE, temperature scaling)
- Kadavath et al. 2022 (P(True) self-knowledge probing)
- Zhao et al. 2023 (ECE-TruthfulQA correlation)
- Wang et al. 2023 (DecodingTrust, NeurIPS Outstanding)
- Sun et al. 2024 (TrustLLM, 16 LLMs)
- Liang et al. 2022 (HELM)
- Yin et al. 2023 (overconfidence and under-refusal correlation)

---

*Generated by YouRA Phase 2B (v6.0) | 2026-04-30*
*Status: COMPLETE | Steps: step-00 through step-10*
