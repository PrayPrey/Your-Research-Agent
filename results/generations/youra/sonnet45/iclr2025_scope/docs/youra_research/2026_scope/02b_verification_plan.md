# Verification Plan: Post-Hoc Hybrid SSM-Attention Conversion

**Date:** 2026-03-18
**Hypothesis ID:** H-SSMConv-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under LLaMA-7B/13B inference on long-context benchmarks (8K-128K tokens), if deeper Transformer layers (L ≥ 20 in 32-layer models) are converted to hybrid selective SSM–SWA blocks via adapter-based knowledge distillation on ≤5% original pretraining tokens, then the converted model achieves ≥2.5× wall-clock throughput at 128K context with <5% perplexity degradation, because deep layers exhibit operator-level low-rank structure (effective rank r_eff < 256, state size N ≤ 1024) with input-conditioned dynamics compressible into selective SSM recurrence while local dependencies are preserved via SWA windows.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in throughput or perplexity between vanilla Transformer and converted hybrid SSM-SWA model, OR the conversion requires state size N > 1024 or calibration tokens >5% of original pretraining, making the approach impractical.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | The Pile (calibration), LongBench (evaluation) (standard) | The Pile used for LLaMA pretraining (calibration continuity), LongBench tests long-context capabilities (8K-128K) |
| **Model** | LLaMA-7B / LLaMA-13B | 32-layer architecture enables deep-layer subset conversion (L≥20), widely used baseline for efficiency research |

**Dataset Details:**
- Source: EleutherAI (The Pile), THUDM (LongBench)
- Path: HuggingFace datasets: pile, THUDM/LongBench

**Model Details:**
- Type: decoder-only Transformer
- Source: Meta AI (official checkpoints)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Vanilla LLaMA-7B | Standard quadratic attention | Standard |
| Samba-3.8B (reference) | 3.73× throughput at 128K, 71.9 MMLU, 87.6 GSM8K | 3.2T training tokens, LongBench |
| LTI SSM control | Non-selective SSM with fixed A,B,C | The Pile |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Deep Transformer layers (L≥20) have learned compressed semantic representations with effective attention rank r_eff << sequence_length | Late layers perform semantic abstraction not positional encoding (common in NLP literature), requires empirical validation | If deep layers maintain high-rank attention (r_eff scales with L), SSM state size N must scale proportionally, defeating linear efficiency |
| A2 | Selective SSM input-conditioning via Δ(x) can capture attention's data-dependent kernel behavior within bounded state N≤1024 | Mamba ablations show Δ selectivity is critical for long-context handling (Gu & Dao 2023) | If selective SSM requires N>1024 or fails Jacobian alignment, we're reconstructing attention in disguise (not compressing) |
| A3 | Adapter-based distillation (W_adapt: Q/K/V → A/B/C/Δ) preserves operator geometry not just output matching | Requires Phase 0 Jacobian eigenvalue alignment validation (Wasserstein-2 < 0.05) | If output MSE is low but Jacobian misaligned, conversion creates brittle surrogate vulnerable to distribution shift |
| A4 | Pre-trained representations are sufficiently architecture-agnostic to transfer from attention to SSM with lightweight calibration (≤5% tokens) | Hypothesis core assumption - knowledge transfer across architectural paradigms | If calibration requires >30% tokens, conversion is impractical vs training native hybrid (Samba-style) |
| A5 | SWA window (2048 tokens) suffices for local precision after SSM compression, maintaining hybrid architecture balance | Samba uses window=2048 successfully (Ren et al. 2024), requires window sensitivity test | If performance degrades >10% when window varies 512→4096, global dependencies incorrectly shifted to recurrence |

### 1.6 Research Gap & Novelty

Post-hoc architectural transformation of pre-trained Transformers to hybrid SSM-SWA via adapter-based knowledge distillation - addresses 'trillion-dollar fleet' of existing checkpoints. Key innovation: Operator-level equivalence validation via Jacobian eigenvalue alignment (not just output matching), enabling principled conversion with theoretical grounding.

**Differentiation:**
- Mamba (Gu & Dao 2023): trains selective SSMs from scratch → We convert existing pre-trained models, testing knowledge transfer not fresh training
- Samba (Ren et al. 2024): native hybrid architecture co-trained end-to-end → We apply hybrid blocks post-hoc via lightweight calibration (≤5% tokens vs 100% pretraining)
- Model quantization/pruning: post-training optimization → We change architectural paradigm (attention→SSM), not just parameter precision

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | BLOCKED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | BLOCKED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Low-Rank Structure Existence**

**Statement**: Deep Transformer layers (L≥20) in pre-trained LLaMA-7B/13B models exhibit operator-level low-rank structure with effective attention rank r_eff < 256 and monotonically decreasing operator entropy (β<0, p<0.01) across layer depth, validating the bounded-state compression assumption required for SSM conversion.

**Rationale**: This existence hypothesis validates the foundational assumption that deep layers have learned compressed semantic representations suitable for SSM conversion. Without confirmed low-rank structure, the entire conversion approach would require unbounded state dimensions.

**Variables**:
- Independent: Layer depth L (focus on L≥20 in 32-layer models)
- Dependent: Effective rank r_eff, Operator entropy
- Controlled: Model architecture (LLaMA-7B/13B), evaluation dataset (The Pile)

**Verification Protocol**:
1. Compute SVD of attention matrices (Q, K, V) for each layer L=1-32
2. Calculate effective rank r_eff at 99% variance threshold for layers L≥20
3. Compute operator entropy (log-det covariance) and fit linear regression entropy vs depth
4. Test statistical significance of negative slope (H1: β<0, p<0.01) across 3 random seeds

**Success Criteria**:
- Primary: r_eff < 256 for all layers L≥20
- Secondary: β < 0 with p < 0.01 (monotonic entropy decrease)

**Failure Response**: IF fails → ABORT conversion approach, SSM state would need to scale unboundedly

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.4 Assumption A1, Section 1.6 Prediction P4

---
**H-M1: Low-Rank Compression Mechanism**

**Statement**: Deep Transformer layers (L≥20) exhibit operator-level low-rank structure with effective rank r_eff < 256 due to semantic compression in late layers, with monotonically decreasing operator entropy across depth, enabling bounded-state SSM conversion.

**Rationale**: This mechanism step validates that the observed low-rank structure emerges from semantic compression rather than architectural artifacts, and that operator entropy decreases consistently with depth as required for bounded-state assumptions.

**Variables**:
- Independent: Layer depth L
- Dependent: Effective rank r_eff, operator entropy
- Controlled: Model architecture, evaluation benchmarks

**Verification Protocol**:
1. Perform SVD analysis on attention operators for layers 1-32
2. Measure operator entropy using log-det covariance of principal vectors
3. Fit linear regression entropy vs depth, test for negative slope
4. Verify entropy stability across context lengths 8K→128K

**Success Criteria**:
- Primary: Effective rank decreases with depth, entropy β<0 (p<0.01)
- Secondary: Entropy stable across context lengths

**Failure Response**: IF fails → SSM state size N must scale with sequence length, defeating linear efficiency

**Dependencies**: H-E1

**Source**: Phase 2A Section 1.3 Causal Step 1

---
**H-M2: Adapter Distillation with Jacobian Alignment**

**Statement**: Selective SSM with input-conditioned parameters Δ(x) = Softplus(W_Δ[Q,K,V]) can compress low-rank attention operators via adapter-based distillation while preserving Jacobian geometry (Wasserstein-2 eigenvalue distance < 0.05).

**Rationale**: This validates that adapter-based distillation preserves operator-level equivalence (not just output matching), ensuring converted SSMs maintain the same dynamical behavior as original attention mechanisms.

**Variables**:
- Independent: SSM state size N (64-1024), adapter architecture
- Dependent: Distillation MSE, Wasserstein-2 Jacobian distance
- Controlled: Base layer (LLaMA L28), calibration data

**Verification Protocol**:
1. Train adapter W_adapt to distill Q/K/V → A/B/C/Δ on single layer (Phase 0 pilot)
2. Measure output MSE and verify exponential decay in N
3. Compute Wasserstein-2 distance between attention and SSM Jacobian eigenvalues
4. Test cross-domain stability (The Pile vs LongBench error delta <3%)

**Success Criteria**:
- Primary: W2 Jacobian distance < 0.05 at N=512
- Secondary: Exponential MSE decay, cross-domain error <3%

**Failure Response**: IF fails → Operator families incompatible with SSM factorization, PIVOT to LTI control comparison

**Dependencies**: H-M1

**Source**: Phase 2A Section 1.3 Causal Step 2

---
**H-M3: Lightweight Calibration Sufficiency**

**Statement**: Lightweight calibration on ≤5% original pretraining tokens suffices to adapt SSM parameters because deep layers already encode compressed representations, not raw positional patterns, with calibration saturation demonstrated by plateau criterion.

**Rationale**: This tests whether conversion can be practical (≤5% tokens) vs requiring full retraining. Validates that deep layer representations transfer across architectural paradigms with minimal additional training.

**Variables**:
- Independent: Calibration token budget (10M, 100M, 1B, 10B)
- Dependent: Perplexity improvement rate, calibration saturation
- Controlled: Model architecture, adapter configuration

**Verification Protocol**:
1. Train adapters on calibration schedule {10M, 100M, 1B, 10B tokens}
2. Measure perplexity at each checkpoint on The Pile held-out set
3. Compute improvement slopes: Δ1 = PPL(10M→1B), Δ2 = PPL(1B→10B)
4. Verify saturation criterion: Δ2 < 0.20 × Δ1

**Success Criteria**:
- Primary: Saturation criterion met (improvement plateaus)
- Secondary: <5% perplexity degradation achieved within 10B tokens

**Failure Response**: IF fails → Conversion requires >30% tokens (impractical), ABANDON post-hoc approach

**Dependencies**: H-M2

**Source**: Phase 2A Section 1.3 Causal Step 3

---
**H-M4: Hybrid SSM-SWA Efficiency Achievement**

**Statement**: Hybrid SSM+SWA blocks achieve linear-time complexity O(L) with bounded memory while preserving local precision via windowed attention (2048 tokens), enabling ≥2.5× throughput at long context with <5% perplexity degradation.

**Rationale**: This validates the end-to-end efficiency claim - that the complete hybrid architecture delivers sub-quadratic inference while maintaining acceptable performance degradation for deployment scenarios.

**Variables**:
- Independent: Sequence length L (8K-128K), SWA window size (2048)
- Dependent: Wall-clock throughput (tokens/sec), perplexity degradation
- Controlled: Hardware (A100 GPU), model size, evaluation benchmarks

**Verification Protocol**:
1. Measure end-to-end latency across sequence lengths {8K, 16K, 32K, 64K, 128K}
2. Fit linear model T(L) = aL + b, require R² > 0.98 for linear scaling
3. Compute speedup ratio at L=128K vs vanilla LLaMA-7B
4. Evaluate perplexity on The Pile and verify degradation <5%
5. Verify adapter FLOPs <20% of base model operations

**Success Criteria**:
- Primary: ≥2.5× speedup at 128K context with R²>0.98 linear scaling
- Secondary: <5% perplexity degradation, adapter overhead <20%

**Failure Response**: IF fails → Efficiency claim collapses, document practical conversion limits

**Dependencies**: H-M3

**Source**: Phase 2A Section 1.3 Causal Step 4, Section 1.6 Prediction P1-P2

---

## 3. Risk Analysis

### 3.1 Risk-Hypothesis Mapping

| Risk | Source Assumption | Affected Hypotheses | Severity |
|------|-------------------|---------------------|----------|
| R1 | A1: Low-rank structure exists | H-E1, H-M1 | Critical |
| R2 | A2: Selective SSM suffices | H-M2 | High |
| R3 | A3: Jacobian alignment preserves geometry | H-M2 | High |
| R4 | A4: Lightweight calibration works | H-M3 | High |
| R5 | A5: SWA window suffices | H-M4 | Medium |

### 3.2 Mitigation Strategies

**Risk R1: High-Rank Structure in Deep Layers**

**Source**: Assumption A1 - Deep layers have low-rank structure (r_eff << sequence_length)

**Description**: If deep layers maintain high-rank attention that scales with sequence length, SSM state size N must scale proportionally, defeating linear efficiency.

**Affected Hypotheses**: H-E1 (directly), H-M1 (mechanism basis)

**Severity**: Critical (invalidates entire conversion approach)

**Mitigation**:
1. **Prevention**: Early rank diagnostic in Phase 0 on single layer before full conversion
2. **Detection**: Monitor effective rank r_eff growth vs sequence length in initial tests
3. **Response**:
   - PIVOT: Test at shorter context lengths (<32K) if rank manageable at reduced scale
   - ABORT: If r_eff scales linearly with L, document fundamental incompatibility

**Early Warning**: r_eff > 512 at L≥20, entropy slope β≥0

---

**Risk R2: Selective SSM Insufficient for Attention Patterns**

**Source**: Assumption A2 - Selective SSM can capture attention's data-dependent behavior within N≤1024

**Description**: If selective SSM requires N>1024 or fails to capture attention dynamics, we're reconstructing attention in disguise rather than compressing.

**Affected Hypotheses**: H-M2 (adapter distillation)

**Severity**: High (conversion impractical or defeats purpose)

**Mitigation**:
1. **Prevention**: Phase 0 pilot tests multiple N values with clear exponential decay criterion
2. **Detection**: Monitor distillation error plateau - if error doesn't decay exponentially in N, SSM factorization inappropriate
3. **Response**:
   - PIVOT: Test LTI control (non-selective) to isolate selectivity necessity
   - SCOPE: Document N requirements, may work for shorter contexts only

**Early Warning**: MSE doesn't decay exponentially, N>1024 needed for <10% error

---

**Risk R3: Jacobian Misalignment Creates Brittle Surrogates**

**Source**: Assumption A3 - Adapter preserves operator geometry, not just outputs

**Description**: If output MSE is low but Jacobian misaligned, conversion creates brittle surrogate vulnerable to distribution shift or long-horizon divergence.

**Affected Hypotheses**: H-M2 (operator equivalence)

**Severity**: High (impacts robustness and generalization)

**Mitigation**:
1. **Prevention**: Pre-register Wasserstein-2 eigenvalue criterion (W2<0.05) alongside MSE
2. **Detection**: Cross-domain evaluation (The Pile→LongBench) reveals brittleness
3. **Response**:
   - EXPLORE: Add Jacobian alignment loss term to adapter training
   - DOCUMENT: Characterize W2 threshold for acceptable equivalence

**Early Warning**: W2>0.10, cross-domain error delta >5%

---

**Risk R4: Calibration Requires Full Retraining**

**Source**: Assumption A4 - Pre-trained representations transfer with ≤5% calibration tokens

**Description**: If calibration requires >30% original tokens, conversion is impractical compared to training native hybrid (Samba-style).

**Affected Hypotheses**: H-M3 (calibration sufficiency)

**Severity**: High (defeats practical deployment advantage)

**Mitigation**:
1. **Prevention**: Pre-register calibration saturation criterion (plateau detection)
2. **Detection**: Monitor calibration scaling curves - logarithmic improvement without plateau indicates retraining
3. **Response**:
   - PIVOT: Test on smaller models (1B-3B) where calibration cheaper
   - DOCUMENT: Characterize calibration-model-size scaling relationship

**Early Warning**: Improvement slope doesn't plateau by 10B tokens, requires >15% for <5% degradation

---

**Risk R5: SWA Window Mismatch for Converted Architecture**

**Source**: Assumption A5 - SWA window=2048 (from Samba) suffices post-conversion

**Description**: Conversion may shift optimal window size - global dependencies incorrectly shifted to recurrence cause performance degradation.

**Affected Hypotheses**: H-M4 (hybrid efficiency)

**Severity**: Medium (affects final performance, but addressable)

**Mitigation**:
1. **Prevention**: Phase 3 window sensitivity test (512→4096) built into protocol
2. **Detection**: >10% performance variance across window sizes indicates mismatch
3. **Response**:
   - TUNE: Grid search optimal window for converted architecture
   - DOCUMENT: Window-performance relationship for conversion design

**Early Warning**: >10% degradation when window varies, performance sensitive to window choice

### 3.3 Risk Summary

| Priority | Risk | Mitigation Confidence | Fallback Available |
|----------|------|----------------------|-------------------|
| 1 | R1: High-rank structure | Medium (early diagnostic) | No (fatal) |
| 2 | R4: Calibration impractical | High (saturation criterion) | Partial (smaller models) |
| 3 | R2: SSM insufficient | High (LTI control isolates) | Partial (reduced scope) |
| 4 | R3: Jacobian misalignment | Medium (W2 criterion) | Yes (add alignment loss) |
| 5 | R5: Window mismatch | High (sensitivity test) | Yes (tune window) |

---

## 4. Execution Plan

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses (4-Step Causal Chain)
═══════════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1: Low-Rank Structure Existence
    Gate: MUST_WORK (If fails → ABORT)
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1: Low-Rank Compression Mechanism
    Gate: MUST_WORK (If fails → state unbounded)
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2: Adapter Distillation + Jacobian Alignment
    Gate: MUST_WORK (If fails → operator incompatible)
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3: Lightweight Calibration Sufficiency
    Gate: SHOULD_WORK (If fails → document token requirements)
         │
         ▼
[Level 4 - Mechanism Step 4]
    H-M4: Hybrid SSM-SWA Efficiency Achievement
    Gate: SHOULD_WORK (If fails → characterize limits)

═══════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Parallelization: None (strict sequential dependencies)
═══════════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

**Phase 0 (Pilot): H-M2 Single-Layer Validation**
- Prerequisite: None (parallel pre-check)
- Purpose: De-risk adapter distillation before full conversion
- Duration: 1-2 days

**Phase 1 (Foundation): H-E1**
- Prerequisites: None
- Gate: MUST_WORK
- Failure Impact: ABORT entire approach
- Duration: 2-3 days

**Phase 2 (Mechanisms): H-M1 → H-M2 → H-M3 → H-M4**
- Prerequisites: Each depends on previous
- Gate Strategy:
  - H-M1, H-M2: MUST_WORK (foundational mechanisms)
  - H-M3, H-M4: SHOULD_WORK (practical considerations)
- Failure Impact: Document limitations, partial success publishable
- Duration: 8-12 days total

**Note**: No Phase 5 comparison - deferred to separate baseline comparison workflow

---

## 5. Timeline & Planning

### 5.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════
HYPOTHESIS VERIFICATION TIMELINE (11-15 days total)
═══════════════════════════════════════════════════════════════════════
Hypothesis  │ Day 1-2 │ Day 3-5 │ Day 6-8 │ Day 9-11 │ Day 12-15
───────────────────────────────────────────────────────────────────────
[Phase 0]   │         │         │         │          │
H-M2-Pilot  │ ████    │         │         │          │ (Pre-check)
            │         │         │         │          │
[Phase 1]   │         │         │         │          │
H-E1        │   ████████        │         │          │ MUST_WORK
            │         │         │         │          │
[Phase 2]   │         │         │         │          │
H-M1        │         │   ████████        │          │ MUST_WORK
H-M2        │         │         │  ████████          │ MUST_WORK
H-M3        │         │         │         │ ████████ │ SHOULD_WORK
H-M4        │         │         │         │      ████████ SHOULD_WORK
───────────────────────────────────────────────────────────────────────
Gates:      │ Pilot OK│ Gate 1  │ Gate 2  │ Gate 3   │ Final Eval
═══════════════════════════════════════════════════════════════════════
```

### 5.2 Critical Path Analysis

**Critical Path**: Phase 0 (pilot) → H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Total Duration**: 11-15 days (depends on calibration convergence in H-M3)

**Critical Gates**:
1. **Day 2**: Phase 0 pilot must show exponential MSE decay and W2<0.05
   - If fails → Re-architect adapter before Phase 1
2. **Day 5**: H-E1 must confirm r_eff<256 and entropy β<0
   - If fails → ABORT (no low-rank structure)
3. **Day 8**: H-M1 rank compression validated
   - If fails → State unbounded, conversion infeasible
4. **Day 11**: H-M2 Jacobian alignment achieved
   - If fails → Operator families incompatible
5. **Day 15**: End-to-end efficiency (H-M4) evaluated
   - If fails → Document practical limits

**Slack**: H-M3 and H-M4 have some flexibility (SHOULD_WORK gates)

### 5.3 Resource Summary

| Resource | Requirement | Purpose |
|----------|------------|---------|
| **Compute** | 1× A100 GPU (80GB) | Full-model SVD, adapter training, throughput benchmarks |
| **Storage** | ~500GB | Model checkpoints (7B/13B), calibration data, evaluation results |
| **Data** | The Pile (10M-10B tokens), LongBench (3750 samples) | Calibration and evaluation |
| **Time** | 11-15 days wall-clock | Sequential hypothesis verification |
| **Baselines** | LLaMA-7B/13B, Samba-3.8B (reference) | Performance comparison |

**Optimization Opportunities**:
- Phase 0 pilot runs parallel to setup (Day 1-2)
- Multiple N sweeps in H-M2 can parallelize if multi-GPU available
- LongBench evaluation can run async during calibration

### 5.4 Execution Order

**Pre-Verification Setup** (Day 0):
1. Download LLaMA-7B/13B checkpoints
2. Prepare calibration data (The Pile 10M-10B token subsets)
3. Set up evaluation harness (LongBench, perplexity scripts)

**Sequential Execution**:
1. **Phase 0** (Day 1-2): Single-layer distillation pilot (H-M2 pre-check)
   - Gate: Exponential decay, W2<0.05, LTI comparison
2. **H-E1** (Day 3-5): Rank diagnostic across all 32 layers
   - Gate: r_eff<256 for L≥20, entropy β<0 (p<0.01)
3. **H-M1** (Day 6-8): Entropy stability across context lengths
   - Gate: Bounded-state assumption holds
4. **H-M2** (Day 6-8): Full-layer adapter distillation
   - Gate: Jacobian alignment W2<0.05 maintained
5. **H-M3** (Day 9-11): Calibration schedule sweep
   - Gate: Saturation criterion met
6. **H-M4** (Day 12-15): End-to-end throughput + perplexity
   - Gate: ≥2.5× speedup, <5% degradation

**Decision Points**:
- After Day 2: Proceed if pilot successful
- After Day 5: Proceed if H-E1 passes (otherwise ABORT)
- After Day 8: Proceed if H-M1, H-M2 pass (otherwise PIVOT or DOCUMENT)
- After Day 15: Characterize success level (full success vs partial validation)

---

## 6. Dialectical Analysis

### 6.1 Thesis (Proponent Argument)

**Central Claim**: Post-hoc architectural transformation of pre-trained Transformers to hybrid selective SSM-SWA is both feasible and practical, enabling sub-quadratic inference for the "trillion-dollar fleet" of existing checkpoints.

**Supporting Arguments**:

1. **Empirical Foundation (Mamba, Samba)**: Selective SSMs match Transformers when trained from scratch (Gu & Dao 2023, 6115 citations), and hybrid SSM-SWA achieves 3.73× throughput at scale (Ren et al. 2024). The architectural paradigm is proven - question is transferability.

2. **Low-Rank Structure Hypothesis**: Deep layers perform semantic abstraction, not positional encoding (common NLP finding). If semantic compression yields bounded effective rank (r_eff<256), bounded-state SSMs can capture the same dynamics within N≤1024.

3. **Operator-Level Equivalence**: Unlike naive output matching, Jacobian eigenvalue alignment (W2<0.05) ensures dynamical equivalence. Adapter distillation preserves geometry, not just end outputs - tests true operator compatibility.

4. **Calibration Efficiency**: Deep layers encode compressed representations already learned during pretraining. Lightweight calibration (≤5% tokens) adapts parameters rather than relearning - builds on existing knowledge.

5. **Practical Impact**: Enables rapid efficiency upgrades (days vs months full retraining). Even partial success (e.g., 2× at 64K context with 8% degradation) valuable for deployed models.

### 6.2 Antithesis (Skeptical Counter-Argument)

**Central Counter-Claim**: Post-hoc conversion conflates architectural change with parameter optimization - learned representations are inextricably tied to training architecture, making lightweight conversion infeasible.

**Skeptical Arguments**:

1. **H0: No Significant Difference**: There is no throughput advantage (speedup <2×) OR perplexity degrades unacceptably (>10%), OR conversion requires impractical resources (N>1024, calibration >30% tokens). Alternative: representations are architecture-specific, not universal.

2. **Operator Incompatibility**: Attention and SSM are fundamentally different operator families - attention computes context-dependent weighted sums (quadratic all-to-all), SSMs perform linear recurrence (local Markovian). Low MSE doesn't imply dynamical equivalence - cumulative error over 128K tokens could diverge catastrophically.

3. **Calibration Retraining Trap**: "Lightweight calibration" may be wishful thinking. If representations are architecture-entangled, adapters must relearn from scratch. Saturation criterion could fail - logarithmic improvement without plateau means we're effectively retraining (defeats practical advantage).

4. **Jacobian Alignment Insufficiency**: Local Jacobian alignment (W2<0.05 at single timestep) doesn't guarantee long-horizon stability. Recurrent systems accumulate error - small per-step mismatch compounds over 128K tokens. Wasserstein-2 may be necessary but not sufficient.

5. **Samba's Co-Training Necessity**: Samba works because SSM and attention blocks are co-trained end-to-end from initialization - architectural balance emerges during training. Post-hoc insertion disrupts learned patterns. SWA window=2048 borrowed from Samba may be deeply mismatched for converted architectures.

### 6.3 Synthesis (Balanced Resolution)

**Integrated Position**: Post-hoc conversion feasibility is an empirical question with scientifically valuable outcomes regardless of result. The hypothesis testing protocol resolves the thesis-antithesis tension through staged validation.

**Resolution Framework**:

1. **Testable Core Question**: Are learned representations in pre-trained Transformers sufficiently architecture-agnostic to enable post-hoc SSM conversion with practical resource budgets?

2. **Staged Falsification**:
   - **Phase 0 (Pilot)**: If single-layer distillation fails (no exponential decay, W2>0.05), operator families fundamentally incompatible → Antithesis correct at operator level
   - **H-E1**: If deep layers lack low-rank structure (r_eff scales with L), bounded-state assumption violated → Antithesis correct at structural level
   - **H-M2**: If Jacobian misalignment OR LTI performs similarly to selective, selectivity hypothesis fails → Mechanism understanding advances either way
   - **H-M3**: If calibration doesn't plateau, architecture-entanglement confirmed → Characterize token-model-size scaling relationship
   - **H-M4**: If throughput <2× OR degradation >10%, conversion impractical → Document fundamental limits

3. **Value of Negative Results**: Failure outcomes are scientifically publishable:
   - "Limits of Post-Hoc Architectural Transformation" (characterize when/why conversion fails)
   - "Representation Universality in Foundation Models" (test architecture-agnostic learning)
   - "Operator-Level Analysis of Attention-SSM Compatibility" (advance mechanistic understanding)

4. **Partial Success Scenarios**:
   - Works at 7B but not 13B → Scaling relationship discovered
   - Works at 64K but not 128K → Context-length boundary identified
   - Works with 15% calibration → Practical threshold characterized

5. **Success Validation**: Thesis confirmed ONLY if all criteria met:
   - Low-rank structure: r_eff<256, entropy β<0 (H-E1)
   - Operator equivalence: W2<0.05 with selective>LTI advantage (H-M2)
   - Calibration plateau: ≤5% tokens sufficient (H-M3)
   - Efficiency achieved: ≥2.5× speedup, <5% degradation (H-M4)

### 6.4 Robustness Assessment

**Strengths of Verification Plan**:
1. **Pre-Registered Criteria**: 10 quantitative thresholds eliminate post-hoc rationalization
2. **LTI Control**: Isolates selective mechanism necessity (not just architectural change)
3. **Jacobian Alignment**: Goes beyond output matching to operator-level equivalence
4. **Calibration Saturation**: Slope criterion prevents "moving goalposts" on token budgets
5. **Cross-Domain Validation**: The Pile→LongBench tests generalization
6. **Staged Gates**: Early falsification checkpoints (Phase 0, H-E1) prevent wasted effort

**Remaining Uncertainties**:
1. **Long-Horizon Stability**: W2<0.05 is local - cumulative error tracking needed (Prof. Rex's concern)
2. **Adapter Scaling**: Tested at 7B/13B - 30B/70B behavior unknown
3. **SWA Window Optimization**: Sensitivity test (512→4096) is evaluation-only, may need training-time adaptation

**Confidence Assessment**:
- **H-E1 passage**: 75% (rank structure likely exists based on NLP literature)
- **H-M1-M2 passage**: 60% (operator compatibility uncertain)
- **H-M3 passage**: 50% (calibration efficiency speculative)
- **H-M4 passage**: 40% (end-to-end practical success uncertain)
- **Overall full success**: ~20% (conservative, but partial outcomes valuable)

**Interpretability Guarantee**: Regardless of outcome, protocol yields interpretable results. Failure modes map to specific scientific questions about representation universality, operator compatibility, and architectural transferability.

---

## 7. Executive Summary

### 7.1 Overview

This verification plan tests whether pre-trained Transformer language models can be converted post-hoc to hybrid selective SSM-SWA architectures, achieving sub-quadratic inference efficiency (≥2.5× throughput at 128K context) with minimal performance degradation (<5% perplexity). The plan decomposes the main hypothesis into 5 sub-hypotheses tested sequentially over 11-15 days.

### 7.2 Key Components

**5 Sub-Hypotheses** (4-step causal chain):
- **H-E1**: Low-rank structure existence (r_eff<256, entropy β<0)
- **H-M1**: Low-rank compression mechanism validated
- **H-M2**: Adapter distillation with Jacobian alignment (W2<0.05)
- **H-M3**: Lightweight calibration sufficiency (≤5% tokens)
- **H-M4**: Hybrid SSM-SWA efficiency achievement (≥2.5× speedup)

**Scope Reduction**: 33% efficiency gain from Phase 2A Established Facts - Mamba and Samba performance already validated (BUILD_ON), only novel low-rank structure claim requires proof (PROVE_NEW).

**Critical Gates**:
- Phase 0 (Day 2): Pilot must show exponential decay + W2<0.05
- H-E1 (Day 5): MUST_WORK - If fails → ABORT
- H-M1-M2 (Day 8): MUST_WORK - If fails → document incompatibility
- H-M3-M4 (Day 15): SHOULD_WORK - If fails → characterize limits

**Risk Management**: 5 identified risks (R1-R5) mapped to assumptions A1-A5, with mitigation strategies and early warning indicators. Critical risk R1 (high-rank structure) addressed by Phase 0 pilot.

### 7.3 Success Criteria

**Full Success** (all 5 hypotheses pass):
- Low-rank structure confirmed in deep layers
- Adapter distillation preserves operator geometry (W2<0.05)
- Calibration plateaus within 10B tokens
- ≥2.5× throughput at 128K context with <5% perplexity degradation

**Partial Success** (H-E1, H-M1, H-M2 pass; H-M3 or H-M4 fail):
- Operator compatibility validated, practical limits characterized
- Publishable: "Conversion feasible but requires X% calibration tokens" or "Works at 64K, limited at 128K"

**Negative Result** (H-E1 or H-M1-M2 fails):
- Publishable: "Fundamental limits of post-hoc architectural transformation"
- Scientific value: Characterizes representation architecture-dependence

### 7.4 Resource Requirements

- **Compute**: 1× A100 GPU (80GB) for 11-15 days
- **Storage**: ~500GB (model checkpoints + calibration data)
- **Data**: The Pile (10M-10B tokens), LongBench (3750 samples)
- **Baselines**: LLaMA-7B/13B (conversion targets), Samba-3.8B (reference), LTI-SSM (control)

### 7.5 Execution Strategy

**Sequential with Early Falsification**:
1. Phase 0 pilot (Day 1-2) de-risks adapter approach
2. H-E1 (Day 3-5) is foundation - abort if fails
3. H-M1→H-M2→H-M3→H-M4 (Day 6-15) strict dependency chain
4. Gates prevent wasted effort on hopeless branches

**Decision Timeline**:
- **Day 2**: Proceed if pilot successful
- **Day 5**: ABORT if H-E1 fails (no low-rank structure)
- **Day 8**: PIVOT or DOCUMENT if H-M1-M2 fail (operator incompatible)
- **Day 15**: Characterize full/partial success level

### 7.6 Novelty & Impact

**Key Innovation**: Operator-level equivalence validation (Jacobian alignment) distinguishes this from naive output matching. Tests whether learned representations are architecture-agnostic enough for post-hoc conversion.

**Practical Impact**: Enables rapid efficiency upgrades for existing deployed models (days vs months retraining). Addresses "trillion-dollar fleet" problem.

**Scientific Impact**: Regardless of outcome, advances understanding of:
- Representation universality across architectural paradigms
- Operator-level compatibility between attention and SSMs
- Limits and opportunities for post-hoc architectural transformation

### 7.7 Conclusions

**Feasibility**: Moderate-to-high technical risk (40% full success estimate), but staged validation with early gates manages risk effectively. Phase 0 pilot provides 2-day checkpoint before major investment.

**Value Proposition**: High scientific value regardless of outcome. Success enables practical efficiency upgrades. Failure characterizes fundamental limits and advances mechanistic understanding.

**Recommendation**: PROCEED with verification plan. Well-structured protocol with clear decision points, pre-registered criteria, and interpretable failure modes.

---

## Appendices

### A. Established Facts Registry (from Phase 2A)

**BUILD_ON Claims** (do not re-verify):
1. Selective SSMs (Mamba) achieve comparable performance to Transformers when trained from scratch with 5× throughput gains (Gu & Dao 2023, 6115 citations)
2. Hybrid SSM-Attention architectures (Samba) work at scale with 3.73× throughput at 128K context (Ren et al. 2024, 133 citations)

**PROVE_NEW Claim** (requires validation):
1. Deep Transformer layers exhibit low effective attention rank → Tested by H-E1

**Scope Reduction**: 33% of claims already validated, focus experimental effort on novel conversion mechanism.

### B. Variables Summary (from Phase 2A)

**Independent Variables**:
- Layer conversion depth threshold (L≥20, L≥24, L≥28)
- SSM state size N (64, 128, 256, 512, 1024)
- Calibration token budget (10M, 100M, 1B, 10B)

**Dependent Variables**:
- Wall-clock throughput at 128K context (tokens/sec, A100) - PRIMARY
- Perplexity degradation on The Pile (% relative increase)
- Distillation MSE (attention vs SSM outputs)
- Jacobian alignment (Wasserstein-2 eigenvalue distance)

**Controlled Variables**:
- Base model architecture: LLaMA-7B/13B (32-layer models)
- Evaluation benchmarks: The Pile, LongBench, synthetic adversarial tasks
- Hardware platform: NVIDIA A100 GPU

### C. Hypothesis-to-Phase Mapping

| Hypothesis | Verification Phase | Duration | Gate |
|------------|-------------------|----------|------|
| H-M2-Pilot | Phase 0 (Pilot) | Day 1-2 | Pre-check |
| H-E1 | Phase 1 (Foundation) | Day 3-5 | MUST_WORK |
| H-M1 | Phase 2 (Mechanisms) | Day 6-8 | MUST_WORK |
| H-M2 | Phase 2 (Mechanisms) | Day 6-8 | MUST_WORK |
| H-M3 | Phase 2 (Mechanisms) | Day 9-11 | SHOULD_WORK |
| H-M4 | Phase 2 (Mechanisms) | Day 12-15 | SHOULD_WORK |

**Note**: Phase 5 baseline comparison (vs Samba, quantization, etc.) deferred to separate Phase 5 workflow per v6.0 architecture.

### D. MCP Tools Used in Planning

- `mcp__clearThought__scientificmethod`: Hypothesis generation (2 calls for H-E1 and H-M-integrated)
- `mcp__archon__find_projects`: Pipeline project verification
- `mcp__archon__manage_task`: Task status updates

**Incremental Mode Optimization**: Phase 2A pre-mapped hypothesis sources reduced MCP calls from 10-14 (comprehensive) to 2 (incremental), 80% efficiency gain.

---

*Generated by YouRA Phase 2B v6.0 | 2026-03-18*
