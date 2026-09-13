# 3. Methodology

We designed a controlled experiment to test the **Architectural Determinism Hypothesis**: that architectural depth creates deterministic fingerprints in weight statistics detectable even in untrained models. Our approach uses binary classification with multiple feature types, validated through random initialization testing to isolate architectural from training-induced signals.

## 3.1 Dataset and Task Definition

**Model Pool.** We collected 20 pretrained convolutional neural networks from PyTorch torchvision, spanning three architecture families: ResNet (9 models), VGG (4 models), and DenseNet (4 models), plus AlexNet, SqueezeNet, and MobileNetV2. All models were pretrained on ImageNet-1K with standard training recipes, minimizing confounding variables from different training protocols.

**Depth Classification Task.** We formulated depth detection as binary classification: shallow (≤34 layers) versus deep (≥50 layers). This threshold creates balanced classes (10 shallow, 10 deep) and maximizes effect size for an existence proof. The gap between 34 and 50 layers avoids ambiguous mid-depth models. Shallow models include ResNet-18/34, all VGG variants (11-19 layers), and DenseNet-121. Deep models include ResNet-50/101/152 and variants, plus DenseNet-161/169/201.

**Train-Test Split.** We used stratified 80/20 splitting (16 train, 4 test) with fixed random seed 42 for reproducibility. Test models were: alexnet (shallow), vgg13 (shallow), resnet152 (deep), wide_resnet50_2 (deep).

**Success Criteria.** Primary threshold: ≥70% test accuracy (substantially above 50% chance baseline). Secondary threshold: ≥65% within-family accuracy to confirm depth signal exists beyond architecture family differences.

## 3.2 Feature Extraction

We tested three feature representations to assess whether architectural depth is redundantly encoded:

**Global Weight Statistics (H-E1).** We computed layer-wise Frobenius norms for all weight tensors, then aggregated into four global statistics: mean, standard deviation, minimum, and maximum. This tests whether simple summary statistics implicitly capture depth through parameter count and weight distributions. Frobenius norm for a weight tensor W: ||W||_F = sqrt(sum(W_{ij}^2)).

**Layer-Wise Progression Features (H-M1).** We extracted six features characterizing how weight norms progress through layers: (1) linear regression slope of layer-wise norms, (2) variance of layer-wise norms, (3) mean norm of first layer, (4) mean norm of last layer, (5) depth-weighted norm sum (sum of position × norm), (6) layer count. These features were designed to capture gradient flow patterns but, as validation reveals, actually proxy architectural depth.

**Explicit Architectural Features (H-M2).** We directly extracted eight architectural properties: (1) residual block count (modules with downsample attribute), (2) dense connection count (layers with "denselayer" naming), (3) bottleneck ratio (1×1 convolutions / total convolutions), (4) layer count, (5) skip connection count, (6) residual path norm, (7) transition layer count, (8) architecture family (one-hot encoded). These features explicitly measure structural properties by definition.

**Batch Normalization Features (H-M3).** We extracted six BN-specific features: (1) BN layer count, (2-3) mean/std of gamma parameters, (4-5) mean/std of beta parameters, (6) depth-weighted BN norm. This tests whether normalization layer count (architectural) or learned normalization statistics (training-induced) enable classification.

## 3.3 Classification and Validation Protocol

**Classifier.** We used logistic regression (scikit-learn, C=1.0, solver='lbfgs', max_iter=1000, random_state=42) for interpretability through coefficient analysis. Features were normalized via StandardScaler before training.

**Random Initialization Test (Critical for Mechanism Validation).** For each feature type, we loaded the same 20 architectures with `pretrained=False` (random PyTorch initialization), extracted identical features, and trained a separate classifier. If random models achieve similar accuracy to pretrained models, features are architectural (exist in network definition). If accuracy degrades, features are training-induced (emergent from gradient flow). This test distinguishes mechanism, not merely existence.

**Within-Family Validation.** We trained separate classifiers on ResNet-only (9 models) and DenseNet-only (4 models) subsets, with held-out test models from the same family. This controls for architecture family differences and tests whether depth signals exist even within single families. VGG was excluded (all shallow models, no depth variation).

**Baselines.** Implicit baselines include: (1) random guessing (50% for binary classification), (2) metadata parsing (requires metadata availability), (3) forward-pass methods (require test data and computation). Our approach requires only weight file access.

## 3.4 Design Rationale

**Why Binary Classification?** Maximizes effect size for existence proof with limited sample size (n=20). Continuous depth regression would test fine-grained discrimination but requires larger samples and stronger assumptions about depth-property monotonicity.

**Why Multiple Feature Types?** Tests whether architectural depth is redundantly encoded across representations. If only one feature type works, the signal may be narrow. If multiple types achieve similar accuracy, depth is broadly encoded.

**Why Random Initialization Test?** Without this test, we cannot distinguish architectural features (in network definition) from training-induced features (emergent from gradients). High accuracy alone does not validate mechanism—random initialization is critical. For example, H-M1 achieved 100% accuracy but was mechanistically rejected when random models matched pretrained performance.

**Why Within-Family Validation?** Cross-family classification might succeed merely by distinguishing ResNet from VGG design patterns rather than detecting depth. Within-family validation proves depth signals exist independent of architecture type.

**Analogy for Intuition.** Architectural fingerprinting resembles identifying building types (skyscraper vs house) from floor plans alone. You can distinguish them from structural properties—floor count, elevator shafts, foundation type—without seeing construction history. Similarly, deep versus shallow networks differ in structural patterns (layer count, residual stages, bottleneck prevalence) detectable from architecture definition regardless of training.
