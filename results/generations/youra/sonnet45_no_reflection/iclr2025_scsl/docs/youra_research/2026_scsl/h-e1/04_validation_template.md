# Phase 4 Validation Report: h-e1
# Jacobian Stable Rank Regularization - EXISTENCE PoC

**Hypothesis ID:** h-e1  
**Date:** 2026-05-12  
**Gate Type:** MUST_WORK  
**Status:** IN_PROGRESS

---

## Executive Summary

**Hypothesis Statement:**  
Under pretraining with explicit residual-corrected Jacobian stable rank (sr_ℓ^res) regularization, if models are trained to minimize sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2 per layer, then mean stable rank reduces by ≥20% relative to baseline while maintaining iso-perplexity (≤1% deviation).

**Implementation Approach:**  
- PoC validation with 5000 training steps (~320M tokens)
- Baseline vs Regularized GPT-2 comparison
- Residual-corrected Jacobian stable rank regularization
- Adaptive lambda tuning for iso-perplexity

**Gate Result:** [PENDING]

---

## Implementation Summary

### Code Structure

```
h-e1/code/
├── config.py          # Configuration dataclasses
├── data.py            # C4 streaming dataset
├── model.py           # Baseline + Regularized GPT-2
├── train.py           # Training loop with adaptive lambda
├── evaluate.py        # Metrics evaluator
├── visualize.py       # Figure generation
├── run_experiment.py  # PoC experiment runner
└── requirements.txt   # Dependencies
```

### Key Components Implemented

1. **Stable Rank Regularizer** (model.py)
   - Hutchinson trace estimator for Frobenius norm (10 probes)
   - Power iteration for spectral norm (5 iterations)
   - Residual correction: J̃_ℓ = J_ℓ - I
   - Stable rank: sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2

2. **Adaptive Lambda Tuning** (train.py)
   - Monitors perplexity deviation from baseline
   - Adjusts regularization strength dynamically
   - Target: maintain perplexity within ±1%

3. **Data Pipeline** (data.py)
   - C4 streaming dataset (HuggingFace)
   - GPT-2 tokenization (seq_length=512)
   - Batch size 32 with gradient accumulation

4. **Evaluation Metrics** (evaluate.py)
   - Perplexity on C4 validation set
   - Per-layer stable rank measurement
   - Layer-wise variance (CV)
   - Measurement precision (CV)

### Test Coverage

- **test_data.py:** Data loading and tokenization
- **test_model.py:** Model initialization and forward pass
- **test_config.py:** Configuration dataclasses
- **test_evaluate.py:** Metrics computation
- **test_visualize.py:** Figure generation

All tests validate core functionality without requiring full training.

---

## Experimental Results

### Training Configuration

| Parameter | Baseline | Proposed |
|-----------|----------|----------|
| Model | GPT-2 125M | GPT-2 125M + Regularization |
| Training Steps | 5000 | 5000 |
| Total Tokens | ~320M | ~320M |
| Batch Size | 32 (effective 128) | 32 (effective 128) |
| Learning Rate | 3e-4 | 3e-4 |
| Lambda Init | 0.0 | 0.01 (adaptive) |
| Seed | 42 | 42 |

### Gate Metrics

[TO BE FILLED AFTER EXPERIMENT COMPLETION]

| Metric | Target | Baseline | Proposed | Pass/Fail |
|--------|--------|----------|----------|-----------|
| Mean Stable Rank Reduction | ≥20% | [TBD] | [TBD] | [TBD] |
| Perplexity Deviation | ≤1% | [TBD] | [TBD] | [TBD] |
| Layer Variance (CV) | <2.0× | N/A | [TBD] | [TBD] |
| Measurement CV | <15% | N/A | [TBD] | [TBD] |

### Detailed Results

**Baseline Model:**
- Final Perplexity: [TBD]
- Mean Stable Rank: [TBD]
- Training Converged: [TBD]

**Proposed Model:**
- Final Perplexity: [TBD]
- Mean Stable Rank: [TBD]
- Lambda Evolution: [TBD]
- Training Converged: [TBD]

---

## Gate Validation

**Gate Type:** MUST_WORK

**Criteria:**
1. ✓/✗ Mean sr_ℓ^res reduction ≥20% vs baseline
2. ✓/✗ Perplexity deviation ≤1% from baseline
3. ✓/✗ Layer variance <2× mean stable rank
4. ✓/✗ Measurement CV <15%

**Gate Decision:** [PENDING]

**Rationale:** [TO BE FILLED]

---

## Visualizations

Generated figures saved to `h-e1/figures/`:

1. **gate_metrics.png** - Gate criteria comparison (mandatory)
2. **layer_evolution.png** - Training loss trajectory
3. **stable_rank_distribution.png** - Per-layer stable rank
4. **perplexity_trajectory.png** - Perplexity vs baseline
5. **measurement_precision.png** - Measurement CV over time

---

## Issues and Observations

### Implementation Challenges

1. **Memory Management:**
   - Regularization computation requires storing layer I/O
   - Forward hooks used to capture intermediate activations
   - Gradients retained for autograd-based Jacobian computation

2. **Numerical Stability:**
   - Epsilon guards (1e-12) prevent division by zero
   - Gradient clipping (norm=1.0) prevents instability
   - Residual correction handles near-identity Jacobians

3. **Computational Cost:**
   - Stable rank evaluation is expensive (Hutchinson + power iteration)
   - Measured every 1000 steps to balance cost and monitoring
   - PoC uses 5000 steps for validation (~1% of full 10B tokens)

### PoC Limitations

- **Reduced Training:** 320M tokens vs 10B tokens (full experiment)
- **Single Seed:** No multi-seed validation in PoC
- **No Ablations:** Minimal hyperparameter tuning
- **Domain Robustness:** Not tested (C4 only)

---

## Recommendations

### If Gate PASSES:

1. **Proceed to Phase 5:** Baseline comparison with standard methods
2. **Full Training:** Run with 10B tokens for final validation
3. **Multi-Seed:** Validate with 3+ random seeds
4. **Ablation Study:** Test different lambda initialization values

### If Gate FAILS:

**Stop Pipeline:** Stable rank not controllable via gradient-based regularization

**Next Steps:**
1. Diagnose failure mode:
   - If sr reduction insufficient: Investigate regularization strength
   - If ppl deviation too large: Review adaptive lambda tuning
   - If layer variance high: Check for capacity redistribution
   - If measurement CV high: Increase probe counts or iterations

2. Pivot options:
   - SVD-based explicit rank regularization
   - Gradient flow analysis instead of stable rank
   - Alternative Jacobian estimation methods

---

## Artifacts

### Code Files
- All source code in `h-e1/code/`
- Tests in `h-e1/tests/`
- Checkpoints in `h-e1/checkpoints/{baseline,proposed}/`

### Results Files
- `h-e1/results/baseline_poc_results.json`
- `h-e1/results/proposed_poc_results.json`
- `h-e1/results/gate_validation.json`

### Logs
- `h-e1/experiment.log` - Full experiment output
- `h-e1/checkpoints/*/training_logs.json` - Per-variant training logs

---

## Sign-off

**Implementation Status:** ✓ Complete  
**Experiment Status:** [PENDING]  
**Gate Validation:** [PENDING]  
**Ready for Phase 5:** [PENDING]

---

**Validation Date:** [TBD]  
**Validated By:** YouRA Phase 4 Pipeline  
**Next Phase:** Phase 5 (if gate passes) or Pipeline Stop (if gate fails)
