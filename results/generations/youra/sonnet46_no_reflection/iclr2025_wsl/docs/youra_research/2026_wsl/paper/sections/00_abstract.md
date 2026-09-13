# Abstract

Cross-architecture weight space learning requires positional encodings that capture structural
information transferable across neural network families. We investigate orbit-based positional
encodings (orbit-PE) derived from the input/output channel permutation group — a group that
acts identically on all linear operator types (Conv2d, Linear, MultiheadAttention). We establish
that this group is a functionally exact symmetry across architectures (|Δacc| = 0.000000 across
4,500 permutation runs on CNN and Transformer Zoo checkpoints) and that orbit-PE is computable
with 1.167× overhead using a unified, architecture-agnostic codebase. However, measuring
permutation versus General Linear (GL) orbit variance across 1,000 CNN Zoo models × 50 training
epochs reveals a fundamental layer-type stratification: permutation orbits explain 63.7% of
Conv2d weight-space variance (sufficient for the permutation-only regime) but only 13.3% of
Linear/attention variance — a 4.8× gap. This bimodal stratification explains why permutation
equivariant methods achieve τ > 0.93 within CNN Zoo but fail cross-architecture, and motivates
a hybrid encoding combining permutation orbit-PE for convolutional layers with GL-invariant
trace features for linear/attention layers. All code and infrastructure for the hybrid
approach is released.
