# Validation Report: H-M2

**Hypothesis:** Update-norm parity intervention attenuates SR divergence (SR ≤ 1.1 vs baseline SR > 1.2)
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-09

## Implementation Status

| Component | Status |
|-----------|--------|
| config.py | COMPLETE |
| data.py | COMPLETE |
| model.py | COMPLETE |
| parity.py | COMPLETE |
| sharpness.py | COMPLETE |
| metrics.py | COMPLETE |
| stats.py | COMPLETE |
| train.py | COMPLETE |
| main.py | COMPLETE |
| visualize.py | COMPLETE |

**Total Files:** 10
**Code Lines:** ~600

## Code Validation

### Module Tests: PASS
```
All imports OK
Model created: 23512130 params
Train samples: 4795
Val samples: 1199
Group norms: {0: 9.63, 1: 5.27, 2: 8.32, 3: 6.19}
Loss: 0.6569
Parity log: {'group': 0, 'orig_norm': 9.63, 'scaled_norm': 7.35, 'target_norm': 7.35}
```

### Key Validation Points
1. Data loading works (Waterbirds dataset, 4 groups)
2. Model creation works (ResNet-50 pretrained + 2-class FC)
3. Per-group gradient norm computation works
4. Parity scaling correctly interpolates toward mean norm
5. Training loop structure validated

## Experiment Execution Status

**Status:** NOT COMPLETED
**Reason:** CPU-only execution (no GPU available)
**CPU Epoch Time:** ~15-20 min (ResNet-50 double precision)

### Attempted Configurations
| Config | Epochs | Variants | Seeds | Status |
|--------|--------|----------|-------|--------|
| Full | 100 | 3 | 5 | Timeout |
| Reduced | 30 | 3 | 3 | Timeout |
| Minimal | 5 | 2 | 1 | Timeout |
| Micro | 2 | 2 | 1 | Timeout (40 min) |

## Gate Evaluation

**Gate Type:** SHOULD_WORK
**Result:** INCONCLUSIVE

### Rationale
- Code implementation is complete and validated
- Core mechanism (parity scaling) works correctly in unit tests
- Full experiment execution blocked by hardware constraints (CPU-only)
- Per SHOULD_WORK semantics: experiment completion required for verdict

### Next Steps
1. Run experiment on GPU-enabled machine
2. Expected GPU runtime: ~30 min for 2 variants × 3 seeds × 30 epochs
3. Success criteria: parity SR ≤ 1.1 vs baseline SR > 1.2

## Findings

### Code Implementation Verified
- UpdateNormParityTrainer correctly computes per-group gradient norms
- Parity scaling correctly moves gradient norm toward group mean
- Training loop properly integrates parity intervention between backward() and step()

### Preliminary Observations (from unit test)
- Group gradient norms vary significantly: 5.27 to 9.63
- Parity scaling reduces this variance (target norm = 7.35)
- Mechanism is functioning as designed

## Files Generated
- h-m2/code/config.py
- h-m2/code/data.py
- h-m2/code/model.py
- h-m2/code/parity.py
- h-m2/code/sharpness.py
- h-m2/code/metrics.py
- h-m2/code/stats.py
- h-m2/code/train.py
- h-m2/code/main.py
- h-m2/code/visualize.py
- h-m2/04_validation.md (this file)

## Summary

H-M2 implementation complete. Experiment execution blocked by CPU-only environment. Gate verdict: INCONCLUSIVE pending GPU execution.
