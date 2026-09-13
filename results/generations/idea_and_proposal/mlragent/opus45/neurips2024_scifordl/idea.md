# Research Idea

## Title
**Falsifying the "Superposition Hypothesis": Testing Whether Neural Networks Actually Compress Features into Shared Dimensions**

## Motivation
The superposition hypothesis—that neural networks represent more features than dimensions by encoding them as nearly-orthogonal vectors in overlapping subspaces—has become a foundational assumption in mechanistic interpretability. However, this hypothesis largely derives from toy models and theoretical arguments rather than rigorous empirical validation on production-scale networks. If superposition is less prevalent than assumed, current interpretability methods may be fundamentally misguided. Understanding the actual prevalence and conditions under which superposition occurs is critical for building reliable interpretability tools.

## Main Idea
I propose a systematic empirical investigation to test the superposition hypothesis across diverse architectures and scales. The methodology involves:

1. **Controlled experiments**: Train networks on tasks with known ground-truth feature counts, varying network width to identify the transition point where superposition becomes necessary.

2. **Geometric analysis**: Measure the effective dimensionality of feature representations using participation ratio and intrinsic dimension estimators, comparing observed dimensions against theoretical predictions from superposition models.

3. **Interference detection**: Design probing tasks that would reveal interference patterns if features share dimensions, testing whether predicted superposition-induced errors actually manifest.

4. **Scale analysis**: Examine whether larger models exhibit less superposition, potentially explaining emergent capabilities.

Expected outcomes include quantitative bounds on superposition prevalence and identification of architecture/task conditions that promote or prevent it, directly informing interpretability research directions.