# Phase 2C Experiment Brief: h-e1

## Hypothesis

**ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Statement**: Log-linear regression of r_opt vs N yields scaling exponent α ∈ (0.3, 0.7) with 95% CI excluding both 0 and 1

## Experimental Design

### Overview

Measure optimal LoRA rank across 4 Pythia model sizes, fit power law r_opt = c·N^α, verify α falls in sub-linear range (0.3-0.7) with 95% CI excluding trivial endpoints.

### Models

| Model | N (params) | log₁₀(N) | HuggingFace ID |
|-------|------------|----------|----------------|
| Pythia-1B | 1.0×10⁹ | 9.00 | EleutherAI/pythia-1b |
| Pythia-2.8B | 2.8×10⁹ | 9.45 | EleutherAI/pythia-2.8b |
| Pythia-6.9B | 6.9×10⁹ | 9.84 | EleutherAI/pythia-6.9b |
| Pythia-12B | 1.2×10¹⁰ | 10.08 | EleutherAI/pythia-12b |

### Dataset

**Primary**: SQuAD-v2 (standard)
- Train: 130,319 examples
- Validation: 11,873 examples  
- Type: extractive QA with unanswerable questions
- Metric: F1 score

**Rationale**: Single-hop QA aligns with hypothesis scope. Full validation set used (>10K samples) for statistically robust r_opt determination.

### LoRA Configuration

- **Ranks to sweep**: [4, 8, 16, 32, 64, 128]
- **Target modules**: ["query_key_value"] (Pythia attention)
- **LoRA alpha**: 2×rank (per rsLoRA scaling guidance)
- **Dropout**: 0.05

### Training Protocol

- **Epochs**: 3
- **Learning rate**: 1e-4 (AdamW)
- **Batch size**: 8 (effective 32 via gradient accumulation)
- **Warmup**: 100 steps
- **Scheduler**: linear decay
- **Seeds**: 3 (for bootstrap CI estimation)
- **Total runs**: 4 models × 6 ranks × 3 seeds = 72 training runs

### Optimal Rank Determination

For each (model, seed):
1. Train 6 ranks, evaluate F1 on full SQuAD-v2 validation
2. Select r_opt = argmax_{r}(F1)
3. Record (N, r_opt) pairs

### Statistical Analysis

**Primary analysis**: Log-linear regression
```
log(r_opt) = α·log(N) + log(c)
```

**CI estimation**: Bootstrap (B=1000)
- Resample (model, r_opt) pairs with replacement
- Fit OLS for each bootstrap sample
- Extract 2.5th and 97.5th percentiles for α

**Pass criteria**:
1. Point estimate α ∈ (0.3, 0.7)
2. 95% CI lower bound > 0 (excludes constant scaling)
3. 95% CI upper bound < 1 (excludes linear scaling)

### Computational Budget

| Component | GPU-hours (A100) |
|-----------|------------------|
| Pythia-1B (6×3 runs) | ~6h |
| Pythia-2.8B (6×3 runs) | ~12h |
| Pythia-6.9B (6×3 runs) | ~24h |
| Pythia-12B (6×3 runs) | ~36h |
| **Total** | ~78h |

### Implementation Requirements

1. **Data loading**: HuggingFace datasets (squad_v2)
2. **Model loading**: HuggingFace transformers + PEFT
3. **Training**: Standard Trainer with LoRA config sweep
4. **Evaluation**: Squad-v2 F1 metric (official script)
5. **Analysis**: scipy.stats for OLS, numpy for bootstrap

### Output Artifacts

- `results/h-e1_rank_sweep.csv`: (model, rank, seed, f1_score)
- `results/h-e1_optimal_ranks.csv`: (model, seed, r_opt, best_f1)
- `results/h-e1_scaling_fit.json`: {alpha, alpha_ci_low, alpha_ci_high, c, r2}
- `figures/h-e1_scaling_plot.png`: log-log plot with fit line and CI band

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| 4 models yield wide CI | Use 3 seeds per model (12 data points for bootstrap) |
| r_opt ties at multiple ranks | Take geometric mean of tied ranks |
| Computational constraints | Prioritize 2.8B and 6.9B if budget limited |

### Baseline Comparison (Phase 5)

- Constant rank=16 (industry default)
- Linear scaling: r ∝ N (α=1)
- Predicted sub-linear: r_opt from fitted law

---

## Validation Checklist

- [x] Real dataset (SQuAD-v2, standard benchmark)
- [x] Statistically meaningful sample (11,873 validation examples)
- [x] Clear pass/fail criteria (α bounds + CI exclusions)
- [x] Reproducible (fixed seeds, standard libraries)
- [x] Computational budget estimated

---

*Generated: 2026-08-24*
*Phase 2C complete for h-e1*
