# Methodology

Building on our observation that permutation invariance must be architecturally encoded, we design experiments to verify both the existence of equivariance benefits and the mechanism underlying them. This section describes our neural architectures, the probe invariance test, and the experimental protocol.

## Neural Functional Networks (NFN)

We adopt the NFN architecture from Zhou et al. [2023] for permutation-equivariant weight processing. Given input weights W from a target neural network, NFN processes them through equivariant layers that respect the permutation symmetry of hidden neurons.

### NPLinear Layer

The core building block is NPLinear, which linearly transforms weight tensors while maintaining equivariance. For weights connecting layer l to layer l+1, NPLinear applies:

$$h^{(l+1)} = \text{NPLinear}(h^{(l)}) = W_{\text{eq}} h^{(l)} + b_{\text{eq}}$$

where $W_{\text{eq}}$ is constrained to be permutation-equivariant—if we permute the neurons in the input weight tensor, the output transforms consistently.

**Rationale:** Standard linear layers treat flattened weights as arbitrary vectors, destroying structural information. NPLinear preserves neuron-level semantics, enabling meaningful feature extraction regardless of arbitrary indexing choices.

### HNPPool Layer

To produce a final permutation-invariant representation for regression, we use HNPPool (Hierarchical Neural Functional Pooling):

$$z = \text{HNPPool}(h^{(L)}) = \text{pool}_{\text{neurons}}(h^{(L)})$$

This pools over neuron dimensions while preserving layer structure, yielding a fixed-size vector invariant to neuron permutation.

**Rationale:** Prediction tasks require a single output regardless of how neurons are indexed. HNPPool mathematically guarantees this invariance rather than hoping the model learns it from data.

### Complete Architecture

Our NFNRegressor combines these components:

```
Input weights → NPLinear(32) → ReLU → NPLinear(32) → ReLU → HNPPool → Linear(1) → R² prediction
```

We use 32 channels throughout, AdamW optimizer with learning rate 1e-3, cosine annealing scheduler, and train for 50 epochs.

## MLP-Matched Baseline

For fair comparison, we design an MLP with matched capacity:

```
Flattened weights → Linear(hidden) → ReLU → Linear(hidden) → ReLU → Linear(1) → R² prediction
```

We set hidden dimension such that total parameters approximately match NFN. The key difference: MLP processes weights as arbitrary vectors with no structural constraints.

**Rationale:** Capacity-matching ensures performance differences stem from architectural properties (equivariance vs. none), not parameter count.

## Probe Invariance Test

To verify whether models develop permutation-invariant representations, we introduce the probe invariance test:

### Protocol

1. Take a trained model M and a test weight tensor W
2. Generate K random permutations π₁, π₂, ..., πₖ of the hidden neurons
3. Apply M to each permuted version: ŷᵢ = M(πᵢ(W))
4. Compute invariance score: $I = \frac{1}{K}\sum_{i<j} \text{corr}(\hat{y}_i, \hat{y}_j)$

For a truly invariant model, all predictions should be identical: I = 1.0.

**Rationale:** R² alone measures prediction accuracy but not mechanism. A model could achieve high R² by memorizing position-dependent patterns that happen to correlate with accuracy in the training distribution. The probe invariance test directly measures whether the model has learned permutation-invariant representations.

### Implementation Details

We use K=10 random permutations per test sample, averaging correlations across 100 test samples. For NFN, we expect I ≈ 1.0 (mathematical guarantee). For MLP, I varies based on whether invariance was learned.

## Experimental Design

Our experiments test the following hypotheses:

| ID | Hypothesis | Test Method | Success Criterion |
|----|-----------|-------------|-------------------|
| H-E1 | NFN outperforms MLP at N=1K | Paired t-test on R² | Difference > 0.05, p < 0.05 |
| H-M1 | NFN layers are equivariant | Output deviation under permutation | Max deviation < 1e-5 |
| H-M2 | NFN predictions are invariant | Prediction correlation across permutations | Correlation > 0.99 |
| H-M3 | Untrained MLP lacks invariance | Output coefficient of variation | CV > 0.1 |
| H-M4 | MLP invariance low at N=1K | Probe invariance score | Score < 0.5 |
| H-M5 | MLP learns invariance at N=40K | Probe invariance score | Score > 0.8 |

H-E1 tests existence of the equivariance benefit. H-M1 through H-M5 test the causal mechanism—whether NFN's advantage comes from correct symmetry encoding and whether MLPs can learn it from data.

## Training Protocol

- **Dataset:** Model Zoo CIFAR-10 CNNs (~42K models)
- **Splits:** 80% train, 20% test (fixed across all N conditions)
- **Seeds:** 1-3 per condition (effect sizes large enough for significance)
- **Target:** Model accuracy prediction (R²)

We normalize weights per-layer to zero mean and unit variance, following standard practice in weight-space learning.

**Figure 1** (figures/permutation_invariance.png) illustrates NFN prediction stability across permutations, demonstrating the mathematical guarantee of equivariance.
