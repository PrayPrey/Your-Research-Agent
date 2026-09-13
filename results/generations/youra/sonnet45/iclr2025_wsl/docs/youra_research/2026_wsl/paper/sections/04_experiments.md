# Experimental Setup

We design experiments to answer the following research questions:

**RQ1**: Does compositional design preserve per-family quality signals? (Tests tokenization effectiveness)

**RQ2**: Does shared NFT maintain architecture-aware representations? (Tests shared processing doesn't destroy structure)

**RQ3**: Do learned representations outperform naive baselines? (Tests compositional value)

## Datasets

We evaluate on a 150-model heterogeneous zoo constructed from publicly available pretrained models:

**Model Sources**:
- **CNNs** (50 models): torchvision pretrained models (ResNet, EfficientNet, DenseNet variants) originally trained on ImageNet
- **Vision Transformers** (50 models): timm library ViT models originally pretrained on ImageNet
- **MLPs** (50 models): Fully-connected networks trained on MNIST from multiple sources

**Generalization Gap Computation**: We evaluate all models on CIFAR-10 to compute generalization gaps (test accuracy - train accuracy). While this creates a domain shift from ImageNet pretraining, CIFAR-10 transfer performance still captures model-specific characteristics relevant to quality assessment.

**Dataset Statistics**:
- Total models: 150
- Train/Val/Test split: 120/30/30 (stratified by architecture family)
- Generalization gap range: [-0.12, 0.31]
- Average parameters per model: ~25M (CNNs), ~86M (ViTs), ~2M (MLPs)

**Rationale**: This 150-model proof-of-concept scale enables mechanism validation before investing in planned 750-model full-scale experiments. The heterogeneous composition (CNN+Transformer+MLP) tests our core claim of architecture-agnostic processing.

## Baselines

We compare against two baselines designed to test specific aspects of our approach:

**Flat-Weight MLP Baseline**: Concatenate all model weights into a single vector, process with 3-layer MLP (same training budget as CAWE). This tests whether tokenization matters—if flat-weight MLP performs comparably, tokenization adds no value.

**Random Forest with Engineered Features**: Hand-crafted weight statistics (L2 norms per layer, sparsity ratios, spectral radius of weight matrices). Trained using sklearn RandomForestRegressor with 100 trees. This tests whether learned representations beat feature engineering.

**Justification**: These baselines isolate our contributions. Flat-weight MLP tests the compositional design claim. Random forest tests the learned representation claim.

## Validation Components

Following our hypothesis verification plan, we implement five validation components:

### Component 1: Per-Family Ablation

Train CAWE on single-architecture subsets (CNN-only, Transformer-only, MLP-only) and measure Spearman ρ for each. Success criterion: ρ > 0.7 for all three families, confirming tokenization preserves family-specific quality signals.

### Component 2: Architecture Clustering

Extract CAWE embeddings for all test models, compute silhouette score using architecture family labels. Success criterion: silhouette > 0.5, confirming shared NFT maintains architecture-aware representations.

### Component 3: Flat-Weight Baseline Comparison

Compare CAWE vs flat-weight MLP using paired t-test. Success criterion: Δρ > 0.15 with p < 0.001, confirming compositional design adds value.

### Component 4: Random Forest Baseline Comparison

Compare CAWE vs random forest with engineered features using Wilcoxon signed-rank test. Success criterion: Δρ > 0.1 with p < 0.01, confirming learned representations outperform hand-crafted features.

### Component 5: Robustness Validation

Test CAWE with 4 tokenization variants (different token dimensions D ∈ {64, 128, 256, 512}). Success criterion: ≥2 variants achieve ρ > 0.65, confirming method tolerates design variations.

## Implementation Details

**Framework**: PyTorch 2.0 with CUDA 12.1

**Hardware**: Single NVIDIA A100 GPU (40GB)

**NFT Library**: `nfn` (PyPI) [Zhou et al., 2023]

**Training Time**: ~2 hours for 150-model PoC, estimated ~8 hours for planned 750-model full-scale

**Key Hyperparameters**:
- Learning rate: 1e-4
- Batch size: 16
- NFT heads: 8
- NFT layers: 4
- Token dimension: D=128
- Early stopping patience: 10 epochs

## Evaluation Metrics

**Primary Metric**: Spearman rank correlation ρ with bootstrap 95% confidence intervals (1000 bootstrap samples). We use Spearman ρ instead of Pearson r because it captures rank-order quality prediction robustly to outliers.

**Clustering Metric**: Silhouette score with architecture family labels. Measures how well embeddings separate by architecture family.

**Statistical Significance**:
- Paired t-test for flat-weight baseline (parametric)
- Wilcoxon signed-rank test for random forest baseline (non-parametric, robust to non-normal distributions)
- Significance threshold: p < 0.05

**Fairness Considerations**:
- All methods trained for same number of epochs with early stopping
- Same data access for all baselines
- Stratified 80/20 split with fixed random seed (42) for reproducibility
