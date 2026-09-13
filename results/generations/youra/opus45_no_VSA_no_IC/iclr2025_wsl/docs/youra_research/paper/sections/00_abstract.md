# Abstract

Predicting neural network accuracy directly from weights enables efficient model selection and zoo curation without running inference. This task requires handling permutation symmetry—hidden units can be reordered without changing network function. We investigate whether permutation equivariance is merely helpful for data efficiency or categorically required.

We compare three methods on ResNet-20/CIFAR-10 model zoos: a statistics baseline (per-layer aggregations), an MLP baseline (flattened raw weights), and a permutation-equivariant NFN architecture (DeepSets-style). Experiments span training sizes N=100 to 5000 with 10 seeds each.

Our findings are striking. The MLP baseline achieves R² < 0 (worse than mean prediction) at all sample sizes including N=5000. The equivariant NFN achieves R² > 0.99 even at N=100. At N=500, the gap is Δ=2.50 R² points (p < 0.00001)—25× larger than our predicted threshold. The statistics baseline also succeeds (R² = 0.9995) via aggressive dimensionality reduction.

These results reframe equivariance from a data efficiency technique to a fundamental requirement. Non-equivariant methods cannot learn weight-to-accuracy mappings from raw weights regardless of sample size. Weight-space learning systems must respect permutation symmetry—either through invariant features or equivariant architectures.
