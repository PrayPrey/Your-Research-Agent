# Verification Plan: Sample Efficiency of Permutation Equivariance in Weight Space Learning

**Date:** 2026-08-12
**Hypothesis ID:** H-EquivScale-v1
**Confidence:** 0.80
**Total Hypotheses:** 6

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under single-architecture CNN model zoos (50K+ models),
if permutation-equivariant architecture (NFN) versus matched-capacity non-equivariant baselines,
then NFN shows significant R² advantage for accuracy prediction at small data scales (N<5K)
that diminishes to non-significance at large scales (N>25K),
because equivariance provides implicit symmetry exploitation that MLPs can learn from data diversity at scale.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in R² between NFN and MLP-Matched at any data scale,
OR the NFN advantage is constant across scales (no diminishing returns pattern).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Model Zoo CIFAR-10 CNN Subset (standard) | 50K models provide sufficient scale for crossover detection; homogeneous architecture ensures valid permutation group |
| **Model** | NFN (Neural Functional Network) | Designed specifically for weight space learning with correct symmetry |

**Dataset Details:**
- Source: github.com/ModelZoos/ModelZooDataset
- Path: To be downloaded; single architecture family extracted

**Model Details:**
- Type: Permutation-equivariant encoder + regression head
- Source: pip install nfn (AllanYangZhou/nfn)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| MLP-Matched | TBD | Model Zoo |
| NFN-Scrambled | TBD | Model Zoo |
| Simple Statistics (mean/std/norm) | Unknown | Model Zoo |
| Random Features | Unknown | Model Zoo |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Model Zoo contains >10K single-architecture models | Model Zoo claims 50K+ total | Adjust scales or use multiple families |
| A2 | Architecture within family is truly homogeneous | Model Zoo documentation | Confound between architecture variation and equivariance |
| A3 | Accuracy labels span sufficient range (10%-90%) | Model Zoo models range from random to well-trained | Ceiling/floor effects limit discriminability |
| A4 | NFN pip implementation handles target weights | Prof. Pax code review; maintained package | Adapt NFN layers for weight formats |
| A5 | Probe invariance test validly measures learned symmetry | Direct test of output stability; face validity | Need alternative mechanism verification |

### 1.6 Research Gap & Novelty

**Key Innovation:** First systematic study of equivariance as sample efficiency mechanism in weight space learning.

**Differentiation:**
- NFN [Zhou et al., 2023]: Focused on generation; we focus on property prediction and scale analysis
- Hyper-Representations [Schurholt et al., 2022]: Used attention without equivariance claims
- Model Zoo [2022]: Provided dataset only; we provide architectural comparison

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |
| H-M5 | MECHANISM | SHOULD_WORK | H-M4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: NFN Advantage at Small Scale

**Type:** EXISTENCE
**Statement:** Under N=1K models, if NFN vs MLP-Matched, then NFN R² > MLP R² + 0.05 (p<0.05), because equivariance provides sample efficiency at small scales.

**Rationale:** Validates the core existence claim that permutation equivariance provides measurable benefit. Without this, no mechanism investigation is warranted.

**Variables:**
- Independent: Architecture Type (NFN vs MLP-Matched)
- Dependent: R² on accuracy prediction
- Controlled: N=1K, training protocol, test set, 10 seeds

**Verification Protocol:**
1. Train NFN and MLP-Matched on N=1K models with 10 seeds each
2. Compute R² on fixed 20% test set for each seed
3. Run one-sided paired t-test: NFN > MLP + 0.05
4. Report p-value, mean difference, 95% CI

**Success Criteria (PoC):**
- Primary: p < 0.05 AND mean R² difference > 0.05
- Secondary: Effect visible across majority of seeds

**Failure Response:**
- IF fails: ABANDON main hypothesis (equivariance provides no benefit)

**Dependencies:** None (foundation)

**Source:** Phase 2A SH1, Prediction P1

---

#### H-M1: NFN Equivariant Layers Encode Permutation Structure

**Type:** MECHANISM
**Statement:** Under standard NFN architecture, if NPLinear and HNPPool layers used, then outputs are permutation-invariant to weight ordering, because these layers are mathematically designed for equivariance.

**Rationale:** Validates that NFN architecture actually achieves the claimed equivariance property. This is the foundation of the causal mechanism.

**Variables:**
- Independent: Input weight permutation (identity vs random)
- Dependent: Output stability (correlation across permutations)
- Controlled: Same NFN weights, same input model

**Verification Protocol:**
1. Load trained NFN model
2. Feed same CNN weights with 10 random neuron permutations
3. Compute mean correlation of NFN outputs across permutations
4. Verify correlation > 0.99 (near-perfect invariance)

**Success Criteria (PoC):**
- Primary: Output correlation > 0.99 across permutations
- Secondary: No systematic drift with permutation

**Failure Response:**
- IF fails: PIVOT to check NFN implementation (bug in equivariance)

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Built-in Equivariance Makes NFN Predictions Invariant

**Type:** MECHANISM
**Statement:** Under trained NFN, if predictions made on permuted vs non-permuted weights, then predictions are identical, because architectural equivariance propagates to output.

**Rationale:** Confirms that equivariance property extends to final predictions, not just intermediate representations.

**Variables:**
- Independent: Weight permutation (applied vs not)
- Dependent: Prediction difference
- Controlled: Same trained NFN, same target model

**Verification Protocol:**
1. Take trained NFN from H-E1
2. Make accuracy prediction on CNN weights
3. Permute CNN weights randomly, predict again
4. Verify predictions match within floating point tolerance

**Success Criteria (PoC):**
- Primary: |pred_original - pred_permuted| < 1e-5
- Secondary: Consistent across multiple permutations

**Failure Response:**
- IF fails: DEBUG NFN architecture (broken implementation)

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: MLP Has No Built-in Permutation Awareness

**Type:** MECHANISM
**Statement:** Under untrained MLP at N=0, if tested on permuted weights, then outputs vary significantly, because MLP has no architectural symmetry constraints.

**Rationale:** Establishes baseline that MLP must learn invariance from data, it doesn't have it built-in.

**Variables:**
- Independent: Weight permutation
- Dependent: MLP output variance
- Controlled: Random MLP initialization

**Verification Protocol:**
1. Initialize random MLP (same architecture as MLP-Matched)
2. Feed same CNN weights with 10 random permutations
3. Compute output variance across permutations
4. Verify high variance (outputs should differ)

**Success Criteria (PoC):**
- Primary: Output correlation < 0.3 across permutations (random behavior)
- Secondary: Variance scales with permutation magnitude

**Failure Response:**
- IF fails: INVESTIGATE data leakage or unexpected structure

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

#### H-M4: At Small N, MLP Sees Insufficient Variation

**Type:** MECHANISM
**Statement:** Under N=1K training, if MLP trained and tested for probe invariance, then invariance < 0.5, because small datasets don't expose enough weight ordering variation.

**Rationale:** Explains WHY MLP fails at small scale - insufficient data diversity for learning invariance.

**Variables:**
- Independent: Training data size (N=1K)
- Dependent: Probe invariance score
- Controlled: Same MLP architecture, training protocol

**Verification Protocol:**
1. Train MLP-Matched on N=1K (from H-E1)
2. Compute probe invariance: mean correlation across 10 random permutations
3. Report probe invariance with 95% CI
4. Compare to NFN probe invariance (should be ~1.0)

**Success Criteria (PoC):**
- Primary: MLP probe invariance < 0.5 at N=1K
- Secondary: NFN probe invariance > 0.95

**Failure Response:**
- IF fails: MLP learns fast, revise mechanism theory

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4

---

#### H-M5: At Large N, Data Diversity Provides Symmetry Information

**Type:** MECHANISM
**Statement:** Under N=50K training, if MLP trained and tested for probe invariance, then invariance > 0.8, because large datasets expose sufficient ordering variation for learning.

**Rationale:** Core mechanism claim: MLPs CAN learn permutation invariance from data at scale.

**Variables:**
- Independent: Training data size (N=50K)
- Dependent: Probe invariance score
- Controlled: Same MLP architecture, training protocol

**Verification Protocol:**
1. Train MLP-Matched on N=50K (or max available)
2. Compute probe invariance: mean correlation across 10 random permutations
3. Report probe invariance with 95% CI
4. Plot probe invariance vs N across all scales

**Success Criteria (PoC):**
- Primary: MLP probe invariance > 0.8 at N=50K
- Secondary: Monotonic increase in invariance with N

**Failure Response:**
- IF fails: Alternative mechanism - MLP succeeds via memorization, not learned invariance

**Dependencies:** H-M4

**Source:** Phase 2A Causal Step 5, Prediction P4

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | p<0.05, diff>0.05 | ABANDON hypothesis |
| H-M1 | MUST_WORK | correlation>0.99 | DEBUG implementation |
| H-M2 | SHOULD_WORK | pred diff<1e-5 | DEBUG architecture |
| H-M3 | SHOULD_WORK | correlation<0.3 | INVESTIGATE leakage |
| H-M4 | SHOULD_WORK | invariance<0.5 | REVISE mechanism |
| H-M5 | SHOULD_WORK | invariance>0.8 | Alternative mechanism |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4, H-M5 | 5 weeks |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1: Insufficient single-arch models | H-E1, H-M4, H-M5 | HIGH |
| R2 | A2: Architecture heterogeneity | All H-M | MEDIUM |
| R3 | A3: Limited accuracy range | H-E1 | MEDIUM |
| R4 | A4: NFN implementation issues | H-M1, H-M2 | HIGH |
| R5 | A5: Probe test validity | H-M4, H-M5 | MEDIUM |

### 4.2 Mitigation Strategies

**R1: Insufficient Models**
- Prevention: Verify subset sizes before finalizing scales
- Detection: Check during data preparation
- Response: Use multiple architecture families if needed

**R2: Architecture Heterogeneity**
- Prevention: Filter for strict homogeneity
- Detection: Check layer shapes match exactly
- Response: Subset to homogeneous models only

**R3: Limited Accuracy Range**
- Prevention: Verify accuracy distribution
- Detection: Plot histogram during EDA
- Response: Use regression-appropriate metrics

**R4: NFN Implementation**
- Prevention: Run Prof. Pax code review
- Detection: H-M1 and H-M2 tests
- Response: Fix or adapt NFN layers

**R5: Probe Test Validity**
- Prevention: Use standard correlation metrics
- Detection: Check face validity
- Response: Add CKA similarity as backup

### 4.3 Risk Summary

| ID | Risk | Severity | Likelihood | Mitigation |
|----|------|----------|------------|------------|
| R1 | Model count | HIGH | LOW | Verify early |
| R2 | Heterogeneity | MEDIUM | LOW | Filter strictly |
| R3 | Accuracy range | MEDIUM | LOW | Check distribution |
| R4 | NFN bugs | HIGH | LOW | Code review |
| R5 | Probe validity | MEDIUM | MEDIUM | Add CKA backup |

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization
```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 6 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - MUST_WORK)
         │
         ▼
[Level 1-5 - Mechanisms]
    H-M1 (Equivariant layers) ← H-E1
         │
         ▼
    H-M2 (Prediction invariance) ← H-M1
         │
         ▼
    H-M3 (MLP no awareness) ← H-M2
         │
         ▼
    H-M4 (Small N insufficient) ← H-M3
         │
         ▼
    H-M5 (Large N sufficient) ← H-M4

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline
```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 6 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3 │ W4 │ W5 │ W6 │ W7 │
─────────────────┼──────┼────┼────┼────┼────┼────┤
PHASE 1: Foundation
  H-E1           │██████│    │    │    │    │    │
  [Gate 1]       │      │ ◆  │    │    │    │    │
─────────────────┼──────┼────┼────┼────┼────┼────┤
PHASE 2: Mechanisms
  H-M1           │      │████│    │    │    │    │
  H-M2           │      │    │████│    │    │    │
  H-M3           │      │    │    │████│    │    │
  H-M4           │      │    │    │    │████│    │
  H-M5           │      │    │    │    │    │████│
  [Gate 2]       │      │    │    │    │    │   ◆│
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

- **Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5
- **Total Duration:** 7 weeks (2 + 5)
- **Slack Available:** 0 weeks (all sequential)
- **Execution Mode:** Sequential chain

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Permutation equivariance provides sample efficiency benefits in weight space learning that diminish as data scale increases.

**Supporting Evidence:**
1. NFN architecture mathematically guarantees permutation invariance (Zhou et al., 2023)
2. MLPs lack built-in symmetry constraints - must learn from data
3. Universal approximation theorem supports eventual MLP convergence at scale

**Strengths:**
- Clear causal mechanism with testable steps
- Grounded in established theory (equivariance, UAT)
- Four pre-registered predictions with quantitative thresholds

**Expected Outcomes:**
- P1: NFN R² > MLP R² + 0.05 at N=1K (p<0.05)
- P2: NFN R² > NFN-Scrambled R² + 0.05 at N=1K
- P3: |NFN - MLP| < 0.02 at N=50K (equivalence)
- P4: MLP probe invariance > 0.8 at N=50K

### 6.2 Antithesis

**Null Hypothesis (H0):** No significant difference between NFN and MLP at any scale, OR constant NFN advantage (no diminishing returns).

**Counter-Arguments:**
1. MLPs may learn order-sensitive statistics sufficient for prediction
2. Equivariance may be unnecessary if data contains sufficient signal
3. NFN-Scrambled may still work if any structure helps

**Potential Failure Points:**
- R1: Insufficient model count invalidates scale study
- R4: NFN implementation bugs mask true equivariance
- H-M5 fails: MLP succeeds via memorization, not learned invariance

**Conditions Under Which H0 Would Be Supported:**
- H-E1 fails: No NFN advantage at small scale
- P3 fails: NFN advantage persists at large scale
- P4 fails: MLP probe invariance stays low despite matching R²

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-EquivScale-v1 presents a testable claim about equivariance as a sample efficiency mechanism. The null hypothesis raises valid concerns about alternative explanations (memorization, order-sensitive statistics).

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes advantage exists before investigating mechanism
2. **Sequential mechanism testing (H-M1-5):** Tests each causal step independently
3. **Probe invariance test (H-M4, H-M5):** Directly tests mechanism claim, not just performance

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- P1-P4 are confirmed
- MLP probe invariance increases with N

**Conditions for Antithesis Support:**
- H-E1 fails: Equivariance provides no benefit
- H-M5 fails but P3 passes: MLP succeeds via different mechanism

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** H-M5 fails → Refined thesis (alternative mechanism)
3. **No Support:** H-E1 fails → Antithesis supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | NFN > MLP at small N | May be marginal | H-E1 quantitative test |
| Mechanism | Equivariance is key | Alternative explanations | H-M1-M5 chain |
| Scale Effect | Advantage diminishes | May persist | P3 TOST equivalence |
| Learned Invariance | MLP learns from data | May memorize instead | H-M5 probe test |

**Overall Robustness Score:** HIGH
**Confidence in Verification Plan:** 0.80

---

## 7. Executive Summary

**Main Hypothesis:** Under single-architecture CNN model zoos, NFN shows R² advantage at small scales (N<5K) that diminishes at large scales (N>25K), because equivariance provides symmetry exploitation MLPs must learn from data.
- ID: H-EquivScale-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 6 total (H-E: 1, H-M: 5)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 (H-E1: MUST_WORK, H-M1: MUST_WORK)

**Risk Assessment:** MEDIUM
- Primary concerns: R1 (model count), R4 (NFN implementation)

**Immediate Action:** Begin Phase 1 with H-E1

---

## 8. Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-EquivScale-v1)
- **Generated:** 2026-08-12
- **Scope Reduction:** 40% (4/6 claims are BUILD_ON)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 2
- **Tools:** mcp__clearThought__scientificmethod (hypothesis, experiment stages)

### C. Files Generated
- 02b_verification_plan.md (this document)
- verification_state.yaml (Phase 2C integration)
