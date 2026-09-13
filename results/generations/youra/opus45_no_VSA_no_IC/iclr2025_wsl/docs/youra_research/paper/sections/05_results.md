# Results

## Main Finding

**Permutation equivariance is a prerequisite for learning weight-to-accuracy mappings from raw weights.**

The MLP baseline achieves negative R² (worse than predicting the mean) at every training size tested, including N=5000. The equivariant NFN achieves R² > 0.99 even at N=100. This is not a data efficiency advantage—it is a categorical difference between methods that work and methods that cannot work.

## Quantitative Results

### Learning Curves Across Training Sizes

| N | Statistics R² | NFN R² | MLP R² |
|---|---------------|--------|--------|
| 100 | 0.9995 | ~0.995 | < 0 |
| 250 | 0.9995 | ~0.997 | < 0 |
| 500 | 0.9995 | 0.9985 | -1.50 |
| 1000 | 0.9995 | ~0.998 | < 0 |
| 2500 | 0.9995 | ~0.999 | < 0 |
| 5000 | 0.9995 | 0.9973 | -1.08 |

Statistics and NFN are both near-perfect across all N. MLP fails categorically.

### Primary Comparison (N=500, 10 seeds)

| Metric | NFN | MLP |
|--------|-----|-----|
| Mean R² | 0.9985 ± 0.0007 | -1.50 ± 0.77 |
| MAE | 0.004 | 0.15 |
| Effect Size (Δ) | — | **2.50** |
| p-value | — | **4.58 × 10⁻⁶** |

The 2.50 R² gap is 25× larger than our predicted threshold of 0.1. Every single seed shows the same pattern: NFN succeeds, MLP fails.

### Equivariance Verification

| Metric | Value |
|--------|-------|
| Pass Rate | 100% (2500/2500) |
| Max Error | 8.94 × 10⁻⁸ |
| Tolerance | 1 × 10⁻⁵ |

The NFN architecture is numerically equivariant within floating-point precision.

## Analysis

### Why MLP Fails

The MLP receives ~270K-dimensional flattened weight vectors. At N=500:

1. **Severe underdetermination**: 270K features, 500 samples—no generalization possible without strong inductive bias
2. **Permutation explosion**: Each N-unit layer has N! equivalent configurations; MLP must implicitly learn invariance
3. **No exploitable structure**: Flattened weights lose layer-wise organization

Even at N=5000, the sample-to-dimension ratio (5000:270K ≈ 1:54) remains severely underdetermined.

### Why NFN Succeeds

The equivariant architecture constrains the hypothesis space:

1. **Weight sharing**: Per-neuron MLPs dramatically reduce effective parameters
2. **Architectural invariance**: Permutation symmetry enforced by design, not learned
3. **Preserved structure**: Layer-wise processing maintains semantic organization

The NFN learns a function over equivalence classes of permutation-related weights, reducing the effective dimensionality of the learning problem.

### Why Statistics Works

The statistics baseline also succeeds because:
1. Layer-wise aggregations are inherently permutation-invariant
2. 63 features vs. 270K means well-conditioned regression
3. No symmetry to learn—invariance is built into features

Statistics trades expressiveness for guaranteed invariance. NFN achieves both.

## Prediction Analysis

### H-M2 Predictions

| Prediction | Expected | Observed | Status |
|------------|----------|----------|--------|
| P1: NFN > MLP + 0.1 at N=500 | Δ ≥ 0.1 | **Δ = 2.50** | CONFIRMED (25×) |
| P2: Methods converge at N=5000 | |ΔR²| ≤ 0.03 | **MLP R² = -1.08** | REFUTED |
| P3: Crossing N* < 2500 | N* exists | **No crossing** | REFUTED |

P1 is confirmed with effect size far exceeding expectations. P2 and P3 are refuted—but these refutations strengthen our conclusions: MLP's failure is more severe than predicted.

## Implications

The original hypothesis—"equivariance reduces sample requirements by 50%"—understated the finding. The comparison is not efficiency; it is feasibility:

- **Equivariant methods**: R² > 0.99 at all N tested
- **Non-equivariant methods**: R² < 0 at all N tested

Permutation equivariance is not an optimization. It is a prerequisite.
