# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-12
**Main Hypothesis:** Quotient-Level Cross-Architecture Canonicalization
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under conditions where neural network architectures (CNNs, Transformers, RNNs) solve the same task via exchangeable computations, if we apply architecture-specific encoders that project model weights into a shared K-dimensional quotient space, then a finite-dimensional quotient space will exist that captures task-relevant computational structure across architectures, as measured by reconstruction error <10%, frozen-K generalization to unseen architectures (R_RNN<10%), and kernel robustness (≥90% of permutations preserve outputs with D<0.01).

### Type
EXISTENCE

### Rationale
This hypothesis validates the foundational claim that weight-space structure can be factorized into architecture-independent representations. Success proves that task-relevant information exists in a lower-dimensional manifold independent of architectural coordinate systems, establishing the existence precondition for all subsequent mechanism tests.

---

## Verification Protocol

### Conceptual Test
1. Train Deep Sets encoder with equivariance loss on CNN+Transformer subset from ModelZoo-14K (70% train, 15% val, 15% test split).
2. Determine minimal K where reconstruction error <10% threshold via binary search over K∈{16, 32, 64, 128}.
3. Apply frozen K to RNN test set without retraining, measure reconstruction error R_RNN.
4. Test kernel robustness via 1000 random neuron permutations per model, measure functional preservation (output divergence D<0.01).
5. Validate that ≥90% of permutations preserve model outputs on both IID (ImageNet) and OOD (ImageNet-V2) test sets.

### Success Criteria
**Primary:** Reconstruction error <10% at K=64, Frozen-K generalization R_RNN<10%, Kernel robustness ≥90% (both IID and OOD)

**Secondary:** Cross-seed consistency (Procrustes <0.10 between quotient spaces learned from different seeds), OOD robustness matches IID (difference <5pp)

### Variables
- **Independent Variable:** Architecture Family (CNN/Transformer/RNN), Number of Slots K (16/32/64), Model Weights M (14,000 pretrained models)
- **Dependent Variable:** Reconstruction Error, Frozen-K Generalization (R_RNN), Kernel Robustness (%)
- **Controlled Variables:** Model Size (10M-100M parameters), Training Dataset (ImageNet), Random Seed (3 seeds)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** ModelZoo-14K
- **Type:** standard
- **Source:** Hugging Face model hub (14,000 pretrained models)
- **Path:** https://huggingface.co/
- **Hypothesis Fit:** Provides heterogeneous model population (CNNs, Transformers, RNNs) at scale required to test cross-architecture canonicalization. 70% train / 15% val / 15% test split enables robust validation.

### Selected Model
- **Name:** Slot-Equivariant Encoder
- **Type:** Set-based encoder with Deep Sets backbone + equivariance loss
- **Source:** Custom implementation based on Zaheer et al. 2017 Deep Sets
- **Hypothesis Fit:** Deep Sets provides permutation-invariant baseline; adding explicit equivariance loss L_equiv = ||E_a(g·M) - ρ(π_a(g))E_a(M)||² enforces quotient-level structure. Weak task supervision (0.1 weight) anchors space.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| DeepSets | ~70% probe transfer, ~40% zero-shot equivariance | ModelZoo-14K |
| Git Re-Basin | Weight-space alignment within single architecture | CIFAR-10/100 models |
| NFN (Zhou et al. 2023) | +17% INR classification | Homogeneous INR zoos |
| Function-Space Embedding | Baseline via output logits | ImageNet 10K samples |

### Baseline Performance
- DeepSets: ~70% probe transfer, ~40% zero-shot equivariance on ModelZoo-14K
- NFN: +17% improvement on INR classification (homogeneous populations only)

### Gap Analysis
Existing methods operate within single architecture families or use unstructured embeddings. No prior work demonstrates scalable equivariant processing across heterogeneous families (CNN/Transformer/RNN) with geometric validation of shared canonical coordinates.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** H-M cannot proceed (quotient space does not exist)

**Failure Response:**
- IF frozen-K fails (R_RNN>25%): Quotient is architecture-specific → PIVOT to per-family encoders, redesign mechanism
- IF kernel robustness fails (<70%): Permutation symmetries not captured → EXPLORE alternative slot encodings (attention-based, graph neural networks)
- IF reconstruction passes but frozen-K fails: Dimensional stability violated → ABANDON shared manifold hypothesis

---

## Dependency Context

### Relationship to Other Hypotheses
This is the foundational EXISTENCE hypothesis. If H-E1 fails, hypothesis H-M (Equivariance Mechanism) cannot proceed as it depends on the existence of a quotient space established by H-E1.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** Will be updated by Phase 2C
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: /home/anonymous/YouRA_results_new_4_sonnet45_no_reflection/TEST_wsl_sonnet45_no_reflection_2/docs/youra_research/20260512_wsl/h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
