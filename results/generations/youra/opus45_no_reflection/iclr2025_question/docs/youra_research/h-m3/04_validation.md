# Phase 4 Validation Report: H-M3

**Generated:** 2026-08-18T17:55:29+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-m3 |
| **Statement** | Linear probe learns hidden state to correctness mapping with AUROC >= 0.70 |
| **Type** | MECHANISM |
| **Phase 4 Start** | 2026-08-18T17:53:00+00:00 |
| **Phase 4 End** | 2026-08-18T17:55:29+00:00 |
| **Duration** | ~2.5 minutes |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 12 |
| Completed | 12 |
| Failed | 0 |
| Skipped | 0 |
| Coder-Validator Cycles | 1/5 |

### Generated Files

| File | Description |
|------|-------------|
| config.py | HM3Config dataclass with all hyperparameters |
| data.py | Load hidden states from H-M1 cache, scale features |
| probe.py | LinearCorrectnessProbe, RandomBaseline, MLPFallbackProbe |
| evaluate.py | Metrics computation, mechanism verification, baseline comparison |
| visualize.py | Gate comparison bar chart, ROC curve plotting |
| train.py | Main orchestration script |

### Code Quality

- [x] Syntax validation passed
- [x] sklearn LogisticRegression with L-BFGS solver
- [x] StandardScaler normalization
- [x] 5-seed random baseline CI
- [x] Mechanism verification (weight norm, pred std, AUROC floor)

---

## Experiment Results

### Execution Details

| Field | Value |
|-------|-------|
| **Mode** | CPU (sklearn LogisticRegression) |
| **Status** | COMPLETED |
| **Data Source** | H-M1 hidden states cache (L19, 60% depth) |
| **Train Samples** | 9,500 |
| **Val Samples** | 1,700 |
| **Seed** | 42 |

### Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **AUROC** | 0.8851 | >= 0.70 | **PASS** |
| **Accuracy** | 79.41% | - | - |
| **Baseline AUROC** | 0.4715 ± 0.059 | ~0.50 | - |
| **Delta vs Baseline** | +0.4136 | > 0.20 | **PASS** |
| **Probe Iterations** | 60 | < 2000 | Converged |
| **Weight Norm** | 0.8425 | > 1e-6 | **PASS** |
| **Prediction Std** | 0.3277 | > 0.01 | **PASS** |

### Key Finding

**Linear probe achieves 0.885 AUROC** — substantially exceeding the 0.70 gate threshold and matching H-E1's direct correctness probe baseline (0.8854). This confirms that correctness signal in hidden states is **linearly separable** with a simple logistic regression classifier.

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | SHOULD_WORK |
| **Result** | **PASS** |
| **Satisfied** | true |
| **Evaluated At** | 2026-08-18T17:55:29+00:00 |

### Criteria Evaluation

| Criterion | Target | Actual | Result |
|-----------|--------|--------|--------|
| AUROC | >= 0.70 | 0.8851 | **PASS** |
| AUROC vs Random | > +0.20 | +0.4136 | **PASS** |
| Probe Convergence | < max_iter | 60 iters | **PASS** |
| Mechanism Verification | All checks | All pass | **PASS** |

### Fallback Status

MLP fallback was NOT triggered (linear AUROC 0.885 > 0.70 threshold).

---

## Figures Generated

1. `figures/gate_comparison.png` - Bar chart: achieved AUROC (0.885) vs threshold (0.70)
2. `figures/roc_curve.png` - ROC curve with AUC=0.885 annotation

---

## Phase 2C Handoff Data

### Proven Components

- **LinearCorrectnessProbe**: sklearn LogisticRegression with C=1e-3, class_weight='balanced'
- **StandardScaler**: Mean=0, Std=1 normalization essential for L-BFGS convergence
- **5-seed Baseline CI**: Random direction baseline confirms 0.47 AUROC floor

### Hyperparameters Confirmed

| Param | Value | Effect |
|-------|-------|--------|
| C | 1e-3 | Strong L2 regularization, prevents overfitting |
| max_iter | 2000 | Convergence at 60 iterations (well under limit) |
| class_weight | balanced | Handles potential class imbalance |
| solver | lbfgs | Fast convergence for high-dimensional sparse problems |

### Lessons Learned

1. Linear probe matches prior work (SEP, concept-probes) at ~0.88 AUROC
2. Hidden states from L19 (60% depth) produce results consistent with L15 (50%) from H-M2
3. Training completes in ~2 seconds on CPU — no GPU required for probe fitting

---

## Next Steps

### Ready for Phase 5

All validation criteria met. Linear probe mechanism is confirmed working.

1. **H-M4**: Compare probe to output-level baselines (token entropy, sequence prob)
2. **Phase 5**: Baseline comparison with established methods
3. **Integration**: Use LinearCorrectnessProbe in production pipeline

**Proceed to:** Next hypothesis in execution order (H-M4)

---

## Appendix: Raw Results

```json
{
  "hypothesis_id": "h-m3",
  "timestamp": "2026-08-18T17:55:29.046506",
  "data": {
    "train_size": 9500,
    "val_size": 1700,
    "layer": "l19",
    "source": "h-m1 cache"
  },
  "probe": {
    "auroc": 0.8851,
    "accuracy": 0.7941,
    "n_iter": 60,
    "converged": true
  },
  "baseline": {
    "mean": 0.4715,
    "std": 0.0593
  },
  "mechanism": {
    "weight_norm": 0.8425,
    "pred_std": 0.3277,
    "all_pass": true
  },
  "gate": {
    "type": "SHOULD_WORK",
    "threshold": 0.70,
    "achieved": 0.8851,
    "satisfied": true,
    "result": "PASS"
  }
}
```
