# Verification Plan: Memory Horizon Separation in SSM Adaptation

**Date:** 2026-03-27
**Hypothesis ID:** H-MHSH-EUH-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under SSM-based language models (Mamba architecture), if we apply parameter-efficient fine-tuning via projection-only LoRA, then task adaptation success depends on whether task information dependencies fall within the model's spectral memory horizon H_spec, because projection-only LoRA can redistribute state energy across existing eigenmodes (Eigenmode Utilization) but cannot extend the spectral horizon without modifying the discretization parameters that determine eigenvalue magnitudes (Spectral Surgery).

### 1.2 Alternative Hypothesis (H0)
There is no significant relationship between SSM spectral properties (eigenvalue magnitudes, eigenmode energy distribution) and the relative effectiveness of projection-only LoRA versus SSM-core adaptation across tasks with varying dependency lengths.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Multi-Query Associative Recall (MQAR) (synthetic) | Controllable dependency length L, prevents low-dimensional compression with N > state_dim |
| **Model** | Mamba-1.4B | Primary Mamba architecture with accessible eigenanalysis |

**Dataset Details:**
- Source: Custom generation following MQAR protocol
- Path: generated at runtime

**Model Details:**
- Type: SSM
- Source: state-spaces/mamba

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Projection-only LoRA | Competitive on short-context NLU (~95% of full fine-tuning) | Standard NLU benchmarks |
| SDT (Sparse Dimension Tuning) | Outperforms LoRA on SSM modules | Mixed benchmarks |
| State-offset Tuning | Empirically effective | Mixed benchmarks |
| Full Fine-tuning | Upper bound reference | All benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Local Jacobian ∂h_{t+1}/∂h_t stable across tokens (CV < 0.3) | Mamba A matrix is input-independent; only Δ varies | H_spec becomes distribution, separation boundary ill-defined |
| A2 | Eigenvalue clamping/scaling isolates memory effects without representational damage | A-matrix scaling preserves eigenvectors; rotation control validates | Surgical experiments confounded |
| A3 | MQAR with N > state_dim prevents low-dimensional compression | Multiple simultaneous associations require distributed state | EUH wins by construction via trivial 1D summary mode |
| A4 | H_spec scales predictably with model size | Depth/width should monotonically affect spectral properties | Results are checkpoint-specific, not structural principle |
| A5 | Pretrained Mamba can learn MQAR with fine-tuning on short contexts | h-m2 failure was due to lack of fine-tuning | Extrapolation test invalid if within-horizon not established |

### 1.6 Research Gap & Novelty

**Gap:** No prior work correlates SSM spectral properties with PEFT method selection. Existing work (SSM-PEFT, MambaPEFT) catalogs methods empirically without principled selection criteria.

**Novelty:** First principled framework connecting SSM spectral dynamics to PEFT method selection. Introduces H_spec = -1/log|λ_max| as measurable boundary. Provides mutually exclusive predictions for MHSH vs EUH mechanisms.

**Differentiation:**
- vs SSM-PEFT (ICML 2025): SSM-PEFT proposes SDT but doesn't explain WHY projection-only fails; we provide spectral theory
- vs MambaPEFT (ICLR 2025): MambaPEFT catalogs 20 methods but offers no selection criterion; we provide H_spec boundary
- vs State-offset Tuning (ACL 2025): Works empirically but lacks connection to spectral dynamics; we unify methods

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | Mechanism | MUST_WORK | H-M1 | BLOCKED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | BLOCKED |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---
#### H-E1: Spectral Horizon Measurability & Stability

**Statement**: Under pretrained Mamba-1.4B, if we compute the local Jacobian eigenvalues across random input sequences, then the spectral memory horizon H_spec = -1/log|λ_max| is stable with CV < 0.3, because the A matrix in Mamba is input-independent diagonal.

**Rationale**: This hypothesis validates that H_spec is a measurable model property, not a sequence-dependent artifact. Without stable H_spec, the entire MHSH/EUH framework collapses. This is the foundation for all subsequent mechanism hypotheses.

**Variables**:
- Independent: Input sequences (1000 random samples)
- Dependent: H_spec stability (CV metric)
- Controlled: Model checkpoint (Mamba-1.4B), sequence length, computation method

**Verification Protocol**:
1. Load pretrained Mamba-1.4B and compute Jacobian eigenvalues at multiple token positions using autograd hooks.
2. Calculate H_spec = -1/log|λ_max| for each of 1000 random sequences.
3. Compute CV = std(H_spec)/mean(H_spec) and verify CV < 0.3.
4. Cross-validate on Mamba-370M for scale consistency.

**Success Criteria** (PoC: Direction-based):
- Primary: CV(H_spec) < 0.3 across 1000 sequences
- Secondary: H_spec scales monotonically with model size

**Failure Response**:
- IF fails: PIVOT to input-conditioned H_spec distribution analysis

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1, Assumption A1

---
#### H-M1: SSM State Dynamics via Discretized Transition Matrix

**Statement**: Under Mamba architecture, if we analyze the state transition mechanism, then state dynamics are governed by Ā = exp(ΔA) where eigenvalues determine information decay rates, because A is a diagonal matrix discretized via the ZOH method.

**Rationale**: This validates the theoretical foundation that eigenvalues control memory. If state dynamics are not governed by eigenvalues as expected, the spectral horizon concept is invalid.

**Variables**:
- Independent: SSM layer index, token position
- Dependent: Eigenvalue distribution of Ā
- Controlled: Model architecture, discretization method

**Verification Protocol**:
1. Extract A matrix and Δ parameter from each Mamba layer.
2. Compute Ā = exp(ΔA) and analyze eigenvalue structure.
3. Verify eigenvalues are real and positive (diagonal A assumption).
4. Measure decay rates across layers.

**Success Criteria** (PoC: Direction-based):
- Primary: Eigenvalues match theoretical ZOH discretization
- Secondary: Decay rates interpretable as memory timescales

**Failure Response**:
- IF fails: EXPLORE alternative state dynamic formulations

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---
#### H-M2: Projection-Only LoRA Preserves Eigenvalues

**Statement**: Under MQAR fine-tuning with projection-only LoRA, if we apply LoRA to input/output projections only, then the spectral horizon H_spec remains unchanged (|ΔH_spec| < 10%), because projection-only LoRA does not modify the A, B, C, D core matrices.

**Rationale**: This tests whether projection-only LoRA truly isolates adaptation to I/O mappings without affecting spectral properties. This is crucial for distinguishing eigenmode utilization from spectral surgery.

**Variables**:
- Independent: Adaptation method (projection-only LoRA vs none)
- Dependent: ΔH_spec (percentage change in spectral horizon)
- Controlled: LoRA rank (r=16), training protocol, parameter count

**Verification Protocol**:
1. Measure baseline H_spec on pretrained Mamba-1.4B.
2. Apply projection-only LoRA (rank 16) and fine-tune on MQAR at L = H_spec.
3. Re-measure H_spec after adaptation.
4. Calculate |ΔH_spec| and verify < 10%.
5. Repeat for 5 random seeds.

**Success Criteria** (PoC: Direction-based):
- Primary: |ΔH_spec| < 10% after projection-only LoRA
- Secondary: Eigenvalue distribution visually unchanged

**Failure Response**:
- IF fails: EXPLORE whether projection-only indirectly affects eigenvalues

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2

---
#### H-M3: Eigenmode Energy Redistribution Under Projection-Only LoRA

**Statement**: Under projection-only LoRA adaptation, if slow eigenmodes exist in pretrained models, then LoRA can redistribute state energy toward these modes (ΔE > 0.1 nats), because input reweighting preferentially excites slow modes without changing eigenvalues.

**Rationale**: This tests the Eigenmode Utilization Hypothesis (EUH) - whether projection-only LoRA succeeds by utilizing latent slow-mode capacity rather than extending the horizon.

**Variables**:
- Independent: Adaptation method (projection-only LoRA)
- Dependent: Modal energy redistribution ΔE (KL divergence in nats)
- Controlled: Parameter count, training protocol, MQAR task

**Verification Protocol**:
1. Compute eigenmode energy distribution p(i) before adaptation.
2. Apply projection-only LoRA and fine-tune on MQAR.
3. Re-compute eigenmode energy distribution p'(i) after adaptation.
4. Calculate ΔE = KL(p' || p) in nats.
5. If ΔE > 0.1 with task success, EUH mechanism confirmed.

**Success Criteria** (PoC: Direction-based):
- Primary: ΔE > 0.1 nats if projection-only succeeds on extended L
- Secondary: Energy shifts toward slow modes (low eigenvalue indices)

**Failure Response**:
- IF fails with ΔE ≈ 0: PIVOT to MHSH (spectral surgery required)

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3

---
#### H-M4: Beyond-Horizon Task Discrimination (MHSH vs EUH)

**Statement**: Under MQAR with L = 4×H_spec, if projection-only LoRA is applied, then either (a) it fails (accuracy < 50%) with ΔH_spec < 10% (MHSH), or (b) it succeeds (accuracy > 70%) with ΔE > 0.1 nats (EUH), because beyond-horizon success requires either spectral surgery or eigenmode utilization.

**Rationale**: This is the critical discriminator between MHSH and EUH. The outcome determines whether projection-only LoRA has fundamental memory limitations or can leverage latent capacity.

**Variables**:
- Independent: Task dependency length L = {H_spec, 2H, 4H, 8H}, Adaptation method
- Dependent: MQAR accuracy, ΔH_spec, ΔE
- Controlled: Parameter count matched, same training protocol, N > state_dim

**Verification Protocol**:
1. Establish within-horizon capability: fine-tune at L = H_spec, verify accuracy > 90%.
2. Apply adaptation methods and evaluate extrapolation at L = {2H, 4H, 8H}.
3. For each condition, measure accuracy, ΔH_spec, and ΔE.
4. Classify outcome: MHSH (fail + Δλ ≈ 0) vs EUH (success + ΔE > 0.1).
5. Surgical A-matrix scaling experiment as definitive test.

**Success Criteria** (PoC: Direction-based):
- Primary: Clear separation between MHSH and EUH signatures
- Secondary: SSM-core LoRA extends H_spec > 50% when successful at L = 4H

**Failure Response**:
- IF both Δλ ≈ 0 AND ΔE ≈ 0 with success: EXPLORE third mechanism

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Predictions P2, P3

---

## 3. Risk Analysis

### 3.1 Identified Risks

**R1: Jacobian Instability (Source: A1)**
- **Description**: If CV(H_spec) ≥ 0.3 across sequences, the spectral horizon becomes a distribution rather than a stable model property, invalidating the MHSH/EUH framework.
- **Severity**: Critical
- **Likelihood**: Medium (Mamba A is input-independent, but Δ varies)
- **Impact**: H-E1, H-M1, H-M2, H-M3, H-M4 (entire framework)

**R2: Surgical Experiment Confounding (Source: A2)**
- **Description**: If eigenvalue clamping/scaling damages representational capacity beyond memory effects, surgical A-matrix experiments cannot isolate the memory mechanism.
- **Severity**: High
- **Likelihood**: Low (eigenvector-rotation control validates isolation)
- **Impact**: H-M3, H-M4 (mechanism discrimination)

**R3: Low-Dimensional Compression Loophole (Source: A3)**
- **Description**: If MQAR allows trivial 1D summary mode with N ≤ state_dim, EUH appears validated by construction rather than through genuine eigenmode utilization.
- **Severity**: High
- **Likelihood**: Low (controllable via N > state_dim design)
- **Impact**: H-M3, H-M4 (EUH validation)

**R4: Checkpoint-Specific Results (Source: A4)**
- **Description**: If H_spec does not scale monotonically with model size, results apply only to tested checkpoints rather than representing a structural principle.
- **Severity**: Medium
- **Likelihood**: Medium (requires cross-scale validation)
- **Impact**: Generalization claims, H-E1 cross-validation

**R5: Within-Horizon Capability Failure (Source: A5)**
- **Description**: If pretrained Mamba cannot learn MQAR even at L = H_spec with fine-tuning, the extrapolation test is invalid and the entire experimental paradigm fails.
- **Severity**: Critical
- **Likelihood**: Low (h-m2 failure was due to lack of fine-tuning)
- **Impact**: All hypotheses (experimental validity)

### 3.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Gate Impact |
|------|--------|---------------------|----------|-------------|
| R1 | A1 | H-E1, H-M1, H-M2, H-M3, H-M4 | Critical | Blocks all if H-E1 fails |
| R2 | A2 | H-M3, H-M4 | High | Confounds mechanism discrimination |
| R3 | A3 | H-M3, H-M4 | High | False positive for EUH |
| R4 | A4 | H-E1 (cross-validation) | Medium | Limits generalization claims |
| R5 | A5 | All (experimental validity) | Critical | Invalidates entire paradigm |

**Critical Path Risks**: R1 and R5 must be resolved before main experiments proceed.

### 3.3 Mitigation Strategies

**R1 Mitigation: Jacobian Instability**
- **Prevention**: Phase 0 characterization - validate CV < 0.3 across 1000 sequences before main experiments
- **Detection**: Monitor CV during H-E1; alert if approaching 0.25
- **Response**:
  - PIVOT: Analyze H_spec as distribution with quantiles rather than point estimate
  - SCOPE: Focus on sequences where H_spec is stable (filter outliers)
  - ABORT: If CV > 0.5, framework fundamentally inapplicable
- **Early Warning**: CV > 0.2 in initial 100 sequences

**R2 Mitigation: Surgical Experiment Confounding**
- **Prevention**: Include eigenvector-rotation control experiments (rotate eigenvectors without changing eigenvalues)
- **Detection**: Compare rotation-control accuracy with eigenvalue-scaling accuracy
- **Response**:
  - PIVOT: Use gradient-based attribution instead of surgical experiments
  - SCOPE: Report surgical results as supplementary, not primary evidence
  - ABORT: If rotation control shows >20% accuracy drop
- **Early Warning**: Rotation control accuracy differs significantly from baseline

**R3 Mitigation: Low-Dimensional Compression**
- **Prevention**: Design MQAR with N > state_dim (e.g., N = 2× state_dim)
- **Detection**: Analyze state rank during MQAR; verify rank > 1
- **Response**:
  - PIVOT: Increase N until compression prevented
  - SCOPE: Report results conditional on compression analysis
  - ABORT: If state rank analysis fails
- **Early Warning**: Effective state rank < N/2 during MQAR

**R4 Mitigation: Checkpoint-Specific Results**
- **Prevention**: Validate on minimum 2 model sizes (Mamba-1.4B + Mamba-370M)
- **Detection**: Check H_spec scales monotonically: H_spec(1.4B) > H_spec(370M)
- **Response**:
  - PIVOT: Report as checkpoint-specific finding with caveats
  - SCOPE: Focus on architectural insights rather than universal claims
  - ABORT: N/A (reduces claim scope, doesn't invalidate)
- **Early Warning**: H_spec(370M) ≈ H_spec(1.4B) despite 4x size difference

**R5 Mitigation: Within-Horizon Capability Failure**
- **Prevention**: Fine-tune on MQAR at L = H_spec before extrapolation; verify >90% accuracy
- **Detection**: Monitor training loss; alert if not converging
- **Response**:
  - PIVOT: Use simpler associative recall task (single-query instead of multi-query)
  - SCOPE: Reduce N to simplify task
  - ABORT: If no task achieves >70% accuracy after fine-tuning
- **Early Warning**: Training accuracy < 50% after 5 epochs

### 3.4 Risk Summary

| ID | Risk | Source | Severity | Affected | Primary Mitigation |
|----|------|--------|----------|----------|-------------------|
| R1 | Jacobian Instability | A1 | Critical | All | Phase 0 characterization (CV < 0.3) |
| R2 | Surgical Confounding | A2 | High | H-M3, H-M4 | Eigenvector-rotation control |
| R3 | Compression Loophole | A3 | High | H-M3, H-M4 | MQAR with N > state_dim |
| R4 | Checkpoint-Specific | A4 | Medium | Generalization | Cross-scale validation (2+ sizes) |
| R5 | Within-Horizon Failure | A5 | Critical | All | Fine-tune at L=H_spec first |

**Risk Distribution:**
- Critical: 2 (R1, R5)
- High: 2 (R2, R3)
- Medium: 1 (R4)
- Low: 0

**Execution Dependency**: R1 and R5 must be resolved in H-E1 before proceeding to H-M experiments.

---

## 4. Execution Plan

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
           DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════════════

[Level 0 - Foundation]
                    ┌─────────────────────────────────────┐
                    │  H-E1: Spectral Horizon Existence   │
                    │  Gate: MUST_WORK                    │
                    │  Prerequisites: None                │
                    └─────────────────────────────────────┘
                                     │
                                     ▼
[Level 1 - Mechanism Chain Start]
                    ┌─────────────────────────────────────┐
                    │  H-M1: SSM State Dynamics           │
                    │  Gate: MUST_WORK                    │
                    │  Prerequisites: H-E1                │
                    └─────────────────────────────────────┘
                                     │
                                     ▼
[Level 2 - Eigenvalue Preservation]
                    ┌─────────────────────────────────────┐
                    │  H-M2: Projection-Only Preserves λ  │
                    │  Gate: MUST_WORK                    │
                    │  Prerequisites: H-M1                │
                    └─────────────────────────────────────┘
                                     │
                                     ▼
[Level 3 - Energy Redistribution]
                    ┌─────────────────────────────────────┐
                    │  H-M3: Eigenmode Energy (ΔE)        │
                    │  Gate: SHOULD_WORK                  │
                    │  Prerequisites: H-M2                │
                    └─────────────────────────────────────┘
                                     │
                                     ▼
[Level 4 - Mechanism Discrimination]
                    ┌─────────────────────────────────────┐
                    │  H-M4: MHSH vs EUH Discrimination   │
                    │  Gate: SHOULD_WORK                  │
                    │  Prerequisites: H-M3                │
                    └─────────────────────────────────────┘
                                     │
                                     ▼
                           ┌─────────────┐
                           │  COMPLETE   │
                           │  → Phase 5  │
                           └─────────────┘

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Levels: 5 (0-4)
Parallelization: None (strict sequential dependency)
═══════════════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Title | Prerequisites | Gate Type | Fail Action |
|-------|------------|-------|---------------|-----------|-------------|
| 0 | H-E1 | Spectral Horizon Measurability | None | MUST_WORK | STOP pipeline |
| 1 | H-M1 | SSM State Dynamics | H-E1 | MUST_WORK | STOP pipeline |
| 2 | H-M2 | Eigenvalue Preservation | H-M1 | MUST_WORK | STOP pipeline |
| 3 | H-M3 | Eigenmode Energy Redistribution | H-M2 | SHOULD_WORK | Document limitation |
| 4 | H-M4 | MHSH vs EUH Discrimination | H-M3 | SHOULD_WORK | Document limitation |

**Verification Phases:**

**Phase 1 - Foundation (H-E1)**
- Validates that H_spec is measurable and stable
- Gate: MUST pass with CV < 0.3
- If fails: Entire framework invalid, reassess hypothesis

**Phase 2 - Core Mechanisms (H-M1, H-M2)**
- Validates eigenvalue-based state dynamics and LoRA preservation
- Gate: Both MUST pass
- If fails: Spectral theory doesn't apply to Mamba as hypothesized

**Phase 3 - Discrimination (H-M3, H-M4)**
- Tests competing MHSH vs EUH mechanisms
- Gate: SHOULD pass (either mechanism valid)
- If both fail: Third unknown mechanism exists

### 4.3 Gate Summary

| Gate | Hypothesis | Type | Pass Condition | Fail Action |
|------|------------|------|----------------|-------------|
| G1 | H-E1 | MUST_WORK | CV(H_spec) < 0.3 | STOP: Reassess framework |
| G2 | H-M1 | MUST_WORK | Eigenvalues match ZOH theory | STOP: Spectral theory invalid |
| G3 | H-M2 | MUST_WORK | |ΔH_spec| < 10% | STOP: Projection-only modifies spectrum |
| G4 | H-M3 | SHOULD_WORK | ΔE > 0.1 nats if successful | PIVOT to MHSH |
| G5 | H-M4 | SHOULD_WORK | Clear MHSH or EUH signature | EXPLORE third mechanism |

**Gate Logic:**
- MUST_WORK gates (G1-G3): Pipeline stops if any fails
- SHOULD_WORK gates (G4-G5): Document limitation and pivot if fails

### 4.4 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════════════════
               VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2     │ W3-4     │ W5       │ W6       │ W7       │
────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation │          │          │          │          │          │
  H-E1 (Spectral)   │ ████████ │          │          │          │          │
  [Gate G1]         │        ◆ │          │          │          │          │
────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Core       │          │          │          │          │          │
  H-M1 (Dynamics)   │          │ ████████ │          │          │          │
  [Gate G2]         │          │        ◆ │          │          │          │
  H-M2 (Preserves)  │          │          │ ████     │          │          │
  [Gate G3]         │          │          │    ◆     │          │          │
────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 3: Discrim.   │          │          │          │          │          │
  H-M3 (Energy)     │          │          │          │ ████     │          │
  [Gate G4]         │          │          │          │    ◆     │          │
  H-M4 (MHSH/EUH)   │          │          │          │          │ ████     │
  [Gate G5]         │          │          │          │          │    ◆     │
────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
                    │          │          │          │          │ COMPLETE │
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════════════════
```

### 4.5 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

| Hypothesis | Duration | Cumulative | Gate |
|------------|----------|------------|------|
| H-E1 | 2 weeks | Week 2 | G1 (MUST_WORK) |
| H-M1 | 2 weeks | Week 4 | G2 (MUST_WORK) |
| H-M2 | 1 week | Week 5 | G3 (MUST_WORK) |
| H-M3 | 1 week | Week 6 | G4 (SHOULD_WORK) |
| H-M4 | 1 week | Week 7 | G5 (SHOULD_WORK) |

**Total Duration:** 7 weeks
**Slack Available:** 0 weeks (all sequential, no parallelization)
**MUST_WORK Gates:** 3 (G1, G2, G3) - pipeline stops if any fails
**SHOULD_WORK Gates:** 2 (G4, G5) - document limitation and pivot

### 4.6 Resource Summary

**Hypothesis Distribution:**
- Total Hypotheses: 5
- Existence (H-E): 1 (H-E1)
- Mechanism (H-M): 4 (H-M1 to H-M4)
- Condition (H-C): 0 (not required)

**Verification Phases:** 3
1. Foundation (H-E1) - Spectral horizon validation
2. Core Mechanisms (H-M1, H-M2) - Eigenvalue preservation
3. Discrimination (H-M3, H-M4) - MHSH vs EUH

**Compute Requirements:**
- GPU: Single GPU (Mamba-1.4B fits in 24GB VRAM)
- Eigenanalysis: PyTorch autograd hooks
- Training: AdamW, ~5 epochs per hypothesis
- Evaluation: MQAR at L = {H_spec, 2H, 4H, 8H}

**Timeline Summary:**
- Total Duration: 7 weeks
- Critical Path Length: 7 weeks
- Execution Mode: Sequential (no parallelization)
- Early Termination: If G1, G2, or G3 fails

### 4.7 Execution Order

**Step-by-Step Execution Protocol:**

| Step | Action | Duration | Gate | Fail Action |
|------|--------|----------|------|-------------|
| 1 | Execute H-E1 (Jacobian stability, H_spec measurement) | Week 1-2 | G1 | STOP |
| 2 | Evaluate G1: CV(H_spec) < 0.3? | End Week 2 | - | Reassess framework |
| 3 | Execute H-M1 (Eigenvalue dynamics verification) | Week 3-4 | G2 | STOP |
| 4 | Evaluate G2: Eigenvalues match ZOH theory? | End Week 4 | - | Spectral theory invalid |
| 5 | Execute H-M2 (Projection-only LoRA eigenvalue test) | Week 5 | G3 | STOP |
| 6 | Evaluate G3: |ΔH_spec| < 10%? | End Week 5 | - | Projection modifies spectrum |
| 7 | Execute H-M3 (Modal energy redistribution) | Week 6 | G4 | PIVOT |
| 8 | Evaluate G4: ΔE > 0.1 if successful? | End Week 6 | - | Document EUH limitation |
| 9 | Execute H-M4 (MHSH vs EUH discrimination) | Week 7 | G5 | EXPLORE |
| 10 | Evaluate G5: Clear mechanism signature? | End Week 7 | - | Third mechanism exists |
| 11 | **COMPLETE**: Proceed to Phase 5 Baseline Comparison | - | - | - |

**Decision Points:**
- After G3 (Week 5): If all MUST_WORK gates pass, hypothesis framework validated
- After G5 (Week 7): Mechanism (MHSH or EUH) determined, ready for baseline comparison

---

## 5. Dialectical Analysis

### 5.1 Overview

This section presents a formal dialectical evaluation of the hypothesis using Thesis-Antithesis-Synthesis structure. The null hypothesis (H0) from Phase 2A serves as the antithesis, ensuring balanced consideration of opposing viewpoints.

**Dialectical Structure:**
- **Thesis**: MHSH/EUH framework (spectral dynamics govern adaptation)
- **Antithesis**: H0 (no spectral-adaptation relationship)
- **Synthesis**: Verification plan fairly adjudicates between positions

**MCP Analysis**: ClearThought Structured Argumentation used for formal dialectical reasoning.

### 5.2 Thesis

**Core Claim:** SSM adaptation success depends on spectral memory horizon H_spec: projection-only LoRA succeeds within H_spec via eigenmode utilization but fails beyond H_spec without spectral surgery.

**Supporting Premises:**
1. SSM state dynamics are governed by discretized transition matrix Ā = exp(ΔA) with eigenvalues determining decay rates
2. Projection-only LoRA modifies input/output mappings but does not change Ā eigenvalues, preserving H_spec
3. Projection-only LoRA can redistribute state energy toward slow eigenmodes (Eigenmode Utilization)
4. Tasks beyond H_spec require either eigenmode utilization of latent slow modes OR spectral surgery via SSM-core adaptation
5. H_spec = -1/log|λ_max| provides a principled, measurable boundary for adaptation strategy selection

**Strengths:**
- Novel theoretical framework connecting spectral dynamics to PEFT method selection
- Pre-registered quantitative thresholds prevent post-hoc interpretation
- Builds on established SSM theory (Mamba paper)
- Clear experimental design with surgical A-matrix scaling control

**Weaknesses:**
- Jacobian stability assumption (CV < 0.3) must be validated empirically
- MQAR is synthetic - generalization to natural language uncertain
- Eigenanalysis requires linearization which may miss nonlinear effects

**Confidence:** 0.80

### 5.3 Antithesis

**Null Hypothesis (H0):** There is no significant relationship between SSM spectral properties and PEFT method effectiveness - projection-only and SSM-core LoRA perform equivalently regardless of task temporal structure.

**Counter-Arguments:**
1. Projection-only LoRA achieves ~95% of full fine-tuning on short-context tasks (MambaPEFT) without spectral considerations
2. Prior work shows LoRA effective across architectures without spectral theory
3. Eigenvalue-based memory theory may not capture the full complexity of learned representations
4. Task success may depend more on representation quality than memory horizon
5. Cross-architecture comparison failures (h-m2) suggest task capability is training-dependent, not architecture-dependent

**Potential Failure Points (from Risk Analysis):**
- R1: Jacobian instability (CV ≥ 0.3) makes H_spec ill-defined
- R5: Pretrained Mamba cannot learn MQAR even with fine-tuning
- Both Δλ ≈ 0 AND ΔE ≈ 0 with beyond-horizon success

**Conditions Under Which H0 Would Be Supported:**
- H-E1 fails: Spectral horizon is not stable/measurable
- H-M1 fails: Eigenvalue dynamics don't match ZOH theory
- H-M4 shows success without either MHSH or EUH signatures

**Confidence in H0:** 0.40 (lower than thesis due to lack of mechanistic explanation)

### 5.4 Synthesis

**Balanced Assessment:**

The hypothesis H-MHSH-EUH-v1 presents a novel, testable claim that SSM spectral dynamics determine PEFT method effectiveness. However, the null hypothesis raises valid concerns: the relationship may be epiphenomenal rather than causal, and empirical LoRA success across architectures suggests simpler explanations may suffice.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes H_spec is measurable and stable before testing mechanism - directly addresses H0's concern about epiphenomenal signatures
2. **Sequential mechanism testing (H-M1-M4):** Tests causal chain step-by-step with falsifiable predictions
3. **Pre-registered thresholds:** Quantitative criteria (CV < 0.3, |ΔH_spec| < 10%, ΔE > 0.1) prevent post-hoc interpretation
4. **Gate conditions:** MUST_WORK gates allow early termination if H0 gains support

**Conditions for Thesis Support:**
- All MUST_WORK gates (G1-G3) pass
- Clear MHSH signature (fail at L=4H with Δλ ≈ 0) OR clear EUH signature (success at L=4H with ΔE > 0.1)
- Mechanism chain validates with expected spectral signatures

**Conditions for Antithesis Support:**
- H-E1 fails: CV(H_spec) ≥ 0.3 (spectral horizon unstable)
- H-M1 fails: Eigenvalues don't match ZOH discretization theory
- H-M4: Beyond-horizon success with BOTH Δλ ≈ 0 AND ΔE ≈ 0

**Nuanced Outcome Possibilities:**
| Outcome | Gates | Implication |
|---------|-------|-------------|
| Full Thesis Support | All pass, clear MHSH or EUH | Spectral framework validated |
| Partial Support | G1-G3 pass, G4-G5 mixed | Framework valid, mechanism unclear |
| Antithesis Support | G1 or G2 fails | Spectral theory doesn't apply |
| Third Mechanism | G1-G3 pass, neither MHSH nor EUH | Unknown mechanism, explore further |

**Confidence in Synthesis:** 0.85

### 5.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | H_spec is measurable and stable (CV < 0.3) | May be sequence-dependent artifact | H-E1 validates with 1000 sequences |
| Mechanism | Eigenvalue dynamics govern memory | Alternative explanations possible | H-M1-M2 test ZOH theory |
| Adaptation | MHSH or EUH explains beyond-horizon | Training dynamics dominate | H-M3-M4 discriminate mechanisms |
| Scope | Applies to Mamba family | Limited to tested checkpoints | Cross-scale validation (370M, 1.4B) |
| Performance | Spectral theory predicts outcomes | Marginal practical improvement | Phase 5 baseline comparison |

**Robustness Indicators:**

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Pre-registered falsification | ✓ Strong | Quantitative thresholds defined before experiments |
| Multiple lines of evidence | ✓ Strong | Eigenvalue (Δλ), energy (ΔE), accuracy metrics |
| Control experiments | ✓ Strong | Eigenvector-rotation control for surgical experiments |
| Cross-validation | ○ Moderate | 2 model sizes (limited by checkpoint availability) |
| External validity | △ Weak | MQAR synthetic, NL generalization exploratory |

**Overall Robustness Score:** HIGH

**Confidence in Verification Plan:** 0.80

**Key Strengths:**
- Mutually exclusive predictions prevent unfalsifiable outcomes
- Sequential gate structure catches failures early
- Either thesis or antithesis support advances the field

**Key Limitations:**
- MQAR-to-natural-language generalization requires follow-up
- Cross-architecture validation limited to Mamba family
- 7-week timeline assumes no major experimental setbacks

---

## 6. Summary & Conclusions

### 6.1 Executive Summary

**Main Hypothesis:** Memory Horizon Separation in SSM Adaptation (MHSH/EUH)
- ID: H-MHSH-EUH-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 3 phases over 7 weeks
- Critical Gates: 5 decision points (3 MUST_WORK, 2 SHOULD_WORK)

**Risk Assessment:** Medium-High
- Primary concerns: R1 (Jacobian instability), R5 (within-horizon capability)
- Mitigation: Phase 0 characterization before main experiments

**Key Discriminator:** Either MHSH (Δλ-based) or EUH (ΔE-based) mechanism validated

**Immediate Action:** Begin Phase 1 with H-E1 (Spectral Horizon Measurability)

### 6.2 Final Summary

**Key Achievements:**
- 5 hypotheses across 3 verification phases
- H0 addressed: Null hypothesis (no spectral-adaptation relationship) used as antithesis
- Pre-registered falsification criteria prevent confirmation bias
- Either outcome (thesis or antithesis supported) advances the field

**Verification Execution Order:**

| Phase | Hypotheses | Duration | Gate |
|-------|------------|----------|------|
| 1: Foundation | H-E1 (Spectral horizon stability) | Week 1-2 | G1: MUST_WORK |
| 2: Core | H-M1 (State dynamics), H-M2 (Eigenvalue preservation) | Week 3-5 | G2-G3: MUST_WORK |
| 3: Discrimination | H-M3 (Energy redistribution), H-M4 (MHSH vs EUH) | Week 6-7 | G4-G5: SHOULD_WORK |

**Critical Decision Points:**
1. **Gate G1 (Week 2):** H-E1 must pass (CV < 0.3)
   - FAIL → STOP, spectral framework invalid
   - PASS → Proceed to core mechanism tests
2. **Gate G3 (Week 5):** H-M2 must pass (|ΔH_spec| < 10%)
   - FAIL → STOP, projection-only modifies spectrum
   - PASS → Proceed to mechanism discrimination
3. **Gate G5 (Week 7):** H-M4 determines mechanism
   - MHSH: Projection-only fails at L=4H with Δλ ≈ 0
   - EUH: Projection-only succeeds at L=4H with ΔE > 0.1

### 6.3 Conclusions

**Open Questions (from Phase 2A):**
- Exact CV threshold for Jacobian stability (currently using 0.3)
- Generalization from MQAR to natural language tasks
- Cross-architecture applicability (RWKV, Mamba-2)

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (Jacobian stability validation)
   - Set up eigenanalysis infrastructure (PyTorch autograd hooks)
   - Generate MQAR dataset with N > state_dim

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path (no parallelization)
   - Reserve 2 weeks buffer for experimental setbacks
   - Single GPU sufficient (Mamba-1.4B fits in 24GB VRAM)

3. **Failure Management:**
   - Document all gate failures with quantitative evidence
   - Execute PIVOT strategies from mitigation plan (Section 3.3)
   - If G1 fails: Consider H_spec as distribution rather than point estimate

### 6.4 Appendices

**A. Phase 2A Reference**
- Source: `03_refinement.yaml` (ID: H-MHSH-EUH-v1)
- Schema: v10.0.0 Free-Parse
- Scope Reduction: 60% (3 BUILD_ON, 2 PROVE_NEW claims)

**B. MCP Tool Usage Summary**
- Total MCP calls: 9
- ClearThought scientificmethod: 6 calls (H-E1, H-M1-M2, H-M3-M4)
- ClearThought structuredargumentation: 3 calls (Thesis, Antithesis, Synthesis)

**C. Hypothesis Quick Reference**
| ID | Type | Gate | Key Metric |
|----|------|------|------------|
| H-E1 | Existence | MUST_WORK | CV(H_spec) < 0.3 |
| H-M1 | Mechanism | MUST_WORK | Eigenvalues match ZOH |
| H-M2 | Mechanism | MUST_WORK | |ΔH_spec| < 10% |
| H-M3 | Mechanism | SHOULD_WORK | ΔE > 0.1 nats |
| H-M4 | Mechanism | SHOULD_WORK | MHSH or EUH signature |

---

## 7. State & Task Management

### 7.1 Verification State

**File Generated:** `verification_state.yaml`
**Schema Version:** 3.5
**Status:** ACTIVE

| Field | Value |
|-------|-------|
| Main Hypothesis ID | H-MHSH-EUH-v1 |
| Sub-Hypotheses | 5 (H-E1, H-M1, H-M2, H-M3, H-M4) |
| Current Phase | Phase 2B → Phase 2C |
| Execution Mode | UNATTENDED |
| Next Action | Begin Phase 2C with H-E1 (READY) |

### 7.2 Pipeline Tasks

**Pipeline Project:** Anonymous Pipeline: Efficient SSM Adaptation via LoRA
**Project ID:** `20fa5b63-14c8-4a7f-98b7-50bcf4ad1a53`

| Task | Status | Action |
|------|--------|--------|
| Phase 2A-Dialogue | done | Completed |
| Phase 2B - Planning | done | Completed (this workflow) |
| Phase 2C - Experiment | doing | Ready to start |

### 7.3 Hypothesis Tasks

**Created in Archon:** 5 hypothesis tasks

| Hypothesis | Task ID | Status | Gate |
|------------|---------|--------|------|
| H-E1 | `db1d4332-69b1-4293-8867-99c046dcb491` | todo | MUST_WORK |
| H-M1 | `7b286f28-037f-4815-b4f8-a683ef2dabaf` | todo | MUST_WORK |
| H-M2 | `c7ef8be0-f2c1-4dc2-add3-a0b44a833d84` | todo | MUST_WORK |
| H-M3 | `b80a1e01-22ad-4dbd-a9ee-4b02183c294a` | todo | SHOULD_WORK |
| H-M4 | `075ce717-35a6-4e7e-894e-4c6e37381396` | todo | SHOULD_WORK |

**Task Mapping:** Stored in `verification_state.yaml` under `metadata.hypothesis_task_mapping`

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-27*
