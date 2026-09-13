# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-27T19:50:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: GAP-001
- **Gap Title**: LoRA Cannot Directly Adapt SSM-Specific Modules (A, B, C, D / Time-Mixing)
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Transformed MHSH vs EUH debate into falsifiable framework with horizon-based metrics (ΔH_spec), variance-controlled Jacobian analysis, and distributed-memory task design that cleanly separates mechanisms.

### Key Insights

1. **Spectral Horizon as Boundary**: The memory horizon H_spec = -1/log|λ_max| provides a principled, threshold-free boundary for determining when projection-only LoRA is sufficient vs when SSM-core adaptation is required.

2. **Two Competing Mechanisms**: The discussion crystallized two mutually exclusive hypotheses:
   - **MHSH (Memory Horizon Separation)**: Projection-only LoRA cannot extend H_spec; spectral surgery required for beyond-horizon tasks
   - **EUH (Eigenmode Utilization)**: Projection-only LoRA redistributes state energy toward slow eigenmodes without changing eigenvalues

3. **Measurable Signatures**: Δλ (eigenvalue shift) and ΔE (modal energy KL divergence) provide clean discrimination between mechanisms.

### Breakthrough Moments

- **Exchange 11**: Dr. Nova's Lottery Ticket analogy — slow eigenmodes as "latent capacity" underutilized by pretrained projections
- **Exchange 12**: Prof. Vera's formalization of Δλ vs ΔE with mutually exclusive predictions
- **Exchange 14**: Prof. Rex's challenge leading to horizon-based (not eigenvalue-based) significance thresholds
- **Exchange 15**: Prof. Pax's feasibility assessment confirming all experiments are technically achievable

---

## Final Hypothesis

### Title
Memory Horizon Separation in SSM Adaptation: Spectral Surgery vs Eigenmode Utilization

### Hypothesis ID
H-MHSH-EUH-v1

### Core Claim

**Under** SSM-based language models (Mamba architecture), **if** we apply parameter-efficient fine-tuning via projection-only LoRA, **then** task adaptation success depends on whether task information dependencies fall within the model's spectral memory horizon H_spec, **because** projection-only LoRA can redistribute state energy across existing eigenmodes (Eigenmode Utilization) but cannot extend the spectral horizon without modifying the discretization parameters that determine eigenvalue magnitudes (Spectral Surgery).

### Mechanism

1. SSM state dynamics governed by discretized transition matrix Ā = exp(ΔA) with eigenvalues determining decay rates
2. Projection-only LoRA modifies input/output mappings but does not change Ā eigenvalues, preserving spectral horizon H_spec
3. Projection-only LoRA can redistribute state energy toward slow eigenmodes, effectively utilizing latent memory capacity
4. Tasks requiring information beyond H_spec fail under projection-only LoRA unless slow modes exist to exploit; SSM-core adaptation can extend H_spec

---

## Predictions

### P1 (Primary)
**Statement**: For MQAR tasks with dependency L ≤ H_spec, projection-only LoRA achieves accuracy within 1% of SSM-core LoRA

**Success Criterion**: |Acc_projection - Acc_core| ≤ 1% absolute

**Falsification**: If projection-only underperforms by >5% at L ≤ H_spec

### P2
**Statement**: For tasks with L = 4×H_spec, either (a) projection-only fails AND ΔH_spec < 10%, or (b) projection-only succeeds with ΔE > 0.1 nats

**Success Criterion**: (Acc < 50% AND ΔH_spec < 10%) XOR (Acc > 70% AND ΔE > 0.1)

**Falsification**: If both conditions hold simultaneously, or neither holds

### P3
**Statement**: SSM-core LoRA increases ΔH_spec > 50% when successful on beyond-horizon tasks

**Success Criterion**: ΔH_spec > 50% when beyond-horizon accuracy > 70%

**Falsification**: If SSM-core succeeds without significant H_spec extension

---

## Novelty

### Key Innovation
First principled framework connecting SSM spectral properties to PEFT method selection. Introduces H_spec as a measurable boundary for adaptation strategy.

### Differentiation from Prior Work

| Prior Work | Our Difference |
|------------|----------------|
| SSM-PEFT (ICML 2025) | Proposes SDT empirically; we provide spectral theory explaining WHY projection-only fails |
| MambaPEFT (ICLR 2025) | Catalogs 20 methods without selection criterion; we provide H_spec boundary |
| State-offset Tuning (ACL 2025) | Works empirically; we unify with spectral dynamics framework |

---

## Experimental Design

### Model
- **Primary**: Mamba-1.4B
- **Validation**: Mamba-370M (cross-scale)

### Dataset
- **MQAR (Multi-Query Associative Recall)**: Synthetic task with controllable dependency length L and N > state_dim associations to prevent low-dimensional compression

### Baselines
1. Projection-only LoRA (standard PEFT)
2. SSM-core LoRA (discretization parameters)
3. State-offset Tuning (h' = h + offset)
4. Hybrid (LoRA + state-offset)
5. Full fine-tuning (upper bound)

### Critical Tests
1. **Jacobian Stability**: CV(λ_max) < 0.3 across 1000 sequences
2. **Within-Horizon**: L = H_spec comparison across methods
3. **Beyond-Horizon**: L = {2H, 4H, 8H} extrapolation with Δλ and ΔE measurement
4. **Surgical Test**: A-matrix scaling with eigenvector-rotation control
5. **Cross-Scale**: H_spec scaling with model size

---

## Limitations

### Known Limitations
- Eigenanalysis requires linearization which may not capture nonlinear effects
- MQAR is synthetic; generalization to natural language tasks is exploratory
- Cross-scale validation limited to available Mamba checkpoints
- RWKV architecture has implicit dynamics, harder eigenanalysis

### Key Assumptions Requiring Validation
- A1: Jacobian stability across tokens (CV < 0.3)
- A2: A-matrix scaling isolates memory effects without representational damage
- A3: MQAR with N > state_dim prevents low-dimensional compression
- A4: H_spec scales predictably with model size
- A5: Pretrained Mamba can learn MQAR with fine-tuning

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Achieved with 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed in discussion) |

### Persona Verdicts

| Persona | Verdict |
|---------|---------|
| Dr. Nova (Novelty) | STRONG |
| Prof. Vera (Falsifiability) | STRONG |
| Dr. Sage (Significance) | STRONG |
| Prof. Pax (Feasibility) | STRONG |

---

## Phase 2B Readiness

**Status**: READY

**Sub-Hypothesis Seeds**:
- **SH1 (Existence)**: SSM spectral horizon H_spec is measurable and stable (CV < 0.3)
- **SH2 (Mechanism)**: Either MHSH or EUH explains adaptation via Δλ vs ΔE signatures
- **SH3 (Comparison)**: Projection-only vs SSM-core effectiveness depends on L/H_spec ratio

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
