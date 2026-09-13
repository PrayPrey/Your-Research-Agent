# Phase 2C: Experiment Brief

**Generated**: 2026-08-25  
**Hypothesis ID**: h-c1  
**Hypothesis Type**: CONDITION  
**Gate**: SHOULD_WORK  
**Prerequisites**: h-e1 (VALIDATED)

---

## Hypothesis Statement

**Signatures generalize across datasets**: Architecture ranking by worst-group gap at 90% average accuracy is consistent from Waterbirds to CelebA, with Spearman rank correlation ρ > 0.8.

---

## Research Context

### From Prerequisites (h-e1)
- **Validated**: BN-LN gap difference exists (9.41 pp, p < 0.001)
- **Proven architectures**: ResNet-18-BN, ResNet-18-LN both reach 90% avg accuracy on Waterbirds
- **Established protocol**: 10 seeds, accuracy-matched comparison at 90% threshold

### Research Question
Does the architectural ranking observed on Waterbirds (based on worst-group gap at 90% average accuracy) transfer to CelebA dataset with high rank correlation (ρ > 0.8)?

---

## Dataset Specification

### Primary Dataset: Waterbirds
- **Source**: Sagawa et al. 2020 (https://github.com/kohpangwei/group_DRO)
- **Task**: Binary classification (waterbird vs landbird)
- **Spurious correlation**: Background (water vs land), 95% correlation in training set
- **Splits**: 4795 train / 1199 val / 5794 test
- **Groups**: 4 groups (waterbird-water, waterbird-land, landbird-water, landbird-land)
- **Preprocessing**: Resize to 224×224, ImageNet normalization
- **Augmentation**: Random horizontal flip, random crop (training only)
- **Status**: Already validated in h-e1

### Secondary Dataset: CelebA
- **Source**: Liu et al. 2015 (http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html)
- **Task**: Binary classification (Blond Hair attribute)
- **Spurious correlation**: Gender (Male/Female), 95% correlation in training set
- **Splits**: Standard CelebA splits (162,770 train / 19,867 val / 19,962 test)
- **Groups**: 4 groups (blond-male, blond-female, not-blond-male, not-blond-female)
- **Preprocessing**: Center crop 178×178, resize to 224×224, ImageNet normalization
- **Augmentation**: Random horizontal flip (training only)
- **Expected sample size**: Full test set (19,962 images)

---

## Model Architecture

### Architectures to Compare (from h-e1)
1. **ResNet-18-BN** (Batch Normalization baseline)
2. **ResNet-18-LN** (Layer Normalization)
3. **ResNet-18-CBAM** (Channel attention - if available from h-m2)
4. **ViT-Small** (Vision Transformer - if available from h-m2)

**Note**: Minimum 2 architectures required (BN, LN from h-e1). If h-m2 incomplete, use only BN/LN.

### Core Mechanism (Ranking Computation)

```python
# For each dataset (Waterbirds, CelebA):
for architecture in architectures:
    gaps = []
    for seed in range(10):
        # Train until 90% average accuracy reached
        model = train_until_threshold(
            architecture=architecture,
            dataset=dataset,
            target_avg_acc=0.90,
            seed=seed
        )
        
        # Measure worst-group gap at that checkpoint
        group_accs = evaluate_by_group(model, test_set)
        avg_acc = mean(group_accs)
        worst_acc = min(group_accs)
        gap = avg_acc - worst_acc
        gaps.append(gap)
    
    # Record mean gap for this architecture
    mean_gaps[architecture] = mean(gaps)

# Rank architectures by mean gap (lower = better)
waterbirds_ranking = rank_by_gap(mean_gaps_waterbirds)  # [1,2,3,4]
celeba_ranking = rank_by_gap(mean_gaps_celeba)          # [1,2,3,4]

# Compute Spearman rank correlation
rho, p_value = spearmanr(waterbirds_ranking, celeba_ranking)
```

**Key Logic**:
- Train each architecture on each dataset independently
- Find epoch where average accuracy crosses 90% threshold
- Measure worst-group gap at that epoch
- Average gaps across 10 seeds
- Rank architectures from best (rank 1) to worst (rank 4)
- Compare rankings across datasets via Spearman ρ

---

## Training Protocol

### Hyperparameters (Controlled - from h-e1)
- **Optimizer**: SGD with momentum 0.9
- **Learning rate**: 0.01 (constant, no schedule)
- **Batch size**: 64
- **Weight decay**: 1e-4
- **Initialization**: He initialization
- **Loss function**: Cross-entropy
- **Max epochs**: 100 (early stop when avg_acc ≥ 90%)

### Training Procedure
1. For each dataset (Waterbirds, CelebA):
   - For each architecture (BN, LN, [CBAM, ViT]):
     - For each seed (0-9):
       - Train from scratch
       - Log avg_acc and worst_group_gap every epoch
       - Identify first epoch where avg_acc ≥ 0.90
       - Record worst_group_gap at that epoch
       - Save checkpoint (optional, for analysis)

2. Compute statistics:
   - Mean gap per architecture per dataset (across 10 seeds)
   - Standard deviation of gaps
   - Rank architectures per dataset

3. Correlation analysis:
   - Compute Spearman ρ between Waterbirds and CelebA rankings
   - Compute p-value for ρ

---

## Evaluation Metrics

### Primary Metric: Spearman Rank Correlation (ρ)
- **Input**: Two ranking vectors (Waterbirds, CelebA)
- **Output**: Correlation coefficient ρ ∈ [-1, 1]
- **Interpretation**: ρ > 0.8 = strong positive correlation (rankings agree)

### Secondary Metrics:
- **Mean worst-group gap** per architecture per dataset
- **Kendall's tau** (alternative rank correlation, more robust to ties)
- **Rank reversal detection**: Count architectures with reversed ranking

### Success Criterion (PoC - Direction-Based):
- **PRIMARY**: Spearman ρ > 0.8 with p < 0.05
- **SECONDARY**: No rank reversals (rank difference ≤ 1 position allowed)
- **FAILURE**: ρ < 0.6 OR rank reversal in top-2 positions

**PoC Note**: This is a direction-based test. Full statistical power analysis deferred to Phase 5.

---

## Ablation Studies

### Ablation 1: Architecture Set Size
- **A1a**: BN + LN only (2 architectures, minimal test)
- **A1b**: BN + LN + CBAM + ViT (4 architectures, full test from Phase 2B)
- **Measures**: Does correlation strength depend on architecture diversity?

### Ablation 2: Dataset Order
- **A2a**: Train Waterbirds first, then CelebA
- **A2b**: Train CelebA first, then Waterbirds
- **Measures**: Ranking stability (should be identical, validates independence)

### Ablation 3: Alternative Correlation Metrics
- **A3a**: Spearman ρ (primary, rank-based)
- **A3b**: Kendall's tau (more robust to ties)
- **A3c**: Pearson r on gap magnitudes (not ranks)
- **Measures**: Sensitivity to metric choice

---

## Expected Baseline Performance

### From h-e1 (Waterbirds)
- ResNet-18-BN: ~18-20% worst-group gap at 90% avg acc
- ResNet-18-LN: ~9-11% worst-group gap at 90% avg acc
- **Ranking**: LN (rank 1) > BN (rank 2)

### Expected CelebA (from literature)
- BN architectures show higher spurious correlation sensitivity
- LN architectures more robust to spurious features
- **Predicted ranking**: LN (rank 1) > BN (rank 2)
- **Predicted ρ**: 0.85-0.95 (strong agreement if hypothesis holds)

### Null Hypothesis
- **H0**: Architectural signatures are dataset-specific (ρ ≈ 0)
- **H1**: Architectural signatures generalize (ρ > 0.8)

---

## Computational Requirements (PoC Estimate)

### Training Budget
- **Waterbirds**: 2 architectures × 10 seeds × ~30 epochs to 90% = 600 runs × 3 min = 30 GPU-hours
- **CelebA**: 2 architectures × 10 seeds × ~20 epochs to 90% = 400 runs × 8 min = 53 GPU-hours
- **Total**: ~83 GPU-hours (single V100) for minimal test (BN + LN only)

**Note**: If h-m2 completes, add +80 GPU-hours for CBAM + ViT (4 architectures total).

### Storage
- Checkpoints: 2 datasets × 2 architectures × 10 seeds × 1 checkpoint = 40 checkpoints × 45MB = 1.8GB
- Logs: ~50MB (CSV files with epoch-level metrics)

---

## Implementation Requirements

### Code Structure (Phase 3 will detail)
```
h-c1/
├── data/
│   ├── waterbirds_loader.py  # Reuse from h-e1
│   ├── celeba_loader.py       # NEW
│   └── group_metrics.py       # Reuse from h-e1
├── models/
│   ├── resnet_bn.py           # Reuse from h-e1
│   ├── resnet_ln.py           # Reuse from h-e1
│   └── model_factory.py       # Reuse from h-e1
├── train_to_threshold.py      # NEW (early stop at 90% avg acc)
├── compute_rankings.py         # NEW (rank by mean gap)
├── correlation_analysis.py     # NEW (Spearman, Kendall, p-values)
└── experiments/
    ├── waterbirds_experiment.sh  # Reuse from h-e1 with modifications
    └── celeba_experiment.sh       # NEW
```

### Key Implementation Notes
- **Reuse h-e1 code**: Waterbirds data loading, BN/LN models, group evaluation metrics
- **New components**: CelebA data loader, early stopping at threshold, ranking computation, correlation stats
- **No new architectures needed** if using only BN/LN from h-e1

---

## Risk Assessment

### Risk 1: CelebA Dataset Complexity
- **Issue**: CelebA has 40 attributes; selecting correct spurious correlation setup
- **Mitigation**: Use standard Blond-Gender setup from Sagawa et al. 2020 Group DRO paper
- **Fallback**: If CelebA unavailable, use CMNIST (mentioned in Phase 2B as boundary test)

### Risk 2: Insufficient Architecture Diversity
- **Issue**: Only 2 architectures (BN, LN) may show perfect correlation by chance
- **Mitigation**: Flag results as "limited test, need h-m2 completion for 4 architectures"
- **Fallback**: Defer to Phase 4.5 synthesis if h-m2 unavailable

### Risk 3: Ranking Ties
- **Issue**: Architectures with identical gaps create rank ambiguity
- **Mitigation**: Use mean gaps across 10 seeds to reduce tie probability
- **Fallback**: Use Kendall's tau (handles ties better than Spearman)

---

## References

### Datasets
1. **Waterbirds**: Sagawa et al. 2020, "Distributionally Robust Neural Networks" (https://github.com/kohpangwei/group_DRO)
2. **CelebA**: Liu et al. 2015, "Deep Learning Face Attributes in the Wild" (http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html)

### Methods
3. **Spearman Rank Correlation**: scipy.stats.spearmanr (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html)
4. **Group DRO**: Sagawa et al. 2020 (baseline comparison method)

### From h-e1 Validation
5. h-e1 validation report (04_validation.md) - confirmed BN/LN gap difference, established training protocol

---

## Phase 3 Handoff

**This experiment brief provides**:
- Concrete dataset specifications (Waterbirds, CelebA)
- Exact training protocol (hyperparameters from h-e1)
- Core mechanism pseudo-code (ranking + correlation)
- Success criteria (ρ > 0.8)
- Reuse strategy (maximize h-e1 code reuse)

**Phase 3 PRD will detail**:
- File structure and module decomposition
- CelebA data loader implementation requirements
- Ranking computation and correlation analysis utilities
- Experiment orchestration scripts
- Testing strategy

**Phase 4 PoC will validate**:
- CelebA data loading correctness
- Ranking computation accuracy
- Correlation calculation (direction-based test: ρ > 0.8 or ρ < 0.6)

**Note**: Full statistical validation deferred to Phase 5 (baseline comparison).
