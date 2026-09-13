# Conclusion

We set out to test whether Mamba-2's theoretical duality between attention and state space models enables practical knowledge transfer from pretrained Transformers. Our findings reveal a clear boundary: duality equations produce numerically stable SSM parameters, but these parameters do not capture attention structure for output-level reconstruction.

## Summary

This work makes three contributions:

1. **First empirical test of Mamba-2 duality for distillation.** We operationalize the SSD framework for attention-to-SSM parameter extraction and validate on BERT-base, finding 100% parameter stability (0% NaN/Inf, 0.11× magnitude ratio).

2. **Separation of validity from fidelity.** Our two-stage verification reveals that duality-derived parameters are valid but reconstruct attention outputs 2.13% worse than random initialization (p < 0.0001, Cohen's d = -4.56)—a consistent negative effect across all 12 BERT layers.

3. **Scope clarification with clear boundary.** We demonstrate that numerical stability does not imply structural preservation, identifying metric mismatch and architecture mismatch as probable causes.

## Future Directions

Our results motivate several promising directions, each grounded in specific experimental findings:

**Testing alternative metrics.** Our h-m1 result used output Frobenius norm, but Mamba-2 duality operates at the matrix level. Testing MOHAWK's matrix alignment loss (CB^T vs. QK^T) could reveal whether duality preserves structure at a different level than we measured.

**Evaluating optimization dynamics.** We tested zero-shot initialization quality. The duality-derived parameters might still provide faster convergence during optimization, even if their zero-shot error is higher. Comparing training trajectories (10-100 steps) would test this hypothesis.

**Extending to compatible architectures.** BERT's multi-head bidirectional attention likely violates SSD conditions. Decoder-only models with causal attention (GPT-2, Pythia) may better satisfy the theoretical requirements, potentially showing different results.

**Developing conversion predictors.** The consistent failure across all 12 layers suggests a systematic mismatch. Identifying which attention characteristics predict successful conversion could enable selective use of duality for compatible attention patterns.

## Closing

Stability is not fidelity. Our work clarifies the scope of Mamba-2 duality for practitioners considering Transformer-to-SSM conversion: expect valid parameters, but verify structural preservation with appropriate metrics. We hope this negative result—with its clear methodology and identified future directions—guides the community toward approaches that work and away from those that do not.
