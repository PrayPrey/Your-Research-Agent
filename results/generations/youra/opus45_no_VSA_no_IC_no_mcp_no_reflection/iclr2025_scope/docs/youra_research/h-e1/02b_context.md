# Phase 2B Context: h-e1

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Date Generated:** 2026-08-29

---

## Hypothesis Statement

Under Mamba-2 duality equations, if attention weights from a pretrained Transformer are converted to SSM parameters (A, B, C, Δ), then the resulting SSM produces non-divergent outputs during forward pass, because the duality mapping preserves core computational structure.

---

## Variables

- **IV:** Conversion method (duality equations vs random init)
- **DV:** SSM output stability (non-divergent forward pass)
- **CV:** Model architecture (12 layers, 768 dim), input sequences

---

## Success Criteria

- SSM forward pass completes without NaN/Inf for 100% of calibration samples
- Output magnitude within 10x of Transformer output magnitude

---

## Gate Condition

- **Type:** MUST_WORK
- **If Fail:** Duality equations are incorrectly implemented or fundamentally incompatible

---

## Prerequisites

None (this is the first hypothesis in the chain)

---

## Verification Protocol

1. Implement closed-form SSM parameter derivation from attention weights
2. Initialize Mamba-12 using duality equations on BERT-base layer 1
3. Run forward pass on 100 calibration samples (512-2048 tokens)
4. Check for NaN/Inf in outputs; measure output magnitude ratio
5. Pass if all outputs valid and magnitude ratio < 10x

---

## Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LongBench (standard) | Provides 4K-128K context evaluation across multiple task types |
| **Model** | BERT-base → Mamba-12 | Standard sizes (12 layers, 768 dim); public implementations |

---

## Key Assumptions Relevant to h-e1

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Mamba-2 duality conditions approximately hold for pretrained Transformer attention patterns | Mamba-2 shows equivalence for attention with specific structure | Closed-form initialization produces poor starting point |
| A4 | 768-dim SSM state is sufficient to represent 768-dim Transformer hidden states | Mamba-2 uses matching dimensions | May need state expansion factor (2x) |

---

*Context extracted from 02b_verification_plan.md for Phase 2C experiment design*
