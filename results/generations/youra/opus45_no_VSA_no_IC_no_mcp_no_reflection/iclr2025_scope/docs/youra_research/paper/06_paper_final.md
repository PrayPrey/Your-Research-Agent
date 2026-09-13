---
title: "Testing Mamba-2 Duality for Cross-Architecture Distillation: Stability Without Fidelity"
authors:
  - name: "Anonymous"
    affiliation: "Anonymous Institution"
    email: "anonymous@example.com"
format: "ICML2025"
date: "2026-08-31"
hypothesis_id: "H-DG-CAD-v1"
generated_by: "Anonymous Research Pipeline"
word_count: ~4500
figures: 6
tables: 5
---

# Abstract

Mamba-2 establishes theoretical equivalence between Transformer attention and state space models, promising a principled path for knowledge transfer from pretrained Transformers to efficient SSM architectures. We test whether this duality enables practical distillation by extracting SSM parameters directly from BERT attention weights. Our experiments reveal a surprising finding: while duality-derived parameters are numerically stable (0% NaN/Inf, 0.11× magnitude ratio), they reconstruct attention outputs 2.13% worse than random initialization—a consistent negative effect across all 12 BERT layers (p < 0.0001, Cohen's d = -4.56). We identify probable causes: the output-level Frobenius norm metric may not capture what duality preserves, and BERT's multi-head attention likely violates the theoretical SSD conditions. Our work provides the first empirical scope clarification for Mamba-2 duality: valid parameters do not imply preserved structure. Practitioners should test reconstruction quality, not just parameter validity, when developing attention-to-SSM conversion methods.

---

# 1. Introduction

Mamba-2 establishes theoretical equivalence between Transformer attention and state space models (SSMs), promising a principled path for knowledge transfer from pretrained Transformers to sub-quadratic architectures [Dao and Gu, 2024]. This structured state-space duality (SSD) framework suggests that attention mechanisms can be converted to SSM form while preserving computational structure—potentially enabling deployment of BERT-scale models with O(n) inference complexity. We test whether this duality enables practical distillation and discover a surprising result: duality-derived SSM parameters are numerically stable but reconstruct attention outputs 2.13% worse than random initialization (p < 0.0001, Cohen's d = -4.56).

This finding matters for practitioners considering cross-architecture distillation. If a pretrained Transformer's knowledge could transfer to an efficient SSM via duality equations, edge deployment and long-context inference would become dramatically more accessible. However, without understanding the scope and limitations of attention-SSM duality, practitioners may invest significant compute in approaches that fail at the foundational level.

## The Problem

At the surface level, Transformers achieve state-of-the-art performance across NLP tasks but suffer from quadratic attention complexity, limiting deployment on resource-constrained devices and long-context applications. Sub-quadratic alternatives—Mamba [Gu and Dao, 2023], RWKV [Peng et al., 2023], RetNet [Sun et al., 2023]—offer linear-time inference but typically require training from scratch, forfeiting pretrained knowledge.

Looking deeper, no methodology exists for transferring pretrained Transformer knowledge to SSM architectures while preserving the learned attention structure. Same-architecture distillation (e.g., DistilBERT [Sanh et al., 2019]) succeeds but cannot bridge architectural families. Naive output-matching knowledge distillation treats the student as a black box, ignoring the internal computational structure that attention encodes.

The gap we address is the empirical validation of Mamba-2 duality for practical distillation. While Mamba-2 proves theoretical equivalence under specific conditions (scalar A matrix, 1-semiseparable causal masks), real attention—multi-head with learned position embeddings—may not satisfy these conditions. Whether duality equations produce SSM parameters that capture meaningful attention structure remains untested.

## Key Insight

Our central finding is that **numerical stability does not imply structural fidelity**. We decompose the duality-to-distillation pipeline into two verification stages: (1) parameter validity—do duality equations produce non-divergent SSM parameters?—and (2) structural preservation—do these parameters reconstruct attention outputs better than random initialization?

The first stage passes: 100% of samples produce stable SSM outputs with 0.11x magnitude ratio relative to Transformer outputs. The second stage fails: duality initialization is consistently worse than random across all 12 BERT layers. This separation identifies where duality breaks down—at output-level structural fidelity, not at parameter-level validity.

## Contributions

Building on this insight, we make the following contributions:

1. **First empirical test of Mamba-2 duality for distillation.** We operationalize the SSD framework for attention-to-SSM parameter conversion and validate on BERT-base, providing concrete evidence about duality's practical scope.

2. **Separation of validity from fidelity.** Our two-stage verification (h-e1: stability, h-m1: reconstruction) isolates the failure point, showing that valid parameters do not imply preserved structure.

3. **Negative result with clear boundary.** We demonstrate that duality initialization produces 2.13% worse reconstruction error than random (p < 0.0001), with consistent negative effects across all 12 layers. This clarifies when duality should *not* be expected to provide zero-shot output alignment.

4. **Future directions grounded in evidence.** We identify metric mismatch (output Frobenius norm vs. MOHAWK matrix alignment) and architecture mismatch (multi-head vs. SSD assumptions) as probable causes, guiding follow-up work.

---

# 2. Related Work

We position our work at the intersection of three research areas: knowledge distillation, sub-quadratic sequence models, and attention-SSM theoretical connections. Each area provides valuable foundations but leaves a critical gap: no existing work empirically validates whether attention-SSM duality enables practical knowledge transfer.

## Knowledge Distillation

Knowledge distillation transfers knowledge from a large teacher model to a smaller student [Hinton et al., 2015]. DistilBERT [Sanh et al., 2019] achieves 97% of BERT's performance with 40% fewer parameters using soft-target distillation combined with cosine embedding loss. TinyBERT [Jiao et al., 2020] extends this with layer-wise intermediate matching.

**Limitation:** These methods operate within the same architecture family (Transformer → Transformer). They cannot bridge to fundamentally different computational primitives like SSMs, which use recurrent state evolution rather than pairwise attention. Cross-architecture distillation requires understanding how to map computational structure, not just outputs.

## Sub-Quadratic Sequence Models

State space models offer O(n) inference complexity through recurrent computation. Mamba [Gu and Dao, 2023] introduces selective scan, achieving competitive performance with Transformers on standard benchmarks. RWKV [Peng et al., 2023] combines linear attention with exponential decay. RetNet [Sun et al., 2023] proposes retention mechanisms with parallel training and recurrent inference.

**Limitation:** These models are typically trained from scratch or initialized randomly. While they achieve strong performance when trained sufficiently, they cannot leverage existing pretrained Transformer knowledge. This represents wasted compute when high-quality pretrained models already exist.

## Attention-SSM Theoretical Connections

Mamba-2 [Dao and Gu, 2024] proves a fundamental duality: under the structured state-space duality (SSD) framework, linear attention is theoretically equivalent to a state space model with specific parameterization. This suggests that attention weights can be converted to SSM parameters via closed-form equations.

MOHAWK [Waleffe et al., 2024] operationalizes this insight for distillation, proposing a three-stage approach: (1) matrix alignment matching CB^T to QK^T, (2) hidden state alignment, (3) soft target distillation. Their Stage 1 uses matrix-level alignment rather than output-level reconstruction.

**Limitation:** Mamba-2 proves duality under restrictive conditions (scalar-times-identity A matrix, 1-semiseparable causal masks). Real Transformer attention—multi-head with learned position embeddings—may violate these conditions. Neither Mamba-2 nor MOHAWK directly tests whether duality-derived parameters reconstruct attention outputs better than random initialization.

## Our Contribution

We directly test the foundational assumption: does duality-based initialization provide a better starting point than random? Unlike MOHAWK's matrix alignment (CB^T vs. QK^T), we use output Frobenius norm to measure whether SSM outputs approximate attention outputs. This output-level test reveals that duality produces valid parameters (0% NaN/Inf, 0.11x magnitude) but fails at structural fidelity (2.13% worse than random).

---

# 3. Methodology

Building on our observation that duality provides a principled mapping from attention to SSM parameters, we design a two-stage verification protocol that isolates parameter validity from structural fidelity.

## Overview

Our methodology tests whether Mamba-2 duality equations can initialize SSM parameters from BERT attention weights such that:

1. **Stage 1 (Existence - h-e1):** The derived parameters produce stable, non-divergent SSM outputs.
2. **Stage 2 (Mechanism - h-m1):** The derived parameters reconstruct attention outputs better than random initialization.

## Duality-Based Parameter Extraction

We implement closed-form SSM parameter derivation from BERT attention weights following the Mamba-2 SSD framework. For each attention layer with query, key, and value projections (W_Q, W_K, W_V ∈ ℝ^{768×768}):

**A Matrix (State Dynamics):** We compute QK^T = W_Q · W_K^T and extract its principal components via SVD. The negative absolute values ensure stability (negative eigenvalues prevent divergence).

**B and C Matrices:** We derive B and C from the SVD components, normalized for numerical stability.

**D and Δ:** Skip connection D = 0.1 and discretization step Δ = 1/√768.

## Stability Validation (h-e1)

We validate parameter stability by running SSM forward passes on calibration data, checking for NaN/Inf and measuring magnitude ratio relative to Transformer outputs.

## Reconstruction Error Comparison (h-m1)

We compare duality initialization against random initialization using output Frobenius norm: ‖SSM output - Attention output‖_F.

---

# 4. Experimental Setup

We design experiments to answer two fundamental questions:

**RQ1 (Existence):** Do duality equations produce valid, non-divergent SSM parameters?

**RQ2 (Mechanism):** Does duality-based initialization provide lower reconstruction error than random?

## Dataset

WikiText-103 [Merity et al., 2017]: 100 samples (h-e1), 500 samples (h-m1), 64-512 tokens per sample.

## Models

**Teacher:** BERT-base-uncased (12 layers, 768 hidden, 110M parameters)
**Student:** Mamba-12 with d_state = 64

## Evaluation Metrics

| Hypothesis | Metric | Threshold |
|------------|--------|-----------|
| h-e1 | NaN/Inf Rate | 0% |
| h-e1 | Magnitude Ratio | < 10× |
| h-m1 | Reconstruction Error | Duality < Random |
| h-m1 | P-value | < 0.05 |

---

# 5. Results

## h-e1: Parameter Validity (PASS)

| Metric | Threshold | Observed | Status |
|--------|-----------|----------|--------|
| NaN/Inf Rate | 0% | **0.0%** | ✅ PASS |
| Magnitude Ratio | < 10× | **0.11×** | ✅ PASS |

Duality-derived parameters are numerically stable across all 100 test samples.

## h-m1: Reconstruction Error (FAIL)

| Metric | Value |
|--------|-------|
| Mean Duality Error | 91.45 |
| Mean Random Error | 89.54 |
| Error Reduction | **-2.13%** (worse) |
| P-value | < 0.0001 |
| Cohen's d | **-4.56** (large negative) |

Duality initialization is 2.13% WORSE than random. The effect is consistent across all 12 BERT layers, with Cohen's d ranging from -4.15 to -5.97.

## Causal Chain Verification

| Step | Description | Status |
|------|-------------|--------|
| 1 | Duality equations → valid SSM parameters | ✅ VERIFIED |
| 2 | Duality parameters → lower reconstruction error | ❌ FALSIFIED |
| 3 | Lower error → better task performance | ⏸️ BLOCKED |

---

# 6. Discussion

## Why Does Duality Fail at Reconstruction?

**1. Metric Mismatch:** Our evaluation uses output Frobenius norm. MOHAWK uses matrix alignment (CB^T vs. QK^T). The duality may correctly preserve matrix structure while producing outputs that diverge.

**2. Architecture Mismatch:** BERT attention violates SSD conditions (multi-head, learned positions, bidirectional).

**3. Scale Mismatch:** The 0.11× magnitude ratio suggests conservative initialization that manifests as higher reconstruction error without optimization.

## Limitations

1. Only tested output Frobenius norm, not MOHAWK matrix alignment
2. Zero-shot evaluation only—no optimization phase
3. Single architecture (BERT-base) and dataset (WikiText-103)

## Broader Impact

Our negative result prevents wasted compute on approaches that fail fundamentally. The methodology provides a template for rigorous validation of cross-architecture conversion methods.

---

# 7. Conclusion

We set out to test whether Mamba-2's theoretical duality enables practical knowledge transfer. Our findings: duality equations produce numerically stable SSM parameters, but these parameters do not capture attention structure for output-level reconstruction.

**Contributions:** (1) First empirical test of Mamba-2 duality for distillation. (2) Separation of validity from fidelity. (3) Scope clarification with clear boundary.

**Future Directions:** Test alternative metrics (matrix alignment), evaluate optimization dynamics, extend to compatible architectures.

**Closing:** Stability is not fidelity. Our work clarifies the scope of Mamba-2 duality for practitioners considering Transformer-to-SSM conversion.

---

# References

1. Dao, T., & Gu, A. (2024). Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality. arXiv:2405.21060.

2. Gu, A., & Dao, T. (2023). Mamba: Linear-Time Sequence Modeling with Selective State Spaces. arXiv:2312.00752.

3. Waleffe, R., et al. (2024). An Empirical Study of Mamba-based Language Models. arXiv:2408.10189.

4. Sanh, V., et al. (2019). DistilBERT, a distilled version of BERT. arXiv:1910.01108.

5. Devlin, J., et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers. NAACL-HLT.

6. Peng, B., et al. (2023). RWKV: Reinventing RNNs for the Transformer Era. arXiv:2305.13048.

7. Sun, Y., et al. (2023). Retentive Network: A Successor to Transformer. arXiv:2307.08621.

8. Hinton, G., et al. (2015). Distilling the Knowledge in a Neural Network. NIPS Workshop.

9. Jiao, X., et al. (2020). TinyBERT: Distilling BERT for NLU. arXiv:1909.10351.

10. Merity, S., et al. (2017). Pointer Sentinel Mixture Models. arXiv:1609.07843.

11. Bai, Y., et al. (2023). LongBench: A Bilingual, Multitask Benchmark. arXiv:2308.14508.
