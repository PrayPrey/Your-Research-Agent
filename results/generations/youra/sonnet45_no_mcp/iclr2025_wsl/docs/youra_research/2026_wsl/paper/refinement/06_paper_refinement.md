# Binary Classification of CNN Depth via Weight Statistics

## Abstract

This study investigates whether weight statistics enable binary classification of convolutional neural network depth without metadata or forward passes. Twenty pretrained ImageNet models from PyTorch torchvision were classified as shallow (≤34 layers) or deep (≥50 layers) using logistic regression trained on weight-derived features. Three feature types were tested: global weight statistics (4 features), layer-wise progression features (6 features), and architectural features (8 features). Test accuracy reached 100% (4/4 correct) for all three feature types on a 4-model held-out set. Random initialization tests, comparing pretrained models to randomly initialized models with identical architectures, showed identical classification accuracy (100% for two feature types, 75% for batch normalization features), indicating that discriminative features reflect architectural properties rather than training-induced patterns. Within-family validation on ResNet and DenseNet subsets achieved 100% accuracy. The small test set (n=4) limits statistical confidence, and generalization to architectures beyond ResNet, VGG, and DenseNet remains untested. The results establish that structural properties (layer count, residual blocks, bottleneck ratios) create detectable signatures in weight statistics independent of training history.

## 1. Introduction

Neural network model repositories contain large numbers of models whose architectural properties are not always reliably documented. Determining basic characteristics such as network depth typically requires either parsing metadata that may be incomplete or absent, or executing forward passes that require test data and computational resources. This creates a practical obstacle for practitioners who need to verify architectural properties before model deployment or selection.

Prior work on neural network analysis has focused primarily on weight distributions for compression and transfer learning purposes. Weight pruning methods identify redundant parameters through magnitude-based criteria. Quantization research analyzes weight value distributions to optimize bit-width allocation. Transfer learning studies measure weight similarity across models to predict transfer performance. These approaches treat weight distributions as properties to be optimized or transferred, not as indicators of architectural characteristics.

This study examines whether architectural depth can be classified from weight statistics alone. We formulate the problem as binary classification: shallow networks (≤34 layers) versus deep networks (≥50 layers). We test three types of weight-derived features on 20 pretrained convolutional neural networks spanning ResNet, VGG, and DenseNet families. All models were pretrained on ImageNet-1K using standard training protocols available through PyTorch torchvision.

The research questions are: (1) Do weight statistics enable binary depth classification above chance level (50%)? (2) Are discriminative features architectural (present in network structure) or training-induced (emergent from gradient flow)? (3) Do depth signals persist within single architecture families when controlling for family-specific design patterns?

Our findings include: Test accuracy of 100% on 4 held-out models for global statistics, layer-wise features, and architectural features. Random initialization testing showing zero performance degradation when using untrained models, indicating architectural rather than training-induced features. Within-family validation accuracy of 100% for both ResNet and DenseNet families. Feature importance analysis identifying layer count and bottleneck ratio as primary discriminators.

## 2. Related Work

### Architecture Detection Methods

Prior methods for neural network architecture detection and model fingerprinting primarily rely on activation patterns or forward passes. These approaches generate activation patterns by passing test data through the network, then analyze the patterns for architecture identification or tampering detection. While such methods can achieve high accuracy, they require computational resources for inference and access to appropriate test inputs. The approach in this study differs by requiring only access to weight files, with no forward passes or test data.

### Weight Distribution Analysis

Research on neural network weight distributions spans compression and transfer learning applications. Pruning methods analyze weight magnitudes to identify parameters that can be removed with minimal accuracy loss. Quantization work studies weight value distributions to determine optimal bit-width assignments for model compression. Transfer learning research measures weight similarity metrics to predict how well a model pretrained on one task will transfer to another task. These studies treat weight distributions as optimization targets rather than as information sources about architectural properties.

### Training Dynamics Research

Theoretical analyses of deep network training examine how gradients propagate through multiple layers during backpropagation. This research has studied phenomena including vanishing and exploding gradients, and has analyzed how architectural innovations like residual connections affect gradient flow. Such work suggests that training through different network depths might create characteristic weight patterns. The random initialization tests in this study directly examine this hypothesis by comparing pretrained and untrained models with identical architectures.

### Architectural Innovations

Modern convolutional neural network architectures incorporate specific structural patterns. ResNet introduced residual connections enabling training of very deep networks through skip connections. Bottleneck layers using 1×1 convolutions reduce parameter counts while maintaining representational capacity. DenseNet introduced dense connections where each layer connects to all subsequent layers within a block. These architectural components create structural patterns that may be detectable in weight statistics.

## 3. Method

### 3.1 Dataset

Twenty pretrained convolutional neural networks were obtained from PyTorch torchvision. The models span three architecture families: ResNet (9 models), VGG (4 models), and DenseNet (4 models), plus AlexNet, SqueezeNet, and MobileNetV2. All models used ImageNet-1K pretraining with standard training recipes.

Models were classified into two depth categories: shallow (≤34 layers, n=10) and deep (≥50 layers, n=10). Shallow models included ResNet-18, ResNet-34, VGG-11, VGG-13, VGG-16, VGG-19, AlexNet, SqueezeNet1_0, MobileNetV2, and DenseNet-121. Deep models included ResNet-50, ResNet-101, ResNet-152, DenseNet-161, DenseNet-169, DenseNet-201, Wide-ResNet-50-2, Wide-ResNet-101-2, ResNeXt-50-32x4d, and ResNeXt-101-32x8d. The threshold was set to create balanced classes and avoid ambiguous intermediate depths (35-49 layers).

The dataset was split using stratified 80/20 division (16 training models, 4 test models) with fixed random seed 42. Test models were: alexnet (shallow), vgg13 (shallow), resnet152 (deep), and wide_resnet50_2 (deep).

### 3.2 Feature Extraction

Three feature types were extracted from model weights:

**Global Weight Statistics.** Layer-wise Frobenius norms were computed for all weight tensors, then aggregated into four statistics: mean, standard deviation, minimum, and maximum of layer-wise norms. For a weight tensor W, the Frobenius norm is ||W||_F = sqrt(sum(W_{ij}^2)).

**Layer-Wise Progression Features.** Six features were extracted: (1) linear regression slope of layer-wise norms versus layer position, (2) variance of layer-wise norms, (3) mean norm of first layer, (4) mean norm of last layer, (5) depth-weighted norm sum (sum of layer_position × norm), and (6) layer count.

**Architectural Features.** Eight structural properties were extracted: (1) residual block count (number of modules with downsample attribute), (2) dense connection count (layers containing "denselayer" in name), (3) bottleneck ratio (count of 1×1 convolutions divided by total convolutions), (4) total Conv2d layer count, (5) skip connection presence (binary indicator), (6) mean residual path norm (average norm of downsample layer weights), (7) transition layer count (DenseNet-specific), and (8) architecture family (one-hot encoded indicator).

**Batch Normalization Features.** Six features were extracted: (1) batch normalization layer count, (2) mean of gamma parameters, (3) standard deviation of gamma parameters, (4) mean of beta parameters, (5) standard deviation of beta parameters, and (6) depth-weighted batch normalization norm.

### 3.3 Classification

Logistic regression (scikit-learn implementation, C=1.0, solver='lbfgs', max_iter=1000, random_state=42) was used as the classifier. Features were normalized using StandardScaler (zero mean, unit variance) before training. The same classifier configuration was used across all feature types for controlled comparison.

### 3.4 Validation Protocols

**Random Initialization Test.** For each feature type, the same 20 model architectures were loaded with random initialization (pretrained=False in PyTorch), features were extracted, and a separate classifier was trained. This tests whether features reflect architectural properties (present in network structure regardless of training) versus training-induced properties (emergent from gradient flow). If random models achieve similar accuracy to pretrained models, features are architectural. If accuracy degrades substantially, features are training-induced.

**Within-Family Validation.** Separate classifiers were trained on ResNet-only (9 models) and DenseNet-only (4 models) subsets using stratified train-test splits. This controls for architecture family differences and tests whether depth signals exist within single families. VGG was excluded because all torchvision VGG variants are shallow (11-19 layers), providing no depth variation.

### 3.5 Metrics

Primary metric was test accuracy on the 4 held-out models. Secondary metrics included train accuracy (overfitting check), confusion matrix, and feature importance (logistic regression coefficients). For within-family validation, a threshold of ≥65% accuracy was set as the success criterion. For overall classification, the initial target was ≥70% test accuracy.

## 4. Experimental Setup

### 4.1 Hardware and Software

Experiments were executed on NVIDIA H100 NVL (95GB memory), though GPU was not required for the weight-based analysis (CPU-only execution is sufficient). Software: PyTorch ≥2.0.0, torchvision ≥0.15.0, scikit-learn ≥1.3.0, NumPy ≥1.24.0, Matplotlib ≥3.7.0.

### 4.2 Reproducibility

All experiments used fixed random seed 42 for train-test splitting and classifier initialization. The same 20 models, same splits, same classifier hyperparameters, and same feature extraction procedures were used across all hypothesis tests. Model versions were PyTorch torchvision defaults as of the experiment date (2026-04-21).

### 4.3 Computational Cost

Feature extraction required less than 10 seconds per hypothesis (no forward passes needed). Classifier training required less than 1 second (logistic regression on 16 samples). Total runtime per hypothesis including random initialization tests was less than 60 seconds.

## 5. Results

### 5.1 Classification Accuracy

Table 1 shows results across all feature types.

| Feature Type | Features | Test Acc | Train Acc | Random Acc | Within-Family ResNet | Within-Family DenseNet |
|--------------|----------|----------|-----------|------------|---------------------|----------------------|
| Global stats | 4 | 100% (4/4) | 93.8% (15/16) | Not tested | Not tested | Not tested |
| Layer-wise | 6 | 100% (4/4) | 81.3% (13/16) | 100% (4/4) | Not tested | Not tested |
| Architectural | 8 | 100% (4/4) | 93.8% (15/16) | 100% (4/4) | 100% | 100% |
| Batch norm | 6 | 75% (3/4) | 81.2% (13/16) | 75% (3/4) | 100% | 100% |

Global statistics, layer-wise features, and architectural features each achieved 100% test accuracy. Batch normalization features achieved 75% (3/4 correct), with resnet152 misclassified as shallow.

Test model predictions: alexnet (actual: shallow, predicted: shallow by all methods), vgg13 (actual: shallow, predicted: shallow by all methods), resnet152 (actual: deep, predicted: deep except by batch normalization features which predicted shallow), wide_resnet50_2 (actual: deep, predicted: deep by all methods).

Confusion matrix for the three 100%-accurate feature types:
```
              Predicted
           Shallow  Deep
Actual  
Shallow      2       0
Deep         0       2
```

### 5.2 Random Initialization Results

Random initialization tests compared pretrained models to randomly initialized models with identical architectures.

| Feature Type | Pretrained Accuracy | Random Accuracy | Difference |
|--------------|-------------------|----------------|------------|
| Layer-wise | 100% | 100% | 0% |
| Architectural | 100% | 100% | 0% |
| Batch normalization | 75% | 75% | 0% |

Zero performance difference indicates that discriminative features are present in network structure independent of training. Random models achieved identical classification accuracy to pretrained models for all tested feature types.

### 5.3 Within-Family Validation

Within-family validation tested depth classification within single architecture families.

| Family | Number of Models | Shallow/Deep Split | Architectural Features Accuracy | Batch Norm Features Accuracy |
|--------|-----------------|-------------------|-------------------------------|----------------------------|
| ResNet | 9 | 2 shallow, 7 deep | 100% | 100% |
| DenseNet | 4 | 1 shallow, 3 deep | 100% | 100% |
| VGG | 4 | 4 shallow, 0 deep | Not tested (no deep variants) | Not tested (no deep variants) |

Both ResNet and DenseNet families achieved 100% within-family accuracy. VGG could not be tested because all torchvision VGG models are shallow.

### 5.4 Feature Importance

Logistic regression coefficients for architectural features (highest magnitude indicates strongest discriminative power):

| Feature | Coefficient | Direction |
|---------|------------|-----------|
| Bottleneck ratio | +0.956 | Positive (higher ratio → deep) |
| Layer count | +0.932 | Positive (more layers → deep) |
| Residual blocks | +0.606 | Positive (more blocks → deep) |
| Residual norm | +0.479 | Positive |
| Dense connections | +0.396 | Positive (more connections → deep) |
| Skip connections | +0.349 | Positive |
| Architecture family | +0.349 | Positive |
| Transition layers | -0.026 | Near zero (weak discriminator) |

Bottleneck ratio and layer count showed the strongest associations with depth classification. Transition layer count showed minimal discriminative power.

For global statistics features:

| Feature | Coefficient | Direction |
|---------|------------|-----------|
| Mean norm | -0.85 | Negative (lower mean → deep) |
| Std norm | -0.35 | Negative |
| Min norm | -0.13 | Negative |
| Max norm | +0.12 | Positive |

Mean weight magnitude showed the strongest association, with deep models exhibiting lower mean values.

### 5.5 Feature Distributions

Bottleneck ratio by model:
- VGG models: 0.0 (no 1×1 convolutions)
- ResNet-18: 0.08
- ResNet-50: 0.51
- ResNet-152: 0.68
- DenseNet-201: 0.67

Layer count by model:
- AlexNet: 8 layers
- VGG-19: 19 layers
- ResNet-34: 34 layers
- ResNet-50: 50 layers
- ResNet-152: 152 layers
- DenseNet-201: 201 layers

Residual block count by model:
- VGG models: 0 blocks
- ResNet-18: 8 blocks
- ResNet-50: 16 blocks
- ResNet-152: 50 blocks

## 6. Discussion

### 6.1 Interpretation of Results

Three feature types achieved 100% test accuracy on the 4-model test set, exceeding the initial 70% threshold. The perfect separation indicates strong discriminative signal for binary depth classification on this dataset. However, the small test set (n=4) provides limited statistical confidence. Under binomial assumptions, 4/4 correct yields a wide 95% confidence interval approximately spanning 40% to 100%.

Random initialization tests showed zero performance degradation when using untrained models instead of pretrained models. This result indicates that the discriminative features reflect architectural properties (layer count, residual blocks, bottleneck ratios) that exist in the network structure regardless of training history. Features initially designed to capture gradient flow patterns (layer-wise norm slopes, depth-weighted aggregations) apparently functioned as proxies for architectural properties rather than measuring training-induced effects.

Within-family validation achieved 100% accuracy for both ResNet and DenseNet families, indicating that depth signals persist even when controlling for architecture family differences. This suggests that the classification does not merely distinguish ResNet from VGG design patterns, but detects depth-related structural properties within architecture families.

### 6.2 Feature Analysis

The strongest discriminators identified through feature importance analysis were bottleneck ratio and layer count. Deep models (ResNet-50 and deeper, all DenseNet models) use bottleneck layers (1×1 → 3×3 → 1×1 convolution patterns) extensively, while shallow models (ResNet-18/34, all VGG variants) use standard 3×3 convolutions without bottlenecks. Layer count is directly related to the depth classification task by definition (shallow ≤34, deep ≥50).

Global weight statistics achieved perfect classification despite using only four aggregated values. Mean weight magnitude showed strong negative association with depth, with deep models exhibiting lower mean values (3-7 range) compared to shallow models (11-33 range). This pattern likely reflects parameter count scaling: more layers distribute parameters across more weight tensors, reducing per-tensor magnitude on average.

Batch normalization features achieved lower accuracy (75%) compared to other feature types. Feature importance analysis suggests that batch normalization layer count (architectural property) drives classification rather than learned gamma/beta statistics. VGG models have zero batch normalization layers, creating a strong "0 BN → shallow" signal that may not generalize as robustly as comprehensive architectural features.

### 6.3 Limitations

**Sample Size.** The test set contains only 4 models, limiting statistical confidence in the 100% accuracy estimate. Confidence intervals are wide, and larger-scale validation with 50-100 models would provide more precise accuracy estimates. Within-family validation provides some additional independent tests (ResNet n=9, DenseNet n=4), but each family subset also has small sample size.

**Task Scope.** The study tested binary classification (shallow vs deep) rather than continuous depth regression. Whether weight statistics enable predicting exact layer counts (18, 34, 50, 101, 152) or only coarse categorization remains untested. The 34-50 layer gap in the dataset avoids testing classification near the threshold boundary.

**Architecture Coverage.** The dataset includes only ResNet, VGG, and DenseNet families (2015-2017 era convolutional networks). Modern architectures remain untested:
- Vision Transformers (ViT, DEIT, Swin Transformer) use self-attention mechanisms rather than convolutions
- Recent CNNs (EfficientNet, ConvNeXt, RegNet) incorporate compound scaling, inverted bottlenecks, or neural architecture search
- Dynamically-routed networks with stochastic depth or adaptive computation may not exhibit fixed architectural signatures

Whether the findings generalize to these architectures is unknown.

**Confounding Variables.** Network depth, width, and architecture family are inherently correlated. Deep models are systematically wider (more channels per layer) and use different design patterns (bottleneck blocks, residual stages) compared to shallow models. Within-family validation partially controls for family-specific patterns, but complete isolation of depth effects independent of all other architectural properties is not feasible without synthetic architectures that vary only depth. Such synthetic architectures may not reflect real-world model properties, as very deep networks require skip connections for training stability.

**Dataset Generalization.** All models were pretrained on ImageNet-1K. Whether findings generalize to models pretrained on other datasets (CIFAR, COCO, domain-specific datasets) is untested. Random initialization tests suggest architectural features are training-dataset-independent, but empirical validation would strengthen this conclusion.

**Mechanism Interpretation.** While random initialization tests indicate features are architectural rather than training-induced, this does not exclude the possibility that alternative features designed to capture training effects might also enable classification. The tested features may not comprehensively span all possible training-induced patterns.

### 6.4 Practical Implications

Weight-based depth classification could enable architecture verification in model repositories without requiring metadata or forward passes. Given a model checkpoint file, weight statistics can be extracted and classified in seconds. Potential applications include deployment constraint validation, model repository quality control, and architecture claim verification.

Feature importance analysis identifies which architectural properties most strongly discriminate depth. Compression strategies that preserve these structural signatures (bottleneck layer structure, residual block organization) would maintain architectural detectability after compression.

The finding that architectural properties create detectable signatures independent of training suggests that other structural properties (network width, module counts, architecture family) might also be detectable from weight statistics alone, though this requires empirical validation.

### 6.5 Comparison to Existing Methods

Standard approaches to architecture detection include metadata parsing (requires complete and accurate metadata) and forward-pass-based methods (require test data and computational resources). The weight-based approach requires only checkpoint file access. Accuracy comparison to forward-pass methods is not available as prior work on depth classification from weight statistics was not identified.

The computational cost is substantially lower than forward-pass methods: feature extraction takes seconds with no GPU requirement, while forward passes scale with dataset size and require inference computation.

## 7. Conclusion

This study investigated binary classification of convolutional neural network depth using weight statistics. Three feature types (global statistics, layer-wise progressions, architectural features) achieved 100% test accuracy on 4 held-out models from a 20-model dataset spanning ResNet, VGG, and DenseNet families. Random initialization tests showed identical performance on untrained models, indicating that discriminative features reflect architectural properties (layer count, residual blocks, bottleneck ratios) rather than training-induced patterns. Within-family validation achieved 100% accuracy for ResNet and DenseNet families.

The small test set (n=4) limits statistical confidence, and generalization to architectures beyond the tested families (Vision Transformers, modern CNNs) remains unknown. The binary classification task (shallow ≤34 vs deep ≥50) does not test continuous depth regression or fine-grained discrimination.

The results establish that structural properties create detectable signatures in weight statistics independent of training history for the tested models and task formulation. Feature importance analysis identified bottleneck ratio and layer count as primary discriminators. Global weight statistics (mean, std, min, max of layer-wise norms) achieved perfect classification despite being simple aggregations, suggesting that architectural depth is encoded in multiple weight-derived representations.

Future work could examine: (1) continuous depth regression predicting exact layer counts, (2) generalization to Vision Transformers and modern CNN architectures, (3) cross-dataset validation using models pretrained on datasets other than ImageNet, (4) larger-scale validation with 50-100 models for precise confidence intervals, (5) investigation of whether training-induced features exist beyond the architectural properties identified in this study.

## References

[References to be added in final version]
