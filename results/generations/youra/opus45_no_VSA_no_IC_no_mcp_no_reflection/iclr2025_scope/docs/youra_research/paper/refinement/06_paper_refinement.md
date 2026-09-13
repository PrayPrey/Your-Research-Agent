# Testing Mamba-2 Duality for Cross-Architecture Distillation: Stability Without Fidelity

## Abstract

Mamba-2 establishes theoretical equivalence between Transformer attention and state space models, suggesting a principled path for knowledge transfer from pretrained Transformers to efficient SSM architectures. This work tests whether this duality enables practical distillation by extracting SSM parameters directly from BERT attention weights. The experiments reveal that while duality-derived parameters are numerically stable (0% NaN/Inf, 0.11× magnitude ratio relative to Transformer outputs), they reconstruct attention outputs 2.13% worse than random initialization. This negative effect is consistent across all 12 BERT layers (p < 0.0001, Cohen's d = −4.56). Two probable causes are identified: the output-level Frobenius norm metric may not capture what duality preserves, and BERT's multi-head attention may violate the theoretical SSD conditions requiring scalar A matrices and 1-semiseparable causal masks. These results provide empirical scope clarification for Mamba-2 duality: valid parameters do not imply preserved structure. Practitioners considering attention-to-SSM conversion should test reconstruction quality, not just parameter validity.

## 1. Introduction

Mamba-2 establishes theoretical equivalence between Transformer attention and state space models (SSMs), promising a principled path for knowledge transfer from pretrained Transformers to sub-quadratic architectures (Dao and Gu, 2024). This structured state-space duality (SSD) framework suggests that attention mechanisms can be converted to SSM form while preserving computational structure—potentially enabling deployment of BERT-scale models with O(n) inference complexity. This work tests whether this duality enables practical distillation and finds a surprising result: duality-derived SSM parameters are numerically stable but reconstruct attention outputs 2.13% worse than random initialization (p < 0.0001, Cohen's d = −4.56).

This finding is relevant for practitioners considering cross-architecture distillation. If a pretrained Transformer's knowledge could transfer to an efficient SSM via duality equations, edge deployment and long-context inference would become more accessible. However, without understanding the scope and limitations of attention-SSM duality, practitioners may invest compute in approaches that fail at the foundational level.

### The Problem

Transformers achieve state-of-the-art performance across NLP tasks but suffer from quadratic attention complexity, limiting deployment on resource-constrained devices and long-context applications. Sub-quadratic alternatives—Mamba (Gu and Dao, 2023), RWKV (Peng et al., 2023), RetNet (Sun et al., 2023)—offer linear-time inference but typically require training from scratch, forfeiting pretrained knowledge.

No validated methodology exists for transferring pretrained Transformer knowledge to SSM architectures while preserving the learned attention structure. Same-architecture distillation (e.g., DistilBERT; Sanh et al., 2019) succeeds but cannot bridge architectural families. Naive output-matching knowledge distillation treats the student as a black box, ignoring the internal computational structure that attention encodes.

The gap addressed here is the empirical validation of Mamba-2 duality for practical distillation. While Mamba-2 proves theoretical equivalence under specific conditions (scalar A matrix, 1-semiseparable causal masks), real attention—multi-head with learned position embeddings—may not satisfy these conditions. Whether duality equations produce SSM parameters that capture meaningful attention structure has not been previously tested.

### Key Insight

The central finding is that numerical stability does not imply structural fidelity. The duality-to-distillation pipeline is decomposed into two verification stages: (1) parameter validity—do duality equations produce non-divergent SSM parameters?—and (2) structural preservation—do these parameters reconstruct attention outputs better than random initialization?

The first stage passes: 100% of samples produce stable SSM outputs with 0.11× magnitude ratio relative to Transformer outputs. The second stage fails: duality initialization is consistently worse than random across all 12 BERT layers. This separation identifies where duality breaks down—at output-level structural fidelity, not at parameter-level validity.

### Contributions

1. **First empirical test of Mamba-2 duality for distillation.** The SSD framework is operationalized for attention-to-SSM parameter conversion and validated on BERT-base, providing evidence about duality's practical scope.

2. **Separation of validity from fidelity.** Two-stage verification (h-e1: stability, h-m1: reconstruction) isolates the failure point, showing that valid parameters do not imply preserved structure.

3. **Negative result with clear boundary.** Duality initialization produces 2.13% worse reconstruction error than random (p < 0.0001), with consistent negative effects across all 12 layers. This clarifies when duality should not be expected to provide zero-shot output alignment.

4. **Identification of probable causes.** Metric mismatch (output Frobenius norm vs. MOHAWK matrix alignment) and architecture mismatch (multi-head vs. SSD assumptions) are identified as candidates for follow-up investigation.

## 2. Related Work

This work is positioned at the intersection of three research areas: knowledge distillation, sub-quadratic sequence models, and attention-SSM theoretical connections.

### Knowledge Distillation

Knowledge distillation transfers knowledge from a large teacher model to a smaller student (Hinton et al., 2015). DistilBERT (Sanh et al., 2019) achieves 97% of BERT's performance with 40% fewer parameters using soft-target distillation combined with cosine embedding loss. TinyBERT (Jiao et al., 2020) extends this with layer-wise intermediate matching.

These methods operate within the same architecture family (Transformer to Transformer). They cannot bridge to fundamentally different computational primitives like SSMs, which use recurrent state evolution rather than pairwise attention. Cross-architecture distillation requires understanding how to map computational structure, not just outputs.

### Sub-Quadratic Sequence Models

State space models offer O(n) inference complexity through recurrent computation. Mamba (Gu and Dao, 2023) introduces selective scan, achieving competitive performance with Transformers on standard benchmarks. RWKV (Peng et al., 2023) combines linear attention with exponential decay. RetNet (Sun et al., 2023) proposes retention mechanisms with parallel training and recurrent inference.

These models are typically trained from scratch or initialized randomly. While they achieve strong performance when trained sufficiently, they cannot leverage existing pretrained Transformer knowledge without additional methodology.

### Attention-SSM Theoretical Connections

Mamba-2 (Dao and Gu, 2024) proves a duality: under the structured state-space duality (SSD) framework, linear attention is theoretically equivalent to a state space model with specific parameterization. This suggests that attention weights can be converted to SSM parameters via closed-form equations.

MOHAWK (Waleffe et al., 2024) operationalizes this insight for distillation, proposing a three-stage approach: (1) matrix alignment matching CB^T to QK^T, (2) hidden state alignment, (3) soft target distillation. Their Stage 1 uses matrix-level alignment rather than output-level reconstruction.

Mamba-2 proves duality under restrictive conditions (scalar-times-identity A matrix, 1-semiseparable causal masks). Real Transformer attention—multi-head with learned position embeddings—may violate these conditions. Neither Mamba-2 nor MOHAWK directly tests whether duality-derived parameters reconstruct attention outputs better than random initialization.

This work directly tests the foundational assumption: does duality-based initialization provide a better starting point than random? Unlike MOHAWK's matrix alignment (CB^T vs. QK^T), output Frobenius norm is used to measure whether SSM outputs approximate attention outputs. This output-level test reveals that duality produces valid parameters (0% NaN/Inf, 0.11× magnitude) but fails at structural fidelity (2.13% worse than random).

## 3. Method

### Overview

The methodology tests whether Mamba-2 duality equations can initialize SSM parameters from BERT attention weights such that:

1. **Stage 1 (Existence):** The derived parameters produce stable, non-divergent SSM outputs.
2. **Stage 2 (Mechanism):** The derived parameters reconstruct attention outputs better than random initialization.

### Duality-Based Parameter Extraction

Closed-form SSM parameter derivation from BERT attention weights is implemented following the Mamba-2 SSD framework. For each attention layer with query, key, and value projections (W_Q, W_K, W_V ∈ ℝ^{768×768}):

**A Matrix (State Dynamics):** QK^T = W_Q · W_K^T is computed and its principal components are extracted via SVD. Negative absolute values ensure stability (negative eigenvalues prevent divergence).

**B and C Matrices:** B and C are derived from the SVD components, normalized for numerical stability.

**D and Δ:** Skip connection D = 0.1 and discretization step Δ = 1/√768.

### Stability Validation (h-e1)

Parameter stability is validated by running SSM forward passes on calibration data, checking for NaN/Inf and measuring magnitude ratio relative to Transformer outputs. The threshold for acceptable magnitude ratio is set at 10×.

### Reconstruction Error Comparison (h-m1)

Duality initialization is compared against random initialization using output Frobenius norm:

‖SSM output − Attention output‖_F

For random initialization, A is sampled from N(0, 1/√d_state), B and C use Xavier uniform initialization, D is set to zeros, and Δ = 0.1. The same random seed (42) ensures reproducibility.

## 4. Experimental Setup

### Research Questions

**RQ1 (Existence):** Do duality equations produce valid, non-divergent SSM parameters?

**RQ2 (Mechanism):** Does duality-based initialization provide lower reconstruction error than random?

### Dataset

WikiText-103 (Merity et al., 2017) validation split: 100 samples for stability testing (h-e1), 500 samples for reconstruction comparison (h-m1), with 64–512 tokens per sample.

### Models

**Teacher:** BERT-base-uncased (12 layers, 768 hidden dimension, 12 attention heads, approximately 110M parameters)

**Student:** SSM with d_state = 64, d_model = 768

### Evaluation Metrics

| Hypothesis | Metric | Threshold |
|------------|--------|-----------|
| h-e1 | NaN/Inf Rate | 0% |
| h-e1 | Magnitude Ratio | < 10× |
| h-m1 | Reconstruction Error | Duality < Random |
| h-m1 | P-value | < 0.05 |

### Statistical Analysis

Paired t-tests compare duality and random initialization errors across the 500 samples. Cohen's d quantifies effect size. Per-layer analysis is conducted across all 12 BERT layers.

## 5. Results

### 5.1 h-e1: Parameter Validity (PASS)

| Metric | Threshold | Observed | Status |
|--------|-----------|----------|--------|
| NaN/Inf Rate | 0% | 0.0% | PASS |
| Magnitude Ratio | < 10× | 0.11× | PASS |

Duality-derived parameters are numerically stable across all 100 test samples. The magnitude ratio of 0.11× indicates conservative parameter scales relative to attention outputs.

### 5.2 h-m1: Reconstruction Error (FAIL)

| Metric | Value |
|--------|-------|
| Mean Duality Error | 91.45 |
| Mean Random Error | 89.54 |
| Error Reduction | −2.13% (worse) |
| P-value | < 0.0001 |
| Cohen's d | −4.56 (large negative) |

Duality initialization produces 2.13% higher reconstruction error than random initialization. The effect is statistically significant (p < 0.0001) with a large negative effect size (Cohen's d = −4.56).

### 5.3 Per-Layer Analysis

| Layer | Duality Error | Random Error | Reduction | Cohen's d |
|-------|---------------|--------------|-----------|-----------|
| 0 | 79.75 | 77.74 | −2.58% | −5.02 |
| 1 | 93.98 | 92.16 | −1.98% | −5.50 |
| 2 | 108.35 | 106.70 | −1.55% | −5.19 |
| 3 | 104.67 | 103.04 | −1.57% | −5.97 |
| 4 | 98.18 | 96.35 | −1.89% | −4.15 |
| 5 | 96.58 | 94.85 | −1.82% | −5.92 |
| 6 | 96.29 | 94.53 | −1.86% | −5.12 |
| 7 | 91.16 | 89.18 | −2.22% | −4.71 |
| 8 | 84.44 | 82.31 | −2.58% | −5.85 |
| 9 | 87.10 | 85.06 | −2.40% | −5.38 |
| 10 | 79.79 | 77.64 | −2.77% | −5.31 |
| 11 | 77.11 | 74.91 | −2.94% | −4.84 |

Duality initialization is consistently worse across all 12 BERT layers, with Cohen's d ranging from −4.15 to −5.97 (all large negative effects). Layer 11 shows the largest degradation (−2.94%), while Layer 2 shows the smallest (−1.55%).

### 5.4 Causal Chain Verification

| Step | Description | Status |
|------|-------------|--------|
| 1 | Duality equations → valid SSM parameters | VERIFIED |
| 2 | Duality parameters → lower reconstruction error | FALSIFIED |
| 3 | Lower error → better task performance | BLOCKED |

The causal chain breaks at Step 2. While duality equations produce valid parameters, these parameters do not capture attention structure for output-level reconstruction.

## 6. Discussion

### Why Does Duality Fail at Reconstruction?

Three hypotheses explain the negative result:

**1. Metric Mismatch:** The evaluation uses output Frobenius norm. MOHAWK uses matrix alignment (CB^T vs. QK^T). The duality may correctly preserve matrix structure while producing outputs that diverge at the activation level. This is considered the most plausible explanation.

**2. Architecture Mismatch:** BERT attention violates SSD conditions. Mamba-2 duality is proven for scalar-times-identity A matrices and 1-semiseparable causal masks. BERT uses multi-head attention (12 heads), learned position embeddings, and bidirectional context. These architectural differences may prevent exact duality from holding.

**3. Scale Mismatch:** The 0.11× magnitude ratio suggests conservative initialization. The duality-derived parameters may have correct relative structure but incorrect absolute scale for matching attention outputs without optimization.

### Implications for Cross-Architecture Distillation

The results do not invalidate cross-architecture distillation generally. They clarify that:

1. Zero-shot duality conversion does not provide output alignment.
2. Practitioners should not assume valid parameters imply structural preservation.
3. Alternative metrics (matrix alignment) or optimization may be necessary.

The duality equations may still provide benefits for optimization dynamics (faster convergence, better local minima) even if zero-shot reconstruction is worse. This remains untested.

### Limitations

1. **Metric scope:** Only output Frobenius norm was tested, not MOHAWK's matrix alignment (CB^T vs. QK^T). Results may differ under alternative metrics.

2. **Zero-shot only:** No optimization phase was included. Duality initialization may provide benefits during training that are not visible in zero-shot evaluation.

3. **Single architecture:** Only BERT-base (encoder-only, 12 layers) was tested. Decoder-only models (GPT-style) or larger models may behave differently.

4. **Single dataset:** Only WikiText-103 was used for calibration. Other domains may yield different results.

### Broader Impact

This negative result provides value by preventing wasted compute on approaches that fail at the foundational level. The two-stage verification methodology (validity then fidelity) provides a template for rigorous validation of cross-architecture conversion methods.

## 7. Conclusion

This work set out to test whether Mamba-2's theoretical duality between attention and SSM enables practical knowledge transfer. The findings: duality equations produce numerically stable SSM parameters (0% NaN/Inf, 0.11× magnitude ratio), but these parameters do not capture attention structure for output-level reconstruction (2.13% worse than random, p < 0.0001, Cohen's d = −4.56).

**Contributions:** (1) First empirical test of Mamba-2 duality for distillation. (2) Separation of validity from fidelity through two-stage verification. (3) Scope clarification with clear boundary conditions.

**Future Directions:** (1) Test alternative metrics (matrix alignment CB^T vs. QK^T). (2) Evaluate optimization dynamics with duality vs. random initialization. (3) Extend to architectures that more closely satisfy SSD conditions.

Stability is not fidelity. Valid SSM parameters extracted via duality equations do not guarantee output alignment with the source attention mechanism. Practitioners considering Transformer-to-SSM conversion should verify reconstruction quality, not just parameter validity.

## References

Bai, Y., Lv, X., Zhang, J., Lyu, H., Tang, J., et al. (2023). LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding. arXiv:2308.14508.

Dao, T., & Gu, A. (2024). Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality. arXiv:2405.21060.

Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL-HLT.

Gu, A., & Dao, T. (2023). Mamba: Linear-Time Sequence Modeling with Selective State Spaces. arXiv:2312.00752.

Hinton, G., Vinyals, O., & Dean, J. (2015). Distilling the Knowledge in a Neural Network. NIPS Deep Learning Workshop.

Jiao, X., Yin, Y., Shang, L., Jiang, X., Chen, X., et al. (2020). TinyBERT: Distilling BERT for Natural Language Understanding. arXiv:1909.10351.

Merity, S., Xiong, C., Bradbury, J., & Socher, R. (2017). Pointer Sentinel Mixture Models. arXiv:1609.07843.

Peng, B., Alcaide, E., Anthony, Q., Albalak, A., Arcadinho, S., et al. (2023). RWKV: Reinventing RNNs for the Transformer Era. arXiv:2305.13048.

Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter. arXiv:1910.01108.

Sun, Y., Dong, L., Huang, S., Ma, S., Xia, Y., et al. (2023). Retentive Network: A Successor to Transformer for Large Language Models. arXiv:2307.08621.

Waleffe, R., Byeon, W., Riber, D., Arber, B., Guha, A., et al. (2024). An Empirical Study of Mamba-based Language Models. arXiv:2408.10189.
