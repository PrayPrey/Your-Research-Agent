# Methodology

Our methodology tests whether gradient subspace accumulation can distinguish spurious from core feature directions. We design a measurement apparatus and document its requirements for valid operation.

## Problem Formulation

Let $f_\theta: \mathcal{X} \to \mathcal{Y}$ be a neural network with parameters $\theta \in \mathbb{R}^d$. During training, the gradient $\nabla_\theta \mathcal{L}$ provides a $d$-dimensional direction of parameter change.

**Hypothesis:** Under simplicity bias, early training gradients point predominantly toward spurious feature directions. Accumulating these gradients into a subspace $S$ via SVD should yield high alignment with spurious directions and low alignment with core directions.

**Measurement goal:** Quantify alignment between gradient subspace $S$ and spurious/core feature directions.

## Gradient Subspace Accumulation

We accumulate gradients during early training epochs and compute a principal subspace via SVD.

**Algorithm: Gradient Subspace Computation**

```
Input: Model θ, epochs T_acc, rank k
Output: Subspace S ∈ ℝ^{d×k}

G ← empty matrix
for epoch t = 1 to T_acc:
    for batch in dataloader:
        compute loss L(θ)
        g_t ← flatten(∇_θ L)  # d-dimensional vector
        append g_t to G
    
U, Σ, V^T ← SVD(G)
S ← V[:k]^T  # top-k right singular vectors (d × k)
return S
```

**Design rationale:** SVD captures principal components of gradient variation. If simplicity bias holds, spurious feature gradients should dominate early principal components.

**Critical requirement identified:** The matrix $G$ must have sufficient rows (gradient samples) relative to parameter dimensionality $d$. With $d = 25 \times 10^6$ parameters and only 10 gradients (one per epoch), rank($G$) ≤ 10. The resulting subspace captures negligible variance.

## Direction Computation

We define spurious and core directions via gradient differences across group-varying samples.

**Spurious direction:** Average gradient when background changes while bird type remains constant:
$$\mathbf{v}_{\text{spur}} = \mathbb{E}_{(x_a, x_b) \in \mathcal{P}_{\text{spur}}} \left[ \nabla_\theta \mathcal{L}(x_a) - \nabla_\theta \mathcal{L}(x_b) \right]$$

where $\mathcal{P}_{\text{spur}}$ pairs images with same bird type but different backgrounds.

**Core direction:** Average gradient when bird type changes while background remains constant:
$$\mathbf{v}_{\text{core}} = \mathbb{E}_{(x_a, x_b) \in \mathcal{P}_{\text{core}}} \left[ \nabla_\theta \mathcal{L}(x_a) - \nabla_\theta \mathcal{L}(x_b) \right]$$

where $\mathcal{P}_{\text{core}}$ pairs images with same background but different bird types.

**Rationale:** These directions isolate gradient components responsive to spurious (background) vs. core (bird type) features by differencing out common components.

## Alignment Measurement

Alignment measures the fraction of a direction's variance explained by the subspace:

$$\text{align}(S, \mathbf{v}) = \frac{\| S S^T \mathbf{v} \|_2}{\| \mathbf{v} \|_2}$$

This equals 1 if $\mathbf{v}$ lies entirely within $S$, and 0 if orthogonal.

**Success criteria (from hypothesis):**
- $\text{align}(S, \mathbf{v}_{\text{spur}}) > 0.70$
- $\text{align}(S, \mathbf{v}_{\text{core}}) < 0.30$

## Experimental Setup

**Dataset:** Waterbirds (Sagawa et al., 2020)
- 4,795 training images, 4 groups (bird type × background)
- 95% spurious correlation in training data

**Model:** ResNet-50 (pretrained ImageNet), final layer replaced with 2-class linear head
- Parameters: $d \approx 25 \times 10^6$

**Training:**
- Optimizer: SGD (momentum=0.9, weight_decay=1e-4)
- Learning rate: 1e-3 with step decay at epochs 60, 75
- Batch size: 128
- Total epochs: 90
- Accumulation window: epochs 1-10
- SVD rank: $k = 50$

**Measurement epochs:** 5, 10, 45

## Implementation Notes

Our implementation accumulated one gradient per epoch (last batch gradient). This produced a gradient matrix $G \in \mathbb{R}^{10 \times 25M}$ with rank at most 10. The resulting 10-dimensional subspace $S$ explains negligible variance in any direction.

**The failure mode:** For any unit vector $\mathbf{v} \in \mathbb{R}^{25M}$ drawn uniformly at random, expected alignment with a rank-10 subspace is approximately $10 / 25M \approx 4 \times 10^{-7}$. Our measured alignments (~0.05) exceed this but remain far below thresholds, indicating the measurement lacks resolution.

**Corrective requirement:** Accumulate gradients across all batches within epochs 1-10, yielding thousands of gradient samples. This increases subspace rank sufficiently for meaningful alignment measurement.
