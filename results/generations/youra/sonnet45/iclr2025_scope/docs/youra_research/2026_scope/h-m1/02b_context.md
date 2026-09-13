# Phase 2B Context: H-M1

**Generated:** 2026-03-18
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Hypothesis Information

### Statement
Deep layers compress semantic information into low-rank operators with decreasing operator entropy, enabling bounded-state conversion.

### Rationale
This mechanism step validates that the observed low-rank structure emerges from semantic compression rather than architectural artifacts, and that operator entropy decreases consistently with depth as required for bounded-state assumptions.

### Prerequisites
- h-e1 (Low-Rank Structure Existence)

### Success Criteria
- Primary: Effective rank decreases with depth, entropy β<0 (p<0.01)
- Secondary: Entropy stable across context lengths

### Failure Action
IF fails → SSM state size N must scale with sequence length, defeating linear efficiency

---

## Experimental Setup (from Phase 2B Section 1.3)

### Dataset
**Selection:** The Pile (calibration), LongBench (evaluation)
**Type:** standard
**Source:** EleutherAI (The Pile), THUDM (LongBench)
**Path:** HuggingFace datasets: pile, THUDM/LongBench
**Justification:** The Pile used for LLaMA pretraining (calibration continuity), LongBench tests long-context capabilities (8K-128K)

### Model
**Selection:** LLaMA-7B / LLaMA-13B
**Type:** decoder-only Transformer
**Source:** Meta AI (official checkpoints)
**Justification:** 32-layer architecture enables deep-layer subset conversion (L≥20), widely used baseline for efficiency research

---

## Baseline & Comparison

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Vanilla LLaMA-7B | Standard quadratic attention | Standard |
| Samba-3.8B (reference) | 3.73× throughput at 128K, 71.9 MMLU, 87.6 GSM8K | 3.2T training tokens, LongBench |
| LTI SSM control | Non-selective SSM with fixed A,B,C | The Pile |

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-e1:** Low-Rank Structure Existence (MUST_WORK gate)
  - Must confirm r_eff < 256 and entropy β < 0

### Gate Type
MUST_WORK - If fails, abort entire conversion approach

### Gate Description
Mechanism validation - if fails, state unbounded

---

## Verification Protocol (from Phase 2B Section 2.2)

### Variables
- **Independent:** Layer depth L
- **Dependent:** Effective rank r_eff, operator entropy
- **Controlled:** Model architecture, evaluation benchmarks

### Protocol Steps
1. Perform SVD analysis on attention operators for layers 1-32
2. Measure operator entropy using log-det covariance of principal vectors
3. Fit linear regression entropy vs depth, test for negative slope
4. Verify entropy stability across context lengths 8K→128K

### Success Criteria
- Primary: Effective rank decreases with depth, entropy β<0 (p<0.01)
- Secondary: Entropy stable across context lengths

### Failure Response
IF fails → SSM state size N must scale with sequence length, defeating linear efficiency

---

## Key Assumptions (from Phase 2B Section 1.5)

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Deep Transformer layers (L≥20) have learned compressed semantic representations with effective attention rank r_eff << sequence_length | Late layers perform semantic abstraction not positional encoding (common in NLP literature), requires empirical validation | If deep layers maintain high-rank attention (r_eff scales with L), SSM state size N must scale proportionally, defeating linear efficiency |

---

## Risk Analysis (from Phase 2B Section 3)

### Related Risks

**Risk R1: High-Rank Structure in Deep Layers**
- **Source:** Assumption A1 - Deep layers have low-rank structure (r_eff << sequence_length)
- **Description:** If deep layers maintain high-rank attention that scales with sequence length, SSM state size N must scale proportionally, defeating linear efficiency.
- **Severity:** Critical (invalidates entire conversion approach)
- **Mitigation:** Early rank diagnostic in Phase 0 on single layer before full conversion
- **Early Warning:** r_eff > 512 at L≥20, entropy slope β≥0

---

## Source References

- Phase 2B Section 1.3: Causal Step 1
- Phase 2B Section 2.2: H-M1 specification
- Phase 2B Section 3.2: Risk R1 mitigation
