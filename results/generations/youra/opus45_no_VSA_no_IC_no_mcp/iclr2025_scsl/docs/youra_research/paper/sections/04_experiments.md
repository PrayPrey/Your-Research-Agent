# Experimental Setup

We design experiments to answer two sequential questions:

**RQ1:** Do spurious features dominate core features early in ERM training? (Existence)

**RQ2:** Do spurious features receive stronger gradient signals than core features? (Mechanism)

RQ1 establishes the phenomenon; RQ2 tests the hypothesized mechanism. We proceed to RQ2 only if RQ1 confirms spurious dominance exists.

## Dataset

**Waterbirds v1.0** [Sagawa et al., 2020]: A benchmark for studying spurious correlations in image classification. The task is to classify bird type (waterbird vs. landbird) while the background habitat (water vs. land) serves as a spurious feature correlated with the label in training data.

| Statistic | Value |
|-----------|-------|
| Total images | 11,788 |
| Training | 4,795 |
| Validation | 1,199 |
| Test | 5,794 |
| Classes | 2 (waterbird, landbird) |
| Spurious attribute | Background (water, land) |
| Minority groups | Waterbird-land, Landbird-water |

**Rationale:** Waterbirds provides ground-truth group labels enabling precise measurement of spurious-aligned versus minority sample behaviors. The spatial separation of spurious (background) and core (bird) features enables attribution analysis.

## Model and Training

| Parameter | Value |
|-----------|-------|
| Architecture | ResNet-50 (ImageNet pretrained) |
| Optimizer | SGD (momentum=0.9, weight_decay=1e-4) |
| Learning rate | 0.01 (H-E1), 0.001 (H-M1) |
| LR schedule | StepLR (step=20, gamma=0.1) |
| Batch size | 128 |
| Epochs | 50 |
| Seeds | 1 (H-E1), 3 (H-M1) |

**Rationale:** We use standard ERM training to establish baseline dynamics. The lower learning rate for H-M1 ensures stable gradient measurements without training collapse.

## Evaluation Protocol

### RQ1: Spurious Feature Attribution

We measure GradCAM [Selvaraju et al., 2017] attribution on layer4 (final convolutional block) across 500 validation samples at each epoch. Spurious and core regions are defined by spatial heuristic:
- **Spurious region:** Upper 60% of image (background)
- **Core region:** Lower 40% of image (bird)

**Primary metric:** Attribution ratio $R(t) = A_{\text{spurious}}(t) / A_{\text{core}}(t)$

**Success criterion:** $R(t) > 1.0$ for $t < 10$ (spurious dominance before epoch 10)

### RQ2: Gradient Norm Analysis

We partition training samples into spurious-aligned (label matches background) and minority (label mismatches background) groups. For each epoch, we compute mean gradient norms at layer4 for each group.

**Primary metric:** Gradient ratio $\rho(t) = G_{\text{spurious}}(t) / G_{\text{minority}}(t)$

**Hypothesis:** $\rho(t) > 1.5$ in epochs 1-10 (spurious features receive stronger gradients)

**Falsification:** $\rho(t) < 1.0$ (mechanism inverted)

### Statistical Analysis

For H-M1, we run 3 seeds (42, 123, 456) and report mean ± standard deviation. Consistency across seeds (all showing same direction) constitutes robust evidence.

## Baselines

This study does not propose a new method requiring baseline comparison. Instead, we test a mechanistic hypothesis about standard ERM training. The relevant "baselines" are the expected behaviors under the gradient competition hypothesis:

| Prediction | Expected (Gradient Competition) | If Falsified |
|------------|--------------------------------|--------------|
| Attribution ratio (H-E1) | $R > 1.0$ early | Spurious dominance absent |
| Gradient ratio (H-M1) | $\rho > 1.5$ early | Mechanism incorrect |

## Implementation

Experiments implemented in PyTorch 2.0 with pytorch-grad-cam for attribution. Training on single NVIDIA GPU. Gradient norms computed via `torch.autograd.grad` with per-sample separation. All code available in supplementary material.
