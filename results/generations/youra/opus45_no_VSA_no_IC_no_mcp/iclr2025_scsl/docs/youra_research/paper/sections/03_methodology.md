# Methodology

Our investigation tests the gradient competition hypothesis through a two-stage experimental design: first establishing that spurious feature dominance exists (Existence, H-E1), then testing whether this dominance arises from stronger gradient signals (Mechanism, H-M1). This sequential design ensures we do not test a mechanism for a phenomenon that may not exist.

## Overview

The gradient competition hypothesis posits that spurious features dominate because they produce stronger gradient signals during training. If true, we should observe:

1. **Existence:** GradCAM attribution on spurious regions exceeds attribution on core regions early in training
2. **Mechanism:** Gradient norms from spurious-aligned samples exceed those from minority samples, especially in early epochs

We design experiments to test both predictions. Existence confirmation (H-E1) enables mechanism testing (H-M1). Mechanism falsification does not invalidate the existence of spurious dominance—it invalidates a specific explanation for why dominance occurs.

## Experiment 1: Spurious Feature Attribution (H-E1)

**Objective:** Measure whether spurious features dominate core features early in training.

### Attribution Measurement

We use GradCAM [Selvaraju et al., 2017] to compute class-discriminative attributions at layer4 (final convolutional block) of ResNet-50. For each validation sample, we obtain a spatial attribution map indicating which image regions contribute to the classification decision.

**Rationale:** GradCAM is a standard attribution method that requires no architectural modifications. Layer4 captures high-level semantic features most relevant to the classification decision.

### Region Definition

We define spurious and core regions based on Waterbirds image structure:
- **Spurious region:** Upper 60% of image (background habitat)
- **Core region:** Lower 40% of image (bird location)

**Rationale:** Waterbirds images are constructed by placing bird crops on background scenes. While ground-truth segmentation masks would provide more precise regions, our heuristic captures the primary spurious correlation (background) versus target feature (bird) distinction.

### Dominance Metric

For each epoch $t$, we compute the attribution ratio:

$$R(t) = \frac{\sum_{i} A_{\text{spurious}}^{(i)}(t)}{\sum_{i} A_{\text{core}}^{(i)}(t)}$$

where $A_{\text{spurious}}^{(i)}(t)$ and $A_{\text{core}}^{(i)}(t)$ are the summed GradCAM attributions over spurious and core regions for sample $i$ at epoch $t$.

**Success criterion:** $R(t) > 1.0$ for $t < 10$ (spurious dominance before epoch 10).

## Experiment 2: Gradient Norm Analysis (H-M1)

**Objective:** Test whether spurious features receive stronger gradient signals.

### Sample Grouping

We partition training samples into two groups based on spurious correlation alignment:

- **Spurious-aligned:** Samples where label matches background type (e.g., waterbird on water)
- **Minority:** Samples where label mismatches background (e.g., waterbird on land)

**Rationale:** Spurious-aligned samples can be classified correctly using either spurious or core features; minority samples require core feature learning for correct classification.

### Gradient Measurement

For each training batch, we compute gradient norms at layer4 for spurious-aligned and minority samples separately:

$$G_{\text{spurious}}(t) = \frac{1}{|S_t|} \sum_{i \in S_t} \|\nabla_\theta \mathcal{L}(x_i, y_i)\|_2$$

$$G_{\text{minority}}(t) = \frac{1}{|M_t|} \sum_{i \in M_t} \|\nabla_\theta \mathcal{L}(x_i, y_i)\|_2$$

where $S_t$ and $M_t$ are the sets of spurious-aligned and minority samples in epoch $t$.

### Mechanism Metric

We compute the gradient norm ratio:

$$\rho(t) = \frac{G_{\text{spurious}}(t)}{G_{\text{minority}}(t)}$$

**Hypothesis:** If gradient competition drives spurious dominance, then $\rho(t) > 1.5$ in early epochs (1-10).

**Falsification:** If $\rho(t) < 1.0$, the mechanism is inverted—minority samples produce stronger gradients.

## Training Configuration

Both experiments use identical training setup:

| Parameter | Value |
|-----------|-------|
| Dataset | Waterbirds v1.0 |
| Model | ResNet-50 (ImageNet pretrained) |
| Optimizer | SGD (momentum=0.9, weight_decay=1e-4) |
| Learning Rate | 0.01 (H-E1), 0.001 (H-M1) |
| Batch Size | 128 |
| Epochs | 50 |
| Seeds | 1 (H-E1), 3 (H-M1) |

**Rationale for H-M1 lower LR:** We use a more conservative learning rate for mechanism testing to ensure stable gradient measurements without training collapse. The lower LR produces more interpretable gradient dynamics.

## Gate Structure

Our experimental design follows a gate-based verification protocol:

| Hypothesis | Gate Type | Condition | Action if Fail |
|------------|-----------|-----------|----------------|
| H-E1 | MUST_WORK | $R(t) > 1.0$ for $t < 10$ | Abort (no spurious dominance) |
| H-M1 | MUST_WORK | $\rho(t) > 1.5$ for $t \in [1,10]$ | Pivot (mechanism incorrect) |

**Rationale:** MUST_WORK gates ensure we do not proceed with invalid assumptions. H-E1 failure would indicate spurious dominance does not exist; H-M1 failure indicates the gradient competition mechanism is incorrect but does not invalidate the existence finding.

## Implementation

All experiments are implemented in PyTorch 2.0. GradCAM attribution uses the `pytorch-grad-cam` library. Training checkpoints are saved every 5 epochs to enable retrospective analysis. Code and results are available in the supplementary material.
