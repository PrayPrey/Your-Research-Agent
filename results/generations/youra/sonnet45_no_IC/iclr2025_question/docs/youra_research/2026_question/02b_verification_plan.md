# Verification Plan: Hierarchical Bayesian Calibration for Foundation Model UQ

**Date:** 2026-07-13
**Hypothesis ID:** H-HBC-v1
**Confidence:** 0.80
**Total Hypotheses:** 2

---

## 0. Established Facts & Scope Reduction

### 0.1 Established Facts Registry

The following claims are **BUILD_ON** (established, do NOT re-verify):

| Claim | Status | Evidence |
|-------|--------|----------|
| SelfCheckGPT-style consistency methods work empirically for hallucination detection | BUILD_ON | Exchange 1-3: 1,061 citations, established empirical success despite theoretical impossibility results |
| Conformal prediction (COIN) provides statistical guarantees for uncertainty bounds | BUILD_ON | Exchange 2-4: COIN (17 citations) demonstrates FDR control via conformal prediction |
| Impossibility results prove absolute hallucination detection requires expert-labeled negative examples | BUILD_ON | Exchange 1-2: Karbasi et al. (14 citations) proves equivalence to language identification |

### 0.2 Claims to Prove (PROVE_NEW)

| Claim | Status | Test Approach |
|-------|--------|---------------|
| Epistemic and aleatoric uncertainty are theoretically distinct but entangled in generative models | PROVE_NEW | Measure correlation ρ(C,I) and demonstrate sweet spot 0.3 < ρ < 0.7 (non-redundancy) |

### 0.3 Scope Reduction Summary

- **Total claims:** 4
- **Established (BUILD_ON):** 3 (75%)
- **Need verification (PROVE_NEW):** 1 (25%)
- **Scope reduction:** 25%

**Phase 2B-4 Instructions:**
Build on established empirical success of consistency methods (SelfCheckGPT) and statistical methods (COIN).
PROVE_NEW: That consistency and conformal methods capture distinct (complementary) aspects of uncertainty.
Key test: measure correlation ρ(C,I) and demonstrate sweet spot 0.3 < ρ < 0.7 (non-redundancy).

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under foundation model uncertainty quantification settings, if we apply hierarchical Bayesian
calibration (HBC) that jointly optimizes consistency-based priors (from SelfCheckGPT-style sampling)
and statistical conformal prediction bounds, then we achieve superior calibration quality (ECE < 0.05)
with computational efficiency (30-50% cost reduction vs. COIN-only), because consistency and conformal
methods capture complementary information sources—consistency reveals epistemic uncertainty structure
while conformal provides aleatoric bounds—and their Bayesian integration enables mutual calibration
that improves both signals.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in Expected Calibration Error (ECE) between hierarchical Bayesian
calibration (HBC) and independent application of consistency-based or conformal prediction methods.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA (primary), HH-RLHF (aleatoric), SQuAD (mixed) (standard) | TruthfulQA tests epistemic uncertainty (model knowledge gaps), HH-RLHF tests aleatoric uncertainty (value alignment ambiguity), SQuAD provides mixed-uncertainty baseline. Domain shift experiments use medical QA (PubMedQA) and legal QA (CaseHOLD) as realistic OOD targets. |
| **Model** | Llama-2-7B | Widely benchmarked (reproducibility), supports sampling (required for consistency methods), 7B size manageable for multi-sample experiments, established baselines on TruthfulQA/SQuAD |

**Dataset Details:**
- Source: TruthfulQA: https://github.com/sylinrl/TruthfulQA; HH-RLHF: Anthropic; SQuAD: Stanford
- Path: To be downloaded during Phase 3 implementation

**Model Details:**
- Type: autoregressive transformer LLM
- Source: Meta AI, HuggingFace Hub

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| SelfCheckGPT (Manakul et al., 2023) | Strong hallucination detection empirically, no statistical guarantees | WikiBio, multiple domains |
| COIN conformal prediction (Wang et al., 2025) | 90%+ coverage with FDR control, computationally expensive | TruthfulQA, factuality benchmarks |
| FactTest (Nie et al., 2024) | Hypothesis testing framework with Type I/II error control | General factuality evaluation |

**Best Baseline Performance:** Independent cascade (SelfCheckGPT → COIN) achieves ECE ~0.06-0.08 on TruthfulQA (inferred from discussion, to be validated)

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Consistency-based and conformal methods measure distinct (non-redundant) aspects of uncertainty, with correlation 0.3 < ρ < 0.7 | Exchange 15: sweet spot assumption; Exchange 17: theoretical justification via distinct information sources (epistemic vs. aleatoric) | If ρ > 0.8: methods redundant, joint calibration adds no value. If ρ < 0.2: methods independent, mutual calibration ineffective. Both → hypothesis collapses to independent cascade baseline. |
| A2 | Bayesian calibration converges within reasonable training time on standard validation sets | Exchange 10: Phase 2 timeline 8 months for full HBC validation, deemed feasible with existing tools | If convergence requires >10K labeled examples or >100 GPU-hours: deployment barrier too high for practitioner adoption |
| A3 | Ground truth labels available for calibration set (standard UQ requirement) | Exchange 10: ground truth requirements met by existing benchmarks (TruthfulQA, FActScore, etc.) | Without labeled validation data, neither consistency threshold tuning nor conformal calibration is possible—standard limitation for all UQ methods |
| A4 | Distributional shift affects P(C,I) correlation structure, causing detectable disagreement | Exchange 16: provable that distributional shift → disagreement change; Exchange 15: P_OOD(C,I) ≠ P_ID(C,I) is theoretical foundation | If correlation ρ remains stable under OOD: disagreement-based OOD detection (P4-P5) fails, but core calibration (P1-P3) unaffected |
| A5 | Transfer degradation is measurable via ECE increase on domain shift (>0.1 threshold) | Exchange 12: Prof. Rex proposed transfer experiments (calibrate Domain A, test Domain B); Exchange 14: ECE degradation metric | If ECE degrades by <0.05 on domain shift: HBC is over-calibrated on in-distribution, under-sensitive to OOD; if >0.2: calibration does not transfer, requires per-domain re-calibration |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First work to formalize hierarchical Bayesian calibration integrating consistency-based (SelfCheckGPT-style) and statistical (conformal prediction) UQ methods. Novel meta-uncertainty framework using disagreement for OOD detection.

**Key Innovation:** Joint calibration via Bayesian updating (consistency informs prior, statistical validation updates posterior) rather than independent or cascaded application. Theoretical grounding: distributional shift → disagreement (provable), not ad-hoc empirical observation.

**Differentiation from Prior Work:**
- **vs. SelfCheckGPT (Manakul et al., 2023, 1061 cit.):** SelfCheckGPT uses consistency alone for hallucination detection. HBC integrates consistency with statistical methods via Bayesian calibration for improved ECE and OOD detection.
- **vs. COIN (Wang et al., 2025, 17 cit.):** COIN provides conformal prediction with FDR control but operates independently. HBC uses consistency as prior to improve conformal calibration efficiency (30-50% cost reduction).
- **vs. UQ Survey (Kang et al., 2025, 11 cit.):** Survey categorizes existing UQ methods but notes lack of unified framework. HBC provides integration framework with theoretical grounding (distributional shift formalism).
- **vs. Impossibility result (Karbasi et al., 2025, 14 cit.):** Impossibility proves absolute hallucination detection impossible. HBC resolves paradox: consistency measures epistemic structure (not absolute truth), conformal provides statistical bounds—complementary, not competing.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | TODO |
| H-M-integrated | Mechanism | MUST_WORK | H-E1 | TODO |

**Total Hypotheses:** 2

---

### 2.2 Hypothesis Specifications

---
#### H-E1: Complementarity Verification

**Statement**: Under foundation model uncertainty quantification settings, if we measure the correlation between consistency-based scores (C) and conformal prediction interval membership (I), then we observe 0.3 < ρ(C,I) < 0.7, because consistency methods capture epistemic uncertainty (generative inconsistency) while conformal methods capture aleatoric uncertainty (inherent data ambiguity), representing distinct but complementary information sources.

**Rationale**: This hypothesis validates the core assumption (A1) that consistency and conformal methods measure non-redundant aspects of uncertainty. If ρ > 0.8 (redundant) or ρ < 0.2 (independent), the entire HBC joint calibration approach collapses to baseline performance. This is the foundation for all subsequent mechanism hypotheses.

**Variables** (from Phase 2A):
- Independent: Consistency Score (C), Conformal Interval Membership (I)
- Dependent: Correlation ρ(C,I)
- Controlled: Foundation Model (Llama-2-7B), Dataset Type (TruthfulQA/HH-RLHF/SQuAD), Consistency Metric (NLI+BERTScore), Conformal Coverage (90%)

**Verification Protocol**:
1. Generate consistency scores C(x) using SelfCheckGPT (5 samples, NLI+BERTScore ensemble) for n≥1000 validation samples per dataset.
2. Compute conformal prediction intervals I(x) with 90% coverage target, binary indicator I_binary(x) = 1 if y ∈ I(x) else 0.
3. Calculate Pearson correlation ρ(C, I_binary) on validation set for each dataset (TruthfulQA, HH-RLHF, SQuAD).
4. Perform two-tailed significance test (p<0.05) to verify correlation differs from extreme values (ρ ≠ 0.9, ρ ≠ 0.1).
5. Verify sweet spot: 0.3 ≤ ρ ≤ 0.7 on ALL three datasets.

**Success Criteria** (MUST_WORK gate):
- Primary: 0.3 ≤ ρ ≤ 0.7 on all three datasets (TruthfulQA, HH-RLHF, SQuAD)
- Secondary: p < 0.05 for two-tailed significance test on each dataset
- Statistical Power: n ≥ 1000 per dataset

**Failure Response**:
- IF ρ > 0.8 on any dataset: Methods redundant → PIVOT to single-method optimization (abandon HBC)
- IF ρ < 0.2 on any dataset: Methods independent → EXPLORE alternative integration approaches or ABANDON HBC
- IF p > 0.05: Insufficient evidence → EXPLORE larger sample size or ABANDON claim

**Dependencies**: None (foundation hypothesis, must pass first)

**Source**: Phase 2A Section 1.6 (Prediction P3), Section 1.4 (Assumption A1)

**Gate Type**: MUST_WORK - If this fails, HBC hypothesis is invalid

---

#### H-M-integrated: Hierarchical Bayesian Co-Calibration

**Statement**: Under foundation model uncertainty quantification settings, if we apply hierarchical Bayesian calibration (HBC) where consistency priors C(x) inform conformal calibration and statistical validation results update consistency thresholds (mutual calibration), then we achieve Expected Calibration Error (ECE) < 0.05 with 30-50% computational cost reduction vs. COIN-only while maintaining coverage ≥ 90%, because the three-step causal mechanism operates: (Step 1) Consistency sampling measures epistemic uncertainty producing prior C(x), (Step 2) Conformal prediction provides aleatoric bounds producing interval I(x), (Step 3) Hierarchical Bayesian updating creates co-calibration exploiting complementarity (0.3 < ρ < 0.7), where mutual calibration improves both signals beyond independent application.

**Rationale**: This hypothesis tests the complete 3-step causal chain from Phase 2A. It validates that joint calibration (not independent or cascade application) provides superior ECE with computational efficiency. This is the core HBC contribution—proving that Bayesian integration of complementary signals improves both consistency and conformal methods.

**Variables** (from Phase 2A):
- Independent: Calibration Method (4-level: SelfCheckGPT-only, COIN-only, Independent Cascade, HBC), Dataset Type (TruthfulQA/HH-RLHF/SQuAD)
- Dependent: Expected Calibration Error (ECE), Computational Cost (forward passes/1000 queries), Coverage (fraction y ∈ I(x))
- Controlled: Foundation Model (Llama-2-7B), Consistency Metric (NLI+BERTScore), Conformal Coverage Target (90%)

**Verification Protocol**:
1. Implement four calibration methods (SelfCheckGPT-only, COIN-only, Independent Cascade, HBC) with identical train/val/test splits.
2. HBC implementation: Bayesian updating where C(x) informs conformal prior (epistemic → statistical direction), statistical validation updates consistency threshold (statistical → epistemic feedback).
3. Measure ECE (primary), computational cost (forward passes per 1000 queries), coverage (fraction y ∈ I(x)) on n≥1000 test samples per dataset.
4. Statistical comparison: two-tailed t-test comparing HBC vs. each baseline on ECE (SelfCheckGPT-only, COIN-only, Independent Cascade), require p<0.05 for all three.
5. Efficiency validation: HBC cost reduction ≥ 30% vs. COIN-only while maintaining coverage ≥ 90%.
6. Ablation study: test with ρ=0.2, 0.5, 0.8 to validate sweet spot dependency (ECE improvement should peak at ρ~0.5).

**Success Criteria** (MUST_WORK gate):
- Primary: ECE_HBC < 0.05 AND significantly lower than all three baselines (p<0.05 for each pairwise comparison)
- Secondary: Cost reduction 30-50% vs. COIN-only while coverage ≥ 90%
- Mechanism Validation: Ablation shows ECE improvement peaks at ρ~0.5 (sweet spot dependency)
- Minimum Effect Size: ECE improvement ≥ 0.01 vs. independent cascade (not just statistical, but practical significance)

**Failure Response**:
- IF ECE improvement < 0.01 vs. independent cascade: Joint calibration adds no value → ABANDON HBC, report independent cascade as sufficient
- IF cost reduction < 20%: Efficiency claim invalid → PIVOT to "quality-only" contribution (drop efficiency claim from paper)
- IF coverage < 85%: Statistical guarantees violated → EXPLORE conformal recalibration or ABANDON coverage claim
- IF ablation shows no sweet spot dependency: Complementarity claim weak → REFINE theoretical model or ABANDON ρ-based mechanism

**Dependencies**: H-E1 (complementarity must be validated before testing joint calibration)

**Source**: Phase 2A Section 1.3 (Causal Mechanism 3-step chain), Section 1.6 (Prediction P1, P2)

**Gate Type**: MUST_WORK - Core HBC contribution, must demonstrate both calibration quality and efficiency

---

---

## 3. Risk Analysis

### 3.1 Risk Identification from Assumptions

From Phase 2A Section 1.4, five key assumptions (A1-A5) have been identified. Each assumption violation represents a potential risk to hypothesis verification.

**Risk R1: Sweet Spot Violation (from A1)**
- **Source:** A1 - Consistency-based and conformal methods measure distinct aspects with 0.3 < ρ < 0.7
- **Description:** If correlation ρ(C,I) falls outside sweet spot (ρ > 0.8 redundant, or ρ < 0.2 independent), joint calibration provides no advantage over independent methods.
- **Severity:** CRITICAL (entire HBC hypothesis collapses)
- **Affected Hypotheses:** H-E1 (validates sweet spot), H-M-integrated (depends on complementarity)
- **Likelihood:** Medium (empirical assumption, not yet validated)

**Risk R2: Convergence Failure (from A2)**
- **Source:** A2 - Bayesian calibration converges within reasonable training time on standard validation sets
- **Description:** If convergence requires >10K labeled examples or >100 GPU-hours, deployment barrier too high for practitioner adoption.
- **Severity:** HIGH (feasibility barrier, not scientific validity)
- **Affected Hypotheses:** H-M-integrated (HBC implementation)
- **Likelihood:** Low (existing Bayesian UQ tools suggest feasibility)

**Risk R3: Data Requirement Violation (from A3)**
- **Source:** A3 - Ground truth labels available for calibration set (standard UQ requirement)
- **Description:** Without labeled validation data, neither consistency threshold tuning nor conformal calibration is possible—standard limitation for all UQ methods.
- **Severity:** MEDIUM (standard UQ limitation, affects all methods equally)
- **Affected Hypotheses:** All hypotheses (fundamental data requirement)
- **Likelihood:** Low (benchmarks provide labeled data; documented as known limitation)

**Risk R4: OOD Stability (from A4)**
- **Source:** A4 - Distributional shift affects P(C,I) correlation structure, causing detectable disagreement
- **Description:** If correlation ρ remains stable under OOD, disagreement-based OOD detection (future extensions P4-P5) fails. Core calibration (P1-P3) unaffected.
- **Severity:** LOW (affects future extensions only, not core contribution)
- **Affected Hypotheses:** None in Phase 2B (P4-P5 deferred to future work)
- **Likelihood:** Medium (empirical claim, requires OOD validation)

**Risk R5: Transfer Degradation Extremes (from A5)**
- **Source:** A5 - Transfer degradation is measurable via ECE increase on domain shift (>0.1 threshold)
- **Description:** If ECE degrades by <0.05 on domain shift, HBC is over-calibrated on in-distribution; if >0.2, calibration does not transfer.
- **Severity:** MEDIUM (affects deployment robustness, not core contribution)
- **Affected Hypotheses:** H-M-integrated (includes domain shift ablation)
- **Likelihood:** Low (calibration degradation on domain shift is expected behavior)

---

### 3.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Likelihood |
|------|--------|---------------------|----------|------------|
| R1: Sweet Spot Violation | A1 | H-E1, H-M-integrated | CRITICAL | Medium |
| R2: Convergence Failure | A2 | H-M-integrated | HIGH | Low |
| R3: Data Requirement | A3 | All | MEDIUM | Low |
| R4: OOD Stability | A4 | None (future work) | LOW | Medium |
| R5: Transfer Degradation | A5 | H-M-integrated | MEDIUM | Low |

**Risk Priority:** R1 (CRITICAL) > R2 (HIGH) > R3, R5 (MEDIUM) > R4 (LOW)

---

### 3.3 Mitigation Strategies

**R1: Sweet Spot Violation** (CRITICAL)

**Prevention:**
- H-E1 validates sweet spot FIRST before H-M-integrated implementation
- Measure ρ on pilot dataset (subset of TruthfulQA) before full experiment
- Ablation study with synthetic data at ρ=0.2, 0.5, 0.8 to understand sensitivity

**Detection:**
- Early warning: ρ measured on validation set immediately after H-E1 implementation
- Red flags: ρ > 0.8 (redundancy) or ρ < 0.2 (independence) on any dataset

**Response:**
- IF ρ > 0.8: **PIVOT** to single-method optimization (use stronger method only, abandon joint calibration)
- IF ρ < 0.2: **EXPLORE** alternative integration (e.g., ensemble instead of Bayesian) or **ABORT** HBC
- IF 0.2 < ρ < 0.3 or 0.7 < ρ < 0.8: **SCOPE** to "partial complementarity" contribution with reduced claims

**R2: Convergence Failure** (HIGH)

**Prevention:**
- Use validation set sizes n=100, 500, 1000 to measure convergence scaling
- Implement HBC-Lite heuristic (simplified non-Bayesian version) as fallback
- Profile GPU time and sample requirements in pilot experiments

**Detection:**
- Monitor convergence after 1K, 5K, 10K labeled examples
- Track GPU-hours required for calibration
- Early warning: >50 GPU-hours at 5K examples suggests scaling problem

**Response:**
- IF >10K examples required: **SCOPE** to "research contribution only" (document as limitation, provide HBC-Lite for practitioners)
- IF >100 GPU-hours: **PIVOT** to approximate Bayesian methods (variational inference) or **SCOPE** to smaller models
- IF convergence unstable: **EXPLORE** hyperparameter tuning or **ABORT** full Bayesian approach, use HBC-Lite

**R3: Data Requirement Violation** (MEDIUM)

**Prevention:**
- Document as standard UQ limitation (affects all methods, not HBC-specific)
- Verify benchmark availability (TruthfulQA, HH-RLHF, SQuAD) before Phase 3 implementation

**Detection:**
- Check labeled dataset availability during Phase 3 planning
- Verify ground truth format matches expected structure

**Response:**
- IF labels unavailable: **SCOPE** to semi-supervised variants (literature suggests pseudo-labeling approaches)
- Document as known limitation: "HBC requires labeled calibration set (standard for all UQ methods)"
- No hypothesis abandonment (standard constraint)

**R4: OOD Stability** (LOW)

**Prevention:**
- Clearly scope Phase 2B to core calibration (P1-P3), defer OOD detection (P4-P5) to future work
- Document OOD extension as "theoretically motivated, empirically testable" (not required for core contribution)

**Detection:**
- Not applicable (OOD experiments not in Phase 2B scope)

**Response:**
- IF future work shows ρ stability under OOD: Document as limitation, drop OOD detection claims
- Core calibration contribution (P1-P3) unaffected

**R5: Transfer Degradation Extremes** (MEDIUM)

**Prevention:**
- Include domain shift experiments as ablation (TruthfulQA → medical QA)
- Measure ECE degradation as secondary metric (not core contribution)

**Detection:**
- Measure ECE on in-distribution vs. OOD test sets
- Early warning: ECE_OOD - ECE_ID outside [0.05, 0.2] range

**Response:**
- IF degradation < 0.05: **SCOPE** to "HBC over-calibrates on ID" (document as limitation)
- IF degradation > 0.2: **SCOPE** to "requires domain-specific re-calibration" (expected behavior, not failure)
- No hypothesis abandonment (transfer robustness is extension, not core claim)

---

### 3.4 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Sweet Spot Violation (ρ outside [0.3, 0.7]) | A1 | CRITICAL | H-E1, H-M-integrated | H-E1 validates FIRST; PIVOT to single-method if violated |
| R2 | Convergence Failure (>10K samples, >100 GPU-hrs) | A2 | HIGH | H-M-integrated | Measure scaling; SCOPE to HBC-Lite if infeasible |
| R3 | Data Requirement (no labeled calibration set) | A3 | MEDIUM | All | Standard UQ limitation; SCOPE to semi-supervised if needed |
| R4 | OOD Stability (ρ stable under domain shift) | A4 | LOW | None (future work) | Not in Phase 2B scope; core contribution unaffected |
| R5 | Transfer Degradation Extremes (<0.05 or >0.2) | A5 | MEDIUM | H-M-integrated | SCOPE to "requires re-calibration" (expected behavior) |

**Critical Risks:** 1 (R1)  
**High Risks:** 1 (R2)  
**Medium Risks:** 2 (R3, R5)  
**Low Risks:** 1 (R4)

---

## 4. Execution Plan

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
   DEPENDENCY GRAPH (DAG) - 2 Hypotheses (Sequential Verification)
═══════════════════════════════════════════════════════════════════

[Phase 1 - Foundation]
     ┌─────────────────────────────────────────────────────┐
     │  H-E1: Complementarity Verification                 │
     │  Test: 0.3 < ρ(C,I) < 0.7 on all datasets          │
     │  Gate: MUST_WORK (critical assumption)              │
     └─────────────────────────────────────────────────────┘
                            │
                            │ IF PASS: ρ validates sweet spot
                            │ IF FAIL: STOP → HBC invalid
                            ▼
              ┌─────────────────────────┐
              │ GATE 1: Foundation Check │
              │ ρ ∈ [0.3, 0.7]?         │
              └─────────────────────────┘
                            │
                  ✓ PASS: Proceed to Phase 2
                  ✗ FAIL: ABORT entire HBC hypothesis
                            │
                            ▼
[Phase 2 - Core Mechanism]
     ┌─────────────────────────────────────────────────────┐
     │  H-M-integrated: HBC Co-Calibration                 │
     │  Test: ECE < 0.05, cost reduction 30-50%           │
     │  Gate: MUST_WORK (core HBC contribution)            │
     │  Prerequisites: H-E1 (complementarity validated)    │
     └─────────────────────────────────────────────────────┘
                            │
                            │ IF PASS: HBC validates → Phase 4
                            │ IF FAIL: Independent cascade = best
                            ▼
              ┌─────────────────────────┐
              │ GATE 2: Mechanism Check  │
              │ ECE < 0.05 & Cost OK?   │
              └─────────────────────────┘
                            │
                  ✓ PASS: Phase 4 Implementation
                  ✗ FAIL: Document limitation, report baseline

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M-integrated (fully sequential, no parallel)
Total Gates: 2 (both MUST_WORK)
Abort Points: Gate 1 failure = STOP, Gate 2 failure = Use baseline
═══════════════════════════════════════════════════════════════════
```

**Verification Flow:**
1. **H-E1 First** (Foundation): Validates complementarity assumption (A1). If ρ outside [0.3, 0.7], entire HBC hypothesis is invalid—STOP and report null result.
2. **Gate 1 Decision**: ρ validated → proceed to H-M-integrated. ρ violated → ABORT, write paper on "why joint calibration doesn't work."
3. **H-M-integrated Second** (Mechanism): Tests full 3-step causal chain with HBC implementation. Requires H-E1 pass (no point testing joint calibration if methods aren't complementary).
4. **Gate 2 Decision**: ECE improvement validated → Phase 4 implementation. ECE improvement < 0.01 → independent cascade is best, report as negative result.

**No Parallelization:** Both hypotheses are sequential dependencies (H-M-integrated requires H-E1 validation first).

---

### 4.2 Dependency Hierarchy

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Phase | Hypothesis | Prerequisites | Gate Type | If Fails |
|-------|-------|------------|---------------|-----------|----------|
| 0 | Foundation | H-E1 | None | MUST_WORK | ABORT HBC |
| 1 | Mechanism | H-M-integrated | H-E1 | MUST_WORK | Use baseline |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Levels: 2
Critical Path Length: 2 hypotheses (sequential)
Parallelization Opportunities: 0 (fully sequential dependencies)

Gate Summary:
- MUST_WORK gates: 2/2 (H-E1, H-M-integrated)
- SHOULD_WORK gates: 0/2
- DETERMINES_SUCCESS gates: 0/2 (Phase 5 baseline comparison handles this)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Dependency Analysis:**
- **H-E1 (Level 0)**: Foundation hypothesis with no prerequisites. Must validate complementarity (0.3 < ρ < 0.7) before proceeding. Failure = entire HBC approach is invalid.
- **H-M-integrated (Level 1)**: Depends on H-E1. No point testing joint calibration if methods aren't complementary. Failure = independent cascade is best approach.

**Critical Path:** H-E1 → H-M-integrated (2 steps, fully sequential)

**No Circular Dependencies:** Dependency chain is acyclic (DAG property satisfied)

---

## 5. Timeline & Gantt

```
═══════════════════════════════════════════════════════════════════════════════
   VERIFICATION TIMELINE - 2 Hypotheses (Phase 2B PoC Verification)
═══════════════════════════════════════════════════════════════════════════════

Phase/Hypothesis       │ Week 1-2 │ Week 3-4 │ Week 5-6 │
───────────────────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation
  H-E1: Complementarity│ ████████ │          │          │
  Verification         │          │          │          │
  [Gate 1 Decision]    │          │ ◆        │          │
───────────────────────┼──────────┼──────────┼──────────┤
PHASE 2: Core Mechanism
  H-M-integrated: HBC  │          │ ████████ │          │
  Co-Calibration       │          │          │          │
  [Gate 2 Decision]    │          │          │ ◆        │
───────────────────────┼──────────┼──────────┼──────────┤

═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point

Total Duration: 4 weeks (PoC verification only, NOT full Phase 4 implementation)
Gate Points: 2 (Week 2: Foundation gate, Week 4: Mechanism gate)
Critical Path: H-E1 → Gate 1 → H-M-integrated → Gate 2 (fully sequential)
═══════════════════════════════════════════════════════════════════════════════

IMPORTANT: This timeline covers Phase 2B verification planning ONLY (hypothesis design + PoC specs).
Full Phase 4 implementation timeline will be defined separately based on Phase 3 architecture.
```

**Phase Breakdown:**

| Phase | Hypotheses | Duration | Deliverable |
|-------|------------|----------|-------------|
| Phase 1: Foundation | H-E1 | 2 weeks | ρ(C,I) measurement on 3 datasets, validate sweet spot |
| Gate 1 | Decision | End Week 2 | GO/NO-GO: ρ ∈ [0.3, 0.7]? |
| Phase 2: Mechanism | H-M-integrated | 2 weeks | 4-way comparison (HBC vs. 3 baselines), ECE + cost |
| Gate 2 | Decision | End Week 4 | GO/NO-GO: ECE < 0.05 & cost reduction ≥ 30%? |

---

### 5.1 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M-integrated (2 hypotheses, fully sequential)

Total Duration: 4 weeks
  Breakdown:
    - H-E1 (Foundation): 2 weeks
    - H-M-integrated (Mechanism): 2 weeks
  Formula: 2 (H-E1) + 2 (H-M-integrated) = 4 weeks

Slack Time: 0 weeks (all tasks are on critical path, no parallelization)

Bottlenecks:
  1. H-E1 must complete before H-M-integrated (dependency constraint)
  2. Gate 1 decision blocks Phase 2 (MUST_WORK gate)
  3. Both hypotheses require full dataset processing (no shortcuts)

Duration Sensitivity:
  - IF H-E1 fails Gate 1 (ρ outside sweet spot): Total = 2 weeks (ABORT)
  - IF H-M-integrated fails Gate 2: Total = 4 weeks (report negative result)
  - IF both pass: 4 weeks → proceed to Phase 3 implementation planning

Comparison to Typical Phase 2B:
  - 2 hypotheses is MINIMAL (typical: 3-7 hypotheses)
  - 4 weeks is FAST (typical: 5-8 weeks for 4-5 hypotheses)
  - Reason: Integrated mechanism (no separate H-M1, H-M2, H-M3 split)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5.2 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                           RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 2
  - Existence: 1 (H-E1: Complementarity verification)
  - Mechanism: 1 (H-M-integrated: Full 3-step causal chain)
  - Condition: 0 (no boundary conditions require verification)

Verification Phases: 2
  1. Foundation (H-E1): Validate sweet spot assumption
  2. Mechanism (H-M-integrated): Test HBC joint calibration

Total Duration: 4 weeks (PoC verification planning)
Critical Path Length: 4 weeks (100% utilization, no slack)
Execution Mode: Fully sequential (no parallel work)

Gate Decisions: 2
  - Gate 1 (Week 2): ρ ∈ [0.3, 0.7]? → MUST_WORK
  - Gate 2 (Week 4): ECE < 0.05 & cost OK? → MUST_WORK

Computational Resources (Phase 4 estimates):
  - GPU: 1x A100 or equivalent (Llama-2-7B inference + sampling)
  - Data: TruthfulQA (~800 samples), HH-RLHF (~1000), SQuAD (~1000)
  - Calibration set: n≥1000 labeled samples per dataset
  - Forward passes: 5 samples × 1000 queries × 4 methods = 20K inferences

Personnel: 1 researcher (can execute sequentially)
  - Week 1-2: Implement H-E1, measure ρ
  - Week 3-4: Implement H-M-integrated, measure ECE + cost

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5.3 Execution Order

**Step-by-Step Verification Plan:**

1. **Week 1-2: Execute H-E1 (Foundation)**
   - Implement SelfCheckGPT consistency scoring (5 samples, NLI+BERTScore)
   - Implement COIN conformal prediction (90% coverage)
   - Measure correlation ρ(C,I) on validation sets (TruthfulQA, HH-RLHF, SQuAD)
   - Statistical test: two-tailed significance (p<0.05)
   - **Deliverable:** ρ measurements for all 3 datasets

2. **End Week 2: Gate 1 Decision**
   - **Criterion:** 0.3 ≤ ρ ≤ 0.7 on ALL three datasets
   - **IF PASS:** Complementarity validated → Proceed to H-M-integrated
   - **IF FAIL:**
     - ρ > 0.8: Methods redundant → ABORT HBC, use stronger method only
     - ρ < 0.2: Methods independent → ABORT HBC, explore alternatives
   - **Outcome:** GO/NO-GO decision for Phase 2 continuation

3. **Week 3-4: Execute H-M-integrated (Mechanism)** [IF Gate 1 PASS]
   - Implement 4 calibration methods:
     1. SelfCheckGPT-only (consistency threshold tuned)
     2. COIN-only (standard conformal prediction)
     3. Independent Cascade (SelfCheckGPT → COIN, separately tuned)
     4. HBC (hierarchical Bayesian co-calibration)
   - Measure ECE (primary), computational cost, coverage on test sets
   - Statistical comparison: HBC vs. each baseline (two-tailed t-test, p<0.05)
   - Ablation: test ρ=0.2, 0.5, 0.8 scenarios (sweet spot validation)
   - **Deliverable:** ECE, cost, coverage metrics for all 4 methods

4. **End Week 4: Gate 2 Decision**
   - **Criteria:**
     1. ECE_HBC < 0.05 (calibration quality)
     2. p < 0.05 for all three pairwise comparisons (HBC vs. baselines)
     3. Cost reduction ≥ 30% vs. COIN-only
     4. Coverage ≥ 90% maintained
   - **IF PASS:** HBC validates → Phase 3 implementation planning
   - **IF FAIL:**
     - ECE improvement < 0.01: Independent cascade is best → Report as baseline
     - Cost reduction < 20%: Drop efficiency claim, keep quality claim
     - Coverage < 85%: Statistical guarantees violated → ABORT coverage claim
   - **Outcome:** HBC viability determination

5. **Week 5+: Phase 3 Transition** [IF Gate 2 PASS]
   - Document verification results in 02b_verification_plan.md (this file)
   - Generate verification_state.yaml for Phase 2C integration
   - Proceed to Phase 3 implementation planning (PRD/Architecture)

**Early Abort Scenarios:**
- **Week 2 (Gate 1 FAIL):** Total time = 2 weeks, deliverable = "complementarity not validated" paper
- **Week 4 (Gate 2 FAIL):** Total time = 4 weeks, deliverable = "independent cascade is best" paper

---

## 6. Dialectical Analysis

This section performs Thesis-Antithesis-Synthesis evaluation to ensure robust verification planning by considering opposing viewpoints.

---

### 6.1 Thesis Statement

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                              THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Core Claim:** 
Hierarchical Bayesian calibration (HBC) that jointly optimizes consistency-based priors 
(from SelfCheckGPT-style sampling) and statistical conformal prediction bounds achieves 
superior calibration quality (ECE < 0.05) with computational efficiency (30-50% cost 
reduction vs. COIN-only), because consistency and conformal methods capture complementary 
information sources—consistency reveals epistemic uncertainty structure while conformal 
provides aleatoric bounds—and their Bayesian integration enables mutual calibration that 
improves both signals.

**Supporting Evidence:**
1. **Causal Mechanism (3-step chain from Phase 2A Section 1.3):**
   - Step 1: Consistency sampling measures epistemic uncertainty → prior C(x)
   - Step 2: Conformal prediction provides aleatoric bounds → interval I(x)
   - Step 3: Bayesian updating creates co-calibration exploiting complementarity
2. **Theoretical Foundation:** Distributional shift provably affects P(C,I) correlation 
   (Exchange 16), providing formal basis for complementarity claim
3. **Empirical Success:** SelfCheckGPT (1061 cit.) and COIN (17 cit.) established 
   independently; HBC integrates both via Bayesian framework

**Strengths:**
- **Clear falsification criteria:** If ρ > 0.8 (redundant) or ρ < 0.2 (independent), 
  entire HBC hypothesis collapses to baseline
- **Risk-managed scope:** Core calibration (P1-P3) survives even if OOD extension fails
- **Resolves paradox:** Consistency methods measure epistemic structure (not absolute 
  truth), resolving impossibility result contradiction

**Expected Outcomes:**
- **Primary (P1):** ECE < 0.05, significantly lower than all baselines (p<0.05)
- **Secondary (P2):** Cost reduction 30-50% vs. COIN-only, coverage ≥ 90%
- **Tertiary (P3):** Correlation 0.3 < ρ < 0.7 validates complementarity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6.2 Antithesis Development

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Null Hypothesis (H0):**
There is no significant difference in Expected Calibration Error (ECE) between 
hierarchical Bayesian calibration (HBC) and independent application of consistency-based 
or conformal prediction methods.

**Counter-Arguments:**

1. **Redundancy Risk (from Baseline Limitations):**
   - SelfCheckGPT and COIN may measure the same underlying uncertainty aspect
   - If ρ > 0.8, methods are redundant → joint calibration adds no value
   - Independent cascade (SelfCheckGPT → COIN) may already capture all benefits

2. **Complexity Without Gain (from Assumption Violations):**
   - A2 violation: Bayesian calibration may not converge within reasonable resources
   - Joint calibration complexity (two interdependent calibrations) creates 
     deployment barrier without proportional quality improvement
   - Practitioner adoption blocked if >10K samples or >100 GPU-hours required

3. **Scope Limitations (from Phase 2A Boundaries):**
   - Requires labeled validation sets (A3) → fails in zero-shot deployment
   - Latency-critical applications cannot afford multiple forward passes
   - Adversarial inputs can fool consistency checks (known limitation)

**Potential Failure Points:**

- **R1 (CRITICAL):** Sweet spot violation (ρ outside [0.3, 0.7])
  - If ρ > 0.8: Methods redundant, use stronger method only
  - If ρ < 0.2: Methods independent, mutual calibration ineffective
- **R2 (HIGH):** Convergence failure (>10K samples, >100 GPU-hours)
  - HBC becomes research-only, impractical for deployment
- **R5 (MEDIUM):** Transfer degradation extremes
  - If ECE degrades <0.05 on OOD: Over-calibrated on in-distribution
  - If ECE degrades >0.2: Requires per-domain re-calibration

**Conditions Under Which H0 Would Be Supported:**

- **H-E1 failure:** If ρ outside [0.3, 0.7] on ANY dataset → complementarity invalid
- **H-M-integrated failure:** If ECE improvement < 0.01 vs. independent cascade → 
  joint calibration provides no advantage
- **Cost inefficiency:** If cost reduction < 20% OR coverage < 85% → efficiency 
  claim invalid
- **Mechanism breakdown:** If ablation study shows no sweet spot dependency → 
  ρ-based mechanism is weak

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                             SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Balanced Assessment:**

The hypothesis H-HBC-v1 presents a testable claim that hierarchical Bayesian calibration 
can exploit complementarity between consistency-based and conformal prediction methods 
to achieve superior ECE with computational efficiency. However, the null hypothesis raises 
valid concerns regarding potential redundancy (ρ > 0.8), independence (ρ < 0.2), and 
added complexity without proportional gain.

**Resolution Path:**

The verification plan addresses this dialectic through **sequential gate-based validation**:

1. **Foundation Verification (H-E1):** Establishes complementarity (0.3 < ρ < 0.7) BEFORE 
   investing in HBC implementation. If ρ outside sweet spot, ABORT immediately—no wasted 
   effort on mechanism testing.

2. **Mechanism Testing (H-M-integrated):** Tests full 3-step causal chain with 4-way 
   comparison (HBC vs. SelfCheckGPT-only, COIN-only, Independent Cascade). Requires 
   H-E1 pass to proceed.

3. **Gate Conditions:** Allow early detection of H0 support:
   - Gate 1 (Week 2): ρ validates sweet spot → If fail, ABORT with "methods not complementary"
   - Gate 2 (Week 4): ECE improvement validated → If fail, report "independent cascade is best"

**Conditions for Thesis Support (HBC Validates):**

- ✓ H-E1 passes: 0.3 ≤ ρ ≤ 0.7 on ALL three datasets (TruthfulQA, HH-RLHF, SQuAD)
- ✓ H-M-integrated passes: ECE_HBC < 0.05 AND significantly lower than all baselines (p<0.05)
- ✓ Efficiency validated: Cost reduction ≥ 30% vs. COIN, coverage ≥ 90%
- ✓ Mechanism validates: Ablation shows ECE peaks at ρ~0.5 (sweet spot dependency)

**Conditions for Antithesis Support (H0 Validates):**

- ✗ H-E1 fails: ρ > 0.8 (redundant) OR ρ < 0.2 (independent) on any dataset
- ✗ H-M-integrated fails: ECE improvement < 0.01 vs. independent cascade
- ✗ Efficiency fails: Cost reduction < 20% OR coverage < 85%
- ✗ Mechanism fails: Ablation shows no sweet spot dependency

**Nuanced Outcome Possibilities:**

1. **Full Support (Thesis Validated):**
   - Both gates pass → HBC demonstrates superior ECE + efficiency
   - Paper contribution: Novel Bayesian integration framework + meta-uncertainty via disagreement
   - Impact: Practical UQ method for foundation models

2. **Partial Support (Refined Thesis):**
   - H-E1 passes, H-M-integrated shows ECE improvement but cost reduction < 30%
   - Paper contribution: Quality improvement (drop efficiency claim)
   - Impact: Research contribution, may need simplification for deployment

3. **No Support (Antithesis Validated):**
   - H-E1 fails (ρ outside sweet spot) → Methods not complementary
   - Paper contribution: "Why joint calibration doesn't work" negative result
   - Impact: Saves community from pursuing this direction

**Key Insight from Dialectical Analysis:**

The sweet spot assumption (0.3 < ρ < 0.7) is the **critical hinge**. If validated by H-E1, 
the mechanism testing (H-M-integrated) has high probability of success because theoretical 
foundation (complementarity) is established. If H-E1 fails, the entire HBC approach 
collapses—but this is discovered in Week 2, not after months of implementation.

This is **good science**: falsifiable hypothesis with early abort condition prevents 
wasted effort.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| **Complementarity** | Consistency (epistemic) and conformal (aleatoric) measure distinct aspects with 0.3 < ρ < 0.7 | ρ may be > 0.8 (redundant) or < 0.2 (independent), invalidating joint calibration | **H-E1 test:** Measure ρ on 3 datasets, ABORT if outside sweet spot |
| **Calibration Quality** | HBC achieves ECE < 0.05, significantly lower than baselines | ECE improvement may be < 0.01 (not practical), independent cascade may be sufficient | **H-M-integrated test:** 4-way comparison with statistical significance (p<0.05) |
| **Computational Efficiency** | HBC reduces cost 30-50% vs. COIN by using consistency as prior | Cost reduction may be < 20% (not worth complexity) or coverage drops below 85% | **Efficiency validation:** Measure forward passes and coverage, SCOPE to quality-only if efficiency fails |
| **Mechanism Validity** | 3-step causal chain (consistency → conformal → Bayesian updating) explains improvement | Alternative explanation: ensemble effect, not Bayesian calibration | **Ablation test:** Vary ρ (0.2, 0.5, 0.8), expect ECE peak at ρ~0.5 (sweet spot dependency) |
| **Scope Applicability** | Works on foundation models with sampling capability and labeled validation sets | Fails in zero-shot deployment, latency-critical apps, or adversarial settings | **Documented limitations:** Known constraints, not failure—applies to all UQ methods |

**Overall Robustness Score:** MEDIUM-HIGH

**Strengths:**
- ✓ Early abort condition (H-E1 gate) prevents wasted effort on invalid approach
- ✓ Clear falsification criteria for both complementarity and mechanism
- ✓ Risk-managed scope: Core contribution (calibration quality) separable from extensions
- ✓ Multiple baselines (3) provide robust comparison

**Weaknesses:**
- ⚠ Sweet spot assumption is empirical (not theoretically guaranteed)
- ⚠ Bayesian convergence may require more resources than estimated (A2 risk)
- ⚠ Domain shift robustness is secondary claim (R5 risk)

**Confidence in Verification Plan:** 0.80 (HIGH)

**Rationale for Confidence:**
- Sequential gates allow early detection of fundamental flaws (H-E1 validates foundation)
- 4-way comparison against strong baselines (SelfCheckGPT, COIN, Independent Cascade)
- Statistical rigor (p<0.05 significance, n≥1000 per dataset)
- Falsification-driven design (clear criteria for when to ABORT, PIVOT, or SCOPE)

**Risk-Adjusted Confidence:**
- IF H-E1 passes (ρ validates sweet spot): Confidence in H-M-integrated success = 0.75
- IF H-E1 fails: Confidence in discovering this early (Week 2) = 0.95 (good science)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Hierarchical Bayesian Calibration (HBC) for Foundation Model UQ
- ID: H-HBC-v1, Confidence: 0.80 (HIGH)
- Core claim: Joint calibration of consistency + conformal methods achieves ECE < 0.05 with 30-50% cost reduction

**Verification Structure:**
- Mode: Incremental (Phase 2A-validated hypothesis)
- Sub-Hypotheses: 2 total (H-E1: Complementarity, H-M-integrated: Full mechanism)
- Duration: 4 weeks (2 phases, fully sequential)
- Critical Gates: 2 decision points (Week 2: Foundation, Week 4: Mechanism)

**Scope Reduction from Phase 2A:**
- 25% reduction: 3 BUILD_ON claims (SelfCheckGPT, COIN, Impossibility) → 1 PROVE_NEW (complementarity)
- Focus: Validate complementarity (0.3 < ρ < 0.7) + joint calibration improvement

**Risk Assessment:** MEDIUM
- CRITICAL risk: Sweet spot violation (R1) → H-E1 validates FIRST (Week 2 gate)
- HIGH risk: Convergence failure (R2) → HBC-Lite fallback available
- Mitigation: Sequential gates allow early abort (Week 2 if ρ outside sweet spot)

**Immediate Action:** Begin Phase 1 with H-E1 (complementarity verification)

---

### 7.2 Final Summary

**Verification Plan Achievements:**
- ✓ 2 hypotheses designed with clear falsification criteria (H-E1, H-M-integrated)
- ✓ Sequential gate-based execution (4 weeks, 2 MUST_WORK gates)
- ✓ Risk analysis complete (5 risks identified, mitigation strategies defined)
- ✓ Dialectical analysis performed (Thesis-Antithesis-Synthesis framework)
- ✓ Null hypothesis (H0) integrated as antithesis foundation

**Key Innovations from Phase 2A:**
1. **Sweet Spot Assumption (0.3 < ρ < 0.7):** Complementarity range validated by H-E1 before mechanism testing
2. **3-Step Causal Chain:** Integrated into single H-M-integrated hypothesis (efficient verification)
3. **Early Abort Condition:** H-E1 failure (Week 2) prevents wasted effort on invalid approach

---

### 7.3 Conclusions

#### 7.3.1 Verification Execution Order

**Phase 1: Foundation** (Week 1-2)
- **H-E1:** Validate complementarity (0.3 < ρ < 0.7) on TruthfulQA, HH-RLHF, SQuAD
- **Gate 1:** MUST PASS (ρ in sweet spot on ALL datasets)
- **If FAIL:** ABORT HBC, report "methods not complementary"

**Phase 2: Core Mechanism** (Week 3-4)
- **H-M-integrated:** Test full 3-step causal chain (consistency → conformal → Bayesian co-calibration)
  - Step 1: Consistency sampling measures epistemic uncertainty → C(x)
  - Step 2: Conformal prediction provides aleatoric bounds → I(x)
  - Step 3: Hierarchical Bayesian updating exploits complementarity
- **Gate 2:** MUST WORK (ECE < 0.05, cost reduction ≥ 30%, coverage ≥ 90%)
- **If FAIL:** Report "independent cascade is best," document as negative result

---

#### 7.3.2 Critical Decision Points

**Gate 1 (Week 2 - Foundation Check):**
- **Criterion:** 0.3 ≤ ρ ≤ 0.7 on ALL three datasets (TruthfulQA, HH-RLHF, SQuAD)
- **PASS:** Complementarity validated → Proceed to H-M-integrated
- **FAIL (ρ > 0.8):** Methods redundant → ABORT HBC, use stronger method only
- **FAIL (ρ < 0.2):** Methods independent → ABORT HBC, explore alternative integration

**Gate 2 (Week 4 - Mechanism Check):**
- **Criteria:**
  1. ECE_HBC < 0.05 (calibration quality)
  2. p < 0.05 for all pairwise comparisons (HBC vs. 3 baselines)
  3. Cost reduction ≥ 30% vs. COIN-only
  4. Coverage ≥ 90% maintained
- **PASS:** HBC validates → Phase 3 implementation planning
- **FAIL (ECE < 0.01 improvement):** Independent cascade is best → Report as baseline
- **FAIL (cost < 20%):** Drop efficiency claim, keep quality contribution

---

#### 7.3.3 Open Questions

**From Phase 2A Section 5 (phase2b_readiness.open_questions):**
1. What is the minimum calibration set size for HBC to converge? (ablation: 100 vs. 500 vs. 1000 examples)
2. How sensitive is HBC to correlation range? (ablation: ρ=0.2, 0.5, 0.8 scenarios)
3. Can meta-learning enable few-shot domain adaptation for HBC? (extension for deployment robustness)
4. What happens when adversarial inputs target consistency checks specifically? (robustness evaluation)

**Additional Questions from Dialectical Analysis:**
5. If H-E1 passes but H-M-integrated shows marginal improvement (<0.02), is HBC still worthwhile given complexity?
6. Can HBC-Lite (simplified heuristic) achieve comparable results without full Bayesian framework?

---

#### 7.3.4 Recommendations

**Immediate Actions (Week 1):**
1. Set up measurement infrastructure:
   - Download datasets (TruthfulQA, HH-RLHF, SQuAD)
   - Implement SelfCheckGPT consistency scoring (NLI+BERTScore)
   - Implement COIN conformal prediction (90% coverage)
2. Start H-E1 correlation measurement (Week 1-2)
3. Prepare 4-way comparison codebase (Week 2-3) for H-M-integrated

**Resource Allocation:**
- GPU: 1x A100 or equivalent (Llama-2-7B inference)
- Personnel: 1 researcher (sequential execution)
- Data: n≥1000 labeled samples per dataset (standard benchmark sizes)

**Risk Mitigation Priorities:**
1. **R1 (CRITICAL):** Run pilot ρ measurement on TruthfulQA subset (Week 1) to detect sweet spot violation early
2. **R2 (HIGH):** Implement HBC-Lite heuristic in parallel as fallback (Week 3)
3. **R3-R5 (MEDIUM/LOW):** Document as known limitations, monitor but don't block execution

**Contingency Plans:**
- **IF Gate 1 FAIL (Week 2):** Pivot to "Why joint calibration doesn't work" negative result paper
- **IF Gate 2 FAIL (Week 4):** Pivot to "Independent cascade is best" comparative analysis paper

**Phase 3 Preparation:**
- IF both gates PASS: Phase 3 generates PRD/Architecture for HBC implementation
- IF either gate FAIL: Phase 3 generates PRD for baseline implementation (independent cascade)

---

### 7.4 Appendices

#### A. Glossary

| Term | Definition |
|------|------------|
| **HBC** | Hierarchical Bayesian Calibration - joint optimization of consistency + conformal methods |
| **ECE** | Expected Calibration Error - metric for calibration quality (lower is better) |
| **ρ (rho)** | Pearson correlation coefficient between consistency and conformal signals |
| **Sweet Spot** | Correlation range [0.3, 0.7] indicating non-redundant complementarity |
| **COIN** | Conformal prediction method with FDR control (Wang et al., 2025) |
| **SelfCheckGPT** | Consistency-based hallucination detection (Manakul et al., 2023) |

#### B. Phase 2A References

- **Section 0:** Established Facts & Scope Reduction (25% reduction)
- **Section 1.1-1.6:** Hypothesis, Variables, Causal Mechanism, Assumptions, Scope, Predictions
- **Section 2:** Experimental Setup (TruthfulQA/HH-RLHF/SQuAD + Llama-2-7B)
- **Section 4:** Related Work (SelfCheckGPT, COIN, FactTest baselines)
- **Section 5:** Phase 2B Readiness (SH1, SH2, open questions)

#### C. File Outputs

**Phase 2B Outputs:**
- `02b_verification_plan.md` (this file) - Complete verification roadmap
- `verification_state.yaml` (generated by Step 10) - State tracking for Phase 2C loop
- Per-hypothesis context files: Generated JIT by Phase 2C (not Phase 2B)

**Next Phase:**
- Phase 2C: Experiment Design (02c_experiment_design_H-E1.md, 02c_experiment_design_H-M-integrated.md)
- Phase 3: Implementation Planning (PRD, Architecture, PRP)

#### D. MCP Tool Usage Summary

**Step 3 (Hypothesis Generation):**
- `mcp__clearThought__scientificmethod` called 2 times
  - H-E1 verification (hypothesis → experiment → analysis)
  - H-M-integrated verification (hypothesis → experiment → analysis)

**Total MCP Calls:** 2 (incremental mode optimized vs. 10-14 in comprehensive mode)

---

## 8. State & Tasks

### 8.1 Verification State Status

**verification_state.yaml Generated:**
- ✅ File created: `docs/youra_research/verification_state.yaml`
- ✅ Sub-hypotheses tracked: 2 (h-e1, h-m-integrated)
- ✅ Execution order defined: h-e1 → h-m-integrated
- ✅ Next hypothesis: h-e1 (READY status)

**State File Contents:**
```yaml
metadata:
  main_hypothesis_id: "H-HBC-v1"
  pipeline_project_id: "e0f77b48-a1c5-4a3b-9a50-2a866f731118"
  phase2b_verification_plan: "docs/youra_research/02b_verification_plan.md"

sub_hypotheses:
  h-e1:
    type: "Existence"
    status: "READY"
    gate: {type: "MUST_WORK", satisfied: null}
    prerequisites: []
    archon_task_id: "11620600-9b9b-4f40-ad78-06474ee16c3f"
  
  h-m-integrated:
    type: "Mechanism"
    status: "NOT_STARTED"
    gate: {type: "MUST_WORK", satisfied: null}
    prerequisites: ["h-e1"]
    archon_task_id: "cafacb0e-4d53-4a83-8438-ab5cb743ddb4"

statistics:
  total_sub_hypotheses: 2
  ready_count: 1
  not_started_count: 1

next_hypothesis: "h-e1"
workflow_status: "Phase 2B Complete - Ready for Phase 2C"
```

---

### 8.2 Pipeline Tasks Updated

**Archon Pipeline Status:**
- ✅ Phase 2B task marked as **done**
  - Task ID: `f872d2fb-4823-4eba-abfd-4ef8ea948d07`
  - Description: "[UNATTENDED] Phase 2B - Planning COMPLETE - 2 hypotheses (H-E1, H-M-integrated), 4-week timeline, verification_state.yaml generated"
  
- ✅ Phase 2C task marked as **doing**
  - Task ID: `9a76db3e-08e9-408a-a003-d5bfe27ec831`
  - Description: "[UNATTENDED] Phase 2C - Experiment Design - Ready to design experiments for H-E1 and H-M-integrated"

**Pipeline Progression:**
```
Phase 0: Brainstorm        ✅ done
Phase 1: Research          ✅ done
Phase 2A: Dialogue         ✅ done
Phase 2B: Planning         ✅ done (just completed)
Phase 2C: Experiment       🔄 doing (next)
Phase 3: Implementation    ⏸ todo
Phase 4: Coding            ⏸ todo
Phase 4.5: Synthesis       ⏸ todo
Phase 6: Paper Writing     ⏸ todo
Phase 6.5: Review          ⏸ todo
```

---

### 8.3 Hypothesis Tasks Created

**Archon Hypothesis Tasks:**

Created 2 hypothesis-specific tasks in Archon project "Anonymous Pipeline: Uncertainty Quantification in Foundation Models":

1. **Hypothesis H-E1: Existence**
   - Task ID: `11620600-9b9b-4f40-ad78-06474ee16c3f`
   - Status: todo
   - Description: "[UNATTENDED] Validate complementarity (0.3 < ρ < 0.7) between consistency and conformal methods on TruthfulQA, HH-RLHF, SQuAD"
   - Feature: Hypothesis Verification
   - Prerequisites: None (foundation hypothesis)

2. **Hypothesis H-M-integrated: Mechanism**
   - Task ID: `cafacb0e-4d53-4a83-8438-ab5cb743ddb4`
   - Status: todo
   - Description: "[UNATTENDED] Test HBC 3-step causal chain: ECE < 0.05, cost reduction 30-50%, 4-way comparison vs. baselines"
   - Feature: Hypothesis Verification
   - Prerequisites: H-E1 (must complete first)

**Task Workflow:**
```
┌─────────────────────────────────────────────┐
│ H-E1: Existence (todo)                      │
│ - Phase 2C: Experiment Design               │
│ - Phase 3: Implementation Planning          │
│ - Phase 4: Coding & Validation              │
└─────────────────────────────────────────────┘
                    │
                    ▼ (H-E1 completes)
┌─────────────────────────────────────────────┐
│ H-M-integrated: Mechanism (todo)            │
│ - Phase 2C: Experiment Design               │
│ - Phase 3: Implementation Planning          │
│ - Phase 4: Coding & Validation              │
└─────────────────────────────────────────────┘
```

**Integration with Phase 2C:**
- Phase 2C will read `verification_state.yaml`
- Process `next_hypothesis: "h-e1"` first
- Generate `02c_experiment_design_H-E1.md`
- Update state file when complete
- Repeat for `h-m-integrated`
