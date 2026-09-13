# Phase 4 Validation Report: H-M1

**Generated:** 2026-08-04T05:52:00+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5
**Hypothesis Type:** MECHANISM (Continuation of H-E3)

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | H-M1 |
| **Type** | MECHANISM |
| **Gate** | MUST_WORK |
| **Prerequisites** | H-E3 (VALIDATED, PASS) |
| **Statement** | Under ERM training on Waterbirds, ERM Phase I spurious feature exploitation creates differential confidence trajectories: p_minority(t*)∈[0.3,0.7] (boundary condition) and p_majority(t*)>0.80 (saturation) in ≥4/5 seeds |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 17 |
| Completed | 17 |
| Coder-Validator Cycles | 1 |
| Hypothesis Type | INCREMENTAL (extends H-E3) |
| Code Copied From Base | No (direct import from H-E3 code path) |

### Generated Files

| File | Description |
|------|-------------|
| `code/config.py` | H-M1 config with H-E3 path injection, gate constants, viz constants |
| `code/compute_confidence.py` | Core: extract_confidence_by_group, compute_trajectory, verify_mechanism_activated, save_results |
| `code/visualize.py` | 4 required figures (gate_metrics, trajectory, distribution, boundary_fraction) |
| `code/run_experiment.py` | Main orchestrator + smoke_test() |
| `code/tests/test_compute_confidence.py` | 3 spec compliance tests (all passed) |
| `results/confidence_results.json` | Full results (5 seeds × 6 epochs) |
| `figures/fig_gate_metrics.png` | Gate metrics comparison (MANDATORY) |
| `figures/fig_confidence_trajectory.png` | Confidence trajectories per seed |
| `figures/fig_conf_distribution.png` | Per-sample confidence distribution at t* |
| `figures/fig_boundary_fraction.png` | Fraction of minority in gate band per epoch |

---

## Code Quality Checklist

- [✓] Syntax validation passed (all files parse correctly)
- [✓] API signatures match 03_logic.md exactly
- [✓] Smoke test passed (SMOKE OK: p_min=0.8271 p_maj=0.9724)
- [✓] Unit tests passed (3/3)
- [✓] Full experiment ran without errors
- [✓] Results serialized to JSON (C-8-2 schema)
- [✓] All 4 required figures generated

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | Waterbirds v1.0 (train split, 4795 samples) |
| Minority | G1 (landbird/water) + G2 (waterbird/land) = 240 samples |
| Majority | G0 (landbird/land) + G3 (waterbird/water) = 4555 samples |
| Checkpoints | H-E3 results/checkpoints/ (30 files: 5 seeds × 6 epochs) |
| Checkpoint epochs | {0, 1, 5, 10, 20, 50} |
| Seeds | {1, 2, 3, 4, 5} |
| t* per seed | {1:20, 2:50, 3:50, 4:20, 5:5} (from H-E3 04_validation.md) |
| Model | ResNet-50 (H-E3 trained weights, eval mode) |
| Batch size | 256 (forward pass only) |
| Device | CUDA (NVIDIA H100) |
| Runtime | ~15 minutes |

---

## Experiment Results

### Per-Seed Results at t*

| Seed | t* | p_minority(t*) | p_majority(t*) | Gap | Boundary [0.3,0.7]? | Maj Saturated >0.80? | Both Pass? |
|------|----|----------------|----------------|-----|----------------------|----------------------|------------|
| 1 | 20 | 0.9956 | 0.9994 | 0.0039 | ✗ | ✓ | ✗ |
| 2 | 50 | 0.9999 | 0.9999 | 0.0000 | ✗ | ✓ | ✗ |
| 3 | 50 | 0.9998 | 0.9999 | 0.0000 | ✗ | ✓ | ✗ |
| 4 | 20 | 0.9964 | 0.9992 | 0.0029 | ✗ | ✓ | ✗ |
| 5 | 5  | 0.9678 | 0.9925 | 0.0247 | ✗ | ✓ | ✗ |

### Summary

| Metric | Value |
|--------|-------|
| Mean p_minority(t*) | 0.9919 |
| Mean p_majority(t*) | 0.9982 |
| Gate pass count | 0/5 |
| Mechanism active | False |

### Full Trajectory (Seed 1)

| Epoch | p_minority | p_majority |
|-------|-----------|-----------|
| 0 | 0.5210 | 0.4913 |
| 1 | 0.8271 | 0.9724 |
| 5 | 0.8975 | 0.9858 |
| 10 | 0.9637 | 0.9956 |
| 20 | 0.9956 | 0.9994 |
| 50 | 0.9996 | 0.9999 |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Primary Criterion** | p_minority(t*) ∈ [0.3, 0.7] in ≥4/5 seeds |
| **Result** | FAIL |
| **Satisfied** | False |
| **Seeds Passing Primary** | 0/5 |

### Failure Analysis

The primary gate criterion failed in all 5 seeds. The empirical finding is:

- **At epoch 0:** p_minority ≈ 0.45–0.57 (near-random, consistent with untrained model)
- **At epoch 1:** p_minority already rises to 0.57–0.83, p_majority to 0.97 (strong differential at early training)
- **At t*:** p_minority ≈ 0.97–0.9999 (fully saturated, not at boundary)

**Root cause:** ERM training on Waterbirds trains to minimize cross-entropy on all training samples including minority. By t* (epochs 5–50), the model has memorized or correctly classified minority training samples with high confidence. The minority samples do NOT remain at the decision boundary on the training set — ERM drives them to high confidence predictions.

**Key insight:** The differential confidence proposed by the hypothesis (H-Phase I theory: minority stays near boundary while majority saturates) does NOT appear in training-set confidence. There IS a differential trajectory: majority saturates faster (by epoch 1, p_maj ≈ 0.97 vs p_min ≈ 0.72 for seed 1), but both groups converge to near-1.0 confidence by t*.

**Nuance:** The early trajectory (t=0→1) shows exactly the predicted differential: majority confidence jumps dramatically while minority rises more slowly. At epoch 1, seed 1: p_min=0.827 vs p_maj=0.972. This is consistent with Phase I dynamics — but the gate criterion requires the differential to persist to t*, which it does not.

---

## Next Steps

**Gate: FAIL (MUST_WORK)** → Route to Phase 0 for hypothesis redesign.

### Failure Response Options

Per PRD Section 8: "IF p_minority(t*) < 0.3 in ≥2/5 seeds → FAIL: ABANDON, route to Phase 0"

In this case p_minority(t*) > 0.7 (not < 0.3) — minority is overly confident, not boundary-straddling. The failure mode is the **opposite** of the guard condition but still a gate failure. The mechanistic basis for H-E3's trace asymmetry needs re-examination.

### Recommended Phase 0 Revision

Consider evaluating confidence on the **validation set** or **out-of-distribution test set** rather than the training set. The differential confidence may manifest at test time (where minority samples encounter distribution shift) rather than at training time (where ERM has optimized for correct classification of all training samples).

---

## Phase 2C Handoff

### Proven Components

| Component | File | Status |
|-----------|------|--------|
| extract_confidence_by_group | compute_confidence.py | ✓ Functional |
| compute_trajectory | compute_confidence.py | ✓ Functional |
| check_gate / verify_mechanism_activated | compute_confidence.py | ✓ Functional |
| save_results (JSON C-8-2) | compute_confidence.py | ✓ Functional |
| 4 figure types | visualize.py | ✓ Generated |

### Optimal Hyperparameters

```yaml
batch_size: 256  # eval-only, fits well on H100
device: cuda
checkpoint_epochs: [0, 1, 5, 10, 20, 50]
tstar_per_seed: {1: 20, 2: 50, 3: 50, 4: 20, 5: 5}
```

### Lessons Learned

**What Worked:**
- Reusing H-E3 checkpoints and code (no redundant training needed)
- Forward-pass-only confidence extraction is fast (~1 min/seed)
- CUDA_VISIBLE_DEVICES=0 required for H100 GPU access in this environment
- Smoke test (single seed/epoch) validates pipeline in <30s before full run

**What Didn't Work:**
- H-M1 gate criterion p_minority(t*) ∈ [0.3, 0.7] — empirically, minority training confidence saturates to ~0.99 by t*
- The proposed Phase I differential mechanism (LaBonte & Muthukumar 2026 Theorem 3.2) may apply to test-set or held-out minority, not training-set minority

**Unexpected Finding:**
- At epoch 1, there IS a strong differential: p_maj rises dramatically (to 0.97) while p_min rises more slowly (to 0.72–0.83). This early-epoch differential is exactly what the theory predicts, but it does not persist.
- The early differential at epoch 1 suggests the mechanism exists transiently, but t* is too late (by which point ERM has saturated minority too).

**Key Insight:**
The differential confidence trajectory exists at early training (epoch 1) but not at t* (which is chosen to maximize Hessian trace AUROC, not confidence differential). The hypothesis needs to test at early epochs or on held-out data.

### Recommendations for Dependent Hypotheses

H-M2, H-M3, H-M4 should note:
- Training-set confidence does not maintain the predicted boundary condition at t*
- Test-set or val-set confidence may show the predicted differential (distribution shift effect)
- Consider using epoch 1 as the relevant checkpoint for mechanism verification (strong differential observable)
- The Hessian trace asymmetry in H-E3 is real, but its mechanistic explanation via training-set confidence differential needs revision

---

## Appendix

### Files Generated

```
docs/youra_research/h-m1/
├── code/
│   ├── config.py
│   ├── compute_confidence.py
│   ├── visualize.py
│   ├── run_experiment.py
│   ├── experiment.log
│   ├── tests/
│   │   └── test_compute_confidence.py
│   └── outputs/
├── results/
│   └── confidence_results.json
└── figures/
    ├── fig_gate_metrics.png
    ├── fig_confidence_trajectory.png
    ├── fig_conf_distribution.png
    └── fig_boundary_fraction.png
```

### Experiment Log Summary

```
Dataset: 4795 samples, minority=240
Device: cuda
--- Seed 1 --- t*=20  p_min=0.9956  p_maj=0.9994  gap=0.0039
--- Seed 2 --- t*=50  p_min=0.9999  p_maj=0.9999  gap=0.0000
--- Seed 3 --- t*=50  p_min=0.9998  p_maj=0.9999  gap=0.0000
--- Seed 4 --- t*=20  p_min=0.9964  p_maj=0.9992  gap=0.0029
--- Seed 5 --- t*=5   p_min=0.9678  p_maj=0.9925  gap=0.0247
Gate pass count: 0/5
Mechanism active: False
Gate: FAIL (0/5 seeds)
```
