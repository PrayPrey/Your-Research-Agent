# Verification Plan: Structural Inductive Biases in Weight Embeddings

**Date:** 2026-08-19
**Hypothesis ID:** H-WeightStructure-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## Executive Summary

**Main Hypothesis:** Under the Model Zoo benchmark, progressively adding structural inductive biases (Flatten+MLP → Layer-wise → Layer-wise+GRB → NFN) increases property prediction correlation because structural biases capture weight-space patterns encoding functional properties.
- ID: H-WeightStructure-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total
  - H-E: 1, H-M: 3
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: A3 (NFN adaptation), A4 (GRB convergence)

**Immediate Action:** Begin Phase 1 with H-E1

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the Model Zoo benchmark with accuracy labels as ground truth,
if we compare four embedding methods with increasing structural sophistication
(Flatten+MLP → Layer-wise → Layer-wise+GRB → NFN),
then Pearson correlation with ground-truth accuracy will increase monotonically across steps,
because structural biases capture weight-space patterns that encode functional model properties.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in property prediction performance between
Layer-wise+GRB (alignment preprocessing) and NFN (equivariant architecture).
Alignment suffices; architectural equivariance provides no additional benefit.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Model Zoos (standard) | Provides thousands of pretrained models with ground-truth accuracy labels |
| **Model** | Multiple (4-step ablation) | Each step adds one structural inductive bias |

**Dataset Details:**
- Source: Schurholt et al. 2022
- Path: github.com/HSG-AIML/model-zoos (to be verified)

**Model Details:**
- Type: embedding + regression
- Source: Hyper-Representations, NFN codebases

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Hyper-Representations VAE | Demonstrated embedding quality for weight generation | Custom model populations |
| Neural Functional Transformers | State-of-the-art for weight processing tasks | Various including MNIST zoo |
| StatNN (statistical features) | Simple baseline using weight statistics | Various |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Model Zoo accuracy labels are reliable ground truth | Labels computed from standardized evaluation protocol in Schurholt et al. | All correlation measurements become unreliable |
| A2 | Model Zoo has sufficient accuracy variance (σ > 10%) | Model Zoos paper describes diverse training configurations | Benchmark is trivial; prediction correlation is meaningless |
| A3 | NFN can be adapted for embedding extraction with pooling head | Permutation-invariant pooling is well-established technique | Step 4 of ablation cannot be implemented |
| A4 | Git Re-Basin alignment converges for Model Zoo architectures | GRB demonstrated on ResNets in original paper | Step 3 of ablation produces inconsistent results |
| A5 | Effect size thresholds (Δr > 0.1, Δr > 0.05) are appropriate after calibration | Thresholds calibrated against baseline variance in Phase 1 of protocol | Statistical conclusions may be over- or under-powered |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic ablation isolating structural inductive biases for weight embedding

**Key Innovation:** Reframes from 'which method wins' to 'what structural properties predict performance'

**Differentiation:**
- Hyper-Representations (2022): Evaluated single method; we compare across structural complexity ladder
- Neural Functional Transformers (2024): Focused on weight processing/generation; we evaluate for property prediction
- Git Re-Basin (2022): Focused on model merging; we use alignment as preprocessing for embedding

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Model Zoo Dataset Validity**

**Statement**: Under standard Model Zoo evaluation, if we analyze the accuracy distribution, then σ(accuracy) > 10% and labels are consistent, because diverse training configurations produce meaningful accuracy variance.

**Rationale**: Foundation hypothesis validates the benchmark is non-trivial. Without sufficient accuracy variance, correlation measurements are meaningless. Must pass before testing any mechanism.

**Variables** (from Phase 2A):
- Independent: None (observational)
- Dependent: Accuracy distribution statistics (mean, σ, range)
- Controlled: Evaluation protocol, architecture family

**Verification Protocol** (3-5 steps):
1. Load Model Zoo dataset and extract all accuracy labels
2. Compute distribution statistics: mean, std, min, max, quartiles
3. Verify σ > 10% threshold is met
4. Check for outliers or label inconsistencies
5. Document dataset characteristics for reproducibility

**Success Criteria** (PoC: Direction-based):
- Primary: Accuracy σ > 10% across Model Zoo
- Secondary: No systematic label errors detected

**Failure Response**:
- IF fails: PIVOT to alternative benchmark or filter Model Zoo subset

**Dependencies**: None

**Source**: Phase 2A SH1, Prediction P1

---

---
**H-M1: Layer-wise Structure Advantage**

**Statement**: Under Model Zoo benchmark, if we compare Layer-wise encoding vs Flatten+MLP, then Pearson correlation improves by Δr > 0.1, because per-layer statistics capture layer-specific functional patterns.

**Rationale**: First causal chain step. Layer-wise processing preserves structural information that flat concatenation destroys. Validates basic structural awareness helps.

**Variables** (from Phase 2A):
- Independent: Embedding method (Flatten+MLP vs Layer-wise)
- Dependent: Pearson correlation with ground-truth accuracy
- Controlled: Dataset, train/test split, regressor architecture

**Verification Protocol**:
1. Implement Flatten+MLP baseline encoder
2. Implement Layer-wise encoder with mean aggregation
3. Train identical MLP regressors on embeddings
4. Compute Pearson r for both on test set (full standard split)
5. Run paired t-test across 5 random seeds

**Success Criteria**:
- Primary: Layer-wise r > Flatten+MLP r + 0.1 with p < 0.05
- Secondary: Consistent improvement across seeds

**Failure Response**:
- IF fails: EXPLORE alternative layer aggregation strategies

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1, Prediction P1

---

---
**H-M2: Alignment Preprocessing Benefit**

**Statement**: Under Model Zoo benchmark, if we add Git Re-Basin alignment preprocessing to Layer-wise encoding, then Pearson correlation improves by Δr > 0.05, because alignment removes permutation-induced variance revealing functional equivalence.

**Rationale**: Second causal chain step. Tests whether explicit alignment preprocessing provides benefit over raw layer-wise features. Key tension point with H0.

**Variables** (from Phase 2A):
- Independent: Preprocessing (none vs GRB alignment)
- Dependent: Pearson correlation with accuracy
- Controlled: Encoder architecture, regressor, reference model (random, fixed)

**Verification Protocol**:
1. Select random reference model for GRB alignment
2. Align all Model Zoo models to reference using Git Re-Basin
3. Apply Layer-wise encoding to aligned weights
4. Train MLP regressor and compute correlation
5. Compare to non-aligned Layer-wise baseline

**Success Criteria**:
- Primary: Layer-wise+GRB r > Layer-wise r + 0.05 with p < 0.05
- Secondary: GRB convergence rate > 95% of models

**Failure Response**:
- IF fails: EXPLORE alternative alignment methods (weight matching)

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2, Prediction P2

---

---
**H-M3: Equivariant Architecture Advantage**

**Statement**: Under Model Zoo benchmark, if we use NFN (permutation-equivariant) instead of Layer-wise+GRB, then Pearson correlation improves by Δr > 0.05, because equivariant architecture directly operates on symmetry-reduced representations.

**Rationale**: Final causal chain step. Tests key tension: does architectural equivariance provide benefit beyond alignment preprocessing? This is the H0 test point.

**Variables** (from Phase 2A):
- Independent: Architecture (Layer-wise+GRB vs NFN)
- Dependent: Pearson correlation with accuracy
- Controlled: Dataset, splits, regressor head complexity

**Verification Protocol**:
1. Adapt NFN for embedding extraction with pooling head
2. Train NFN encoder + MLP regressor
3. Compute correlation on test set
4. Compare to Layer-wise+GRB baseline
5. Statistical test across 5 seeds

**Success Criteria**:
- Primary: NFN r > Layer-wise+GRB r + 0.05 with p < 0.05
- Secondary: NFN training stable and converges

**Failure Response**:
- IF fails: Document as support for H0 (alignment suffices)

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3, Prediction P3

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | σ(accuracy) > 10% | STOP, find alternative benchmark |
| H-M1 | MUST_WORK | Δr > 0.1, p < 0.05 | PIVOT to alternative approach |
| H-M2 | SHOULD_WORK | Δr > 0.05, p < 0.05 | Document limitation, continue |
| H-M3 | SHOULD_WORK | Δr > 0.05, p < 0.05 | Document as H0 support |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 | H-E1, All | High |
| R2 | A2 | H-E1 | High |
| R3 | A3 | H-M3 | Medium |
| R4 | A4 | H-M2 | Medium |
| R5 | A5 | H-M1, H-M2, H-M3 | Low |

### 4.2 Mitigation Strategies

**Risk R1: Unreliable Ground Truth Labels**
- Source: A1 - Model Zoo accuracy labels
- Severity: High
- Mitigation:
  1. Prevention: Cross-validate label consistency with re-evaluation
  2. Detection: Compare claimed vs recomputed accuracy on subset
  3. Response: PIVOT to different benchmark or filter problematic models

**Risk R2: Insufficient Accuracy Variance**
- Source: A2 - Variance threshold
- Severity: High
- Mitigation:
  1. Prevention: Pre-check dataset statistics before experiments
  2. Detection: H-E1 explicitly tests this
  3. Response: Filter to high-variance subset or use different benchmark

**Risk R3: NFN Adaptation Failure**
- Source: A3 - NFN embedding extraction
- Severity: Medium
- Mitigation:
  1. Prevention: Prototype pooling head early
  2. Detection: Monitor training stability metrics
  3. Response: EXPLORE alternative equivariant architectures

**Risk R4: GRB Convergence Issues**
- Source: A4 - Git Re-Basin on Model Zoo
- Severity: Medium
- Mitigation:
  1. Prevention: Test GRB on small subset first
  2. Detection: Track convergence rate across models
  3. Response: EXPLORE weight matching alternatives

**Risk R5: Effect Size Threshold Calibration**
- Source: A5 - Statistical power
- Severity: Low
- Mitigation:
  1. Prevention: Run baseline variance estimation first
  2. Detection: Check effect size vs measurement noise
  3. Response: Adjust thresholds based on calibration

### 4.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Label reliability | A1 | High | All | Cross-validation |
| R2 | Low variance | A2 | High | H-E1 | Pre-check statistics |
| R3 | NFN adaptation | A3 | Medium | H-M3 | Early prototype |
| R4 | GRB convergence | A4 | Medium | H-M2 | Subset testing |
| R5 | Threshold calibration | A5 | Low | H-M* | Baseline estimation |

Critical Risks: 0
High Risks: 2
Medium Risks: 2
Low Risks: 1

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1 ← H-E1
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3 ← H-M2

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4
═══════════════════════════════════════════════════════════
```

### 5.2 Verification Phases

**Phase 1 - Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Dataset variance σ > 10% | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, benchmark invalid.

**Phase 2 - Core Mechanisms**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS |
| H-M2 | H-M1 | Should pass |
| H-M3 | H-M2 | Should pass |

→ **Gate 2**: H-M1 must pass. H-M2/H-M3 failures = documented limitations.

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │
─────────────────┼─────────┼─────────┼─────────┼
PHASE 1: Foundation
  H-E1           │ ████████│         │         │
  [Gate 1]       │        ◆│         │         │
─────────────────┼─────────┼─────────┼─────────┼
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │
  H-M2           │         │     ████│████     │
  H-M3           │         │         │    ████ │
  [Gate 2]       │         │         │       ◆ │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

**Total Duration:** 5 weeks
- Formula: 2 (H-E1) + 3 (H-M1-3) = 5 weeks

**Slack Available:** 0 weeks (all sequential)

### 5.5 Resource Summary

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1 to H-M3)
- Condition: 0

Verification Phases: 2
1. Foundation (H-E1)
2. Mechanisms (H-M1-3)

Execution Mode: Sequential chain

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Progressively adding structural inductive biases (layer-awareness → permutation alignment → permutation equivariance) improves accuracy prediction performance on Model Zoo.

**Supporting Evidence:**
1. Layer-wise processing preserves per-layer statistics correlated with functionality (Hyper-Representations)
2. Permutation alignment removes symmetry-induced variance (Git Re-Basin)
3. Permutation equivariance directly operates on symmetry-reduced representations (NFN)

**Strengths:**
- Based on established component techniques
- Clear mechanistic explanation for each step
- Testable predictions with quantitative thresholds

**Expected Outcomes:**
- Primary: Layer-wise > Flatten+MLP by Δr > 0.1
- Secondary: Layer-wise+GRB > Layer-wise by Δr > 0.05
- Tertiary: NFN > Layer-wise+GRB by Δr > 0.05

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference between Layer-wise+GRB and NFN. Alignment preprocessing suffices; architectural equivariance provides no additional benefit.

**Counter-Arguments:**
1. NFN may be overkill for property prediction (designed for generation)
2. GRB alignment already handles permutation symmetry
3. Added architectural complexity may not translate to prediction benefit

**Potential Failure Points:**
- R3: NFN adaptation may not preserve equivariance properties
- R4: GRB may not converge reliably, making comparison unfair
- R5: Effect size thresholds may be too strict or too lenient

**Conditions Under Which H0 Would Be Supported:**
- If NFN r ≤ Layer-wise+GRB r + 0.05
- If H-M3 fails while H-M2 passes
- If alignment preprocessing captures all relevant symmetry information

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-WeightStructure-v1 presents a testable claim that structural inductive biases progressively improve property prediction. However, the null hypothesis raises valid concerns that alignment preprocessing may suffice, making architectural equivariance unnecessary complexity.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes benchmark validity before mechanism tests
2. **Sequential mechanism testing (H-M1-3):** Tests each causal chain step independently
3. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- At least one of P2/P3 confirmed
- Progressive improvement pattern observed

**Conditions for Antithesis Support:**
- H-M3 fails while H-M2 passes → alignment suffices
- H-M1 fails → structural bias hypothesis itself questioned
- No significant improvement at any step

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis fully validated
2. **Partial Support (likely):** H-M1, H-M2 pass, H-M3 fails → Thesis validated to alignment level, equivariance unnecessary
3. **Minimal Support:** Only H-E1 passes → Structural bias approach needs rethinking
4. **No Support:** H-E1 fails → Benchmark invalid, restart with different data

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Benchmark valid | May be artifact | H-E1 test |
| Mechanism | Progressive improvement | Diminishing returns | H-M1-3 tests |
| Scope | Applies to Model Zoo | Limited to CNNs | Document |
| Performance | NFN best | GRB sufficient | H-M3 vs H0 |

**Overall Robustness Score:** Medium

**Confidence in Verification Plan:** 0.75

---

## 7. Conclusions

### 7.1 Key Achievements

- 4 hypotheses across 2 phases
- H0 addressed: Alignment vs equivariance tension explicitly tested in H-M3
- Clear falsification criteria at each step
- Either outcome (thesis or antithesis) is publishable

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Validate Model Zoo accuracy variance σ > 10%
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Layer-wise vs Flatten+MLP (Δr > 0.1)
- H-M2: Layer-wise+GRB vs Layer-wise (Δr > 0.05)
- H-M3: NFN vs Layer-wise+GRB (Δr > 0.05)
- Gate 2: H-M1 must pass

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, benchmark invalid
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → PIVOT hypothesis
   - H-M2/H-M3 FAIL → Document as limitation/H0 support

### 7.4 Open Questions

- Will effect size thresholds hold after calibration?
- Can NFN be successfully adapted for embedding extraction?
- Does Git Re-Basin converge reliably on Model Zoo architectures?

### 7.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 dataset validation
   - Set up measurement infrastructure (correlation, t-tests)

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path
   - Reserve 1 week buffer for failures

3. **Failure Management:**
   - Document all failures with details
   - Execute PIVOT strategies when needed
   - Either thesis or antithesis support is valuable

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-WeightStructure-v1)

### B. Established Facts (Not Re-Tested)
- Model Zoos provides ground-truth accuracy labels (Schurholt 2022)
- Hyper-Representations VAE learns weight embeddings (Schurholt 2022)
- NFN provides permutation-equivariant processing (Zhou 2024)
- Git Re-Basin aligns weights across symmetries (Ainsworth 2022)

### C. Scope Reduction
- 67% scope reduction from BUILD_ON claims
- Only PROVE_NEW claims require hypothesis generation

---

**Status:** Complete
**Steps Completed:** step-00 through step-10
**Completed At:** 2026-08-19
