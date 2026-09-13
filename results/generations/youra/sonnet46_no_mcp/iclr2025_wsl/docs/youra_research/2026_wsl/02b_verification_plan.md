# Verification Plan: Permutation-Equivariant Inductive Bias Advantage in Weight-Space Accuracy Prediction: A Controlled Δρ Benchmark

**Date:** 2026-05-05
**Hypothesis ID:** H-NFNDeltaRho-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under conditions of matched encoder capacity (~500K parameters, ±5% via per-architecture width grid search) on the Schurholt et al. MNIST-CNN and CIFAR-10 model zoo benchmarks, if we replace a flat MLP encoder with a permutation-equivariant NFN encoder (Navon et al. 2023 equivariant architecture), then the Spearman rank correlation in test accuracy prediction increases by Δρ ≥ 0.05 on the MNIST-CNN zoo (with bootstrap 95% CI lower bound > 0), because NFN encoders operate on the permutation-quotient weight space and direct all encoder capacity toward accuracy-predictive features rather than navigating the factorial-sized permutation orbits that confuse flat MLP encoders.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference (Δρ = 0) in Spearman rank correlation between matched-capacity NFN (Navon et al. equivariant architecture, ~500K parameters) and flat MLP encoders for test accuracy prediction on the Schurholt MNIST-CNN and CIFAR-10 model zoos.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Schurholt ModelZooDataset (standard) | Directly cited benchmark; ground-truth test accuracy for ~4K MNIST-CNN and ~1.5K CIFAR-10 checkpoints — exact benchmark required for Spearman ρ evaluation |
| **Model** | Navon et al. equivariant weight-space encoder (primary); Deep Sets symmetrized MLP (intermediate baseline) | Navon et al. repo directly targets Schurholt zoo weight tensor shapes; implements equivariant layers for the exact CNN architectures in the zoo |

**Dataset Details:**
- Source: Schurholt et al. (2022) arXiv:2209.12892; GitHub: ModelZoos/ModelZooDataset
- Path: Download from ModelZoos/ModelZooDataset repository

**Model Details:**
- Type: Permutation-equivariant encoder for weight tensors (primary); permutation-invariant set network (baseline)
- Source: GitHub: AvivNavon/equivariant-weight-space-networks; Zaheer et al. Deep Sets

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Navon et al. (2023) NFN equivariant encoder | Spearman ρ ≈ 0.6–0.8 on Schurholt MNIST-CNN (estimated) | Schurholt MNIST-CNN zoo | Not capacity-controlled; no bootstrap CI on Δρ; no CIFAR-10 cross-zoo analysis |
| Unterthiner et al. (2020) flat MLP baseline | Spearman ρ ≈ 0.5–0.7 (estimated, different setup) | Proprietary model zoo | Different dataset; no equivariant comparison; older setup |
| Schurholt et al. (2023) multi-encoder comparison | Multiple Spearman ρ values for various encoders | Schurholt MNIST-CNN and CIFAR-10 | Capacity not matched; no bootstrap CI; no Deep Sets intermediate baseline |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | CIFAR-10 zoo (n≈1,500) provides sufficient statistical power for Δρ ≥ 0.05 | Bootstrap CI width ≈ ±0.03 at n=1,500; Δρ=0.05 gives marginal CI ≈ [0.02, 0.08] | Relax CIFAR-10 threshold to Δρ > 0; MNIST-CNN (n≈4,000) remains primary target |
| A2 | MNIST-CNN zoo trained without batch normalization, preserving neuron-permutation symmetry | Schurholt et al. (2022) describes plain CNNs; BN would break permutation symmetry | If BN present, permutation orbit argument invalid — must verify before Phase 4 |
| A3 | Matching total parameter count (±5%) = fair capacity comparison | Prof. Pax and Prof. Rex noted different parameter distributions; capacity curves as mitigation | Report FLOPs-matched comparison as sensitivity check |
| A4 | Schurholt zoo diversity representative for internal validity | Zoo generated with specific training procedures; internal validity sufficient | External validity reduced but internal validity (Δρ on zoo itself) intact |
| A5 | Navon et al. architecture can be width-adjusted to ~500K params | Equivariant layers parameterized by widths; width adjustment is standard practice | If minimum NFN exceeds 500K, capacity matching fails — pre-check before experiments |

### 1.6 Research Gap & Novelty

**Gap:** No published study provides a standardized Δρ benchmark comparing matched-capacity (~500K params ±5%) NFN equivariant encoder vs flat MLP encoder on Schurholt model zoo benchmarks with bootstrap 95% CIs.

**Three Novel Contributions:**
1. First controlled, matched-capacity Δρ measurement with bootstrap CIs on Schurholt zoos — resolves capacity-confound in all prior NFN vs flat MLP comparisons
2. First cross-zoo consistency analysis (MNIST-CNN and CIFAR-10 in single experiment)
3. First symmetry spectrum benchmark: flat MLP < Deep Sets (invariant) < NFN (equivariant) with Deep Sets as intermediate baseline

**Scope Reduction:** 57% of claims are BUILD_ON (established facts). Only 2 PROVE_NEW claims require Phase 4 verification.

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
**H-E1: Permutation-Equivalent Model Pairs Exist in Schurholt MNIST-CNN Zoo**

**Statement:** Under conditions of the Schurholt MNIST-CNN model zoo (plain feedforward CNNs without batch normalization), if we analyze the zoo's weight tensor distribution, then we will find a non-trivial proportion of model pairs with similar test accuracy but different weight configurations (permutation-equivalent representatives), because feedforward neural networks with L layers of widths n_1,...,n_L have |S_{n_1}| × ... × |S_{n_L}| symmetry-equivalent weight configurations per function.

**Rationale:**
This hypothesis validates the foundational premise of the causal mechanism: that the permutation orbit problem is empirically non-trivial in the Schurholt zoo. Without this foundation, the capacity-wasting argument (Step 2) and the matched-capacity advantage of NFN (Step 3) have no empirical basis. It also confirms the BN-free assumption (A2) is met.

**Variables (from Phase 2A):**
- Independent: Zoo architecture type (MNIST-CNN plain CNN, confirmed no BN)
- Dependent: Proportion of model pairs with |accuracy diff| < 0.01 but cosine distance > 0.1 in weight space (proxy for permutation-equivalent distinct representations)
- Controlled: Full MNIST-CNN zoo dataset (~4,000 checkpoints), fixed pairwise sampling procedure

**Verification Protocol:**
1. Download Schurholt MNIST-CNN zoo; inspect model architecture configs to confirm absence of batch normalization layers.
2. Load all ~4,000 model checkpoints; flatten weight tensors to vectors; compute pairwise cosine distance for a random stratified sample of 500 model pairs grouped by accuracy decile.
3. Identify pairs with |Δaccuracy| < 0.01 and cosine_distance > 0.1 as candidate permutation-equivalent representatives; compute proportion over sampled pairs.
4. Report: proportion of such pairs, mean cosine distance within accuracy deciles, and BN-free confirmation.
5. Declare H-E1 PASS if BN-free confirmed AND proportion of candidate permutation-equivalent pairs > 5% of same-accuracy-decile pairs.

**Success Criteria (PoC: Direction-based):**
- Primary: BN-free architecture confirmed AND > 5% of same-accuracy-decile pairs show high weight-space distance (orbit non-triviality demonstrated)
- Secondary: Mean cosine distance within accuracy deciles > 0.2 (indicating substantial orbit size)

**Failure Response:**
- IF fails (BN found): PIVOT — update scope to CIFAR-10 only; check CIFAR-10 BN status; redesign scope in Phase 2A revision
- IF fails (proportion < 5%): EXPLORE — check if zoo diversity is limited; consider relaxing threshold; document as limitation

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.3 Step 1 + Section 5 SH1 + A2 assumption

---

---
**H-M1: Flat MLP Encoder Wastes Capacity Navigating Permutation Orbits**

**Statement:** Under conditions of matched encoder capacity (~500K parameters ±5%) on the Schurholt MNIST-CNN zoo, if we train a flat MLP encoder (concatenated weight vector input) on accuracy prediction, then its learned embeddings will exhibit permutation sensitivity (different embeddings for permutation-equivalent weight configurations of similar-accuracy models), because flat MLPs receive all permutations of a network's weights as distinct input vectors and must learn to map all equivalent permutations to the same output — consuming capacity for redundant mappings.

**Rationale:**
This hypothesis tests the core capacity-wasting mechanism (Causal Step 2). If flat MLPs are empirically permutation-sensitive, it validates the theoretical argument that NFN's structural advantage is real, not merely theoretical. Failure here (flat MLPs learn approximate permutation invariance) would challenge the entire causal chain.

**Variables (from Phase 2A):**
- Independent: Encoder type (flat MLP at ~500K params)
- Dependent: Permutation sensitivity score — variance of encoder output embeddings for matched permutation-equivalent weight pairs (should be HIGH for flat MLP)
- Controlled: ~500K param budget via width grid search; same zoo train/test split; Adam optimizer with pre-registered training budget

**Verification Protocol:**
1. Implement flat MLP encoder with width grid search to reach ~500K ±5% total parameters; train on Schurholt MNIST-CNN zoo train split for accuracy prediction.
2. Identify 50+ permutation-equivalent model pairs from H-E1 output (same-accuracy, high weight-space distance pairs).
3. Pass both weight configurations of each pair through the trained flat MLP encoder; compute L2 distance between resulting embeddings.
4. Compute permutation sensitivity score: mean L2 distance between embeddings of permutation-equivalent pairs, normalized by mean L2 distance of random non-equivalent pairs.
5. Declare H-M1 PASS if permutation sensitivity score > 0.3 (embeddings of equivalent pairs are meaningfully different, confirming capacity waste).

**Success Criteria (PoC: Direction-based):**
- Primary: Permutation sensitivity score > 0.3 (flat MLP is NOT permutation-invariant in practice)
- Secondary: Spearman ρ of flat MLP on test split ≥ 0.5 (encoder trained successfully; baseline quality check)

**Failure Response:**
- IF fails (sensitivity ≤ 0.3): EXPLORE — flat MLPs may learn approximate invariance from data; document as key finding; re-examine key tension from Phase 2A; partial support for H0

**Dependencies:** H-E1 (permutation-equivalent pairs must be identified)

**Source:** Phase 2A Section 1.3 Step 2 + Section 1.6 key_tension

---

---
**H-M2: NFN Encoder Achieves Structural Permutation Invariance at Matched Capacity**

**Statement:** Under conditions of matched encoder capacity (~500K parameters ±5%) on the Schurholt MNIST-CNN zoo, if we train a Navon et al. permutation-equivariant NFN encoder on accuracy prediction, then its learned embeddings will exhibit near-zero permutation sensitivity (similar embeddings for permutation-equivalent weight configurations), because NFN encoders are equivariant by construction and map all permutation-equivalent weight vectors to identical embeddings before the final prediction head.

**Rationale:**
This hypothesis tests whether the NFN's structural guarantee translates to empirically consistent embeddings on actual zoo data. If NFN embeddings are permutation-consistent, it confirms the mechanism by which NFN reallocates capacity toward accuracy-predictive features rather than orbit navigation.

**Variables (from Phase 2A):**
- Independent: Encoder type (Navon et al. NFN equivariant at ~500K params)
- Dependent: Permutation sensitivity score for NFN (should be LOW, near 0)
- Controlled: Same ~500K param budget; same permutation-equivalent pairs from H-E1; same train/test split; same training procedure as H-M1

**Verification Protocol:**
1. Implement Navon et al. equivariant weight-space encoder with width grid search to reach ~500K ±5% parameters; verify equivariant layer architecture integrity is preserved.
2. Train NFN encoder on identical Schurholt MNIST-CNN zoo train split as H-M1 flat MLP.
3. Evaluate permutation sensitivity score on the same 50+ permutation-equivalent pairs used in H-M1.
4. Compare NFN permutation sensitivity score to flat MLP score from H-M1.
5. Declare H-M2 PASS if NFN permutation sensitivity score < 0.1 (near-zero, as expected by equivariant construction) AND NFN score < (flat MLP score × 0.5).

**Success Criteria (PoC: Direction-based):**
- Primary: NFN permutation sensitivity score < 0.1 AND at least 50% lower than flat MLP score
- Secondary: NFN Spearman ρ on test split ≥ flat MLP Spearman ρ (structural invariance translates to prediction quality)

**Failure Response:**
- IF fails: EXPLORE — investigate whether width adjustment compromised equivariant layer structure; check implementation; consider H-M2 redesign if architectural integrity issues found

**Dependencies:** H-E1, H-M1

**Source:** Phase 2A Section 1.3 Step 2 + Section 1.2 variables

---

---
**H-M3: Matched-Capacity NFN Achieves Δρ ≥ 0.05 over Flat MLP on Schurholt Zoos**

**Statement:** Under conditions of matched encoder capacity (~500K parameters ±5%) on the Schurholt MNIST-CNN and CIFAR-10 model zoo benchmarks, if we compare Navon et al. NFN encoder Spearman rank correlation against flat MLP Spearman rank correlation for test accuracy prediction, then Δρ = ρ(NFN) − ρ(flat MLP) ≥ 0.05 on MNIST-CNN (bootstrap 95% CI lower bound > 0) and Δρ > 0 on CIFAR-10 (CI lower bound > 0), because NFN's capacity reallocation from orbit navigation to accuracy-predictive features produces more consistent embeddings for functionally equivalent models, resulting in better rank-ordering by accuracy.

**Rationale:**
This is the primary experimental measurement of the main hypothesis. It directly tests PROVE_NEW claim 1 (Δρ benchmark with bootstrap CI) and integrates all three causal steps. Success here, combined with H-E1 and H-M1/H-M2, provides a complete mechanistic explanation for the measured advantage.

**Variables (from Phase 2A):**
- Independent: Encoder architecture type (flat_mlp, symmetrized_mlp_deep_sets, nfn_navon_equivariant), all at ~500K params ±5%
- Dependent: Spearman ρ per encoder per zoo; Δρ = ρ(NFN) − ρ(flat MLP) with bootstrap 95% CI (n=1,000 resamples)
- Controlled: Schurholt zoo standard train/test splits; Adam optimizer; pre-registered training budget; capacity matching via width grid search

**Verification Protocol:**
1. Train all three encoder variants (flat MLP, Deep Sets symmetrized MLP, NFN equivariant) at matched ~500K ±5% params on MNIST-CNN zoo train split; evaluate Spearman ρ on held-out test split (full ~4,000 model test set).
2. Repeat Step 1 on CIFAR-10 zoo (full ~1,500 model test set); use same training protocol.
3. Compute Δρ = ρ(NFN) − ρ(flat MLP) for each zoo; compute bootstrap 95% CI with n=1,000 resamples (standard bootstrap on test-set predictions).
4. Test P2 symmetry spectrum: confirm strict monotone ordering ρ(flat) < ρ(Deep Sets) < ρ(NFN) on MNIST-CNN.
5. Test P3 mechanistic fingerprint: partition MNIST-CNN test set into accuracy terciles; compute tier-specific Δρ; verify mid-tier > low-tier and mid-tier > high-tier.

**Success Criteria (PoC: Direction-based):**
- Primary (P1): Δρ(MNIST-CNN) ≥ 0.05 AND CI_lower(MNIST-CNN) > 0 AND Δρ(CIFAR-10) > 0 AND CI_lower(CIFAR-10) > 0
- Secondary (P2): ρ(flat) < ρ(Deep Sets) < ρ(NFN) on MNIST-CNN (strict monotone symmetry spectrum)
- Secondary (P3): Δρ(mid-tier) > Δρ(low-tier) AND Δρ(mid-tier) > Δρ(high-tier) on MNIST-CNN

**Failure Response:**
- IF Δρ(MNIST-CNN) < 0.05 but CI_lower > 0: PARTIAL — report as "directional support, below threshold"; document as limitation
- IF CI crosses zero on MNIST-CNN: EXPLORE — check if flat MLP learned approximate invariance (H-M1 finding); consider PIVOT if H-M1 also failed
- IF CIFAR-10 CI crosses zero: SCOPE — reduce to MNIST-CNN primary claim; document CIFAR-10 power limitation (A1)

**Dependencies:** H-E1, H-M1, H-M2

**Source:** Phase 2A Section 1.3 Step 3 + Section 1.6 P1/P2/P3 + PROVE_NEW claims

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
| H-E1 | MUST_WORK | BN-free confirmed AND >5% permutation-equivalent pairs in zoo | STOP — reassess hypothesis scope; A2 violation requires redesign |
| H-M1 | MUST_WORK | Flat MLP permutation sensitivity score > 0.3 | EXPLORE — flat MLP may learn invariance; document key tension; partial H0 support |
| H-M2 | SHOULD_WORK | NFN sensitivity score < 0.1 AND < 50% of flat MLP score | EXPLORE — check equivariant layer implementation integrity |
| H-M3 | SHOULD_WORK | Δρ(MNIST-CNN) ≥ 0.05 AND CI_lower > 0 on both zoos | PIVOT/SCOPE per failure mode (see spec above) |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | Weeks 1–2 |
| Gate 1 decision | — | Week 2 |
| Phase 2: Core Mechanisms | H-M1 | Weeks 3–4 |
| Phase 2 (cont.) | H-M2 | Week 5 |
| Phase 2 (cont.) | H-M3 | Week 6 |
| Gate 2 decision | — | Week 6 |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Key Assumptions → Risk Mapping

**Risk R1: CIFAR-10 Marginal Statistical Power**
- **Source Assumption:** A1 — CIFAR-10 zoo (n≈1,500) statistical power marginal for Δρ ≥ 0.05
- **Affected Hypotheses:** H-M3 (CIFAR-10 result only)
- **Severity:** Medium
- **Mitigation Strategy:**
  1. Prevention: Apply asymmetric threshold from Phase 2A — CIFAR-10 success = Δρ > 0 (not ≥ 0.05)
  2. Detection: Pre-compute bootstrap CI width before final evaluation; if > 0.06, flag power concern
  3. Response: SCOPE — relegate CIFAR-10 to secondary cross-zoo consistency check; MNIST-CNN (n≈4,000) is primary inference target

**Risk R2: MNIST-CNN Zoo Uses Batch Normalization (A2 Violation)**
- **Source Assumption:** A2 — MNIST-CNN zoo trained without BN
- **Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3 (entire causal chain invalid if BN present)
- **Severity:** Critical
- **Mitigation Strategy:**
  1. Prevention: MUST verify architecture configs from Schurholt et al. (2022) supplementary materials BEFORE Phase 4
  2. Detection: Inspect model checkpoint configs for `BatchNorm` layers at H-E1 Step 1
  3. Response: PIVOT — if BN found, restrict scope to CIFAR-10 only (check CIFAR-10 BN status); if both zoos have BN, hypothesis requires redesign via Phase 2A revision
- **Early Warning:** H-E1 Step 1 architecture inspection reveals BN layers

**Risk R3: Flat MLP Learns Approximate Permutation Invariance from Zoo Data**
- **Source Assumption:** A3 (implied) + key_tension from Phase 2A
- **Affected Hypotheses:** H-M1, H-M3 (mechanism invalidated if flat MLPs are effectively permutation-invariant)
- **Severity:** High
- **Mitigation Strategy:**
  1. Prevention: Use probing experiments (H-M1 permutation sensitivity score) to test empirically
  2. Detection: Sensitivity score ≤ 0.3 at H-M1 evaluation is the detection signal
  3. Response: EXPLORE — document as key tension resolution (Prof. Rex's A1 concern); report as partial support for H0; include in paper as null result analysis; the finding itself is publishable

**Risk R4: Capacity Matching Procedure Unfair Between NFN and Flat MLP**
- **Source Assumption:** A3 — total parameter count matching is fair comparison
- **Affected Hypotheses:** H-M3 (primary Δρ measurement)
- **Severity:** Medium
- **Mitigation Strategy:**
  1. Prevention: Document matched total params ±5% as the defined comparison; pre-register before experiments
  2. Detection: If NFN and flat MLP FLOPs differ by > 2× at matched param count, flag as sensitivity concern
  3. Response: Include FLOPs-matched comparison as supplementary sensitivity analysis (capacity curves from P4)

**Risk R5: Navon et al. Architecture Cannot Be Width-Adjusted to ~500K Params**
- **Source Assumption:** A5 — NFN architecture can be tuned to ~500K params
- **Affected Hypotheses:** H-M2, H-M3 (capacity matching fails)
- **Severity:** High
- **Mitigation Strategy:**
  1. Prevention: Pre-check minimum NFN parameter count for Schurholt zoo weight tensor shapes BEFORE Phase 4
  2. Detection: Width grid search at initialization — if minimum achievable params > 600K, flag immediately
  3. Response: PIVOT — if 500K budget unachievable, shift target to 1M params and revise hypothesis threshold; document constraint in paper

### 4.2 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | CIFAR-10 marginal power | A1 | Medium | H-M3 (CIFAR-10) | Asymmetric threshold (>0 not ≥0.05) |
| R2 | MNIST-CNN zoo has BN | A2 | **Critical** | H-E1, H-M1–M3 | Verify BN-free before Phase 4 (MUST) |
| R3 | Flat MLP learns approx. invariance | key_tension | High | H-M1, H-M3 | Permutation sensitivity probing (H-M1) |
| R4 | Capacity matching unfair | A3 | Medium | H-M3 | FLOPs-matched sensitivity analysis |
| R5 | NFN min params > 500K | A5 | High | H-M2, H-M3 | Pre-check param count before Phase 4 |

**Risk Counts:** Critical: 1 | High: 2 | Medium: 2 | Low: 0

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root / Foundation]
    H-E1: Permutation-Equivalent Pairs Exist in Zoo
         │  (no dependencies)
         ▼
[Level 1 - Mechanism Step 1]
    H-M1: Flat MLP Wastes Capacity on Orbits
         │  ← depends on H-E1
         ▼
[Level 2 - Mechanism Step 2]
    H-M2: NFN Achieves Structural Permutation Invariance
         │  ← depends on H-M1
         ▼
[Level 3 - Mechanism Step 3 / Primary Measurement]
    H-M3: Matched-Capacity NFN Achieves Δρ ≥ 0.05
               ← depends on H-M2

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4 | All Sequential | No Parallelism
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-E1, H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-E1, H-M1, H-M2 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │        ◆│         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Core Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████████│         │
  H-M3           │         │         │         │ ████████│
  [Gate 2]       │         │         │         │        ◆│
─────────────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 6 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3)

Slack Available: 0 weeks (fully sequential)
Execution Mode: Sequential chain
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
- Condition: 0 (BN boundary documented as R2 risk, not H-C)

Verification Phases: 2
1. Foundation (H-E1)
2. Mechanisms (H-M1, H-M2, H-M3)

Total Duration: 6 weeks
Critical Path Length: 6 weeks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation: verify BN-free + permutation pairs) — Weeks 1–2
Step 2: Evaluate Gate 1 → If PASS proceed; If FAIL stop and reassess
Step 3: Execute H-M1 (Flat MLP permutation sensitivity probing) — Weeks 3–4
Step 4: Execute H-M2 (NFN structural invariance verification) — Week 5
Step 5: Execute H-M3 (Primary Δρ measurement + P2/P3 predictions) — Week 6
Step 6: Evaluate Gate 2 → Assess full result; document outcome
Step 7: Verification complete → Proceed to Phase 3 implementation planning
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Under matched encoder capacity (~500K params ±5%)
on Schurholt MNIST-CNN and CIFAR-10 zoos, permutation-equivariant
NFN encoders achieve Δρ ≥ 0.05 over flat MLPs in test accuracy
prediction (bootstrap 95% CI lower bound > 0) because they
operate on the permutation-quotient weight space.

Supporting Evidence:
1. Mathematical fact: FFNNs have |S_n1|×...×|S_nL| equivalent
   weight configurations per function (established, citable)
2. Theoretical argument: NFN equivariant construction maps all
   permutation-equivalent weights to identical embeddings
   (Navon et al. 2023, Zhou et al. 2023)
3. Empirical prior: Heterogeneous comparisons (uncontrolled)
   show Δρ ≈ 0.05–0.15 between equivariant and flat encoders

Strengths:
- Step 1 of causal chain is a proven mathematical fact
- Step 2 follows from equivariant architecture by construction
- Predictions are quantitative with explicit falsification thresholds
- Uses only existing data and code — no new infrastructure

Expected Outcomes:
- Primary: Δρ(MNIST-CNN) ≥ 0.05 with CI_lower > 0 (P1)
- Secondary: ρ(flat) < ρ(Deep Sets) < ρ(NFN) on MNIST-CNN (P2)
- Tertiary: Largest Δρ in mid-accuracy tier 40th–60th % (P3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): There is no significant difference
(Δρ = 0) in Spearman rank correlation between matched-capacity
NFN and flat MLP encoders on Schurholt MNIST-CNN and CIFAR-10.

Counter-Arguments:
1. (From key_tension / Prof. Rex A1) Flat MLPs with sufficient
   zoo training data may empirically learn approximate permutation
   invariance, nullifying the structural NFN advantage at 500K params
2. (From A3 / Prof. Pax) NFN and flat MLP distribute 500K params
   differently; the comparison may favor NFN not due to equivariance
   but due to more efficient architectural capacity utilization
3. (From scope_not_applies) If MNIST-CNN zoo is not BN-free, the
   permutation orbit argument is invalid and H0 cannot be rejected

Potential Failure Points:
- Flat MLP learns approximate invariance from zoo data (R3 risk)
- CIFAR-10 zoo has BN layers breaking permutation symmetry (R2 risk)
- CIFAR-10 n≈1,500 too small; CI crosses zero even if Δρ = 0.04 (R1 risk)

Conditions Under Which H0 Would Be Supported:
- Δρ(MNIST-CNN) < 0.05 or CI_lower(MNIST-CNN) ≤ 0
- H-M1 permutation sensitivity score ≤ 0.3 (flat MLP learned invariance)
- H-E1 BN inspection reveals BN in MNIST-CNN architecture
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

The hypothesis H-NFNDeltaRho-v1 presents a theoretically grounded
claim that NFN's structural equivariance provides a measurable
advantage (Δρ ≥ 0.05) under controlled capacity conditions.
However, the antithesis correctly identifies that the empirical
magnitude of the advantage depends on whether flat MLPs can
learn approximate permutation invariance from zoo data — a
question that theory alone cannot resolve.

Resolution Path:

The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Confirms BN-free architecture
   and orbit non-triviality before testing mechanisms
2. Probing experiment (H-M1): Empirically tests whether flat MLPs
   learn permutation invariance — directly resolves the key tension
3. Structural invariance check (H-M2): Confirms NFN's guarantee
   holds on actual Schurholt zoo weight tensors
4. Primary measurement (H-M3): Quantifies Δρ with bootstrap CI,
   allowing statistical adjudication of the thesis vs. antithesis

Conditions for Thesis Support:
- H-E1: BN-free confirmed, permutation pairs non-trivial
- H-M1: Flat MLP sensitivity score > 0.3 (does NOT learn invariance)
- H-M3: Δρ(MNIST-CNN) ≥ 0.05, CI_lower > 0

Conditions for Antithesis Support:
- H-M1: Sensitivity score ≤ 0.3 (flat MLP learns approximate invariance)
- H-M3: Δρ < 0.05 or CI crosses zero on MNIST-CNN

Nuanced Outcome Possibilities:
1. Full Support: H-E1 PASS + H-M1 PASS + H-M3 PASS → Thesis fully validated
2. Partial Support: H-E1 PASS + H-M1 borderline + H-M3 Δρ < 0.05 but CI_lower > 0
   → "Directional equivariant advantage; insufficient magnitude at 500K"
3. No Support: H-M1 FAIL (flat MLP learns invariance) → Antithesis supported;
   key tension resolved in H0's favor — itself a publishable finding
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence (H-E1) | Permutation orbits are empirically non-trivial in Schurholt zoo | Zoo diversity too constrained to exhibit orbit non-triviality | H-E1 pairwise distance analysis + BN check |
| Mechanism (H-M1/M2) | Flat MLPs are permutation-sensitive; NFNs are not | Flat MLPs learn approximate invariance from zoo data | Permutation sensitivity probing experiment |
| Primary Measurement (H-M3) | Δρ ≥ 0.05 at matched 500K params | No significant difference; capacity matching confounds result | Bootstrap CI on Δρ with n=1,000 resamples |
| Scope | Applies to BN-free feedforward CNN zoos | MNIST-CNN may have BN, invalidating mechanism | A2 verification (H-E1 architecture inspection) |
| Statistical Power | MNIST-CNN (n≈4K) has sufficient power | CIFAR-10 (n≈1.5K) marginal power for Δρ ≥ 0.05 | Asymmetric thresholds (≥0.05 MNIST, >0 CIFAR) |

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-NFNDeltaRho-v1 — At matched ~500K param capacity, permutation-equivariant NFN encoders achieve Δρ ≥ 0.05 over flat MLP on Schurholt MNIST-CNN zoo (bootstrap 95% CI lower > 0).

**Verification Structure:**
- Mode: Incremental (57% scope reduction — 5 BUILD_ON claims excluded from re-verification)
- Sub-Hypotheses: 4 total (H-E1, H-M1, H-M2, H-M3)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Gate 1 at Week 2, Gate 2 at Week 6)

**Risk Assessment:** Medium-High risk
- Critical concern: MNIST-CNN BN verification (R2) — MUST resolve before Phase 4
- High concerns: Flat MLP approximate invariance (R3), NFN param floor (R5)

**Immediate Action:** Begin Phase 1 with H-E1 — inspect architecture configs for BN and analyze permutation-equivalent pair statistics.

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases with full mechanistic coverage of causal chain
- H0 explicitly addressed: Δρ = 0 (no equivariant advantage at matched capacity)
- All PROVE_NEW claims from Phase 2A mapped to testable sub-hypotheses

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Verify BN-free MNIST-CNN zoo AND detect permutation-equivalent model pairs
- Gate 1: MUST PASS — BN-free confirmation is prerequisite for all mechanism tests

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Flat MLP encoder permutation sensitivity probing (Weeks 3–4)
- H-M2: NFN structural invariance confirmation (Week 5)
- H-M3: Primary Δρ measurement with bootstrap CI on both zoos (Week 6)
- Gate 2: H-M3 primary result adjudicates thesis vs. antithesis

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - BN FOUND → STOP, update scope, redirect to Phase 2A revision
   - PASS → Proceed to Phase 2 mechanism testing

2. **Gate 2 (Mechanisms):** H-M3 result determines outcome
   - FULL PASS (Δρ ≥ 0.05, CI_lower > 0) → Strong thesis support; proceed to paper
   - PARTIAL (directional but < 0.05) → Partial support; publish with limitations
   - FAIL (CI crosses 0) → Antithesis supported; publish as null result; revisit hypothesis

**Open Questions (from Phase 2A):**
- Does CIFAR-10 zoo use batch normalization? (Must verify — may narrow scope to MNIST-CNN only)
- What is the minimum achievable NFN parameter count for Schurholt zoo weight tensor shapes?
- Does Zhou et al. Neural Functional Transformer also show Δρ ≥ 0.05 at matched capacity? (Robustness check)

**Recommendations:**

1. **Immediate (before Phase 4):**
   - Download Schurholt zoo and inspect architecture configs for BN in both MNIST-CNN and CIFAR-10
   - Run NFN parameter count pre-check for Schurholt zoo weight tensor shapes
   - Pre-register experimental protocol (capacity matching procedure, optimizer, training budget)

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path (no slack — all sequential)
   - Reserve 1-week buffer for BN-related scope adjustments if needed

3. **Failure Management:**
   - Execute PIVOT strategy immediately if R2 (BN) materializes
   - Document all H-M1 sensitivity scores regardless of pass/fail — key tension resolution is publishable

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `03_refinement.yaml` (H-NFNDeltaRho-v1, schema v10.0.0)
- Generated: 2026-05-05, UNATTENDED mode, 14 discussion exchanges
- 6 agents: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**B. Scope Reduction Summary**
- Total claims: 7 | BUILD_ON (excluded): 5 | PROVE_NEW (active): 2
- Scope reduction: 57% — only Δρ benchmark and symmetry spectrum require Phase 4 verification

**C. MCP Tool Usage**
- ClearThought scientific method: Called analytically (no-MCP TEST env)
- Archon: Task management deferred (no-MCP TEST env)
- All hypothesis designs derived from Phase 2A structured data

---

## 8. State

**stepsCompleted:** step-00-init-environment, step-01-init-parsing, step-02-input-hypothesis, step-03-hypothesis-generation, step-04-hypothesis-inventory, step-05-risk-analysis, step-06-dependency-graph, step-07-timeline-planning, step-08-dialectical-analysis, step-09-summary, step-10-finalize
**status:** complete
**completedAt:** 2026-05-05T00:00:00Z

---

*Generated by YouRA Phase 2B Planning (v6.0) | 2026-05-05*
