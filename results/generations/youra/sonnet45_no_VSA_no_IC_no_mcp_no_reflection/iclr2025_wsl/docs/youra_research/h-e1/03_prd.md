# Product Requirements Document: h-e1

**Date:** 2026-08-28  
**Author:** Phase 3 Pipeline  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  

---

## Executive Summary

Validate foundational assumption A1: layer-wise weight tokenization preserves structural signal for backbone comparison tasks. Build weight transformer for property prediction on timm model zoo (100-200 pre-trained vision models). Success criterion: >60% test accuracy on architecture family classification, significantly above random (20-25%) and weight statistics baseline (30-40%).

---

## Problem Statement

Before testing backbone complementarity (H-M1, H-M2), must verify layer-wise processing doesn't destroy signal. If tokenization loses cross-layer dependencies, entire weight-space learning pipeline fails.

**Success Metric:** Test accuracy >60% on architecture family classification
**Baseline:** Random 20-25%, Weight statistics 30-40%

---

## Requirements

### Functional Requirements

#### FR-1: Data Loader
- Extract layer-wise weights from timm models
- Filter 100-200 models across ResNet, ViT, EfficientNet, ConvNeXt families
- Split 70% train / 15% val / 15% test by architecture family
- Cache extracted weights locally

#### FR-2: Weight Tokenization
- Flatten each layer → weight token sequence
- Pad/truncate to max layer size
- Add layer position encoding
- Normalize per-layer (zero mean, unit variance)

#### FR-3: Transformer Backbone
- Input: [batch, num_layers, layer_size]
- Token projection: layer_size → d_model=256
- Positional encoding: layer index
- TransformerEncoder: 6 layers, 8 heads, 1024 FFN dim
- Global pooling: mean over layers
- Output: [batch, d_model]

#### FR-4: Baseline Model
- Extract layer statistics: mean, std, L2 norm per layer
- 3-layer MLP: 256 → 128 → num_classes
- Same training protocol as transformer

#### FR-5: Training
- Optimizer: AdamW, lr=1e-4, weight_decay=1e-5
- Scheduler: CosineAnnealingLR (T_max=50, eta_min=1e-6)
- Loss: CrossEntropyLoss (architecture family classification)
- Batch size: 32 models
- Epochs: 50, early stopping patience=10
- Gradient clipping: max_norm=1.0

#### FR-6: Evaluation
- Report test accuracy on held-out 15% split
- Compare: Random vs Baseline vs Proposed
- Generate confusion matrix, training curves, attention heatmap
- Save all figures to `h-e1/figures/`

### Non-Functional Requirements

#### NFR-1: Reproducibility
- Fixed random seed (42)
- Deterministic data splits by architecture family
- Log all hyperparameters to YAML config

#### NFR-2: Logging
- Train/val loss and accuracy per epoch
- Final test metrics (accuracy, confusion matrix)
- Model checkpoint at best validation accuracy

#### NFR-3: Computational Budget
- Single GPU training (A100 or equivalent)
- ~2-4 hours training time for 50 epochs
- Memory: <16GB GPU RAM

---

## Success Criteria

### MUST_WORK Gate
- Test accuracy >60% on architecture family classification
- Outperform random baseline (20-25%) by >35 percentage points
- Outperform weight statistics baseline (30-40%) by >20 percentage points

### Failure Conditions
- Test accuracy <50%: Layer-wise tokenization loses too much signal
- Overfitting: Train accuracy >80%, test accuracy <50%

---

## System Architecture

```
timm Model Zoo (100-200 models)
  ↓
Data Loader: Extract layer weights
  ↓
Weight Tokenizer: Flatten layers → tokens + position encoding
  ↓
[Transformer Backbone] → Global Pooling → MLP Head → Predictions
[Baseline: Layer Stats] → MLP → Predictions
  ↓
Training Loop: AdamW + CosineAnnealingLR + Early Stopping
  ↓
Evaluation: Test accuracy, confusion matrix, figures
  ↓
Gate Check: accuracy >60%?
```

---

## Deliverables

### Code
- `data_loader.py`: timm model extraction, weight tokenization
- `model.py`: WeightTransformer, BaselineMLP
- `train.py`: Training loop, early stopping, logging
- `evaluate.py`: Test metrics, confusion matrix, figures

### Outputs
- `h-e1/figures/gate_metrics.png`: Bar chart (Random vs Baseline vs Proposed)
- `h-e1/figures/training_curves.png`: Train/val loss and accuracy
- `h-e1/figures/confusion_matrix.png`: Per-family accuracy
- `h-e1/figures/attention_heatmap.png`: Transformer attention over layers
- `h-e1/04_validation.md`: Final report with gate decision

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Layer-wise tokenization loses cross-layer dependencies | High (blocks all downstream hypotheses) | Two-stage validation: synthetic networks first → timm zoo |
| Small dataset (100-200 models) causes overfitting | Medium | Aggressive regularization (dropout 0.1, weight decay 1e-5) |
| Imbalanced architecture families | Medium | Stratified split by family, report per-family accuracy |
| OOM on large models | Low | Limit max layer size, batch size 32 |

---

## Timeline Estimate

- **Data Preparation:** 2 hours (timm model extraction, weight caching)
- **Model Implementation:** 4 hours (Transformer, Baseline, data loader)
- **Training:** 4 hours (2 models × 50 epochs each)
- **Evaluation:** 1 hour (metrics, figures)
- **Total:** ~11 hours (automated via Phase 4 Coder-Validator loop)

---

## Appendix: Configuration Schema

```yaml
# config.yaml
data:
  source: timm
  families: [resnet, vit, efficientnet, convnext]
  num_models: 100
  splits:
    train: 0.7
    val: 0.15
    test: 0.15
  cache_path: ./data/model_zoo_cache/

model:
  type: transformer
  d_model: 256
  nhead: 8
  num_layers: 6
  dim_feedforward: 1024
  dropout: 0.1
  max_layer_size: 4096
  num_classes: 4  # ResNet, ViT, EfficientNet, ConvNeXt

training:
  optimizer: AdamW
  lr: 1e-4
  weight_decay: 1e-5
  batch_size: 32
  epochs: 50
  early_stopping_patience: 10
  gradient_clip_max_norm: 1.0
  scheduler:
    type: CosineAnnealingLR
    T_max: 50
    eta_min: 1e-6

evaluation:
  gate_threshold: 0.6
  random_baseline: 0.25
  stats_baseline: 0.35
```

---

*Document Status: FINAL*  
*Next Step: Phase 3 - Architecture, Logic, Config agent generation*
