# Experimental Setup

We design experiments to answer the following research questions, each mapping to sub-hypotheses from our verification framework:

**RQ1 (H-E1):** Can temporal dynamic attention be implemented and trained stably?

**RQ2 (H-M1):** Does reducing temporal steps (T) decrease FLOPs while maintaining perplexity?

**RQ3 (H-M2):** Does attention entropy decrease across temporal steps (convergence)?

**RQ4 (H-C1):** Does FLOP reduction scale with sequence length?

## Dataset

We evaluate on **WikiText-103**, a standard language modeling benchmark.

| Property | Value |
|----------|-------|
| Vocabulary | ~270K tokens |
| Training tokens | 103M |
| Validation tokens | 218K |
| Test tokens | 246K |

**Why WikiText-103:** Standard benchmark for transformer language modeling, enabling comparison with reported baselines. Long-form articles test attention at various context lengths.

For scaling experiments (H-C1), we evaluate at sequence lengths {128, 512, 1024}.

## Model Architecture

| Component | Configuration |
|-----------|--------------|
| Model | Decoder-only Transformer |
| Layers | 6 |
| Hidden dimension | 512 |
| Attention heads | 8 |
| Feed-forward dimension | 2048 |
| Temporal steps T | {1, 2, 3} (varied) |

**Temporal attention variants:**
- `baseline`: Standard attention (T=1, no temporal dynamics)
- `temporal_t3`: Temporal attention with T=3 steps (full iteration)
- `temporal_t2`: Temporal attention with T=2 steps (reduced iteration)
- `cached_kv_t3`: T=3 with K/V caching (ablation)

## Baselines

We compare against the following methods:

**Standard Attention:** Baseline transformer without temporal dynamics. Establishes the complexity and accuracy floor.

**Temporal T=3 (Full):** Our temporal attention with maximum iteration count. Tests whether T reduction degrades quality.

**K/V Cached T=3:** Temporal attention with explicit K/V caching at each step. Tests whether caching (rather than iteration reduction) drives efficiency.

## Implementation Details

**Framework:** PyTorch 2.0
**Hardware:** CPU-only (CUDA unavailable during experiments)
**Training:** AdamW optimizer, learning rate 1e-4, batch size 32, 10 epochs
**FLOP measurement:** `thop` library for PyTorch

**Hyperparameters:**
- Dropout: 0.1
- Weight initialization: Xavier uniform
- Gradient clipping: 1.0

**Reproducibility:** All experiments use fixed random seeds. Code structured for replication.

## Evaluation Metrics

**Perplexity (PPL):** exp(cross-entropy loss). Primary quality metric for language modeling. Lower is better.

**FLOPs (G):** Floating-point operations in billions. Measured via thop profiler for a single forward pass. Primary efficiency metric.

**Attention Entropy:** H = -Σ p log p where p is the attention distribution. Measures attention concentration. Lower entropy indicates more focused attention.

**FLOP Reduction:** (FLOPs_baseline - FLOPs_method) / FLOPs_baseline × 100%.

**Gate criteria:**
- H-E1 PASS: PPL within 10% of baseline, gradients stable
- H-M1 PASS: FLOP reduction ≥ 10%, PPL within ±5%
- H-M2 PASS: Entropy reduction > 5% across steps
- H-C1 PASS: Positive scaling coefficient with sequence length

## Experimental Protocol

For each sub-hypothesis:

1. **H-E1 (Existence):** Train temporal_t3 on WikiText-103 for 10 epochs. Monitor loss curves and gradient norms. Compare final PPL to baseline.

2. **H-M1 (Efficiency):** Profile FLOPs for baseline, temporal_t3, temporal_t2, and cached_kv_t3. Compare efficiency at matched training epochs.

3. **H-M2 (Convergence):** Extract attention weights at each temporal step (t=1, 2, 3). Compute entropy for each step. Test for monotonic decrease.

4. **H-C1 (Scaling):** Repeat H-M1 efficiency measurements at sequence lengths 128, 512, 1024. Fit scaling coefficient.
