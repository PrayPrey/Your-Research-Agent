# Phase 4 Validation Report: h-m2

**Hypothesis:** CNNs show larger temporal gaps than Vision Transformers (Δ_ResNet > Δ_ViT by ≥2 epochs) due to architectural inductive bias differences

**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-29  
**Status:** LIMITATION_RECORDED

---

## Executive Summary

**Result:** Gate FAIL (limitation recorded, pipeline continues)

The architectural comparison between ResNet-50 and ViT-B/16 on CMNIST showed **opposite effect** from hypothesis prediction:
- ResNet-50: Δ = 0 epochs (no temporal gap)
- ViT-B/16: Δ = 1 epoch (small temporal gap)
- Difference: Δ_ResNet - Δ_ViT = -1 epochs (opposite direction)

**Gate Threshold:** Δ_ResNet - Δ_ViT ≥ 2 epochs → **NOT MET**

**Limitation Severity:** Low (SHOULD_WORK gate → does not block Phase 5)

**Root Cause:** Convergence too fast (1-2 epochs) at 70% accuracy threshold, insufficient to distinguish architectural temporal dynamics.

---

## Experimental Setup

### Dataset
- **Primary:** CMNIST (Colored MNIST, 10% subset)
- **Reason:** Waterbirds download failed (HTTP 500 error), fallback per PRD risk mitigation
- **Size:** ~6,000 training samples (10% of 60K)
- **Spurious correlation:** 75% (color-label alignment)

### Models
- **ResNet-50:** timm `resnet50` (25.6M params, from scratch)
- **ViT-B/16:** timm `vit_base_patch16_224` (86M params, from scratch)

### Training Configuration
| Parameter | ResNet-50 | ViT-B/16 |
|-----------|-----------|----------|
| Learning rate | 0.001 | 0.0003 |
| Batch size | 256 | 512 |
| Weight decay | 1e-4 | 0.05 |
| Optimizer | SGD (momentum 0.9) | SGD (momentum 0.9) |
| Scheduler | Cosine (T_max=30) | Cosine (T_max=30) |
| Epochs | 30 | 30 |
| Seed | 42 | 42 |

### Convergence Criterion
- **Threshold:** 70% accuracy (lowered from 90% due to CMNIST spurious correlation strength)
- **Detection:** First epoch reaching threshold
- **Tracking:** Separate for spurious-only and core-only variants

### Feature Masking
- **Spurious-only:** Gaussian blur (kernel=31) → removes digit shape, keeps color channel
- **Core-only:** Grayscale conversion → removes color, keeps digit shape

---

## Primary Gate Results

### ResNet-50
| Variant | Convergence Epoch | Accuracy |
|---------|-------------------|----------|
| Spurious-only | 1 | 74.35% |
| Core-only | 1 | 74.18% |
| **Temporal Gap (Δ)** | **0** | - |

### ViT-B/16
| Variant | Convergence Epoch | Accuracy |
|---------|-------------------|----------|
| Spurious-only | 1 | 74.88% |
| Core-only | 2 | 71.95% |
| **Temporal Gap (Δ)** | **1** | - |

### Gate Evaluation
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Δ_ResNet - Δ_ViT | ≥ 2 epochs | -1 epochs | ✗ FAIL |
| Direction | ResNet > ViT | ViT > ResNet | ✗ OPPOSITE |
| Statistical significance | p < 0.05 | N/A (1 seed only) | ✗ NOT TESTED |

**Gate Result:** FAIL  
**Consequence:** Limitation recorded, hypothesis proceeds to Phase 5 (SHOULD_WORK gate does not block)

---

## Analysis

### Why the Gate Failed

1. **Convergence too fast:** Both architectures reached 70% threshold in 1-2 epochs
   - Insufficient temporal separation to measure meaningful gaps
   - Color cue dominates both architectures equally in early training

2. **Opposite direction:** ViT showed Δ=1 while ResNet showed Δ=0
   - Hypothesis predicted ResNet would have larger gap
   - Suggests ViT slightly more sensitive to shape (grayscale) than ResNet at this threshold

3. **Threshold too low:** 70% accuracy easily achieved by both architectures
   - Original 90% threshold more appropriate for distinguishing temporal dynamics
   - Lowered to accommodate CMNIST spurious correlation (75%), but overcorrected

### Technical Issues

1. **Dataset fallback:** Waterbirds (primary) unavailable → CMNIST used instead
   - CMNIST has weaker spurious correlation (75% vs 95% in Waterbirds)
   - Simpler task may not reveal architectural differences

2. **Masking strategy:**
   - Gaussian blur (spurious-only) may not fully remove shape information
   - Grayscale (core-only) removes all color but may be insufficient for ViT patch embeddings

3. **Single seed:** PoC validation (seed 42 only), no statistical testing
   - Cannot assess variance or significance
   - Full 10-seed validation not run due to fast convergence

---

## Lessons Learned

### What Worked
- Fast iteration with CMNIST fallback after Waterbirds failure
- Architecture-specific hyperparameters correctly configured
- Convergence detection functional (accuracy-based)

### What Didn't Work
- 70% accuracy threshold too low for temporal gap measurement
- Feature masking (blur/grayscale) insufficient to create temporal separation
- CMNIST task difficulty not suitable for architectural comparison

### What to Try Next (if retrying)
1. **Raise threshold to 85-90%** to force longer training and capture temporal dynamics
2. **Use harder datasets** (Waterbirds with manual download, or CelebA)
3. **Improve masking:**
   - Spurious-only: Stronger blur or noise injection
   - Core-only: More sophisticated shape preservation (edge detection instead of grayscale)
4. **Extend training to 100 epochs** to capture full convergence trajectory
5. **Run multi-seed validation** to assess variance and statistical significance

---

## Deliverables

### Code
- ✓ `h-m2/code/data.py` — CMNIST loader with spurious correlation
- ✓ `h-m2/code/model.py` — ResNet-50/ViT-B/16 factory + AblationTrainer
- ✓ `h-m2/code/train.py` — Multi-architecture training orchestration
- ✓ `h-m2/code/evaluate.py` — Statistical comparison (unused due to single seed)
- ✓ `h-m2/code/main.py` — Experiment runner (PoC + full)
- ✓ `h-m2/code/config.py` — Architecture-specific hyperparameters

### Results
- ✓ `h-m2/results/full_results.json` — ResNet-50 and ViT-B/16 convergence data
- ✓ `h-m2/04_validation.md` — This report
- ✓ `.serena/limitation_h-m2_run1.md` — Limitation record for cross-phase reference

### Figures
- ✗ No figures generated (convergence too fast for meaningful plots)

---

## Next Steps

### Phase 5 Continuation
- Hypothesis proceeds to Phase 5 baseline comparison with **limitation noted**
- Phase 5 gate (DETERMINES_SUCCESS) will evaluate overall approach validity
- If Phase 5 PARTIAL → limitation informs Phase 0 brainstorming

### Recommendations for Future Work
1. **Dataset:** Use Waterbirds or CelebA with manual download/setup
2. **Threshold:** 85-90% accuracy for meaningful temporal separation
3. **Masking:** Investigate alternative ablation strategies (gradient-based attribution, targeted masking)
4. **Training duration:** 100+ epochs to capture full convergence trajectory
5. **Statistical validation:** 10-seed runs with t-test for significance

---

## Appendix: Raw Results

### ResNet-50 Training Log (Spurious-only)
```
Epoch 01: loss=0.5872, acc=0.7435
Converged at epoch 1 (accuracy=0.7435)
```

### ResNet-50 Training Log (Core-only)
```
Epoch 01: loss=0.6144, acc=0.7418
Converged at epoch 1 (accuracy=0.7418)
```

### ViT-B/16 Training Log (Spurious-only)
```
Epoch 01: loss=0.5951, acc=0.7488
Converged at epoch 1 (accuracy=0.7488)
```

### ViT-B/16 Training Log (Core-only)
```
Epoch 01: loss=0.6629, acc=0.6985
Epoch 02: loss=0.5889, acc=0.7195
Converged at epoch 2 (accuracy=0.7195)
```

### Full Results JSON
```json
{
  "gate_status": "FAIL",
  "resnet50": {
    "arch_name": "resnet50",
    "seed": 42,
    "E_spurious": 1,
    "E_core": 1,
    "delta": 0
  },
  "vit_b16": {
    "arch_name": "vit_b16",
    "seed": 42,
    "E_spurious": 1,
    "E_core": 2,
    "delta": 1
  },
  "comparison": {
    "delta_resnet": 0,
    "delta_vit": 1,
    "diff": -1
  }
}
```

---

**Validation Complete:** 2026-08-29  
**Status:** LIMITATION_RECORDED (SHOULD_WORK gate FAIL)  
**Serena Memory:** `limitation_h-m2_run1.md` written  
**Next Phase:** Phase 5 (baseline comparison)
