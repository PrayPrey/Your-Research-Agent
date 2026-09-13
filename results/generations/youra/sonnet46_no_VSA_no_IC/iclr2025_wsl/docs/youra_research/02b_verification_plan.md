---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory"]
status: in_progress
hypothesis_id: H-EquivSampleEfficiency-v1
research_mode: incremental
total_hypothesis_count: 4
causal_chain_count: 3
condition_hypothesis_count: 0
scope_reduction_percentage: 83
requires_transfer_validation: false
---

# Verification Plan: Equivariant Weight-Space Encoders Are More Sample-Efficient Than Plain Encoders

**Date:** 2026-08-21
**Hypothesis ID:** H-EquivSampleEfficiency-v1
**Confidence:** 0.78
**Total Hypotheses:** 4

---

## 0. Established Facts & Scope Reduction

**Scope Reduction: 83%** (5 of 6 claims are BUILD_ON — not re-verified)

| Claim | Status | Evidence |
|-------|--------|----------|
| Permutation equivariance is a symmetry of neural network weight spaces | BUILD_ON | DWSNets [Navon 2023]; NFN [Zhou 2023] |
| All permutation-equivariant weight-space networks have equivalent expressive power | BUILD_ON | Dayan et al. 2026 [arXiv:2602.01083] |
| Plain SSL on flattened weights can predict model accuracy from weights alone | BUILD_ON | Schürholt et al. 2021 — R²≈0.83 |
| ModelZooDataset provides standardized model zoos with ground-truth metrics | BUILD_ON | Schürholt et al. 2022 [arXiv:2209.14764] |
| Equivariant encoders achieve SOTA on property prediction but use different splits | BUILD_ON | DWSNets R²≈0.89; GNN-NFN SOTA (no unified comparison) |
| Whether equivariant inductive bias provides sample efficiency advantage | **PROVE_NEW** | No controlled comparison on shared splits in any published work |

**Phase 2B-4 Scope:** Only Claim 6 (sample efficiency advantage on shared splits) requires experimental validation. Claims 1–5 are treated as pre-validated foundations.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the weight-space property prediction setting using the ModelZooDataset MNIST and CIFAR-10 model zoos with standardized shared train/test splits, if we train equivariant weight-space encoders (DWSNets, GNN-NFN) versus plain encoders (flat-MLP, flat-MLP + permutation augmentation) at matched parameter budget ranges across systematically varied training set sizes {100, 250, 500, 1000, full}, then equivariant encoders will demonstrate superior sample efficiency — reaching ≥90% of their peak accuracy-prediction R² at ≤50% of the training set size required by plain encoders to reach the same relative threshold — because permutation equivariance constrains the hypothesis space to symmetry-consistent functions, reducing the effective sample complexity of learning weight-space property mappings.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in the training-size-normalized R² efficiency between equivariant encoders and plain encoders for weight-space accuracy prediction on ModelZooDataset; the 90%/50% threshold is not met, or the gap is within bootstrap confidence interval overlap.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ModelZooDataset MNIST + CIFAR-10 Model Zoos (standard) | Standardized model zoos with ground-truth performance metrics; MNIST (~4,860 models) and CIFAR-10 (~9,000 models) provide two independent scales |
| **Model** | 4-condition encoder comparison (Multi-architecture ablation) | Directly tests IV with all public implementations; flat-MLP is ~50 lines PyTorch |

**Dataset Details:**
- Source: Schürholt et al. 2022 [arXiv:2209.14764]
- Path: https://github.com/ModelZoos/ModelZooDataset

**Model Details:**
- Type: Multi-architecture ablation
- Source: DWSNets (github.com/AvivNavon/DWSNets), GNN-NFN (github.com/mkofinas/neural-graphs), custom flat-MLP

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| DWSNets [Navon et al. 2023] | R²≈0.89 accuracy prediction | Private MNIST zoo (own splits — not shared) |
| Schürholt SSL [2021] | R²≈0.83 accuracy prediction | ModelZooDataset MNIST zoo (standard splits) |
| GNN-NFN [Kofinas et al. 2024] | SOTA on multiple property prediction tasks | Custom per-architecture splits |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | ModelZooDataset provides sufficient model diversity (systematic HP variation) | Schürholt 2022 zoo construction; R²≈0.83 suggests meaningful signal | Both encoders trivially achieve high R² with few models — efficiency comparison meaningless |
| A2 | Parameter-count range matching provides fair comparison | Prior work uses parameter count as standard fairness control | Gains attributed to architecture depth/width rather than equivariance; must run architecture search |
| A3 | Permutation augmentation is a valid approximation of equivariance (not full replication) | Data augmentation achieves some but not all benefits of architectural invariance | Augmentation fully replicates structural equivariance → distinction is practically irrelevant |
| A4 | MNIST and CIFAR-10 model zoo tasks representative of general weight-space property prediction | Standard CNNs widely studied; two zoo scales tested | Efficiency gap is architecture-size-specific only |
| A5 | Fixed Adam optimizer/LR (tuned on full data) provides fair comparison across training sizes | Standard practice in learning curve studies | Plain-MLP benefits from different LR at small sizes → comparison unfair |

### 1.6 Research Gap & Novelty

All prior equivariant weight-space papers (DWSNets, GNN-NFN, NFN) benchmark on private/custom splits preventing direct comparison. Schürholt 2021 provides the only plain baseline on ModelZooDataset but never compares to equivariant methods on the same data. Dayan et al. 2026 proves expressivity equivalence but provides no empirical efficiency data.

**Key Innovation:** First controlled comparison of equivariant vs. plain weight-space encoders on shared ModelZooDataset splits at multiple training sizes; first empirical sample efficiency curve for weight-space encoders; permutation augmentation as mechanistic ablation condition.

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
**H-E1: Sample Efficiency Advantage Exists on Shared Splits**

**Statement:** Under the weight-space property prediction setting using ModelZooDataset MNIST and CIFAR-10 model zoos with standardized shared splits, if we train equivariant encoders (DWSNets, GNN-NFN) vs. plain Flat-MLP at matched parameter budget ranges at training sizes {100, 250, 500}, then equivariant encoders will show measurably higher accuracy-prediction R² with non-overlapping bootstrap 95% CIs at ≥1 training size, because the permutation equivariance inductive bias reduces effective sample complexity.

**Rationale:** This existence hypothesis establishes the empirical phenomenon before testing the causal mechanism. Dayan et al. 2026 proves expressivity equivalence — so if equivariant encoders show higher R² at low data, efficiency (not capability ceiling) is the differentiator. Without H-E1, mechanism testing is pointless.

**Variables:**
- Independent: Encoder Architecture Type (DWSNets/GNN-NFN vs Flat-MLP); Training Set Size (100, 250, 500)
- Dependent: Test-Set Accuracy Prediction R² on fixed held-out ModelZooDataset models
- Controlled: Parameter budget range (small/medium/large); fixed train/test split seed; Adam optimizer/LR fixed

**Verification Protocol:**
1. Download ModelZooDataset; verify DWSNets/GNN-NFN checkpoint format compatibility with MNIST zoo.
2. Fix train/test split (random seed); subsample training sets {100, 250, 500, 1000, full}.
3. Train each encoder at each training size within matched parameter budget range (10 seeds for ≤250, 5 seeds for >250).
4. Compute R² on fixed held-out test set with bootstrap 95% CIs for each condition.
5. Check whether equivariant R² > Flat-MLP R² with non-overlapping CIs at ≥1 training size on both MNIST and CIFAR-10.

**Success Criteria (PoC):**
- Primary: Equivariant R² > Flat-MLP R² with non-overlapping bootstrap 95% CIs at training size ≤500 on at least one zoo
- Secondary: Efficiency ratio ≥2.0 on both MNIST and CIFAR-10 zoos (full P1 criterion)

**Failure Response:**
- IF fails: PIVOT — revisit A1 (zoo diversity) and A2 (parameter matching); check checkpoint format compatibility first

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1 (sh1_existence), Prediction P1 (primary)

---

---
**H-M1: Permutation Equivariance Implementation Verified (Structural Constraint Exists)**

**Statement:** Under controlled verification, if DWSNets and GNN-NFN encoder implementations are tested by permuting neuron orderings within layers of identical weight tensors, then their output representations will be identical regardless of permutation, because the architectures are mathematically constrained to permutation-equivariant operations.

**Rationale:** H-M1 validates the foundational step of the causal chain — the structural inductive bias actually exists in the implementation. Without confirming the constraint is realized in code (not just claimed), the mechanism attribution is invalid. This is a necessary prerequisite for H-M2 and H-M3.

**Variables:**
- Independent: Neuron permutation applied to weight tensor (permuted vs. identity)
- Dependent: Encoder output representation (should be identical; distance = 0)
- Controlled: Weight tensor values; architecture configuration; random seed

**Verification Protocol:**
1. Load pretrained DWSNets and GNN-NFN encoders.
2. Generate a sample weight tensor from ModelZooDataset MNIST zoo.
3. Apply all neuron permutations within a layer (or random subset of 100 permutations for large layers).
4. Feed original and permuted tensors through encoder; compare output representations.
5. Assert max absolute difference < 1e-5 across all tested permutations.

**Success Criteria (PoC):**
- Primary: Max absolute difference in encoder output < 1e-5 for all tested permutations on both DWSNets and GNN-NFN
- Secondary: Flat-MLP output differs from equivariant for same permutations (confirms plain encoder is NOT equivariant)

**Failure Response:**
- IF fails: EXPLORE — identify which layers violate equivariance; check implementation bug vs. deliberate approximation; may require contacting DWSNets authors

**Dependencies:** H-E1 (existence demonstrated before mechanism validation)

**Source:** Phase 2A Causal Chain Step 1; Evidence: DWSNets [Navon 2023] mathematical proof; NFN [Zhou 2023] auto-constructed equivariant layers

---

---
**H-M2: Smaller Effective Hypothesis Space Manifests as Steeper Learning Curves**

**Statement:** Under the weight-space property prediction setting, if we plot R² learning curves (R² vs. training set size) for equivariant encoders (DWSNets, GNN-NFN) and plain Flat-MLP across {100, 250, 500, 1000, full} training sizes, then equivariant learning curves will be steeper in the low-data regime (≤500 models), reaching 90% of peak R² at fewer training examples, because the structural constraint to permutation-symmetric functions reduces the effective VC dimension of the encoder.

**Rationale:** H-M2 operationalizes the theoretical claim (smaller hypothesis space) through its observable consequence (faster learning curve convergence). The efficiency ratio (plain 90%-peak size / equivariant 90%-peak size ≥ 2.0) is the primary quantitative test of the overall hypothesis.

**Variables:**
- Independent: Training Set Size (100, 250, 500, 1000, full); Encoder Architecture Type
- Dependent: R² at each training size; Efficiency Ratio (plain 90%-peak size / equivariant 90%-peak size)
- Controlled: Fixed train/test split; parameter budget range; optimizer/LR

**Verification Protocol:**
1. Use training results from H-E1 (same experimental runs, no additional experiments required).
2. Plot R² vs. training size learning curves for all 4 conditions on MNIST zoo.
3. Identify training size at which each encoder reaches 90% of its full-data R².
4. Compute efficiency ratio = plain-MLP 90%-peak size / equivariant 90%-peak size.
5. Replicate on CIFAR-10 zoo; report efficiency ratios with bootstrap 95% CIs on both.

**Success Criteria (PoC):**
- Primary: Efficiency ratio ≥ 2.0 for at least one equivariant condition on both MNIST and CIFAR-10 zoos
- Secondary: Learning curves for equivariant encoders are visually distinguishable from Flat-MLP in the 100–500 range

**Failure Response:**
- IF fails: EXPLORE — test whether A5 (fixed LR) disadvantages equivariant at small sizes; run LR sensitivity analysis; document as limitation if ratio 1.5–2.0

**Dependencies:** H-M1 (equivariance structurally verified)

**Source:** Phase 2A Causal Chain Step 3; Prediction P1 (efficiency ratio ≥ 2.0)

---

---
**H-M3: Permutation Augmentation is Intermediate — Advantage is Structural, Not Merely Distributional**

**Statement:** Under the weight-space property prediction setting, if Flat-MLP + permutation augmentation (PermAug) is trained at the same training sizes, then its R² will be strictly between Flat-MLP (no augmentation) and equivariant encoders at training sizes ≤250 models with non-overlapping bootstrap 95% CIs, because permutation augmentation makes the training data distribution approximately symmetric but does not structurally eliminate non-symmetric functions from the hypothesis space, providing partial but not full benefit.

**Rationale:** H-M3 is the key mechanistic ablation that distinguishes structural equivariance from data-level symmetry. If PermAug fully closes the gap, the structural constraint provides no additional benefit and the mechanism is attributable to symmetry in the data distribution, not the architecture. If PermAug is intermediate, the causal chain (structural constraint → smaller hypothesis space → lower sample complexity) is supported.

**Variables:**
- Independent: Augmentation type (None / PermAug / Structural Equivariance); Training Set Size (100, 250)
- Dependent: R² at ≤250 training models; ordering of PermAug relative to Flat-MLP and equivariant
- Controlled: Fixed split; parameter budget; optimizer/LR

**Verification Protocol:**
1. Use training results from H-E1 (PermAug condition already included in 4-condition design).
2. At training sizes 100 and 250, compare R²: Flat-MLP vs. Flat-MLP+PermAug vs. equivariant (DWSNets, GNN-NFN).
3. Check strict ordering: Flat-MLP R² < PermAug R² < equivariant R² with non-overlapping bootstrap 95% CIs.
4. If ordering holds on MNIST zoo, replicate check on CIFAR-10 zoo.
5. Report effect sizes: (equivariant − PermAug) and (PermAug − Flat-MLP) gaps as fractions of total gap.

**Success Criteria (PoC):**
- Primary: Strict ordering Flat-MLP < PermAug < equivariant with non-overlapping CIs at both 100 and 250 training models on at least one zoo
- Secondary: PermAug closes 50–80% of the Flat-MLP-to-equivariant gap (P2 criterion from Phase 2A)

**Failure Response:**
- IF PermAug = equivariant: Mechanism is data-distributional, not structural; document as null result on H-M3 (still publishable per Prof. Rex); revise mechanism claim
- IF PermAug = Flat-MLP: Augmentation provides no benefit; interesting negative result; document violation of A3

**Dependencies:** H-M2 (learning curve analysis complete, efficiency ratio computed)

**Source:** Phase 2A Causal Chain Step 2; Prediction P2 (PermAug intermediate)

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
| H-E1 | MUST_WORK | Equivariant R² > Flat-MLP R² with non-overlapping CIs at ≤500 training models | STOP — reassess entire hypothesis; check checkpoint compatibility |
| H-M1 | MUST_WORK | DWSNets/GNN-NFN output identical across neuron permutations (max diff < 1e-5) | EXPLORE implementation bug; contact authors; may block H-M2/H-M3 |
| H-M2 | SHOULD_WORK | Efficiency ratio ≥ 2.0 on both MNIST and CIFAR-10 | Document limitation; mechanism partially supported if ratio 1.5–2.0 |
| H-M3 | SHOULD_WORK | Strict ordering Flat-MLP < PermAug < equivariant at ≤250 models | Revise mechanism attribution; null result is publishable |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Low Zoo Diversity (from A1)**

**Source Assumption:** A1 — ModelZooDataset provides sufficient model diversity.

**Description:** If zoo models are too similar (all trained to convergence with minimal HP variation), both equivariant and plain encoders trivially reach high R² with very few training models, making the efficiency comparison degenerate.

**Affected Hypotheses:** H-E1, H-M2

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Before running encoders, compute diversity metrics on zoo checkpoints (pairwise R² of model properties; variance in test accuracy across zoo). If test-accuracy variance < 5%, flag as low-diversity.
2. **Detection:** If Flat-MLP reaches R²>0.85 at 100 training models, zoo may be too easy — check diversity metrics.
3. **Response:** PIVOT — compute model-diversity-stratified subsets; or use generalization gap prediction (harder DV); or extend to CIFAR-10 zoo (typically more diverse). SCOPE — report results conditional on diversity check. ABORT — if both zoos show degenerate efficiency curves, report as negative finding.

**Early Warning Indicators:**
- Flat-MLP R² > 0.85 at 100 training models
- All 4 conditions have overlapping CIs at all training sizes

---

**Risk R2: Parameter Matching Confound (from A2)**

**Source Assumption:** A2 — Parameter-count range matching provides fair comparison.

**Description:** DWSNets may be architecturally deeper or use different nonlinearities that provide accuracy benefits independent of equivariance, making attribution to equivariance incorrect.

**Affected Hypotheses:** H-E1, H-M2, H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** For each parameter range, verify that equivariant and plain encoders have comparable layer depth and nonlinearities; document in experiment log.
2. **Detection:** If equivariant advantage persists even in full-data regime (violating P3 expressivity equivalence prediction), likely capacity confound.
3. **Response:** EXPLORE — run ablation with deeper Flat-MLP at same parameter count; if advantage disappears, attribution to equivariance confirmed. PIVOT — report results with architecture matching caveat.

**Early Warning Indicators:**
- Equivariant R² > Flat-MLP R² by >0.05 at full training size (violates P3)
- Equivariant advantage grows with training size (opposite of expected pattern)

---

**Risk R3: Augmentation Fully Replicates Equivariance (from A3)**

**Source Assumption:** A3 — Permutation augmentation is valid approximation, not full replication.

**Description:** If Flat-MLP + PermAug achieves R² matching equivariant at ≤250 training models, the structural constraint provides no benefit beyond data symmetry — H-M3 fails and mechanism attribution must be revised.

**Affected Hypotheses:** H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Use sufficient permutation count in PermAug (augment each batch with 10 random permutations) to maximize augmentation effectiveness — if this still fails to close gap, structural advantage is clear.
2. **Detection:** Monitor R² ordering at 100-model training size; if PermAug ≈ equivariant at 100 models, H-M3 is at risk.
3. **Response:** PIVOT — revise mechanism claim to "data symmetry sufficient, structural constraint not required"; still novel finding. SCOPE — report as P2 falsification; null result is still publishable.

**Early Warning Indicators:**
- PermAug R² overlaps equivariant R² CIs at 100 training models
- PermAug efficiency ratio ≥ 1.8 (close to equivariant's predicted ≥2.0)

---

**Risk R4: Architecture-Specific Finding (from A4)**

**Source Assumption:** A4 — MNIST and CIFAR-10 zoo tasks are representative.

**Description:** If efficiency gap exists for MNIST zoo (small MLPs) but not CIFAR-10 zoo (larger CNNs), the finding is architecture-size-specific and may not generalize.

**Affected Hypotheses:** H-E1, H-M2

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Run MNIST and CIFAR-10 zoos in parallel from the start; do not pre-declare success before CIFAR-10 replication.
2. **Detection:** CIFAR-10 efficiency ratio < 1.5 while MNIST ratio ≥ 2.0.
3. **Response:** SCOPE — report as "advantage holds for MLP weight spaces (MNIST) but diminishes for CNN weight spaces (CIFAR-10)"; characterize the boundary condition. PIVOT — investigate whether GNN-NFN (more general architecture) maintains advantage on CIFAR-10 while DWSNets does not.

**Early Warning Indicators:**
- GNN-NFN/DWSNets advantage differs substantially between MNIST and CIFAR-10 zoos
- CIFAR-10 R² curves show overlap between equivariant and plain at all training sizes

---

**Risk R5: Optimizer Fairness (from A5)**

**Source Assumption:** A5 — Fixed LR (tuned on full data) is fair across training sizes.

**Description:** LR tuned on full training data may be suboptimal at small sizes (100–250 models), disproportionately affecting plain MLP which might benefit more from smaller LR at small sizes — making the comparison unfair.

**Affected Hypotheses:** H-E1, H-M2 (all hypotheses that rely on efficiency ratio)

**Severity:** Low

**Mitigation Strategy:**
1. **Prevention:** Run LR sensitivity analysis at 100-model training size for both Flat-MLP and equivariant (grid: 1e-3, 5e-4, 1e-4); if optimal LR differs by >1 order of magnitude, report sensitivity.
2. **Detection:** Monitor training loss curves; if Flat-MLP shows slow convergence at small sizes, optimizer may be suboptimal.
3. **Response:** EXPLORE — run with per-size LR tuning for Flat-MLP only; if R² improves substantially, recompute efficiency ratio with fair LR; report both results.

**Early Warning Indicators:**
- Flat-MLP training loss at 100 models does not converge in standard epoch budget
- Large variance in Flat-MLP R² across seeds at small training sizes (high LR sensitivity)

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Low Zoo Diversity | A1 | H-E1, H-M2 | High |
| R2: Parameter Matching Confound | A2 | H-E1, H-M2, H-M3 | Medium |
| R3: Augmentation Fully Replicates Equivariance | A3 | H-M3 | Medium |
| R4: Architecture-Specific Finding | A4 | H-E1, H-M2 | Medium |
| R5: Optimizer Fairness | A5 | H-E1, H-M2 | Low |

**Critical Risks: 0 | High Risks: 1 | Medium Risks: 3 | Low Risks: 1**

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root / Foundation]
    H-E1: Sample Efficiency Advantage Exists on Shared Splits
    (EXISTENCE — no dependencies — MUST_WORK gate)
         │
         ▼ [Gate 1: MUST_WORK — if FAIL → STOP]
[Level 1 - Core Mechanism Step 1]
    H-M1: Permutation Equivariance Implementation Verified
    (MECHANISM — depends on H-E1 — MUST_WORK gate)
         │
         ▼ [Gate 2: MUST_WORK — if FAIL → EXPLORE]
[Level 2 - Core Mechanism Step 2]
    H-M2: Steeper Learning Curves (Efficiency Ratio ≥2.0)
    (MECHANISM — depends on H-M1 — SHOULD_WORK gate)
         │
         ▼
[Level 3 - Core Mechanism Step 3]
    H-M3: PermAug is Intermediate (Structural vs Distributional)
    (MECHANISM — depends on H-M2 — SHOULD_WORK gate)
         │
         ▼
[COMPLETE — proceed to Phase 2C → 3 → 4 per hypothesis]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4 | No parallelization (all sequential)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2    │ W3-4    │ W5      │ W6      │ W7
───────────────────┼─────────┼─────────┼─────────┼─────────┼──────
PHASE 1: Foundation
  H-E1            │ ████████│         │         │         │
  [Gate 1] ◆      │         │ ◆       │         │         │
───────────────────┼─────────┼─────────┼─────────┼─────────┼──────
PHASE 2: Mechanisms
  H-M1            │         │ ████████│         │         │
  H-M2            │         │         │ ████    │         │
  H-M3            │         │         │         │ ████    │
  [Gate 2] ◆      │         │         │ ◆       │         │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
Note: H-M2 and H-M3 reuse H-E1 experimental data (no new runs needed)
      H-M1 requires short verification run (~1 day)
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 5 weeks
  Formula: 2 (H-E1 foundation) + 3 (H-M1-3 mechanisms)

Slack Available: 0 weeks (all sequential)

Note: H-M2 and H-M3 are analysis steps reusing H-E1 training
      data — their calendar duration is reduced (~1 week each
      for analysis, not new training runs). The primary compute
      cost is H-E1 (~15-20 GPU hours per Prof. Pax estimate).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0

Verification Phases: 2
1. Foundation (H-E1): ~15-20 GPU hours
2. Mechanisms (H-M1-3): ~1 day H-M1 verification + reuse H-E1 data

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain
Compute Estimate: ~20 GPU hours total (per Phase 2A dialogue consensus)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1:** Execute H-E1 (Foundation) — Week 1-2: full 4-condition training experiment across {100, 250, 500, 1000, full} training sizes on MNIST and CIFAR-10.
**Step 2:** Evaluate Gate 1 → If H-E1 MUST_WORK passes, proceed. If FAIL, STOP and reassess.
**Step 3:** Execute H-M1 (Mechanism Step 1) — Week 3: programmatic permutation invariance verification on DWSNets/GNN-NFN.
**Step 4:** Evaluate Gate 2 → If H-M1 MUST_WORK passes, proceed. If FAIL, EXPLORE (may block H-M2/H-M3).
**Step 5:** Execute H-M2 (Mechanism Step 2) — Week 4-5: compute efficiency ratios from H-E1 training data; no new experiments.
**Step 6:** Execute H-M3 (Mechanism Step 3) — Week 6-7: analyze PermAug ordering from H-E1 training data; no new experiments.
**Final:** Verification complete → Phase 2C experiment design per hypothesis.

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Permutation equivariance provides measurable sample
efficiency advantage for weight-space property prediction in the
low-data regime (<500 models), because structural constraints
reduce effective hypothesis space and thus sample complexity.

Supporting Evidence:
1. DWSNets [Navon 2023] and NFN [Zhou 2023] prove mathematical
   equivariance; Dayan 2026 proves expressivity equivalence ceiling
   — making efficiency the open differentiator
2. Analogous sample efficiency gains well-documented in image (CNNs
   vs MLPs) and graph (GNNs vs MLPs) domains
3. Phase 2A: 6/6 convergence criteria met; 3 testable quantitative
   predictions defined; major objections addressed

Strengths:
- Clear falsifiable criterion (efficiency ratio ≥ 2.0)
- Multiple replication conditions (MNIST + CIFAR-10 zoos)
- Mechanistic ablation built in (PermAug condition)
- Null result (augmentation closes gap) is still publishable

Expected Outcomes:
- P1: Efficiency ratio ≥ 2.0 on both MNIST and CIFAR-10
- P2: PermAug strictly intermediate at ≤250 training models
- P3: Full-data convergence within 5% R² (expressivity parity)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): There is no significant difference in sample
efficiency between equivariant and plain encoders; the 90%/50%
threshold is not met, or the gap is within bootstrap CI overlap.

Counter-Arguments:
1. Gradient descent on flat-MLPs with large datasets implicitly
   discovers permutation-symmetric solutions (implicit bias) —
   Dayan 2026 expressivity equivalence may translate to practical
   efficiency parity even at low data
2. ModelZooDataset MNIST zoo (~4860 models) may have too-low
   diversity (all trained to convergence on MNIST with narrow HP
   range) — both encoders trivially fit with few training samples
3. Parameter range matching may not fully control for architectural
   differences; DWSNets depth/connectivity may confound the result

Potential Failure Points:
- R1 (High): Zoo too easy → degenerate efficiency curves
- R2 (Medium): Architecture confound → attribution to equivariance fails
- R3 (Medium): PermAug closes gap → mechanism is distributional, not structural

Conditions Under Which H0 Would Be Supported:
- If efficiency ratio < 1.5 on both MNIST and CIFAR-10 zoos
- If Flat-MLP R² converges to equivariant R² at ≤500 training models
- If Flat-MLP + PermAug matches equivariant at ≤250 training models
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

H-EquivSampleEfficiency-v1 presents a testable claim grounded in
learning theory and supported by analogous inductive bias effects
in CNNs and GNNs. However, the null hypothesis raises valid concerns:
(1) implicit gradient-descent symmetry discovery, (2) ModelZooDataset
diversity sufficiency, and (3) parameter matching validity.

Resolution Path:

The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Establishes existence with
   quantitative criterion (non-overlapping bootstrap CIs) before
   mechanism attribution
2. Sequential mechanism testing (H-M1→H-M2→H-M3): Tests the causal
   chain step-by-step, isolating structural (H-M1) from learning-
   dynamics (H-M2) from distributional (H-M3) contributions
3. Gate conditions: H-E1 MUST_WORK gate allows early detection of
   H0 support without wasting compute on mechanism analysis
4. Built-in risk mitigation: A1 (diversity check), A2 (LR
   sensitivity), ablation design (PermAug condition)

Conditions for Thesis Support:
- H-E1 MUST_WORK gate passes (non-overlapping CIs at ≤500 models)
- Efficiency ratio ≥ 2.0 on at least one zoo (H-M2)
- PermAug intermediate (H-M3, even if SHOULD_WORK only)

Conditions for Antithesis Support:
- H-E1 fails: equivariant R² ≤ Flat-MLP R² at all training sizes ≤500
- Efficiency ratio < 1.5 on both zoos (within noise)
- PermAug matches equivariant at ≤250 models (distributional suffices)

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1 + H-M2 + H-M3 all pass → Thesis validated
2. Partial Support: H-E1 + H-M1 + H-M2 pass, H-M3 fails → Advantage
   exists but mechanism is distributional; still novel finding
3. Weak Support: H-E1 passes, H-M2 ratio 1.5–2.0 → Advantage exists
   but smaller than predicted; report with scope caveat
4. No Support: H-E1 fails → H0 supported; explore zoo diversity issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Equivariant advantage empirically measurable at ≤500 models | Gradient descent discovers symmetry implicitly; zoo too easy | H-E1 test with zoo diversity pre-check |
| Mechanism (structural) | Mathematical equivariance is implemented correctly | Implementation may approximate equivariance, not enforce it | H-M1 programmatic verification |
| Mechanism (learning) | Structural constraint → steeper learning curves | Expressivity equivalence may translate to sample efficiency parity | H-M2 efficiency ratio test |
| Mechanism (distributional) | Structural advantage beyond data symmetry | Augmentation fully replicates structural benefit | H-M3 PermAug ablation |
| Generalizability | MNIST + CIFAR-10 zoos provide dual-scale replication | Finding may be MLP-specific (MNIST) not CNN-general | Mandatory CIFAR-10 replication in H-E1/H-M2 |

**Overall Robustness Score:** Medium-High (well-designed falsification criteria; multiple ablations; zoo diversity is the primary uncontrolled risk)

**Confidence in Verification Plan:** 0.78

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-EquivSampleEfficiency-v1 — Equivariant encoders achieve ≥90% peak R² at ≤50% of plain encoder training data (efficiency ratio ≥2.0) on shared ModelZooDataset splits.
- ID: H-EquivSampleEfficiency-v1 | Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (Phase 2A data loaded; 83% scope reduction)
- Sub-Hypotheses: 4 total (H-E1: 1, H-M1-3: 3, H-C: 0)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1 at H-E1, Gate 2 at H-M1)

**Risk Assessment:** Medium
- Primary concerns: R1 (zoo diversity may be too low), R2 (parameter matching confound)

**Immediate Action:** Begin Phase 2C for H-E1; run zoo diversity pre-check before main experiment.

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases (Foundation + Mechanisms)
- H0 addressed: no significant efficiency difference, ratio < 1.5
- H-M2/H-M3 reuse H-E1 experimental data — compute overhead minimal after Phase 4 H-E1

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Equivariant R² > Flat-MLP R² at ≤500 training models on shared splits
- Gate 1: MUST PASS → if FAIL, STOP

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Programmatic equivariance verification (Step 1 — ~1 day)
- H-M2: Efficiency ratio computation from H-E1 data (Step 2)
- H-M3: PermAug ordering analysis from H-E1 data (Step 3)
- Gate 2: H-M1 must pass → if FAIL, EXPLORE (blocks H-M2/H-M3)

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 MUST_WORK
   - FAIL → STOP: Check checkpoint compatibility first, then zoo diversity, then reassess hypothesis

2. **Gate 2 (Mechanisms):** H-M1 MUST_WORK
   - FAIL → EXPLORE: Contact DWSNets authors; may need custom implementation fix
   - H-M2/H-M3 SHOULD_WORK failures → Document as limitations, narrow scope claim

**Open Questions (from Phase 2A):**
- Are DWSNets checkpoints compatible with ModelZooDataset MNIST zoo format without preprocessing?
- What is the appropriate parameter count range for each architecture class to ensure fair matching?
- Should the experiment also include NFN (not just DWSNets and GNN-NFN) as a third equivariant condition?

**Recommendations:**

1. **Immediate Actions:**
   - Run zoo diversity pre-check (pairwise property variance) before committing to full H-E1 experiment
   - Verify DWSNets/GNN-NFN checkpoint compatibility with ModelZooDataset format
   - Begin Phase 2C experiment design for H-E1 first

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path
   - Reserve 1-week buffer for checkpoint compatibility issues (identified in Phase 2A open questions)

3. **Failure Management:**
   - Document all gate failures with quantitative results
   - Execute PIVOT strategies per risk mitigation plan above
   - Null result (H-E1 fails) → zoo diversity analysis provides publishable negative finding

### 7.3 Appendices

**A. Phase 2A Reference:**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-EquivSampleEfficiency-v1)
- Hypothesis validated after 6 exchanges; 6/6 convergence criteria met

**B. MCP Tool Usage Summary:**
- Total MCP calls: 2 (incremental mode)
- Tools: `mcp__clearThought__scientificmethod` (Call 1: H-E1 existence; Call 2: H-M integrated mechanism)
- Scope reduction: 83% (5 of 6 claims BUILD_ON)
