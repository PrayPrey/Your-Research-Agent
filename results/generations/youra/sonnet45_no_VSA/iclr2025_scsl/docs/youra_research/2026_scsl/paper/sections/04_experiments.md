# 4. Experiments

We design experiments to test three specific predictions from our semantic invalidity hypothesis: (1) horizontal flip degrades asymmetric digit accuracy while leaving symmetric digits stable, (2) degradation increases monotonically with flip probability (dose-response), and (3) the effect is specific to semantically invalid augmentation, not general augmentation effects.

## 4.1 Experimental Questions

Our experimental design operationalizes the semantic validity hypothesis through three interrelated questions:

**Q1: Does horizontal flip cause differential degradation?** If flip introduces label noise by creating non-canonical asymmetric digit images, we predict asymmetric digit accuracy (classes {2,3,5,6,7,9}) will decrease significantly under flip augmentation compared to baseline, while symmetric digit accuracy (classes {0,1,8}) remains stable. We test this via per-class accuracy grouped by digit symmetry at flip probability p=0.5, with statistical validation using Wilcoxon signed-rank test (p<0.05) and effect size measurement via Cohen's d (threshold d≥0.5).

**Q2: Is degradation dose-dependent?** If label noise is the mechanism, degradation magnitude should be a monotonic function of flip probability—higher p → more label-noisy training examples → stronger test accuracy degradation. We test flip probabilities p ∈ {0.3, 0.5, 0.9} plus baseline (p=0.0), computing Spearman rank correlation between flip probability and asymmetric digit accuracy. Our threshold for mechanism validation is ρ<0 with p<0.05, but stronger evidence (ρ approaching -1.0) would indicate a deterministic relationship.

**Q3: Is the effect specific to semantic invalidity?** To isolate semantic invalidity from general augmentation effects (training noise, increased visual diversity, regularization), we compare horizontal flip against rotation ±15°—a semantically valid augmentation where rotated asymmetric digits remain recognizable as their original class. If semantic invalidity is the causal factor, rotation should show no differential effect on asymmetric versus symmetric digits (threshold: |difference| < 1-2%), while flip should cause significant asymmetric degradation.

## 4.2 Experimental Protocol

**Dataset.** We use MNIST handwritten digits (60,000 train / 10,000 test images, 28×28 grayscale, 10 classes) for four reasons: (1) well-established baseline performance (~99% overall accuracy) enables precise degradation measurement, (2) clear semantic asymmetry exists (digits 2,3,5 versus 0,1,8), (3) practitioner folklore explicitly avoids flip on MNIST (Kaggle competition winners, PyTorch official tutorials), providing a real-world validation target, and (4) fast training (~5 minutes per seed on standard GPU) enables multi-seed statistical validation. We acknowledge MNIST is a controlled, low-complexity dataset; generalization to Fashion-MNIST, CIFAR-10, and medical imaging is documented as future work (Section 6).

**Model Architecture.** All experiments use a standard convolutional neural network (PyTorch MNISTNet): two convolutional layers (32→64 channels), ReLU activations, 2×2 max pooling, dropout (0.25 after conv, 0.5 after first FC layer), and two fully connected layers (128→10). This ~100K-parameter architecture is deliberately shallow to test the effect on resource-constrained models common in edge deployment scenarios. Modern architectures (ResNet, Vision Transformers, pre-trained models) may exhibit different robustness; this is documented as a principled limitation requiring future empirical validation.

**Training Configuration.** We maintain strict hyperparameter consistency across all conditions: SGD optimizer with Nesterov momentum (lr=0.01, momentum=0.9), batch size 64, 10 epochs, cross-entropy loss. Each experimental condition is trained with n=5 random seeds to quantify seed variability and enable statistical testing. The only varying factor across conditions is the augmentation strategy, allowing us to isolate augmentation effects.

**Augmentation Conditions.** We test five conditions:
- **Baseline:** `ToTensor` + `Normalize(mean=0.1307, std=0.3081)` only (no augmentation)
- **Flip30, Flip50, Flip90:** Baseline + `RandomHorizontalFlip(p={0.3, 0.5, 0.9})`
- **Rotation:** Baseline + `RandomRotation(degrees=15)` (positive control)

Flip probabilities {0.3, 0.5, 0.9} are chosen to span low, moderate, and high augmentation rates, enabling dose-response curve fitting. Rotation ±15° preserves digit recognizability (rotated '2' remains visually identifiable as '2') while providing comparable visual diversity to flip.

**Evaluation Metrics.** We measure per-class test accuracy for all 10 digits, then aggregate by symmetry groups: asymmetric = mean({2,3,5,6,7,9}), symmetric = mean({0,1,8}). This grouping increases statistical power (6+3 samples per group versus individual digit analysis) and directly tests the semantic invalidity prediction (asymmetric-specific degradation). We report overall accuracy for context but focus on group-level metrics to reveal class-specific effects that aggregate metrics would mask.

**Statistical Testing.** For differential effect (Q1), we use Wilcoxon signed-rank test (paired comparison: baseline vs flip50, same architecture/hyperparameters) with significance threshold p<0.05. For dose-response (Q2), we compute Spearman rank correlation across {baseline, flip30, flip50, flip90} × 5 seeds = 20 data points, testing null hypothesis ρ=0 against alternative ρ<0 (negative correlation). For rotation control (Q3), we compare asymmetric digit accuracy differences: |rotation_asym - baseline_asym| versus threshold 1-2% (domain expertise: differences <1% are practically negligible on MNIST).

## 4.3 Controlled Design Rationale

Our experimental design incorporates three critical controls to isolate semantic invalidity as the causal mechanism:

**Positive Control (Rotation).** Rotation ±15° serves as a "semantically valid augmentation" control. Unlike flip, rotation preserves digit class identity—a rotated asymmetric digit remains recognizable as the original class (e.g., rotated '2' is still a '2', not visually ambiguous). If the degradation we observe under flip were due to general augmentation effects (increased training noise, visual diversity exceeding model capacity, regularization artifacts), we should see similar degradation under rotation. Observing neutral/beneficial rotation effects while flip causes degradation confirms that semantic invalidity (not augmentation per se) is the causal factor.

**Negative Control (Symmetric Digits).** Symmetric digits {0,1,8} are flip-invariant by geometry—flipped '0' is visually identical to canonical '0'. Under our label noise mechanism, these digits should show minimal degradation because flip does not create semantically invalid images for symmetric classes. This within-dataset control (comparing asymmetric vs symmetric digit groups under identical training conditions) strengthens causal inference: if flip harms only asymmetric digits while symmetric digits remain stable, the effect is class-specific and tied to geometric asymmetry, not a global training artifact.

**Dose-Response Design.** Testing multiple flip probabilities {0.3, 0.5, 0.9} rather than a single binary comparison (flip on/off) provides mechanistic evidence. If label noise is the causal mechanism, degradation should scale with flip probability—more flipped images in training → higher proportion of label-noisy examples → stronger degradation. A monotonic dose-response relationship (tested via Spearman correlation) is stronger evidence for a causal mechanism than a single effect size measurement. Perfect monotonicity (ρ approaching -1.0) would indicate a deterministic, not merely correlational, relationship.

## 4.4 Threats to Validity and Mitigation

**Internal Validity (Confounding).** Alternative explanations for observed degradation include: (a) effective dataset size differences (higher flip probability → more augmented images per epoch), (b) optimizer dynamics (augmentation may interact with SGD momentum), (c) random seed variation masking true effect. We mitigate (a) by comparing flip vs rotation at equivalent augmentation rates—both generate similar numbers of augmented images, but only flip should degrade if semantic invalidity is causal. We address (b) by holding all training hyperparameters constant except augmentation strategy. We handle (c) via multi-seed validation (n=5 seeds) and statistical testing rather than single-run comparisons.

**External Validity (Generalization).** Our findings are specific to MNIST digits with standard CNN architecture. Effect size and mechanism may differ on: (1) datasets with higher inter-class similarity (Fashion-MNIST, CIFAR-10), (2) datasets with critical orientation semantics (medical imaging: anatomical left/right), (3) deeper architectures (ResNet-50, Vision Transformers), or (4) pre-trained models (ImageNet → MNIST fine-tuning, which may have learned flip-invariance during pre-training). We document these as principled limitations (Section 6) and propose systematic follow-up experiments. Our claim is bounded: semantic invalidity causes degradation on MNIST with standard CNN; the principle (augmentations violating domain symmetries introduce label noise) is hypothesized to generalize, but effect sizes are dataset/architecture-dependent.

**Measurement Validity.** Per-class accuracy may be sensitive to class imbalance (MNIST is balanced, but test set noise or annotation errors could bias results). We verify MNIST test set quality (known to be high-quality, minimal label noise) and use balanced accuracy computation (no class weighting needed for MNIST). Seed variability (random initialization, SGD stochasticity) is quantified via standard deviation across 5 seeds; observed variability is <0.12%, much smaller than effect sizes (0.37-4.10 pp), confirming signal exceeds noise.

## 4.5 Experimental Hypotheses (Hierarchical Validation)

We structure experiments into four sub-hypotheses with increasing rigor, following Phase 4 hypothesis validation protocol:

- **h-e1 (EXISTENCE):** Proof-of-concept with single seed (n=1) demonstrating differential effect exists. Gate criteria: baseline accuracy ≥98%, asymmetric degradation at flip50 > symmetric degradation, rotation control |difference| < 1%. Purpose: Fast directional evidence before committing to multi-seed statistical validation.

- **h-m1 (MECHANISM):** Statistical validation of dose-response with multi-seed rigor (n=5). Gate criteria: Spearman ρ<0 and p<0.05, monotonic degradation observed across {flip30, flip50, flip90}. Purpose: Confirm mechanism via perfect dose-response correlation.

- **h-c1 (CONDITION):** Positive control validation focusing on rotation ±15° neutrality. Gate criteria: rotation differential (sym - asym) < 2%, baseline differential < 2%, difference between conditions < 1%. Purpose: Isolate semantic invalidity from general augmentation effects.

- **h-m (EXTENDED MECHANISM):** Comprehensive causal chain validation with all four mechanistic steps observable, combining dose-response, rotation control, and per-digit heterogeneity analysis. Gate criteria: All h-m1 criteria plus rotation control replication and per-digit degradation analysis. Purpose: Full mechanistic validation with independent implementation replicating h-m1 findings.

All four sub-hypotheses must pass their respective gate criteria for overall hypothesis validation. This hierarchical structure (existence → mechanism → control → extended validation) follows best practices in empirical hypothesis testing, building confidence incrementally while enabling early termination if existence-level evidence fails.
