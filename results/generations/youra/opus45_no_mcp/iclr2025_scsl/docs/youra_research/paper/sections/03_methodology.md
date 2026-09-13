# Methodology

Our goal is to detect when classifier commitment to spurious features accelerates—the crystallization point. We approach this as a signal detection problem: identify a characteristic signature in training dynamics that marks the transition.

## Overview

The crystallization zone represents a phase where worst-group accuracy (WGA) decline accelerates. While WGA decreases throughout early ERM training, the rate of decline is not constant. We hypothesize that crystallization manifests as a localized acceleration—a negative second derivative—rather than gradual monotonic decline.

Our detection pipeline consists of three stages: (1) dense WGA tracking during training, (2) smoothing to reduce noise, and (3) second derivative computation with peak detection.

## Worst-Group Accuracy Tracking

We compute worst-group accuracy at every epoch during training. For a dataset with group annotations (spurious attribute × label), WGA is the minimum accuracy across all groups:

$$\text{WGA} = \min_{g \in \mathcal{G}} \frac{1}{|D_g|} \sum_{(x,y) \in D_g} \mathbf{1}[\hat{y}(x) = y]$$

where $\mathcal{G}$ is the set of groups and $D_g$ is the subset of data belonging to group $g$. On Waterbirds, groups are defined by (bird type × background): the worst group is typically waterbirds on land backgrounds.

Dense checkpointing (every epoch) is essential. Coarser intervals may miss the crystallization peak or shift its apparent timing.

## Smoothing

Raw WGA curves exhibit epoch-to-epoch noise due to batch sampling variance. We apply a rolling average with a window of 5 epochs:

$$\text{WGA}_{\text{smooth}}(t) = \frac{1}{5} \sum_{i=t-2}^{t+2} \text{WGA}(i)$$

The choice of 5-epoch window balances noise reduction with temporal resolution. Our sensitivity analysis (H-M3) confirms that windows of 3, 5, or 7 epochs all achieve 100% detection rate, with 5 epochs providing optimal signal-to-noise ratio.

## Second Derivative Detection

We compute the second derivative using central differences on the smoothed WGA:

$$\frac{d^2\text{WGA}}{dt^2}(t) = \text{WGA}_{\text{smooth}}(t+1) - 2 \cdot \text{WGA}_{\text{smooth}}(t) + \text{WGA}_{\text{smooth}}(t-1)$$

A significant negative peak in $d^2\text{WGA}/dt^2$ indicates accelerating decline—the crystallization signature. We detect peaks using the following criteria:

1. **Prominence threshold**: Peak magnitude must exceed 0.005 (absolute value)
2. **Search window**: Peak must occur in the first 50% of training
3. **Signal-to-noise ratio**: Peak magnitude must be at least 2× the baseline noise level

The crystallization epoch is defined as the location of the most prominent negative peak satisfying these criteria.

## Linear Probe Analysis

To verify that crystallization represents classifier commitment rather than representation degradation, we analyze feature representations using linear probes.

At each checkpoint, we extract penultimate layer activations and train two logistic regression classifiers:
- **Spurious probe**: Predicts the spurious attribute (e.g., background for Waterbirds)
- **Core probe**: Predicts the true label (e.g., bird species)

If crystallization were a representation-level phenomenon, we would expect core probe accuracy to decrease while spurious probe accuracy increases. Instead, following Kirichenko et al. (2023), we expect both probes to achieve high accuracy—indicating that representations contain both features, while the classifier weights favor spurious ones.

## Gradient Ratio Tracking

To verify the causal role of gradient starvation, we track the gradient ratio between minority and majority group examples:

$$\text{Gradient Ratio}(t) = \frac{\|\nabla_\theta \mathcal{L}_{\text{minority}}\|}{\|\nabla_\theta \mathcal{L}_{\text{majority}}\|}$$

where gradients are averaged over examples in each group. If gradient starvation causes crystallization, we expect:
1. The gradient ratio to decrease during early training (minority gradients starved)
2. An inflection point in the gradient ratio to *precede* the WGA crystallization peak

This temporal ordering—gradient inflection before WGA acceleration—confirms causal precedence.

## Experimental Protocol

We train ResNet-50 models on three benchmarks using standard ERM with the following configuration:

| Parameter | Value |
|-----------|-------|
| Optimizer | SGD with momentum 0.9 |
| Learning rate | 0.001 (constant) |
| Weight decay | 1e-4 |
| Batch size | 128 |
| Epochs | 50-100 (benchmark-dependent) |

Constant learning rate eliminates confounds from learning rate schedules. We run 5 seeds per benchmark and report mean and variance.

## Detection Evaluation Metrics

We evaluate our detection method using:

1. **Detection rate**: Fraction of runs where a valid crystallization peak is detected
2. **Timing variance**: Standard deviation of detected peak timing (in epochs) across seeds
3. **Signal-to-noise ratio (SNR)**: Peak magnitude divided by baseline noise level
4. **Normalized timing**: Peak timing as percentage of total training duration

For the method to be practical, we target: detection rate > 80%, timing variance < 5 epochs, SNR > 2.0.
