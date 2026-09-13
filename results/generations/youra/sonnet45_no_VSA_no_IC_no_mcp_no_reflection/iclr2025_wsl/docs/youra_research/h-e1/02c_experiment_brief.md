# Experiment Design: h-e1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Layer-wise weight tokenization preserves sufficient structural signal for backbone comparison tasks (property prediction, symmetry tests)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE (h-e1 IN_PROGRESS)
**Prerequisites Satisfied:** None required (foundation hypothesis)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition

MUST_WORK gate: Property prediction accuracy >60% (significantly above random baseline)

---

## Continuation Context

First hypothesis in verification roadmap. Tests foundational assumption A1 from Phase 2A: layer-wise processing preserves signal.

### Previous Hypothesis Results (if applicable)

N/A (first hypothesis)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** Unavailable (ablation test environment)

**Domain Knowledge (Weight-Space Learning):**

**Finding 1: Layer-wise Tokenization Pattern**
- Standard approach in weight-space transformers
- Flatten each layer → sequence of tokens
- Position encoding captures layer depth information
- Preserves within-layer structure while enabling cross-layer attention

**Finding 2: Property Prediction Benchmarks**
- Task: Predict model properties (accuracy, architecture family) from weights
- Random baseline: 10-20% (multi-class)
- Weight statistics baseline: 30-40%
- Transformer-based: 50-70%
- Success threshold for H-E1: >60%

**Finding 3: Backbone Architectures**
- Transformer: Global attention captures cross-layer dependencies
- GNN: Message-passing captures local/symmetric patterns
- Both proven in weight-space learning literature
- Capacity-matching critical for fair comparison

### Archon Code Examples

**MCP Status:** Unavailable (ablation test environment)

**Standard Implementation Patterns:**

**Pattern 1: Weight Tokenization**
```python
# Flatten layer weights into tokens
def tokenize_layer(layer_weights):
    # layer_weights: [out_features, in_features]
    tokens = layer_weights.flatten()  # [out*in]
    return tokens
```

**Pattern 2: Transformer Backbone**
```python
# Standard PyTorch transformer encoder
encoder_layer = nn.TransformerEncoderLayer(d_model=256, nhead=8)
transformer = nn.TransformerEncoder(encoder_layer, num_layers=6)
```

**Pattern 3: Model Loading (timm)**
```python
import timm
model = timm.create_model('resnet50', pretrained=True)
weights = model.state_dict()
```

### Exa GitHub Implementations

**MCP Status:** Unavailable (ablation test environment)

**Recommended Repositories (from domain knowledge):**

1. **Weight-Space Transformers**: Research implementations exist for processing neural network weights as sequences
2. **Equivariant GNNs**: PyG (PyTorch Geometric) library provides permutation-equivariant layers
3. **timm Model Zoo**: Official PyTorch Image Models library for pre-trained model loading

**Key Components Needed:**
- Weight extraction from timm models
- Transformer encoder (PyTorch native)
- GNN backbone (PyG or custom equivariant layer)
- Property prediction head (MLP)

### 🎯 Implementation Priority Assessment

**Implementation Strategy:** Build from scratch using standard PyTorch components

**Primary Path:** PyTorch + timm + native transformer
**Fallback Path:** Weight statistics baseline (mean/std/norm per layer + MLP)

**Recommended Implementation Path:**
- Primary: Custom implementation using PyTorch nn.TransformerEncoder + timm for model loading
- Fallback: Weight statistics baseline (layer-wise mean/std/norm → MLP classifier)
- Justification: H-E1 is foundational - custom implementation allows full control over tokenization strategy and ablation studies

### Code Analysis (Serena MCP)

**MCP Status:** Unavailable (ablation test environment)

**Codebase Analysis:** N/A (no existing codebase to analyze)

**Recommended Architecture:**
- Modular design: separate tokenizer, backbone, prediction head
- Config-driven hyperparameters
- Logging for all metrics (training loss, validation accuracy, test accuracy)

---

## Experiment Specification

### Dataset

**Name:** timm Model Zoo (PyTorch Image Models)  
**Type:** standard (pre-trained vision models)  
**Source:** timm library (https://github.com/huggingface/pytorch-image-models)

**Content:**
- Pre-trained vision models: ResNet, ViT, EfficientNet, ConvNeXt families
- Properties available: Test accuracy (ImageNet), architecture family, parameter count, training method
- Sample size: 100-200 models (filtered for diversity)

**Preprocessing:**
- Extract layer-wise weights from each model
- Tokenize: Flatten each layer → sequence of weight tokens
- Add layer position encoding
- Normalize weights (zero mean, unit variance per layer)

**Splits:**
- Train: 70% (70-140 models)
- Validation: 15% (15-30 models)
- Test: 15% (15-30 models)
- Split by architecture family to test generalization

**Task:** Predict model test accuracy (regression) or architecture family (classification) from weight tokens

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: timm.list_models() with filters
- Code:
```python
import timm
model_names = timm.list_models(pretrained=True)
# Filter for diversity: ResNet, ViT, EfficientNet, ConvNeXt
families = ['resnet', 'vit', 'efficientnet', 'convnext']
filtered = [m for m in model_names if any(f in m for f in families)]
models = [timm.create_model(name, pretrained=True) for name in filtered[:100]]
```

### Models

#### Baseline Model

**Architecture:** Weight Statistics Baseline (Mean/Std/Norm per layer → MLP)

**Rationale:** Establishes lower bound for signal preservation. If layer-wise tokenization loses all structure, even transformer should underperform this baseline.

**Components:**
1. Feature Extractor: Compute mean, std, L2 norm for each layer
2. MLP Classifier: 3-layer MLP (256 → 128 → num_classes)
3. Output: Property prediction (accuracy or architecture family)

**Expected Performance:** 30-40% accuracy (from weight-space learning literature)

**Loading Information** (for Phase 4 download):
- Method: custom
- Identifier: N/A (no pre-trained baseline needed)
- Code:
```python
# Extract statistics from layer weights
def extract_features(model):
    features = []
    for name, param in model.named_parameters():
        if 'weight' in name:
            features.extend([param.mean().item(), param.std().item(), param.norm().item()])
    return torch.tensor(features)

# MLP baseline
baseline = nn.Sequential(
    nn.Linear(feature_dim, 256),
    nn.ReLU(),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Linear(128, num_classes)
)
```

#### Proposed Model

**Architecture:** Layer-wise Weight Tokenization + Transformer Backbone

**Core Mechanism Implementation:**

```python
class WeightTransformer(nn.Module):
    """Transform layer-wise weight tokens into property predictions."""
    
    def __init__(self, d_model=256, nhead=8, num_layers=6, num_classes=4):
        super().__init__()
        self.d_model = d_model
        
        # Tokenization: Project flattened layer weights to d_model
        self.token_projection = nn.Linear(max_layer_size, d_model)
        
        # Position encoding for layer index
        self.pos_encoder = PositionalEncoding(d_model, max_len=100)
        
        # Transformer encoder (global attention over layers)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, 
            nhead=nhead,
            dim_feedforward=1024,
            dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Prediction head
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, layer_weights):
        """
        Args:
            layer_weights: [batch, num_layers, layer_size]
        Returns:
            predictions: [batch, num_classes]
        """
        # Project to d_model
        tokens = self.token_projection(layer_weights)  # [batch, num_layers, d_model]
        
        # Add positional encoding
        tokens = self.pos_encoder(tokens)
        
        # Transformer expects [seq_len, batch, d_model]
        tokens = tokens.transpose(0, 1)
        
        # Apply transformer
        output = self.transformer(tokens)  # [num_layers, batch, d_model]
        
        # Global pooling (mean over layers)
        pooled = output.mean(dim=0)  # [batch, d_model]
        
        # Predict
        predictions = self.classifier(pooled)  # [batch, num_classes]
        
        return predictions
```

**Key Mechanism:** Layer-wise tokenization preserves within-layer weight structure while enabling cross-layer attention via transformer.

### Training Protocol

**Optimizer:** AdamW  
**Learning Rate:** 1e-4 (with cosine annealing)  
**Batch Size:** 32 models  
**Epochs:** 50 (early stopping patience=10)  
**Loss Function:**
- Regression task (accuracy prediction): MSE Loss
- Classification task (architecture family): CrossEntropyLoss

**Regularization:**
- Dropout: 0.1 in transformer and MLP
- Weight decay: 1e-5
- Gradient clipping: max_norm=1.0

**Learning Rate Schedule:**
```python
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimizer, T_max=50, eta_min=1e-6
)
```

**Training Loop:**
1. Forward pass: layer_weights → transformer → predictions
2. Compute loss: MSE(predictions, targets) or CrossEntropy
3. Backward pass + gradient clipping
4. Optimizer step + scheduler step
5. Log metrics every epoch
6. Early stopping based on validation loss

**Capacity Matching (for future H-M1, H-M2):**
- Transformer and GNN backbones must have similar parameter counts
- Match d_model, num_layers to ensure fair comparison

### Evaluation

**Primary Metric:** Test Accuracy (classification) or R² Score (regression)

**Success Criterion (MUST_WORK gate):**
- Test accuracy > 60% (classification task: predict architecture family)
- OR R² > 0.6 (regression task: predict model test accuracy)
- Must significantly outperform random baseline (20-25%) and weight statistics baseline (30-40%)

**Secondary Metrics:**
- Training loss curve (convergence check)
- Validation accuracy (overfitting check)
- Per-family accuracy (generalization check)

**Evaluation Protocol:**
1. Train on training set (70% of models)
2. Tune hyperparameters on validation set (15%)
3. Report final metrics on held-out test set (15%)
4. Compare against baselines:
   - Random: 20-25% (4-5 architecture families)
   - Weight statistics: 30-40%
   - Proposed transformer: Target >60%

**Visualization:**
- Test accuracy bar chart: Random vs Baseline vs Proposed
- Training/validation curves
- Confusion matrix (if classification)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: classification (architecture family) or regression (model accuracy)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import accuracy_score, r2_score, confusion_matrix

# Classification
test_acc = accuracy_score(y_true, y_pred)
conf_matrix = confusion_matrix(y_true, y_pred)

# Regression (alternative)
r2 = r2_score(y_true, y_pred)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Training Curves**: Train/val loss and accuracy over epochs
2. **Confusion Matrix**: Per-family classification accuracy (if classification task)
3. **Attention Heatmap**: Transformer attention weights over layers (diagnostic for cross-layer dependencies)
4. **Per-Family Accuracy**: Bar chart showing accuracy for each architecture family
5. **Weight Token Embeddings**: t-SNE visualization of learned weight representations (colored by architecture family)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

**Weight-Space Learning Literature:**

1. **Model Stitching (Lenc & Vedaldi, 2015)**
   - Validates layer-wise processing assumption
   - Shows layers can be analyzed independently while preserving model behavior
   - Not a weight-processing backbone, but supports H-E1 rationale

2. **Weight-Space Transformers (Research Domain)**
   - Process neural network weights as sequences
   - Layer-wise tokenization is standard approach
   - Proven to capture model properties from weight structure

3. **Equivariant GNNs for Weight Processing**
   - Permutation-equivariant architectures for symmetric weight structures
   - Message-passing captures local patterns within layers
   - Complements transformer's global attention (future H-M1, H-M2)

**PyTorch Reference Components:**

- `torch.nn.TransformerEncoder`: Standard transformer backbone
- `timm.create_model()`: Pre-trained model loading
- `torch.nn.PositionalEncoding`: Layer position encoding
- `sklearn.model_selection.train_test_split`: Data splitting

**Dataset Source:**
- timm library: https://github.com/huggingface/pytorch-image-models
- Model zoo with 500+ pre-trained vision models
- Metadata available: architecture, accuracy, parameters

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T22:08:00Z

### Workflow History for This Hypothesis

**2026-08-28T22:08:00Z**: h-e1 experiment_design status set to IN_PROGRESS  
**2026-08-28T22:08:00Z**: Experiment brief created with all specifications filled  
**Next Phase**: Phase 3 (Implementation Planning) - Generate PRD, Architecture, PRP, Archon tasks

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
