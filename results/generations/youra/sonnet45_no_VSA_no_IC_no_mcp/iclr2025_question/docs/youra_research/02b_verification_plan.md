# Verification Plan: Pilot-Driven Viability Gates for Early Identification of Non-Viable ML Hypotheses

**Date:** 2026-08-25
**Hypothesis ID:** H-PilotGates-v1
**Confidence:** 0.85
**Total Hypotheses:** 4 (H-E1 + H-M1-3)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under ML research contexts where computational overhead thresholds exist (e.g., <10% for deployment), if researchers apply Pilot-Driven Viability Gates (incremental empirical validation at 10-sample, 100-sample, full-dataset scales), then non-viable hypotheses (overhead >threshold) will be identified at the micro-pilot stage (Gate 1, 10 samples, <1 hour) with >80% accuracy, because overhead scales predictably from micro-pilot to full implementation, and Bayesian updates refine predictions incrementally.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in accuracy between Gate 1 micro-pilot predictions and random guessing (50% accuracy baseline) for identifying non-viable hypotheses based on computational overhead thresholds.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Retrospective ML Projects Corpus (custom) | Framework validation requires past hypotheses with BOTH micro-pilot (10-sample) and full-scale overhead measurements. Papers with Code and ML conference papers (NeurIPS, ICML, ICLR) often report ablation studies with small-sample timing data. Target: 30 hypotheses (10 low-overhead <20%, 10 mid 20-80%, 10 high >80%) for balanced evaluation. |
| **Model** | Bayesian Overhead Predictor | The framework IS the model being tested. No external ML model needed. Bayesian predictor takes O_10 as prior mean, updates with O_100 as likelihood, outputs posterior P(O_full). |

**Dataset Details:**
- Source: Papers with Code leaderboards + conference papers with published micro-pilot data
- Path: N/A (meta-dataset of published results)

**Model Details:**
- Type: statistical model
- Source: Implemented using scipy.stats Gaussian priors/likelihoods

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Random Guessing | 50% accuracy baseline (coin flip for viable/non-viable classification) | Any ML hypothesis |
| Full Implementation First | 100% accuracy eventually (ground truth), but requires full time investment (hours to days) | Any ML hypothesis |
| Expert Intuition | Estimated 60-70% accuracy based on h-e1 anecdote (researchers thought approach was viable, turned out it wasn't) | Researcher experience-dependent |
| Complexity Analysis (Big-O theoretical bounds) | Identifies asymptotic scaling, but misses constant factors. h-e1 was O(n) but with large constant (68.65% overhead) | Theoretical analysis |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Computational overhead scales predictably from 10-sample micro-pilot to full dataset | h-e1 showed consistent KL divergence computation across samples, suggesting linear or near-linear scaling for many operations | If scaling is non-linear (e.g., memory bottlenecks at 100 samples not present at 10), Gate 1 predictions will have high error rate |
| A2 | Past ML projects report sufficient micro-pilot data for retrospective validation | Papers with Code and ML conference papers often include ablation studies with small-sample results | If <20 papers with 10-sample data available, statistical power drops below significance; need prospective validation instead |
| A3 | Scaling factor k generalizes across hypothesis types within a category | Attention mechanisms share computational patterns (O(n²) self-attention), suggesting within-category similarity | If each hypothesis requires unique k, framework needs large training set of past hypotheses to learn per-hypothesis scaling |
| A4 | Researchers will honestly report negative results from Gate 1 stops | Framework design includes incentive: saving time is valuable, early stops prevent wasted effort | If researchers skip Gate 1 or ignore stop signals, framework adoption fails |
| A5 | Overhead is the dominant feasibility constraint (vs. memory, dataset size, human annotation) | h-e1 failed on overhead despite having dataset and metrics; Phase 1 constraints emphasize 'no new data/human eval' | If memory or other constraints dominate, framework needs additional gates beyond overhead measurement |

### 1.6 Research Gap & Novelty

**Key Innovation:** First formalized feasibility-first framework treating viability assessment as incremental empirical validation rather than one-shot constraint checking or post-hoc discovery (like h-e1).

**Preserved Novelty:** Pilot-Driven Viability Gates with Bayesian updates: structured search through sample scales (10 → 100 → full) with probabilistic prediction refinement. Combines software engineering gating (fail-fast) with Bayesian inference (uncertainty reduction).

**Differentiation:**
- vs. Ablation studies: Ablations test hypothesis VARIATIONS, not viability GATES. No formalized stop/continue decision protocol.
- vs. Hyperparameter early stopping: Optimizes hyperparams, not feasibility. Different objective: maximize accuracy vs. predict overhead.
- vs. Complexity analysis (Big-O): Theoretical, doesn't account for constant factors or implementation details. Framework uses empirical measurement.
- vs. h-e1 post-hoc discovery: h-e1 discovered overhead AFTER full implementation. Framework discovers at micro-pilot BEFORE committing resources.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Retrospective ML Projects Corpus Exists

**Statement**: Under retrospective validation using published ML research, if we search Papers with Code leaderboards and conference papers (NeurIPS, ICML, ICLR) for hypotheses with micro-pilot data, then we will find ≥30 hypotheses with BOTH 10-sample and full-scale overhead measurements, because ML papers often report ablation studies with small-sample timing data.

**Rationale**: Framework validation requires empirical data from past hypotheses. Without a corpus of ≥30 hypotheses, statistical power drops below significance and retrospective validation becomes infeasible.

**Variables** (from Phase 2A):
- Independent: Search scope (Papers with Code + conferences)
- Dependent: Count of hypotheses with micro-pilot + full-scale data
- Controlled: Hypothesis type (attention/gradient/etc), publication venue

**Verification Protocol**:
1. Search Papers with Code for overhead metrics with sample size breakdowns.
2. Search NeurIPS/ICML/ICLR papers (2020-2024) for ablation studies with 10-sample timing.
3. Filter for hypotheses with BOTH 10-sample and full-dataset overhead reported.
4. Stratify by overhead level (10 low <20%, 10 mid 20-80%, 10 high >80%).
5. Verify ≥30 total hypotheses meet criteria.

**Success Criteria** (PoC):
- Primary: ≥30 hypotheses with micro-pilot + full-scale data found
- Secondary: Balanced stratification across overhead levels

**Failure Response**:
- IF <20 hypotheses: PIVOT to prospective validation (run new micro-pilots)
- IF 20-29 hypotheses: EXPLORE combining retrospective + prospective
- IF ≥30: PASS

**Gate**:
- Type: MUST_WORK
- If Fail: No corpus = no retrospective validation possible

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 5 (sh1_existence)

---

#### H-M1: Micro-Pilot Overhead Correlates with Full-Scale Overhead

**Statement**: Under retrospective validation using the corpus from H-E1, if we measure correlation between 10-sample overhead (O_10) and full-dataset overhead (O_full), then correlation r will exceed 0.7, because overhead operations (like KL divergence in h-e1) scale predictably across sample sizes.

**Rationale**: Core mechanism assumption (A1). If O_10 doesn't correlate with O_full, extrapolation from Gate 1 micro-pilot to full-scale prediction is invalid.

**Variables**:
- Independent: Sample size (10 vs full dataset)
- Dependent: Measured overhead (O_10, O_full)
- Controlled: Hypothesis type, benchmark dataset, hardware

**Verification Protocol**:
1. Extract O_10 and O_full from each hypothesis in the corpus.
2. Compute Pearson correlation r between O_10 and O_full across all hypotheses.
3. Fit linear regression O_full = k × O_10 to derive scaling factor k.
4. Compute per-hypothesis-type k values (attention, gradient, etc).
5. Test if r >0.7 and k variance is low within types.

**Success Criteria** (PoC):
- Primary: Correlation r >0.7 between O_10 and O_full
- Secondary: Scaling factor k consistent within hypothesis types (CV <30%)

**Failure Response**:
- IF r <0.5: ABANDON (extrapolation fundamentally invalid)
- IF 0.5 ≤ r <0.7: EXPLORE non-linear models or per-type calibration

**Gate**:
- Type: MUST_WORK
- If Fail: Predictive scaling invalid → framework collapses

**Dependencies**: H-E1 (requires corpus)

**Source**: Phase 2A Section 1.3 Causal Step 1, Assumption A1

---

#### H-M2: Bayesian Updates Reduce Prediction Error

**Statement**: Under hypotheses that reach Gate 2 (100 samples), if we apply Bayesian updates combining Gate 1 prior P(O_full | O_10) with Gate 2 likelihood P(O_100 | O_full), then posterior prediction error will be >40% lower than Gate 1 prior error, because Bayesian inference reduces uncertainty by incorporating new evidence.

**Rationale**: Tests incremental refinement claim. If Gate 2 data doesn't improve predictions, Bayesian updates add complexity without value.

**Variables**:
- Independent: Gate stage (Gate 1 prior vs Gate 2 posterior)
- Dependent: Prediction error |O_pred - O_full| / O_full
- Controlled: Bayesian model (Gaussian prior/likelihood), hypothesis type

**Verification Protocol**:
1. For hypotheses with Gate 2 data (100 samples), compute Gate 1 prediction error.
2. Apply Bayesian update with O_100 as likelihood, compute Gate 2 posterior prediction.
3. Compute Gate 2 prediction error.
4. Measure error reduction: (Error_G1 - Error_G2) / Error_G1 × 100%.
5. Test if mean reduction >40% via paired t-test (p <0.05).

**Success Criteria** (PoC):
- Primary: Mean error reduction >40% (paired t-test p <0.05)
- Secondary: At least 10 hypotheses with Gate 2 data for statistical power

**Failure Response**:
- IF reduction <20%: SHOULD_WORK fail → Document limitation, proceed without Gate 2
- IF reduction 20-40%: EXPLORE alternative update strategies

**Gate**:
- Type: SHOULD_WORK (nice-to-have refinement, not core claim)
- If Fail: Framework still works with Gate 1 only

**Dependencies**: H-M1 (requires valid extrapolation)

**Source**: Phase 2A Section 1.3 Causal Step 2, Prediction P3

---

#### H-M3: Gate 1 Viability Decision Accuracy >80%

**Statement**: Under the framework applied to the corpus from H-E1, if we use Gate 1 micro-pilot (10 samples, <1 hour) to predict viability (overhead >threshold vs ≤threshold), then accuracy (TP + TN) / Total will exceed 80%, compared to 50% random guessing null hypothesis, because overhead scaling from H-M1 enables early prediction.

**Rationale**: **CORE CLAIM** - validates primary prediction P1. This is the main testable hypothesis for the Pilot-Driven Viability Gates framework.

**Variables**:
- Independent: Viability Gate Stage (Gate 1 micro-pilot)
- Dependent: Prediction accuracy (0-100%)
- Controlled: Overhead threshold (10% for deployment context), hypothesis type

**Verification Protocol**:
1. For each hypothesis in corpus, apply Gate 1 prediction using O_10 × k.
2. Compare predicted viability (O_pred >threshold) to actual viability (O_full >threshold).
3. Classify: TP (correctly predicted non-viable), TN (correctly predicted viable), FP, FN.
4. Compute accuracy = (TP + TN) / 30.
5. Binomial test: accuracy >80% vs null hypothesis 50%, p <0.05.

**Success Criteria** (PoC):
- Primary: Accuracy >80% (24/30 correct predictions), binomial test p <0.05
- Secondary: 60%+ non-viable filtered at Gate 1 (P2 claim)

**Failure Response**:
- IF accuracy ≤60%: MUST_WORK fail → Framework doesn't beat random + margin
- IF 60% <accuracy ≤80%: PARTIAL → Explore per-type thresholds or calibration

**Gate**:
- Type: MUST_WORK (core claim)
- If Fail: Framework prediction claim unsupported

**Dependencies**: H-M2 (builds on scaling + updates)

**Source**: Phase 2A Section 1.6 Prediction P1 (primary)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥30 hypotheses with micro-pilot data | PIVOT to prospective validation |
| H-M1 | MUST_WORK | Correlation r >0.7 | ABANDON (extrapolation invalid) |
| H-M2 | SHOULD_WORK | Error reduction >40% | Document limitation, proceed |
| H-M3 | MUST_WORK | Accuracy >80% (p <0.05) | Framework claim unsupported |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1-3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption Risks

| Risk | Source | Description | Severity | Mitigation |
|------|--------|-------------|----------|------------|
| R1 | A1 | Non-linear scaling (memory bottlenecks) breaks extrapolation | High | Add memory profiling at each gate; test scaling linearity |
| R2 | A2 | <20 papers with micro-pilot data | Medium | Prospective validation fallback (run new micro-pilots) |
| R3 | A3 | Scaling factor k varies by hypothesis type | Medium | Learn type-specific k values; stratify validation |
| R4 | A4 | Researchers skip Gate 1 or ignore stop signals | Low | Framework design incentive (time savings); adoption study |
| R5 | A5 | Memory/other constraints dominate vs overhead | Medium | Add memory/dataset gates beyond overhead measurement |

### 4.2 Mitigation Strategies

**R1 (Non-linear scaling):**
- Prevention: Profile memory usage at Gate 1 (10 samples) and Gate 2 (100 samples)
- Detection: Monitor O_100 vs linear extrapolation from O_10
- Response: PIVOT to non-linear models (polynomial, log scaling) if r <0.7

**R2 (Insufficient corpus):**
- Prevention: Expand search to arXiv, GitHub repos with timing benchmarks
- Detection: Early corpus size check in H-E1
- Response: PIVOT to prospective validation (run 30 new micro-pilots)

**R3 (k generalization):**
- Prevention: Stratify corpus by hypothesis type during H-E1
- Detection: High variance in k values within type (CV >30%)
- Response: SCOPE to type-specific k or EXPLORE per-hypothesis calibration

---

## 5. Execution Planning

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Retrospective Corpus Exists)
         │
         ▼
[Level 1 - Mechanism Chain]
    H-M1 (Micro-pilot Correlation)
         │ (MUST_WORK)
         ▼
    H-M2 (Bayesian Updates)
         │ (SHOULD_WORK)
         ▼
    H-M3 (Gate 1 Accuracy >80%)
         │ (MUST_WORK - CORE CLAIM)
         ▼
    [Terminal]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (5 weeks)
═══════════════════════════════════════════════════════════
```

### 5.2 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ Week 1-2 │ Week 3 │ Week 4 │ Week 5 │
─────────────────┼──────────┼────────┼────────┼────────┤
PHASE 1: Foundation
  H-E1           │ ████████ │        │        │        │
  [Gate 1]       │          │ ◆      │        │        │
─────────────────┼──────────┼────────┼────────┼────────┤
PHASE 2: Mechanisms
  H-M1           │          │ ████   │        │        │
  H-M2           │          │        │ ████   │        │
  H-M3           │          │        │        │ ████   │
  [Gate 2]       │          │        │        │     ◆  │
─────────────────┼──────────┼────────┼────────┼────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Execution Order

**Phase 1: Foundation** (Weeks 1-2)
- Execute H-E1: Search Papers with Code + conferences for ≥30 hypotheses
- Gate 1: If <20 hypotheses → PIVOT to prospective validation

**Phase 2: Core Mechanisms** (Weeks 3-5)
- Week 3: H-M1 (Test correlation r >0.7 between O_10 and O_full)
- Week 4: H-M2 (Test Bayesian error reduction >40%)
- Week 5: H-M3 (Test Gate 1 accuracy >80% vs null hypothesis)
- Gate 2: H-M1 must pass; H-M2 can fail (SHOULD_WORK); H-M3 validates core claim

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Pilot-Driven Viability Gates enable >80% accurate prediction of non-viable hypotheses at Gate 1 (<1 hour micro-pilot), because overhead scales predictably and Bayesian updates refine predictions.

**Supporting Evidence:**
- h-e1 showed measurable overhead (68.65%) at small scales, validating measurement feasibility
- Bayesian inference is established for uncertainty reduction
- Papers with Code provides published overhead data for retrospective validation

**Strengths:**
- Empirical grounding (measure, don't theorize)
- Incremental validation (fail-fast at each gate)
- Leverages existing benchmarks (no new datasets)

### 6.2 Antithesis (H0-Based)

**Null Hypothesis:** No difference between Gate 1 predictions and random guessing (50% accuracy).

**Counter-Arguments:**
- Overhead may scale non-linearly (memory bottlenecks, I/O bounds) → extrapolation fails
- Micro-pilot data may be sparse in papers (<20 available) → low statistical power
- Scaling factor k may be hypothesis-specific → no generalization

**Potential Failure Points:**
- R1: Non-linear scaling breaks correlation (r <0.7 in H-M1)
- R2: Insufficient corpus (<20 hypotheses) makes validation infeasible
- R3: High k variance within types → per-hypothesis calibration needed

### 6.3 Synthesis

**Balanced Assessment:** The framework presents a testable claim that micro-pilot overhead predicts full-scale viability with >80% accuracy. However, the null hypothesis raises valid concerns about scaling predictability and corpus availability.

**Resolution Path:**
1. H-E1 establishes corpus existence before testing mechanism
2. H-M1 validates scaling assumption empirically (r >0.7 test)
3. H-M2 tests Bayesian refinement (optional, SHOULD_WORK)
4. H-M3 validates core claim against null hypothesis

**Conditions for Thesis Support:**
- H-E1 passes (≥30 hypotheses found)
- H-M1 passes (r >0.7, scaling valid)
- H-M3 passes (accuracy >80%, p <0.05)

**Conditions for Antithesis Support:**
- H-E1 fails (<20 hypotheses)
- H-M1 fails (r <0.5, extrapolation invalid)
- H-M3 fails (accuracy ≤60%, framework no better than baseline)

**Robustness Score:** Medium-High (0.85 confidence from Phase 2A)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Pilot-Driven Viability Gates framework for early identification of non-viable ML hypotheses
- ID: H-PilotGates-v1, Confidence: 0.85

**Verification Structure:**
- Mode: Incremental (Phase 2A-based)
- Sub-Hypotheses: 4 total (H-E1, H-M1-3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1: Foundation, Gate 2: Mechanisms)

**Risk Assessment:** Medium
- Primary concerns: Non-linear scaling (R1), corpus availability (R2)

**Immediate Action:** Begin Phase 1 with H-E1 (corpus search)

### 7.2 Key Achievements

- 4 hypotheses across 2 phases with clear dependency chain
- H0 addressed: No difference from 50% random guessing baseline
- Risk mitigation strategies for all 5 key assumptions

### 7.3 Critical Decision Points

**Gate 1 (Foundation):** H-E1 must pass
- FAIL (<20 hypotheses) → PIVOT to prospective validation
- PASS (≥30 hypotheses) → Proceed to Phase 2

**Gate 2 (Mechanisms):**
- H-M1 FAIL (r <0.5) → ABANDON (extrapolation invalid)
- H-M2 FAIL → Document limitation, proceed (SHOULD_WORK)
- H-M3 FAIL (accuracy ≤60%) → Core claim unsupported

### 7.4 Open Questions

- What is optimal micro-pilot sample size? (10 chosen heuristically)
- How to handle non-linear scaling? (Memory profiling, non-linear models)
- Can scaling factor k be learned from past data or requires per-hypothesis tuning?

### 7.5 Recommendations

**Immediate Actions:**
- Start Phase 1: Search Papers with Code + NeurIPS/ICML/ICLR (2020-2024)
- Set up measurement infrastructure (time.time(), scipy.stats for Bayesian)

**Resource Allocation:**
- Allocate 5 weeks for critical path
- Reserve 2-week buffer for corpus expansion (if R2 triggers)

**Failure Management:**
- Document all gate failures with root cause analysis
- Execute PIVOT strategies (prospective validation for R2, non-linear models for R1)

---

## 8. Appendices

### A. Phase 2A Reference
- Source: 03_refinement.yaml (ID: H-PilotGates-v1)
- Causal Chain: 3 steps (micro-pilot → Bayesian → decision)
- Scope Reduction: 0% (facts serve as context, not exclusion)

### B. Hypothesis Type Distribution
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1-3, from 3-step causal chain)
- Condition: 0 (no testable boundary conditions)

---
