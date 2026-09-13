# Methodology

Our method extracts two statistical features directly from PyTorch checkpoint files (`state_dict`) without requiring model instantiation or forward passes. The features capture structural fingerprints that discriminate architecture families: normalization layer type counts reflect data processing paradigm (spatial vs sequential), while parameter-mass ratio reflects computation style (local vs global). We then train a simple logistic regression classifier, deliberately avoiding neural networks to ensure that discriminative power comes from the features themselves rather than learned non-linearities.

## Feature 1: Normalization Layer Type Counts

Architecture families impose different data processing paradigms that manifest as normalization layer conventions. CNNs process spatially-structured image tensors benefiting from batch-wise statistics across spatial dimensions, leading to BatchNorm (BN) adoption. Transformers process sequential token representations requiring instance-wise normalization, leading to LayerNorm (LN) adoption. We exploit this structural coupling by counting normalization layers of each type directly from checkpoint metadata.

**Extraction Protocol.** Given a PyTorch checkpoint file containing `state_dict` (a dictionary mapping layer names to weight tensors), we iterate through all keys and classify layers by name pattern matching:

```
bn_count = sum(1 for key in state_dict.keys() if 'bn' in key or 'batch_norm' in key)
ln_count = sum(1 for key in state_dict.keys() if 'ln' in key or 'layer_norm' in key)
gn_count = sum(1 for key in state_dict.keys() if 'gn' in key or 'group_norm' in key)
```

We also define a binary `no_norm_flag` to handle edge cases where architectures intentionally omit normalization layers (e.g., NormFree networks using scaled weight standardization). This flag is set to 1 if `bn_count + ln_count + gn_count = 0`, and 0 otherwise.

**Rationale.** Normalization layer choice is not an arbitrary training convention—it reflects fundamental architectural assumptions about data structure. Chun (2026) proved theoretically that LayerNorm reduces linear layer condition numbers by factors proportional to feature dimensionality, making it suited for token representations where dimensions vary independently. BatchNorm enforces spatial normalization suited for image data where spatial locations share statistics. Our validation (Section 5.2) confirms this mechanistic coupling: CNNs exhibit 0% violation rate (100% use BatchNorm as dominant normalization type), Transformers exhibit 14.29% violation rate (85.71% use LayerNorm), both within the ≤15% threshold validating paradigm alignment.

**Design Alternatives.** We considered extracting BatchNorm running statistics (mean, variance) as features, following Zhang & Abdulla (2023), but this requires forward passes to populate running buffers. Our checkpoint-only constraint demands features computable purely from `state_dict` inspection. We also considered weighting normalization counts by layer depth or parameter count, but preliminary experiments showed raw counts provide sufficient discriminative power with perfect interpretability.

## Feature 2: Parameter-Mass Ratio

Architecture families allocate parameters differently based on their core computation paradigm. CNNs allocate predominantly to convolutional kernels (4D tensors representing local spatial filters), while Transformers allocate to large linear projection matrices (2D tensors for global attention mechanisms). We capture this allocation pattern through the parameter-mass ratio.

**Extraction Protocol.** Given `state_dict`, we compute total parameter counts for convolutional layers (identified by 4D weight tensors) and linear layers (identified by 2D weight tensors), excluding the final classifier head:

```
conv_params = sum(tensor.numel() for key, tensor in state_dict.items() 
                  if tensor.ndim == 4 and 'head' not in key and 'fc' not in key)

linear_params = sum(tensor.numel() for key, tensor in state_dict.items() 
                    if tensor.ndim == 2 and 'head' not in key and 'fc' not in key)

R = conv_params / (conv_params + linear_params) if (conv_params + linear_params) > 0 else 0.0
```

The ratio R ranges from 0 (pure Transformer, all parameters in linear layers) to 1 (pure CNN, all parameters in convolutional layers), with Hybrid architectures falling in between.

**Rationale.** Fang et al. (2024) empirically observed that convolutional and attention layers have diverged parameter importance distributions. We operationalize this observation: CNNs require many small convolutional kernels for local receptive fields at multiple scales, leading to R ≈ 1.0. Transformers require few large linear projections for global token mixing (query, key, value matrices), leading to R ≈ 0.0. Our validation (Section 5.3) demonstrates exceptional inter-family separation: CNN R mean = 1.000, Transformer R mean = 0.169, Cohen's d = 3.202 (p < 0.001).

**Design Rationale for Excluding Classifier Head.** We exclude the final classification layer (`head`, `fc`) because it is architecture-agnostic—both CNNs and Transformers use linear classifiers for ImageNet-1k (1000 classes), contributing identical parameter counts. Including the head would dilute the discriminative signal from backbone architecture. This design choice is validated by our feature importance analysis (Section 5.1), where parameter-mass ratio has the highest coefficient (0.777) despite being computed only on backbone parameters.

**Scale Invariance Property.** A critical property of R is scale invariance within architecture families. ResNet architectures scale by stacking more residual blocks with identical convolutional structure, preserving R = 1.0 regardless of depth. Vision Transformers scale by stacking more attention blocks with identical linear projection structure, preserving R ≈ 0.0. Our validation (Section 5.3) confirms perfect scale invariance for ResNet family across 5× parameter range (ResNet-18 to ResNet-152): coefficient of variation CV = 0.00. This property enables family classification independent of model size.

## Classification Protocol

We deliberately use logistic regression rather than neural network classifiers to ensure discriminative power comes from features, not learned non-linearities.

**Preprocessing.** We apply standard scaling (zero mean, unit variance) to both features independently. This prevents parameter-mass ratio (range [0, 1]) from dominating normalization counts (range [0, 100+]) due to scale differences.

**Classifier.** We train a multi-class logistic regression with L2 regularization (C = 1.0), using the LBFGS solver with balanced class weighting to handle class imbalance (20 CNN, 20 Transformer, 10 Hybrid in our 50-model dataset). The classifier outputs calibrated probabilities for each class, enabling confidence thresholding for production deployment.

**Validation Protocol.** We use stratified 70/30 train-validation split to ensure all three classes are represented in both sets. Stratification maintains class proportions: validation set contains 6 CNN, 6 Transformer, 3 Hybrid models (total 15), ensuring balanced evaluation. We report macro-averaged accuracy (class-balanced) to avoid bias toward majority classes.

**Feature Importance Analysis.** Logistic regression provides interpretable coefficients indicating feature importance. We extract coefficients for each feature and normalize by L2 norm to obtain relative importance rankings. This enables mechanistic validation—if normalization counts and parameter-mass ratio genuinely capture architectural paradigms, they should have comparable importance rather than one dominating.

## Edge Case Handling

Some architectures violate standard normalization conventions, requiring fallback heuristics.

**NormFree Networks.** Architectures like NFNet replace normalization layers with scaled weight standardization, resulting in `bn_count = ln_count = gn_count = 0`. Our `no_norm_flag` captures this absence, providing a binary signal. However, without normalization fingerprints, classification relies solely on parameter-mass ratio, which may be insufficient for novel architectural paradigms.

**Hybrid Architectures.** Models like LeViT (lightweight Vision Transformer) combine convolutional stems with transformer bodies, exhibiting mixed normalization (both BN and LN present) and intermediate parameter-mass ratios (R ≈ 0.5). Our features naturally capture this mixing—hybrid models fall between CNN and Transformer extremes in feature space.

**MetaFormer Architectures.** PoolFormer replaces self-attention with pooling operators, which may be implemented as convolution-like operations (4D tensors) despite being labeled "Transformer" in TIMM. Our structure-based features classify based on actual parameter allocation, potentially revealing mismatches between naming conventions and structural reality.

## Computational Efficiency

Checkpoint-only extraction is CPU-bound and requires no GPU resources. For a typical TIMM checkpoint (~200 MB, 25M parameters):

1. **Load checkpoint:** ~0.5 seconds (I/O bound)
2. **Count normalization layers:** ~0.1 seconds (dictionary iteration)
3. **Compute parameter-mass ratio:** ~0.4 seconds (tensor shape queries)
4. **Total:** ~1.0 second per model

For 1000 TIMM models, total extraction time is ~17 minutes on commodity CPU hardware, compared to 50+ hours for graph neural network approaches requiring GPU resources and graph construction. This 100× speedup enables practical model zoo management at scale.

## Why This Design Works

Our method succeeds because it exploits mechanistic understanding of architectural constraints rather than learning representations from data. Normalization layer choice is structurally coupled to data processing paradigm (spatial vs sequential), not an arbitrary convention. Parameter allocation reflects core computation style (local vs global), enforced by architecture definition. Both properties are checkpoint-observable through metadata inspection. By designing features that directly measure these structural fingerprints, we bypass the need for complex neural architectures to learn what can be directly extracted. The simplicity is not a limitation—it is the contribution, demonstrating that interpretable, hand-crafted features guided by mechanistic insight suffice when targeting specific classification tasks aligned with those mechanisms.
