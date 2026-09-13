# Experimental Setup

We design experiments to answer three research questions that map directly to our claims:

**RQ1 (Existence):** Do per-sample loss trajectory features predict minority group membership with discriminative power significantly above chance?

**RQ2 (Feature Analysis):** Which trajectory features are most informative for minority prediction, and does this reveal the mechanism underlying trajectory divergence?

**RQ3 (Spurious-Specificity):** Is the trajectory signal specific to spurious correlation conflict, or does it reflect generic sample difficulty?

## Dataset

We evaluate on the **Waterbirds** benchmark [Sagawa et al., 2020], a standard testbed for spurious correlation research. The dataset contains images of waterbirds and landbirds, where bird type is spuriously correlated with background:

| Statistic | Value |
|-----------|-------|
| Training samples | 4,795 |
| Validation samples | 1,199 |
| Test samples | 5,794 |
| Classes | 2 (waterbird, landbird) |
| Groups | 4 (bird type × background) |
| Spurious correlation | 95% (majority have aligned backgrounds) |
| Minority prevalence | ~5% |

**Group definitions:**
- **Majority groups:** Waterbirds on water (G3: 1,057 samples), Landbirds on land (G1: 3,498 samples)
- **Minority groups:** Waterbirds on land (G4: 56 samples), Landbirds on water (G2: 184 samples)

**Why Waterbirds:** This benchmark provides ground-truth group labels for evaluation, enables direct comparison with prior spurious correlation methods, and has been used in 100+ papers establishing its role as a standard testbed. The 95%/5% correlation ratio creates a strong spurious signal that models reliably exploit under ERM training.

## Baselines and Comparisons

**For RQ1 (Existence):**
- **Random baseline:** AUROC = 0.5 (chance level)
- **Success threshold:** AUROC > 0.75 (pre-registered)

**For RQ3 (Spurious-Specificity):**
- **ERM:** Standard empirical risk minimization (baseline condition)
- **GroupDRO:** Group Distributionally Robust Optimization [Sagawa et al., 2020], which specifically targets spurious correlation reliance by minimizing worst-group loss
- **Variance-matched random reweighting:** Control condition matching GroupDRO's gradient variance without targeting spurious correlations

## Implementation Details

**Model architecture.** ResNet-50 pretrained on ImageNet, with the final fully-connected layer replaced for binary classification. Pretrained weights from torchvision.

**Training configuration:**
| Parameter | Value |
|-----------|-------|
| Optimizer | SGD with momentum |
| Learning rate | 0.001 |
| Momentum | 0.9 |
| Weight decay | 0.0001 |
| Batch size | 128 |
| Total epochs | 20 |
| Trajectory extraction | Epochs 1-5 |

**Per-sample loss tracking.** After each training epoch, we run a deterministic evaluation pass over the training set with:
- Data augmentation disabled
- Fixed batch ordering (seeded shuffling)
- Per-sample cross-entropy loss with `reduction='none'`

**GroupDRO configuration.** Group adjustment parameter γ = 0.1, following Sagawa et al. [2020]. Group weights updated after each batch based on per-group losses.

**Variance-matched random reweighting.** We measure gradient variance under GroupDRO training and sample random per-sample weights that produce matching gradient variance, controlling for generic gradient smoothing effects.

**Compute resources.** All experiments run on a single NVIDIA GPU. Training time is approximately 15 minutes per seed for 20 epochs.

**Random seeds.** We use seeds {42, 123, 456, 789, 1011} for statistical robustness. For RQ1 (existence test), we report 5-fold cross-validation results within a single seed. For RQ3 (specificity test), we use 3 seeds per condition.

## Evaluation Metrics

**AUROC (Area Under ROC Curve).** Primary metric for minority prediction. Chosen because:
- Threshold-independent evaluation appropriate for imbalanced classes
- Standard metric for binary classification with 5% minority prevalence
- Enables comparison across different operating points

**Statistical significance.** We report mean ± standard deviation across cross-validation folds or seeds. For AUROC comparisons between conditions, significance assessed at p < 0.05.

**Success criteria:**
- **RQ1:** AUROC > 0.75 (26% above random chance)
- **RQ3:** ΔAUROC_GroupDRO > 0.10 AND ΔAUROC_Random < 0.05

## Trajectory Feature Definitions

We extract four features from the loss matrix L ∈ ℝ^(N×5) (N samples, 5 epochs):

1. **L₁ (Initial Loss):** Loss at epoch 1 — captures immediate spurious feature conflict
2. **Slope:** Linear regression coefficient of loss over epochs — captures learning speed
3. **Variance:** Variance of losses across epochs — captures trajectory instability
4. **Convergence Time:** First epoch where normalized loss (L_t/L_1) < 0.1, or 6 if not reached

These features are designed to capture different aspects of the hypothesized optimization conflict experienced by minority samples.
