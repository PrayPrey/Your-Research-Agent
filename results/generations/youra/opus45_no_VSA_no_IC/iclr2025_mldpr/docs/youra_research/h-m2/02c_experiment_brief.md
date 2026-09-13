# Phase 2C: Experiment Brief for H-M2

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Generated:** 2026-08-24  
**Prerequisites:** h-e1 (VALIDATED)

---

## Hypothesis Statement

Models fine-tuned on a single benchmark show larger cross-dataset gap than models fine-tuned on a mix of 3+ benchmarks (>5 percentage points difference).

---

## Experiment Design

### Overview

Compare cross-dataset generalization between two training regimes:
1. **Single-benchmark:** Fine-tune on one dataset, evaluate on held-out domains
2. **Multi-benchmark:** Fine-tune on 3+ datasets combined, evaluate on same held-out domains

Measure the "cross-dataset gap" (in-distribution accuracy minus out-of-distribution accuracy) for each regime.

### Experimental Conditions

| Condition | Training Data | Evaluation | Models |
|-----------|---------------|------------|--------|
| Single-CUB | CUB-200-2011 only | NABirds, Dogs, Cars | 3 seeds |
| Single-Dogs | Stanford Dogs only | NABirds, CUB, Cars | 3 seeds |
| Single-Cars | Stanford Cars only | NABirds, CUB, Dogs | 3 seeds |
| Single-Aircraft | FGVC Aircraft only | NABirds, CUB, Dogs | 3 seeds |
| Single-Flowers | Oxford Flowers 102 only | NABirds, CUB, Dogs | 3 seeds |
| Multi-3mix | CUB + Dogs + Cars | NABirds, Flowers, Aircraft | 3 seeds |
| Multi-4mix | CUB + Dogs + Cars + Flowers | NABirds, Aircraft | 3 seeds |
| Multi-5mix | All 5 benchmarks | NABirds | 3 seeds |

**Total Models:** 24 (8 conditions × 3 seeds)

### Cross-Dataset Gap Definition

```
Gap_single = Acc_train_domain - Acc_test_domain (averaged across held-out domains)
Gap_multi = Acc_train_domains - Acc_test_domain (averaged across held-out domains)
```

For fair comparison, evaluate all models on the same held-out test set (NABirds) using a unified evaluation protocol.

---

## Phase 1: Model Fine-tuning

### Single-Benchmark Training

| Parameter | Value |
|-----------|-------|
| Base Model | ResNet-50 (ImageNet-1K pretrained, torchvision) |
| Benchmarks | CUB, Dogs, Cars, Aircraft, Flowers (5 separate) |
| Seeds | 3 per benchmark |
| Total Models | 15 |
| Epochs | 30 |
| Optimizer | SGD (momentum=0.9, weight_decay=1e-4) |
| Learning Rate | 0.01, cosine annealing |
| Batch Size | 32 |

### Multi-Benchmark Training

| Parameter | Value |
|-----------|-------|
| Base Model | ResNet-50 (ImageNet-1K pretrained, torchvision) |
| Dataset | ConcatDataset of 3/4/5 benchmarks |
| Class Mapping | Unified label space (offset per dataset) |
| Seeds | 3 per mix configuration |
| Total Models | 9 (3 configurations × 3 seeds) |
| Epochs | 30 |
| Sampling | Balanced sampling across datasets |
| Optimizer | SGD (momentum=0.9, weight_decay=1e-4) |
| Learning Rate | 0.01, cosine annealing |
| Batch Size | 32 |

**Implementation Note:** Use `torch.utils.data.ConcatDataset` with weighted sampling to balance datasets of different sizes.

```python
# Multi-dataset training
from torch.utils.data import ConcatDataset, WeightedRandomSampler

datasets = [cub_train, dogs_train, cars_train]
combined = ConcatDataset(datasets)

# Balanced sampling weights
weights = []
for i, ds in enumerate(datasets):
    weights.extend([1.0 / len(ds)] * len(ds))
sampler = WeightedRandomSampler(weights, len(combined))
```

---

## Phase 2: Cross-Dataset Evaluation

### Evaluation Protocol

For each fine-tuned model, evaluate on:
1. **In-distribution test set** (same benchmark as training)
2. **Out-of-distribution test sets** (other benchmarks)
3. **Held-out domain** (NABirds - not used in any training)

### Evaluation Metric: k-NN Classification

Since label spaces differ across datasets, use k-NN on frozen features:

| Parameter | Value |
|-----------|-------|
| Feature Layer | Penultimate (avgpool, 2048-d) |
| k-NN | k=5, cosine similarity |
| Support Set | 5 examples per class from target dataset train split |
| Query Set | Full test split of target dataset |

```python
def knn_accuracy(model, support_loader, query_loader, k=5):
    """Evaluate model on target dataset via k-NN."""
    model.eval()
    
    # Extract support features
    support_feats, support_labels = extract_features(model, support_loader)
    
    # Extract query features
    query_feats, query_labels = extract_features(model, query_loader)
    
    # k-NN classification
    from sklearn.neighbors import KNeighborsClassifier
    knn = KNeighborsClassifier(n_neighbors=k, metric='cosine')
    knn.fit(support_feats, support_labels)
    preds = knn.predict(query_feats)
    
    return (preds == query_labels).mean()
```

### Cross-Dataset Gap Calculation

```python
def compute_gap(in_dist_acc, out_dist_accs):
    """Compute cross-dataset generalization gap."""
    mean_out_acc = np.mean(out_dist_accs)
    gap = in_dist_acc - mean_out_acc
    return gap
```

---

## Datasets

### Training Benchmarks (5)

| Dataset | Classes | Train Images | Test Images |
|---------|---------|--------------|-------------|
| CUB-200-2011 | 200 | 5,994 | 5,794 |
| Stanford Dogs | 120 | 12,000 | 8,580 |
| Oxford Flowers 102 | 102 | 2,040 | 6,149 |
| Stanford Cars | 196 | 8,144 | 8,041 |
| FGVC Aircraft | 100 | 6,667 | 3,333 |

### Held-Out Evaluation Domain

| Dataset | Classes | Test Images | Purpose |
|---------|---------|-------------|---------|
| NABirds | 555 | ~24,000 | Primary OOD evaluation |

---

## Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Gap Difference | >5pp | Mean(Gap_single) - Mean(Gap_multi) > 5 percentage points |
| Statistical Significance | p < 0.05 | Two-sample t-test comparing gap distributions |
| Effect Size | Cohen's d > 0.5 | Medium effect or larger |

### Falsification Criteria

- **Fail if:** Gap_multi ≥ Gap_single (multi-benchmark models have equal or larger gap)
- **Inconclusive if:** 0 < Gap_single - Gap_multi < 5pp (effect exists but below threshold)

---

## Statistical Analysis

1. **Primary Comparison:** Independent samples t-test
   - Group 1: Gap values from single-benchmark models (n=15)
   - Group 2: Gap values from multi-benchmark models (n=9)
   
2. **Effect Size:** Cohen's d with pooled standard deviation

3. **Confidence Intervals:** 95% CI via bootstrap (1000 resamples)

4. **Visualization:** 
   - Box plots: Gap distribution by training regime
   - Bar chart: Mean gap ± SE by condition

---

## Baseline Experiments

### Baseline 1: ImageNet Pretrained (No Fine-tuning)
- Use frozen ImageNet pretrained ResNet-50
- Measure cross-dataset gap with k-NN
- Expected: Moderate gap, no benchmark-specific bias

### Baseline 2: Dataset Size Control
- Subsample multi-benchmark training to match single-benchmark size
- Controls for total training samples vs diversity effect

### Baseline 3: Random Multi-benchmark Assignment
- Shuffle which benchmarks are combined
- Tests whether specific combinations matter

---

## Implementation Specification

### Directory Structure

```
src/
├── data/
│   ├── datasets.py              # Dataset loaders
│   ├── multi_dataset.py         # ConcatDataset with balanced sampling
│   └── transforms.py            # Standard augmentations
├── models/
│   └── feature_extractor.py     # ResNet-50 feature extraction
├── training/
│   ├── finetune_single.py       # Single-benchmark training
│   └── finetune_multi.py        # Multi-benchmark training
├── evaluation/
│   ├── knn_eval.py              # k-NN cross-dataset evaluation
│   └── gap_analysis.py          # Gap computation and statistics
├── experiments/
│   └── h_m2_training_regime.py  # Main experiment script
└── utils/
    └── metrics.py               # Accuracy, gap metrics
```

### Key Configuration

```python
# Experiment config
CONFIG = {
    "single_benchmarks": ["cub", "dogs", "cars", "aircraft", "flowers"],
    "multi_configs": [
        ["cub", "dogs", "cars"],           # 3-mix
        ["cub", "dogs", "cars", "flowers"], # 4-mix
        ["cub", "dogs", "cars", "flowers", "aircraft"],  # 5-mix
    ],
    "seeds": [42, 123, 456],
    "held_out_eval": "nabirds",
    "knn_k": 5,
    "knn_support_per_class": 5,
}
```

### Dependencies

```
torch>=2.0
torchvision>=0.15
timm>=0.9
scikit-learn>=1.3
scipy>=1.10
numpy
pandas
tqdm
matplotlib
seaborn
```

---

## Compute Budget

| Phase | GPU Hours | Notes |
|-------|-----------|-------|
| Single-benchmark training | 10h | 15 models × 30 epochs |
| Multi-benchmark training | 8h | 9 models × 30 epochs (larger batches) |
| Feature extraction | 3h | 24 models × 6 datasets |
| k-NN evaluation | 1h | CPU-intensive but parallelizable |
| **Total** | ~22h | Single A100/V100 |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Class imbalance in multi-dataset | WeightedRandomSampler for balanced training |
| Label space mismatch | Use k-NN (no label mapping needed) |
| Dataset size confound | Report results normalized by training size |
| Small effect size | Increase seeds if needed (6 per condition) |
| Memory for large feature matrices | Batch extraction, disk caching |

---

## Output Artifacts

1. `models/single_benchmark/` — 15 single-benchmark checkpoints
2. `models/multi_benchmark/` — 9 multi-benchmark checkpoints
3. `features/` — Extracted features per model × dataset
4. `results/h_m2_results.json` — Gap statistics, t-test, effect size
5. `figures/gap_comparison.png` — Box plots by training regime
6. `figures/gap_by_condition.png` — Detailed bar chart
7. `04_validation.md` — Validation report

---

## Analysis Pipeline

```python
def run_analysis():
    # 1. Compute gaps for all models
    single_gaps = []
    for model_path in single_benchmark_models:
        model = load_model(model_path)
        in_acc = evaluate_in_distribution(model)
        out_accs = [evaluate_ood(model, ds) for ds in ood_datasets]
        gap = compute_gap(in_acc, out_accs)
        single_gaps.append(gap)
    
    multi_gaps = []
    for model_path in multi_benchmark_models:
        model = load_model(model_path)
        in_acc = evaluate_in_distribution(model)  # avg across train domains
        out_accs = [evaluate_ood(model, ds) for ds in ood_datasets]
        gap = compute_gap(in_acc, out_accs)
        multi_gaps.append(gap)
    
    # 2. Statistical comparison
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(single_gaps, multi_gaps)
    
    # 3. Effect size
    cohens_d = (np.mean(single_gaps) - np.mean(multi_gaps)) / pooled_std(single_gaps, multi_gaps)
    
    # 4. Report
    mean_diff = np.mean(single_gaps) - np.mean(multi_gaps)
    print(f"Gap difference: {mean_diff:.2f}pp")
    print(f"p-value: {p_value:.4f}")
    print(f"Cohen's d: {cohens_d:.2f}")
    
    return {
        "gap_difference_pp": mean_diff,
        "p_value": p_value,
        "cohens_d": cohens_d,
        "hypothesis_supported": mean_diff > 5 and p_value < 0.05
    }
```

---

## Connection to H-E1

This experiment builds on H-E1 (fingerprint detectability):
- H-E1 showed benchmark fingerprints exist in representations
- H-M2 tests whether mixing benchmarks during training reduces both fingerprint strength and generalization gap
- Models from H-M2 can be used to validate H-E1's probe (multi-benchmark models should have weaker fingerprints)

---

## Next Steps

1. **Phase 3:** Generate PRD, Architecture, PRP from this brief
2. **Phase 4:** Implement and validate
3. **Phase 5:** Compare results to H-E1 fingerprint strength correlation
