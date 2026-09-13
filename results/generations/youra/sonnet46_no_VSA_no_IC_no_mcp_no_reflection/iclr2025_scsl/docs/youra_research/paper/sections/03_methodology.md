# Methodology

## Overview

Building on the theoretical intuition that spurious-minority samples should have gradients conflicting with the majority-dominated batch mean, we define a **Gradient Alignment Score** as the negated cosine similarity between a sample's per-sample last-layer gradient and the within-batch mean gradient. A low alignment score (conflicting gradient direction) serves as the minority membership signal — the core of the proposed Gradient Alignment Debiasing (GAD) framework.

This section describes our existence test: we measure whether the gradient alignment score achieves higher ROC-AUC than per-sample loss as a binary predictor of spurious-minority group membership. We test this at multiple training epochs to characterize the signal's temporal dynamics. Critically, we do *not* evaluate the downstream intervention (upweighting) in this work — the existence test (Hypothesis H-E1) is a prerequisite: if alignment ROC-AUC does not exceed loss ROC-AUC, the directional proxy provides no advantage and the intervention is unmotivated.

## Per-Sample Gradient Alignment Score

### Definition

Let $f_\theta: \mathcal{X} \to \mathbb{R}^C$ be a neural network with parameters $\theta$. At each training step, for a mini-batch $\mathcal{B} = \{(x_i, y_i)\}_{i=1}^{B}$, define:

$$g_i = \nabla_{\theta_{\text{fc}}} \mathcal{L}(f_\theta(x_i), y_i)$$

the per-sample gradient of the cross-entropy loss with respect to the last fully-connected layer parameters $\theta_{\text{fc}}$ only (the Linear$(2048, C)$ head). The batch-mean gradient is:

$$\bar{g} = \frac{1}{B} \sum_{i=1}^{B} g_i$$

The gradient alignment score for sample $i$ is:

$$a_i = 1 - \frac{g_i \cdot \bar{g}}{\|g_i\|_2 \cdot \|\bar{g}\|_2}$$

where $a_i \in [0, 2]$, with high $a_i$ indicating that sample $i$'s gradient *conflicts* with the batch mean (the predicted minority signal).

**Rationale for last-layer scope:** Restricting gradient computation to $\theta_{\text{fc}}$ (4,098 parameters for ResNet-50 with $C=2$) serves two purposes: (1) computational feasibility with vmap — computing gradients over all ResNet-50 parameters (~25M) per sample would require excessive memory; (2) the last layer is the most class-discriminative layer, where gradient directions most directly reflect the feature the model is exploiting for the current prediction.

**Rationale for cosine similarity:** Cosine similarity is magnitude-invariant — it measures *direction* of the gradient rather than magnitude. Per-sample loss already captures gradient magnitude information. Using cosine similarity isolates the directional component and, in theory, separates hard-majority samples (large gradient magnitude, but aligned direction) from spurious-minority samples (gradient conflicting in direction regardless of magnitude).

### Efficient Computation via vmap

Per-sample gradient computation is implemented using PyTorch's `torch.func` API:

```python
from torch.func import functional_call, vmap, grad

def per_sample_loss(params, buffers, x, y):
    pred = functional_call(model, (params, buffers), (x.unsqueeze(0),))
    return F.cross_entropy(pred, y.unsqueeze(0))

ft_grad = grad(per_sample_loss)
ft_per_sample_grad = vmap(ft_grad, in_dims=(None, None, 0, 0))

# params scoped to last layer only (model.fc)
fc_params = {k: v for k, v in model.named_parameters() if 'fc' in k}
fc_buffers = {}
per_sample_grads = ft_per_sample_grad(fc_params, fc_buffers, x_batch, y_batch)
```

The vmap scope is restricted to `model.fc` parameters; the backbone (ResNet-50 feature extractor) is frozen during probe computation. This reduces per-batch gradient storage from ~100M floats to 131K floats ($32 \times 4098$).

### Probe Injection Protocol

The gradient alignment probe is injected at checkpoint epochs $\mathcal{E} = \{1, 5, 10, 25, 50\}$ without modifying the standard ERM training loop. At each checkpoint epoch $e \in \mathcal{E}$:

1. After completing epoch $e$ of standard ERM training, freeze model parameters.
2. Run a full pass over the training set in mini-batches of $B=32$.
3. For each batch, compute $g_i$ and $a_i$ for all $i \in \mathcal{B}$.
4. Collect alignment scores $\mathbf{a} = (a_1, \ldots, a_N)$ and loss scores $\boldsymbol{\ell} = (\ell_1, \ldots, \ell_N)$ over all $N$ training samples.
5. Evaluate ROC-AUC of $\mathbf{a}$ and $\boldsymbol{\ell}$ against binary minority group membership labels.

**Rationale for checkpoint epochs:** Early epochs ($e=1, 5$) probe the simplicity-bias regime where spurious features are being learned; middle epochs ($e=10, 25$) probe the consolidation phase; late epoch ($e=50$) probes near-convergence. This range captures the full temporal dynamics predicted by the simplicity bias literature.

**Rationale for full training-set probe:** The probe computes alignment scores over all training samples (not just a held-out set) because ROC-AUC requires sufficient minority and majority samples for a stable estimate. On Waterbirds ($N=4795$, ~5% minority), this provides ~240 minority samples — adequate for reliable AUC estimation.

## Training Configuration

### Waterbirds

- **Model:** ResNet-50 (ImageNet pretrained, `torchvision.models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)`)
- **Last layer:** `model.fc = nn.Linear(2048, 2)` (replaced, randomly initialized)
- **Optimizer:** SGD, learning rate 0.001, momentum 0.9, weight decay $10^{-4}$
- **Batch size:** 32
- **Training size:** 4,795 samples (standard Waterbirds train split)
- **Seed:** 42
- **Preprocessing:** Resize(256) → CenterCrop(224) → ImageNet normalize; train augmentation: RandomHorizontalFlip

**Rationale for SGD over Adam:** We follow the standard Waterbirds ERM training protocol from Sagawa et al. [2020] for reproducibility and comparability. SGD preserves the gradient dynamics properties (loss landscape geometry, gradient direction structure) assumed by the spurious correlation literature.

### CelebA

- **Model:** Same ResNet-50 architecture
- **Optimizer:** SGD, learning rate 0.0001, momentum 0.9, weight decay $10^{-4}$
- **Batch size:** 32
- **Training size:** 16,000 samples (subsample from 162K for PoC feasibility; seed 42)
- **Target:** Blond hair prediction; spurious feature: gender

**Rationale for subsampling:** The existence test (H-E1) requires only that the alignment signal *exists* — a 16K subsample preserves the group composition ratios and is sufficient for ROC-AUC estimation with adequate minority representation. The primary question (does alignment ROC-AUC exceed loss ROC-AUC at any epoch?) is not sensitive to training set size as long as the minority group is represented.

## Evaluation Protocol

### ROC-AUC as Primary Metric

We evaluate gradient alignment and per-sample loss as binary classifiers of spurious-minority group membership using the area under the receiver operating characteristic curve (ROC-AUC). ROC-AUC is threshold-free — it measures the probability that a randomly chosen minority sample receives a higher score than a randomly chosen majority sample — making it the natural discriminability metric for an evaluation that doesn't assume a specific operating point.

**Minority group definitions:**
- Waterbirds: minority = $\{$landbird on water, waterbird on land$\}$ (groups 1 and 2 in group\_DRO encoding, combined ~18% of training data; however the semantically relevant "spurious minority" — samples where spurious correlation conflicts with prediction — is ~5%)
- CelebA: minority = blond male (group\_id 1 in group\_DRO encoding, ~0.8% of training data)

Binary label: $y_{\text{minority},i} = \mathbb{1}[\text{group\_id}_i \in \text{minority\_groups}]$.

### Comparison Signal: Per-Sample Loss

The natural comparator is $\ell_i = \mathcal{L}(f_\theta(x_i), y_i)$ — the same cross-entropy loss used for training. JTT and LfF both use variants of this signal. We evaluate loss ROC-AUC at the same checkpoint epochs under identical conditions, providing a direct comparison between the directional (gradient alignment) and magnitude (loss) proxies on the same model states.

## Scope and Limitations of This Study

This work is an existence test for H-E1: *can* within-batch gradient alignment be a viable minority proxy? We deliberately restrict scope to last-layer gradients, within-batch reference direction, and binary ROC-AUC comparison. We do not evaluate the full GAD intervention (EMA-smoothed upweighting), as this is only motivated if H-E1 passes. We do not test penultimate-layer alignment, global mean reference direction, or multi-seed variance — these are immediate next experiments conditional on H-E1 results.
