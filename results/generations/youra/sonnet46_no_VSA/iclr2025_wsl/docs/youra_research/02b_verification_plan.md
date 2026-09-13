# Verification Plan: Architectural Permutation-Invariance Improves ModelZoo Prediction by Eliminating Encoder Symmetry Noise

**Date:** 2026-08-03
**Hypothesis ID:** H-InvEnc-v1
**Confidence:** 0.78
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under S_16³ functional permutations (coupled row-column actions across adjacent layers
as formalized in DWSNet [Navon et al., 2023]), if a weight encoder implements architectural
permutation-invariance (DeepSets sum pooling or NFN structured equivariance) rather than
non-invariant channel-position-aware encoding (CISE sinusoidal PE), then:
(1) OrbitVar will be < 1e-6 for invariant encoders vs 0.010333 for CISE,
(2) LightGBM R² for invariant encoders will be ≥ simple per-layer statistics baseline (R²≈0.984),
(3) CISE will achieve R² < Ŵ_L baseline because permutation-induced prediction variance
    MSE_perm is non-negligible (≥ 10% of total MSE),
because CISE's sinusoidal PE introduces within-orbit representational noise that contributes
to prediction error, while architectural invariance eliminates this noise source entirely.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in LightGBM R² between architecturally invariant encoders
(DeepSets, NFN) and the simple per-layer statistics baseline (Ŵ_L), and CISE achieves
similar R² to Ŵ_L, indicating that LightGBM implicitly learns approximate permutation
invariance regardless of encoder architecture.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ModelZooDataset CIFAR10-GS (standard) | Contains 100+ CNNs (3 conv + 1 dense) trained on CIFAR-10 with test accuracy labels. Used in sh1/sh2 to establish CISE baseline. S_16³ symmetry group applies to 16-channel conv layers. |
| **Model** | Small CNN (3 conv layers, C=16 channels) | Channel permutation group S_16³ defined by 16-channel convolutional layers. Functional permutations preserve network output (coupled row-column action). |

**Dataset Details:**
- Source: Zenodo record 6620869
- Path: dataset_cifar_small_hyp_rand.pt

**Model Details:**
- Type: CNN
- Source: ModelZooDataset CIFAR10-GS

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Ŵ_L per-layer statistics (GBM) | R² = 0.984, Kendall's τ = 0.915 | ModelZooDataset CIFAR10-GS |
| NFN (Neural Functional Networks) | Kendall's τ = 0.934 | ModelZooDataset (related split) |
| DWSNet | 85.7% vs 58.9% on MNIST INR | INR datasets (different) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | sh1's apply_channel_permutation() implements functional (coupled row-column) permutations per DWSNet Eq. 5 | sh1 PASS established CISE OrbitVar=0.010333; if non-functional, baseline is invalid | OrbitVar=0.010333 invalid; all comparisons to sh1 baseline invalid — re-run with corrected permutations |
| A2 | LightGBM does not implicitly learn perfect permutation invariance from CISE embeddings | Unterthiner [2020] shows MAD~0.05 in predictions under permutations — partial robustness only | MSE_perm^C1 ≈ 0; gap between C1 and C2 collapses; hypothesis cannot be tested — use linear head ablation |
| A3 | ModelZooDataset CIFAR10-GS has enough prediction headroom above CISE baseline R² for measurable improvement | Unterthiner's simple statistics achieve R²=0.984, leaving 1.6% headroom | R² ceiling effect prevents measurement; redirect to Kendall's τ as primary metric |
| A4 | DeepSets (C2) and NFN (C3) can be implemented with matched embedding capacity to C0/C1 | NFN pip-installable (AllanYangZhou/nfn, 93★); DeepSets pattern verified in Phase 1 | Capacity mismatch confounds R² comparison; use matched linear head as isolation test |
| A5 | CIFAR-10-C distribution shift provides a meaningfully different test distribution | CIFAR-10-C is a standard benchmark; models trained on CIFAR-10 generalize differently under corruptions | Distribution-shift test has no power; restrict claims to in-distribution R² comparison only |

### 1.6 Research Gap & Novelty

**Scope Reduction:** 45% of claims are BUILD_ON (established); only 3 PROVE_NEW claims targeted.

**PROVE_NEW targets:**
1. The true functional symmetry group for CNNs requires coupled row-column permutations (not independent per-layer)
2. Architecturally invariant encoders (DeepSets, NFN) achieve OrbitVar < 0.001 on ModelZooDataset CIFAR10-GS
3. OrbitVar reduction causally mediates R² improvement via MSE_perm reduction

**Key Innovation:** First paper to jointly measure OrbitVar, MSE_perm, and R² across the full invariance spectrum (approximately invariant → non-invariant → architecturally invariant → structured equivariant) in a closed causal loop on ModelZooDataset CIFAR10-GS. MSE bias-variance decomposition over permutation orbits: E[(y-ŷ)²] = MSE_res + MSE_perm enables direct causal measurement.

**BUILD_ON (established, not re-verified):**
- Per-layer quantile encoders are provably permutation-invariant (h-m1 FAIL: OrbitVar(C1)=1.24e-33)
- CISE encoder achieves mean OrbitVar=0.010333 under S_16³ (sh1 PASS)
- Post-hoc cross-model alignment does not reduce OrbitVar (sh2 FAIL)
- Deep Sets Theorem 2: sum/mean pooling guarantees OrbitVar=0 (Zaheer et al. 2017)
- Simple Ŵ_L statistics achieve R²=0.984 (Unterthiner et al. 2020)
- NFN achieves Kendall's τ=0.934 > STATNN τ=0.915 (Zhou et al. 2023)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None (permutation audit is prerequisite action) | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Architecturally Invariant Encoders Achieve Near-Zero OrbitVar

**Type:** EXISTENCE
**Statement:** Under S_16³ functional permutations (coupled row-column across adjacent CNN layers), if a weight encoder implements architectural permutation-invariance (DeepSets sum pooling or NFN structured equivariance), then OrbitVar < 1e-6, because Deep Sets Theorem 2 guarantees OrbitVar=0 for sum pooling by construction, and NFN parameter sharing enforces equivariance.

**Rationale:** Prior work (sh1) established CISE OrbitVar=0.010333 as the non-invariant baseline. Invariant encoders are theoretically guaranteed to achieve OrbitVar≈0; this hypothesis verifies that guarantee holds empirically under functionally correct S_16³ permutations on ModelZooDataset CIFAR10-GS.

**Variables:**
- IV: Weight Encoder Architecture (C2=DeepSets sum-pooling, C3=NFN NF-Layers)
- DV: OrbitVar = E_v[Var_π(encoder(π·W))]
- CV: 100 models from ModelZooDataset CIFAR10-GS; 50 functional permutations per model; identical permutation code (post-audit)

**Verification Protocol:**
1. Audit sh1's apply_channel_permutation() — verify functional permutations via ||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6.
2. Implement C2 (DeepSets: φ(w_c) per channel, sum-pool over C=16 channels).
3. Implement C3 (pip install nfn; NF-Layers with CNN spatial folding for 3-conv architecture).
4. Compute OrbitVar for 100 models × 50 permutations for both C2 and C3.
5. Compare results against thresholds: mean < 1e-6, max < 1e-4.

**Success Criteria (PoC: Direction-based):**
- Primary: mean OrbitVar(C2) < 1e-6 AND mean OrbitVar(C3) < 1e-6
- Secondary: max OrbitVar < 1e-4 for both encoders

**Gate:**
- Type: MUST_WORK
- If Fail: PIVOT — debug φ(w_c) for channel-position indexing; verify NFN spatial folding; confirm permutation audit passed; do NOT proceed to H-M1 if H-E1 fails

**Dependencies:** None (foundation)

**Source:** Phase 2A SH1, Section 1.6 P1, Deep Sets Theorem 2 [Zaheer et al. 2017]

---

#### H-M1: Encoder Architecture Determines OrbitVar (Causal Step 1)

**Type:** MECHANISM
**Statement:** Under matched experimental conditions on ModelZooDataset CIFAR10-GS, if encoder architectural design differs (non-invariant CISE vs architecturally invariant C2/C3), then OrbitVar measurably differs by ≥ 4 orders of magnitude (CISE=0.010333 vs C2/C3<1e-6), because Deep Sets Theorem 2 and NFN equivariance construction eliminate within-orbit variance by design while CISE sinusoidal PE introduces channel-position sensitivity.

**Rationale:** Establishes the first causal link — architecture directly determines OrbitVar, not confounders like model capacity or training distribution. H-E1 provides the C2/C3 OrbitVar measurements; H-M1 frames this as a causal contrast against the CISE baseline.

**Variables:**
- IV: Encoder architecture type (invariant C2/C3 vs non-invariant C1=CISE)
- DV: OrbitVar ratio (C1 vs C2, C1 vs C3)
- CV: Same 100 models, same permutation implementation, matched embedding capacity where possible

**Verification Protocol:**
1. Use OrbitVar results from H-E1 for C2 and C3.
2. Measure C1 (CISE) OrbitVar on same 100 models × 50 permutations (use sh1 result 0.010333 or re-measure).
3. Compute ratio: OrbitVar(C1) / OrbitVar(C2) and OrbitVar(C1) / OrbitVar(C3).
4. Confirm difference is ≥ 4 orders of magnitude.
5. Run anti-h-m1 gate: confirm DeepSets φ uses no order statistics over channel dimension.

**Success Criteria:**
- Primary: OrbitVar(C1) / OrbitVar(C2) > 1e4 AND OrbitVar(C1) / OrbitVar(C3) > 1e4
- Secondary: Anti-h-m1 gate passes (no order statistics in φ)

**Gate:**
- Type: MUST_WORK
- If Fail: EXPLORE — check if permutation audit revealed non-functional permutations; if so, re-run sh1 CISE baseline with corrected implementation

**Dependencies:** H-E1 (OrbitVar results for C2/C3 required)

**Source:** Phase 2A Section 1.3 Step 1, causal_mechanism

---

#### H-M2: OrbitVar Propagates to Prediction-Level MSE_perm (Causal Step 2)

**Type:** MECHANISM
**Statement:** Under 5-fold CV LightGBM on CISE (C1) embeddings from ModelZooDataset CIFAR10-GS, if CISE OrbitVar=0.010333 persists to prediction space, then MSE_perm^C1 ≥ 10% of MSE_total^C1, because permutation-sensitive encoder representations create within-orbit prediction variance that LightGBM cannot fully cancel.

**Rationale:** The key novel measurement — quantifying whether encoder-level symmetry violation propagates to predictor-level noise. Prior work (sh2) showed cross-model alignment doesn't reduce OrbitVar; this directly tests whether remaining OrbitVar translates to measurable MSE_perm at the prediction level.

**Variables:**
- IV: CISE encoder (C1) with established OrbitVar=0.010333
- DV: MSE_perm = E_v[Var_g(ŷ(g·v))], K=50 orbit samples per model; also R²(C1) vs R²(C0)
- CV: Same LightGBM HP search space and seeds, same 80/10/10 split, ≥5 random seeds

**Verification Protocol:**
1. Train LightGBM on C1 (CISE) embeddings with 5-fold CV, identical HP search.
2. For each model v, compute K=50 orbit predictions {ŷ(π_k·W)}: MSE_perm = E_v[Var_k(ŷ(π_k·v))].
3. Compute MSE_total(C1) = average 5-fold CV MSE; MSE_res = MSE_total - MSE_perm.
4. Compute ratio MSE_perm^C1 / MSE_total^C1.
5. Compute orbit-averaged C1 baseline ŷ_avg(W) = (1/K)Σŷ(π_k·W) as implicit-invariance control.

**Success Criteria:**
- Primary: MSE_perm^C1 / MSE_total^C1 ≥ 0.10 (≥10% of total error from permutation variance)
- Secondary: R²(C1) < R²(C0)=0.984 (CISE underperforms simple statistics baseline)

**Gate:**
- Type: MUST_WORK
- If Fail: EXPLORE — if MSE_perm < 1% of MSE_total, LightGBM cancels permutation variance; H0 holds; redirect to Kendall's τ as primary metric; still report MSE decomposition

**Dependencies:** H-M1 (causal chain Step 1 must hold)

**Source:** Phase 2A Section 1.3 Step 2, Section 1.6 P2

---

#### H-M3: Reduced MSE_perm Causes Higher R² via Mechanism Closure (Causal Step 3)

**Type:** MECHANISM
**Statement:** Under matched LightGBM training on ModelZooDataset CIFAR10-GS, if DeepSets (C2) eliminates MSE_perm relative to CISE (C1), then R²(C2) ≥ R²(C0)=0.984 and the mechanism closure criterion holds: ΔMSE(C1→C2) = MSE_perm^C1 ± 10%, because bias-variance decomposition E[(y-ŷ)²] = MSE_res + MSE_perm predicts that eliminating MSE_perm closes the performance gap by exactly MSE_perm^C1.

**Rationale:** The mechanism closure test is the methodological core. If ΔMSE matches MSE_perm^C1 within 10%, the causal chain is closed — architectural invariance works through MSE_perm elimination. If ΔMSE ≫ MSE_perm^C1, representation geometry (not noise elimination) is the true driver and a separate hypothesis is needed.

**Variables:**
- IV: Encoder shift from C1 (CISE, OrbitVar=0.010333) to C2 (DeepSets, OrbitVar<1e-6)
- DV: ΔMSE(C1→C2), MSE_perm^C1, R²(C2) vs R²(C0), R²(C3 linear) vs R²(C2 linear)
- CV: Identical LightGBM HP, same data split, same orbit sample K=50, matched linear head

**Verification Protocol:**
1. Train LightGBM on C0, C2, C3, C4 embeddings with 5-fold CV (reuse C1 results from H-M2).
2. Compute ΔMSE = MSE_total(C1) - MSE_total(C2).
3. Verify mechanism closure: |ΔMSE - MSE_perm^C1| / MSE_perm^C1 ≤ 0.10.
4. Run matched linear head ablation: Ridge regression on frozen C2, C3; compute R²(C3 linear) - R²(C2 linear).
5. Report Kendall's τ as backup significance metric if R² ceiling effect detected; evaluate distribution-shift ΔR²_shift if CIFAR-10-C zoo available.

**Success Criteria:**
- Primary: R²(C2) ≥ R²(C0)=0.984 AND |ΔMSE - MSE_perm^C1| / MSE_perm^C1 ≤ 0.10
- Secondary: R²(C3 linear) - R²(C2 linear) ≥ 0.01 (95% CI excludes 0, ≥5 seeds)

**Gate:**
- Type: SHOULD_WORK
- If R²(C2) < R²(C0): EXPLORE — expressivity collapse; use HIE (C4 = Ŵ_L + DeepSets) as fallback; report Kendall's τ
- If ΔMSE ≫ MSE_perm^C1: PIVOT — mechanism is representation geometry, not noise; refine hypothesis

**Dependencies:** H-M2 (MSE_perm^C1 value required for closure test)

**Source:** Phase 2A Section 1.3 Step 3, Section 1.6 P3 and P4

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | OrbitVar(C2) < 1e-6 AND OrbitVar(C3) < 1e-6 | STOP — debug implementation before proceeding |
| H-M1 | MUST_WORK | OrbitVar(C1)/OrbitVar(C2) > 1e4 | EXPLORE — check permutation audit result |
| H-M2 | MUST_WORK | MSE_perm^C1 / MSE_total^C1 ≥ 0.10 | EXPLORE — H0 supported; use τ as primary metric |
| H-M3 | SHOULD_WORK | R²(C2) ≥ 0.984 AND closure ±10% | EXPLORE or PIVOT based on failure type |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 (incl. permutation audit) | 2 weeks |
| Gate 1 | H-E1 decision point | Week 2 |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 (sequential) | 3 weeks |
| Gate 2 | H-M1 decision point | Week 4 |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

| Risk | Source | Description | Severity | Affected Hypotheses |
|------|--------|-------------|----------|---------------------|
| R1 | A1 | sh1 permutation.py implements independent (not coupled row-column) permutations | Critical | H-E1, H-M1, H-M2, H-M3 (all) |
| R2 | A2 | LightGBM implicitly cancels CISE permutation variance → MSE_perm negligible | High | H-M2, H-M3 |
| R3 | A3 | R² ceiling effect (1.6% headroom) makes gains undetectable | Medium | H-M3 |
| R4 | A4 | DeepSets/NFN capacity mismatch confounds R² comparison | Medium | H-M3 |
| R5 | A5 | CIFAR-10-C zoo unavailable or not meaningfully different | Low | H-M3 (secondary) |

### 4.2 Risk Details & Mitigation

**Risk R1: Non-functional permutation implementation (CRITICAL)**
- Source: A1 — sh1's apply_channel_permutation() may use independent per-layer permutations, not DWSNet coupled row-column
- Affected: ALL hypotheses (invalidates CISE OrbitVar=0.010333 baseline)
- Severity: Critical
- Mitigation:
  1. Prevention: Mandatory functional validator before ANY experiment — ||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6
  2. Detection: If validator fails, permutations are non-functional
  3. Response: Fix permutation implementation; re-run sh1 CISE baseline; update OrbitVar=0.010333 if needed
- Early Warning: Functional validator ||f_v(x) - f_{g·v}(x)||_∞ > 1e-3

**Risk R2: LightGBM implicit invariance (HIGH)**
- Source: A2 — LightGBM may learn approximate invariance from CISE embeddings, suppressing MSE_perm
- Affected: H-M2, H-M3
- Severity: High
- Mitigation:
  1. Prevention: Compute orbit-averaged C1 baseline ŷ_avg as implicit-invariance control
  2. Detection: MSE_perm^C1 / MSE_total^C1 < 0.01
  3. Response: EXPLORE — switch primary metric to Kendall's τ; report negative finding; still publishable
- Early Warning: MSE_perm^C1 / MSE_total^C1 < 0.05

**Risk R3: R² ceiling effect (MEDIUM)**
- Source: A3 — only 1.6% headroom above R²=0.984
- Affected: H-M3
- Severity: Medium
- Mitigation:
  1. Prevention: Pre-register Kendall's τ as backup metric; plan CIFAR-10-C evaluation
  2. Detection: R²(C2) - R²(C0) < 0.005 even if direction is correct
  3. Response: Shift primary claim to Kendall's τ ordering and/or distribution-shift robustness
- Early Warning: R²(C0) already at 0.990+ on new run

**Risk R4: Capacity mismatch (MEDIUM)**
- Source: A4 — DeepSets/NFN embedding dimensions may differ from Ŵ_L/CISE
- Affected: H-M3
- Severity: Medium
- Mitigation:
  1. Prevention: Match embedding capacity; document all dimensions
  2. Detection: Capacity discrepancy > 50% between encoders
  3. Response: Use matched linear head (Ridge regression) as capacity-controlled comparison
- Early Warning: DeepSets embedding dim significantly larger than C0 before any tuning

**Risk R5: CIFAR-10-C unavailability (LOW)**
- Source: A5 — CIFAR-10-C zoo may not exist or be easily constructed
- Affected: H-M3 secondary metric only
- Severity: Low
- Mitigation:
  1. Prevention: Check for CIFAR-10-C zoo before starting Phase 3
  2. Response: SCOPE — restrict distribution-shift claim; use in-distribution metrics only
- Early Warning: No CIFAR-10-C compatible models found in ModelZooDataset

### 4.3 Baseline Failure Patterns → Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| Ŵ_L: no OrbitVar analysis | Cannot compare mechanism — only outcome | MSE decomposition provides mechanism signal independent of R² |
| NFN: no MSE_perm reported | Cannot validate causal chain from prior work | Measure MSE_perm directly in this experiment |
| DWSNet: different dataset | Cannot use DWSNet R² as benchmark | Use Ŵ_L (R²=0.984) as primary comparison baseline |

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1 (Existence — no dependencies)
    ┌─────────────────────────────────────┐
    │ OrbitVar < 1e-6 for C2, C3         │
    │ Gate 1: MUST_WORK                   │
    └─────────────────┬───────────────────┘
                      │
                      ▼
[Level 1 - Mechanism Step 1]
    H-M1 ← H-E1
    ┌─────────────────────────────────────┐
    │ OrbitVar(C1)/OrbitVar(C2) > 1e4    │
    │ Gate: MUST_WORK                     │
    └─────────────────┬───────────────────┘
                      │
                      ▼
[Level 2 - Mechanism Step 2]
    H-M2 ← H-M1
    ┌─────────────────────────────────────┐
    │ MSE_perm^C1 ≥ 10% MSE_total^C1    │
    │ Gate: MUST_WORK                     │
    └─────────────────┬───────────────────┘
                      │
                      ▼
[Level 3 - Mechanism Step 3]
    H-M3 ← H-M2
    ┌─────────────────────────────────────┐
    │ R²(C2) ≥ 0.984 + closure ±10%     │
    │ Gate: SHOULD_WORK                   │
    └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4 | All Sequential
═══════════════════════════════════════════════════════════
```

### 5.2 Verification Phases with Gate Conditions

**Phase 1 — Foundation (H-E1)**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | OrbitVar(C2, C3) < 1e-6 under functionally verified S_16³ permutations | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, debug encoder implementation before proceeding.

**Phase 2 — Core Mechanisms (H-M1, H-M2, H-M3)**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST_WORK |
| H-M2 | H-M1 | MUST_WORK |
| H-M3 | H-M2 | SHOULD_WORK |

→ **Gate 2**: H-M1 must pass (causal chain root). H-M2 failure = explore τ metric. H-M3 failure = document limitation.

### 5.3 Dependency Hierarchy

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type    |
|-------|-----------|---------------|--------------|
| 0     | H-E1      | None          | MUST_WORK    |
| 1     | H-M1      | H-E1          | MUST_WORK    |
| 2     | H-M2      | H-M1          | MUST_WORK    |
| 3     | H-M3      | H-M2          | SHOULD_WORK  |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.4 Gantt Timeline (ASCII)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2    │ W3-4    │ W5      │
─────────────────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation  │         │         │         │
  H-E1 (incl. audit) │ ████████│         │         │
  [Gate 1]           │        ◆│         │         │
─────────────────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms  │         │         │         │
  H-M1               │         │ ████████│         │
  H-M2               │         │ ████████│         │
  [Gate 2 (H-M1)]    │         │        ◆│         │
  H-M3               │         │         │ ████████│
─────────────────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
Critical Path: H-E1 (2w) → H-M1+H-M2 (2w, parallel) → H-M3 (1w)
═══════════════════════════════════════════════════════════════════
```

**Note:** H-M1 and H-M2 share the same experimental data (LightGBM training + OrbitVar contrast) and can be evaluated in the same experimental run (Week 3-4).

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks
  Formula: 2 (H-E1) + 2 (H-M1+H-M2, same run) + 1 (H-M3) = 5 weeks
Slack Available: 0 weeks (sequential chain)

Notes:
  - H-M1 and H-M2 share experimental infrastructure (same LightGBM run)
  - Permutation audit (A1) is Week 1 prerequisite — critical before H-E1 coding
  - If R² ceiling reached, τ reporting adds ~2 days (no schedule impact)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (not required)

Verification Phases: 2
1. Foundation (H-E1) — 2 weeks
2. Mechanisms (H-M1, H-M2, H-M3) — 3 weeks

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain (H-M1+H-M2 share run)

Prerequisite (not a hypothesis):
  - Functional permutation audit (Week 1, before H-E1 coding)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Execution Order

```
Step 1: Functional permutation audit (prerequisite) — Week 1
Step 2: Execute H-E1 (OrbitVar for C2, C3) — Week 1-2
Step 3: Evaluate Gate 1 → If pass, proceed; if fail, debug C2/C3 implementation
Step 4: Execute H-M1+H-M2 (OrbitVar contrast + MSE decomposition, same LightGBM run) — Week 3-4
Step 5: Evaluate Gate 2 (H-M1) → If pass, proceed; if fail, explore Kendall's τ
Step 6: Execute H-M3 (mechanism closure + linear head ablation) — Week 5
Step 7: Final: Verification complete — report R², Kendall's τ, MSE_perm, mechanism closure
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Architectural permutation-invariance (DeepSets sum pooling, NFN
equivariance) eliminates encoder-level within-orbit variance (OrbitVar→0) which
propagates to reduced prediction-level variance (MSE_perm), causally improving
LightGBM R² to ≥ 0.984 while CISE's PE noise keeps R²(C1) < R²(C0).

Supporting Evidence:
1. Deep Sets Theorem 2 (Zaheer et al. 2017): sum pooling guarantees OrbitVar=0
   by construction — mathematical proof, not empirical assumption
2. sh1 PASS: CISE achieves OrbitVar=0.010333 under S_16³ (empirically confirmed)
3. sh2 FAIL: cross-model alignment doesn't reduce OrbitVar (orthogonal variances)
   → elimination of PE is the only viable invariance mechanism
4. Bias-variance decomposition: E[(y-ŷ)²] = MSE_res + MSE_perm — standard theory

Strengths:
- Theoretically grounded (Deep Sets theorem proven, not assumed)
- Empirically anchored (sh1/sh2 baselines firmly established)
- Falsifiable at every step with pre-registered quantitative gates
- Positive AND negative outcomes are scientifically publishable

Expected Outcomes:
- P1 (primary): OrbitVar(C2, C3) < 1e-6
- P2 (primary): MSE_perm^C1 ≥ 10% MSE_total^C1; R²(C1) < R²(C0)
- P3: R²(C2) ≥ R²(C0); ΔMSE closure ±10%
- P4: R²(C3 linear) - R²(C2 linear) ≥ 0.01 (structured equivariance adds value)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis (H0-Based)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): There is no significant difference in LightGBM R² between
architecturally invariant encoders (C2, C3) and simple per-layer statistics (C0),
indicating that LightGBM implicitly learns approximate permutation invariance
regardless of encoder architecture.

Counter-Arguments:
1. LightGBM's decision trees are invariant to feature permutations (within a fixed
   embedding) and may learn to ignore channel-order-sensitive features in CISE
2. R² ceiling (1.6% headroom above 0.984) may prevent any encoder from showing
   improvement, even if the mechanism is real
3. sh1's permutation.py may not implement functional permutations — if validated
   CISE OrbitVar is much lower, the mechanism may be absent

Potential Failure Points:
- H-E1 fails: DeepSets/NFN implementation has channel-position indexing bug
- H-M2 fails: LightGBM implicitly cancels MSE_perm (A2 violated)
- H-M3 fails: R² ceiling prevents detection even with correct mechanism

Conditions Under Which H0 Would Be Supported:
- MSE_perm^C1 / MSE_total^C1 < 0.01 (negligible permutation-induced error)
- R²(C2) ≈ R²(C1) ≈ R²(C0) (all encoders equivalent under LightGBM)
- Functional permutation audit reveals non-functional sh1 permutations → CISE OrbitVar actually ≈ 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

H-InvEnc-v1 presents a theoretically rigorous, multi-step causal claim that
architectural invariance eliminates encoder symmetry noise as measured by OrbitVar,
which then reduces prediction-level MSE_perm. The null hypothesis raises a legitimate
concern that gradient-based or tree-based predictors may compensate for encoder noise,
making architectural invariance less impactful in practice than theory predicts.

Resolution Path:
The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Establishes OrbitVar empirically before any
   downstream experiment — separates encoder symmetry from predictor behavior
2. MSE decomposition (H-M2): Directly measures MSE_perm independent of R², giving
   mechanistic evidence even if R² ceiling prevents full statistical power
3. Mechanism closure (H-M3): Pre-registered ±10% criterion makes the causal test
   falsifiable regardless of which direction the result goes

Conditions for Thesis Support:
- H-E1 passes: OrbitVar(C2, C3) < 1e-6 (architectural guarantee verified)
- H-M2 passes: MSE_perm^C1 ≥ 10% of MSE_total^C1 (LightGBM doesn't cancel noise)
- H-M3 passes: R²(C2) ≥ 0.984 AND closure ±10% holds

Conditions for Antithesis Support:
- H-E1 fails: Implementation bug (not antithesis support, just technical failure)
- H-M2 fails: MSE_perm < 1% (LightGBM implicitly invariant)
- H-M1+H-M2 pass but H-M3 fails: Mechanism exists but R² ceiling prevents measurement

Nuanced Outcome Possibilities:
1. Full Support: All 4 hypotheses pass → Thesis validated with causal mechanism closed
2. Mechanism without R² gain: H-M1+H-M2 pass, H-M3 fails R² but closure holds → Mechanism
   real but ceiling prevents R² measurement; Kendall's τ and distribution-shift as fallback claims
3. Mechanism absent: H-M2 fails → LightGBM implicit invariance; H0 supported; publishable
   as negative finding establishing LightGBM's robustness to encoder symmetry noise
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Symmetry enforcement | Deep Sets Theorem 2 guarantees OrbitVar=0 | Implementation bug possible | H-E1 empirical test + functional audit |
| Propagation to MSE | OrbitVar → MSE_perm non-negligible | LightGBM compensates implicitly | H-M2 direct MSE decomposition |
| R² improvement | Invariance removes noise source → R²↑ | R² ceiling (1.6%) masks gain | H-M3 closure criterion + τ backup |
| Generalization | Invariant encoder more robust to shifts | CIFAR-10-C may not test right axis | Optional distribution-shift test |

Overall Robustness Score: High (theoretically grounded, multi-gate verification, both positive and negative outcomes publishable)
Confidence in Verification Plan: 0.78

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### Executive Summary

**Main Hypothesis:** Architectural permutation-invariance eliminates encoder symmetry noise (OrbitVar), reducing prediction-level MSE_perm and improving LightGBM R² to ≥ 0.984 on ModelZooDataset CIFAR10-GS.
- ID: H-InvEnc-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (45% scope reduction via BUILD_ON facts)
- Sub-Hypotheses: 4 total — H-E: 1, H-M: 3, H-C: 0
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1: H-E1, Gate 2: H-M1)

**Risk Assessment:** High
- Primary concerns: (R1) permutation audit may reveal non-functional sh1 permutations; (R2) LightGBM may implicitly cancel MSE_perm

**Immediate Action:** Week 1 — functional permutation audit before any coding; then begin H-E1 encoder implementation.

---

### Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases covering full causal chain
- H0 addressed: LightGBM implicit invariance tested directly via MSE decomposition
- First joint OrbitVar + MSE_perm + R² measurement planned in a closed causal loop

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- Prerequisite: Functional permutation audit (sh1 apply_channel_permutation())
- H-E1: OrbitVar(C2, C3) < 1e-6 under functionally verified S_16³ permutations
- Gate 1: MUST PASS — failure blocks all downstream hypotheses

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: OrbitVar contrast — C1/C2 ratio > 1e4 (Week 3-4, same run as H-M2)
- H-M2: MSE_perm^C1 ≥ 10% of MSE_total^C1 (Week 3-4)
- H-M3: R²(C2) ≥ 0.984 + closure ±10% + linear head ablation (Week 5)
- Gate 2: H-M1 must pass

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, debug C2/C3 implementation (implementation bug, not scientific failure)
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → EXPLORE — check permutation audit result
   - H-M2 FAIL → EXPLORE — H0 supported; switch to Kendall's τ; still publishable
   - H-M3 FAIL → PIVOT or EXPLORE based on failure type

**Open Questions:**
- Is sh1's apply_channel_permutation() implementing functional (coupled row-column) permutations? (Mandatory audit before coding)
- What is CISE's actual LightGBM R² on ModelZooDataset CIFAR10-GS? (Not measured in sh1)
- Does CIFAR-10-C variant of ModelZooDataset exist or need construction for distribution-shift test?
- Will NFN's spatial folding (for CNNs) match DWSNet's coupling exactly on CIFAR10-GS architecture?

**Recommendations:**

1. **Immediate Actions:**
   - Week 1: Execute functional permutation audit before any encoder implementation
   - Set up MSE_perm measurement infrastructure (orbit sampling K=50) alongside OrbitVar

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path
   - Reserve Week 5 buffer for H-M3 if H-M2 takes longer than expected

3. **Failure Management:**
   - Document all gate decisions regardless of outcome
   - Pre-register Kendall's τ as backup metric before running any experiment
   - If R² ceiling reached, distribution-shift test converts findings to publishable robustness claim

---

### Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-InvEnc-v1)
- Supplementary: 02_synthesis.yaml, 01_round_table/final_opinions.yaml
- Schema version: 10.0.0 | Discussion exchanges: 16 | Convergence: 6/6 criteria met

**B. MCP Tool Usage Summary**
- Total MCP inquiries: 2 (H-E1-verification, H-M-integrated)
- Tools: mcp__clearThought__scientificmethod (hypothesis + experiment stages each)
- Mode: Incremental (Phase 2A pre-mapped hypothesis sources used)
