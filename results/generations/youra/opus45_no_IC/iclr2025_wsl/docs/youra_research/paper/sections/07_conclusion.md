# Conclusion

We began with a counterintuitive question: can a model achieve 99% accuracy while fundamentally misunderstanding its input structure? Our experiments demonstrate that yes—MLPs trained on 40K models achieve near-perfect accuracy prediction (R²=0.99) but fail to learn permutation invariance (0.63), exploiting dataset-specific correlations rather than semantic weight structure.

This finding has clear implications: **architectural inductive biases are essential, not merely convenient, for certain symmetries**. Permutation equivariance must be built into the architecture; data quantity cannot substitute.

Our key contributions:

1. **Sample Efficiency:** NFN achieves 60 percentage point R² advantage over MLP at N=1K (0.95 vs 0.35), demonstrating massive practical value of equivariance in data-limited regimes.

2. **Mechanism Verification:** We introduce probe invariance testing, revealing that NFN's invariance is mathematically perfect (deviation < 1.19e-07) while MLP invariance plateaus at 0.63 regardless of scale.

3. **Falsification:** We provide the first direct evidence that MLPs cannot learn permutation invariance from data diversity, challenging the assumption that "more data teaches symmetries."

Looking forward, we envision extending these principles to transformer weight spaces, where attention mechanisms introduce different symmetry structures. The broader message—that certain structural properties require architectural encoding—may inform design choices across deep learning domains where symmetries are present but not currently exploited.

A model that learns the right answers through the wrong mechanism may seem acceptable when training and test distributions align. But robustness requires correct representations. Our work provides both the diagnostic tools (probe invariance) and the architectural solution (NFN) for ensuring that weight-space models learn not just to predict, but to understand.
