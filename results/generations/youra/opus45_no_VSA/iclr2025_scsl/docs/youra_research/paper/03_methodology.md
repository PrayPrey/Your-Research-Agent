# Methodology

## Problem Setup

Consider a classification task with input space $\mathcal{X}$, label space $\mathcal{Y}$, and group structure $\mathcal{G}$. Each sample $(x, y, g) \in \mathcal{X} \times \mathcal{Y} \times \mathcal{G}$ belongs to a group $g$ defined by the combination of label and spurious attribute. In Waterbirds, groups are {landbird-land, landbird-water, waterbird-water, waterbird-land}, with the latter two being minority groups (5% of training data).

Let $f_\theta: \mathcal{X} \to \mathcal{Y}$ be a neural network with parameters $\theta$. ERM minimizes the average loss:
$$\mathcal{L}(\theta) = \frac{1}{n} \sum_{i=1}^{n} \ell(f_\theta(x_i), y_i)$$

We investigate how this objective creates differential optimization dynamics across groups.

## Sharpness Ratio (SR)

We measure group-conditional curvature via the maximum Hessian eigenvalue. For group $g$, define the group-conditional loss:
$$\mathcal{L}_g(\theta) = \frac{1}{|g|} \sum_{(x,y) \in g} \ell(f_\theta(x), y)$$

The maximum eigenvalue $\lambda_{\max}(H_g)$ of the Hessian $H_g = \nabla^2 \mathcal{L}_g(\theta)$ characterizes local curvature. We compute this via power iteration (20 iterations) on a subsample of 100 samples per group.

The **Sharpness Ratio** is:
$$\text{SR} = \frac{\lambda_{\max}(H_{\text{minority}})}{\lambda_{\max}(H_{\text{majority}})}$$

SR > 1.0 indicates minority groups occupy sharper regions; SR ≈ 1.0 indicates symmetric curvature.

## Gradient Ratio

We track per-group gradient convergence via the gradient ratio:
$$r_t = \frac{\|\nabla \mathcal{L}_{\text{majority}}(\theta_t)\| / n_{\text{maj}}}{\|\nabla \mathcal{L}_{\text{minority}}(\theta_t)\| / n_{\text{min}}}$$

where $n_{\text{maj}}, n_{\text{min}}$ are group sample counts. Normalizing by sample count isolates per-sample gradient magnitude from frequency effects. $r_t < 1$ indicates majority gradients (per sample) are smaller—i.e., majority has converged more.

## Temporal Precedence Analysis

To test whether gradient ratio decay precedes SR divergence, we compute the lagged cross-correlation between $r_t$ and $\text{SR}_t$ over training epochs:
$$\rho(\tau) = \text{corr}(r_{t}, \text{SR}_{t+\tau})$$

for lags $\tau \in [-5, +5]$ epochs. The optimal lag $\tau^* = \arg\max_\tau |\rho(\tau)|$ indicates temporal precedence. $\tau^* > 0$ means gradient ratio changes precede SR changes, consistent with causation from gradient dynamics to curvature.

## Experimental Protocol

### H-E1: Initialization Baseline
- Initialize ResNet-50 with random weights (5 seeds)
- Compute SR₀ before any training
- Success criterion: SR₀ ∈ [0.9, 1.1] with 95% CI including 1.0

### H-M1: Temporal Precedence
- Train ResNet-50 (ImageNet pretrained) on Waterbirds for 10 epochs
- Log $r_t$ and $\text{SR}_t$ at each epoch
- Compute lagged cross-correlation
- Success criterion: $\tau^* > 0$ with 95% CI excluding zero

### Implementation Details
- **Model:** ResNet-50 (torchvision, ImageNet pretrained for H-M1)
- **Optimizer:** SGD (lr=0.001, momentum=0.9, weight_decay=0.0001)
- **Batch size:** 128
- **Hessian computation:** Power iteration, 20 iterations, 100 samples/group
- **Seeds:** 5 for H-E1, 3 for H-M1
