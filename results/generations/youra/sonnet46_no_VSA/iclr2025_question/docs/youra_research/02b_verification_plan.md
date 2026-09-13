---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-08-02T15:48:00Z"
hypothesis_id: H-SE-Ensemble-v1
total_hypothesis_count: 4
research_mode: incremental
---

# Verification Plan: SE Conditional Independence & Ensemble AUROC on TriviaQA/TruthfulQA

**Date:** 2026-08-02
**Hypothesis ID:** H-SE-Ensemble-v1
**Confidence:** 0.72
**Total Hypotheses:** 4

---

## 0. Established Facts & Scope Reduction

### 0.1 BUILD_ON Claims (DO NOT RE-VERIFY)

| Claim | Evidence |
|-------|----------|
| SE pipeline non-degenerate (fraction_degenerate=0.000, SE_variance=0.1522) on TriviaQA dev with Llama-3.1-8B at temp=0.7 | h-e1 snapshot 2026-08-02, 90 prompts |
| Full-sequence token log-probability variance: AUROC ~0.825 on TriviaQA dev (Llama-3.1-8B) | h-m1 limitation record, 300/2500 samples |
| AUROC under lexical correctness (ROUGE-L) biased by response length (Spearman |ρ| up to 0.9) | Santilli et al. 2025 (arXiv:2504.13677) |
| NLI-based black-box UQ scorers best in 13/24 AUROC scenarios | UQLM Bouchard et al. 2025 (arXiv:2504.19254) |
| Hidden-state trajectory SVD PROHIBITED (AUROC=0.537 after length control, MECHANISM_CONFOUNDED_BY_LENGTH) | h-e1 FAIL record 2026-08-02 |

**Scope Reduction: 50%** (5 claims total; 3 BUILD_ON, 2 PROVE_NEW)

### 0.2 PROVE_NEW Claims (Hypothesis Targets)

1. SE and min_logprob are algebraically distinct, manifesting as conditional independence (partial R² ≥ 0.02 in conditional LR)
2. Adding SE to min_logprob achieves ΔAUROC ≥ 0.025 on TriviaQA dev under LM-as-a-judge correctness with length-matched evaluation

**Phase 2B-4 Instructions:** Use validated h-e1 infrastructure directly. Focus exclusively on PROVE_NEW claims.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under Llama-3.1-8B (temperature=0.7, N=5 stochastic samples, greedy decode for log-prob features) on TriviaQA dev (2500 prompts, LM-as-a-judge correctness with a separate cross-model judge), if Semantic Entropy (SE_N5, bidirectional DeBERTa-MNLI NLI clustering per Kuhn et al. 2023) is added to a min_logprob baseline ensemble, then ΔAUROC ≥ 0.025 (95% CI lower bound > 0 on a length-matched subset of ~400-800 matched pairs), because SE captures semantic disagreement across stochastic samples that is conditionally independent of token-level minimum log-probability — as demonstrated by partial R² ≥ 0.02 for SE in a conditional logistic regression controlling for min_logprob, response length, and their interaction.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in AUROC between the min_logprob baseline and the [min_logprob + SE_N5] ensemble on TriviaQA dev under LM-as-a-judge correctness (ΔAUROC = 0, 95% CI overlapping zero on length-matched subset), indicating that SE does not provide conditionally independent uncertainty signal beyond token-level likelihood on TriviaQA short-answer factual QA.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA dev (primary) + TruthfulQA (transfer) [standard] | TriviaQA dev was benchmark for h-m1 (AUROC=0.825 baseline) and h-e1 (SE validation). Directly comparable. TruthfulQA is secondary generalizability benchmark. |
| **Model** | Llama-3.1-8B (primary generator) + cross-model judge (Qwen-2.5-7B or GPT-4o-mini) | Llama-3.1-8B validated in h-m1; cross-model judge required to avoid shared-bias circularity per Santilli 2025. |

**Dataset Details:**
- Source: mandarjoshi/trivia_qa (HuggingFace); sylinrl/TruthfulQA (GitHub)
- Path: TriviaQA: standard HuggingFace split, dev set 2500 prompts; TruthfulQA: MC split

**Model Details:**
- Type: Open-weight 7-8B decoder LLM
- Source: meta-llama/Llama-3.1-8B (HuggingFace); judge: cross-model (separate from generator)

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| min_logprob + full_seq_variance (h-m1 baseline) | AUROC ~0.825 | TriviaQA dev (300/2500 samples) |
| Semantic Entropy standalone (Kuhn et al. 2023) | AUROC 0.83 | TriviaQA (30B OPT, different protocol) |
| UQLM tunable ensemble (Bouchard et al. 2025) | Best in 20/24 scenarios | GSM8K, SVAMP, CSQA, AI2-ARC, PopQA, NQ-Open |
| Raghuvanshi et al. 2025 | AUC 0.818 | SQuAD2.0 only |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | SE and min_logprob not strongly correlated (Pearson \|r\| < 0.7) | Algebraic distinctness; UQLM complementary profiles | Ensemble compresses correlated signals; ΔAUROC ≈ 0; H0 not rejected |
| A2 | LM-as-a-judge not correlated with SE (Spearman \|ρ\| < 0.4) | Judge evaluates factual alignment of single answer; SE evaluates consistency across N=5 samples | ρ > 0.6 → circularity; ΔAUROC under LM-judge not genuine UQ measurement |
| A3 | temp=0.7 produces sufficient SE diversity (SE_variance > 0) | h-e1 snapshot: SE_variance=0.1522, fraction_degenerate=0.000 | SE provides no discriminative signal (already validated as non-issue) |
| A4 | Ensemble generalizes Llama→Qwen (AUROC gap < 0.05 on TruthfulQA) | CCUF +5.2% vs GPT-4 on TruthfulQA; UQLM consistent across GPT-4o and Gemini | Per-model retuning required; generalizability limited |
| A5 | No prohibited approaches reintroduced | All features are log-prob or black-box sampling-based; length residualization on UQ features only | Reproduces prior failures with known mechanism |

### 1.6 Research Gap & Novelty

First length-bias-robust AUROC benchmark for consistency+log-prob ensemble on TriviaQA/TruthfulQA with open-weight Llama-3.1-8B and Qwen-2.5-7B. First mechanistic conditional independence test (partial R² in conditional LR) for SE vs min_logprob. Operationalizes Santilli 2025's call for LM-judge evaluation with cross-model judge, length-matching, and correctness-function robustness sweep.

**Differentiation from prior work:**
- Kuhn 2023: SE standalone, OPT-30B, ROUGE-L; we add log-prob combination + LM-judge + length controls
- Manakul 2023: SelfCheckGPT on WikiBio; we use TriviaQA/TruthfulQA + log-prob combination
- Raghuvanshi 2025: SQuAD2.0 only, no public code; we benchmark TriviaQA/TruthfulQA, open-weight, public code
- UQLM 2025: GPT-4o/Gemini, 6 other benchmarks; we provide open-weight benchmark with mechanistic analysis

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | SE_N5 and min_logprob are empirically conditionally independent (Pearson \|r\| < 0.7; partial R² ≥ 0.02 in conditional LR) | MUST_WORK | None | READY |
| H-M1 | MECHANISM | Algebraic distinctness of SE and min_logprob manifests as conditional independence in logistic regression (partial R² ≥ 0.02, p < 0.05) | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Orthogonality zone (min_logprob ≥ 0.8 AND SE top quartile) is enriched for factual hallucinations (error rate ≥ baseline + 10pp) | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | Ensemble [min_logprob + SE_N5] achieves ΔAUROC ≥ 0.025 over min_logprob alone on TriviaQA dev (95% CI lower bound > 0, length-matched) with cross-model transfer to Qwen-2.5-7B (AUROC gap < 0.05 on TruthfulQA) | MUST_WORK | H-M1 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: SE–min_logprob Conditional Independence (Existence)**

**Statement**: Under Llama-3.1-8B (temp=0.7, N=5) on TriviaQA dev (2500 prompts), if SE_N5 (bidirectional DeBERTa-MNLI clustering) and min_logprob (greedy decode) are computed, then Pearson |r|(SE, min_logprob) < 0.7 and partial R²(SE) ≥ 0.02 in conditional LR [logit(h=1) ~ min_logprob + SE + L + SE×min_logprob], because SE marginalizes over semantic class masses while min_logprob captures minimum token-level prediction confidence — algebraically distinct measures.

**Rationale**: This is the foundational test: if SE and min_logprob are not empirically independent, the ensemble hypothesis collapses. H-E1 is intentionally scoped to a diagnostic (pre-experiment correlation check + conditional LR), not a full ensemble evaluation. The h-e1 infrastructure (generate.py, compute_signals.py) is directly reusable.

**Variables**:
- Independent: SE_N5 (DeBERTa-MNLI clustering), min_logprob (greedy decode)
- Dependent: Pearson r(SE, min_logprob); partial R²(SE) in conditional LR; ρ(SE, LM-judge)
- Controlled: Response length (covariate in LR); LM-as-a-judge correctness (cross-model judge)

**Verification Protocol**:
1. Load h-e1 checkpoint; extract SE_N5 and min_logprob on TriviaQA dev 2500 prompts.
2. Compute Spearman/Pearson correlation matrix (features × response_length × LM-judge).
3. Run pre-experiment circularity diagnostic: ρ(SE, LM-judge); report before proceeding.
4. Fit conditional LR; compute partial R²(SE) via likelihood-ratio test (LRT).
5. Report: |r|(SE, min_logprob), partial R²(SE), β₂(SE) significance, ρ(SE, LM-judge).

**Success Criteria**:
- Primary: Pearson |r|(SE, min_logprob) < 0.7 AND partial R²(SE) ≥ 0.02 (LRT p < 0.05)
- Secondary: ρ(SE, LM-judge) < 0.4 (circularity check passes)

**Failure Response**:
- IF |r| > 0.85: ABANDON — SE is near-monotone reparameterization; report as meaningful null
- IF 0.7 < |r| < 0.85 OR partial R² < 0.02: EXPLORE — recheck N=10 ablation; narrow scope

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 1.3 (Causal Step 1), Section 5 (SH1 existence)

---

**H-M1: Conditional Independence Mechanism (Mechanism Step 1)**

**Statement**: Under Llama-3.1-8B on TriviaQA dev, the algebraic distinctness of SE_N5 (entropy over semantic class masses) and min_logprob (minimum token probability on greedy path) manifests as conditional independence in a logistic regression: partial R²(SE) ≥ 0.02 (LRT p < 0.05) when predicting LM-as-a-judge correctness while controlling for min_logprob, response length, and their interaction.

**Rationale**: H-M1 operationalizes the core mechanism claim: algebraic distinctness must manifest as statistical conditional independence to support the ensemble hypothesis. Partial R² ≥ 0.02 is the pre-registered threshold from Phase 2A Dialogue consensus (all 6 agents agreed). Builds directly on H-E1 correlation diagnostics.

**Variables**:
- Independent: SE_N5, min_logprob, response_length, SE×min_logprob (interaction)
- Dependent: Partial R²(SE) in conditional LR; β₂(SE) coefficient significance
- Controlled: Cross-model LM-as-a-judge labels; 5-fold nested CV for LR weight tuning

**Verification Protocol**:
1. Use H-E1 computed features (SE_N5, min_logprob, response_length, LM-judge labels).
2. Fit conditional LR with 5-fold CV (inner: L2 regularization; outer: evaluation).
3. Compute partial R²(SE) via likelihood-ratio test comparing model with/without SE term.
4. Report β₂(SE) coefficient, Wald p-value, and partial R² with 95% CI.
5. Verify sign-stability of β₂(SE) across correctness functions (ROUGE-L, BERTScore, LM-judge).

**Success Criteria**:
- Primary: Partial R²(SE) ≥ 0.02 AND β₂(SE) significant at p < 0.05
- Secondary: β₂(SE) sign positive and stable across all three correctness functions

**Failure Response**:
- IF partial R² < 0.01: PIVOT — investigate N=10 ablation; consider SelfCheckNLI as substitute
- IF 0.01 ≤ partial R² < 0.02: EXPLORE — report as marginal; proceed to H-M3 with caveat

**Dependencies**: H-E1 (correlation diagnostics must confirm |r| < 0.7)

**Source**: Phase 2A Section 1.3 (Causal Step 1), Section 1.6 (Prediction P2)

---

**H-M2: Orthogonality Zone Hallucination Enrichment (Mechanism Step 2)**

**Statement**: Under Llama-3.1-8B on TriviaQA dev, prompts in the orthogonality zone (min_logprob ≥ 0.8 AND SE in top quartile) have an error rate (1 − LM-judge correctness) at least 10 percentage points above the overall baseline error rate, because these prompts correspond to cases where the model generates individually fluent but globally semantically inconsistent answers across N=5 samples.

**Rationale**: H-M2 provides the mechanistic explanation for WHY the ensemble works: the orthogonality zone captures a qualitatively distinct failure mode (locally confident, globally inconsistent) that min_logprob alone misses. This slice analysis is an original mechanistic contribution beyond AUROC comparison.

**Variables**:
- Independent: min_logprob threshold (≥ 0.8) AND SE quartile (top 25%)
- Dependent: Error rate in orthogonality zone vs baseline error rate on TriviaQA dev
- Controlled: Same LM-as-a-judge labels as H-E1/H-M1; same 2500-prompt set

**Verification Protocol**:
1. Using H-E1 computed features, slice TriviaQA dev: min_logprob ≥ 0.8 AND SE top quartile.
2. Compute error rate (1 − LM-judge correctness) in this zone vs full dataset baseline.
3. Compute error rate difference with 95% bootstrap CI (question-level resampling).
4. Check zone size (expected: ~10-20% of dataset); report if zone is too sparse (<5%).
5. Vary min_logprob threshold (0.7, 0.8, 0.9) as sensitivity analysis.

**Success Criteria**:
- Primary: Zone error rate ≥ baseline error rate + 10pp (95% CI lower bound > 0)
- Secondary: Zone size ≥ 5% of dataset (sufficient support for the claim)

**Failure Response**:
- IF zone enrichment < 10pp: EXPLORE — widen zone definition; document as limitation
- IF zone too sparse: SCOPE — report as observation rather than mechanistic test

**Dependencies**: H-M1 (partial R² test must pass; confirms SE carries independent signal)

**Source**: Phase 2A Section 1.3 (Causal Step 2), Section 1.6 (Falsifier for Step 2)

---

**H-M3: Ensemble AUROC Gain & Cross-Model Transfer (Mechanism Step 3)**

**Statement**: The logistic regression ensemble [min_logprob + SE_N5] trained on TriviaQA dev with Llama-3.1-8B achieves AUROC ≥ 0.85 and ΔAUROC ≥ 0.025 over min_logprob alone (95% CI lower bound > 0 on length-matched subset of ≥400 matched pairs) under LM-as-a-judge correctness, with ΔAUROC sign-stable across ROUGE-L, BERTScore, and LM-judge correctness functions; and Llama-calibrated ensemble weights applied to Qwen-2.5-7B on TruthfulQA achieve AUROC within 0.05 of Llama baseline.

**Rationale**: H-M3 is the primary empirical claim and the terminal mechanism step. It integrates H-M1 (conditional independence) and H-M2 (orthogonality zone) into a concrete AUROC benchmark. The cross-model transfer test (Llama→Qwen without refitting) is the generalizability check. This is a MUST_WORK gate because a failed or null result here (ΔAUROC < 0.025) would indicate likelihood saturation — still a publishable finding, but requires reclassification as null result.

**Variables**:
- Independent: UQ method (baseline_min_logprob, plus_SE, full_5feature); LLM (Llama-3.1-8B, Qwen-2.5-7B)
- Dependent: AUROC (LM-judge, TriviaQA dev); ΔAUROC (ensemble − min_logprob); cross-model AUROC gap
- Controlled: 5-fold nested CV; length-matched subset (±1 token pairs); question-level bootstrap CI (N=2000)

**Verification Protocol**:
1. Fit logistic regression ensemble [min_logprob + SE_N5] via 5-fold nested CV on TriviaQA dev.
2. Evaluate AUROC on held-out folds; compute ΔAUROC over min_logprob standalone.
3. Construct length-matched subset (correct vs incorrect pairs ±1 token); compute ΔAUROC with 2000 bootstrap samples.
4. Run correctness-function sweep: ΔAUROC under ROUGE-L, BERTScore, LM-judge; verify sign-stability.
5. Generate Qwen-2.5-7B responses on TruthfulQA (N=5, temp=0.7); apply Llama-calibrated weights; compute AUROC gap vs Llama on same TruthfulQA split.

**Success Criteria**:
- Primary: AUROC(ensemble) ≥ 0.85 AND ΔAUROC ≥ 0.025 (95% CI lower bound > 0, length-matched)
- Secondary: ΔAUROC sign positive and stable across all three correctness functions
- Secondary: Cross-model AUROC gap < 0.05 (Llama→Qwen, TruthfulQA)

**Failure Response**:
- IF ΔAUROC < 0.025 (CI overlaps zero): treat as likelihood saturation finding, NOT pipeline failure; report H0 supported with evidence
- IF AUROC < 0.85: EXPLORE — check whether SelfCheckNLI_N5 or full_5feature ensemble recovers performance
- IF cross-model gap > 0.05: SCOPE — report ensemble as Llama-specific; recommend per-model calibration

**Dependencies**: H-M1 (partial R² ≥ 0.02 confirmed), H-M2 (orthogonality zone check completed, even if marginal)

**Source**: Phase 2A Section 1.3 (Causal Step 3), Section 1.6 (Predictions P1, P3)

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Pearson \|r\| < 0.7 AND partial R²(SE) ≥ 0.02 | STOP if |r| > 0.85; EXPLORE if marginal |
| H-M1 | MUST_WORK | Partial R²(SE) ≥ 0.02, p < 0.05 in conditional LR | PIVOT to N=10 ablation; EXPLORE if marginal |
| H-M2 | SHOULD_WORK | Zone error rate ≥ baseline + 10pp | Document as limitation; proceed to H-M3 |
| H-M3 | MUST_WORK | ΔAUROC ≥ 0.025, 95% CI lower bound > 0 | Treat as likelihood saturation null result if <0.025 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Gate 1 | — | Week 2 end |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 4 weeks |
| Gate 2 | — | Week 6 end |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): High Correlation Between SE and min_logprob**
- **Source Assumption:** A1 — SE and min_logprob not strongly correlated (|r| < 0.7)
- **Description:** If |r| > 0.7, SE is effectively a reparameterization of log-prob; ensemble gain collapses to zero; ΔAUROC ≈ 0; partial R² ≈ 0.
- **Severity:** Critical
- **Likelihood:** Medium (algebraic distinction is theoretically motivated; but TriviaQA short-answer QA may yield high correlation empirically given likelihood saturation concern)
- **Affected Hypotheses:** H-E1, H-M1, H-M3 (entire chain blocked)
- **Mitigation:**
  1. Prevention: Pre-experiment diagnostic (Pearson r) before any ensemble fitting
  2. Detection: Spearman correlation matrix as first analysis step in H-E1
  3. Response: If |r| > 0.85 → ABANDON H-M1-M3; report as meaningful null (likelihood saturation); publishable as-is

**Risk R2 (from A2): Circularity — LM-Judge Shares NLI Reasoning with SE**
- **Source Assumption:** A2 — ρ(SE, LM-judge) < 0.4
- **Description:** If the cross-model judge uses NLI-based reasoning similar to DeBERTa-MNLI, the ΔAUROC under LM-judge would be artificially inflated (circular).
- **Severity:** High
- **Likelihood:** Low (judge evaluates single factual answer; SE evaluates multi-sample semantic consistency — functionally distinct)
- **Affected Hypotheses:** H-M3 (AUROC under LM-judge interpretation affected)
- **Mitigation:**
  1. Prevention: Use cross-model judge (different model family from generator)
  2. Detection: Pre-experiment diagnostic — compute ρ(SE, LM-judge) before ensemble training; threshold < 0.4
  3. Response: If ρ > 0.4 → Run secondary ROUGE-L and BERTScore AUROC as primary metrics; reframe LM-judge results as auxiliary

**Risk R3 (from A3): Temperature Diversity Insufficient (SE Degenerate)**
- **Source Assumption:** A3 — temp=0.7 produces sufficient SE diversity
- **Description:** If SE_variance ≈ 0, SE carries no signal.
- **Severity:** Low (already mitigated — h-e1 validated: fraction_degenerate=0.000, SE_variance=0.1522)
- **Likelihood:** Very Low
- **Affected Hypotheses:** H-E1, H-M1, H-M3
- **Mitigation:** Already validated. Monitor SE_variance on full 2500-sample run; abort if SE_variance < 0.05.

**Risk R4 (from A4): Ensemble Not Generalizable (Llama→Qwen Gap > 0.05)**
- **Source Assumption:** A4 — Ensemble generalizes Llama→Qwen (AUROC gap < 0.05)
- **Description:** If AUROC gap > 0.05 on TruthfulQA without weight refitting, the ensemble is model-specifically calibrated.
- **Severity:** Medium
- **Likelihood:** Medium (Qwen-2.5-7B has different architecture and training; feature distribution shift possible)
- **Affected Hypotheses:** H-M3 (cross-model transfer test)
- **Mitigation:**
  1. Prevention: Report calibration slope in addition to AUROC gap
  2. Detection: AUROC gap check as defined in P3
  3. Response: If gap > 0.05 → SCOPE — report as "Llama-3.1-8B-specific calibration"; recommend per-model retuning as future work

**Risk R5 (from A5): Prohibited Approaches Reintroduced**
- **Source Assumption:** A5 — No hidden-state SVD, no POS filtering, no EM label residualization
- **Description:** Inadvertent reintroduction of any prohibited approach reproduces known failures.
- **Severity:** High
- **Likelihood:** Very Low (explicit exclusion in all specifications)
- **Affected Hypotheses:** All
- **Mitigation:** Code review checklist: verify compute_signals.py uses only (1) min_logprob from greedy forward pass, (2) SE_N5 via jlko/semantic_uncertainty, (3) SelfCheckNLI via potsawee/selfcheckgpt. No hidden-state extraction. No EM labels.

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: High SE–min_logprob correlation | A1 | H-E1, H-M1, H-M3 | Critical |
| R2: Circularity (LM-judge) | A2 | H-M3 | High |
| R3: SE degenerate | A3 | H-E1, H-M1, H-M3 | Low (mitigated) |
| R4: Cross-model gap > 0.05 | A4 | H-M3 | Medium |
| R5: Prohibited approach reintroduced | A5 | All | High |

**Critical: 1 | High: 2 | Medium: 1 | Low: 1**

### 4.3 Baseline Failure Pattern Risks

| Baseline Limitation | Potential Risk | Mitigation |
|--------------------|----------------|------------|
| h-m1 AUROC ~0.825 under lexical correctness | Length bias may inflate/deflate ΔAUROC | LM-as-a-judge + length-matched subset + OLS residualization of UQ features |
| h-e1 TPU AUROC=0.975 (log-prob captures SNNE) | Likelihood saturation leaves no room for SE gain | Pre-register null result threshold; treat ΔAUROC < 0.025 as saturation finding |
| h-m2 SUPERSEDED (EM label residualization) | Risk of reintroducing EM/correctness label residualization | Explicit A5 exclusion; code review checklist |

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Root: Foundation]
    H-E1: SE–min_logprob Conditional Independence
    (Existence; no dependencies; MUST_WORK gate)
         │
         ▼ Gate 1: MUST PASS (|r| < 0.7 AND partial R² ≥ 0.02)
         │
[Level 1 — Core Mechanism: Algebraic Distinctness]
    H-M1: Conditional Independence in LR
    (Mechanism; depends on H-E1; MUST_WORK gate)
         │
         ▼ Gate 2a: MUST PASS (partial R² ≥ 0.02, p < 0.05)
         │
[Level 2 — Mechanistic Explanation: Orthogonality Zone]
    H-M2: Orthogonality Zone Hallucination Enrichment
    (Mechanism; depends on H-M1; SHOULD_WORK gate)
         │
         ▼ Gate 2b: SHOULD PASS (zone enrichment ≥ 10pp)
         │         [failure narrows scope but does not block H-M3]
[Level 3 — Primary Outcome: Ensemble AUROC]
    H-M3: Ensemble AUROC Gain & Cross-Model Transfer
    (Mechanism; depends on H-M1; MUST_WORK gate)
         │
         ▼ Gate 3: MUST PASS (ΔAUROC ≥ 0.025, CI > 0)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M3
Optional Path: H-E1 → H-M1 → H-M2 → H-M3 (H-M2 parallel to H-M3)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 2 | H-M3 | H-M1 | MUST_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2     │ W3-4     │ W5       │ W6
─────────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation
  H-E1               │ ████████ │          │          │
  [Gate 1]           │        ◆ │          │          │
─────────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Mechanisms
  H-M1               │          │ ████████ │          │
  H-M2               │          │          │ ████████ │
  H-M3               │          │          │ ████████ │
  [Gate 2]           │          │          │          │ ◆
─────────────────────┼──────────┼──────────┼──────────┼──────────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Note: H-M2 and H-M3 are computed from same features (Week 5 concurrent)
Total Duration: 6 weeks
Critical Path: H-E1 → H-M1 → H-M3 = 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

- **Critical Path:** H-E1 → H-M1 → H-M3
- **Total Duration:** 6 weeks (2 + 2 + 2; H-M2 concurrent with H-M3 in Week 5)
- **Slack:** 0 weeks (all critical-path steps sequential)
- **Parallelization:** H-M2 and H-M3 analysis can be computed concurrently from same feature set in Week 5

### 5.5 Resource Summary

| Resource | Specification |
|----------|---------------|
| Total Hypotheses | 4 (H-E1, H-M1, H-M2, H-M3) |
| Verification Phases | 2 (Foundation + Mechanisms) |
| Total Duration | 6 weeks |
| MCP Calls Used | 4 (2 inquiries × 2 stages) |
| Infrastructure Reuse | h-e1 generate.py + compute_signals.py (no reimplementation) |
| Compute | Llama-3.1-8B inference (TriviaQA 2500 × 6 passes); Qwen-2.5-7B (TruthfulQA N=5) |

### 5.6 Execution Order

1. **Step 1**: Execute H-E1 (Weeks 1-2) — load h-e1 checkpoint; compute SE_N5 + min_logprob; run pre-experiment diagnostics
2. **Step 2**: Evaluate Gate 1 (end of Week 2) — if |r| > 0.85, ABANDON; if |r| < 0.7 AND partial R² ≥ 0.02, proceed
3. **Step 3**: Execute H-M1 (Weeks 3-4) — fit conditional LR with 5-fold CV; compute partial R² via LRT
4. **Step 4**: Execute H-M2 + H-M3 concurrently (Week 5) — orthogonality zone slice + ensemble AUROC + length-matched bootstrap
5. **Step 5**: Evaluate Gate 2 (end of Week 6) — ΔAUROC ≥ 0.025 CI check; cross-model transfer; correctness-function sweep
6. **Final**: Verification complete → Phase 4.5 Synthesis or null-result documentation

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** SE_N5 (entropy over semantic class masses from N=5 stochastic samples) provides conditionally independent uncertainty signal beyond min_logprob (minimum token probability on greedy path), enabling a logistic regression ensemble to achieve ΔAUROC ≥ 0.025 on TriviaQA dev under LM-as-a-judge correctness.

**Supporting Evidence:**
1. Algebraic distinctness: SE marginalizes over semantic class probability masses (Kuhn 2023 Eq. 3); min_logprob finds weakest prediction point in single decode — mathematically distinct operations
2. NLI-based scorers empirically best black-box UQ in 13/24 scenarios (UQLM, Bouchard 2025) — SE-family methods competitive
3. h-e1 validation: SE non-degenerate (SE_variance=0.1522), confirming informative signal exists at temp=0.7
4. Validated h-e1 infrastructure enables feasible PoC without reimplementation risk

**Strengths:**
- Mechanistically motivated orthogonality (not just hoped-for empirical correlation)
- Pre-registered falsification criteria reduce p-hacking risk
- Meaningful regardless of sign: positive validates SE independence; negative establishes likelihood saturation

**Expected Outcomes:**
- P1: AUROC ≥ 0.85, ΔAUROC ≥ 0.025 (95% CI lower bound > 0)
- P2: Partial R²(SE) ≥ 0.02, β₂ significant p < 0.05
- P3: Cross-model AUROC gap < 0.05 (Llama→Qwen)

### 6.2 Antithesis

**Null Hypothesis (H0):** No significant AUROC difference between min_logprob baseline and [min_logprob + SE_N5] ensemble. SE does not provide conditionally independent uncertainty signal — ΔAUROC = 0, 95% CI overlapping zero.

**Counter-Arguments:**
1. Likelihood saturation: TPU AUROC=0.975 from h-e1 suggests log-prob may already capture SNNE-based uncertainty near-perfectly on TriviaQA short-answer QA — leaving near-zero room for SE's independent contribution
2. Architectural similarity: DeBERTa-MNLI NLI clustering processes the same token sequences as greedy decode; high |r| possible despite algebraic distinction
3. Short-answer domain limit: TriviaQA short answers (1-10 tokens) may produce low SE diversity (few semantic equivalence classes possible for 1-token answers)

**Potential Failure Points:**
- R1: High correlation (|r| > 0.7) collapses the entire chain
- R2: Circularity (ρ(SE, LM-judge) > 0.4) inflates apparent AUROC gain
- AUROC ceiling: Existing min_logprob AUROC ~0.825 leaves limited headroom to reach 0.85 threshold

**Conditions Under Which H0 Would Be Supported:**
- Pearson |r|(SE, min_logprob) > 0.85
- Partial R²(SE) < 0.01 in conditional LR
- ΔAUROC 95% CI overlaps zero on length-matched subset
- Sign of ΔAUROC flips under ROUGE-L or BERTScore

### 6.3 Synthesis

The verification plan addresses this dialectic through sequential hypothesis testing with gate conditions at each causal step:

- **H-E1** tests empirical independence before committing to ensemble training
- **H-M1** operationalizes mechanism via conditional LR partial R² (not just AUROC)
- **H-M2** provides mechanistic explanation independent of AUROC metric
- **H-M3** delivers the primary empirical claim with three layers of length-bias control

**Resolution Path:** Gate 1 (H-E1) acts as an early-exit for the antithesis: if |r| > 0.85, the hypothesis collapses before any ensemble is built, and the null result is cleanly documented. If H-E1 passes, H-M3's null result would establish likelihood saturation on TriviaQA short-answer QA — equally publishable.

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M1 + H-M3 all pass → Thesis validated; ensemble benchmarked on TriviaQA/TruthfulQA with open-weight LLMs
2. **Partial Support:** H-E1 + H-M1 pass but ΔAUROC < 0.025 → Mechanism confirmed (conditional independence holds) but effect too small for practical gain at N=5; recommend N=10 ablation
3. **No Support:** H-E1 fails (|r| > 0.85) → Likelihood saturation established; SE is log-prob reparameterization on TriviaQA short-answer QA
4. **H-M2 only fail:** Orthogonality zone not enriched but ΔAUROC passes → Mechanism is real but operates differently than expected; reframe as empirical finding without mechanistic zone explanation

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Algebraic Independence | SE and min_logprob are distinct by formula | May correlate empirically on short-answer QA | H-E1 Pearson r test; partial R² in conditional LR |
| Orthogonality Zone | High confidence + high SE = hallucination enrichment | Zone may be too sparse or not enriched | H-M2 slice analysis with bootstrap CI |
| AUROC Gain | ΔAUROC ≥ 0.025 with length-matched CI | Likelihood saturation from h-e1 (TPU 0.975) | H-M3 nested CV + length-matched subset |
| Generalizability | Llama→Qwen transfer without refitting | Feature distribution shift across model families | P3 cross-model transfer test with calibration slope |
| Evaluation Bias | LM-as-a-judge with cross-model judge | Judge may share NLI reasoning with SE | Pre-experiment circularity diagnostic + ROUGE-L/BERTScore sweep |

**Overall Robustness Score:** Medium-High (5 bias controls; 3 layers of length control; pre-registered falsification criteria; meaningful null result treatment)

**Confidence in Verification Plan:** 0.72

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-SE-Ensemble-v1 — SE_N5 + min_logprob ensemble achieves ΔAUROC ≥ 0.025 on TriviaQA dev (LM-as-a-judge, length-matched), because SE and min_logprob are conditionally independent (partial R² ≥ 0.02).
- ID: H-SE-Ensemble-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (50% scope reduction from BUILD_ON established facts)
- Sub-Hypotheses: 4 total (H-E1 + H-M1 + H-M2 + H-M3)
- Phases: 2 over 6 weeks
- Critical Gates: 3 decision points (Gate 1 after H-E1; Gates 2a/2b/3 after mechanisms)

**Risk Assessment:** Medium
- Primary concerns: (1) Likelihood saturation — |r|(SE, min_logprob) may be high on TriviaQA short-answer QA; (2) Circularity — ρ(SE, LM-judge) requires pre-experiment diagnostic

**Immediate Action:** Begin Phase 1 with H-E1 — load h-e1 checkpoint, run pre-experiment diagnostics

### 7.2 Conclusions

**Key Achievements:**
- 4 sub-hypotheses across 2 phases with 3 gate conditions
- H0 addressed: "Likelihood saturation on TriviaQA — SE does not add independent signal"
- 50% scope reduction: 3 BUILD_ON facts excluded from re-verification
- h-e1 infrastructure directly reusable (no reimplementation)

**Verification Execution Order:**

**Phase 1: Foundation** (Weeks 1-2)
- H-E1: Pre-experiment diagnostics + conditional LR partial R² test
- Gate 1: MUST PASS — |r| < 0.7 AND partial R² ≥ 0.02

**Phase 2: Core Mechanisms** (Weeks 3-6)
- H-M1: Conditional LR with 5-fold CV (Weeks 3-4); Gate 2a: MUST PASS
- H-M2: Orthogonality zone slice analysis (Week 5); Gate 2b: SHOULD PASS
- H-M3: Ensemble AUROC + length-matched CI + cross-model transfer (Week 5-6); Gate 3: MUST PASS

**Critical Decision Points:**

1. **Gate 1 (H-E1 Foundation):**
   - FAIL (|r| > 0.85): ABANDON — report likelihood saturation; SE is log-prob reparameterization
   - PASS: Proceed to Phase 2

2. **Gate 2a (H-M1 Mechanism):**
   - CRITICAL FAIL (partial R² < 0.01): PIVOT — N=10 ablation or SelfCheckNLI substitute
   - MARGINAL (0.01 ≤ partial R² < 0.02): EXPLORE — proceed with caveat
   - PASS: Proceed to H-M2 + H-M3

3. **Gate 3 (H-M3 Ensemble AUROC):**
   - NULL RESULT (ΔAUROC < 0.025): Report as "Likelihood saturation on TriviaQA short-answer QA" — publishable finding
   - PASS: Proceed to Phase 4.5 Synthesis

**Open Questions (from Phase 2A):**
- Is the orthogonality zone (min_logprob ≥ 0.8 + SE top quartile) enriched for errors (≥10pp above base rate)?
- Does the circularity concern (ρ(SE, LM-judge) > 0.4) materialize?
- Does the 2-feature ensemble capture ≥95% of the full 5-feature ensemble gain?
- Is there an N-efficiency breakeven (N=3 vs N=5) for TriviaQA short answers?

**Recommendations:**
1. **Immediate:** Start Phase 1 with H-E1; run pre-experiment diagnostics before ensemble training
2. **Resource:** Allocate 6 weeks for critical path; reuse h-e1 infrastructure to save 1-2 weeks of setup
3. **Failure Management:** Document all gate results; pre-register null result treatment; sign-stability sweep as mandatory correctness-function check

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-SE-Ensemble-v1)
- Generated: 2026-08-02T15:45:00Z; convergence at exchange 15/15

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (mcp__clearThought__scientificmethod)
  - Call 1: H-E1-verification hypothesis stage
  - Call 2: H-E1-verification experiment stage
  - Call 3: H-M-integrated hypothesis stage
  - Call 4: H-M-integrated experiment stage
