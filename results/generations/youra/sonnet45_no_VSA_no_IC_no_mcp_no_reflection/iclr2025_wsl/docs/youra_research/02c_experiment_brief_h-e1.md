# Phase 2C: Experiment Design Brief — H-E1

**Generated**: 2026-08-28T22:08:00Z  
**Hypothesis ID**: h-e1  
**Hypothesis Type**: EXISTENCE  
**Gate Type**: MUST_WORK

---

## Hypothesis Statement

**Layer-wise weight tokenization preserves sufficient structural signal for backbone comparison tasks (property prediction, symmetry tests)**

**Success Criterion**: Property prediction accuracy >60% on held-out models (significantly above random baseline)

**Rationale**: Foundation check before testing backbone complementarity. If layer-wise processing destroys signal, all downstream hypotheses (H-M1, H-M2, H-C1) are blocked.

---

## Experimental Design

### Dataset Specification

**Type**: standard  
**Name**: timm Model Zoo (Vision Transformers + ConvNets)  
**Rationale**: Real pre-trained models with known metadata (architecture, test accuracy, training dataset)

**Dataset Construction**:
- **Source**: `timm` library pre-trained models
- **Model Families**: 
  - Vision Transformers (ViT, DeiT, Swin)
  - ConvNets (ResNet, EfficientNet, MobileNet)
- **Sample Size**: 
  - Minimum: 500 models (statistically meaningful)
  - Target: 1000+ models (full timm zoo coverage)
- **Labels (Properties to Predict)**:
  1. **Test Accuracy** (regression): ImageNet-1k top-1 accuracy
  2. **Architecture Family** (classification): ViT, ResNet, EfficientNet, MobileNet, Swin, DeiT
  3. **Model Size** (regression): Total parameter count
  4. **Input Resolution** (classification): 224, 384, 512

**Data Split**:
- Train: 70% (700 models)
- Validation: 15% (150 models)
- Test: 15% (150 models)
- Stratified by architecture family

**Cache Path**: `./data/model_zoo_cache/`

---

### Baseline Experiment Specifications

#### Baseline 1: Random Guess
- **Purpose**: Lower bound performance check
- **Implementation**: Uniform random prediction from label distribution
- **Expected Performance**: 
  - Accuracy classification: ~16.7% (6 architecture families)
  - Test accuracy regression: R² ≈ 0

#### Baseline 2: Mean Predictor
- **Purpose**: Sanity check for regression tasks
- **Implementation**: Predict mean label value from training set
- **Expected Performance**: R² ≈ 0

#### Baseline 3: Simple MLP on Raw Weights
- **Purpose**: Control for tokenization overhead
- **Implementation**: 
  - Flatten all model weights → single vector
  - 2-layer MLP: [weight_dim, 512, num_classes]
  - No layer-wise structure
- **Expected Performance**: Baseline to compare against tokenized approach

#### Baseline 4: Layer-wise Weight Tokenization + Transformer
- **Purpose**: PRIMARY EXPERIMENT - Test H-E1 hypothesis
- **Implementation**:
  1. **Weight Tokenization**:
     - For each layer in model:
       - Flatten layer weights: `w_layer.flatten()` 
       - Embed to fixed dimension: `Linear(layer_size, 256)`
       - Result: One token per layer [num_layers, 256]
  2. **Backbone Architecture**:
     - Transformer encoder (2 layers, 4 heads, 256 dim)
     - Positional encoding for layer ordering
     - Global average pooling over layer tokens
  3. **Prediction Head**:
     - MLP: [256, 128, num_classes]
- **Training**:
  - Optimizer: AdamW (lr=1e-4, weight_decay=0.01)
  - Batch size: 32
  - Epochs: 50
  - Early stopping: 10 epochs patience on validation loss
- **Expected Performance**: >60% accuracy on architecture family classification

---

### Measurement Plan

#### Primary Metrics
1. **Architecture Family Classification Accuracy**:
   - Metric: Top-1 accuracy on test set
   - Success threshold: >60% (random baseline: 16.7%)
   - Why: Tests if layer-wise tokens preserve architecture-discriminative signal

2. **Test Accuracy Prediction (Regression)**:
   - Metric: R² score, Mean Absolute Error (MAE)
   - Success threshold: R² > 0.5, MAE < 5%
   - Why: Tests if layer-wise tokens preserve performance-related signal

#### Secondary Metrics
3. **Model Size Prediction (Regression)**:
   - Metric: R² score
   - Success threshold: R² > 0.7
   - Why: Easier task (size correlates with layer count), sanity check

4. **Input Resolution Classification**:
   - Metric: Top-1 accuracy
   - Success threshold: >70% (random baseline: 33%)
   - Why: Tests if input shape information is preserved

#### Ablation Studies
- **Tokenization Method**: Compare linear embedding vs learned projection vs autoencoder
- **Pooling Strategy**: Compare global average vs max vs attention pooling
- **Layer Subset**: Test if using only conv/linear layers improves signal

---

### Statistical Testing

**Hypothesis Test**: One-tailed t-test
- **Null hypothesis (H₀)**: Layer-wise tokenization accuracy ≤ random baseline
- **Alternative hypothesis (H₁)**: Layer-wise tokenization accuracy > random baseline
- **Significance level**: α = 0.05
- **Power analysis**: Minimum detectable effect size = 10% accuracy improvement

**Cross-Validation**:
- 5-fold stratified cross-validation on train+val set
- Report mean ± std across folds
- Test set held out for final evaluation only

---

### Falsification Criteria

**H-E1 FAILS if any of these conditions hold**:
1. Architecture family accuracy ≤ 30% (< 2× random baseline)
2. Test accuracy R² < 0.2 (near-zero predictive power)
3. Model size R² < 0.5 (fails sanity check)
4. No significant difference from random baseline (p > 0.05)

**Failure Interpretation**:
- Layer-wise processing loses too much structural information
- Cross-layer dependencies are critical (cannot be ignored)
- Alternative tokenization scheme required (e.g., graph-based)

**Contingency Plan**:
- Route to Phase 2A Dialogue for hypothesis modification
- Consider alternatives: full-network graph tokenization, hierarchical layer grouping

---

### Expected Results

**If H-E1 PASSES** (architecture accuracy >60%, test accuracy R² >0.5):
- **Interpretation**: Layer-wise tokenization preserves sufficient signal for property prediction
- **Next Steps**: Proceed to H-M1 and H-M2 (mechanism hypotheses)
- **Implications**: Validates Assumption A1 from Phase 2A

**If H-E1 PARTIALLY PASSES** (30-60% accuracy):
- **Interpretation**: Weak signal preservation, borderline feasibility
- **Action**: Investigate ablation studies (tokenization method, pooling strategy)
- **Decision**: Conditional proceed to H-M1/H-M2 with caution flag

**If H-E1 FAILS** (<30% accuracy):
- **Interpretation**: Layer-wise processing destroys critical signal
- **Action**: HALT downstream hypotheses (H-M1, H-M2, H-C1)
- **Next Steps**: Route to Phase 2A Dialogue for fundamental assumption revision

---

## Implementation Checklist

### Phase 3 (Implementation Planning)
- [ ] PRD: Dataset loading pipeline (timm model zoo)
- [ ] PRD: Weight tokenization module (layer-wise embedding)
- [ ] PRD: Baseline architectures (MLP, Transformer)
- [ ] PRD: Training loop (AdamW, early stopping)
- [ ] PRD: Evaluation metrics (accuracy, R², MAE)
- [ ] Architecture: Data pipeline (model loader, tokenizer, dataloader)
- [ ] Architecture: Model architecture (tokenizer, backbone, predictor head)
- [ ] Architecture: Training infrastructure (trainer, evaluator, logger)

### Phase 4 (Coding & Validation)
- [ ] Implement dataset construction (download timm models, extract metadata)
- [ ] Implement weight tokenization (flatten, embed, stack)
- [ ] Implement baselines (random, mean, MLP, Transformer)
- [ ] Implement training loop (optimizer, scheduler, early stopping)
- [ ] Implement evaluation pipeline (metrics, cross-validation, statistical tests)
- [ ] Validate on small subset (10 models, 5 epochs)
- [ ] Run full experiment (1000 models, 50 epochs)
- [ ] Generate result tables and plots

### Phase 5 (Baseline Comparison)
- [ ] Compare against related work (model stitching, weight-space learning)
- [ ] Contextualize results (what does 60% accuracy mean?)
- [ ] Identify limitations (timm zoo bias, architecture coverage)

---

## Resource Requirements

**Compute**:
- GPU: 1× NVIDIA V100 or A100
- RAM: 32GB
- Storage: 50GB (timm model cache)

**Time Estimate**:
- Dataset construction: 2 hours (download + cache)
- Training (per baseline): 30 minutes
- Full experiment (4 baselines × 5 folds): 10 hours
- Total: ~12 hours

**Dependencies**:
- PyTorch 2.0+
- timm 0.9+
- numpy, pandas, scikit-learn
- matplotlib, seaborn (visualization)

---

## Risk Mitigation

**Risk 1**: timm models have heterogeneous layer structures
- **Mitigation**: Pad/truncate to fixed sequence length OR use variable-length attention
- **Fallback**: Use only models with similar depth (e.g., ResNet family)

**Risk 2**: Weight tokenization dimensionality explosion
- **Mitigation**: Use adaptive embedding (large layers → compressed, small layers → padded)
- **Fallback**: Use PCA/SVD for dimensionality reduction per layer

**Risk 3**: Class imbalance (timm has more ResNets than ViTs)
- **Mitigation**: Stratified sampling, class-weighted loss
- **Fallback**: Oversample minority classes

---

## Code Examples from Research

**[INFERRED]** Weight Tokenization Pattern:
```python
def tokenize_weights(model, embed_dim=256):
    layer_tokens = []
    for name, param in model.named_parameters():
        if 'weight' in name:  # Skip biases
            flat = param.data.flatten()
            # Adaptive embedding for variable layer sizes
            embedding = nn.Linear(flat.size(0), embed_dim)
            token = embedding(flat.unsqueeze(0))
            layer_tokens.append(token)
    return torch.stack(layer_tokens, dim=1)  # [1, num_layers, embed_dim]
```

**[INFERRED]** Model Zoo Dataset Construction:
```python
import timm
dataset = []
for model_name in timm.list_models(pretrained=True):
    try:
        model = timm.create_model(model_name, pretrained=True)
        cfg = timm.get_pretrained_cfg(model_name)
        dataset.append({
            'name': model_name,
            'weights': tokenize_weights(model),
            'accuracy': cfg.test_acc_top1,
            'architecture': model_name.split('_')[0],
            'params': sum(p.numel() for p in model.parameters())
        })
    except Exception as e:
        print(f"Skipped {model_name}: {e}")
```

---

## Archon Project Integration

**Pipeline Project ID**: mock-pipeline-proj-001  
**Hypothesis Task ID**: mock-task-e1-001  
**Phase 2C Task ID**: mock-phase2c-task

**Archon Document IDs** (to be generated in Phase 3):
- PRD: `mock-prd-e1-001`
- Architecture: `mock-arch-e1-001`
- Experiment Design: `mock-expdesign-e1-001`

---

**End of Phase 2C Experiment Design Brief — H-E1**
