# Discussion

Our experiments reveal that Mamba-2 duality equations produce valid SSM parameters but fail to preserve attention structure at the output level. We discuss the implications of this finding, propose explanations, and acknowledge limitations.

## Interpretation of Results

### Why Does Duality Fail at Reconstruction?

We identify three probable explanations for the negative result:

**1. Metric Mismatch (Most Likely)**

Our evaluation uses output Frobenius norm: ‖SSM_output - Attention_output‖_F. However, the Mamba-2 duality framework establishes equivalence at the *matrix* level, not the output level. MOHAWK [Waleffe et al., 2024] uses matrix alignment (CB^T vs. QK^T) for its Stage 1 loss.

The duality equations may correctly preserve matrix structure while producing outputs that diverge in Frobenius distance. Testing with MOHAWK's matrix alignment metric could show different results.

**2. Architecture Mismatch**

Mamba-2 SSD duality is proven under specific conditions:
- Scalar-times-identity A matrix
- 1-semiseparable causal masks
- Single-head attention

BERT attention violates all three:
- Multi-head attention (12 heads)
- Learned position embeddings (not 1-semiseparable)
- Full bidirectional attention (not causal)

The duality equations may not hold for BERT's attention structure, causing the mapping to produce valid but structurally misaligned parameters.

**3. Scale Mismatch**

The duality-derived parameters may have correct *relative structure* but incorrect *absolute scale*. The 0.11× magnitude ratio suggests conservative initialization. Without optimization, this scale mismatch manifests as higher reconstruction error.

### What This Means for Practitioners

**Do not expect zero-shot output alignment from duality initialization.** Our results show that simply extracting SSM parameters via duality equations does not produce an SSM that approximates attention outputs better than random initialization.

**Duality may still benefit optimization.** We tested zero-shot reconstruction (no training). The duality-derived parameters might still provide faster convergence or better final performance *after* optimization. This remains an open question for future work.

**Test reconstruction quality, not just parameter validity.** Our two-stage verification reveals that valid parameters ≠ preserved structure. Practitioners developing attention-to-SSM conversion methods should include reconstruction error comparisons in their validation.

## Limitations

### Output-Level Metric Only

We evaluate using output Frobenius norm. Matrix-level alignment (CB^T vs. QK^T, as in MOHAWK Stage 1) may show different properties. This metric choice is a limitation of our study design.

**Why acceptable:** Output alignment is a reasonable interpretation of "reconstruction error." Matrix alignment is noted as future work.

**Future mitigation:** Implement MOHAWK Stage 1 loss and rerun h-m1.

### Zero-Shot Evaluation Only

We test initialization quality without any optimization. The duality-derived parameters might converge faster or to better optima despite worse zero-shot error.

**Why acceptable:** Zero-shot evaluation directly tests the initialization hypothesis. If duality provides a "better starting point," it should show some advantage at step 0.

**Future mitigation:** Compare convergence trajectories with 10-100 optimization steps.

### Single Architecture and Dataset

We test only BERT-base on WikiText-103. Results may differ for:
- Decoder-only models (GPT-style)
- Causal attention (which better matches SSD assumptions)
- Other domains

**Why acceptable:** BERT-base is a standard benchmark. Our methodology establishes a template for broader testing.

**Future mitigation:** Extend to GPT-2, Pythia, and other architectures.

## Theoretical Contributions

Despite the negative empirical result, our work makes theoretical contributions:

1. **Scope clarification for Mamba-2 duality:** We demonstrate that the duality framework produces valid parameters but does not guarantee output-level structural preservation. This identifies the boundary of the theoretical result.

2. **Separation of validity from fidelity:** Our two-stage verification (existence vs. mechanism) provides a methodology for testing architecture conversion approaches.

3. **Identification of future directions:** The competing explanations (metric mismatch, architecture mismatch) provide concrete hypotheses for follow-up work.

## Broader Impact

### Positive Impacts

Our negative result prevents wasted compute. Practitioners considering duality-based initialization for Transformer-to-SSM conversion can now make informed decisions rather than investing in an approach that fails at the foundational level.

The methodology (two-stage verification, claim-evidence separation) provides a template for rigorous validation of cross-architecture conversion methods.

### Potential Concerns

Publishing a negative result about a prominent theoretical framework (Mamba-2 SSD) might discourage exploration of duality-based approaches. We emphasize that our result is *scope clarification*, not *invalidation*: duality may work under different metrics, with optimization, or for architectures that better satisfy SSD conditions.

### Mitigation

We present our findings as boundary identification, not definitive rejection. The future work section explicitly identifies promising directions for extending duality-based distillation.
