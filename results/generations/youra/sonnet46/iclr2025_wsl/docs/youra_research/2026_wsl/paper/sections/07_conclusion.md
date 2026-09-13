# Conclusion

We opened with a striking fragility: a neural network trained to predict how well another
network generalizes loses 89% of its predictive correlation when the target network's neurons
are randomly shuffled. This is not a dataset artifact or a benchmark quirk — it is a structural
misalignment between the encoder's representational assumptions and the symmetry structure of
what it encodes. Flat-MLP encoders treat neuron position as meaningful signal; fully-connected
networks treat neuron position as an arbitrary artifact. The two are fundamentally incompatible
for robust weight-space analysis.

In this work, we addressed this misalignment by bridging two previously disconnected research
lines: the Neural Functional Transformer (NFT, equivariant architecture for FC-MLP weight
spaces) and the Unterthiner model zoo benchmark (weight-space property prediction). We conducted
the first controlled empirical comparison between these lines, with three main results.

**First,** NFT encoders achieve near-zero permutation sensitivity (Δρ ≈ 4.7×10⁻⁷, matching
oracle performance without oracle access) while flat-MLP degrades by 52–89%. The robustness is
not approximate — it is exact, guaranteed by the equivariance theorem and confirmed empirically
across 21 training runs. For practitioners, this means a concrete architecture choice that
eliminates a fundamental brittleness.

**Second,** the mechanism is confirmed via mediation analysis (ΔR² = 0.228): NFT's advantage
is not incidental. Equivariant attention specifically captures neuron influence concentration
signals — the functional structural property that flat-MLP encodes position-dependently. We can
now answer not just "does NFT work better?" but "why, and by how much."

**Third,** the alternatives are insufficient. Permutation augmentation provides partial but
stochastically unreliable robustness (seed variance spanning 4× range). L2 canonicalization
catastrophically destroys the magnitude signal that generalization gap prediction requires,
providing a principled negative result for the field.

The unexpected bonus — NFT achieving higher baseline performance (ρ = 0.489 vs. 0.303) with
40× fewer parameters — challenges the assumption that scale substitutes for structural alignment.
When the architecture respects the symmetry of the task, compact and accurate may be achievable
simultaneously.

## Future Directions

**From unresolved alternatives:** The baseline performance advantage of NFT (62% relative
improvement with 40× fewer parameters) could reflect structural inductive bias or scale effects.
A matched-parameter-count comparison (75K flat-MLP vs. 75K NFT) would disentangle these
explanations and clarify when architectural alignment alone provides advantages independent
of parameter efficiency.

**From unverified claims:** The original hypothesis included cross-pipeline transfer robustness
(MNIST→CIFAR zoo evaluation) as a key prediction. Experiments h-m3 and h-m4 are designed and
require only the existing infrastructure and checkpoints from h-m1. Executing these experiments
would complete the causal chain from permutation symmetry through within-distribution robustness
to cross-distribution transfer, providing a comprehensive characterization of architectural
equivariance advantages.

**From scope extensions:** Validating on native FC-MLP weights (as opposed to the CNN zoo
adaptation used here) would establish generalizability to the original hypothesis scope.
Testing stronger canonicalization approaches (sort-by-magnitude, Hungarian alignment) would
complete the comparison between architectural equivariance and the best practical post-hoc
alternatives. Extending NFT-based analysis to heterogeneous architectures (variable-width
FC-MLPs, Transformers) would test the generality of the symmetry alignment principle.

## Closing Thought

For FC-MLP model zoo analysis, knowing which neuron is which is not just unnecessary — it is
a liability. Architectures that treat all neuron orderings as equivalent are not just more
robust; they are more efficient, more accurate, and structurally correct. As weight-space
analysis scales to larger and more diverse model repositories, the architectural alignment
principle demonstrated here becomes increasingly relevant: the right inductive bias for a
symmetric task is a symmetric architecture.
