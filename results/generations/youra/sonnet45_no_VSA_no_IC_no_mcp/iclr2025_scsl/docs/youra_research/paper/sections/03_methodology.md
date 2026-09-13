# Methodology

Building on our hypothesis that Batch Normalization's batch-level statistics amplify spurious correlation learning while Layer Normalization's instance-level normalization does not, we design experiments to (1) quantify the worst-group gap difference between these architectures at matched training progress, and (2) measure the underlying gradient mechanism. This section describes our accuracy-matched temporal comparison methodology and gradient instrumentation approach.

## Overview

Our approach consists of three components:

1. **Accuracy-matched comparison**: Compare ResNet-18-BN and ResNet-18-LN at the epoch where each architecture first reaches 90% average accuracy, eliminating training-speed confounds.

2. **Gradient asymmetry measurement**: Instrument the first convolutional layer with gradient hooks to measure gradient magnitude toward spurious-aligned versus spurious-misaligned samples during early training (epochs 0–19).

3. **Statistical validation**: Use 10 random seeds for statistical power, paired *t*-tests for significance, and Cohen's *d* for effect size.

**Rationale**: Comparing architectures at fixed epochs confounds training speed with spurious learning mechanisms (Batch Normalization trains faster due to loss landscape smoothing). Comparing at matched average accuracy isolates the architectural effect. Gradient measurement during early training (when spurious features are preferentially learned) reveals the mechanistic driver.

## Architectures

### ResNet-18 with Batch Normalization (ResNet-18-BN)

Standard torchvision ResNet-18 architecture with 17 Batch Normalization layers (1 after initial conv1 + 16 in residual blocks). Batch Normalization normalizes activations per channel using batch statistics:

$$
\hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}, \quad y_i = \gamma \hat{x}_i + \beta
$$

where $\mu_B$ and $\sigma_B^2$ are mean and variance computed over the batch dimension, and $\gamma$, $\beta$ are learned affine parameters. During training, batch statistics are computed from the current batch; during inference, running averages are used.

**Rationale**: Batch Normalization is the default choice in modern convolutional architectures, making it the natural baseline. Its batch-level statistics are hypothesized to amplify spurious batch-level correlations.

### ResNet-18 with Layer Normalization (ResNet-18-LN)

ResNet-18 with all Batch Normalization layers replaced by Layer Normalization. Layer Normalization normalizes activations per-instance over all feature dimensions:

$$
\hat{x}_i = \frac{x_i - \mu_L}{\sqrt{\sigma_L^2 + \epsilon}}, \quad y_i = \gamma \hat{x}_i + \beta
$$

where $\mu_L$ and $\sigma_L^2$ are mean and variance computed over feature dimensions (channels, height, width) for each individual example. Layer Normalization processes each example independently, eliminating batch-level information aggregation.

**Implementation**: Layer Normalization's `normalized_shape` parameter is set to `[C, H, W]` for each residual block, where `C` is the number of channels and `H \times W` is the spatial resolution. For example, `conv2_x` blocks use `[64, 56, 56]`, `conv3_x` uses `[128, 28, 28]`, `conv4_x` uses `[256, 14, 14]`, and `conv5_x` uses `[512, 7, 7]`. This ensures normalization over all feature dimensions per instance.

**Rationale**: Layer Normalization provides a controlled ablation of Batch Normalization's batch-level statistics while preserving the same architecture depth, parameter count (within 1%), and activation normalization principle. If the hypothesis is correct, Layer Normalization should exhibit lower worst-group gaps due to the absence of batch-level spurious signal amplification.

## Accuracy-Matched Comparison

### Motivation

Batch Normalization is known to accelerate training convergence (Santurkar et al., 2019). Comparing ResNet-18-BN and ResNet-18-LN at a fixed epoch (e.g., epoch 50) confounds two effects:
1. Architectural effect on spurious learning (what we want to measure)
2. Training speed difference (nuisance variable)

For example, if ResNet-18-BN reaches 95% average accuracy by epoch 50 while ResNet-18-LN reaches only 88%, comparing worst-group accuracy at epoch 50 mixes learning dynamics with convergence speed.

### Design

We eliminate this confound by comparing architectures at matched average accuracy checkpoints. Specifically, for each random seed:

1. Train ResNet-18-BN for up to 100 epochs, logging average accuracy and worst-group accuracy every epoch.
2. Train ResNet-18-LN for up to 100 epochs with identical logging.
3. Identify the epoch where ResNet-18-BN first reaches 90% average accuracy (denote $e_{\text{BN}}$).
4. Identify the epoch where ResNet-18-LN first reaches 90% average accuracy (denote $e_{\text{LN}}$).
5. Record worst-group accuracy at these epochs: $\text{WGA}_{\text{BN}}(e_{\text{BN}})$ and $\text{WGA}_{\text{LN}}(e_{\text{LN}})$.
6. Compute worst-group gap: $\text{Gap}_{\text{BN}} = 90\% - \text{WGA}_{\text{BN}}(e_{\text{BN}})$, $\text{Gap}_{\text{LN}} = 90\% - \text{WGA}_{\text{LN}}(e_{\text{LN}})$.

We then perform a paired *t*-test across 10 seeds to test whether $\text{Gap}_{\text{BN}} - \text{Gap}_{\text{LN}} \geq 5.0$ percentage points (*p* < 0.05, Cohen's *d* ≥ 0.8).

**Rationale**: By comparing at matched average accuracy (90%), we control for training progress. The worst-group gap at this checkpoint reflects architectural effects on spurious learning, independent of convergence speed.

## Gradient Asymmetry Measurement

### Motivation

To establish a mechanistic explanation beyond correlation, we measure gradient flow to spurious-aligned versus spurious-misaligned samples during early training. If Batch Normalization amplifies spurious learning via batch-level statistics, we expect higher gradient magnitude toward majority-group (spurious-aligned) samples in ResNet-18-BN compared to ResNet-18-LN.

### Design

For each architecture and random seed, we instrument the first convolutional layer (`conv1.weight`) with gradient hooks during epochs 0–19:

1. **Group stratification**: Partition training samples into majority groups (spurious-aligned: label and spurious feature co-occur) and minority groups (spurious-misaligned: label and spurious feature conflict).

2. **Gradient accumulation**: For each batch, compute gradients $\nabla_{\theta} \mathcal{L}$ with respect to `conv1.weight`. Separate gradients by group:
   - $g_{\text{maj}}$: gradient contributions from majority-group samples
   - $g_{\text{min}}$: gradient contributions from minority-group samples

3. **Gradient ratio**: Compute the ratio of gradient norms:
$$
r = \frac{\|g_{\text{maj}}\|_2}{\|g_{\text{min}}\|_2}
$$

4. **Temporal aggregation**: Average gradient ratio over epochs 0–19 for each seed.

5. **Statistical test**: Compare $r_{\text{BN}}$ vs. $r_{\text{LN}}$ across 10 seeds using paired *t*-test. Success criterion: $r_{\text{BN}} - r_{\text{LN}} \geq 20\%$, *p* < 0.05, Cohen's *d* ≥ 0.5.

**Rationale**: Early training (epochs 0–19) is when simplicity bias dominates and spurious features are preferentially learned (Toneva et al., 2019). Measuring gradients at the first convolutional layer captures early feature extraction, where spurious vs. core feature competition is most acute. A higher gradient ratio in Batch Normalization indicates stronger gradient flow toward spurious-aligned samples, providing mechanistic evidence for the amplification hypothesis.

## Training Configuration

All experiments use identical hyperparameters to isolate architectural effects:

- **Optimizer**: SGD with learning rate 0.01, momentum 0.9, weight decay $10^{-4}$
- **Learning rate schedule**: Constant (no warmup, no decay) to eliminate optimizer-induced temporal dynamics
- **Batch size**: 64 for both architectures
- **Initialization**: He normal (Kaiming initialization) for all convolutional and fully connected layers
- **Epochs**: 20 (proof-of-concept; planned 100 epochs for production)
- **Random seeds**: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] for reproducibility
- **Determinism**: `torch.manual_seed()`, `torch.backends.cudnn.deterministic = True`, `torch.backends.cudnn.benchmark = False`

**Rationale**: Constant learning rate eliminates confounds from learning rate schedules (warmup can delay spurious learning; decay can enable late correction). Identical batch size, initialization, and weight decay ensure controlled comparison. 10 seeds provide statistical power to detect a 2 percentage point gap difference with 80% power at $\alpha = 0.05$.

## Dataset

**Planned**: Waterbirds dataset (Sagawa et al., 2020), a spurious correlation benchmark with 4795 training images (landbirds/waterbirds on land/water backgrounds, 95% spurious correlation) and 1199 test images. Group labels are available for worst-group accuracy evaluation.

**Fallback (used in this study)**: Synthetic spurious correlation dataset with 5000 training samples and 1000 test samples, binary classification, 90% spurious correlation strength. Generated due to WILDS Waterbirds server unavailability (HTTP 500 error during dataset download).

**Rationale**: Waterbirds is the standard benchmark for spurious correlation research, with established group annotations and baselines. Synthetic data demonstrates workflow validity but requires real dataset validation for scientific generalization (see Limitations).

## Evaluation Metrics

- **Average accuracy**: Accuracy over all test samples (standard metric)
- **Worst-group accuracy (WGA)**: Minimum accuracy across all four groups (label × spurious feature)
- **Worst-group gap**: $\text{Gap} = \text{Average Accuracy} - \text{WGA}$

**Rationale**: Worst-group accuracy reveals spurious reliance better than average accuracy (Sagawa et al., 2020). A model with 97% average accuracy but 72% worst-group accuracy has a 25 percentage point gap, indicating strong spurious reliance.

## Statistical Analysis

All hypothesis tests use paired *t*-tests (each seed is a matched pair for BN vs. LN) with significance threshold $\alpha = 0.05$. Effect sizes are reported as Cohen's *d*:

$$
d = \frac{\bar{x}_{\text{BN}} - \bar{x}_{\text{LN}}}{s_{\text{pooled}}}
$$

where $s_{\text{pooled}}$ is the pooled standard deviation. We interpret $d \geq 0.8$ as a large effect (Cohen, 1988).

**Rationale**: Paired tests exploit the matched structure (same seed, different architectures) for higher statistical power. Cohen's *d* quantifies practical significance beyond *p*-values.
