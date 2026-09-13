# 4. Experiments

We designed experiments to test three claims: (1) weight statistics enable binary depth classification above chance, (2) discriminative features are architectural rather than training-induced, (3) depth signals are robust within architecture families. Each hypothesis tests specific predictions about mechanism and generalization.

## 4.1 H-E1: Existence of Weight-Based Depth Discrimination

**Experimental Question.** Do aggregated weight statistics enable binary depth classification above 70% threshold?

**Feature Extraction.** We computed Frobenius norms for all Conv2d layer weights across 20 models, then aggregated into four global statistics: mean, std, min, max of layer-wise norms. This tests whether simple summary statistics implicitly encode depth.

**Hypothesis.** Deeper networks would show systematically different weight magnitude distributions due to either training dynamics (gradient accumulation across many layers) or architectural properties (parameter count scaling with depth).

**Expected Outcome.** ≥70% test accuracy would validate existence of depth-discriminative weight statistics. Perfect separation (100%) would exceed expectations and suggest very strong architectural signatures.

**Execution.** Train logistic regression on 16 models, test on 4 held-out models. Report train accuracy (overfitting check), test accuracy (primary metric), and feature importance (logistic coefficients).

## 4.2 H-M1: Gradient Flow Mechanism Test

**Experimental Question.** Are discriminative features training-induced (gradient accumulation) or architectural (network definition)?

**Feature Extraction.** Six features designed to capture gradient flow patterns: norm slope (layer progression), norm variance (gradient instability), input/output layer norms (gradient endpoints), depth-weighted norm (position-sensitive aggregation), layer count (depth proxy).

**Hypothesis.** If backpropagation through 50+ layers creates characteristic gradient accumulation patterns, pretrained models should show depth-specific weight progressions absent in randomly initialized models. High accuracy on pretrained models with degraded performance on random models would support gradient flow mechanism.

**Critical Test: Random Initialization.** Load same 20 architectures with `pretrained=False`, extract identical features, train separate classifier. Compare accuracy: pretrained vs random.

**Expected Outcome.** Performance gap (pretrained > random) would indicate training-induced features. No gap would indicate architectural features, refuting gradient flow hypothesis.

**Execution.** Train on 16 pretrained models, test on 4 pretrained models (primary result). Repeat with 16 random models training, 4 random models testing (mechanism validation). Report accuracy gap as key diagnostic.

## 4.3 H-M2: Architectural Constraints Mechanism Test

**Experimental Question.** Which architectural properties create depth signatures?

**Feature Extraction.** Eight explicit architectural features: residual block count (ResNet stages), dense connection count (DenseNet), bottleneck ratio (1×1 conv prevalence), layer count, skip connections, residual path norms, transition layers, architecture family (one-hot). These features directly measure structural properties.

**Hypothesis.** Architectural design patterns (residual blocks for training very deep networks, bottleneck layers for parameter efficiency, dense connections for feature reuse) systematically differ between shallow and deep models. High accuracy with interpretable feature importance would identify which properties discriminate depth.

**Within-Family Validation.** Train separate classifiers on ResNet-only and DenseNet-only subsets. Test whether depth signal exists within single architecture family, controlling for family-specific design patterns (ResNet residual blocks vs DenseNet dense connections).

**Random Initialization Test.** Same protocol as H-M1. Expected outcome: no performance gap (features are architectural by definition).

**Expected Outcome.** ≥70% accuracy with high importance for layer count, bottleneck ratio, residual/dense blocks. Within-family accuracy ≥65% would confirm depth signals beyond family differences. Feature importance analysis identifies primary discriminators.

**Execution.** Full dataset: train on 16, test on 4. ResNet-only: train/test split on 9 models. DenseNet-only: train/test split on 4 models. Report feature coefficients and within-family accuracy.

## 4.4 H-M3: Batch Normalization Mechanism Test

**Experimental Question.** Does batch normalization layer count (architectural) or learned BN statistics (training-induced) enable depth classification?

**Feature Extraction.** Six BN-specific features: BN layer count, gamma parameter mean/std, beta parameter mean/std, depth-weighted BN norm. VGG models have zero BN layers (legacy architecture), creating edge case.

**Hypothesis.** Modern architectures place BN after each convolution, so BN layer count scales linearly with depth. Learned gamma/beta statistics might also encode training-induced patterns. Feature importance analysis distinguishes architectural (BN count) from training-induced (gamma/beta stats) contributions.

**Expected Outcome.** Moderate accuracy (60-80%) with BN layer count dominating importance, suggesting architectural contribution. Lower accuracy than H-M2 would indicate BN is weaker signal than comprehensive architectural features.

**Execution.** Train on 16 models (including VGG with 0 BN), test on 4. Within-family validation for ResNet and DenseNet (both use BN), excluding VGG. Random initialization test.

## 4.5 Fairness and Reproducibility

**Consistent Protocol Across Hypotheses:**
- Same train-test split (stratified 80/20, seed 42)
- Same classifier (LogisticRegression, C=1.0, max_iter=1000, seed 42)
- Same normalization (StandardScaler)
- Same evaluation metrics (train/test accuracy, confusion matrix)
- Same random initialization protocol (pretrained=False)

**Confounding Variables:**
- Depth, width, and architecture family are inherently confounded (deep models are systematically wider and use different design patterns)
- Within-family validation partially controls for family differences
- Cannot fully isolate "pure depth" effect without synthetic architectures

**Computational Cost:**
- Feature extraction: <5 seconds per hypothesis (no forward passes)
- Training: <1 second (logistic regression on 16 samples)
- Total per hypothesis: <60 seconds including random tests
- Hardware: NVIDIA H100 NVL (95GB), though CPU-only would suffice

**Limitations Acknowledged:**
- Small test set (n=4) limits statistical confidence (addressed via within-family validation)
- Binary classification only (continuous regression is future work)
- Limited architecture families (ResNet/VGG/DenseNet, 2015-2017 era)
- ImageNet pretraining only (dataset generalization untested)
