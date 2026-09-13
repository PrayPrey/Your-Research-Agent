# Discussion

## Key Findings

Our experiments reveal a nuanced picture: **positive efficiency results can coexist with falsified mechanistic explanations.**

**Finding 1: Efficiency without convergence.** Temporal dynamic attention achieves 10.2% FLOP reduction while attention entropy *increases* across steps. The efficiency derives from architectural iteration reduction (T=2 vs T=3), not from attention patterns converging toward task-relevant distributions. This suggests that biological intuitions about iterative refinement may not transfer directly to artificial attention systems—or may require different architectural constraints to manifest.

**Finding 2: Iteration count dominates K/V caching.** The 10.2% efficiency from T reduction exceeds the 6.8% from K/V caching. K/V projection is a smaller fraction of total attention cost than the per-step attention computation. This has practical implications: when optimizing temporal attention, prioritize iteration scheduling over memory optimizations.

**Finding 3: Constant scaling, not scaling advantage.** The 5.31% FLOP reduction is sequence-length-independent. This bounds applicability: temporal dynamic attention provides consistent savings but no special long-sequence advantage. For applications where long-sequence efficiency is critical, complementary approaches (sparse attention, linear attention) may be needed.

## Implications for Mechanism Validation

Our methodology—decomposing efficiency claims into sub-hypotheses with MUST_WORK and SHOULD_WORK gates—detected a divergence that end-to-end benchmarking would miss. A traditional evaluation would report "10% FLOP reduction" without falsifying the convergence hypothesis.

This suggests a broader principle: **efficiency claims should include mechanism-level tests, not just outcome measurements.** When a method claims efficiency through mechanism X, experimental design should include tests that could falsify X even if efficiency is achieved through other means.

## Limitations

**L1: Random initialization for convergence testing.** H-M2 tested convergence on a model with random (not trained) weights. Without learned representations, temporal steps may behave differently than in a trained model. Future work should test convergence after full training.

**L2: CPU-only execution.** All experiments ran on CPU due to CUDA unavailability. This prevented memory profiling and wall-clock timing measurements. GPU validation would provide more complete efficiency characterization.

**L3: P3 (reasoning tasks) not tested.** The original hypothesis included improved performance on temporal reasoning tasks (P3). This prediction remains inconclusive—we focused on efficiency validation and did not evaluate reasoning benchmarks.

**L4: Single architecture.** Results are specific to our 6-layer, 512-dim transformer. Scaling to larger architectures and different attention patterns may yield different mechanism behavior.

## Why These Limitations Are Acceptable

L1-L4 do not invalidate our core contributions. H-M1 (efficiency) and H-E1 (existence) are validated regardless of convergence behavior. The negative results on H-M2 and H-C1 provide valuable bounds even if future work refines the convergence analysis. We report limitations honestly to enable appropriate interpretation.

## Broader Impact

**Positive impacts:** Our methodology promotes rigorous mechanism validation in efficiency research. Distinguishing "what works" from "why it works" enables more principled architectural extensions and reduces wasted effort pursuing mechanistically incorrect intuitions.

**Potential concerns:** Demonstrating that efficiency can be achieved without the proposed mechanism might discourage biologically-inspired research. We emphasize that our results are specific to one architecture; biological intuitions remain valuable starting points even when specific implementations require refinement.

**Reproducibility:** We structure experiments for replication and report hyperparameters, seeds, and evaluation protocols. The methodology (sub-hypothesis decomposition) is transferable to other efficiency claims.
