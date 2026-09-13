# Methodology

We test the semantic validity hypothesis through controlled experiments on MNIST digit classification, designed to isolate augmentation-induced label noise effects from general training dynamics. Our methodology follows naturally from the core insight: if horizontal flip introduces label noise for asymmetric digits, we should observe (1) differential degradation on asymmetric versus symmetric digit classes, (2) monotonic dose-response where degradation increases with flip probability, and (3) absence of effects under semantically valid augmentation like rotation. This section describes our experimental design, explaining each methodological choice and its rationale.

## Dataset and Task

We use MNIST handwritten digit classification (LeCun et al., 1998): 60,000 training images and 10,000 test images across 10 digit classes {0, 1, ..., 9}, grayscale 28×28 pixels, pixel values normalized to [0, 1]. MNIST is selected for five reasons:

1. **Known baseline performance**: Standard CNNs achieve ~99% test accuracy, establishing a high-quality reference.

2. **Clear semantic asymmetry**: Digits partition cleanly into symmetric {0, 1, 8} and asymmetric {2, 3, 5, 6, 7, 9} classes based on horizontal reflection symmetry.

3. **Established folklore**: Practitioners consistently avoid horizontal flip on MNIST (Kaggle solutions, PyTorch tutorials), providing implicit knowledge to formalize.

4. **Low task complexity**: High baseline accuracy and well-separated classes create a low-noise experimental environment, maximizing statistical power for detecting differential effects.

5. **Computational efficiency**: Fast training (~5 minutes per seed on GPU) enables multi-seed validation with modest resources.

The task is standard supervised classification: map input image x ∈ R^(28×28) to digit label y ∈ {0, ..., 9} by minimizing cross-entropy loss.

## Digit Grouping by Symmetry

A critical design choice is grouping digits by horizontal reflection symmetry rather than analyzing overall accuracy. This grouping operationalizes our semantic validity hypothesis: horizontal flip should harm only asymmetric digits.

**Symmetric digits** {0, 1, 8}: Horizontally flipped images are visually nearly identical to canonical images. For example, digit '0' (ellipse) and digit '8' (stacked loops) have approximate bilateral symmetry; digit '1' (vertical stroke) is symmetric by construction. Flipping these digits produces semantically valid training examples—the flipped image remains a canonical representation of the labeled class.

**Asymmetric digits** {2, 3, 5, 6, 7, 9}: Horizontally flipped images are visually non-canonical or ambiguous. Digit '2' (rightward curve at bottom) becomes a leftward curve when flipped; digit '5' (loop on top-right) becomes top-left; digit '3' (rightward curves) reverses. These flipped images retain their original labels (by augmentation design), creating label noise: the model sees both canonical '2' and mirror-reversed '2', both labeled '2', but only canonical '2' appears in the test set.

We compute per-class test accuracy for all 10 digits, then group by symmetry:
- **Asymmetric accuracy**: Mean accuracy across digits {2, 3, 5, 6, 7, 9} (6 classes)
- **Symmetric accuracy**: Mean accuracy across digits {0, 1, 8} (3 classes)

This grouping increases statistical power (6+3 digit averaging) compared to individual digit analysis, while isolating the semantic validity effect. If flip introduces label noise, asymmetric accuracy should degrade while symmetric accuracy remains stable.

**Why not overall accuracy?** Aggregate metrics obscure class-specific effects. A model may degrade 4% on asymmetric digits while maintaining 99%+ on symmetric digits, yielding 97-98% overall accuracy—strong by most standards, but masking significant class-specific harm. Per-class analysis grouped by semantics reveals the mechanism.

## Augmentation Conditions

We test five augmentation conditions: baseline (no augmentation), three flip probabilities, and rotation control.

### Baseline (No Augmentation)

Training uses only `ToTensor()` and `Normalize(mean=0.1307, std=0.3081)` transformations. This establishes expected MNIST performance (~99% test accuracy) without augmentation-induced effects.

### Horizontal Flip Conditions

We apply `RandomHorizontalFlip(p)` for p ∈ {0.3, 0.5, 0.9}, where p is the probability that a given training image is flipped during each epoch. These probabilities span low (p=0.3), medium (p=0.5), and high (p=0.9) flip rates, enabling dose-response analysis.

**Why these probabilities?** We select discrete levels with large spacing (0.2-0.4 units) to ensure clear differentiation across doses while covering a wide range. Pilot experiments (not shown) confirmed monotonic trends are observable at these levels. Finer granularity (p = 0.1, 0.2, ..., 0.9) is unnecessary given the strong effect size.

**Label preservation**: Crucially, flip augmentation retains original labels. A training image of digit '2' has probability p of being flipped each epoch, but its label remains '2' regardless. This design choice—standard in data augmentation—creates label noise for asymmetric digits: flipped '2' is visually non-canonical but labeled '2'.

### Rotation Control (Semantically Valid Augmentation)

We apply `RandomRotation(degrees=15)`, uniformly sampling rotation angles in [-15°, +15°]. Rotation is selected as a positive control because it is semantically valid for all MNIST digits: rotated '2' remains recognizable as '2', rotated '8' as '8'. Small rotations (±15°) preserve digit identity while introducing visual diversity, serving as a general augmentation baseline.

**Why rotation as control?** This design isolates semantic invalidity from general augmentation effects. Both flip and rotation increase training set diversity and introduce geometric transformations. If degradation were due to increased training noise or visual variation, both flip AND rotation should harm performance. If degradation is specific to semantic invalidity, flip (invalid) should harm asymmetric digits while rotation (valid) should not. The rotation condition tests this distinction.

**Alternative controls considered**: Translation and scaling are also semantically valid but less familiar in practice. Color jitter is inapplicable (MNIST is grayscale). We select rotation for its clarity and prevalence in MNIST augmentation pipelines.

## Model Architecture and Training

We use a standard CNN architecture following PyTorch official MNIST examples (MNISTNet):
- Conv2d(1 → 32, kernel=3) + ReLU + Conv2d(32 → 64, kernel=3) + ReLU
- MaxPool2d(kernel=2)
- Dropout(p=0.25)
- Fully Connected (9216 → 128) + ReLU
- Dropout(p=0.5)
- Fully Connected (128 → 10)

This architecture (~100K parameters, 4 layers) is shallow by modern standards but representative of resource-constrained settings and canonical MNIST baselines. Training hyperparameters are held constant across all conditions:
- **Optimizer**: Adam (learning rate 0.001, default β₁=0.9, β₂=0.999)
- **Batch size**: 64
- **Epochs**: 10 (sufficient for MNIST convergence, baseline reaches ~99% by epoch 5)
- **Loss**: Cross-entropy

**Why standard CNN?** We prioritize experimental control over state-of-the-art performance. Using a well-documented architecture ensures reproducibility and isolates augmentation effects from architectural confounders. Modern architectures (ResNet, Vision Transformers) may exhibit different robustness to label noise—testing these is valuable future work, but standard CNN provides a controlled baseline.

## Experimental Design: Four Sub-Hypotheses

We validate the main semantic validity hypothesis through four sub-hypotheses with escalating rigor:

### h-e1 (EXISTENCE): Proof-of-Concept

**Question**: Does the differential effect exist at all?

**Method**: Single-seed experiment (n=1) testing baseline, flip p=0.5, and rotation conditions. Compute asymmetric and symmetric digit accuracy for each condition.

**Success criteria**: Asymmetric accuracy lower under flip vs. baseline (directional evidence), symmetric accuracy stable (|Δ| < 1%), rotation neutral (asymmetric difference from baseline < 1%).

**Rationale**: Establishes whether the core phenomenon exists before investing in multi-seed validation. Proof-of-concept level.

### h-m1 (MECHANISM): Dose-Response Validation

**Question**: Does degradation increase monotonically with flip probability?

**Method**: Multi-seed experiment (n=5 random seeds) testing flip probabilities p ∈ {0.0, 0.3, 0.5, 0.9}. Compute Spearman rank correlation between flip probability and asymmetric accuracy.

**Success criteria**: Spearman ρ < 0 (negative correlation) with p < 0.05 (statistically significant).

**Rationale**: If label noise is the mechanism, degradation magnitude should be a monotonic function of flip probability (higher p → more label noise → worse accuracy). Dose-response relationships provide stronger evidence than binary comparisons.

### h-c1 (CONDITION): Positive Control Validation

**Question**: Does rotation (semantically valid) show no differential effect?

**Method**: Single-seed experiment (n=1) comparing baseline and rotation conditions. Measure asymmetric vs. symmetric digit differential (Sym_Acc - Asym_Acc) in both conditions.

**Success criteria**: Both differentials < 2% threshold; difference between baseline and rotation differentials < 1%.

**Rationale**: Critical for ruling out alternative explanations. If degradation were due to general augmentation effects (increased training difficulty, visual noise), rotation should also harm asymmetric digits. Observing rotation neutrality isolates semantic invalidity as the causal factor.

### h-m (EXTENDED MECHANISM): Full Causal Chain

**Question**: Can we validate all four causal steps (flip → label noise → training degradation → dose-response)?

**Method**: Multi-seed experiment (n=5) testing all four flip probabilities {0.0, 0.3, 0.5, 0.9} plus rotation control. Compute dose-response correlation and rotation effect.

**Success criteria**: Spearman ρ < 0 with p < 0.05; rotation asymmetric accuracy within 1% of baseline; degradation visible at p=0.3 and increasing through p=0.5, 0.9.

**Rationale**: Comprehensive validation integrating dose-response and control evidence in a single experiment. Confirms all mechanistic steps independently.

## Evaluation Metrics and Statistical Tests

**Per-class accuracy**: For each digit class c ∈ {0, ..., 9}, we compute test accuracy as the fraction of correct predictions on test set images labeled c. This metric isolates class-specific performance, critical for detecting differential effects.

**Group accuracy**: Mean per-class accuracy across digit groups:
- Asymmetric accuracy = mean(Acc₂, Acc₃, Acc₅, Acc₆, Acc₇, Acc₉)
- Symmetric accuracy = mean(Acc₀, Acc₁, Acc₈)

**Dose-response analysis**: For experiments testing multiple flip probabilities, we compute Spearman rank correlation coefficient ρ between flip probability and asymmetric accuracy across all (probability, seed) pairs. Spearman is chosen over Pearson because it tests monotonicity (rank-based) rather than linearity, appropriate for dose-response relationships. Significance is assessed via p-value with α=0.05 threshold.

**Effect size**: We report both raw accuracy differences (percentage points) and Cohen's d for key comparisons (baseline vs. flip, asymmetric vs. symmetric groups).

**Reproducibility**: All experiments use n=5 random seeds (except proof-of-concept h-e1 and h-c1, which use n=1 for speed). We report mean ± standard deviation across seeds and verify low variance (std < 0.2%) to confirm reproducibility.

## Design Rationale Summary

Our methodology directly operationalizes the semantic validity hypothesis:

1. **Per-class accuracy grouped by symmetry**: Tests differential effect prediction—asymmetric digits degrade, symmetric stable.

2. **Dose-response testing**: Tests mechanism prediction—degradation magnitude increases monotonically with flip probability (label noise rate).

3. **Rotation control**: Tests specificity prediction—semantically valid augmentation shows no differential effect, isolating semantic invalidity as causal factor.

These design choices isolate augmentation-induced label noise from confounders (general training noise, model capacity, dataset difficulty) through controlled comparisons. All conditions share identical architecture, hyperparameters, and evaluation protocol; only augmentation type and flip probability vary. This design enables causal attribution: observed differences in asymmetric digit accuracy are attributable to augmentation choice, not experimental artifacts.

The four sub-hypotheses provide hierarchical validation: existence (h-e1) → mechanism (h-m1) → condition (h-c1) → integrated validation (h-m). If all four pass, the main hypothesis is robustly confirmed. If any fail, we identify the boundary conditions where semantic invalidity effects break down. This structured approach follows best practices for experimental validation, progressing from proof-of-concept to comprehensive multi-seed statistical testing.
