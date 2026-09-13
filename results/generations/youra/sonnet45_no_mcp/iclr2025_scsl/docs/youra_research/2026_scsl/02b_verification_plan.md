# Verification Plan: Loss Landscape Geometry and Spurious Correlation Robustness

**Date:** 2026-04-24
**Hypothesis ID:** H-GeometricRobustness-v1
**Confidence:** 0.80
**Total Hypotheses:** 5 (1 Existence + 4 Mechanism)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard ERM training on datasets with spurious correlations (Waterbirds, CelebA), if we measure curvature subspace orientation via Marchenko-Pastur-defined Hessian outlier eigenvectors, then solutions with high minority-gradient alignment to this subspace will exhibit poor worst-group accuracy, because SGD dynamics preferentially flow along locally flat directions away from sharp, spurious-feature-aligned curvature concentrations.

### 1.2 Alternative Hypothesis (H0)

There is no systematic relationship between Marchenko-Pastur subspace alignment A(w) and worst-group accuracy. Geometric curvature orientation does not predict or explain robustness to distribution shift.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (primary), CelebA + Colored MNIST (cross-validation) (standard) | Ground-truth spurious labels enable behavioral phenotyping (spurious vs core solutions). Waterbirds: background spurious correlation, CelebA: gender-attribute correlation, Colored MNIST: color-digit correlation |
| **Model** | ResNet-50 (Standard CNN with skip connections) | Li et al. show ResNets produce analyzable loss landscapes with skip connections creating flat minima. Sufficient over-parameterization for Marchenko-Pastur assumptions. Standard architecture enables reproducibility. |

**Dataset Details:**
- Source: group_DRO repository (https://github.com/kohpangwei/group_DRO)
- Path: Downloaded via group_DRO scripts

**Model Details:**
- Type: Standard CNN with skip connections
- Source: torchvision.models

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard ERM | 85-90% average, 60-75% worst-group | Waterbirds, CelebA |
| Group-DRO | 75-80% worst-group (requires group labels) | Waterbirds, CelebA |
| Fast Geometric Ensembling (FGE) | Cyclical learning rate sampling | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Marchenko-Pastur bulk edge accurately identifies signal vs noise eigenvalue threshold | Random matrix theory for large over-parameterized networks; validated in Sagun et al. | Subspace definition becomes arbitrary, alignment metric unstable |
| A2 | Minority-group gradients reliably indicate spurious-vs-core feature directions | Group-DRO theory: minority groups expose shortcuts; worst-group accuracy measures spurious reliance | Alignment metric overfits subgroup sampling noise rather than structural geometry |
| A3 | Curvature orientation is more stable than magnitude across batch sizes and parameterizations | Sagun shows magnitude depends on batch size; orientation reflects data structure | Geometric signature collapses under hyperparameter variation |
| A4 | SGD implicit bias toward flat directions creates directional flow in optimization dynamics | Extensive literature on flatness-generalization link; SAM (Foret 2020) exploits this | No mechanism linking local geometry to trajectory preference |
| A5 | Mode connectivity doesn't preclude functional variation within connected components | Garipov shows connectivity; Sagun shows geometric variation within basins | FGE test would show geometric variation without phenotype shifts |

### 1.6 Research Gap & Novelty

**Primary Contribution:** First mechanistic framework linking loss landscape curvature ORIENTATION to spurious correlation robustness via distribution-shift-aware subspace alignment.

**Differentiation from Prior Work:**
- **vs SAM (Foret 2020):** SAM targets scalar flatness (feature-agnostic). We target curvature orientation relative to subgroup gradients (distribution-shift-aware). SAM is optimization technique; we provide diagnostic + explanation.
- **vs Group-DRO (Sagawa 2020):** Group-DRO is a solution that fixes the problem. We explain WHY ERM fails via geometric mechanism and enable label-free early diagnostics via A(w) monitoring.
- **vs Loss landscape analysis (Sagun 2017, Li 2018, Garipov 2018):** They study architecture/optimization effects on landscapes. We apply their tools to spurious correlation domain—novel synthesis rather than novel methods.

**Builds on Established:**
- Marchenko-Pastur theory for signal/noise separation (Sagun et al. 2017)
- Filter normalization for visualization (Li et al. 2018)
- Mode connectivity and FGE sampling (Garipov et al. 2018)
- Group-DRO benchmarks with ground-truth labels (Sagawa et al. 2020)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Prerequisites | Gate | Status |
|----|------|-------------------|---------------|------|--------|
| H-E1 | Existence | ERM vs DRO solutions show distinct MP-subspace alignment | None | MUST_WORK | READY |
| H-M1 | Mechanism | Sharp curvature concentrates in Hessian outlier subspace | H-E1 | MUST_WORK | NOT_STARTED |
| H-M2 | Mechanism | Sharp directions align with minority gradients (high A(w)) | H-M1 | SHOULD_WORK | NOT_STARTED |
| H-M3 | Mechanism | SGD flows along flat directions avoiding sharp curvature | H-M2 | SHOULD_WORK | NOT_STARTED |
| H-M4 | Mechanism | Lower A(w) solutions exhibit better worst-group robustness | H-M3 | SHOULD_WORK | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
#### H-E1: Geometric Signature Exists

**Type:** EXISTENCE

**Statement:** Under standard ERM and Group-DRO training on Waterbirds, if we measure Marchenko-Pastur-defined curvature subspace alignment A(w), then ERM solutions will exhibit significantly higher alignment than Group-DRO solutions, because ERM exploits spurious features that create sharp, concentrated curvature.

**Rationale:**
This hypothesis establishes that the geometric signature (curvature orientation difference) exists and is measurable. It validates that ERM and DRO solutions occupy geometrically distinct regions before testing the causal mechanism.

**Variables:**
- Independent: Training Method (ERM vs Group-DRO)
- Dependent: Curvature Subspace Alignment A(w) = ||P_S_out g_minority||² / ||g_minority||²
- Controlled: Batch size (32, 128, 512), Architecture (ResNet-50), Random seed (20 runs)

**Verification Protocol:**
1. Train 20 seeds each of ERM and Group-DRO on Waterbirds dataset
2. At convergence, compute Hessian eigendecomposition and fit Marchenko-Pastur distribution
3. Calculate A(w) for each trained model using minority-group gradients
4. Perform two-sample t-test comparing ERM vs DRO alignment distributions
5. Verify effect size (Cohen's d) and stability across batch sizes

**Success Criteria (PoC: Direction-based):**
- Primary: ERM alignment > DRO alignment (p<0.01, Cohen's d>0.8)
- Secondary: Effect stable across 3 batch sizes (32, 128, 512)

**Failure Response:**
- IF fails: PIVOT to alternative geometric metrics or ABANDON geometric explanation

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.6 Prediction P1

---
#### H-M1: Spurious Features Create Sharp Curvature

**Type:** MECHANISM (Step 1 of 4)

**Statement:** Under ERM training on Waterbirds, if spurious features dominate learning, then sharp curvature will concentrate in specific Hessian eigenspace subspaces (outliers beyond MP bulk edge), because Gauss-Newton decomposition shows Hessian outliers align with data structure.

**Rationale:**
First causal link: establishes that spurious features create measurable sharp curvature concentrations in specific eigenspace directions, not just global flatness differences.

**Variables:**
- Independent: Feature type (spurious-dominated vs core-dominated solutions)
- Dependent: Hessian eigenvalue spectrum structure (outlier count, MP bulk edge)
- Controlled: Architecture, dataset, training hyperparameters

**Verification Protocol:**
1. Train ERM models to convergence on Waterbirds
2. Compute full Hessian eigenvalue spectrum via power iteration + deflation
3. Fit Marchenko-Pastur distribution to identify bulk vs outlier eigenvalues
4. Compare eigenvalue spectra between ERM (spurious) and DRO (core) solutions
5. Validate via Gauss-Newton decomposition showing outlier-data structure alignment

**Success Criteria (PoC: Direction-based):**
- Primary: ERM shows more outlier eigenvalues than DRO (distinguishable spectra)
- Secondary: Outlier count correlates with spurious reliance (worst-group accuracy)

**Failure Response:**
- IF fails: EXPLORE alternative curvature metrics or reconsider MP threshold

**Dependencies:** H-E1 (existence of geometric distinction)

**Source:** Phase 2A Section 1.3 Causal Step 1

---
#### H-M2: Sharp Directions Align with Minority Gradients

**Type:** MECHANISM (Step 2 of 4)

**Statement:** Under ERM training, if sharp curvature exists in outlier subspace (H-M1), then these sharp directions will align with minority-group gradient directions (high A(w)), because minority groups expose spurious correlations and their gradients point toward spurious-feature directions.

**Rationale:**
Second causal link: connects geometric structure (sharp curvature from H-M1) to behavioral signature (minority gradient alignment), explaining why A(w) metric captures spurious reliance.

**Variables:**
- Independent: Minority-group gradient direction
- Dependent: Alignment A(w) with outlier subspace
- Controlled: Subspace definition (from H-M1), gradient batch composition

**Verification Protocol:**
1. Using H-M1 outlier subspace S_out, compute minority-group gradients g_minority
2. Calculate alignment A(w) = ||P_S_out g_minority||² / ||g_minority||²
3. Compare alignment for minority vs majority gradients
4. Test correlation between A(w) and worst-group accuracy across seeds
5. Verify alignment is not arbitrary (randomization test with shuffled subspaces)

**Success Criteria (PoC: Direction-based):**
- Primary: Minority gradient alignment > majority gradient alignment (significant difference)
- Secondary: A(w) correlates with worst-group accuracy (ρ>0.6, p<0.01)

**Failure Response:**
- IF fails: EXPLORE alternative gradient definitions or minority group sampling strategies

**Dependencies:** H-M1 (sharp curvature subspace identified)

**Source:** Phase 2A Section 1.3 Causal Step 2

---
#### H-M3: SGD Flows Along Flat Directions

**Type:** MECHANISM (Step 3 of 4)

**Statement:** During training, if sharp curvature exists in specific directions (H-M2), then SGD dynamics will preferentially follow locally flat directions to minimize curvature-induced gradient variance, because well-documented SGD implicit bias toward flat minima creates directional flow.

**Rationale:**
Third causal link: explains optimization dynamics—WHY high A(w) solutions emerge from SGD (flatness bias) rather than being artifacts of final solutions.

**Variables:**
- Independent: Local curvature landscape (flat vs sharp directions)
- Dependent: SGD trajectory direction (measured via gradient alignment over time)
- Controlled: Learning rate, momentum, batch size

**Verification Protocol:**
1. Track SGD trajectories during training via gradient direction logging
2. Measure directional bias: correlation between gradient steps and eigenvector directions
3. Calculate curvature-induced gradient variance along different directions
4. Verify that SGD steps preferentially align with low-curvature (flat) directions
5. Test early-epoch A(w) prediction of final trajectory (forecasting power)

**Success Criteria (PoC: Direction-based):**
- Primary: SGD steps align more with flat directions than sharp directions (measured bias)
- Secondary: Early A(w) (10% training) predicts final robustness (incremental R²>10% beyond λ_max)

**Failure Response:**
- IF fails: EXPLORE alternative optimization dynamics or reconsider SGD implicit bias assumption

**Dependencies:** H-M2 (minority gradient alignment established)

**Source:** Phase 2A Section 1.3 Causal Step 3, Prediction P3

---
#### H-M4: Lower A(w) Solutions Show Better Robustness

**Type:** MECHANISM (Step 4 of 4)

**Statement:** At convergence, if solutions have lower minority-gradient alignment A(w) (from H-M3 SGD flow), then they will exhibit better worst-group accuracy, because functional coupling between geometry and phenotype within mode-connected manifolds means geometric regions determine robustness outcomes.

**Rationale:**
Final causal link: validates functional coupling—geometry (A(w)) predicts phenotype (worst-group accuracy), not just correlation but causal relationship via FGE sampling.

**Variables:**
- Independent: Curvature alignment A(w)
- Dependent: Worst-group accuracy (WGA)
- Controlled: Architecture, dataset, connectivity path (FGE vs linear)

**Verification Protocol:**
1. Sample solutions along FGE-optimized paths (M=20 checkpoints between ERM and DRO)
2. For each checkpoint, compute A(w) and measure worst-group accuracy
3. Calculate Spearman correlation ρ(A(w), WGA) to test monotonic coupling
4. Validate via linear interpolation (simpler path, no optimization)
5. Test robustness to 10% minority label noise

**Success Criteria (PoC: Direction-based):**
- Primary: FGE shows strong coupling ρ(A(w), WGA) > 0.6, p<0.01
- Secondary: Linear interpolation shows monotonic coupling ρ>0.7

**Failure Response:**
- IF fails: Document as geometry variation without phenotype variation (falsifies A5)

**Dependencies:** H-M3 (SGD flow dynamics established)

**Source:** Phase 2A Section 1.3 Causal Step 4, Predictions P2 & P5

---

---

## 3. Risk Analysis

### 3.1 Risk Identification from Assumptions

| Risk ID | Source | Description | Severity | Affected Hypotheses |
|---------|--------|-------------|----------|---------------------|
| R1 | A1 | Marchenko-Pastur bulk edge estimation unstable under non-Gaussian initialization or heavy-tailed activations | High | H-E1, H-M1, H-M2 |
| R2 | A2 | Minority-group gradients may overfit subgroup sampling noise rather than structural geometry | Medium | H-M2, H-M4 |
| R3 | A3 | Curvature orientation may collapse under hyperparameter variation (batch size, architecture) | High | All H-M* |
| R4 | A4 | SGD implicit bias assumption may not hold for all optimizers or learning rate schedules | Medium | H-M3 |
| R5 | A5 | Mode connectivity may show geometry variation without phenotype variation (FGE test failure) | High | H-M4 |

### 3.2 Mitigation Strategies

**Risk R1: MP Edge Estimation Instability**
- **Prevention:** Test multiple edge-detection methods (MP fit, spectral gap, fixed percentile)
- **Detection:** Visual inspection of eigenvalue spectrum fit quality, residual analysis
- **Response:**
  - PIVOT: Use spectral gap method if MP fit unstable
  - SCOPE: Restrict to architectures/initializations with validated MP assumptions
  - ABORT: If no stable edge definition across conditions

**Risk R2: Minority Gradient Noise Overfitting**
- **Prevention:** Compare alignment using different minority definitions (balanced sampling)
- **Detection:** Randomization test—shuffle group labels and check if A(w) correlation collapses
- **Response:**
  - PIVOT: Use averaged gradients over multiple minority batches
  - SCOPE: Report as methodology limitation
  - ABORT: If correlation collapses under label shuffling

**Risk R3: Orientation Instability**
- **Prevention:** Batch size ablation study (32, 128, 512) as validation requirement
- **Detection:** Track orientation stability metric across hyperparameters
- **Response:**
  - PIVOT: Normalize or stabilize orientation metric
  - SCOPE: Document valid hyperparameter ranges
  - ABORT: If effect disappears under variation (d<0.5)

**Risk R4: Optimizer Dependence**
- **Prevention:** Test with SGD, Adam, momentum variants
- **Detection:** Compare SGD trajectory bias across optimizers
- **Response:**
  - PIVOT: Focus on SGD-specific claims
  - SCOPE: Generalize to "gradient-descent family" not all optimizers
  - ABORT: If effect specific to vanilla SGD only

**Risk R5: Geometry-Phenotype Decoupling**
- **Prevention:** Both FGE (optimized) and linear interpolation (simple) path tests
- **Detection:** Low ρ(<0.3) on FGE coupling test
- **Response:**
  - PIVOT: Investigate alternative geometric metrics
  - SCOPE: Geometry exists but doesn't drive robustness
  - ABORT: If both FGE and linear show no coupling

---

## 4. Execution Plan

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH - 5 Hypotheses (Sequential Chain)
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - Geometric Signature)
         │
         ▼
    [Gate 1: MUST_WORK]
         │
         ▼
[Level 1 - Mechanism Chain]
    H-M1 (Sharp Curvature Concentration)
         │
         ▼
    H-M2 (Minority Gradient Alignment)
         │
         ▼
    H-M3 (SGD Flatness Bias)
         │
         ▼
    H-M4 (Geometry-Robustness Coupling)
         │
         ▼
    [Gate 2: Mechanism Validated]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════
```

### 4.2 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ Week 1-2 │ Week 3  │ Week 4  │ Week 5  │ Week 6  │
─────────────────┼──────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████ │         │         │         │         │
  [Gate 1]       │          │ ◆       │         │         │         │
─────────────────┼──────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanism Chain
  H-M1           │          │ ████    │         │         │         │
  H-M2           │          │         │ ████    │         │         │
  H-M3           │          │         │         │ ████    │         │
  H-M4           │          │         │         │         │ ████    │
  [Gate 2]       │          │         │         │         │       ◆ │
─────────────────┼──────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 4.3 Gate Conditions

**Gate 1 (Foundation):** MUST_WORK
- **Hypothesis:** H-E1
- **Pass Condition:** ERM vs DRO alignment distributions significantly different (p<0.01, d>0.8)
- **Fail Action:** STOP—geometric signature doesn't exist, abandon hypothesis

**Gate 2 (Mechanism Chain):** MUST_WORK for H-M1, SHOULD_WORK for H-M2-4
- **Critical:** H-M1 must pass (sharp curvature exists)
- **Optional:** H-M2-4 failures document limitations but don't invalidate
- **Fail Action:** PIVOT to refined mechanism or document boundary conditions

### 4.4 Execution Order

**Step 1:** Execute H-E1 (Foundation) - Week 1-2
**Step 2:** Evaluate Gate 1 → If pass, proceed to mechanisms
**Step 3:** Execute H-M1 (Sharp curvature) - Week 3
**Step 4:** Execute H-M2 (Minority alignment) - Week 4
**Step 5:** Execute H-M3 (SGD flow) - Week 5
**Step 6:** Execute H-M4 (Coupling validation) - Week 6
**Step 7:** Evaluate Gate 2 → Synthesis and Phase 4.5 transition
**Final:** Verification complete, proceed to Phase 5 (Baseline Comparison)

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:**
Curvature subspace orientation relative to minority gradients (Marchenko-Pastur-defined alignment A(w)) mechanistically explains spurious correlation dominance in ERM training and predicts worst-group robustness.

**Supporting Evidence:**
1. Gauss-Newton decomposition (Sagun et al.) links Hessian outliers to data structure
2. Group-DRO theory establishes minority groups expose spurious shortcuts
3. SGD implicit bias toward flat minima is well-documented (SAM, mode connectivity)
4. Testable predictions provide 5 independent falsification opportunities

**Strengths:**
- Intrinsic geometric definition (MP edge, no arbitrary thresholds)
- 4-step causal mechanism with per-step falsifiers
- Builds on validated tools (Li, Sagun, Garipov methods)

**Expected Outcomes:**
- Primary: ERM > DRO alignment (P1), FGE coupling ρ>0.6 (P2)
- Secondary: Early prediction beyond λ_max (P3), noise robustness (P4)

### 5.2 Antithesis (H0-Based)

**Null Hypothesis:**
There is no systematic relationship between Marchenko-Pastur subspace alignment A(w) and worst-group accuracy. Geometric curvature orientation does not predict or explain robustness to distribution shift.

**Counter-Arguments:**
1. **Baseline limitations:** Group-DRO requires labels (impractical), SAM is feature-agnostic (doesn't explain spurious reliance)
2. **Assumption violations:** A1-A5 could fail (MP unstable, minority gradients noisy, orientation collapses)
3. **Scope limitations:** May not extend to self-supervised learning, under-parameterized models, non-SGD optimizers

**Potential Failure Points:**
- R1: MP edge estimation unstable → arbitrary subspace definition
- R3: Orientation collapses under hyperparameter variation → not intrinsic property
- R5: FGE shows geometry variation without phenotype coupling → correlation without causation

**Conditions Supporting H0:**
- ERM and DRO alignment distributions overlap (d<0.5)
- Early A(w) fails to predict robustness when controlling for λ_max (p>0.05)
- FGE coupling weak or non-monotonic (ρ<0.3)

### 5.3 Synthesis

**Balanced Assessment:**
The hypothesis H-GeometricRobustness-v1 presents a testable mechanistic explanation for spurious correlation dominance via loss landscape geometry. However, the null hypothesis raises valid concerns regarding MP edge stability, minority gradient noise, and geometry-phenotype coupling assumptions.

**Resolution Path:**
The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes geometric signature before mechanism
2. **Sequential mechanism testing (H-M1-4):** Each step independently falsifiable
3. **Gate conditions:** Allow early detection of H0 support with pivot strategies

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- Primary predictions confirmed (P1: alignment difference, P2: FGE coupling)
- Mechanism chain validates sequentially with stable geometric signatures

**Conditions for Antithesis Support:**
- H-E1 fails (no geometric signature) → full support for H0
- H-M1 fails (sharp curvature doesn't concentrate) → mechanism broken
- Orientation instability across batch sizes (R3) → not intrinsic property

**Nuanced Outcome Possibilities:**
1. **Full Support:** All 5 hypotheses pass → Thesis validated, publish mechanism
2. **Partial Support:** H-E1+H-M1-2 pass, H-M3-4 fail → Refined thesis with scope limitations
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported, pivot to alternative explanations

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Geometric signature exists (ERM ≠ DRO) | May be dataset artifact | H-E1 cross-validation (3 datasets) |
| Mechanism | 4-step causal chain valid | Alternative explanations possible | Sequential H-M* with per-step falsifiers |
| Scope | Applies to SGD-trained deep networks | Limited to specific conditions | Scope boundaries documented (A3, A4) |
| Prediction | A(w) forecasts robustness | Correlation without causation | FGE coupling test (P2) validates causation |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.80 (matches Phase 2A confidence)

---

## 6. Executive Summary

**Main Hypothesis:** Curvature subspace orientation (MP-defined A(w)) explains spurious correlation dominance
- ID: H-GeometricRobustness-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-analysis)
- Sub-Hypotheses: 5 total
  - H-E: 1 (Existence), H-M: 4 (Mechanism chain)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Foundation, Mechanism)

**Risk Assessment:** Medium-High
- Primary concerns: MP edge stability (R1), orientation instability (R3), geometry-phenotype decoupling (R5)

**Immediate Action:** Begin Phase 1 with H-E1 (geometric signature validation)

---

## 7. Conclusions

### 7.1 Key Achievements
- 5 hypotheses across 2 verification phases
- H0 explicitly addressed with dialectical analysis
- Scope reduction: 25% (3 BUILD_ON claims from Phase 2A)

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: ERM vs DRO solutions show distinct MP-subspace alignment
- Gate 1: MUST PASS

**Phase 2: Mechanism Chain** (4 weeks)
- H-M1: Sharp curvature concentrates in Hessian outlier subspace
- H-M2: Sharp directions align with minority gradients
- H-M3: SGD flows along flat directions avoiding sharp curvature
- H-M4: Lower A(w) solutions exhibit better worst-group robustness
- Gate 2: H-M1 must pass, H-M2-4 should pass

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess entire hypothesis
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanism):** H-M1 must pass
   - CRITICAL FAIL → Execute pivot strategy (alternative geometric metrics)
   - OPTIONAL FAIL (H-M2-4) → Document limitation, narrow scope

### 7.4 Open Questions
- How does parameterization invariance affect alignment metric stability across layer types?
- Can we extend to self-supervised learning where minority gradients are not well-defined?
- Does MP edge estimation remain stable under non-Gaussian initialization or heavy-tailed activations?

### 7.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 2C (Experiment Design) for H-E1
   - Set up Hessian computation infrastructure (pytorch-hessian-eigenthings)
   - Prepare Waterbirds dataset with group annotations

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path execution
   - Reserve 2-week buffer for failure pivots
   - Single GPU sufficient (ResNet-50 scale)

3. **Failure Management:**
   - Document all failures with SUPERSEDED routing to Serena memory
   - Execute PIVOT strategies per risk mitigation plans (Section 3.2)
   - Maintain hypothesis versioning (max 3 modifications per ID)

---

## Appendices

### A. Phase 2A Reference
- **Source:** /home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_scsl_3/docs/youra_research/20260421_scsl/03_refinement.yaml
- **Hypothesis ID:** H-GeometricRobustness-v1
- **Discussion Exchanges:** 15 (convergence achieved)

### B. Workflow Execution
- **Workflow:** phase2b-planning v7.7.0
- **Mode:** UNATTENDED (batch-mode auto-execution)
- **Date:** 2026-04-24

---

*Generated by YouRA Phase 2B Planning Workflow | 2026-04-24*
