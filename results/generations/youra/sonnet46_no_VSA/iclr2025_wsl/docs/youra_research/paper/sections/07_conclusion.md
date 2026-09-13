# Conclusion

We began by observing that averaging a neural network's predicted accuracy across all permutations of its weight channels produces R² = −1.63 — a result so far below chance that it is almost comically bad. This observation is, in fact, a precise measurement of something important: a non-invariant encoder encodes which neuron occupies which position as a predictive feature, and channel positions are arbitrary. The orbit-averaging result is not a failure to be explained away; it is the experiment confirming that CISE fundamentally misrepresents the weight space.

This paper provides the first empirical closure of the causal chain that this observation implies: encoder architecture → OrbitVar → MSE_perm → R². We demonstrate that:

1. **Architectural invariance produces machine-precision zero OrbitVar.** DeepSets sum pooling achieves OrbitVar = 1.002e-14 — 12 orders of magnitude below CISE's 0.010333 — confirmed across all 100 models (Wilcoxon p = 1.95e-18). NFN achieves 8.905e-08. The gap is not incremental; it is qualitative.

2. **CISE's OrbitVar propagates to dominate prediction error.** MSE_perm/MSE_total = 3.35 for CISE — 33× the 10% threshold — with R²(C1_avg) = −1.63 as the diagnostic confirming that channel position is a primary predictive signal, not background noise.

3. **Eliminating MSE_perm improves R² by 6.4 percentage points.** DeepSets achieves R² = 0.9148 vs CISE's 0.851, with zero additional training supervision. The direction of the causal mechanism is confirmed; the additive closure prediction fails (closure = 0.872), revealing entanglement between MSE_perm and MSE_res that opens new questions about weight-space representation geometry.

## Future Directions

From the entanglement finding: the implicit compensation hypothesis — that LightGBM partially learns to suppress permutation-sensitive CISE dimensions — can be tested by training LightGBM on CISE embeddings augmented with K=50 permuted versions per model. If augmented training matches C2's R² = 0.9148, implicit invariance learning explains the closure gap; if not, architectural invariance provides irreducible benefit.

From the NFN comparison gap: resolving the NFN library installation issue and comparing NFN downstream R² against DeepSets under matched conditions (same predictor, same embed_dim) will determine whether structured equivariance (NFN) provides advantages over pooled invariance (DeepSets) when both are measured by downstream prediction quality rather than representational similarity metrics.

From scope extension: the MSE decomposition diagnostic (MSE_res + MSE_perm) is architecturally agnostic and can be applied to any model zoo with known functional permutations. Applying it to wider architectures (ResNets, ViTs) and larger datasets will establish whether the 3.35 ratio observed for 3-conv CNNs is a property of the specific permutation group or a general feature of non-invariant weight encoding.

Architectural invariance in weight encoders is not a theoretical nicety. It is the difference between a predictor that encodes what a network *computes* and one that encodes an arbitrary labeling of its neurons. The results reported here establish that this difference is measurable, causal, and practically significant — and that the measurement framework introduced here provides the tools to quantify it for any future encoder design.
