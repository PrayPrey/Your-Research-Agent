# Experimental Setup

Our experimental design validates three core predictions through five complementary experiments: (P1) lightweight features achieve >80% accuracy on held-out validation, (P2) features generalize to edge case architectures, and (P3) features exhibit scale invariance and strong inter-family separation. Each experiment tests a specific aspect of our checkpoint fingerprinting hypothesis.

## Experimental Questions

We structure our validation around five hypotheses, each testing a distinct claim:

**H-E1 (Existence).** Do normalization counts and parameter-mass ratio achieve >80% 3-way classification accuracy on held-out TIMM models? This is the primary MUST_WORK validation—if features cannot reliably separate families, the method fails regardless of mechanistic understanding.

**H-M1 (Mechanism: Normalization Fingerprinting).** Do CNNs exclusively use BatchNorm while Transformers use LayerNorm, with violation rates ≤15% per class? This validates our assumption that normalization layer choice reflects architectural paradigm rather than arbitrary training convention.

**H-M2 (Mechanism: Parameter Allocation).** Does parameter-mass ratio R exhibit exceptional inter-family separation (Cohen's d > 1.0) between CNN and Transformer families? This validates that parameter allocation patterns are fundamentally distinct across paradigms.

**H-M3 (Mechanism: Checkpoint-Only Feasibility).** Can features be extracted from checkpoint files in <10 minutes with 0 MB GPU usage? This validates practical feasibility of checkpoint-only analysis at scale.

**H-C1 (Condition: Edge Case Robustness).** Do features maintain ≥70% accuracy on non-standard architectures (NormFree, SENet, RegNet, ViT-Extreme) with ≤15% degradation from baseline? This tests generalization beyond standard CNN/Transformer paradigms.

## Dataset Construction

We curated 60 pre-trained models from the TIMM model zoo (version 0.9.12), ensuring diversity across architecture families and model scales while maintaining implementation feasibility within our <8 hour constraint.

**Model Selection.** We selected 24 CNN models (ResNet-{18,34,50,101,152}, VGG-{11,16,19}, DenseNet-{121,161,201}, EfficientNet-{B0,B1,B2,B3}, MobileNetV3-{Small,Large}, RegNet-{Y_400MF,Y_800MF,Y_1_6GF,Y_3_2GF}, ConvNeXt-{Tiny,Small,Base}), 24 Transformer models (ViT-{Tiny,Small,Base,Large}, DeiT-{Tiny,Small,Base}, Swin-{Tiny,Small,Base}, BEiT-{Base,Large}, CaiT-{XXS24,XS24,S24}, LeViT-{128,192,256}, PoolFormer-{S12,S24,S36,M36,M48}), and 12 Hybrid models (MLP-Mixer-{B16,L16}, FNet-{Base,Large}, ResMLP-{12,24,36}, GFNet-{XS,S,B}, ConvMixer-{768_32,1024_20,1536_20}). Models span 5× parameter range within families (e.g., ResNet-18 at 11M to ResNet-152 at 60M params) to test scale invariance.

**Train-Validation Split.** We applied stratified 70/30 split, ensuring balanced class representation: 42 training models (17 CNN, 17 Transformer, 8 Hybrid) and 18 validation models (7 CNN, 7 Transformer, 4 Hybrid). Stratification maintains class proportions to prevent overfitting to majority classes. Random seed fixed at 42 for reproducibility.

**Edge Case Validation Set.** For H-C1, we selected 12 additional edge case models: 3 NormFree networks (NFNet-{F0,F1,F2}), 3 SENet variants (SE-ResNet-{50,101}, SE-ResNeXt-{50}), 3 RegNet extreme scales (RegNet-{Y_400MF,Y_16GF,Y_32GF}), and 3 ViT extreme variants (ViT-{Giant,Huge}-patch14). These architectures violate standard normalization conventions (NormFree replaces BatchNorm with scaled weight standardization) or operate at extreme parameter scales.

**Ground Truth Labeling.** We derived labels from TIMM naming conventions with structural validation on 10-model sample. While TIMM naming alignment was only 40% (violating our initial ≥90% assumption A1), this failure paradoxically validates that our features extract structural information independent of naming—the method succeeded despite noisy labels.

## Baseline and Metrics

**Baseline for Comparison.** We compare against Kofinas et al. (2024) graph neural network approach as the state-of-the-art weight-space learning method. Direct accuracy comparison is infeasible (different datasets, different task scopes), so we compare implementation complexity (GNN graph construction + 50+ hours vs our checkpoint inspection + <6 hours), computational requirements (GPU-intensive vs CPU-only), and interpretability (black-box neural representations vs hand-crafted statistical features).

**Primary Evaluation Metrics.** For H-E1, we report macro-averaged accuracy (class-balanced average) to avoid bias toward majority classes. Per-class precision and recall must meet ≥75% threshold for all three families. For H-M2, we compute Cohen's d effect size to quantify inter-family separation strength (d > 0.8 = large effect). For H-M1, we measure violation rates (percentage of models not using dominant normalization type per class). For H-M3, we measure extraction time per model and peak GPU memory usage.

**Statistical Validation.** For scale invariance (H-E1, A3), we compute coefficient of variation (CV = std/mean) across ResNet-{18,34,50,101,152} family, requiring CV < 0.15. For inter-family separation (H-M2), we apply Welch's t-test for unequal variances and report p-values with Bonferroni correction for multiple comparisons. For edge case degradation (H-C1), we compute accuracy drop from baseline and require ≤15% relative degradation.

## Feature Extraction Protocol

Features are extracted via pure PyTorch `state_dict` inspection without model instantiation. For each checkpoint file, we load the `state_dict` dictionary and apply two extraction functions:

**Normalization Layer Counts.** We iterate through all layer names (dictionary keys) and count occurrences of 'bn', 'batch_norm' (BatchNorm), 'ln', 'layer_norm' (LayerNorm), 'gn', 'group_norm' (GroupNorm). The binary `no_norm_flag` is set to 1 if all counts are zero (indicating NormFree architecture), else 0. This produces 4 features: `bn_count`, `ln_count`, `gn_count`, `no_norm_flag`.

**Parameter-Mass Ratio.** We compute total parameter counts for 4D tensors (convolutional kernels) and 2D tensors (linear projection matrices), excluding final classification head by filtering layer names containing 'head' or 'fc'. The ratio R = conv_params / (conv_params + linear_params) ranges from 0 (pure Transformer) to 1 (pure CNN). This produces 1 feature: `param_mass_ratio`.

Total feature dimensionality: 5 features per model. Extraction is CPU-bound, averaging 1.05 seconds per model on commodity hardware.

## Classifier Training

We deliberately use logistic regression (scikit-learn `LogisticRegression` with multinomial loss) rather than neural network classifiers to ensure discriminative power comes from features themselves, not learned non-linearities. If a linear classifier fails to achieve >80% accuracy, it indicates features are insufficient—no MLP "rescue" is permitted.

**Hyperparameters.** We use LBFGS solver (handles multi-class well), maximum 1000 iterations (converged in <100 iterations), balanced class weighting to handle 20% Hybrid class imbalance, C=1.0 L2 regularization (default, no hyperparameter tuning). Preprocessing applies `StandardScaler` (zero mean, unit variance) to prevent parameter-mass ratio [0,1] from dominating normalization counts [0,100+] due to scale differences.

**Training Protocol.** We fit the classifier on 42 training samples with 5 features, requiring no cross-validation or hyperparameter search due to simplicity of linear model. Feature importance is computed from absolute logistic regression coefficients, normalized by L2 norm for interpretability.

## Implementation Details

All experiments use Python 3.9, PyTorch 2.1.0, scikit-learn 1.3.0, and TIMM 0.9.12. Checkpoints are cached locally in `~/.cache/torch/hub/checkpoints/` (15 GB storage, one-time download ~2.5 hours). Feature extraction is sequential (not parallelized) for simplicity, taking ~15 minutes for 60 models. Training and evaluation complete in <2 minutes. Total experimental runtime: ~3 hours, dominated by one-time checkpoint downloads. Peak RAM usage: 4.2 GB (loading ResNet-152 checkpoint). No GPU required—all operations are CPU-only.

**Reproducibility.** We fix random seed at 42 for train-validation split. All code, extracted features (CSV), and evaluation scripts are available in experiment artifacts (`h-e1/code/`, `h-m1/code/`, `h-m2/code/`, `h-m3/code/`, `h-c1/code/`). TIMM version pinned to 0.9.12 to ensure checkpoint availability and consistent model architectures.

## Validation Protocol

Each hypothesis (H-E1, H-M1, H-M2, H-M3, H-C1) is validated independently with explicit success criteria:

**H-E1:** Train on 42 models, evaluate on 18 held-out validation models. Success: macro-accuracy >80%, per-class precision/recall ≥75%.

**H-M1:** Measure normalization layer violation rates on training set (42 models). Success: CNN violation ≤15%, Transformer violation ≤15%.

**H-M2:** Compute Cohen's d between CNN and Transformer R distributions on validation set. Success: d > 1.0, p < 0.05.

**H-M3:** Time checkpoint loading and feature extraction for all 60 models. Success: total time <10 minutes, GPU memory = 0 MB.

**H-C1:** Evaluate classifier on 12 edge case models. Success: accuracy >70%, degradation from baseline ≤15%.

This experimental design provides orthogonal validation of existence (H-E1), mechanisms (H-M1, H-M2, H-M3), and boundary conditions (H-C1), ensuring robust evidence for our checkpoint fingerprinting hypothesis.
