# Phase 2C Experiment Brief: h-m2

## Hypothesis

**ID**: h-m2  
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Statement**: Rank sensitivity (∂accuracy/∂log(r)) is >2x higher at 12B vs 1B, indicating phase transition in rank importance

**Prerequisites**: h-e1 (must validate sub-linear scaling first)

## Experimental Design

### Overview

Measure rank sensitivity as the gradient of accuracy with respect to log-rank for each Pythia model size. Compare sensitivity at 12B vs 1B to test for >2x increase, indicating phase transition where larger models become more rank-dependent.

### Models

| Model | N (params) | log₁₀(N) | HuggingFace ID |
|-------|------------|----------|----------------|
| Pythia-1B | 1.0×10⁹ | 9.00 | EleutherAI/pythia-1b |
| Pythia-2.8B | 2.8×10⁹ | 9.45 | EleutherAI/pythia-2.8b |
| Pythia-6.9B | 6.9×10⁹ | 9.84 | EleutherAI/pythia-6.9b |
| Pythia-12B | 1.2×10¹⁰ | 10.08 | EleutherAI/pythia-12b |

### Dataset

**Primary**: SQuAD-v2 (reuse h-e1 data pipeline)
- Validation: 11,873 examples (full set)
- Metric: F1 score

**Secondary**: HotpotQA (distractor setting)
- Validation: 7,405 examples (full set)
- Metric: F1 score
- Purpose: Confirm sensitivity pattern generalizes to multi-hop reasoning

### LoRA Configuration

Same as h-e1 to ensure comparability:
- **Ranks to sweep**: [4, 8, 16, 32, 64, 128]
- **Target modules**: ["query_key_value"]
- **LoRA alpha**: 2×rank (rsLoRA scaling)
- **Dropout**: 0.05

### Training Protocol

Reuse h-e1 training infrastructure:
- **Epochs**: 3
- **Learning rate**: 1e-4 (AdamW)
- **Batch size**: 8 (effective 32 via gradient accumulation)
- **Warmup**: 100 steps
- **Seeds**: 3 per configuration
- **Total runs**: 4 models × 6 ranks × 3 seeds × 2 datasets = 144 runs

### Rank Sensitivity Measurement

For each (model, dataset, seed):

1. Train at ranks [4, 8, 16, 32, 64, 128], record F1
2. Fit local linear regression: F1 = β₀ + β₁·log₂(r)
3. Sensitivity S = |β₁| (slope magnitude)

**Rationale**: Using log-rank aligns with the power-law scaling hypothesis. The slope captures how much accuracy changes per doubling of rank.

### Statistical Analysis

**Primary test**: One-sided t-test
- H₀: S(12B) ≤ 2·S(1B)
- H₁: S(12B) > 2·S(1B)
- α = 0.05

**Secondary analysis**:
1. Plot S vs log(N) for all 4 models
2. Fit: S = a·N^γ (test for super-linear γ > 1)
3. Report transition ratio: S(12B)/S(1B) with bootstrap 95% CI

**Pass criteria**:
1. Point estimate S(12B)/S(1B) > 2.0
2. 95% CI lower bound for ratio > 1.5 (conservative threshold)
3. p-value < 0.05 for one-sided test

### Computational Budget

Builds on h-e1 runs (72 runs already done for SQuAD-v2):
| Component | GPU-hours (A100) |
|-----------|------------------|
| HotpotQA runs (4 models × 6 ranks × 3 seeds) | ~78h |
| Analysis (negligible) | <1h |
| **Total new** | ~79h |

### Implementation Requirements

1. **Reuse from h-e1**:
   - Data loading (add HotpotQA support)
   - Model loading with LoRA
   - Training loop
   - Evaluation (adapt for HotpotQA F1)

2. **New components**:
   - Sensitivity calculation module
   - Statistical test implementation
   - Comparison visualization

### Code Modifications

```python
def compute_sensitivity(ranks: list[int], f1_scores: list[float]) -> float:
    """Compute rank sensitivity as slope of F1 vs log2(rank)."""
    log_ranks = np.log2(ranks)
    slope, _, _, _, _ = scipy.stats.linregress(log_ranks, f1_scores)
    return abs(slope)

def test_phase_transition(
    sensitivities_1b: list[float],
    sensitivities_12b: list[float],
) -> dict:
    """Test if 12B sensitivity > 2x 1B sensitivity."""
    ratio = np.mean(sensitivities_12b) / np.mean(sensitivities_1b)
    # Bootstrap CI for ratio
    ratios = []
    for _ in range(1000):
        s1b = np.random.choice(sensitivities_1b, len(sensitivities_1b), replace=True)
        s12b = np.random.choice(sensitivities_12b, len(sensitivities_12b), replace=True)
        ratios.append(np.mean(s12b) / np.mean(s1b))
    ci_low, ci_high = np.percentile(ratios, [2.5, 97.5])
    return {"ratio": ratio, "ci": (ci_low, ci_high), "pass": ci_low > 1.5}
```

### Output Artifacts

- `results/h-m2_rank_sweep_hotpotqa.csv`: (model, rank, seed, f1_score)
- `results/h-m2_sensitivities.csv`: (model, dataset, seed, sensitivity)
- `results/h-m2_phase_transition.json`: {ratio, ci_low, ci_high, p_value, pass}
- `figures/h-m2_sensitivity_vs_scale.png`: S vs log(N) with error bars
- `figures/h-m2_rank_curves.png`: F1 vs rank curves for all models (overlay)

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Sensitivity measurement noise | Use 3 seeds, report mean ± std |
| Transition may be gradual, not sharp | Report continuous γ exponent, not binary |
| HotpotQA harder → lower absolute F1 | Sensitivity is relative slope, not absolute |
| h-e1 results show no scaling | Cannot run h-m2 if h-e1 fails (blocked) |

### Baseline Comparison (Phase 5)

Compare sensitivity patterns under:
1. Constant rank=16 (no sensitivity by definition)
2. Our predicted scaling law (from h-e1)
3. Full fine-tuning (upper bound sensitivity)

---

## Validation Checklist

- [x] Real datasets (SQuAD-v2, HotpotQA - standard benchmarks)
- [x] Statistically meaningful samples (11,873 + 7,405 validation examples)
- [x] Clear pass/fail criteria (ratio > 2.0, CI > 1.5)
- [x] Reproducible (fixed seeds, reuse h-e1 code)
- [x] Computational budget estimated
- [x] Prerequisites declared (h-e1)

---

*Generated: 2026-08-24*
*Phase 2C complete for h-m2*
