# Experimental Setup

We design experiments to test the foundational assumption of Progressive Gradient Orthogonalization: that early training gradients primarily capture spurious feature directions.

## Research Questions

**RQ1:** Does the accumulated gradient subspace align more strongly with spurious (background) directions than core (bird type) directions during early training?

**RQ2:** Is the alignment difference measurable given realistic subspace ranks in high-dimensional parameter spaces?

## Dataset

**Waterbirds** (Sagawa et al., 2020): A spurious correlation benchmark where background type (water/land) correlates 95% with bird type (waterbird/landbird) in training data.

| Split | Samples | Groups | Spurious Correlation |
|-------|---------|--------|---------------------|
| Train | 4,795 | 4 (bird × background) | 95% |
| Validation | 1,199 | 4 | 95% |
| Test | 5,794 | 4 | Balanced |

**Why Waterbirds:** The 95% spurious correlation ensures that simplicity bias (if present) should strongly favor background features. The four-group structure enables computation of spurious and core gradient directions via controlled feature variation.

## Baselines

This experiment does not compare methods—it tests measurement validity. The implicit baseline is random projection: if our subspace captures no meaningful structure, alignment should approach the random baseline of $k/d \approx 2 \times 10^{-6}$ for rank-50 in 25M dimensions.

## Model and Training

**Model:** ResNet-50 pretrained on ImageNet, final fully-connected layer replaced with a 2-class linear head (25.6M trainable parameters).

**Training Configuration:**

| Parameter | Value |
|-----------|-------|
| Optimizer | SGD (momentum=0.9, weight_decay=1e-4) |
| Learning rate | 1e-3 (step decay at epochs 60, 75, γ=0.1) |
| Batch size | 128 |
| Total epochs | 90 |
| Random seed | 42 |

**Gradient Accumulation:**
- Accumulation window: epochs 1-10
- Samples accumulated: 1 gradient per epoch (last batch)
- SVD rank: k=50

## Evaluation Metrics

**Spurious Alignment:** Fraction of spurious direction variance captured by subspace S:
$$\text{align}_{\text{spur}} = \frac{\| S S^T \mathbf{v}_{\text{spur}} \|_2}{\| \mathbf{v}_{\text{spur}} \|_2}$$

**Core Alignment:** Fraction of core direction variance captured by subspace S:
$$\text{align}_{\text{core}} = \frac{\| S S^T \mathbf{v}_{\text{core}} \|_2}{\| \mathbf{v}_{\text{core}} \|_2}$$

**Success Criteria (from hypothesis H-E1):**
- Spurious alignment > 0.70 at epoch 10
- Core alignment < 0.30 at epoch 10

**Measurement Schedule:** Epochs 5, 10, 45 (early, accumulation end, late training)

## Reproducibility

Code implemented in PyTorch 2.0. Training completed on single NVIDIA A100 GPU in approximately 11 minutes. Checkpoint saved at epoch 10 for alignment measurement. Figures generated via matplotlib and saved to `figures/` directory.
