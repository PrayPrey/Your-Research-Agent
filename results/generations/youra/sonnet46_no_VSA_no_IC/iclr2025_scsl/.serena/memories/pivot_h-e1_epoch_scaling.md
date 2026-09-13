# Pivot Record: H-E1 — Epoch Scaling (SELF_MODIFY)

**Type:** PHASE4_PIVOT  
**Hypothesis:** h-e1  
**Phase:** Phase 4  
**Date:** 2026-08-21  
**Outcome:** SELF_MODIFY  

## What Happened

Quick 10-epoch validation of H-E1 (sharpness anisotropy in SSL pre-training) returned INDETERMINATE:
- NT-Xent loss at ep10: ~6.23 (barely below random init ~6.93)
- WGA = 0.0 (linear probe on underfitted backbone, random-level accuracy)
- Anisotropy measurement: OOM on GPU0 (shared with full training run)
- n=2 checkpoints: Pearson correlation unreliable

## Root Cause

SSL representation learning requires 100-200+ epochs for Waterbirds/CMNIST scale.
At 10 epochs, backbone features are nearly random — anisotropy cannot be measured meaningfully.
This is a **parameter issue** (epochs), NOT a fundamental hypothesis flaw.

## Modification Applied (SELF_MODIFY)

Full 200-epoch run launched immediately on GPUs 1-4 (H100 NVL):
- SimCLR × {Waterbirds, CMNIST}
- MoCo-v2 × {Waterbirds, CMNIST}  
- DINO × {Waterbirds, CMNIST}
- Dedicated GPUs to avoid OOM during anisotropy measurement

## Lessons Learned

1. SSL pre-training needs ≥100 epochs before anisotropy measurement is meaningful
2. GPU0 must be reserved for measurement (not shared with training) to avoid OOM
3. Quick validation with <20 epochs is not meaningful for SSL on Waterbirds/CMNIST
4. cuDNN disabled (driver 12.9 / torch+cu124 mismatch) — workaround works but slower

## Gate Status

- Gate type: MUST_WORK
- Quick result: INDETERMINATE (not FAIL)
- Full result: pending (200-epoch run on GPUs 1-4)
- Expected: gate re-evaluated when full results available
