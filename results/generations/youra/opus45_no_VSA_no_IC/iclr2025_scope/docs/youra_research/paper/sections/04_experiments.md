# Experimental Setup

## Research Questions

Our experiments address four questions aligned with sub-hypotheses:

1. **RQ1 (h-e1)**: Does optimal LoRA rank scale sub-linearly with model size? What is the scaling exponent $\alpha$?
2. **RQ2 (h-m2)**: Does rank sensitivity increase with model scale, indicating phase transition behavior?
3. **RQ3 (h-c1)**: Is the scaling exponent consistent across task types (single-hop vs multi-hop QA)?
4. **RQ4 (h-m1)**: Does attention entropy correlate with model size, explaining the sub-linear relationship?

## Experimental Matrix

### Main Sweep (h-e1, h-m2)

| Dimension | Values | Count |
|-----------|--------|-------|
| Models | Pythia 1B, 2.8B, 6.9B, 12B | 4 |
| Ranks | 4, 8, 16, 32, 64, 128 | 6 |
| Seeds | 42, 1337, 2024 | 3 |
| Tasks | SQuAD-v2, HotpotQA | 2 |
| **Total** | | 144 runs |

Estimated compute: ~150 GPU-hours (A100 40GB).

### Cross-Task Comparison (h-c1)

- Run full rank sweeps on both SQuAD-v2 and HotpotQA
- Compute $\alpha_{\text{SQuAD}}$ and $\alpha_{\text{HotpotQA}}$ independently
- Test $|\Delta\alpha| = |\alpha_{\text{SQuAD}} - \alpha_{\text{HotpotQA}}| \leq 0.15$

### Attention Analysis (h-m1)

- Measure attention entropy at layer $L/2$ for each model scale
- No training required—measurement at initialization
- Test Pearson correlation between entropy and $\log(N)$

## Evaluation Metrics

### Primary Metrics

- **SQuAD-v2**: F1 score (0-100 scale)
- **HotpotQA**: Exact Match (EM) + F1 score

### Derived Metrics

- **$r_{\text{opt}}$**: Smallest rank achieving 99% of rank-128 F1
- **Sensitivity**: Slope of F1 vs $\log_2(r)$ via linear regression
- **Scaling exponent $\alpha$**: Slope of $\log(r_{\text{opt}})$ vs $\log(N)$

## Baselines

We compare against:

1. **Constant rank**: Use $r=16$ for all model sizes (current practice)
2. **Linear scaling**: Use $r \propto N$ (naive scaling)
3. **Full fine-tuning**: All parameters updated (upper bound)

## Statistical Analysis

- **Bootstrap CI**: 1000 resamples for all reported intervals
- **Significance**: $p < 0.05$ for correlation tests
- **Effect size**: Report sensitivity ratios with 95% CI

## Implementation Details

- **Framework**: PyTorch + HuggingFace Transformers + PEFT
- **Hardware**: NVIDIA A100 40GB GPUs
- **Precision**: Mixed precision (fp16) with gradient scaling
- **Checkpointing**: Per-epoch model saves for reproducibility

Code and configurations available at [anonymized repository].
