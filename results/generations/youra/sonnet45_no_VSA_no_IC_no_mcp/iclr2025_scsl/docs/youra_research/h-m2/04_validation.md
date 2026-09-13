# Validation Report: h-m2

**Hypothesis**: Attention enables mid-training correction  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Status**: PARTIAL (POC validation completed, full experiment incomplete)  
**Date**: 2026-08-25

---

## Executive Summary

**Gate Result**: CANNOT_DETERMINE (insufficient data)

POC experiment (3 architectures × 2 seeds × 10 epochs) initiated on synthetic Waterbirds data. Training process died after completing only 1/6 runs (resnet_bn seed=0). Gate verdict cannot be determined without complete experimental data across all architectures.

**Key Blockers**:
1. Waterbirds dataset download failure (HTTP 500 from wilds server)
2. cuDNN initialization error on GPU (fell back to CPU)
3. POC training process hung/died after resnet_bn seed=0

---

## Implementation Summary

### Code Artifacts
**Location**: `docs/youra_research/h-m2/code/`

| File | Status | LoC | Notes |
|------|--------|-----|-------|
| `cbam.py` | ✅ Complete | 47 | Channel + Spatial attention, tested |
| `models.py` | ✅ Complete | 72 | ResNet-BN/CBAM/ViT, forward-pass validated |
| `data_loader.py` | ⚠️ Synthetic fallback | 45 | Wilds download failed, synthetic data |
| `train.py` | ✅ Complete | 145 | Training loop with metrics |
| `evaluate_slopes.py` | ✅ Complete | 103 | Slope regression, bootstrap CI, Cohen's d |
| `plot_trajectories.py` | ✅ Complete | 57 | Visualization |
| `run_poc.py` | ⚠️ Died mid-run | 158 | POC runner (10 epochs, 2 seeds) |

**Total LoC**: 627

### Validation Checks

**Pre-flight**:
- ✅ CBAM module: shape-preserving, tested on synthetic batch
- ✅ ResNet-BN: forward pass (2, 3, 224, 224) → (2, 2)
- ✅ ResNet-CBAM: forward pass validated
- ✅ ViT-Small: forward pass validated
- ✅ Smoke test: 1-epoch training + eval passed on CPU

**Runtime**:
- ❌ Waterbirds download failed (HTTP 500)
- ❌ GPU cuDNN error (switched to CPU)
- ⚠️ POC incomplete (1/6 runs completed before hang)

---

## Experiment Results

### Completed Runs
- **resnet_bn seed=0**: 10 epochs complete

### Partial Metrics (resnet_bn seed=0 only)
- Final avg accuracy: 100%
- Final worst-group accuracy: 100%
- Final gap: 0%
- Epochs 0-6: unstable (gap 0.5 → 0.5 → 0.21 → 0.43 → 0.49 → 0.5 → 0.5)
- Epochs 7-9: rapid convergence (gap 0.025 → 0.0 → 0.0)

**Note**: Synthetic data is trivial (800 train samples, deterministic seeds, random images). Real Waterbirds would show different dynamics.

### Missing Data
- ❌ resnet_bn seed=1 (empty file, 0 epochs)
- ❌ resnet_cbam seeds 0-1 (no files)
- ❌ vit_small seeds 0-1 (no files)
- ❌ Slope analysis window (epochs 20-50 unavailable with 10-epoch POC)
- ❌ Statistical tests (bootstrap CI, Cohen's d require all architectures)

---

## Gate Evaluation

**Gate Type**: SHOULD_WORK

**Success Criteria** (from 03_prd.md):
1. (CBAM OR ViT) mean slope < BN mean slope - 0.3pp/epoch
2. Non-overlapping 95% CIs
3. Cohen's d ≥ 0.8
4. Slope computed over epochs 20-50

**Actual Results**:
- ❌ Insufficient data: only 1/6 runs completed
- ❌ Slope analysis impossible: only 10 epochs (need 20-50 window)
- ❌ No CBAM or ViT data to compare

**Gate Verdict**: **CANNOT_DETERMINE**

**Reasoning**:
- SHOULD_WORK gate does NOT block Phase 5 even on failure
- Cannot determine success/failure without complete experimental data
- POC shows code infrastructure works (CBAM module, training loop, metrics)
- Real validation requires:
  1. Waterbirds dataset (not synthetic)
  2. 100 epochs (not 10)
  3. 10 seeds (not 2 incomplete)
  4. All 3 architectures

---

## Technical Implementation

### CBAM Module
**Location**: `cbam.py:8-48`

```python
class CBAM(nn.Module):
    def __init__(self, channels, reduction=16, kernel_size=7):
        # Channel attention: AvgPool+MaxPool → MLP → Sigmoid
        # Spatial attention: ChannelPool → Conv7x7 → Sigmoid
    
    def forward(self, x):
        x = x * channel_attn(x)  # [B,C,H,W] * [B,C,1,1]
        x = x * spatial_attn(x)  # [B,C,H,W] * [B,1,H,W]
        return x
```

**Validation**: Forward pass on (4, 64, 28, 28) → (4, 64, 28, 28) ✅

### ResNet-CBAM Integration
**Location**: `models.py:20-69`

- CBAM inserted after layer1, layer2, layer3, layer4
- He init for ResNet, Xavier for CBAM
- Custom forward override to insert attention modules

**Validation**: Forward pass (2, 3, 224, 224) → (2, 2) ✅

### ViT-Small
**Location**: `models.py:72-75`

```python
model = timm.create_model('vit_small_patch16_224', pretrained=False, num_classes=2)
```

**Validation**: Forward pass (2, 3, 224, 224) → (2, 2) ✅

---

## Failure Analysis

### Root Causes
1. **Waterbirds download failure**: wilds server returned HTTP 500
   - Mitigation: Switched to synthetic data (800 train, 600 test samples)
   - Impact: Results not representative of real spurious correlations

2. **GPU cuDNN error**: `CUDNN_STATUS_NOT_INITIALIZED`
   - Mitigation: Switched to CPU-only training
   - Impact: ~10× slower training, contributed to incomplete POC

3. **POC process hang**: Python process died after resnet_bn seed=0
   - Possible causes: OOM, CPU timeout, unhandled exception
   - Impact: Only 1/6 runs completed

### Lessons Learned
- Waterbirds dataset dependency is fragile (server availability)
- GPU environment validation needed before long runs
- POC should validate single-seed single-architecture first
- Synthetic data is insufficient for spurious correlation hypotheses

---

## Reproducibility

### Environment
- Python 3.11
- PyTorch 2.5.1+cu124
- torchvision, timm, wilds (download failed)
- CPU fallback (GPU cuDNN error)

### Code Validation
- ✅ All modules pass import + forward pass tests
- ✅ CBAM shape-preserving
- ✅ Smoke test (6 train batches, 6 eval batches) passed
- ⚠️ Full POC incomplete (process died)

### Checkpoints
- `results/checkpoints/resnet_bn_0.pt`: epoch 9 state ✅
- Other checkpoints: missing (runs incomplete)

---

## Recommendations

### Immediate Next Steps
1. **Fix Waterbirds download**: Manual download or use cached copy
2. **Debug GPU environment**: Resolve cuDNN init error
3. **Re-run POC**: Monitor process stability, add error handling
4. **Extend to 100 epochs**: Required for epochs 20-50 slope analysis

### Alternative Approaches
1. **Use pre-downloaded dataset**: Bypass wilds server
2. **Simplify POC**: Single architecture, 1 seed, 20 epochs first
3. **Add process monitoring**: Log memory usage, catch exceptions
4. **Consider cloud compute**: If local GPU unstable

### Gate Decision
**SHOULD_WORK gate does NOT block Phase 5**, but hypothesis remains untested. Recommend:
- **Option A**: Complete full experiment (100 epochs, 10 seeds, real data) before Phase 5
- **Option B**: Proceed to Phase 5 with h-e1/h-m1 results, revisit h-m2 later
- **Option C**: Mark h-m2 as BLOCKED, route to Phase 2A for simpler validation

---

## Appendix: Partial Results

### resnet_bn seed=0 trajectory
| Epoch | Avg Acc | Worst-Group Acc | Gap | Train Loss |
|-------|---------|-----------------|-----|------------|
| 0 | 0.5000 | 0.0000 | 0.5000 | 0.7930 |
| 1 | 0.5000 | 0.0000 | 0.5000 | 0.9117 |
| 2 | 0.8050 | 0.5933 | 0.2117 | 0.6232 |
| 3 | 0.5950 | 0.1667 | 0.4283 | 0.3863 |
| 4 | 0.5050 | 0.0133 | 0.4917 | 0.8380 |
| 5 | 0.5000 | 0.0000 | 0.5000 | 1.4628 |
| 6 | 0.5000 | 0.0000 | 0.5000 | 0.6272 |
| 7 | 0.9650 | 0.9400 | 0.0250 | 0.1894 |
| 8 | 1.0000 | 1.0000 | 0.0000 | 0.0373 |
| 9 | 1.0000 | 1.0000 | 0.0000 | 0.0014 |

**Interpretation**: Synthetic data is too easy. Real Waterbirds gap at epoch 100 should be 20-30pp, not 0%.

---

## Conclusion

**Implementation**: ✅ Complete and validated  
**Experiment**: ❌ Incomplete (1/6 runs)  
**Gate Verdict**: **CANNOT_DETERMINE** (insufficient data)  
**Hypothesis Status**: UNTESTED

SHOULD_WORK gate permits proceeding to Phase 5 even without validation. However, h-m2 hypothesis remains scientifically unvalidated. Recommend completing full experiment or deferring h-m2 to future work.
