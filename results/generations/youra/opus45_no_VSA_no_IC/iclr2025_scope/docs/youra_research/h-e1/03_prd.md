# Product Requirements Document: h-e1

## Hypothesis

**ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Statement**: Log-linear regression of r_opt vs N yields scaling exponent α ∈ (0.3, 0.7) with 95% CI excluding both 0 and 1

---

## Executive Summary

Validate that optimal LoRA rank scales sub-linearly with model size across Pythia family. Sweep ranks [4-128] on 4 model sizes (1B-12B), fit power law r_opt = c·N^α, confirm α ∈ (0.3, 0.7) with statistical confidence.

---

## Problem Statement

Current LoRA practice uses fixed rank (typically 16) regardless of model size. If optimal rank scales sub-linearly with parameters, this wastes capacity on large models and under-fits small ones. Quantifying the scaling law enables principled rank selection.

---

## Functional Requirements

### FR-1: Data Loading
- Load SQuAD-v2 from HuggingFace datasets
- Train split: 130,319 examples
- Validation split: 11,873 examples (full set for evaluation)
- Preprocessing: standard QA tokenization with max_length=384

### FR-2: Model Loading
- Load Pythia models via HuggingFace transformers + PEFT
- Models: EleutherAI/pythia-{1b, 2.8b, 6.9b, 12b}
- Apply LoRA to query_key_value modules

### FR-3: LoRA Configuration Sweep
- Ranks: [4, 8, 16, 32, 64, 128]
- Alpha: 2×rank (rsLoRA scaling)
- Dropout: 0.05
- Target modules: ["query_key_value"]

### FR-4: Training Protocol
- Epochs: 3
- Optimizer: AdamW, lr=1e-4
- Batch size: 8 (effective 32 via gradient accumulation 4)
- Warmup: 100 steps
- Scheduler: linear decay
- Seeds: [42, 1337, 2024]

### FR-5: Evaluation
- Metric: SQuAD-v2 F1 (official evaluation script)
- Evaluate on full validation set (11,873 examples)
- Record per-run F1 scores

### FR-6: Optimal Rank Determination
- For each (model, seed): r_opt = argmax_r(F1)
- Handle ties: geometric mean of tied ranks
- Output: (N, r_opt) pairs (12 data points)

### FR-7: Statistical Analysis
- Log-linear regression: log(r_opt) = α·log(N) + log(c)
- Bootstrap CI: B=1000 resamples
- Extract: α point estimate, 95% CI [α_low, α_high]

### FR-8: Pass/Fail Criteria
- α ∈ (0.3, 0.7)
- CI lower > 0 (excludes constant scaling)
- CI upper < 1 (excludes linear scaling)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seeds for all random operations
- Deterministic training where possible
- Log all hyperparameters

### NFR-2: Compute Budget
- ~78 GPU-hours (A100)
- Checkpoint every epoch for recovery

### NFR-3: Output Artifacts
- `results/h-e1_rank_sweep.csv`
- `results/h-e1_optimal_ranks.csv`
- `results/h-e1_scaling_fit.json`
- `figures/h-e1_scaling_plot.png`

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| All 72 training runs complete | 100% |
| α point estimate | 0.3 < α < 0.7 |
| 95% CI lower bound | > 0 |
| 95% CI upper bound | < 1 |
| R² of fit | > 0.7 |

---

## Dependencies

- transformers >= 4.35.0
- peft >= 0.7.0
- datasets
- scipy
- numpy
- matplotlib

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Wide CI from 4 models | 3 seeds per model (12 points) |
| r_opt ties | Geometric mean |
| OOM on 12B | Gradient checkpointing |
| Training instability | LR warmup, gradient clipping |

---

*Generated: 2026-08-24*
