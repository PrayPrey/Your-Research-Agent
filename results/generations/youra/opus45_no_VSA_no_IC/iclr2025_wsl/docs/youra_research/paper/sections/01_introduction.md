# Introduction

Neural network weights encode everything about a model's learned function, yet extracting meaningful properties directly from these high-dimensional parameter vectors remains challenging. Weight-to-accuracy prediction—inferring test performance without running inference—enables efficient model selection, zoo curation, and training diagnostics. Prior work demonstrates this task is solvable: simple per-layer statistics (mean, variance, spectral norm) fed to linear regression achieve R² > 0.98 on large model collections.

The core difficulty lies in permutation symmetry. Within each layer, hidden units can be arbitrarily reordered (with corresponding permutation of downstream weights) without changing the network's input-output mapping. This symmetry creates exponentially many weight configurations representing identical functions—N! equivalent parameterizations per N-unit layer.

Two architectural strategies address this symmetry. **Feature engineering** computes permutation-invariant statistics (layer-wise aggregations), discarding structural information but guaranteeing invariance. **Permutation-equivariant networks** (e.g., Neural Functional Networks) encode symmetry directly in their architecture, processing weights while respecting permutation structure. The equivariant approach preserves richer information but requires specialized layers.

We investigate a fundamental question: **Is permutation equivariance merely helpful for data efficiency, or is it categorically required for learning weight-to-accuracy mappings from raw weights?**

Our experiments compare three methods across training sizes N ∈ {100, 250, 500, 1000, 2500, 5000}:
- **Statistics baseline**: Per-layer weight statistics with Ridge regression
- **MLP baseline**: Flattened raw weights as input features
- **NFN model**: Permutation-equivariant DeepSets-style architecture

We find that equivariance is not an optimization—it is a prerequisite. The MLP baseline achieves R² < 0 (worse than mean prediction) at all sample sizes, including N=5000. Meanwhile, the equivariant NFN achieves R² > 0.99 even at N=100. The effect size at N=500 (Δ = 2.5 R² points, p < 0.00001) is 25× larger than our predicted threshold.

These results reframe equivariance from a data efficiency advantage to a fundamental requirement. Non-equivariant methods cannot learn weight-to-accuracy mappings from raw weights regardless of sample size within practical ranges. This has direct implications for weight-space learning architectures: symmetry must be respected, either through careful feature engineering or equivariant design.
