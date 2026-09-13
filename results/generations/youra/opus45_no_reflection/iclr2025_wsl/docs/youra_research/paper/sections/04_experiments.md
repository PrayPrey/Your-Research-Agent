# Experimental Setup

## 4.1 Dataset

**Small CNN Zoo.** We use the Small CNN Zoo, a collection of convolutional neural networks trained on CIFAR-10 with systematic hyperparameter variation. The full zoo contains approximately 30,000 models; we use a filtered subset of 193 final-epoch models with complete metadata and stored predictions.

**Architecture.** All models share the same architecture: 3 convolutional layers followed by 2 fully-connected layers, with approximately 12,000 trainable parameters per model. This homogeneity enables direct weight comparison without architecture alignment.

**Variation Sources.** Models differ in:
- Learning rate (log-uniform sampling)
- Batch size (discrete set)
- Optimizer (SGD variants)
- Weight initialization seed
- Data augmentation settings

**Stored Data.** For each model, the zoo provides:
- Final-epoch weights (all layers)
- Per-sample predictions on CIFAR-10 test set
- Overall test accuracy
- Training configuration metadata

**Sample Size Limitation.** Our 193-model subset is 150× smaller than the full zoo. This affects statistical power for the 25-feature regression in H-M1. We note this as a primary limitation; H-E1 (variance decomposition) is less sensitive to sample size.

## 4.2 Experimental Protocol

### H-E1: Behavioral Variance Existence

**Data Preparation.** From stored predictions, we compute class-wise accuracy vectors for all 193 models, yielding a 193 × 10 accuracy matrix.

**Baseline Fitting.** We fit per-class linear models predicting class accuracy from overall accuracy using ordinary least squares on all 193 models.

**Metric Computation.** We compute the residual variance ratio as the fraction of class-wise variance not explained by the stratified baseline.

**Threshold.** We use 0.05 (5%) as the minimum residual ratio to indicate meaningful behavioral variance. This threshold reflects our judgment that less than 5% unexplained variance would be practically negligible.

### H-M1: Weight Feature Mechanism

**Feature Extraction.** For each of 193 models, we extract 5 statistics (mean, std, min, max, L2 norm) from each of 5 layers (3 conv + 2 FC), yielding 25 features per model.

**Train/Test Split.** We use 80/20 random split (154 train, 39 test) with fixed random seed for reproducibility.

**Model Training.** Ridge regression with α = 1.0, trained separately for each of 10 classes on the training set.

**Evaluation.** We compute per-class R² on the held-out test set, comparing weight-feature predictions against stratified baseline predictions.

**Success Criterion.** Mean ΔR² > 0 across classes indicates weight features capture behavioral variance beyond baseline.

## 4.3 Evaluation Metrics

| Metric | Hypothesis | Description | Threshold |
|--------|------------|-------------|-----------|
| Residual Ratio | H-E1 | Fraction of variance unexplained by stratified baseline | > 0.05 |
| Per-Class Variance σ²_c | H-E1 | Variance of residuals per class | Descriptive |
| Weight R² | H-M1 | R² of Ridge regression from weight features | — |
| Baseline R² | H-M1 | R² of stratified baseline predictions | — |
| ΔR² | H-M1 | Weight R² − Baseline R² | > 0 |

## 4.4 Reproducibility

**Code.** All experiments implemented in Python with scikit-learn for regression and NumPy for statistics.

**Data Access.** Small CNN Zoo available via the HSG-AIML model zoo repository on Zenodo.

**Random Seeds.** Fixed seeds for train/test splitting; results should reproduce exactly.

**Compute.** Experiments run on standard CPU hardware; no GPU required for statistical analysis.
