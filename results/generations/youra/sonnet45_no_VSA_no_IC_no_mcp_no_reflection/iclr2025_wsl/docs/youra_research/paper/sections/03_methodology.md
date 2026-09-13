# Methodology

## Dataset: timm Model Zoo

We use 100 pretrained vision models from PyTorch Image Models (timm) [1], spanning 4 architecture families:

- **ResNet** (25 models): Residual networks with BatchNorm and skip connections
- **ViT** (25 models): Vision transformers with patch embeddings and multi-head attention
- **EfficientNet** (25 models): Depthwise separable convolutions with compound scaling
- **ConvNeXt** (25 models): Modernized ConvNets with layer-scaled residuals

All models are pretrained on ImageNet-1K. We extract weight tensors using `timm.create_model(name, pretrained=True).state_dict()`, resulting in layer-wise parameter dictionaries with varying shapes (e.g., `layer1.conv.weight: [64, 3, 7, 7]`, `layer10.fc.weight: [1000, 2048]`).

**Splits**: 70% train (70 models), 15% validation (15 models), 15% test (15 models), stratified by architecture family.

**Task**: 4-class classification predicting architecture family from weight tensors. Random baseline accuracy: 25%.

## Weight Tokenization

We tokenize weights layer-wise to handle variable dimensions:

```python
def tokenize_layer(weight_tensor, max_length=4096):
    """
    Args:
        weight_tensor: (out_dim, in_dim, *kernel_size)
        max_length: Fixed token sequence length
    Returns:
        tokens: (max_length,) normalized token sequence
    """
    # Flatten to 1D
    flat = weight_tensor.flatten()
    
    # Zero-pad to fixed length
    if len(flat) < max_length:
        flat = F.pad(flat, (0, max_length - len(flat)))
    else:
        flat = flat[:max_length]  # Truncate if exceeds
    
    # Per-layer normalization
    normalized = (flat - flat.mean()) / (flat.std() + 1e-8)
    
    return normalized
```

**Rationale**: Flattening preserves within-layer weight structure while enabling uniform sequence length for batch processing. Per-layer normalization prevents scale domination (large layers vs small layers).

**Output**: For a model with $L$ layers, tokenization produces $\mathbf{W} \in \mathbb{R}^{L \times D}$ where $D=4096$ is the fixed token dimension.

## Models

### Baseline: Weight Statistics MLP

Extracts per-layer statistics (mean, standard deviation, L2 norm) as features:

```python
def extract_features(model):
    features = []
    for name, param in model.named_parameters():
        if 'weight' in name:
            features.extend([
                param.mean().item(),
                param.std().item(),
                param.norm().item()
            ])
    return torch.tensor(features)
```

**Architecture**: 3-layer MLP with input dimension matching concatenated statistics ($3L$ features), hidden layers [256, 128], output layer [4 classes]. Total parameters: ~200K.

**Rationale**: Establishes lower bound for signal preservation. If tokenization loses all structure, even transformer should underperform this baseline.

### Proposed: Weight Transformer

Processes tokenized weights with cross-layer attention:

```python
class WeightTransformer(nn.Module):
    def __init__(self, d_model=256, nhead=8, num_layers=6):
        super().__init__()
        self.embedding = nn.Linear(4096, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=1024,
            dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 4)
        )
    
    def forward(self, x):  # x: (B, L, 4096)
        x = self.embedding(x)  # (B, L, d_model)
        x = self.pos_encoder(x)
        x = x.transpose(0, 1)  # (L, B, d_model)
        x = self.transformer(x)
        x = x.mean(dim=0)  # Global pooling (B, d_model)
        return self.classifier(x)  # (B, 4)
```

**Architecture**: Token embedding projects 4096-dim flattened weights to 256-dim latent space. Sinusoidal positional encoding adds layer depth information. 6-layer transformer with 8 attention heads captures cross-layer dependencies. Global mean pooling aggregates layer representations before classification. Total parameters: ~2M.

**Rationale**: Transformer's global attention mechanism models cross-layer dependencies (e.g., residual connections spanning multiple layers, attention patterns across blocks).

## Training Protocol

**Optimizer**: AdamW with learning rate $10^{-4}$, weight decay $10^{-5}$  
**Scheduler**: CosineAnnealingLR ($T_{max}=50$, $\eta_{min}=10^{-6}$)  
**Batch Size**: 32 models  
**Epochs**: 50 (early stopping patience=10 on validation loss)  
**Loss**: CrossEntropyLoss for 4-class classification  
**Regularization**: Dropout 0.1, gradient clipping (max norm=1.0)  
**Seed**: Fixed random seed 42 for reproducibility

**Capacity Matching**: While baseline (200K params) and proposed (2M params) differ in size, both significantly exceed dataset size (70 training samples), making overfitting risk comparable. We report training/validation curves to diagnose overfitting.

## Evaluation

**Primary Metric**: Test accuracy on held-out 15 models  
**Success Criterion**: Test accuracy >60% (gate threshold, significantly above 25% random baseline)

**Secondary Metrics**:
- Training/validation loss curves (convergence and overfitting analysis)
- Per-family accuracy (generalization across architecture types)
- Confusion matrix (family discrimination patterns)

**Evaluation Protocol**:
1. Train on 70 models until validation loss plateaus (early stopping)
2. Select best checkpoint based on validation accuracy
3. Report test accuracy on held-out 15 models (never seen during training/validation)
4. Bootstrap 95% confidence intervals (1000 resamples)

**Reproducibility**: All code, hyperparameters, and random seeds documented. Dataset loading via public timm API (`timm.create_model(name, pretrained=True)`).

**References**  
[1] Wightman, R., "PyTorch Image Models", https://github.com/huggingface/pytorch-image-models, 2019
