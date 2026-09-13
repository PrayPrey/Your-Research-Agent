# Phase 2C: Experiment Brief for H-E1

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Generated:** 2026-08-24

---

## Hypothesis Statement

A linear classifier trained on penultimate layer representations can predict which fine-tuning benchmark was used with >60% accuracy (chance=20% for 5 benchmarks).

---

## Experiment Design

### Overview

Train ResNet-50 models on 5 fine-grained classification benchmarks, extract penultimate layer features, train a linear probe to classify which benchmark produced each model's representations.

### Phase 1: Model Fine-tuning

| Parameter | Value |
|-----------|-------|
| Base Model | ResNet-50 (ImageNet-1K pretrained, torchvision) |
| Benchmarks | CUB-200-2011, Stanford Dogs, Oxford Flowers 102, Stanford Cars, FGVC Aircraft |
| Seeds | 3 per benchmark |
| Total Models | 15 |
| Epochs | 30 |
| Optimizer | SGD (momentum=0.9, weight_decay=1e-4) |
| Learning Rate | 0.01, cosine annealing to 0 |
| Batch Size | 32 |
| Input Size | 224×224 |
| Augmentation | RandomResizedCrop(224), RandomHorizontalFlip, Normalize(ImageNet) |

### Phase 2: Feature Extraction

| Parameter | Value |
|-----------|-------|
| Layer | Penultimate (avgpool output, 2048-d) |
| Extraction Method | `model.avgpool` output or `forward_features()` |
| Probe Dataset | NABirds test set (held-out domain) |
| Samples per Model | Full NABirds test set (~24,000 images) |
| Total Feature Vectors | 15 models × 24,000 = 360,000 |

### Phase 3: Linear Probe Training

| Parameter | Value |
|-----------|-------|
| Classifier | LogisticRegression (sklearn) or nn.Linear |
| Input | 2048-d feature vector |
| Output | 5-class (benchmark label) |
| Train/Val/Test Split | 70/15/15 by model (stratified) |
| Regularization | L2, C=1.0 |
| Metric | Classification accuracy |

---

## Datasets

### Fine-tuning Benchmarks (5)

| Dataset | Classes | Train Images | Test Images | Download |
|---------|---------|--------------|-------------|----------|
| CUB-200-2011 | 200 | 5,994 | 5,794 | [Link](http://www.vision.caltech.edu/datasets/cub_200_2011/) |
| Stanford Dogs | 120 | 12,000 | 8,580 | [Link](http://vision.stanford.edu/aditya86/StanfordDogs/) |
| Oxford Flowers 102 | 102 | 2,040 | 6,149 | torchvision |
| Stanford Cars | 196 | 8,144 | 8,041 | [Link](http://ai.stanford.edu/~jkrause/cars/car_dataset.html) |
| FGVC Aircraft | 100 | 6,667 | 3,333 | torchvision |

### Probe Dataset (Held-out)

| Dataset | Classes | Test Images | Purpose |
|---------|---------|-------------|---------|
| NABirds | 555 | ~24,000 | Feature extraction for fingerprint detection |

---

## Implementation Specification

### Directory Structure

```
src/
├── data/
│   ├── datasets.py          # Dataset loaders for all 6 datasets
│   └── transforms.py        # Standard augmentations
├── models/
│   └── feature_extractor.py # ResNet-50 with feature hook
├── training/
│   ├── finetune.py          # Fine-tuning loop
│   └── linear_probe.py      # Logistic regression probe
├── experiments/
│   └── h_e1_fingerprint.py  # Main experiment script
└── utils/
    └── metrics.py           # Accuracy, confusion matrix
```

### Key Functions

```python
# Feature extraction (timm pattern)
def extract_features(model, dataloader, device):
    model.eval()
    features, labels = [], []
    with torch.no_grad():
        for x, y in dataloader:
            x = x.to(device)
            feat = model.forward_features(x)  # or hook avgpool
            feat = F.adaptive_avg_pool2d(feat, 1).flatten(1)
            features.append(feat.cpu())
            labels.append(y)
    return torch.cat(features), torch.cat(labels)

# Linear probe
def train_probe(features, benchmark_labels):
    from sklearn.linear_model import LogisticRegression
    clf = LogisticRegression(max_iter=1000, C=1.0)
    clf.fit(features, benchmark_labels)
    return clf
```

### Dependencies

```
torch>=2.0
torchvision>=0.15
timm>=0.9
scikit-learn>=1.3
numpy
pandas
tqdm
```

---

## Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Probe Accuracy | >60% | 5-class classification on held-out model features |
| Chance Level | 20% | 1/5 random baseline |
| Falsification | ≤25% | Near-chance indicates no detectable fingerprint |

---

## Statistical Analysis

1. **Primary Metric:** Mean accuracy across 3-fold cross-validation (models as units)
2. **Confidence Interval:** 95% CI via bootstrap (1000 resamples)
3. **Significance Test:** One-sample t-test vs chance (20%)
4. **Effect Size:** Cohen's d

---

## Baseline Experiments

### Baseline 1: Random Features
- Extract features from untrained ResNet-50
- Expected accuracy: ~20% (chance)

### Baseline 2: Same-benchmark Features
- Train probe on features from same benchmark (not NABirds)
- Expected accuracy: Higher (task-specific signals)

### Baseline 3: Shuffled Labels
- Permute benchmark labels
- Expected accuracy: ~20% (sanity check)

---

## Compute Budget

| Phase | GPU Hours | Notes |
|-------|-----------|-------|
| Fine-tuning | 10h | 15 models × 30 epochs × ~40min each |
| Feature extraction | 2h | 15 models × 6 datasets |
| Probe training | <1h | CPU-only sklearn |
| **Total** | ~13h | Single A100/V100 |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Dataset download failures | Use torchvision where available; cache locally |
| Memory for 360k features | Extract in batches, save to disk |
| Overfitting probe | Use regularization, cross-validation |
| Weak signal | Increase probe data, try non-linear probes |

---

## Output Artifacts

1. `models/finetuned/` — 15 fine-tuned ResNet-50 checkpoints
2. `features/` — Extracted feature matrices per model
3. `results/h_e1_results.json` — Probe accuracy, CI, p-value
4. `figures/confusion_matrix.png` — 5×5 benchmark confusion
5. `04_validation.md` — Validation report

---

## Next Steps

1. **Phase 3:** Generate PRD, Architecture, PRP from this brief
2. **Phase 4:** Implement and validate
3. **Phase 5:** Compare to baseline expectations
