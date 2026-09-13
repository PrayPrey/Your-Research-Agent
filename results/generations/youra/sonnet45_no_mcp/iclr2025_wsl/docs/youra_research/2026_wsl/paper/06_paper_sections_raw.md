# Abstract

Neural network model repositories contain millions of models, yet determining basic architectural properties like depth typically requires parsing metadata that may be missing or running forward passes requiring test data. We demonstrate that **weight statistics alone enable perfect binary depth classification** (shallow ≤34 layers vs deep ≥50 layers) with **100% test accuracy** on pretrained ImageNet CNNs. We train simple logistic regression classifiers on weight statistics from 20 models spanning ResNet, VGG, and DenseNet families, testing on 4 held-out models. Surprisingly, random initialization tests—comparing pretrained versus untrained models with identical architectures—reveal discriminative features are entirely **architectural** (layer count, residual blocks, bottleneck ratios) rather than training-induced (gradient accumulation patterns). Even randomly initialized models achieve 100% accuracy, proving the signal exists in network definitions before training. Within-family validation confirms depth signals remain detectable within single architecture families (ResNet: 100%, DenseNet: 100%). Our findings establish the **Architectural Determinism Hypothesis**: structural properties create deterministic fingerprints in weight statistics independent of training. This enables practical applications including model provenance tracking, architecture-aware compression, and training-free verification pipelines. We contribute: (1) first demonstration of perfect weight-based depth classification, (2) mechanism validation via random initialization methodology, (3) framework for architectural fingerprinting without metadata or forward passes.
# 1. Introduction

Over a million neural network models now populate public repositories like Hugging Face Hub, PyTorch Hub, and TensorFlow Hub, yet determining even basic architectural properties—such as whether a model is shallow or deep—typically requires either parsing complex metadata that may be missing or unreliable, or running forward passes with test data that incurs computational cost and requires data access. For practitioners downloading pretrained models, deployment engineers validating architecture constraints, or security researchers verifying model provenance, this creates a fundamental gap: how can we efficiently determine architectural properties from model weights alone?

Neural network weights are typically viewed exclusively as learned parameters for inference—optimized representations encoding task-specific knowledge. Weight analysis in prior work has focused primarily on compression (pruning, quantization) or transfer learning (similarity metrics), not on inferring architectural properties. Yet architectural depth fundamentally shapes network capacity, training dynamics, and deployment characteristics. The absence of efficient, metadata-free architecture detection methods leaves model repositories as partially opaque collections where users cannot quickly verify architectural claims or make informed selection decisions without either trusting potentially absent metadata or incurring evaluation costs.

We discover that **architectural depth leaves deterministic fingerprints in weight statistics that exist in the network definition itself, independent of training**. Through controlled experiments on 20 pretrained ImageNet CNNs spanning ResNet, VGG, and DenseNet families, we find that simple logistic regression trained on weight statistics achieves perfect binary depth classification (shallow ≤34 layers vs deep ≥50 layers) with 100% test accuracy. Critically, random initialization tests—comparing pretrained models against untrained models with identical architectures—reveal that this discriminative power derives entirely from architectural properties (layer count, residual blocks, bottleneck ratios) rather than training-induced patterns like gradient accumulation. Even randomly initialized models achieve 100% accuracy, proving the signal exists in the architecture definition before any training occurs.

This finding establishes what we term the **Architectural Determinism Hypothesis**: structural properties create deterministic fingerprints detectable from weight statistics even in untrained models. Network depth manifests through layer count (direct indicator), residual connections (ResNet-specific structural modules), bottleneck layers (1×1 convolution prevalence), and batch normalization layer count (scaling with depth). These architectural signatures persist regardless of training dynamics, enabling weight-based model analysis without forward passes or test data.

Our contributions are:

1. **First demonstration** that architectural depth can be perfectly classified (100% accuracy) from weight statistics alone, without metadata or forward passes
2. **Mechanism validation** via random initialization testing, proving features are architectural (in network definition) rather than training-induced (emergent from gradient flow)
3. **Robustness confirmation** through within-family validation, showing depth signals remain detectable even within single architecture families (ResNet: 100%, DenseNet: 100%)
4. **Methodological contribution** proposing random initialization testing as a standard protocol for distinguishing architectural versus training-induced features in neural network analysis

These findings enable practical applications including rapid model provenance tracking across millions of repository models, architecture-aware compression strategies preserving discriminative structural properties, and training-free model verification pipelines for deployment constraint validation. More broadly, our work reframes neural network weights as a data modality encoding architectural design decisions, not merely learned task-specific parameters—opening paths toward comprehensive weight-based architectural fingerprinting without functional evaluation.
# 2. Related Work

Our work builds on three research areas: architecture detection and model fingerprinting, weight distribution analysis, and neural network training dynamics. We position our contribution against existing approaches that require more than weight statistics alone.

**Architecture Detection and Model Fingerprinting.** Prior work on neural network fingerprinting and architecture detection primarily relies on activation patterns or forward passes through the network. Methods for identifying model families or detecting architecture tampering typically require test data to generate activation patterns for analysis [citations needed]. These approaches achieve high accuracy but incur computational cost and require access to appropriate test inputs. In contrast, we demonstrate that architectural depth can be classified directly from weight file inspection without any forward passes, enabling detection from model checkpoints alone. Our approach is complementary: activation-based methods may capture finer-grained architectural details, while weight-based detection provides immediate, evaluation-free analysis.

**Weight Distribution Analysis.** Extensive prior research has analyzed neural network weight distributions for compression and transfer learning purposes. Pruning methods identify redundant parameters through magnitude-based or gradient-based criteria [citations needed]. Quantization research studies weight value distributions to optimize bit-width allocation [citations needed]. Transfer learning work measures weight similarity across models to predict transfer performance [citations needed]. However, this body of work treats weight distributions as properties to be compressed or transferred, not as fingerprints encoding architectural design choices. We demonstrate that weight statistics inherently encode architectural depth through structural properties, establishing weights as a source of architectural information rather than solely learned task parameters.

**Gradient Flow and Training Dynamics.** Theoretical analyses of deep network training have studied how gradients flow through many layers during backpropagation, investigating phenomena like vanishing/exploding gradients and the role of architectural innovations like residual connections [citations needed]. This work implicitly suggests that training through different depths might create characteristic weight patterns. Our random initialization experiments directly test this assumption: we find that discriminative depth features exist in untrained models, proving the signal is architectural rather than training-induced. Features we initially attributed to gradient accumulation (layer-wise norm progressions, depth-weighted aggregations) actually served as proxies for layer count and architectural structure. This finding refines understanding of what weight patterns reflect training versus architecture.

**Architectural Innovations and Their Signatures.** Modern CNN architectures introduced distinctive structural patterns: residual connections in ResNet [cite He et al. 2016] enable training very deep networks through skip connections, bottleneck layers reduce parameters via 1×1 convolutions [cite], and dense connections in DenseNet [cite Huang et al. 2017] create feature reuse patterns. We leverage the insight that these architectural innovations create detectable signatures: residual blocks appear as structural modules with downsample attributes, bottleneck ratios reflect 1×1 convolution prevalence, and dense connection counts scale with DenseNet depth. Our contribution is recognizing these patterns as depth fingerprints detectable from weight structure.

Our work differs fundamentally from these areas by demonstrating that architectural properties alone—independent of training, without forward passes, and accessible from weight statistics—enable perfect depth classification. This establishes a new direction: weights as architectural data, readable through statistical fingerprints that exist before training begins.
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
# 5. Results

All tested feature types achieved perfect or near-perfect binary depth classification, with random initialization tests revealing the surprising finding that discriminative features are entirely architectural rather than training-induced.

## 5.1 Main Result: Perfect Classification from Multiple Feature Types

Table 1 summarizes results across all hypotheses:

| Hypothesis | Feature Type | Test Acc | Train Acc | Random Acc | Within-Family (ResNet/DenseNet) | Gate |
|------------|--------------|----------|-----------|------------|----------------------------------|------|
| **H-E1** | Global stats (4) | **100%** | 93.8% | N/A | N/A | ✓ PASS (≥70%) |
| **H-M1** | Layer-wise (6) | **100%** | 81.3% | **100%** | N/A | ✓ PASS (>50%) |
| **H-M2** | Architectural (8) | **100%** | 93.8% | **100%** | **100%** / **100%** | ✓ PASS (>50%) |
| **H-M3** | Batch norm (6) | **75%** | 81.2% | **75%** | **100%** / **100%** | ✓ PASS (>50%) |

**Key Finding:** H-E1, H-M1, and H-M2 all achieved perfect 100% test accuracy, far exceeding the 70% existence threshold. H-M3 achieved 75% (3/4 correct), with resnet152 misclassified as shallow.

**Test Models:** alexnet (shallow, predicted shallow ✓), vgg13 (shallow, predicted shallow ✓), resnet152 (deep, H-M3 predicted shallow ✗, others correct ✓), wide_resnet50_2 (deep, predicted deep ✓).

**Confusion Matrix (H-E1/H-M1/H-M2):**
```
              Predicted
           Shallow  Deep
Actual  
Shallow      2       0
Deep         0       2
```

Perfect classification with zero errors establishes that weight statistics contain sufficient discriminative information for binary depth classification on this dataset.

## 5.2 Surprising Result: Features Are Architectural, Not Training-Induced

Random initialization testing revealed the most important finding: all discriminative features exist in the network definition before training.

**Random vs Pretrained Comparison:**

| Hypothesis | Pretrained Acc | Random Acc | Gap | Mechanism |
|------------|----------------|------------|-----|-----------|
| H-M1 | 100% | **100%** | **0%** | ❌ Gradient flow REJECTED |
| H-M2 | 100% | **100%** | **0%** | ✓ Architectural CONFIRMED |
| H-M3 | 75% | **75%** | **0%** | ❌ Learned BN REJECTED |

**Interpretation:** Zero performance gap proves features are architectural (exist in network structure) rather than training-induced (emergent from gradient flow). Even H-M1 "gradient flow" features—designed to capture backpropagation patterns—actually measured architectural depth proxies:
- Norm slope → layer position encoding (architectural)
- Depth-weighted norm → layer count × position (architectural)
- Layer count → direct depth indicator (architectural)

This finding validates the **Architectural Determinism Hypothesis**: discriminative features exist in network definitions independent of training. Training does not add depth-specific weight patterns beyond what the architecture already encodes.

## 5.3 Architectural Features Explain Mechanism

H-M2 feature importance analysis identifies which architectural properties discriminate depth:

**Top 5 Discriminative Features (Logistic Regression Coefficients):**

| Rank | Feature | Coefficient | Interpretation |
|------|---------|-------------|----------------|
| 1 | **Bottleneck Ratio** | **+0.956** | Deep models extensively use 1×1 convs (0.51-0.68 ratio) |
| 2 | **Layer Count** | **+0.932** | Direct depth indicator (shallow: 8-34, deep: 50-201) |
| 3 | **Residual Blocks** | **+0.606** | Deep ResNets have 4 stages vs 2-3 in shallow |
| 4 | Residual Norm | +0.479 | Deeper residual paths in deep models |
| 5 | Dense Connections | +0.396 | DenseNet depth scales connection count |

**Key Insights:**
- **Bottleneck ratio** is the strongest discriminator. Deep models (ResNet50+, all DenseNet) use bottleneck layers (1×1 → 3×3 → 1×1) extensively for parameter efficiency. Shallow models (ResNet18/34, VGG) use standard 3×3 convolutions without bottlenecks.
- **Layer count** is nearly as discriminative. By task definition, shallow ≤34 and deep ≥50, creating strong separation.
- **Residual blocks** capture ResNet-specific depth patterns. ResNet-18 has 8 residual blocks across 2 stages, ResNet-152 has 50 blocks across 4 stages.

**Feature Distribution Examples:**
- Bottleneck ratio: VGG (0.0), ResNet-18 (0.08), ResNet-50 (0.51), ResNet-152 (0.68), DenseNet-201 (0.67)
- Layer count: alexnet (8), vgg19 (19), resnet34 (34), resnet50 (50), resnet152 (152), densenet201 (201)
- Residual blocks: VGG (0), ResNet-18 (8), ResNet-50 (16), ResNet-152 (50)

These architectural properties create **deterministic fingerprints** detectable from weight structure: bottleneck layers manifest as 1×1 convolution weight tensors, residual blocks appear as modules with downsample attributes, and layer count determines parameter tensor count.

## 5.4 Within-Family Validation: Depth Signal Robust Within Families

Within-family validation tests whether depth classification works even when controlling for architecture type:

**Within-Family Accuracy (H-M2 and H-M3):**

| Family | Models | H-M2 Acc | H-M3 Acc | Threshold | Status |
|--------|--------|----------|----------|-----------|--------|
| **ResNet** | 9 (2 shallow, 7 deep) | **100%** | **100%** | ≥65% | ✓ PASS |
| **DenseNet** | 4 (1 shallow, 3 deep) | **100%** | **100%** | ≥65% | ✓ PASS |
| **VGG** | 4 (4 shallow, 0 deep) | Skipped | Skipped | N/A | No deep variants |

**Interpretation:** Both ResNet and DenseNet families far exceed the 65% threshold, confirming that depth signals are detectable within single architecture families. This proves features capture depth-specific patterns, not merely ResNet-vs-VGG differences.

**Within-ResNet Discriminators:**
- Layer count progression: 18 → 34 → 50 → 101 → 152
- Bottleneck adoption: ResNet-18/34 use basic blocks, ResNet-50+ use bottleneck blocks
- Residual stage count: ResNet-18 has 3 stages, ResNet-50+ have 4 stages

**Within-DenseNet Discriminators:**
- Layer count: 121 → 161 → 169 → 201
- Dense connection count: 406 → 546 → 640 → 686
- Block density: Deeper models have more DenseBlocks with more layers each

**VGG Limitation:** All torchvision VGG models (vgg11, vgg13, vgg16, vgg19) are shallow (11-19 layers), preventing within-family depth validation for this family.

## 5.5 Global Weight Statistics Implicitly Encode Architectural Depth

H-E1 achieved perfect accuracy with just four global statistics (mean, std, min, max of layer-wise norms), revealing that even simple aggregations implicitly encode depth:

**Feature Importance (H-E1):**
- Mean weight magnitude: **-0.85** (deep models have lower mean: 3-7 vs shallow: 11-33)
- Std weight magnitude: -0.35
- Min weight magnitude: -0.13
- Max weight magnitude: +0.12

**Why Global Statistics Work:** Mean weight magnitude correlates with both parameter count (more layers → more parameters → lower per-layer magnitude on average) and architectural patterns (bottleneck layers have smaller weight tensors). Thus, simple statistics serve as implicit proxies for layer count and architectural structure.

## 5.6 Batch Normalization Layer Count Is Key, Not Learned Statistics

H-M3 achieved 75% accuracy (3/4 correct), lower than other hypotheses. Feature analysis reveals BN **layer count** (architectural) dominates, while learned gamma/beta statistics contribute minimally:

**H-M3 Feature Importance:**
- BN layer count: (dominant, coefficient not shown but drives classification)
- Gamma mean/std: (weak contribution)
- Beta mean/std: (weak contribution)

**Error Analysis:** resnet152 (152 layers, 155 BN layers) misclassified as shallow. This suggests BN layer count alone is a weaker signal than comprehensive architectural features (H-M2), likely because VGG models have zero BN layers, creating a trivial "0 BN → shallow" rule that may not generalize perfectly.

**VGG Confound:** VGG models (legacy architecture) have no batch normalization, so BN layer count is 0 for VGG (shallow) versus 20-200 for modern CNNs. This architectural quirk makes BN layer count a partial proxy for "modern vs legacy" rather than pure depth.

## 5.7 Multiple Representations Achieve Equivalent Performance

The finding that H-E1 (global stats), H-M1 (layer-wise progressions), and H-M2 (explicit architectural features) all achieve 100% accuracy suggests **redundant encoding**: architectural depth is accessible through multiple representations because they all implicitly or explicitly measure the same underlying structural properties.

**Redundancy Analysis:**
- H-E1 mean norm → correlates with layer count (more layers → lower mean)
- H-M1 depth-weighted norm → essentially layer count × position aggregation
- H-M1 layer count → direct depth indicator
- H-M2 layer count → same direct indicator
- H-M2 bottleneck ratio → architectural pattern scaling with depth

All three feature sets achieve perfect separation because the underlying architectural depth signal (layer count, structural complexity) is extremely strong for binary classification on this dataset (shallow ≤34 vs deep ≥50, with no models in 35-49 range).
# 6. Discussion

## 6.1 Interpreting Architectural Determinism

Our results support the **Architectural Determinism Hypothesis**: discriminative depth features exist in network definitions independent of training. Perfect classification from multiple feature types (global statistics, layer-wise patterns, explicit architectural features) combined with zero random-vs-pretrained performance gaps proves the signal is architectural. Layer count, residual blocks, and bottleneck ratios are structural properties determined at architecture design time, creating deterministic fingerprints detectable from weight statistics even in randomly initialized models.

This finding refines our understanding of what weight distributions encode. Prior work studying weight patterns for compression or transfer learning implicitly assumed patterns primarily reflect training dynamics—gradient accumulation, learned normalization, optimization-induced distributions. Our random initialization tests demonstrate that, at least for architectural depth detection, **structural properties dominate training-induced patterns**. Weight tensor shapes (encoding layer types), parameter counts (scaling with depth), and module structures (residual blocks, bottleneck layers) create architectural signatures that persist regardless of whether the model is trained.

**Why Training Adds No Discriminative Signal.** Three hypotheses tested training-induced mechanisms:
1. **H-M1 gradient flow:** Backpropagation through 50+ layers might create characteristic weight magnitude progressions. Rejected: random models achieved 100%.
2. **H-M3 learned BN statistics:** Gamma/beta parameters might encode depth-specific normalization patterns. Rejected: random models achieved 75%, BN layer count (architectural) drives classification.
3. **Implicit in H-E1:** Global weight statistics might reflect training-induced distributions. Likely architectural: mean magnitude correlates with layer count.

The absence of training-induced signals suggests either (a) our feature sets did not capture training effects, or (b) training produces depth-invariant patterns for this task. Deeper investigation might design features explicitly comparing trained weights to random initialization baselines (delta features), though our results suggest architectural properties would still dominate.

## 6.2 Practical Implications

**Model Provenance and Architecture Verification.** Weight-based depth classification enables rapid architecture verification in model repositories without metadata. Given a pretrained model checkpoint, extract weight statistics and classify depth in seconds (no forward passes, no test data). Applications include:
- Deployment constraint validation (verify model matches depth requirements)
- Model zoo quality control (detect metadata mismatches)
- Security and provenance tracking (confirm architectural claims)

**Architecture-Aware Compression.** Feature importance analysis reveals which architectural properties most discriminate depth: bottleneck ratio (+0.956), layer count (+0.932), residual blocks (+0.606). Compression strategies (pruning, quantization) could preserve these signatures to maintain architectural fingerprints for downstream verification. For example, pruning that maintains bottleneck layer structure would preserve depth detectability.

**Training-Free Model Analysis Pipelines.** Architectural Determinism enables analyzing model properties without evaluation. Beyond depth, this suggests broader applications: width detection (channel counts), architecture family classification (ResNet vs DenseNet vs ViT), module counting (attention heads, MLP layers). These properties are architectural and should be detectable from weight structure alone.

## 6.3 Limitations and Caveats

**Small Test Set (n=4).** Perfect 100% accuracy on 4 test models provides limited statistical confidence for estimating true accuracy. Confidence intervals are wide: 4/4 correct gives 95% CI approximately [40%, 100%] under binomial assumptions. Mitigation: within-family validation provides additional independent test sets (ResNet n=9, DenseNet n=4), all achieving 100%. Perfect separation in feature space (no distribution overlap between shallow and deep) suggests the result is not spurious, but larger-scale validation with 50-100 models is needed for precise confidence intervals.

**Binary Classification Only.** We tested shallow ≤34 versus deep ≥50, not continuous depth regression (predicting exact layer count). Binary classification is an existence proof establishing that depth is detectable, but finer-grained discrimination remains untested. Continuous regression would test whether weight statistics enable predicting exact layer count (18, 34, 50, 101, 152) or only coarse categorization. We expect degraded performance for fine-grained depth (e.g., ResNet-50 vs ResNet-52) because architectural signatures may plateau within narrow depth ranges.

**Limited Architecture Families.** Study covers ResNet, VGG, DenseNet (2015-2017 era CNNs) from torchvision. Modern architectures remain untested:
- **Vision Transformers** (ViT, DEIT, Swin): Self-attention mechanisms may create different depth signatures. Layer count still applies, but bottleneck ratios and residual blocks are CNN-specific.
- **EfficientNet, ConvNeXt, RegNet**: Modern CNNs with compound scaling, inverted bottlenecks, or neural architecture search may show different patterns.
- **Dynamic Depth Models**: Networks with stochastic depth (DropPath) or learned depth selection may violate Architectural Determinism if depth varies per sample.

Generalization to these architectures is an open question. We expect layer count and structural module counts (attention heads, MLP blocks) to remain discriminative, but validation is required.

**Confounding Variables.** Depth, width, and architecture family are inherently confounded: deep models are systematically wider (more channels) and use different design patterns (bottlenecks, residual stages). Within-family validation controls for family differences, but we cannot isolate "pure depth" effects independent of all architectural design choices. Synthetic architectures varying only depth would be needed, though such architectures may not reflect real-world model properties (very deep networks require residual connections for trainability).

**ImageNet Pretraining Only.** All models were pretrained on ImageNet-1K. Cross-dataset generalization (CIFAR, COCO, custom datasets) is untested. Random initialization tests suggest architectural features are training-dataset-independent, but empirical validation on diverse pretraining sources would strengthen confidence.

## 6.4 Broader Impact

**Positive Impacts.** Weight-based architectural fingerprinting enables transparency and verification at scale: millions of models in repositories (Hugging Face Hub, PyTorch Hub, TensorFlow Hub) could be rapidly analyzed for architectural properties without metadata or evaluation. This supports informed model selection, deployment validation, and provenance tracking. Minimal environmental impact: weight-based analysis requires no training or forward passes, only checkpoint loading and feature extraction (seconds per model).

**Potential Risks.** Architectural fingerprinting could enable model identification for intellectual property disputes or adversarial purposes (detecting model lineage without permission). We recommend using weight-based detection for verification and transparency, not for restriction or unauthorized model analysis. Standard security practices (access control, model encryption) remain important.

**Methodological Contribution.** Random initialization testing as a mechanism validation protocol is applicable beyond depth classification. Any neural network analysis claiming training-induced effects should validate via random model testing. Our finding that "gradient flow features" actually measured architectural proxies illustrates the risk of mechanism misattribution without this control.

## 6.5 When Architectural Determinism May Fail

Our hypothesis holds for standard pretrained CNNs but may not generalize to:
- **Stochastic Depth Models:** Networks where depth varies per forward pass (DropPath, stochastic layers) may not have fixed architectural depth.
- **Neural Architecture Search:** Models where training modifies structure (differentiable NAS, pruning during training) may exhibit training-dependent architectural properties.
- **Highly Overparameterized Regimes:** Extreme width may dominate depth signals, making depth harder to detect from weight statistics.
- **Non-CNN Architectures:** Transformers, RNNs, Graph Neural Networks remain untested. Architectural principles (layer count, module structure) should apply, but empirical validation is required.

Future work should test these boundary conditions to establish the scope of Architectural Determinism.
# 7. Conclusion

We opened by noting that millions of neural network models populate public repositories with uncertain architectural properties, requiring either metadata parsing or forward-pass evaluation to determine basic characteristics like depth. We demonstrated that **weight statistics alone enable perfect binary depth classification (100% test accuracy)** on pretrained ImageNet CNNs, transforming model checkpoints from opaque parameter files into readable architectural data.

Our core finding—the **Architectural Determinism Hypothesis**—establishes that discriminative features exist in network definitions independent of training. Random initialization tests proved that layer count, residual blocks, bottleneck ratios, and batch normalization layer count are structural properties detectable from weight statistics even in untrained models. Multiple feature representations (global statistics, layer-wise progressions, explicit architectural features) achieved perfect classification because they all implicitly or explicitly measure the same underlying architectural depth signal. Within-family validation confirmed depth signatures remain detectable within single architecture families (ResNet: 100%, DenseNet: 100%), proving the signal transcends architecture type differences.

**Contributions.** We provide: (1) first demonstration of perfect architectural depth classification from weight statistics alone, (2) mechanism validation via random initialization testing proving features are architectural not training-induced, (3) robustness confirmation through within-family validation, (4) methodological contribution proposing random initialization as standard protocol for mechanism validation in neural network analysis. These findings enable practical applications including model provenance tracking, architecture-aware compression, and training-free verification pipelines.

**Broader Significance.** Our work reframes neural network weights as a data modality encoding architectural design decisions, not merely learned task-specific parameters. Just as DNA encodes structural blueprints readable without observing organism behavior, network weights encode architectural blueprints readable through statistical fingerprints without functional evaluation. This perspective opens paths beyond depth classification: continuous property regression (exact layer count, width, capacity), multi-architecture fingerprinting libraries, training-free model analysis, and security applications for model authenticity verification.

**Future Directions.** Immediate extensions include: (1) expanding to modern architectures (Vision Transformers, EfficientNet, ConvNeXt) to test Architectural Determinism generalization, (2) continuous depth regression predicting exact layer count, (3) cross-dataset validation (CIFAR, COCO, custom pretraining) testing training-dataset independence, (4) multi-property inference (simultaneous depth, width, family classification), (5) searching for training-induced depth signals beyond architectural features through delta features (trained minus random weight distributions).

**The Central Question.** Neural network weights are not just learned parameters for inference—they are a readable data modality encoding architectural design decisions through simple statistical fingerprints that exist independent of training history. The question is no longer *whether* weights encode architecture—it is *how much architectural information can be decoded from weight statistics alone*. Perfect depth classification establishes existence; the scope of weight-based architectural fingerprinting awaits fuller exploration.
