# Methodology

Building on our hypothesis that spurious correlation learning creates distinctive per-sample loss patterns, we design a methodology to (1) extract interpretable trajectory features from standard ERM training, (2) evaluate whether these features predict minority group membership, and (3) test whether the signal is spurious-specific rather than reflecting generic sample difficulty.

## Problem Setup

Consider a classification task with training data $\{(x_i, y_i, g_i)\}_{i=1}^{N}$ where $x_i$ is the input, $y_i \in \{0, 1\}$ is the class label, and $g_i \in \{1, 2, 3, 4\}$ is the group label encoding the combination of class and spurious attribute. In the Waterbirds setting, groups are defined by (bird type × background): majority groups have aligned spurious features (waterbirds on water, landbirds on land), while minority groups have conflicting spurious features (waterbirds on land, landbirds on water).

Under standard ERM training, the model minimizes aggregate loss without access to group labels:
$$\mathcal{L}_{ERM} = \frac{1}{N} \sum_{i=1}^{N} \ell(f_\theta(x_i), y_i)$$

Our goal is to determine whether the per-sample loss trajectories $\{\ell_i^{(t)}\}_{t=1}^{T}$ during ERM training encode information that distinguishes minority from majority samples.

## Per-Sample Loss Tracking

We track per-sample cross-entropy loss across training epochs. To obtain clean trajectory signals, we make several design choices:

**Deterministic evaluation passes.** After each training epoch, we run a separate evaluation pass over the training set with data augmentation disabled and batch ordering fixed. This removes stochasticity from augmentation that would add noise to trajectory measurements.

**Per-sample loss computation.** We use `reduction='none'` in the loss function to obtain individual sample losses rather than batch aggregates:
```python
loss_per_sample = F.cross_entropy(logits, targets, reduction='none')
```

**Early-epoch focus.** We extract trajectory features from epochs 1-5, when spurious correlation learning is most active. Later epochs are dominated by fine-tuning dynamics that are less informative for our purpose.

## Trajectory Feature Extraction

From the loss matrix $L \in \mathbb{R}^{N \times T}$ where $L_{i,t}$ is sample $i$'s loss at epoch $t$, we extract four interpretable features per sample:

**Initial Loss (L₁).** The loss value at epoch 1:
$$L_1^{(i)} = L_{i,1}$$
This captures immediate conflict between the sample and early model representations. We hypothesize that minority samples start with higher loss because pretrained features encode spurious correlations that immediately conflict with their true labels.

**Slope.** The linear trend of loss decrease:
$$\text{slope}^{(i)} = \frac{\sum_{t=1}^{T}(t - \bar{t})(L_{i,t} - \bar{L}_i)}{\sum_{t=1}^{T}(t - \bar{t})^2}$$
Majority samples with aligned spurious features should show steeper (more negative) slopes as the shortcut works perfectly for them.

**Variance.** The variability of losses across epochs:
$$\text{var}^{(i)} = \frac{1}{T} \sum_{t=1}^{T} (L_{i,t} - \bar{L}_i)^2$$
Minority samples may exhibit higher variance due to gradient conflict between spurious cues and true class features.

**Convergence Time.** The first epoch where normalized loss drops below a threshold $\tau = 0.1$:
$$\text{conv}^{(i)} = \min\{t : L_{i,t}/L_{i,1} < \tau\}$$
If no convergence occurs within the observation window, we set $\text{conv}^{(i)} = T + 1$.

These features are chosen for interpretability: each captures a distinct aspect of the learning trajectory that maps to intuitions about how spurious correlation learning should differentially affect minority and majority samples.

## Minority Prediction Evaluation

We evaluate whether trajectory features predict minority group membership using binary classification:

**Feature matrix.** For each sample, we construct feature vector $\mathbf{f}_i = [L_1^{(i)}, \text{slope}^{(i)}, \text{var}^{(i)}, \text{conv}^{(i)}]$.

**Minority labels.** We define binary minority labels $m_i = \mathbb{1}[g_i \in \{2, 4\}]$ (groups with conflicting spurious features).

**Classifier.** We train a logistic regression classifier on trajectory features to predict minority labels. Logistic regression is chosen for interpretability and to avoid overfitting on the relatively simple feature space.

**Evaluation.** We use 5-fold stratified cross-validation to compute AUROC, ensuring balanced minority representation in each fold despite the 5% minority prevalence. AUROC is threshold-independent and appropriate for imbalanced binary classification.

**Success criterion.** We require AUROC > 0.75 with statistical significance (p < 0.05) versus random baseline (AUROC = 0.5).

## Spurious-Specificity Test

A critical question is whether trajectory divergence reflects *spurious correlation conflict specifically* or merely *generic sample difficulty*. Hard samples might show distinctive trajectories for reasons unrelated to spurious features.

We design a controlled experiment with three training regimes:

**ERM (baseline).** Standard empirical risk minimization, which learns spurious correlations.

**GroupDRO.** Group Distributionally Robust Optimization [Sagawa et al., 2020], which minimizes worst-group loss and specifically targets spurious correlation reliance:
$$\mathcal{L}_{GroupDRO} = \max_{g \in \mathcal{G}} \mathbb{E}_{(x,y) \sim P_g}[\ell(f_\theta(x), y)]$$
If trajectory divergence reflects spurious feature conflict, GroupDRO training should *attenuate* the signal by reducing spurious reliance.

**Variance-matched random reweighting.** A control condition that matches GroupDRO's gradient variance but without targeting spurious correlations. We sample random per-sample weights with the same variance as GroupDRO's adaptive weights. This controls for the possibility that gradient variance reduction—rather than spurious-targeting—explains any attenuation.

**Hypothesis.** If trajectory divergence is spurious-specific:
- AUROC should decrease substantially under GroupDRO (Δ > 0.10)
- AUROC should remain stable under random reweighting (Δ < 0.05)

If both conditions attenuate similarly, the signal reflects generic gradient effects, not spurious-specificity.

## Implementation Details

**Model.** ResNet-50 pretrained on ImageNet, with the final fully-connected layer replaced for binary classification.

**Training.** SGD optimizer with momentum 0.9, learning rate 0.001, weight decay 0.0001, batch size 128. We train for 20 epochs total but extract trajectory features from epochs 1-5.

**GroupDRO hyperparameters.** Group adjustment parameter γ = 0.1, following Sagawa et al. [2020].

**Variance matching.** For random reweighting, we compute the per-batch gradient variance under GroupDRO and sample random weights that produce matching variance.

**Statistical testing.** We report mean ± standard deviation across seeds. For AUROC comparison, we use DeLong's test for statistical significance.
