# Verification Plan: NFT vs. Flat-MLP for FC-MLP Model Zoo Generalization Gap Prediction

**Date:** 2026-03-16
**Hypothesis ID:** H-NFT-GenGap-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

**Under** conditions where FC-MLP model zoos exhibit permutation symmetry in neuron ordering,
**If** NFT (Neural Functional Transformer) encoders are used instead of flat-MLP encoders,
**Then** the permutation robustness (Δρ) will be significantly lower (NFT Δρ < 0.02 vs. flat-MLP Δρ > 0.10) and cross-pipeline transfer gap will be smaller (NFT Δ < 0.05 vs. flat-MLP Δ > 0.10),
**Because** NFT's equivariant attention mechanism captures neuron concentration patterns invariantly under permutation, providing structural inductive bias that flat-MLPs lack.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in Spearman ρ for generalization gap prediction attributable to encoder architecture (NFT vs. flat-MLP) beyond what can be achieved through permutation augmentation or oracle canonicalization baseline; any observed differences lie within the paired bootstrap test margin (α=0.05, Holm-corrected, n=10,000).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Unterthiner FC-MLP zoo (standard) | Controlled comparison requires standardized zoo with known properties; MNIST + CIFAR-10 subsets |
| **Model** | NFT + flat-MLP encoder variants (6 levels) | NFT directly addresses FC-MLP permutation symmetry via equivariant attention |

**Dataset Details:**
- Source: Unterthiner et al. 2020
- Path: Standard zoo download (MNIST FC-MLP 2-4 layer; CIFAR-10 FC-MLP 2-4 layer)

**Model Details:**
- Type: Transformer-based weight encoder (NFT) + flat-MLP baseline
- Source: Zhou et al. 2023 (NFT); Unterthiner 2020 (flat-MLP baseline)

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Flat-MLP encoder | R²>0.98 (in-distribution) | Unterthiner MNIST zoo | Cannot handle permutation symmetry; Δρ > 0.10 under permutation stress |
| Permutation augmentation | Partial robustness | MNIST zoo | Engineering workaround, not architectural solution; ↓Δρ≈0.20 but still suboptimal |
| Oracle canonicalization | Upper bound | MNIST zoo | Theoretically underpowered due to neuron non-identifiability; serves as ceiling check |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Flat-MLP prediction ceiling R²>0.98 in-distribution | Established (BUILD_ON) | Comparison meaningless; revisit experimental design |
| A2 | NFT compatible with FC-MLP weight dimensions | Confirmed from NFT implementation | Must verify NFT cross-layer architecture before H-M4 |
| A3 | Zoo diversity sufficient (2-4 layer, MNIST/CIFAR) | Unterthiner zoo specs | Results may not generalize to wider architecture space |
| A4 | Pipeline shift partitionable (MNIST train → CIFAR test) | Zoo structure | Cross-pipeline transfer test fails; H-M4 scope reduced |
| A5 | Cross-layer attention architecture available in NFT | NFT paper architecture | H-M4 would need alternative cross-layer mechanism |

### 1.6 Research Gap & Novelty

**Gap confirmed (PROVE_NEW):** No controlled comparison of NFT vs. flat-MLP on Unterthiner FC-MLP zoo for generalization gap prediction exists in the literature.

**Differentiations:**
1. vs. Zhou 2023: NFT paper focuses on weight generation/editing, not gen-gap prediction robustness
2. vs. Unterthiner 2020: Used flat-MLP; did not address permutation symmetry as architectural problem
3. vs. Schürholt 2021: Focused on hypernetwork self-supervised learning, not equivariant encoders for property prediction

**Novelty:** First controlled experiment establishing whether architectural equivariance (NFT) is necessary vs. engineering convenience (augmentation/canonicalization) for FC-MLP zoo property prediction.

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

---

### 2.2 Hypothesis Specifications

#### H-E1: Permutation Sensitivity Differential Exists

**Type:** EXISTENCE
**Statement:** Under controlled conditions using the Unterthiner FC-MLP zoo (MNIST, 2-4 layer), flat-MLP encoders show significantly degraded Spearman ρ for generalization gap prediction under permutation stress (Δρ > 0.10), while NFT encoders maintain robustness (Δρ < 0.02), demonstrating that the permutation sensitivity differential is a real and measurable phenomenon requiring architectural solution.

**Variables:**
- IV: Encoder type (flat-MLP vs. NFT-base)
- DV: Δρ = ρ(original) - ρ(permuted) for generalization gap prediction
- CV: Zoo (Unterthiner MNIST), permutation severity s∈{0.25, 0.5, 1.0}, evaluation split

**Success Criteria:**
- flat-MLP Δρ > 0.10 at s=1.0 (permutation fully randomized)
- NFT-base Δρ < 0.02 at s=1.0
- Paired bootstrap test significant (p < 0.05, Holm-corrected)
- Minimum 500 models evaluated (full MNIST zoo or representative stratified sample)

**Gate:**
- Type: MUST_WORK
- If Fail: STOP entire pipeline → phenomenon does not exist → reassess main hypothesis H-NFT-GenGap-v1

**Prerequisites:** None

**Verification Protocol:**
1. Download Unterthiner MNIST FC-MLP zoo (full split)
2. Run alignment diagnostic (Step 0 in measurement plan): verify flat-MLP baseline R²>0.98
3. Train flat-MLP encoder on in-distribution split; record baseline Spearman ρ
4. Apply permutation stress at s∈{0.25, 0.5, 1.0}; record Δρ per level
5. Train NFT-base encoder (same split); repeat permutation stress test
6. Compute paired bootstrap (n=10,000), apply Holm correction
7. Compare Δρ(flat-MLP) vs. Δρ(NFT-base) at all severity levels
8. Gate decision: MUST_WORK → PASS if flat-MLP Δρ > 0.10 AND NFT Δρ < 0.02

---

#### H-M1: NFT Equivariant Attention Mediates Permutation Robustness

**Type:** MECHANISM
**Statement:** Under permutation stress (s=1.0), NFT encoders achieve significantly lower Δρ compared to flat-MLP because NFT's equivariant attention mechanism operates on neuron-level representations invariantly under permutation, as evidenced by the mechanism mediation analysis (ΔR² ≥ 0.10 when controlling for equivariance).

**Variables:**
- IV: Encoder architecture (flat-MLP vs. NFT variants: base, +aug, +canon, +aug+canon)
- DV: Δρ under permutation stress; mediation ΔR² attributable to equivariance
- CV: Zoo, permutation severity, evaluation split

**Success Criteria:**
- NFT-base Δρ < 0.02 vs. flat-MLP Δρ > 0.10 (reconfirm from H-E1)
- Mechanism mediation ΔR² ≥ 0.10 (NFT equivariance explains variance beyond augmentation)
- Ablation: flat-MLP+aug narrows but doesn't close gap; NFT-base without aug still robust

**Gate:**
- Type: MUST_WORK
- If Fail: STOP mechanism chain → flat-MLP+aug may suffice → document limitation, execute PIVOT to augmentation-focused design

**Prerequisites:** H-E1 (MUST_WORK passed)

**Verification Protocol:**
1. Run full 6-encoder comparison (flat-MLP, NFT-base, NFT+aug, NFT+canon, NFT+aug+canon, Oracle-canon)
2. Apply permutation stress at all severity levels; record Δρ per encoder
3. Compute mediation analysis: variance in Δρ explained by encoder type vs. augmentation
4. Ablation: NFT-base (no aug) vs. flat-MLP+aug — compare Δρ and R²
5. Verify ΔR² ≥ 0.10 for NFT equivariance contribution
6. Gate decision: MUST_WORK → PASS if mechanism confirmed

---

#### H-M2: Augmentation vs. Canonicalization Provide Partial But Insufficient Compensation

**Type:** MECHANISM
**Statement:** Permutation augmentation (flat-MLP+aug) and oracle canonicalization (flat-MLP+canon) reduce Δρ compared to flat-MLP baseline but do not match NFT-base performance, confirming that architectural equivariance provides a necessary (not merely convenient) inductive bias for permutation-robust property prediction.

**Variables:**
- IV: Compensation strategy (none vs. augmentation vs. canonicalization vs. NFT-base)
- DV: Δρ at s=1.0; R² for gen-gap prediction
- CV: Zoo, evaluation split

**Success Criteria:**
- flat-MLP+aug: Δρ reduced but > 0.05 (partial, not full compensation)
- flat-MLP+canon: Δρ reduced but > 0.03 (oracle ceiling still suboptimal)
- NFT-base: Δρ < 0.02 (architecture outperforms engineering fixes)
- Three-way ranking: NFT < canon < aug < flat-MLP in Δρ

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document that augmentation/canonicalization suffice → scope narrowed but H-M1 stands; narrow claim to "NFT is competitive with, not strictly superior to, oracle canon"

**Prerequisites:** H-M1

**Verification Protocol:**
1. Compare all 6 encoder variants on Δρ at s=1.0
2. Statistical test: flat-MLP+aug vs. NFT-base (paired bootstrap, p < 0.05)
3. Statistical test: oracle-canon vs. NFT-base (is NFT significantly better?)
4. Plot Δρ vs. permutation severity curve for all encoders
5. Gate decision: SHOULD_WORK → PASS if aug/canon < flat-MLP but > NFT-base

---

#### H-M3: NFT Maintains Calibrated Performance Across Permutation Severity Levels

**Type:** MECHANISM
**Statement:** NFT encoders maintain Spearman ρ > 0.85 across all permutation severity levels (s ∈ {0, 0.25, 0.5, 1.0}), demonstrating graceful degradation compared to flat-MLP's sharp performance cliff, confirming the robustness of equivariant attention for varying permutation intensities.

**Variables:**
- IV: Permutation severity s ∈ {0, 0.25, 0.5, 1.0}
- DV: Spearman ρ for gen-gap prediction; degradation slope
- CV: Encoder type (NFT-base vs. flat-MLP), zoo, evaluation split

**Success Criteria:**
- NFT-base: ρ > 0.85 at all severity levels
- flat-MLP: ρ drops below 0.75 at s ≥ 0.5
- Degradation slope: NFT slope < flat-MLP slope (graceful vs. cliff)
- Minimum 500 models per severity level

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document cliff only at high severity; scope claim to "NFT robustness under high-severity permutation" instead of full calibration

**Prerequisites:** H-M2

**Verification Protocol:**
1. Evaluate both encoders at s ∈ {0, 0.25, 0.5, 1.0}
2. Plot ρ vs. severity curve; compute degradation slopes
3. Bootstrap confidence intervals per severity level
4. Gate decision: SHOULD_WORK → PASS if NFT graceful degradation confirmed

---

#### H-M4: NFT Cross-Layer Attention Enables Cross-Pipeline Transfer

**Type:** MECHANISM
**Statement:** NFT encoders with cross-layer attention achieve cross-pipeline transfer gap Δ < 0.05 (MNIST→CIFAR zoo evaluation), whereas flat-MLP encoders show Δ > 0.10, confirming that cross-layer equivariant attention provides cross-pipeline robustness beyond single-layer mechanisms.

**Variables:**
- IV: Encoder type (flat-MLP vs. NFT-base vs. NFT with cross-layer attention)
- DV: Transfer gap Δ = |ρ(in-pipeline) - ρ(cross-pipeline)|
- CV: Zoo (MNIST zoo train, CIFAR zoo test), evaluation protocol

**Success Criteria:**
- NFT cross-layer: Δ < 0.05
- flat-MLP: Δ > 0.10
- Cross-pipeline test: train on MNIST zoo split, evaluate on CIFAR zoo split
- Minimum 200 models per pipeline for transfer evaluation

**Gate:**
- Type: SHOULD_WORK
- If Fail: Scope reduced to "NFT robustness within MNIST zoo only"; cross-pipeline claim dropped; still publishable as controlled permutation robustness result

**Prerequisites:** H-M3

**Verification Protocol:**
1. Confirm NFT cross-layer architecture available (A5 check)
2. Train all encoders on MNIST zoo (train split)
3. Evaluate on CIFAR zoo (test split); compute Δ for each encoder
4. Paired bootstrap test: NFT cross-layer vs. flat-MLP transfer gap
5. Gate decision: SHOULD_WORK → PASS if cross-pipeline transfer confirmed

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | flat-MLP Δρ>0.10 AND NFT Δρ<0.02 | STOP pipeline, reassess H-NFT-GenGap-v1 |
| H-M1 | MUST_WORK | ΔR²≥0.10 mechanism mediation confirmed | STOP mechanism chain, PIVOT to augmentation design |
| H-M2 | SHOULD_WORK | aug/canon < flat-MLP but > NFT-base in Δρ | Narrow claim: NFT competitive with oracle-canon |
| H-M3 | SHOULD_WORK | NFT ρ>0.85 at all severity levels | Narrow claim to high-severity robustness only |
| H-M4 | SHOULD_WORK | NFT Δ<0.05 cross-pipeline | Drop cross-pipeline claim; in-pipeline result sufficient |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (2+1+1+1) |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|-----------|
| R1 | NFT cross-layer architecture incompatible/unavailable | Medium | High (H-M4 blocked) | Pre-verify A5 before H-M4; fallback to standard NFT |
| R2 | Oracle canonicalization outperforms NFT (neuron non-identifiability) | Medium | Medium (H-M2 scope narrow) | Design as bound-check; not primary claim; three-way comparison still publishable |
| R3 | Flat-MLP Δρ < 0.10 (existence not demonstrated) | Low | Critical (H-E1 FAIL) | Pre-register thresholds; aligned ceiling check (A1) required first |
| R4 | Zoo sample size insufficient (<500) for bootstrap | Low | Medium (statistical power) | Use full Unterthiner MNIST zoo (>1,000 models available) |
| R5 | CIFAR zoo not accessible/partitionable for transfer test | Medium | Low (H-M4 only) | H-M4 SHOULD_WORK; failure narrows scope without invalidating main result |
| R6 | NFT training instability on weight-space inputs | Low | High (multiple hypotheses) | Pre-run NFT baseline sanity check; use established implementation |

### 4.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Gate Impact |
|------|--------------------|-----------|
| R1 | H-M4 | SHOULD_WORK only; non-blocking |
| R2 | H-M2 | SHOULD_WORK; scope narrowed |
| R3 | H-E1 | MUST_WORK FAIL → pipeline stop |
| R4 | H-E1, H-M1 | Statistical validity; mitigated by full zoo |
| R5 | H-M4 | SHOULD_WORK; non-blocking |
| R6 | H-M1, H-M2, H-M3, H-M4 | Mitigated by pre-run sanity check |

### 4.3 Mitigation Strategies

1. **Pre-experiment checklist** (before Phase 4 coding):
   - Verify flat-MLP baseline R²>0.98 (A1 ceiling check)
   - Confirm NFT cross-layer architecture from implementation (A5)
   - Verify CIFAR zoo partitionability (A4)

2. **Statistical safeguards:**
   - Pre-registered thresholds (no p-hacking)
   - Holm-corrected paired bootstrap (n=10,000)
   - Full zoo evaluation (≥500 models per condition)

3. **Scope management protocol:**
   - SHOULD_WORK failures → narrow claim, not terminate
   - MUST_WORK failures → terminate with documented failure context

### 4.4 Risk Summary

| Level | Count | Hypotheses at Risk |
|-------|-------|-------------------|
| Critical | 1 (R3) | H-E1 (MUST_WORK) |
| High | 1 (R1, R6) | H-M4, H-M1-4 |
| Medium | 2 (R2, R4) | H-M2, H-E1/H-M1 |
| Low | 1 (R5) | H-M4 |

**Overall Risk Level:** Medium (critical path protected by MUST_WORK gates; most risks are SHOULD_WORK scope-narrowing only)

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (EXISTENCE - no dependencies)
         │
         ▼ [Gate 1: MUST_WORK]
[Level 1 - Foundation Mechanism]
    H-M1 ← H-E1
         │
         ▼ [Gate 2: MUST_WORK]
[Level 2 - Compensation Analysis]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Severity Robustness]
    H-M3 ← H-M2
         │
         ▼
[Level 4 - Cross-Pipeline Transfer]
    H-M4 ← H-M3
         │
         ▼
[Terminal: Phase 5 Baseline Comparison]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Critical MUST_WORK: H-E1, H-M1
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type   |
|-------|-----------|---------------|-------------|
|   0   | H-E1      | None          | MUST_WORK   |
|   1   | H-M1      | H-E1          | MUST_WORK   |
|   2   | H-M2      | H-M1          | SHOULD_WORK |
|   3   | H-M3      | H-M2          | SHOULD_WORK |
|   4   | H-M4      | H-M3          | SHOULD_WORK |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │ W7
─────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │         │ ◆       │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  [Gate 2]       │         │         │ ◆       │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │         │ ████    │
  H-M4           │         │         │         │         │ ████
─────────────────┼─────────┼─────────┼─────────┼─────────┼────────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)

Slack Available: 0 weeks (all sequential)
MUST_WORK gates: 2 (H-E1, H-M1) — critical decision points

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (none required)

Verification Phases: 2
1. Foundation (H-E1)
2. Mechanisms (H-M1 to H-M4)

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) - Week 1-2
Step 2: Evaluate Gate 1 (MUST_WORK) → If PASS, proceed; If FAIL, STOP
Step 3: Execute H-M1 (Mechanism mediation) - Week 3-4
Step 4: Evaluate Gate 2 (MUST_WORK) → If PASS, proceed; If FAIL, PIVOT
Step 5: Execute H-M2 (Augmentation vs. canonicalization) - Week 5
Step 6: Execute H-M3 (Severity robustness) - Week 6
Step 7: Execute H-M4 (Cross-pipeline transfer) - Week 7
Final:  Verification complete → Phase 5 Baseline Comparison
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: NFT encoders provide necessary architectural
equivariance for permutation-robust FC-MLP zoo property
prediction, outperforming flat-MLP, augmentation, and
oracle canonicalization strategies.

Supporting Evidence:
1. NFT equivariance theorem proven for permutation symmetry
   (established fact, BUILD_ON)
2. DWSNets incompatibility with FC-MLP confirms need for
   alternative equivariant architecture (established fact)
3. Permutation augmentation ↓Δρ≈0.20 but insufficient
   (established partial evidence)

Strengths:
- Mathematically grounded: equivariance proven, not assumed
- Clean controlled experiment: 6-level IV comparison
- Three publishable outcomes regardless of direction
- Pre-registered thresholds; no p-hacking

Expected Outcomes:
- Primary: NFT Δρ < 0.02 vs. flat-MLP Δρ > 0.10
- Secondary: Transfer gap NFT Δ < 0.05 vs. flat-MLP Δ > 0.10
- Tertiary: Mediation ΔR² ≥ 0.10 for equivariance contribution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant difference in Spearman ρ
attributable to encoder architecture beyond augmentation/
canonicalization baseline (α=0.05, Holm-corrected).

Counter-Arguments:
1. Oracle canonicalization may theoretically match NFT since
   neuron non-identifiability means equivariance is only
   "theoretically sound" not "empirically necessary"
2. If flat-MLP Δρ < 0.10 (ceiling too high), existence
   claim fails → NFT benefit unmeasurable
3. NFT cross-layer architecture may not be available for
   FC-MLP (A5 violation) → H-M4 untestable

Potential Failure Points:
- R3: flat-MLP Δρ < 0.10 → H-E1 FAIL
- R2: Oracle-canon performance matches NFT → H-M2 scope narrow
- R1: NFT cross-layer unavailable → H-M4 untestable
- R6: NFT training instability on weight-space data

Conditions Under Which H0 Supported:
- If NFT Δρ ≥ 0.02 under permutation stress
- If oracle-canon achieves Δρ ≤ 0.02 as well
- If augmentation alone narrows gap to < 0.02
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

The thesis presents a well-grounded claim supported by
mathematical equivariance theory and prior work confirming
that flat-MLP encoders lack the inductive bias for
permutation-symmetric weight spaces. However, the antithesis
raises a legitimate challenge: oracle canonicalization may
achieve equivalent robustness despite neuron non-identifiability,
and the existence threshold (flat-MLP Δρ > 0.10) is the
single critical assumption that could falsify the entire chain.

Resolution Path:

1. H-E1 (Foundation): Pre-verify existence with alignment
   diagnostic; this is the critical gate. If flat-MLP
   Δρ < 0.10, the entire comparison is moot.
2. H-M1 (Mechanism): Mediation analysis distinguishes NFT
   equivariance from augmentation → directly addresses H0
3. H-M2 (Compensation): Three-way comparison (aug vs. canon
   vs. NFT) produces publishable result regardless of winner
4. Gates 1-2: Allow early detection of H0 support at minimal
   experimental cost before proceeding to cross-pipeline claims

Conditions for Thesis Support:
- H-E1 passes (flat-MLP Δρ > 0.10, NFT Δρ < 0.02)
- H-M1 passes (ΔR² ≥ 0.10 mechanism mediation)

Conditions for Antithesis Support:
- H-E1 fails (Δρ < 0.02 for flat-MLP; ceiling too high)
- Oracle-canon achieves same robustness as NFT-base

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1 + H-M2 all pass → Strong NFT advantage, publishable
2. Partial Support: H-E1/H-M1 pass, H-M2 narrow → NFT = oracle-canon; architectural necessity vs. engineering convenience debatable
3. No Support: H-E1 or H-M1 fail → Antithesis supported; document and route to Phase 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect       | Thesis Position          | Antithesis Challenge     | Resolution      |
|--------------|--------------------------|--------------------------|-----------------|
| Existence    | Δρ differential is real  | Ceiling too high         | H-E1 test       |
| Mechanism    | Equivariance mediates    | Aug/canon suffice        | H-M1/M2 tests   |
| Scope        | MNIST+CIFAR zoo applies  | Limited to in-distribution| H-M4 transfer  |
| Performance  | NFT outperforms all      | Oracle-canon competes    | Phase 5 final   |

Overall Robustness Score: Medium-High
Confidence in Verification Plan: 0.75

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** NFT encoders provide necessary equivariance for permutation-robust FC-MLP zoo gen-gap prediction
- ID: H-NFT-GenGap-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (80% scope reduction; 4/5 claims already established)
- Sub-Hypotheses: 5 total — H-E: 1, H-M: 4
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 MUST_WORK decision points (H-E1, H-M1)

**Risk Assessment:** Medium
- Primary concerns: Existence threshold (flat-MLP Δρ > 0.10) and NFT training stability

**Immediate Action:** Begin Phase 1 with H-E1 alignment diagnostic + permutation stress test

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases with clear sequential dependency
- H0 addressed via mediation analysis (ΔR² threshold) and three-way comparison
- Pre-registered thresholds protect against p-hacking
- Publishable at 3 levels: full support / NFT = oracle-canon / negative result

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Permutation sensitivity differential (flat-MLP Δρ > 0.10, NFT Δρ < 0.02)
- Gate 1: MUST PASS → existence confirmed before mechanism testing

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Equivariant attention mediation (ΔR² ≥ 0.10) — Week 3-4
- H-M2: Augmentation/canon vs. NFT comparison — Week 5
- H-M3: Severity robustness (graceful degradation) — Week 6
- H-M4: Cross-pipeline transfer (MNIST→CIFAR) — Week 7
- Gate 2: H-M1 MUST PASS → mechanism confirmed

**Critical Decision Points:**

1. **Gate 1 (Foundation H-E1):**
   - FAIL → STOP entire pipeline, reassess H-NFT-GenGap-v1
   - PASS → Proceed to Phase 2 (mechanism testing)

2. **Gate 2 (Mechanism H-M1):**
   - CRITICAL FAIL → PIVOT to augmentation-only design
   - OPTIONAL H-M2-4 FAIL → Narrow scope, document limitations

**Open Questions:**
- Does NFT cross-layer architecture work with FC-MLP weight dims? (A5 — verify before H-M4)
- Is oracle canonicalization practically achievable given neuron non-identifiability?
- Does prediction ceiling (flat-MLP R²>0.98) hold on CIFAR zoo?
- Can MNIST and CIFAR zoo splits be cleanly partitioned for transfer test?

**Recommendations:**

1. **Immediate Actions:**
   - Run alignment diagnostic FIRST (pre-verify flat-MLP baseline R²>0.98)
   - Confirm NFT cross-layer architecture from implementation repo
   - Set up measurement infrastructure with pre-registered thresholds

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path (all sequential)
   - Reserve buffer for NFT training instability debugging

3. **Failure Management:**
   - MUST_WORK fail → Document in Serena memory, route to Phase 0
   - SHOULD_WORK fail → Narrow claim, continue with documented scope

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-NFT-GenGap-v1)
- Round table convergence: 16 exchanges, all 6 criteria met
- Supplementary: 02_synthesis.yaml (measurement plan), final_opinions.yaml (agent perspectives)

**B. MCP Tool Usage Summary**
- Archon: Pipeline project verified, Phase 2B task activated
- ClearThought: Sequential thinking for hypothesis chain design and risk analysis
- Exa: Used in Phase 1 for literature verification (NFT architecture, Unterthiner zoo specs)

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-16*
